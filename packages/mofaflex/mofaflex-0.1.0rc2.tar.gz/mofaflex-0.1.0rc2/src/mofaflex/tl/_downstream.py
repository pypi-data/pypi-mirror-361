import logging

import numpy as np
import pandas as pd
from anndata import AnnData
from mudata import MuData
from numpy.typing import NDArray
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

from .._core import MOFAFLEX, MofaFlexDataset, pcgse_test

_logger = logging.getLogger(__name__)


def test_annotation_significance(
    model: MOFAFLEX,
    annotations: dict[str, pd.DataFrame],
    data: MuData | dict[str, dict[str, AnnData]] | MofaFlexDataset | None = None,
    corr_adjust: bool = True,
    p_adj_method: str = "fdr_bh",
    min_size: int = 10,
    subsample: int = 1000,
) -> dict[str, pd.DataFrame]:
    """Test feature sets for significant associations with model factors.

    This is an implementation of PCGSE :cite:p:`pmid26300978`.

    Args:
        model: The MOFA-FLEX model.
        annotations: Boolean dataframe with feature sets in each row for each view.
        data: The data that the model was trained on. Only required if `corr_adjust=True`.
        corr_adjust: Whether to adjust for correlations between features.
        p_adj_method: Method for multiple testing adjustment.
        min_size: Minimum size threshold for feature sets.
        subsample: Work with a random subsample of the data to speed up testing. Set to 0 to use
            all data (may use excessive amounts of memory). Only relevant if `corr_adjust=True`.

    Returns:
        PCGSE results for each view.
    """
    if corr_adjust and data is None:
        raise ValueError("`data` cannot be `None` if `corr_adjust=True`.")

    if data is not None and not isinstance(data, MofaFlexDataset):
        data = model._mofaflexdataset(data)
    annotations = {
        view_name: annot.loc[:, features].astype(bool)
        for view_name, annot in annotations.items()
        if view_name in model.view_names
        and (features := annot.columns.intersection(model.feature_names[view_name])).size > 0
    }

    if len(annotations) > 0:
        return pcgse_test(
            data,
            model._model_opts.nonnegative_weights,
            annotations,
            model.get_weights("pandas"),
            corr_adjust=corr_adjust,
            p_adj_method=p_adj_method,
            min_size=min_size,
            subsample=subsample,
        )
    else:
        return {}


def match(reference: NDArray, permutable: NDArray, axis: int) -> tuple[NDArray[int], NDArray[int], NDArray[np.uint8]]:
    """Find optimal permutation and signs to match two tensors along specified axis.

    Finds the permutation and sign of permutable along one axis to maximize
    correlation with reference. Useful for comparing ground truth factor scores/loadings
    with inferred values where factor order and sign is arbitrary.

    Args:
        reference: Reference array to match against.
        permutable: Array to be permuted and sign-adjusted.
        axis: Axis along which to perform matching.

    Returns:
        A tuple with optimal permutation indices and optimal signs (+1 or -1) for each
        permuted element.

    Notes:
        - Special handling for non-negative arrays
        - Uses linear sum assignment to find optimal matching
    """
    nonnegative = np.all(reference >= 0) and np.all(permutable >= 0)
    one_d = reference.ndim == 1 or np.all(np.delete(reference.shape, axis) == 1)

    reference = np.moveaxis(reference, axis, -1).reshape(-1, reference.shape[axis]).T
    permutable = np.moveaxis(permutable, axis, -1).reshape(-1, permutable.shape[axis]).T

    signs = np.ones(shape=permutable.shape[0], dtype=np.int8)
    if not one_d:
        correlation = 1 - cdist(reference, permutable, metric="correlation")
        correlation = np.nan_to_num(correlation, 0)

        reference_ind, permutable_ind = linear_sum_assignment(-1 * np.abs(correlation))

        # if correlation is negative, flip the sign of the corresponding column
        for k in range(signs.shape[0]):
            if correlation[reference_ind, permutable_ind][k] < 0 and not nonnegative:
                signs[k] *= -1
    else:
        difference = cdist(reference, permutable, metric="euclidean")
        reference_ind, permutable_ind = linear_sum_assignment(difference)

    return reference_ind, permutable_ind, signs
