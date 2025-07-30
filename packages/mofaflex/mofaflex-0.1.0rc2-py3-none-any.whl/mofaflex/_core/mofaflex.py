import logging
import time
from collections import defaultdict
from dataclasses import MISSING, asdict, dataclass, field, fields
from pathlib import Path
from typing import Literal, get_args

import numpy as np
import numpy.typing as npt
import pandas as pd
import pyro
import torch
from anndata import AnnData
from array_api_compat import array_namespace
from dtw import dtw
from mudata import MuData
from pyro.infer import SVI, TraceMeanField_ELBO
from pyro.optim import ClippedAdam
from scipy import stats
from scipy.sparse import issparse
from sklearn.decomposition import NMF, PCA
from torch.utils.data import DataLoader, default_convert
from torch.utils.data._utils.collate import collate  # this is documented, so presumably part of the public API
from tqdm.auto import tqdm
from tqdm.notebook import tqdm_notebook

from .. import pl
from . import gp, preprocessing
from .datasets import CovariatesDataset, GuidingVarsDataset, MofaFlexBatchSampler, MofaFlexDataset, StackDataset
from .io import MOFACompatOption, load_model, save_model
from .likelihoods import Likelihood, LikelihoodType
from .pcgse import pcgse_test
from .pyro import MofaFlexModel
from .pyro.priors import FactorPriorType, WeightPriorType
from .training import EarlyStopper
from .utils import MeanStd, impute, sample_all_data_as_one_batch

_logger = logging.getLogger(__name__)

_ResultsTypeDF = dict[str, pd.DataFrame | AnnData | npt.NDArray[np.float32]]
_ResultsTypeSeries = dict[str, pd.Series | AnnData | npt.NDArray[np.float32]]


@dataclass(kw_only=True)
class _Options:
    def __or__(self, other):
        if self.__class__ is not other.__class__:
            raise TypeError("Can only merge objects of the same type")

        kwargs = self.asdict()
        for f in fields(other):
            val = getattr(other, f.name)
            if (
                f.default is not MISSING
                and val != f.default
                or f.default_factory is not MISSING
                and val != f.default_factory()
            ):
                kwargs[f.name] = val
        return self.__class__(**kwargs)

    def __ior__(self, other):
        if self.__class__ is not other.__class__:
            raise TypeError("Can only merge objects of the same type")

        for f in fields(other):
            val = getattr(other, f.name)
            if (
                f.default is not MISSING
                and val != f.default
                or f.default_factory is not MISSING
                and val != f.default_factory()
            ):
                setattr(self, f.name, val)
        return self

    def __post_init__(self):
        # after an HDF5 roundtrip, these are numpy scalars, which PyTorch doesn't handle well'
        for f in fields(self):
            if f.type in (float, int, bool):
                setattr(self, f.name, f.type(getattr(self, f.name)))


@dataclass(kw_only=True)
class DataOptions(_Options):
    """Options for the data."""

    group_by: str | list[str] | None = None
    """Columns of `.obs` in :class:`MuData<mudata.MuData>` objects to group data by. Ignored if the input data
    is not a :class:`MuData<mudata.MuData>` object.
    """

    scale_per_group: bool = True
    """Scale Normal likelihood data per group, otherwise across all groups."""

    annotations_varm_key: dict[str, str] | str | None = None
    """Key of .varm attribute of each AnnData object that contains annotation values."""

    covariates_obs_key: dict[str, str] | str | None = None
    """Key of .obs attribute of each :class:`AnnData<anndata.AnnData>` object that contains covariate values."""

    covariates_obsm_key: dict[str, str] | str | None = None
    """Key of .obsm attribute of each :class:`AnnData<anndata.AnnData>` object that contains covariate values."""

    guiding_vars_obs_keys: dict[str, dict[str, str]] | dict[str, str] | None = None
    """Keys of .obs attribute of each :class:`AnnData<anndata.AnnData>` object that contains guiding variable values."""

    use_obs: Literal["union", "intersection"] | None = "union"
    """How to align observations across views. Ignored if the data is not a nested dict of :class:`AnnData<anndata.AnnData>` objects."""

    use_var: Literal["union", "intersection"] | None = "union"
    """How to align variables across groups. Ignored if the data is not a nested dict of :class:`AnnData<anndata.AnnData>` objects"""

    plot_data_overview: bool = True
    """Plot data overview."""

    remove_constant_features: bool = True
    """Remove constant features from the data."""


@dataclass(kw_only=True)
class ModelOptions(_Options):
    """Options for the model."""

    n_factors: int = 0
    """Number of latent factors."""

    weight_prior: dict[str, WeightPriorType] | WeightPriorType = "Normal"
    """Weight priors for each view (if dict) or for all views (if str)."""

    factor_prior: dict[str, FactorPriorType] | FactorPriorType = "Normal"
    """Factor priors for each group (if dict) or for all groups (if str)."""

    likelihoods: dict[str, LikelihoodType] | LikelihoodType | None = None
    """Data likelihoods for each view (if dict) or for all views (if str). Inferred automatically if None."""

    nonnegative_weights: dict[str, bool] | bool = False
    """Non-negativity constraints for weights for each view (if dict) or for all views (if bool)."""

    guiding_vars_likelihoods: dict[str, str] | Literal["Normal", "Categorical", "Bernoulli"] | None = "Normal"
    """Likelihood for each guiding variable (if dict) or for all guiding variables (if str)."""

    guiding_vars_scales: dict[str, float] | float = 1.0
    """Scale for the likelihood of each guiding variable, to put more or less emphasis on them during training."""

    nonnegative_factors: dict[str, bool] | bool = False
    """Non-negativity constraints for factors for each group (if dict) or for all groups (if bool)."""

    annotation_confidence: float = 0.99
    """Confidence in the provided feature annotation. Must be between 0 and 1. Smaller values make the model more likely to
        add features to the annotated pathways during training, while larger values encourage the model to more closely adhere
        to the provided annotations."""

    init_factors: float | Literal["random", "orthogonal", "pca"] = "random"
    """Initialization method for factors."""

    init_scale: float = 0.1
    """Initialization scale of Normal distribution for factors."""


@dataclass(kw_only=True)
class TrainingOptions(_Options):
    """Options for training."""

    device: str | torch.device = "cuda"
    """Device to run training on."""

    batch_size: int = 0
    """Batch size."""

    max_epochs: int = 10_000
    """Maximum number of training epochs."""

    n_particles: int = 1
    """Number of particles for ELBO estimation."""

    lr: float = 0.001
    """Learning rate."""

    early_stopper_patience: int = 100
    """Number of steps without relevant improvement to stop training."""

    save_path: str | None = None
    """Path to save model."""

    mofa_compat: MOFACompatOption = False
    """Save model in MOFA2 compatible format. If `True` or `"full"`, will include the data in the file. This
    can result in very large files. `"modelonly"` will save only the trained model."""

    seed: int | None = None
    """Seed for the pseudorandom number generator."""

    num_workers: int = 0
    """Number of data loader workers."""

    pin_memory: bool = False
    """Whether to use pinned memory in the data loader."""

    def __post_init__(self):
        super().__post_init__()
        self.device = torch.device(self.device)


@dataclass(kw_only=True)
class SmoothOptions(_Options):
    """Options for Gaussian processes."""

    n_inducing: int = 100
    """Number of inducing points."""

    kernel: Literal["RBF", "Matern"] = "RBF"
    """Kernel function to use."""

    mefisto_kernel: bool = True
    """Whether to use the MEFISTO group covariance kernel or treat groups independently."""

    independent_lengthscales: bool = False
    """Whether to use a separate lengthscale per covariate dimension."""

    group_covar_rank: int = 1
    """Rank of the group correlation matrix. Only relevant if `mefisto_kernel=True`."""

    warp_groups: list[str] = field(default_factory=list)
    """List of groups to apply dynamic time warping to."""

    warp_interval: int = 20
    """Apply dynamic time warping every `warp_interval` epochs."""

    warp_open_begin: bool = True
    """Perform open-ended alignment."""

    warp_open_end: bool = True
    """Perform open-ended alignment."""

    warp_reference_group: str | None = None
    """Reference group to align the others to. Defaults to the first group of `warp_groups`."""

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.warp_groups, str):
            self.warp_groups = [self.warp_groups]
        else:
            self.warp_groups = list(self.warp_groups)  # in case the user passed a tuple here, we need a list for saving


class MOFAFLEX:
    """Fit the model using the provided data.

    Args:
        data: can be any of:

            - MuData object
            - Nested dict with group names as keys, view names as subkeys and AnnData objects as values
              (incompatible with :class:`TrainingOptions` `.group_by`)

        *args: Options for training.
    """

    def __init__(self, data: MuData | dict[str, dict[str, AnnData]], *args: _Options):
        self._preprocess_options(*args)
        data = self._make_dataset(data)
        self._adjust_options(data)

        if self._data_opts.plot_data_overview:
            pl.overview(data).show()

        self._setup_likelihoods(data)
        preprocessor = self._make_preprocessor(data)

        # this needs to be after preprocessor, since preprocessor may filter out features with zero variance
        self._setup_annotations(data)
        self._setup_guiding_vars()

        self._metadata = data.get_obs()
        self._view_names = data.view_names
        self._group_names = data.group_names
        self._sample_names = data.sample_names
        self._feature_names = data.feature_names

        self._fit(data, preprocessor)

    def _make_dataset(self, data: MuData | dict[str, dict[str, AnnData]]) -> MofaFlexDataset:
        return MofaFlexDataset(
            data, group_by=self._data_opts.group_by, use_obs=self._data_opts.use_obs, use_var=self._data_opts.use_var
        )

    def _make_preprocessor(self, data: MofaFlexDataset) -> preprocessing.MofaFlexPreprocessor:
        preprocessor = preprocessing.MofaFlexPreprocessor(
            dataset=data,
            likelihoods=self._model_opts.likelihoods,
            nonnegative_weights=self._model_opts.nonnegative_weights,
            nonnegative_factors=self._model_opts.nonnegative_factors,
            scale_per_group=self._data_opts.scale_per_group,
            remove_constant_features=self._data_opts.remove_constant_features,
            state=getattr(self, "_preprocessor_state", None),
        )
        data.preprocessor = preprocessor
        return preprocessor

    def _mofaflexdataset(self, data: MuData | dict[str, dict[str, AnnData]]) -> MofaFlexDataset:
        data = self._make_dataset(data)
        self._make_preprocessor(data)
        return data

    @property
    def n_guided_factors(self) -> int:
        """Number of guided factors."""
        return self._n_guiding_vars

    @property
    def group_names(self) -> npt.NDArray[str]:
        """Group names."""
        return self._group_names

    @property
    def n_groups(self) -> int:
        """Number of groups."""
        return len(self.group_names)

    @property
    def view_names(self) -> npt.NDArray[str]:
        """View names."""
        return self._view_names

    @property
    def n_views(self) -> int:
        """Number of views."""
        return len(self.view_names)

    @property
    def feature_names(self) -> dict[str, npt.NDArray[str]]:
        """Feature names for each view."""
        return self._feature_names

    @property
    def n_features(self) -> dict[str, int]:
        """Number of features in each view."""
        return {k: len(v) for k, v in self.feature_names.items()}

    @property
    def n_features_total(self) -> int:
        """Total number of features."""
        return sum(self.n_features.values())

    @property
    def sample_names(self) -> dict[str, npt.NDArray[str]]:
        """Sample names for each group."""
        return self._sample_names

    @property
    def n_samples(self) -> dict[str, int]:
        """Number of samples in each group."""
        return {k: len(v) for k, v in self.sample_names.items()}

    @property
    def n_samples_total(self) -> int:
        """Total number of samples."""
        return sum(self.n_samples.values())

    @property
    def n_factors(self):
        """Total number of factors."""
        return self._model_opts.n_factors

    @property
    def n_dense_factors(self) -> int:
        """Number of dense (uninformed) factors."""
        return self._n_dense_factors

    @property
    def n_informed_factors(self) -> int:
        """Number of informed factors."""
        return self._n_informed_factors

    @property
    def factor_order(self) -> npt.NDArray[int]:
        """Ordering of factors by explained variance (highest to lowest)."""
        return self._factor_order

    @factor_order.setter
    def factor_order(self, value: npt.ArrayLike):
        order = np.asarray(value, dtype=int)
        if order.ndim != 1:
            raise ValueError(f"The ordering must have 1 dimension, but got {order.ndim}.")
        if order.size != self.n_factors:
            raise ValueError(f"The ordering must have {self.n_factors} items, but got {order.size}.")
        if order.min() != 0 or order.max() != self.n_factors - 1 or np.unique(order).size != order.size:
            raise ValueError(f"The ordering must contain all integers in [0, {self.n_factors}).")
        self._factor_order = order

    @property
    def factor_names(self) -> npt.NDArray[str | np.str_]:
        """Factor names."""
        return self._factor_names

    @property
    def warped_covariates(self) -> dict[str, npt.NDArray[np.float32]] | None:
        """Time-warped covariates for each group, if using a GP prior and dynamic time warping was enabled."""
        return self._covariates if hasattr(self, "_orig_covariates") else None

    @property
    def covariates(self) -> dict[str, npt.NDArray[np.float32]]:
        """Covariates for each group, if using a GP prior."""
        return self._orig_covariates if hasattr(self, "_orig_covariates") else self._covariates

    @property
    def covariates_names(self) -> dict[str, str | npt.NDArray[str | np.str_]]:
        """Covariate names for each group where they could be inferred from the input."""
        return self._covariates_names

    @property
    def gp_lengthscale(self) -> npt.NDArray[np.float32] | None:
        """Inferred lengthscales for each factor, if using a GP prior."""
        return self._gp.lengthscale.detach().cpu().numpy() if self._gp is not None else None

    @property
    def gp_scale(self) -> npt.NDArray[np.float32] | None:
        """Inferred variance scales (smoothness) for each factor, if using a GP prior."""
        return self._gp.outputscale.detach().cpu().numpy() if self._gp is not None else None

    @property
    def gp_group_correlation(self) -> npt.NDArray[np.float32]:
        """Between-group correlation for each factor, if using a GP prior."""
        return self._gp.group_corr.detach().cpu().numpy() if self._gp is not None else None

    @property
    def training_loss(self) -> npt.NDArray[np.float32]:
        """Total loss (negative ELBO) for each training epoch."""
        return self._train_loss_elbo

    def _setup_likelihoods(self, data):
        if (
            not isinstance(self._model_opts.likelihoods, dict | str | None)
            or isinstance(self._model_opts.likelihoods, str)
            and self._model_opts.likelihoods not in get_args(LikelihoodType)
            or isinstance(self._model_opts.likelihoods, dict)
            and not all(val in get_args(LikelihoodType) for val in self._model_opts.likelihoods.values())
        ):
            raise ValueError("Likelihoods must be a dictionary or a string containing a valid likelihood name.")

        if self._model_opts.likelihoods is None:
            self._model_opts.likelihoods = data.apply(Likelihood.infer, by_group=False)
            msg = []
            for view_name, likelihood in self._model_opts.likelihoods.items():
                msg.append(f"{view_name}: {likelihood}")
            _logger.info("No likelihoods provided. Using inferred likelihoods: " + "; ".join(msg))
        else:
            if isinstance(self._model_opts.likelihoods, str):
                self._model_opts.likelihoods = dict.fromkeys(data.view_names, self._model_opts.likelihoods)

            self._model_opts.likelihoods = {
                view: Likelihood.get(likelihood) for view, likelihood in self._model_opts.likelihoods.items()
            }

            data.apply(
                lambda *args, likelihood, **kwargs: likelihood.validate(*args, **kwargs),
                view_kwargs={"likelihood": self._model_opts.likelihoods},
                by_group=False,
            )

    def _setup_annotations(self, data):
        annotations = None
        if self._data_opts.annotations_varm_key is not None:
            annotations, annotations_names = data.get_annotations(self._data_opts.annotations_varm_key)

        informed = annotations is not None and len(annotations) > 0
        valid_n_factors = self._model_opts.n_factors is not None and self._model_opts.n_factors > 0

        n_dense_factors = 0
        n_informed_factors = 0
        factor_names = []

        if informed:
            ignored_views = []
            for vn in data.view_names:
                if vn in annotations and (prior := self._model_opts.weight_prior[vn]) != "Horseshoe":
                    ignored_views.append(vn)
                    _logger.warning(
                        f"Horseshoe prior required for annotations, but got {prior} for view {vn}. Annotations will be ignored."
                    )
            if len(ignored_views) == data.view_names.size:
                informed = False
                n_informed_factors = 0

        if not informed and not valid_n_factors:
            raise ValueError(
                "Invalid latent configuration, "
                "please provide either a collection of prior masks, "
                "or set `n_factors` to a positive integer."
            )

        if self._model_opts.n_factors is not None:
            n_dense_factors = self._model_opts.n_factors
            factor_names += [f"Factor {k + 1}" for k in range(n_dense_factors)]

        prior_masks = {}

        if informed:
            # TODO: annotations need to be processed if not aligned or full
            n_informed_factors = annotations[data.view_names[0]].shape[0]
            if data.view_names[0] in annotations_names:
                factor_names += annotations_names[data.view_names[0]].to_list()
            else:
                factor_names += [
                    f"Factor {k + 1}" for k in range(n_dense_factors, n_dense_factors + n_informed_factors)
                ]

            prior_masks = {vn: vm.astype(np.bool_) for vn, vm in annotations.items()}

        self._n_dense_factors = n_dense_factors
        self._n_informed_factors = n_informed_factors
        self._model_opts.n_factors = n_dense_factors + n_informed_factors

        self._factor_names = np.asarray(factor_names)
        self._factor_order = np.arange(self._model_opts.n_factors)

        # storing prior_masks as full annotations instead of partial annotations
        self._annotations = prior_masks

    def _setup_gp(self, covariates=None, full_setup=True):
        gp_group_names = [g for g in self.group_names if self._model_opts.factor_prior[g] == "GP"]

        gp_warp_groups_order = None
        if len(gp_group_names):
            if full_setup:
                if len(self._gp_opts.warp_groups) > 1:
                    if not set(self._gp_opts.warp_groups) <= set(gp_group_names):
                        raise ValueError(
                            "The set of groups with dynamic time warping must be a subset of groups with a GP factor prior."
                        )
                    gp_warp_groups_order = {}
                    for g in self._gp_opts.warp_groups:
                        ccov = covariates[g].squeeze()
                        if ccov.ndim > 1:
                            raise ValueError(
                                f"Warping can only be performed with 1D covariates, but the covariate for group {g} has {ccov.ndim} dimensions."
                            )
                        gp_warp_groups_order[g] = ccov.argsort()
                    self._orig_covariates = {g: c.copy() for g, c in covariates.items()}

                    if self._gp_opts.warp_reference_group is None:
                        self._gp_opts.warp_reference_group = self._gp_opts.warp_groups[0]
                elif len(self._gp_opts.warp_groups) == 1:
                    _logger.warning("Need at least 2 groups for warping, but only one was given. Ignoring warping.")
                    self._gp_opts.warp_groups = []
            else:
                covariates = self._covariates

            self._gp = gp.GP(
                n_inducing=self._gp_opts.n_inducing,
                covariates=(covariates[g] for g in gp_group_names),
                n_factors=self._model_opts.n_factors,
                n_groups=len(gp_group_names),
                kernel=self._gp_opts.kernel,
                independent_lengthscales=self._gp_opts.independent_lengthscales,
                rank=self._gp_opts.group_covar_rank,
                use_mefisto_kernel=self._gp_opts.mefisto_kernel,
            ).to(self._train_opts.device)
            self._gp_group_names = gp_group_names
        else:
            self._gp = None
            self._gp_group_names = None
        return gp_warp_groups_order

    def _setup_guiding_vars(self):
        guiding_vars_names = (
            list(self._data_opts.guiding_vars_obs_keys.keys()) if self._data_opts.guiding_vars_obs_keys else []
        )
        self._n_guiding_vars = len(guiding_vars_names)
        if self._n_guiding_vars == 0:
            return

        # update global number of factors
        self._model_opts.n_factors = self._model_opts.n_factors + self._n_guiding_vars

        # update global factor names (dense factors + guiding vars + informed factors)
        self._factor_names = np.concatenate(
            [self._factor_names[: self.n_dense_factors], guiding_vars_names, self._factor_names[self.n_dense_factors :]]
        )

    def _setup_svi(
        self,
        prior_scales,
        init_tensor,
        covariates,
        guiding_vars_factors,
        guiding_vars_n_categories,
        feature_means,
        sample_means,
    ):
        gp_warp_groups_order = self._setup_gp(covariates=covariates)

        model = MofaFlexModel(
            n_samples=self.n_samples,
            n_features=self.n_features,
            n_factors=self._model_opts.n_factors,
            likelihoods=self._model_opts.likelihoods,
            guiding_vars_likelihoods=self._model_opts.guiding_vars_likelihoods,
            guiding_vars_n_categories=guiding_vars_n_categories,
            guiding_vars_factors=guiding_vars_factors,
            guiding_vars_scales=self._model_opts.guiding_vars_scales,
            prior_scales=prior_scales,
            factor_prior=self._model_opts.factor_prior,
            weight_prior=self._model_opts.weight_prior,
            nonnegative_factors=self._model_opts.nonnegative_factors,
            nonnegative_weights=self._model_opts.nonnegative_weights,
            gp=self._gp,
            feature_means=feature_means,
            sample_means=sample_means,
            factors_init_tensor=init_tensor,
        ).to(self._train_opts.device)

        n_iterations = int(self._train_opts.max_epochs * (self.n_samples_total // self._train_opts.batch_size))
        gamma = 0.1
        lrd = gamma ** (1 / n_iterations)

        optimizer = ClippedAdam(model.get_lr_func(self._train_opts.lr, lrd=lrd))

        svi = SVI(
            model=pyro.poutine.scale(model.model, scale=1.0 / self.n_samples_total),
            guide=pyro.poutine.scale(model.guide, scale=1.0 / self.n_samples_total),
            optim=optimizer,
            loss=TraceMeanField_ELBO(
                retain_graph=True, num_particles=self._train_opts.n_particles, vectorize_particles=True
            ),
        )

        return svi, model, gp_warp_groups_order

    def _post_fit(self, data, preprocessor, covariates, model, train_loss_elbo):
        self._weights = model.get_weights()
        self._factors = model.get_factors()
        self._dispersions = model.get_dispersion()
        self._sparse_factors_probabilities = model.get_sparse_factor_probabilities()
        self._sparse_weights_probabilities = model.get_sparse_weight_probabilities()
        self._sparse_factors_precisions = model.get_sparse_factor_precisions()
        self._sparse_weights_precisions = model.get_sparse_weight_precisions()
        self._covariates, self._covariates_names = (covariates.covariates, covariates.covariates_names)
        self._gps = self._get_gps(self._covariates)
        self._train_loss_elbo = np.asarray(train_loss_elbo)

        self._df_r2_full, self._df_r2_factors, self._factor_order = self._sort_factors(
            data,
            weights=self.get_weights(return_type="numpy", moment="mean", sparse_type="mix", ordered=False),
            factors=self.get_factors(return_type="numpy", moment="mean", sparse_type="mix", ordered=False),
        )

        self._preprocessor_state = preprocessor.state_dict()

        if len(self._annotations) > 0:
            self._pcgse = pcgse_test(
                data,
                self._model_opts.nonnegative_weights,
                self.get_annotations("pandas"),
                self.get_weights("pandas"),
                min_size=1,
                subsample=1000,
            )
        else:
            self._pcgse = None

        if self._train_opts.save_path is not False:
            if self._train_opts.save_path is None:
                self._train_opts.save_path = f"mofaflex_{time.strftime('%Y%m%d_%H%M%S')}.h5"
            _logger.info(f"Saving results to {self._train_opts.save_path}...")
            Path(self._train_opts.save_path).parent.mkdir(parents=True, exist_ok=True)
            self._save(self._train_opts.save_path, self._train_opts.mofa_compat, data, preprocessor.feature_means)

    @staticmethod
    def _init_factor_group(adata, group_name, view_name, impute_missings, initializer):
        arr = adata.X
        if issparse(arr):
            havenan = np.isnan(arr.data).any()
        else:
            xp = array_namespace(arr)
            havenan = xp.isnan(arr).any()
        if havenan:
            if impute_missings:
                from sklearn.impute import SimpleImputer

                imp = SimpleImputer(missing_values=np.nan, strategy="mean")
                arr = imp.fit_transform(arr)
            else:
                raise ValueError("Data has missing values. Please impute missings or set `impute_missings=True`.")
        return initializer.fit_transform(arr)

    def _initialize_factors(self, data, impute_missings=True):
        init_tensor = defaultdict(dict)
        _logger.info(f"Initializing factors using `{self._model_opts.init_factors}` method...")

        if not isinstance(self._model_opts.init_factors, str):
            for group_name, n in self.n_samples.items():
                init_tensor[group_name]["loc"] = np.full(
                    shape=(n, self._model_opts.n_factors), fill_value=self._model_opts.init_factors, dtype=np.float32
                ).T[..., None]
                init_tensor[group_name]["scale"] = np.full(
                    shape=(n, self._model_opts.n_factors), fill_value=self._model_opts.init_scale, dtype=np.float32
                ).T[..., None]
            return init_tensor
        match self._model_opts.init_factors:
            case "random":
                for group_name, n in self.n_samples.items():
                    init_tensor[group_name]["loc"] = np.random.uniform(size=(n, self._model_opts.n_factors))
            case "orthogonal":
                for group_name, n in self.n_samples.items():
                    # Compute PCA of random vectors
                    pca = PCA(n_components=self._model_opts.n_factors, whiten=True)
                    pca.fit(stats.norm.rvs(loc=0, scale=1, size=(n, self._model_opts.n_factors)).T)
                    init_tensor[group_name]["loc"] = pca.components_.T
            case "pca" | "nmf" as init:
                if init == "pca":
                    initializer = PCA(n_components=self._model_opts.n_factors, whiten=True)
                elif init == "nmf":
                    initializer = NMF(n_components=self._model_opts.n_factors, max_iter=1000)

                inits = data.apply(
                    self._init_factor_group, by_view=False, impute_missings=impute_missings, initializer=initializer
                )
                for group_name, init in inits.items():
                    init_tensor[group_name]["loc"] = init
            case _:
                raise ValueError(
                    f"Initialization method `{self._model_opts.init_factors}` not found. Please choose from `random`, `orthogonal`, `PCA`, or `NMF`."
                )

        for group_name, n in self.n_samples.items():
            # scale factor values from -1 to 1 (per factor)
            q = init_tensor[group_name]["loc"]

            if q.shape[0] > 1:  # min and max are not defined for dimensions of size 1
                q = 2.0 * (q - np.min(q, axis=0)) / (np.max(q, axis=0) - np.min(q, axis=0)) - 1
            else:
                q = 2.0 * (q - np.min(q)) / (np.max(q) - np.min(q)) - 1

            # Add artifical dimension at dimension -2 for broadcasting
            init_tensor[group_name]["loc"] = q.T[..., None].astype(np.float32, copy=False)
            init_tensor[group_name]["scale"] = np.full(
                shape=(n, self._model_opts.n_factors), fill_value=self._model_opts.init_scale, dtype=np.float32
            ).T[..., None]

        return init_tensor

    def _preprocess_options(self, *args: _Options):
        self._data_opts = DataOptions()
        self._model_opts = ModelOptions()
        self._train_opts = TrainingOptions()
        self._gp_opts = SmoothOptions()

        for arg in args:
            match arg:
                case DataOptions():
                    self._data_opts |= arg
                case ModelOptions():
                    self._model_opts |= arg
                case TrainingOptions():
                    self._train_opts |= arg
                case SmoothOptions():
                    self._gp_opts |= arg

        if self._train_opts.seed is not None:
            try:
                self._train_opts.seed = int(self._train_opts.seed)
            except ValueError:
                _logger.warning(f"Could not convert `{self._train_opts.seed}` to integer.")
                self._train_opts.seed = None

        if self._train_opts.seed is None:
            self._train_opts.seed = int(time.strftime("%y%m%d%H%M"))

    def _adjust_options(self, data: dict[dict[AnnData]]):
        # convert input arguments to dictionaries if necessary
        guiding_vars_names = (
            self._data_opts.guiding_vars_obs_keys.keys() if self._data_opts.guiding_vars_obs_keys else []
        )
        for guiding_var_name in guiding_vars_names:
            if isinstance(self._data_opts.guiding_vars_obs_keys[guiding_var_name], str):
                self._data_opts.guiding_vars_obs_keys[guiding_var_name] = dict.fromkeys(
                    data.group_names, self._data_opts.guiding_vars_obs_keys[guiding_var_name]
                )

        for opt_name, keys in zip(
            (
                "weight_prior",
                "factor_prior",
                "nonnegative_weights",
                "nonnegative_factors",
                "guiding_vars_likelihoods",
                "guiding_vars_scales",
            ),
            (
                data.view_names,
                data.group_names,
                data.view_names,
                data.group_names,
                guiding_vars_names,
                guiding_vars_names,
            ),
            strict=True,
        ):
            val = getattr(self._model_opts, opt_name)
            if not isinstance(val, dict):
                setattr(self._model_opts, opt_name, dict.fromkeys(keys, val))

        for opt_name, keys in zip(
            ("covariates_obs_key", "covariates_obsm_key", "annotations_varm_key"),
            (data.group_names, data.group_names, data.view_names),
            strict=True,
        ):
            val = getattr(self._data_opts, opt_name)
            if isinstance(val, str):
                setattr(self._data_opts, opt_name, dict.fromkeys(keys, val))

        self._train_opts.device = self._setup_device(self._train_opts.device)
        if self._train_opts.batch_size is None or not (0 < self._train_opts.batch_size <= data.n_samples_total):
            self._train_opts.batch_size = data.n_samples_total

    def _fit(self, data, preprocessor):
        pyro.set_rng_seed(self._train_opts.seed)

        # informed factors
        prior_scales = None
        if self.n_informed_factors > 0:
            prior_scales = {
                vn: np.clip(
                    self._annotations.get(
                        vn, np.broadcast_to(0, (self.n_informed_factors, self.n_features[vn]))
                    ).astype(np.float32)
                    + (1 - self._model_opts.annotation_confidence),
                    1e-8,
                    1.0,
                )
                for vn in self.view_names
            }

            if self.n_dense_factors + self.n_guided_factors > 0:
                prior_scales = {
                    vn: np.concatenate(
                        (
                            np.ones(
                                (self.n_dense_factors + self.n_guided_factors, data.n_features[vn]), dtype=vm.dtype
                            ),
                            vm,
                        ),
                        axis=0,
                    )
                    for vn, vm in prior_scales.items()
                }

        # guided factors
        guiding_vars_factors = {}
        guiding_vars_names = (
            self._data_opts.guiding_vars_obs_keys.keys() if self._data_opts.guiding_vars_obs_keys else []
        )
        for i, guiding_var_name in enumerate(guiding_vars_names):
            guiding_vars_factors[guiding_var_name] = self._n_informed_factors + i

        guiding_vars = GuidingVarsDataset(data, self._data_opts.guiding_vars_obs_keys)
        covariates = CovariatesDataset(data, self._data_opts.covariates_obs_key, self._data_opts.covariates_obsm_key)

        # get unique categories for each guiding variable
        guiding_vars_n_categories = {}
        if self._data_opts.guiding_vars_obs_keys:
            for guiding_var_name, guiding_var_likelihood in self._model_opts.guiding_vars_likelihoods.items():
                if guiding_var_likelihood == "Categorical":
                    guiding_vars_categories = set()
                    # find number of unique categories across groups
                    for group_name in self._group_names:
                        guiding_vars_categories.update(
                            map(tuple, guiding_vars.datasets[guiding_var_name].covariates[group_name])
                        )
                    guiding_vars_n_categories[guiding_var_name] = len(guiding_vars_categories)

                else:
                    # if not categorical, set to default
                    guiding_vars_n_categories[guiding_var_name] = 1

        init_tensor = self._initialize_factors(data)

        svi, model, gp_warp_groups_order = self._setup_svi(
            prior_scales,
            init_tensor,
            covariates.covariates,
            guiding_vars_factors,
            guiding_vars_n_categories,
            preprocessor.feature_means,
            preprocessor.sample_means,
        )

        # clean start
        pyro.enable_validation(True)
        pyro.clear_param_store()

        # Train
        singlebatch = self._train_opts.batch_size >= max(self.n_samples.values())
        collate_fn_map = {
            torch.Tensor: lambda x, **kwargs: x[0].to(self._train_opts.device, non_blocking=True),
            slice: lambda x, **kwargs: x[0],
        }
        dataset = StackDataset(data=data, covariates=covariates, guiding_vars=guiding_vars)
        if singlebatch:
            batch = collate(
                (default_convert(dataset.__getitems__(sample_all_data_as_one_batch(data))),),
                collate_fn_map=collate_fn_map,
            )
        else:
            loader = DataLoader(
                dataset,
                batch_sampler=MofaFlexBatchSampler(
                    data.n_samples, self._train_opts.batch_size, False, generator=torch.default_generator
                ),
                collate_fn=default_convert,
                num_workers=self._train_opts.num_workers,
                pin_memory=self._train_opts.pin_memory,
                persistent_workers=self._train_opts.num_workers > 0,
            )

        train_loss_elbo = []
        earlystopper = EarlyStopper(
            mode="min", min_delta=0.1, patience=self._train_opts.early_stopper_patience, percentage=True
        )
        with tqdm(range(self._train_opts.max_epochs), unit="epochs", dynamic_ncols=True) as t:
            for i in t:
                epoch_loss = 0
                if singlebatch:
                    with self._train_opts.device:
                        epoch_loss += svi.step(
                            **batch["data"], covariates=batch["covariates"], guiding_vars=batch["guiding_vars"]
                        )
                else:
                    for batch in loader:
                        batch = collate((batch,), collate_fn_map=collate_fn_map)
                        with self._train_opts.device:
                            epoch_loss += svi.step(
                                **batch["data"], covariates=batch["covariates"], guiding_vars=batch["guiding_vars"]
                            )
                train_loss_elbo.append(epoch_loss)
                if (
                    self._gp is not None
                    and len(self._gp_opts.warp_groups)
                    and i > 0
                    and not i % self._gp_opts.warp_interval
                ):
                    self._warp_covariates(covariates, model, gp_warp_groups_order)

                t.set_postfix({"Loss": epoch_loss}, refresh=False)

                if earlystopper.step(epoch_loss):
                    _logger.info(f"Training converged after {i} epochs.")
                    break
        if isinstance(t, tqdm_notebook):  # https://github.com/tqdm/tqdm/issues/1659
            t.container.children[1].bar_style = "success"

        self._post_fit(data, preprocessor, covariates, model, train_loss_elbo)

    def _warp_covariates(self, covariates, model, warp_groups_order):
        factormeans = model.get_factors().mean
        refgroup = self._gp_opts.warp_reference_group
        reffactormeans = factormeans[refgroup].mean(axis=0)
        refidx = warp_groups_order[refgroup]
        for g in self._gp_opts.warp_groups[1:]:
            idx = warp_groups_order[g]
            alignment = dtw(
                reffactormeans[refidx],
                factormeans[g][:, idx].mean(axis=0),
                open_begin=self._gp_opts.warp_open_begin,
                open_end=self._gp_opts.warp_open_end,
                step_pattern="asymmetric",
            )
            covariates.covariates[g] = self._orig_covariates[g].copy()
            covariates.covariates[g][idx[alignment.index2], 0] = self._orig_covariates[refgroup][
                refidx[alignment.index1], 0
            ]
        self._gp.update_inducing_points(covariates.covariates.values())

    def _sort_factors(self, data, weights, factors, subsample=1000):
        # Loop over all groups
        dfs_factors, dfs_full = {}, {}

        def r2_wrapper(view, group_name, view_name):
            if subsample is not None and subsample > 0 and subsample < view.n_obs:
                sample_idx = np.random.choice(view.n_obs, subsample, replace=False)
            else:
                sample_idx = slice(None)
            cdata = data.preprocessor(view.X[sample_idx, :], slice(None), slice(None), group_name, view_name)[0]
            if issparse(cdata):
                cdata = cdata.toarray()

            dispersions = self._dispersions.mean.get(view_name)
            if dispersions is not None:
                dispersions = align_global_array_to_local(dispersions, group_name, view_name, align_to="features")  # noqa F821
            try:
                return self._model_opts.likelihoods[view_name].r2(
                    view_name,
                    y_true=cdata,
                    factors=align_global_array_to_local(  # noqa F821
                        factors[group_name], group_name, view_name, align_to="samples", axis=0
                    )[sample_idx, :],
                    weights=align_global_array_to_local(  # noqa F821
                        weights[view_name], group_name, view_name, align_to="features", axis=1
                    ),
                    dispersions=dispersions,
                    sample_means=align_global_array_to_local(  # noqa F821
                        data.preprocessor.sample_means[group_name][view_name],
                        group_name,
                        view_name,
                        align_to="samples",
                        axis=0,
                    )[sample_idx],
                )
            except NotImplementedError:
                _logger.warning(
                    f"R2 calculation for {self._model_opts.likelihoods[view_name]} likelihood has not yet been implemented. Skipping view {view_name} for group {group_name}."
                )

        r2s = data.apply(r2_wrapper)
        for group_name, group_r2 in r2s.items():
            group_r2_factors, group_r2_full = {}, {}
            for view_name, view_r2 in group_r2.items():
                group_r2_full[view_name], group_r2_factors[view_name] = view_r2
            if len(group_r2_factors) == 0:
                _logger.warning(f"No R2 values found for group {group_name}. Skipping...")
                continue
            dfs_factors[group_name] = pd.DataFrame(group_r2_factors)
            dfs_full[group_name] = pd.Series(group_r2_full)

        # sum the R2 values across all groups
        df_concat = pd.concat(dfs_factors.values())
        df_sum = df_concat.groupby(df_concat.index).sum()
        dfs_full = pd.DataFrame(dfs_full)

        try:
            # sort factors according to mean R2 across all views
            sorted_r2_means = df_sum.mean(axis=1).sort_values(ascending=False)
            factor_order = sorted_r2_means.index.to_numpy()
        except NameError:
            _logger.warning("Sorting factors failed. Using default order.")
            factor_order = np.array(list(range(self.model_opts.n_factors)))

        return dfs_full, dfs_factors, factor_order

    def _get_component(self, component, return_type="pandas"):
        match return_type:
            case "numpy":
                return {k: v.to_numpy() for k, v in component.items()}
            case "pandas":
                return component
            case "torch":
                return {k: torch.tensor(v.values, dtype=torch.float).clone().detach() for k, v in component.items()}
            case "anndata":
                return {k: AnnData(v) for k, v in component.items()}

    def _get_sparse(self, what, moment, sparse_type):
        ret = {}
        probs = getattr(self, f"_sparse_{what}_probabilities")
        vals = getattr(self, "_" + what)
        precs = getattr(self, f"_sparse_{what}_precisions")
        for name, cvals in getattr(vals, moment).items():
            if name in probs:
                if sparse_type == "mix":
                    if moment == "mean":
                        cvals = cvals * probs[name]
                    else:
                        p = probs[name]
                        a = precs.mean[name][:, None]
                        cvals = np.sqrt(vals.mean[name] ** 2 * p * (1 - p) + p * cvals**2 + (1 - p) / a**2)
                elif sparse_type == "thresh":
                    if moment == "mean":
                        cvals = cvals * (vals[name].mean >= 0.5)
                    else:
                        cvals = 1 / precs.mean[name]
            ret[name] = cvals
        return ret

    def get_factors(
        self,
        return_type: Literal["pandas", "anndata", "numpy"] = "pandas",
        moment: Literal["mean", "std"] = "mean",
        sparse_type: Literal["raw", "mix", "thresh"] = "mix",
        ordered: bool = False,
    ) -> _ResultsTypeDF:
        """Get the factor matrices Z for each group.

        Args:
             return_type: Format of the returned object.
             moment: Which moment of the posterior distribution to return.
             sparse_type: How to handle sparsity when using the spike and slab prior.

                 - raw: Do nothing, return inferred values for all entries.
                 - mix: Return the corresponding moment of a mixture distribution of two
                   Normal distributions: One centered at 0 and the other centered at the
                   inferred non-sparse value. The mixture is weighted by the inferred
                   sparsity probability. This is what MOFA does.
                 - thresh: Set all values with a sparsity probablity > 0.5 to 0.

             ordered: Whether to return the factors ordered by explained variance (highest to lowest).
        """
        factors = {
            group_name: pd.DataFrame(
                group_factors.T, index=self.sample_names[group_name], columns=self.factor_names
            ).iloc[:, self.factor_order if ordered else slice(None)]
            for group_name, group_factors in self._get_sparse("factors", moment, sparse_type).items()
        }
        factors = self._get_component(factors, return_type)

        if return_type == "anndata":
            for group_name, group_adata in factors.items():
                group_adata.obs = pd.concat(self._metadata[group_name].values(), axis=1)
                group_adata.obs = group_adata.obs.loc[:, ~group_adata.obs.columns.duplicated()]

        return factors

    def get_r2(self, total: bool = False, ordered: bool = False) -> pd.DataFrame | dict[str, pd.DataFrame]:
        """Get the fraction of explained variance for each view and group.

        Args:
             total: If `True`, returns a DataFrame with fraction of explained variance for the full
                 model for each group (columns) and view (rows). Otherwise returns a dict with group
                 names as keys containing DataFrames with the fraction of explained variance for each
                 view (columns) and factor(rows).
             ordered: Whether to return the factors ordered by explained variance (highest to lowest).
                 Has no effect if `total == True`.
        """
        if total:
            return self._df_r2_full
        else:
            return {
                group_name: df.set_index(self.factor_names).iloc[self.factor_order if ordered else slice(None), :]
                for group_name, df in self._df_r2_factors.items()
            }

    def get_significant_factor_annotations(self) -> dict[str, pd.DataFrame] | None:
        """Get the results of significance testing of annotations against factors.

        The significance testing is an implementation of PCGSE :cite:p:`pmid26300978`. While
        originally intended to assign annotations to uninformed factors, here it is used
        as a diagnostic plot to find factors that are mismatched to their annotations.

        Returns:
            PCGSE results for each view or `None` if the model does not have prior annotations.
        """
        return self._pcgse

    def get_weights(
        self,
        return_type: Literal["pandas", "anndata", "numpy"] = "pandas",
        moment: Literal["mean", "std"] = "mean",
        sparse_type: Literal["raw", "mix", "thresh"] = "mix",
        ordered: bool = False,
    ) -> _ResultsTypeDF:
        """Get the weight matrices W for each view.

        Args:
             return_type: Format of the returned object.
             moment: Which moment of the posterior distribution to return.
             sparse_type: How to handle sparsity when using the spike and slab prior.

                 - raw: Do nothing, return inferred values for all entries.
                 - mix: Return the corresponding moment of a mixture distribution of two
                   Normal distributions: One centered at 0 and the other centered at the
                   inferred non-sparse value. The mixture is weighted by the inferred
                   sparsity probability. This is what MOFA does.
                 - thresh: Set all values with a sparsity probablity > 0.5 to 0.

             ordered: Whether to return the factors ordered by explained variance (highest to lowest).
        """
        weights = {
            view_name: pd.DataFrame(view_weights, index=self.factor_names, columns=self.feature_names[view_name]).iloc[
                self.factor_order if ordered else slice(None), :
            ]
            for view_name, view_weights in self._get_sparse("weights", moment, sparse_type).items()
        }

        return self._get_component(weights, return_type)

    def get_sparse_factor_probabilities(
        self, return_type: Literal["pandas", "anndata", "numpy"] = "pandas", ordered: bool = False
    ) -> _ResultsTypeDF:
        """Get the probabilties that a factor value is non-sparse for each group with a spike and slab factor prior.

        Args:
             return_type: Format of the returned object.
             ordered: Whether to return the factors ordered by explained variance (highest to lowest).
        """
        probs = {
            group_name: pd.DataFrame(group_prob.T, index=self.sample_names[group_name], columns=self.factor_names).iloc[
                :, self.factor_order if ordered else slice(None)
            ]
            for group_name, group_prob in self._sparse_factors_probabilities.items()
        }
        return self._get_component(probs, return_type)

    def get_sparse_weight_probabilities(
        self, return_type: Literal["pandas", "anndata", "numpy"] = "pandas", ordered: bool = False
    ) -> _ResultsTypeDF:
        """Get the probabilties that a weight value is non-sparse for each view with a spike and slab view prior.

        Args:
             return_type: Format of the returned object.
             ordered: Whether to return the factors ordered by explained variance (highest to lowest).
        """
        probs = {
            view_name: pd.DataFrame(view_prob, index=self.factor_names, columns=self.feature_names[view_name]).iloc[
                self.factor_order if ordered else slice(None), :
            ]
            for view_name, view_prob in self._sparse_weights_probabilities.items()
        }
        return self._get_component(probs, return_type)

    def get_dispersion(
        self, return_type: Literal["pandas", "anndata", "numpy"] = "pandas", moment: Literal["mean", "std"] = "mean"
    ) -> _ResultsTypeSeries:
        """Get the dispersion vectors for each view.

        Args:
             return_type: Format of the returned object.
             moment: Which moment of the posterior distribution to return.
        """
        dispersion = {
            view_name: pd.Series(view_dispersion, index=self.feature_names[view_name])
            for view_name, view_dispersion in getattr(self._dispersions, moment).items()
        }

        return self._get_component(dispersion, return_type)

    def get_gps(
        self,
        return_type: Literal["pandas", "anndata", "numpy"] = "pandas",
        moment: Literal["mean", "std"] = "mean",
        x: dict[str, np.ndarray | torch.Tensor] | None = None,
        batch_size: int | None = None,
        ordered: bool = False,
    ) -> _ResultsTypeDF:
        """Get all latent functions.

        Args:
             return_type: Format of the returned object.
             moment: Which moment of the posterior distribution to return.
             x: Covariate values for each group. If `None`, will return latent function values at
                 covariate coordinates used for training.
             batch_size: Minibatch size. Only has an effect if `x` is not `None`. Defaults to the
                 minibatch size used for training.
             ordered: Whether to return the factors ordered by explained variance (highest to lowest).
        """
        gps = getattr(self._gps if x is None else self._get_gps(x, batch_size), moment)
        gps = {
            group_name: pd.DataFrame(
                group_f[self.factor_order if ordered else slice(None), :].T, columns=self.factor_names
            )
            for group_name, group_f in gps.items()
        }

        if x is None:
            for gname, df in gps.items():
                df.set_index(np.asarray(self.sample_names[gname]), inplace=True)

        return self._get_component(gps, return_type)

    def _get_gps(self, x: dict[str, np.ndarray | torch.Tensor], batch_size: int | None = None):
        if batch_size is None:
            batch_size = self._train_opts.batch_size
        gps = MeanStd({}, {})
        if self._gp is not None:
            with (
                torch.inference_mode(),
                self._train_opts.device,
            ):  # FIXME: allow user to run this in a `with device` context?
                for group_idx, group_name in enumerate(self._gp_group_names):
                    gidx = torch.as_tensor(group_idx)
                    gdata = x[group_name]
                    mean, std = [], []

                    for start_idx in range(0, gdata.shape[0], batch_size):
                        end_idx = min(start_idx + batch_size, gdata.shape[0])
                        minibatch = gdata[start_idx:end_idx]

                        gp_dist = self._gp(
                            (gidx.expand(minibatch.shape[0], 1), torch.as_tensor(minibatch, dtype=torch.float32)),
                            prior=False,
                        )

                        mean.append(gp_dist.mean.cpu().numpy().squeeze())
                        std.append(gp_dist.stddev.cpu().numpy().squeeze())

                    gps.mean[group_name] = np.concatenate(mean, axis=1)
                    gps.std[group_name] = np.concatenate(std, axis=1)
        return gps

    def get_annotations(
        self, return_type: Literal["pandas", "anndata", "numpy"] = "pandas", ordered=False
    ) -> _ResultsTypeDF:
        """Get the annotation matrices for each view.

        Args:
            return_type: Format of the returned object.
            ordered: Whether to return the factors ordered by explained variance (highest to lowest).
        """
        informed_factors = slice(self.n_dense_factors, self.n_dense_factors + self.n_informed_factors)
        annotations = {
            k: pd.DataFrame(v, index=self.factor_names[informed_factors], columns=self.feature_names[k])
            .astype(bool)
            .iloc[np.argsort(np.argsort(self.factor_order[informed_factors])) if ordered else slice(None), :]
            for k, v in self._annotations.items()
        }

        return self._get_component(annotations, return_type)

    def _setup_device(self, device):
        device = torch.device(device)
        tens = torch.tensor(())
        try:
            tens.to(device)
        except (RuntimeError, AssertionError):
            default_device = tens.device
            _logger.warning(f"Device {str(device)} is not available. Using default device: {default_device}")
            device = default_device

        return device

    def impute_data(self, data: MuData | dict[str, dict[str, AnnData]], missing_only=False) -> dict[dict[str, AnnData]]:
        """Impute values in the training data using the trained factorization.

        Args:
            data: The data the model was trained on.
            missing_only: Only impute missing values in the data.

        Returns:
            Nested dictionary of AnnData objects with either fully imputed data or with only the missing values filled in.
            In both cases, the returned data will be preprocessed. In the case of Gaussian distributed data, that involves
            centering and scaling.
        """
        data = self._mofaflexdataset(data)

        factors = self.get_factors(return_type="numpy")
        weights = self.get_weights(return_type="numpy")

        return data.apply(
            impute,
            view_kwargs={
                "weights": weights,
                "feature_names": self.feature_names,
                "likelihood": self._model_opts.likelihoods,
            },
            group_kwargs={"factors": factors, "sample_names": self.sample_names},
            missingonly=missing_only,
            preprocessor=data.preprocessor,
        )

    def _save(
        self,
        path: str | Path,
        mofa_compat: MOFACompatOption = False,
        data: dict[str, dict[str, AnnData]] | None = None,
        intercepts: dict[str, dict[str, np.ndarray]] | None = None,
    ):
        state = {
            "weights": self._weights._asdict(),
            "factors": self._factors._asdict(),
            "covariates": self._covariates,
            "covariates_names": self._covariates_names,
            "n_guiding_vars": self._n_guiding_vars,
            "df_r2_full": self._df_r2_full,
            "df_r2_factors": self._df_r2_factors,
            "pcgse": self._pcgse,
            "n_dense_factors": self._n_dense_factors,
            "n_informed_factors": self._n_informed_factors,
            "factor_names": self._factor_names,
            "factor_order": self._factor_order,
            "sparse_factors_probabilities": self._sparse_factors_probabilities,
            "sparse_weights_probabilities": self._sparse_weights_probabilities,
            "sparse_factors_precisions": self._sparse_factors_precisions._asdict(),
            "sparse_weights_precisions": self._sparse_weights_precisions._asdict(),
            "gps": self._gps._asdict(),
            "dispersions": self._dispersions._asdict(),
            "train_loss_elbo": self._train_loss_elbo,
            "group_names": self._group_names,
            "view_names": self._view_names,
            "feature_names": self._feature_names,
            "sample_names": self._sample_names,
            "annotations": self._annotations,
            "metadata": self._metadata,
            "data_opts": asdict(self._data_opts),
            "model_opts": asdict(self._model_opts),
            "train_opts": asdict(self._train_opts),
            "gp_opts": asdict(self._gp_opts),
            "preprocessor_state": self._preprocessor_state,
        }
        state["train_opts"]["device"] = str(state["train_opts"]["device"])
        state["model_opts"]["likelihoods"] = {
            view_name: str(likelihood) for view_name, likelihood in state["model_opts"]["likelihoods"].items()
        }
        if hasattr(self, "_orig_covariates"):
            state["orig_covariates"] = self._orig_covariates

        pickle = None
        if self._gp is not None and self._gp_group_names is not None:
            pickle = self._gp.state_dict()
            state["gp_group_names"] = self._gp_group_names
        save_model(state, pickle, path, mofa_compat, self, data, intercepts)

    @classmethod
    def load(cls, path: str | Path, map_location=None) -> "MOFAFLEX":
        """Load a saved MOFAFLEX model.

        Args:
            path: Path to the saved model file.
            map_location: Specify how to remap storage locations for PyTorch tensors. See the `torch.load`
                documentation for details.
        """
        state, pickle = load_model(path, map_location)

        if map_location is not None:
            state["train_opts"]["device"] = map_location
        state["model_opts"]["likelihoods"] = {
            view_name: Likelihood.get(likelihood)
            for view_name, likelihood in state["model_opts"]["likelihoods"].items()
        }

        model = cls.__new__(cls)
        model._weights = MeanStd(**state["weights"])
        model._factors = MeanStd(**state["factors"])
        model._covariates = state.get("covariates")
        if "orig_covariates" in state:
            model._orig_covariates = state["orig_covariates"]
        model._covariates_names = state.get("covariates_names")
        model._n_guiding_vars = state.get("n_guiding_vars")
        model._df_r2_full = state["df_r2_full"]
        model._df_r2_factors = state["df_r2_factors"]
        model._pcgse = state.get("pcgse")
        model._n_dense_factors = state["n_dense_factors"]
        model._n_informed_factors = state["n_informed_factors"]
        model._factor_names = state["factor_names"]
        model._factor_order = state["factor_order"]
        model._sparse_factors_probabilities = state["sparse_factors_probabilities"]
        model._sparse_weights_probabilities = state["sparse_weights_probabilities"]
        model._sparse_factors_precisions = MeanStd(**state["sparse_factors_precisions"])
        model._sparse_weights_precisions = MeanStd(**state["sparse_weights_precisions"])
        model._gps = MeanStd(**state["gps"])
        model._dispersions = MeanStd(**state["dispersions"])
        model._train_loss_elbo = state["train_loss_elbo"]
        model._group_names = state["group_names"]
        if "gp_group_names" in state:
            model._gp_group_names = state["gp_group_names"]
        model._view_names = state["view_names"]
        model._feature_names = state["feature_names"]
        model._sample_names = state["sample_names"]
        model._annotations = state.get("annotations")
        model._metadata = state["metadata"]
        model._data_opts = DataOptions(**state["data_opts"])
        model._model_opts = ModelOptions(**state["model_opts"])
        model._train_opts = TrainingOptions(**state["train_opts"])
        model._gp_opts = SmoothOptions(**state["gp_opts"])
        model._preprocessor_state = state["preprocessor_state"]

        model._setup_gp(full_setup=False)
        if model._gp is not None and len(pickle):
            model._gp.load_state_dict(pickle)

        return model
