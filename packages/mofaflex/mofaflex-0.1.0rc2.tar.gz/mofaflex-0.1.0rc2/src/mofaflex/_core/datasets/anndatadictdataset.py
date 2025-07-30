import logging
from collections.abc import Callable
from functools import reduce
from typing import Any, Literal, TypeVar, Union

import anndata as ad
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy import sparse

from ..settings import settings
from .base import ApplyCallable, ApplyToCallable, MofaFlexDataset, Preprocessor
from .utils import AlignmentMap, anndata_to_dask, apply_to_nested, from_dask, have_dask, warn_dask

T = TypeVar("T")
_logger = logging.getLogger(__name__)


class AnnDataDictDataset(MofaFlexDataset):
    # There are 3 different alignments to consider: Global, local, and data. In particular, the user may provide a
    # global alignment in sample_names or feature_names that is a proper superset of the data (i.e. it has names not
    # present in any of the AnnData objects). Similarly, the global alignment may only capture a subset of the data.
    # this is the case when use_obs="intersection" or use_var="intersection", as well as due to a global alignment
    # given in sample_names or feature_names. The local alignment is defined to always be a subset of the global
    # alignment, and the data is subsetted (but not reordered) when necessary. The following picture illustrates this:
    #
    # global:           🞓🞓🞓🞓🞓🞓🞓
    #                   ｜\/
    #                   ｜/\
    # data:     🞓🞓🞓🞓🞓🞓🞓🞓🞓
    #                   ｜|｜
    # local:            🞓🞓🞓
    #
    # apply() is guaranteed to pass local views of the data to `func`. To achieve this, we compute two aligment maps:
    # data_to_global = data.get_indexer(global)
    # global_to_data = global.get_indexer(data)
    #
    # A local view of the data is given by data[global_to_data >= 0].
    # The corresponding nonmissing indices for __getitems__ are available as global_to_data[global_to_data >= 0]
    #
    # If we get a global index vector in __getitems__, we do need to reorder the data accordingly. The corresponding
    # view of the data is obtained as data[data_to_global_map[data_to_global_map[global_idx] >= 0]].
    # The corresponding nonmissing indices are given by nonzero(data_to_global_map[global_idx] >= 0)
    #
    # A map from local to global views is given by argsort(global_to_data[global_to_data >= 0])
    def __init__(
        self,
        data: dict[str, dict[str, ad.AnnData]],
        *,
        use_obs: Literal["union", "intersection"] = "union",
        use_var: Literal["union", "intersection"] = "union",
        preprocessor: Preprocessor | None = None,
        cast_to: Union[np.ScalarType] | None = np.float32,  # noqa UP007
        sample_names: dict[str, NDArray[str]] | None = None,
        feature_names: dict[str, NDArray[str]] | None = None,
        **kwargs,
    ):
        super().__init__(data, preprocessor=preprocessor, cast_to=cast_to)
        self._use_obs = use_obs
        self._use_var = use_var

        self.reindex_samples(sample_names)
        self.reindex_features(feature_names)

    def _reindex_attr(self, attr: Literal["obs", "var"], aligned: dict[str, NDArray[str]] | None = None):
        if aligned is None:
            aligned = getattr(self, f"_aligned_{attr}")
        map = {}
        for group_name, group in self._data.items():
            gmap = {}
            for view_name, view in group.items():
                vnames = getattr(view, f"{attr}_names")
                caligned = aligned[group_name if attr == "obs" else view_name]

                if caligned.size != vnames.size or not np.all(caligned == vnames):
                    d2g_map = vnames.get_indexer(caligned)
                    g2d_map = caligned.get_indexer(vnames)
                    gmap[view_name] = AlignmentMap(d2g=d2g_map, g2d=g2d_map)
            map[group_name] = gmap
        setattr(self, f"_{attr}map", map)

    def reindex_samples(self, sample_names: dict[str, NDArray[str]] | None = None):
        union = lambda x, y: x.union(y, sort=False)
        aligned = {}
        if sample_names is not None:
            self._used_obs = "union"
            for group_name, group in self._data.items():
                cnames = sample_names.get(group_name)
                if cnames is not None:
                    cunion = reduce(union, (view.obs_names for view in group.values()))
                    cnames = pd.Index(cnames)
                    if not cnames.isin(cunion).all():
                        _logger.warning(
                            f"Not all sample names given for group {group_name} are present in the data. Restricting alignment to sample names present in the data."
                        )
                        cnames = cnames.intersection(cunion)
                    aligned[group_name] = cnames
                else:
                    aligned[group_name] = reduce(union, (view.obs_names for view in group.values()))
        else:
            self._used_obs = self._use_obs
            for group_name, group in self._data.items():
                aligned[group_name] = reduce(
                    union if self._use_obs == "union" else lambda x, y: x.intersection(y),
                    (view.obs_names for view in group.values()),
                )

        self._aligned_obs = aligned
        self._reindex_attr("obs", aligned)

    def reindex_features(self, feature_names: dict[str, NDArray[str]] | None = None):
        union = lambda x, y: x.union(y)
        aligned = {}
        if feature_names is not None:
            self._used_var = "union"
            for view_name in self.view_names:
                cunion = reduce(
                    union, (group[view_name].var_names for group in self._data.values() if view_name in group)
                )
                cnames = feature_names.get(view_name)
                if cnames is not None:
                    cnames = pd.Index(cnames)
                    if not cnames.isin(cunion).all():
                        _logger.warning(
                            f"Not all feature names given for view {view_name} are present in the data. Restricting alignment to feature names present in the data."
                        )
                        cnames = cnames.intersection(cunion)
                    aligned[view_name] = cnames
                else:
                    aligned[view_name] = reduce(
                        union, (group[view_name].var_names for group in self._data.values() if view_name in group)
                    )
        else:
            self._used_var = self._use_var
            for view_name in self.view_names:
                aligned[view_name] = reduce(
                    union if self._use_var == "union" else lambda x, y: x.intersection(y),
                    (group[view_name].var_names for group in self._data.values() if view_name in group),
                )

        self._aligned_var = aligned
        self._reindex_attr("var", aligned)

    @staticmethod
    def _accepts_input(data):
        return isinstance(data, dict) and all(
            isinstance(group, dict) and all(isinstance(view, ad.AnnData) for view in group.values())
            for group in data.values()
        )

    @property
    def n_features(self) -> dict[str, int]:
        return {view_name: var.size for view_name, var in self._aligned_var.items()}

    @property
    def n_samples(self) -> dict[str, int]:
        return {group_name: obs.size for group_name, obs in self._aligned_obs.items()}

    @property
    def view_names(self) -> NDArray[str]:
        return np.asarray(tuple(reduce(lambda x, y: x | y, (group.keys() for group in self._data.values()))))

    @property
    def group_names(self) -> NDArray[str]:
        return np.asarray(tuple(self._data.keys()))

    @property
    def sample_names(self) -> dict[str, NDArray[str]]:
        return {group_name: obs.to_numpy() for group_name, obs in self._aligned_obs.items()}

    @property
    def feature_names(self) -> dict[str, NDArray[str]]:
        return {view_name: var.to_numpy() for view_name, var in self._aligned_var.items()}

    def __getitems__(self, idx: dict[str, int | list[int]]) -> dict[str, dict]:
        data = {}
        nonmissing_obs = {}
        nonmissing_var = {}
        for group_name, group_idx in idx.items():
            group = {}
            gobsmap = self._obsmap[group_name]
            gvarmap = self._varmap[group_name]
            gnonmissing_obs = {}
            gnonmissing_var = {}
            for view_name, view in self._data[group_name].items():
                if view_name in gvarmap:
                    varmap = gvarmap[view_name].d2g
                    varidx = varmap >= 0
                    cvarmap = varmap[varidx]
                    cnonmissing_var = np.nonzero(varidx)[0]
                else:
                    cnonmissing_var = cvarmap = slice(None)

                if view_name in gobsmap:
                    obsmap = gobsmap[view_name].d2g[group_idx]
                    obsidx = obsmap >= 0
                    cobsmap = obsmap[obsidx]
                    cnonmissing_obs = np.nonzero(obsidx)[0]
                else:
                    cobsmap = group_idx
                    cnonmissing_obs = slice(None)

                if not isinstance(cvarmap, slice) and not isinstance(cobsmap, slice):
                    cobsmap, cvarmap = np.ix_(cobsmap, cvarmap)
                arr = view.X[cobsmap, cvarmap]
                arr, gnonmissing_obs[view_name], gnonmissing_var[view_name] = self.preprocessor(
                    arr, cnonmissing_obs, cnonmissing_var, group_name, view_name
                )
                if self.cast_to is not None:
                    arr = arr.astype(self.cast_to, copy=False)
                if sparse.issparse(arr):
                    arr = arr.toarray()
                group[view_name] = np.asarray(
                    arr
                )  # arr may be an anndata._core.views.ArrayView, which is not recognized by PyTorch
            data[group_name] = group
            idx[group_name] = np.asarray(group_idx)
            nonmissing_obs[group_name] = gnonmissing_obs
            nonmissing_var[group_name] = gnonmissing_var

        return {
            "data": data,
            "sample_idx": idx,
            "nonmissing_samples": nonmissing_obs,
            "nonmissing_features": nonmissing_var,
        }

    def _align_array_to_global(
        self,
        arr: NDArray[T],
        group_name: str,
        view_name: str,
        align_to: Literal["samples", "features"],
        local_indexer: Callable[[AlignmentMap], NDArray[int]],
        axis: int = 0,
        fill_value: np.ScalarType = np.nan,
    ):
        map = (self._obsmap if align_to == "samples" else self._varmap)[group_name].get(view_name)
        if map is None:
            return arr

        outshape = [map.d2g.size]
        outshape.extend(arr.shape[:axis])
        outshape.extend(arr.shape[axis + 1 :])

        arr = np.moveaxis(arr, axis, 0)
        out = np.full(outshape, fill_value=fill_value, dtype=np.promote_types(type(fill_value), arr.dtype), order="C")
        out[map.d2g >= 0, ...] = arr[local_indexer(map), ...]
        return np.moveaxis(out, 0, axis)

    def _align_data_array_to_global(
        self,
        arr: NDArray[T],
        group_name: str,
        view_name: str,
        align_to: Literal["samples", "features"],
        axis: int = 0,
        fill_value: np.ScalarType = np.nan,
    ):
        return self._align_array_to_global(
            arr, group_name, view_name, align_to, lambda map: map.d2g[map.d2g >= 0], axis, fill_value
        )

    def align_local_array_to_global(
        self,
        arr: NDArray[T],
        group_name: str,
        view_name: str,
        align_to: Literal["samples", "features"],
        axis: int = 0,
        fill_value: np.ScalarType = np.nan,
    ):
        return self._align_array_to_global(
            arr, group_name, view_name, align_to, lambda map: np.argsort(map.g2d[map.g2d >= 0]), axis, fill_value
        )

    def align_global_array_to_local(
        self, arr: NDArray[T], group_name: str, view_name: str, align_to: Literal["samples", "features"], axis: int = 0
    ) -> NDArray[T]:
        map = (self._obsmap if align_to == "samples" else self._varmap)[group_name].get(view_name)
        if map is None:
            return arr
        map = map.g2d
        return np.take(arr, map[map >= 0], axis=axis)

    def map_local_indices_to_global(
        self, idx: NDArray[int], group_name: str, view_name: str, align_to: Literal["samples, features"]
    ) -> NDArray[int]:
        map = (self._obsmap if align_to == "samples" else self._varmap)[group_name].get(view_name)
        if map is None:
            return idx
        return map.g2d[map.g2d >= 0][idx]

    def map_global_indices_to_local(
        self, idx: NDArray[int], group_name: str, view_name: str, align_to: Literal["samples, features"]
    ) -> NDArray[int]:
        map = (self._obsmap if align_to == "samples" else self._varmap)[group_name].get(view_name)
        if map is None:
            return idx
        idx = map.d2g[idx]
        return idx - np.cumsum(map.g2d < 0)[idx]  # this is for use_obs="intersection"

    def _get_attr(self, attr: Literal["obs", "var"]) -> dict[str, pd.DataFrame]:
        return {
            group_name: {
                view_name: getattr(view, attr)
                .reindex(
                    getattr(self, f"_aligned_{attr}")[group_name if attr == "obs" else view_name], fill_value=pd.NA
                )
                .apply(lambda x: x.astype("string") if x.dtype == "O" else x, axis=1)
                for view_name, view in group.items()
            }
            for group_name, group in self._data.items()
        }

    def get_obs(self) -> dict[str, pd.DataFrame]:
        return self._get_attr("obs")

    def get_missing_obs(self) -> pd.DataFrame:
        dfs = []
        for group_name, group in self._data.items():
            for view_name, view in group.items():
                if sparse.issparse(view.X):
                    viewmissing = view.X.copy()
                    viewmissing.data = np.isnan(viewmissing.data)
                    viewmissing = ~(np.asarray(viewmissing.sum(axis=1)).squeeze() == 0)
                else:
                    viewmissing = np.isnan(view.X).all(axis=1)
                viewmissing = self.align_local_array_to_global(
                    viewmissing, group_name, view_name, "samples", fill_value=True
                )
                dfs.append(
                    pd.DataFrame(
                        {
                            "view": view_name,
                            "group": group_name,
                            "obs_name": self._aligned_obs[group_name],
                            "missing": viewmissing,
                        }
                    )
                )
        return pd.concat(dfs, axis=0, ignore_index=True)

    def get_covariates(
        self, obs_key: dict[str, str] | None = None, obsm_key: dict[str, str] | None = None
    ) -> tuple[dict[str, dict[str, NDArray]], dict[str, NDArray]]:
        covariates, covariates_names = {}, {}
        if obs_key is None:
            obs_key = {}
        if obsm_key is None:
            obsm_key = {}
        for group_name, group in self._data.items():
            obskey = obs_key.get(group_name, None)
            obsmkey = obsm_key.get(group_name, None)
            if obskey is None and obsmkey is None:
                continue
            if obskey and obsmkey:
                raise ValueError(
                    f"Provide either covariates_obs_key or covariates_obsm_key for group {group_name}, not both."
                )

            ccovs = {}
            if obskey is not None:
                for view_name, view in group.items():
                    if obskey in view.obs.columns:
                        ccovs[view_name] = self._align_data_array_to_global(
                            view.obs[obskey].to_numpy(), group_name, view_name, "samples"
                        )[:, None]
                if len(ccovs):
                    covariates_names[group_name] = obskey
                else:
                    _logger.warn(f"No covariate data found in obs attribute for group {group_name}.")
            elif obsmkey is not None:
                covar_dim = []
                for view_name, view in group.items():
                    if obsmkey in view.obsm:
                        covar = view.obsm[obsmkey]
                        if isinstance(covar, pd.DataFrame):
                            covariates_names[group_name] = covar.columns.to_numpy()
                        elif isinstance(covar, pd.Series):
                            covariates_names[group_name] = np.asarray(covar.name, dtype=object)

                        covar = np.asarray(covar)
                        if covar.ndim == 1:
                            covar = covar[..., None]
                        covar_dim.append(covar.shape[1])
                        ccovs[view_name] = self._align_data_array_to_global(covar, group_name, view_name, "samples")
                if len(set(covar_dim)) > 1:
                    raise ValueError(
                        f"Number of covariate dimensions in group {group_name} must be the same across views."
                    )

            covariates[group_name] = ccovs
        return covariates, covariates_names

    def get_annotations(self, varm_key: dict[str, str]) -> tuple[dict[str, NDArray], dict[str, NDArray]]:
        annotations, annotations_names = {}, {}
        if varm_key is not None:
            for view_name, key in varm_key.items():
                cannot = []
                for group_name, group in self._data.items():
                    if key in group[view_name].varm:
                        annot = group[view_name].varm[key]
                        if isinstance(annot, pd.DataFrame):
                            annotations_names[view_name] = annot.columns
                            annot = annot.to_numpy()
                        fill_value = False if annot.dtype == np.bool_ else np.nan
                        cannot.append(
                            self._align_data_array_to_global(
                                annot, group_name, view_name, "features", fill_value=fill_value
                            ).T
                        )
                if all(a.dtype == np.bool_ for a in cannot):
                    annotations[view_name] = reduce(np.logical_or, cannot)
                else:
                    annotations[view_name] = np.nanmean(np.stack(cannot, axis=0), axis=0)

        return annotations, annotations_names

    def _view_for_apply(self, group_name: str, view_name: str) -> ad.AnnData:
        havedask = have_dask()
        if not havedask and settings.use_dask:
            warn_dask(_logger)

        view = self._data[group_name].get(view_name)
        if view is not None:
            gobsmap = self._obsmap[group_name]
            gvarmap = self._varmap[group_name]
            vobsmap = gobsmap.get(view_name)
            vvarmap = gvarmap.get(view_name)
            if vobsmap is not None or vvarmap is not None:
                if havedask and settings.use_dask:
                    view = anndata_to_dask(view)
                obsidx = slice(None) if vobsmap is None else vobsmap.g2d >= 0
                varidx = slice(None) if vvarmap is None else vvarmap.g2d >= 0
                view = view[obsidx, varidx]

        return view

    def _apply_to_view(
        self, view_name: str, func: ApplyToCallable[T], gkwargs: dict[str, dict[str, Any]], **kwargs
    ) -> dict[str, T]:
        ret = {}
        for group_name in self.group_names:
            view = self._view_for_apply(group_name, view_name)
            if view is not None:
                cret = func(view, group_name, **kwargs, **gkwargs[group_name])
                ret[group_name] = apply_to_nested(cret, from_dask)
        return ret

    def _apply_to_group(
        self, group_name: str, func: ApplyToCallable[T], vkwargs: dict[str, dict[str, Any]], **kwargs
    ) -> dict[str, T]:
        ret = {}
        for view_name in self.view_names:
            view = self._view_for_apply(group_name, view_name)
            if view is not None:
                cret = func(view, view_name, **kwargs, **vkwargs[view_name])
                ret[group_name] = apply_to_nested(cret, from_dask)
        return ret

    def _apply_by_group_view(
        self, func: ApplyCallable[T], gvkwargs: dict[str, dict[str, dict[str, Any]]], **kwargs
    ) -> dict[str, dict[str, T]]:
        havedask = have_dask()
        if not havedask and settings.use_dask:
            warn_dask(_logger)
        ret = {}
        for group_name in self.group_names:
            cret = {}
            for view_name in self.view_names:
                view = self._view_for_apply(group_name, view_name)
                if view is not None:
                    ccret = func(view, group_name, view_name, **kwargs, **gvkwargs[group_name][view_name])
                    cret[view_name] = apply_to_nested(ccret, from_dask)
            ret[group_name] = cret
        return ret

    def _apply_by_view(self, func: ApplyCallable[T], vkwargs: dict[str, dict[str, Any]], **kwargs) -> dict[str, T]:
        havedask = have_dask()
        ret = {}
        if not havedask and settings.use_dask:
            warn_dask(_logger)
        for view_name in self.view_names:
            data = {}
            convert = False
            for group_name, group in self._data.items():
                cdata = anndata_to_dask(group[view_name]) if havedask and settings.use_dask else group[view_name]
                obsmap = self._obsmap[group_name].get(view_name)
                if obsmap is not None:
                    cdata = cdata[obsmap.g2d >= 0, :]
                if cdata.n_vars != self.n_features[view_name]:
                    convert = True
                data[group_name] = cdata
            if convert:
                for group_name, cdata in data.items():
                    cdata = cdata.copy()
                    cdata.X = cdata.X.astype(np.promote_types(cdata.X.dtype, type(np.nan)))
                    data[group_name] = cdata
            data = ad.concat(
                data,
                axis="obs",
                join="inner" if self._used_var == "intersection" else "outer",
                label="__group",
                merge="unique",
                uns_merge=None,
                fill_value=np.nan,
            )
            if (
                data.n_vars != self._aligned_var[view_name].size
                or (data.var_names != self._aligned_var[view_name]).any()
            ):
                data = data[:, self._aligned_var[view_name]]

            cret = func(data, data.obs["__group"].to_numpy(), view_name, **kwargs, **vkwargs[view_name])
            ret[view_name] = apply_to_nested(cret, from_dask)

        return ret

    def _apply_by_group(self, func: ApplyCallable[T], gkwargs: dict[str, dict[str, Any]], **kwargs) -> dict[str, T]:
        havedask = have_dask()
        ret = {}
        if not havedask and settings.use_dask:
            warn_dask(_logger)
        for group_name, group in self._data.items():
            data = {}
            convert = False
            gvarmap = self._varmap[group_name]
            for view_name, view in group.items():
                cdata = anndata_to_dask(view) if havedask and settings.use_dask else view
                varmap = gvarmap.get(view_name)
                if varmap is not None:
                    cdata = cdata[:, varmap.g2d >= 0]
                if cdata.n_obs != self.n_samples[group_name]:
                    convert = True
                data[view_name] = cdata
            if convert:
                for view_name, cdata in data.items():
                    cdata = cdata.copy()
                    cdata.X = cdata.X.astype(np.promote_types(cdata.X.dtype, type(np.nan)))
                    data[view_name] = cdata
            data = ad.concat(
                data,
                axis="var",
                join="inner" if self._used_obs == "intersection" else "outer",
                label="__view",
                merge="unique",
                uns_merge=None,
                fill_value=np.nan,
            )
            if (
                data.n_obs != self._aligned_obs[group_name].size
                or (data.obs_names != self._aligned_obs[group_name]).any()
            ):
                data = data[self._aligned_obs[group_name], :]

            cret = func(data, group_name, data.var["__view"].to_numpy(), **kwargs, **gkwargs[group_name])
            ret[group_name] = apply_to_nested(cret, from_dask)

        return ret
