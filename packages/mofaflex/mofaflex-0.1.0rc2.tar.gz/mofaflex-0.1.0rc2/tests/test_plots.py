from functools import partial, wraps

import matplotlib.pyplot as plt
import plotnine
import pytest
from matplotlib.testing.decorators import image_comparison as mpl_image_comparison
from packaging.version import Version

import mofaflex as mfl

image_comparison = partial(
    mpl_image_comparison, extensions=["png"], tol=0.5
)  # tolerance for differences in text rendering
plotnine.options.base_family = "DejaVu Sans"  # bundled with Matplotlib


def plotnine_comparison(*decorator_args, **decorator_kwargs):
    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            plots = func(*args, **kwargs)
            if not isinstance(plots, list) and not isinstance(plots, tuple):
                plots = [plots]
            for plot in plots:
                plt.figure(plot.draw(show=False))

        return pytest.mark.xfail(
            condition=Version(plotnine.__version__).is_prerelease, reason="plotnine pre-release", strict=False
        )(image_comparison(*decorator_args, **decorator_kwargs)(decorated))

    return wrapper


@plotnine_comparison(baseline_images=["overview"])
def test_overview(cll_data):
    return mfl.pl.overview(cll_data)


@plotnine_comparison(baseline_images=["training_curve"])
def test_training_curve(cll_model):
    return mfl.pl.training_curve(cll_model)


@plotnine_comparison(baseline_images=["factor_correlation"])
def test_factor_correlation(cll_model):
    return mfl.pl.factor_correlation(cll_model)


@plotnine_comparison(baseline_images=["variance_explained"])
def test_variance_explained(cll_model):
    return mfl.pl.variance_explained(cll_model)


@plotnine_comparison(
    baseline_images=["factor_significance", "factor_significance_nfactors-5", "factor_significance_alpha-1e-42"]
)
def test_factor_significance(mousebrain_model):
    return (
        mfl.pl.factor_significance(mousebrain_model, figsize=(8, 5)),
        mfl.pl.factor_significance(mousebrain_model, n_factors=5, figsize=(8, 5)),
        mfl.pl.factor_significance(mousebrain_model, alpha=1e-42, figsize=(8, 5)),
    )


@plotnine_comparison(baseline_images=["all_weights", "all_weights_Mutations", "all_weights_Mutations_mRNA"])
def test_all_weights(cll_model):
    return (
        mfl.pl.all_weights(cll_model),
        mfl.pl.all_weights(cll_model, views="Mutations"),
        mfl.pl.all_weights(cll_model, views=["Mutations", "mRNA"]),
    )


@plotnine_comparison(baseline_images=["factor"])
def test_factor(cll_model):
    return mfl.pl.factor(cll_model)


@plotnine_comparison(
    baseline_images=[
        "top_weights",
        "top_weights_features-5",
        "top_weights_view-Mutations",
        "top_weights_views-Mutations-mRNA",
        "top_weights_factor-1",
        "top_weights_factors-1-7",
        "top_weights_view-Mutations_factor_1",
        "top_weights_nrows-2",
    ]
)
def test_top_weights(cll_model):
    return (
        mfl.pl.top_weights(cll_model, figsize=(20, 20)),
        mfl.pl.top_weights(cll_model, n_features=5, figsize=(20, 20)),
        mfl.pl.top_weights(cll_model, views="Mutations", figsize=(20, 20)),
        mfl.pl.top_weights(cll_model, views=["Mutations", "mRNA"], figsize=(20, 20)),
        mfl.pl.top_weights(cll_model, factors=1),
        mfl.pl.top_weights(cll_model, factors=["Factor 1", "Factor 7"]),
        mfl.pl.top_weights(cll_model, views="Mutations", factors=1),
        mfl.pl.top_weights(cll_model, nrow=2, figsize=(20, 5)),
    )


@plotnine_comparison(
    baseline_images=[
        "weights",
        "weights_features-5",
        "weights_view-Mutations",
        "weights_views-Mutations-mRNA",
        "weights_factor-1",
        "weights_factors-1-7",
        "weights_view-Mutations_factor_1",
        "weights_views-Mutations-mRNA_nrows-3",
    ]
)
def test_weights(cll_model):
    return (
        mfl.pl.weights(cll_model, figsize=(40, 20)),
        mfl.pl.weights(cll_model, n_features=5, figsize=(40, 20)),
        mfl.pl.weights(cll_model, views="Mutations", figsize=(40, 5)),
        mfl.pl.weights(cll_model, views=["Mutations", "mRNA"], figsize=(40, 10)),
        mfl.pl.weights(cll_model, factors=1),
        mfl.pl.weights(cll_model, factors=["Factor 1", "Factor 7"]),
        mfl.pl.weights(cll_model, views="Mutations", factors=1),
        mfl.pl.weights(cll_model, views=["Mutations", "mRNA"], nrow=3, figsize=(30, 15)),
    )


@plotnine_comparison(baseline_images=["weight_sparsity_histogram"])
def test_weight_sparsity_histogram(cll_model):
    return mfl.pl.weight_sparsity_histogram(cll_model)


@plotnine_comparison(baseline_images=["top_weights_annotations"])
def test_top_weights_annotations(mousebrain_model):
    return mfl.pl.top_weights(mousebrain_model, figsize=(20, 20))


@plotnine_comparison(baseline_images=["weights_annotations"])
def test_weights_annotations(mousebrain_model):
    return mfl.pl.weights(mousebrain_model, factors=["Factor 1", "Factor 2", "Astrocytes", "Interneurons"])


@plotnine_comparison(baseline_images=["factors_scatter", "factors_scatter-color"])
def test_factors_scatter(mousebrain_model):
    return mfl.pl.factors_scatter(mousebrain_model, 1, "Astrocytes"), mfl.pl.factors_scatter(
        mousebrain_model, 1, "Astrocytes", color="log1p_total_counts"
    )


@plotnine_comparison(
    baseline_images=[
        "covariates_factor_scatter",
        "covariates_factor_scatter_Astrocytes",
        "covariates_factor_scatter_cov0_color-Astrocytes",
        "covariates_factor_scatter_cov0_color-log1p_total_counts",
        "covariates_factor_scatter_cov1-cov0",
    ]
)
def test_covariates_factor_scatter(mousebrain_model):
    return (
        mfl.pl.covariates_factor_scatter(mousebrain_model, 1),
        mfl.pl.covariates_factor_scatter(mousebrain_model, "Astrocytes"),
        mfl.pl.covariates_factor_scatter(mousebrain_model, 1, covariate_dims=0, color="Astrocytes"),
        mfl.pl.covariates_factor_scatter(mousebrain_model, 1, covariate_dims=0, color="log1p_total_counts"),
        mfl.pl.covariates_factor_scatter(mousebrain_model, 1, covariate_dims=(1, 0)),
    )


@plotnine_comparison(baseline_images=["factors_covariate-cov0", "factors_covariate-cov1-cov0"])
def test_factors_covariate(mousebrain_model):
    return mfl.pl.factors_covariate(mousebrain_model, 0, figsize=(60, 4)), mfl.pl.factors_covariate(
        mousebrain_model, 1, 0, figsize=(60, 4)
    )


@plotnine_comparison(baseline_images=["gp_covariate"])
def test_gp_covariate(mousebrain_model):
    return mfl.pl.gp_covariate(mousebrain_model, size=0.25, figsize=(60, 4))


@plotnine_comparison(baseline_images=["smoothness"])
def test_smoothness(mousebrain_model):
    return mfl.pl.smoothness(mousebrain_model, figsize=(5, 5))
