"""Dispersion estimation for RNA-seq data analysis.

This module provides functionality to estimate dispersion parameters for negative
binomial models from RNA-seq count data. Accurate dispersion estimation is crucial
for differential expression analysis using methods like DESeq2 or edgeR, especially
for datasets with limited replication.

The implementation supports various estimation methods including:
- DESeq2-style estimation with gamma-distributed trend fitting
- EdgeR-style estimation with log-linear trend shrinkage
- Maximum likelihood estimation (MLE)
- Method of moments estimation

All methods support batch processing for efficient computation with large datasets.
"""

import jax.numpy as jnp
import numpy as np
import patsy
import tqdm
from anndata import AnnData

from delnx._logging import logger
from delnx._utils import _get_layer, _to_dense
from delnx.models import DispersionEstimator


def _estimate_dispersion_batched(
    X: jnp.ndarray,
    design_matrix: jnp.ndarray | None = None,
    size_factors: jnp.ndarray | None = None,
    method: str = "full",
    trend_type: str = "parametric",
    min_disp: float = 1e-8,
    max_disp: float = 10.0,
    min_mu: float = 0.5,
    batch_size: int = 2048,
    verbose: bool = True,
) -> jnp.ndarray:
    """Estimate dispersion parameters for negative binomial regression in batches.

    Parameters
    ----------
    X : jnp.ndarray
        Expression data matrix, shape (n_cells, n_features). Should contain raw count data.
    design_matrix : jnp.ndarray | None, default=None
        Design matrix for the model, shape (n_cells, n_covariates).
        If :obj:`None`, a simple intercept model is used.
    size_factors : jnp.ndarray | None, default=None
        Size factors for normalization, shape (n_cells,).
        If :obj:`None`, assumes all samples have equal size.
    method : str, default="full"
        Method for dispersion estimation:
            - "full": Use full DESeq2-style estimation with trend fitting and MAP estimation.
            - "approx": Use approximate estimation by skipping initial MLE fitting.
            - "fast": Fast approximation using only initial dispersion estimates.
    trend_type : str, default="parametric"
        Type of trend to fit for dispersion estimates:
            - "parametric": Fit a parametric trend (e.g., gamma distribution).
            - "mean": Fit a constant mean-dispersion trend.
    min_disp : float, default=1e-8
        Minimum allowed dispersion value.
    max_disp : float, default=10.0
        Maximum allowed dispersion value.
        Note: The threshold that is actually enforced is max(max_disp, n_samples).
    min_mu : float, default=0.5
        Threshold for mean estimates.
    batch_size : int, default=2048
        Number of features to process per batch. Adjust based on available memory.
    verbose : bool, default=True
        Whether to display progress information during computation.

    Returns
    -------
    jnp.ndarray
        Dispersion estimates for each feature, shape (n_features,).
    """
    if design_matrix is None:
        # If no design matrix is provided, use a simple intercept model
        design_matrix = jnp.ones((X.shape[0], 1), dtype=jnp.float64)

    if size_factors is None:
        # If no size factors are provided, assume all samples have equal size
        size_factors = jnp.ones(X.shape[0], dtype=jnp.float64)

    max_disp = max(max_disp, X.shape[0])
    normed_means = np.array((X / size_factors[:, None]).mean(axis=0)).flatten()
    non_zero_mask = normed_means > 0
    n_features = sum(non_zero_mask).item()
    X_use = X[:, non_zero_mask]
    normed_means = jnp.array(normed_means[non_zero_mask], dtype=jnp.float64)

    estimator = DispersionEstimator(
        design_matrix=design_matrix,
        size_factors=size_factors,
        min_disp=min_disp,
        max_disp=max_disp,
        min_mu=min_mu,
    )

    init_dispersions = []
    mle_dispersions = []
    mle_success = []

    logger.info("Fitting initial dispersions", verbose=verbose)

    # Compute genewise estimates in batches
    for i in tqdm.tqdm(range(0, n_features, batch_size), disable=not verbose):
        batch = slice(i, min(i + batch_size, n_features))
        X_batch = jnp.asarray(_to_dense(X_use[:, batch]), dtype=jnp.float32)

        # Fit initial dispersions, mu, and MLE dispersion (genewise)
        disp_init = estimator.fit_initial_dispersions(X_batch)

        if method in ["fast", "approx"]:
            # Skip MLE fitting for fast and approx method
            mle_dispersions.append(disp_init)
            mle_success.append(jnp.zeros_like(disp_init, dtype=bool))
            init_dispersions.append(disp_init)
            continue

        mu_hat = estimator.fit_mu(X_batch)
        disp_mle, success = estimator.fit_dispersion_mle(X_batch, mu_hat, disp_init)

        init_dispersions.append(disp_init)
        mle_dispersions.append(disp_mle)
        mle_success.append(success)

    init_dispersions = jnp.concatenate(init_dispersions, axis=0)
    mle_dispersions = jnp.concatenate(mle_dispersions, axis=0)
    mle_success = jnp.concatenate(mle_success, axis=0)

    if method == "fast":
        # If method is "fast", return initial dispersions only
        return {
            "init_dispersions": init_dispersions,
            "mle_dispersions": None,
            "mle_converged": None,
            "fitted_trend": None,
            "map_dispersions": None,
            "normed_means": normed_means,
            "non_zero_mask": non_zero_mask,
        }

    logger.info("Fitting dispersion trend curve", verbose=verbose)

    # Use MLE dispersions for trend fitting if method is "full", otherwise use initial dispersions
    dispersions_use = mle_dispersions if method == "full" else init_dispersions

    # Fit trend across genes on genewise dispersion estimates
    fitted_trend = estimator.fit_dispersion_trend(
        dispersions_use,
        normed_means,
        trend_type=trend_type,
    )

    # Get prior variance
    prior_disp_var = estimator.fit_dispersion_prior(
        dispersions_use,
        fitted_trend,
    )

    logger.info("Fitting MAP dispersions", verbose=verbose)

    map_dispersions = []

    # Genewise MAP estimation in batches
    for i in tqdm.tqdm(range(0, n_features, batch_size), disable=not verbose):
        batch = slice(i, min(i + batch_size, n_features))
        X_batch = jnp.asarray(_to_dense(X_use[:, batch]), dtype=jnp.float32)

        # Fit mu and MAP dispersions
        mu_hat = estimator.fit_mu(X_batch)
        map_disp, _ = estimator.fit_MAP_dispersions(
            X_batch, dispersions_use[batch], fitted_trend[batch], mu_hat, prior_disp_var
        )

        map_dispersions.append(map_disp)

    map_dispersions = jnp.concatenate(map_dispersions, axis=0)

    return {
        "init_dispersions": init_dispersions,
        "mle_dispersions": mle_dispersions,
        "mle_converged": mle_success,
        "fitted_trend": fitted_trend,
        "map_dispersions": map_dispersions,
        "normed_means": normed_means,
        "non_zero_mask": non_zero_mask,
    }


def dispersion(
    adata: AnnData,
    layer: str | None = None,
    size_factor_key: str | None = None,
    covariate_keys: list[str] | None = None,
    method: str = "full",
    var_key_added: str = "dispersions",
    trend_type: str = "parametric",
    dispersion_range: tuple[float, float] = (1e-8, 10.0),
    batch_size: int = 2048,
    verbose: bool = True,
) -> None:
    """Estimate dispersion parameters from (single-cell) RNA-seq data.

    This function estimates gene-specific dispersion parameters for negative binomial
    models from count data. The approach closely follows the PyDESeq2 implementation.

    Parameters
    ----------
    adata : :class:`~anndata.AnnData`
        Annotated data matrix containing expression data. The data should contain
        raw or normalized counts.
    layer : str | None, default=None
        Layer in `adata.layers` containing count data to use for dispersion estimation.
        If :obj:`None`, uses `adata.X`. Should contain raw counts.
    size_factor_key : str | None, default=None
        Key in `adata.obs` containing size factors for normalization. If provided,
        counts will be normalized by these factors before dispersion estimation.
        This is important for accurate dispersion estimation in datasets with
        variable sequencing depth.
    method : str, default="full"
        Method for dispersion estimation:
            - "full": Use full DESeq2-style estimation with trend fitting and MAP estimation.
            - "approx": Use approximate estimation by skipping initial MLE fitting.
            - "fast": Fast approximation using only initial dispersion estimates.
    var_key_added : str, default="dispersion"
        Key in `adata.var` where the final estimated dispersion values will be stored.
        Existing values will be overwritten.
    dispersion_range : tuple[float, float], default=(1e-4, 10.0)
        Allowed range for dispersion values, specified as (min_dispersion, max_dispersion).
        Note: The threshold that is actually enforced is max(max_disp, n_samples).
    trend_type : str, default="parametric"
        Type of trend to fit for dispersion estimates:
            - "parametric": Fit a parametric trend (e.g., gamma distribution).
            - "mean": Fit a constant mean-dispersion trend.
    batch_size : int, default=2048
        Number of features to process per batch. Adjust based on available memory
        and dataset size.
    verbose : bool, default=True
        Whether to display progress information during computation.

    Returns
    -------
    Updates ``adata`` in place and sets the following fields:

            - ``adata.var[var_key_added]``: Final estimated dispersion values for each feature.
            - ``adata.var["dispersion_init"]``: Initial dispersion estimates.
            - ``adata.var["dispersion_mle"]``: Genewise maximum likelihood dispersion estimates.
            - ``adata.var["dispersion_trend"]``: Fitted dispersion trend across genes.
            - ``adata.var["dispersion_map"]``: MAP dispersion estimates after trend fitting.

    Examples
    --------
    Estimate dispersions on (sc)RNA-seq data:

    >>> import scanpy as sc
    >>> import delnx as dx
    >>> adata = sc.read_h5ad("counts.h5ad")
    >>> # Calculate size factors first (optional but recommended)
    >>> adata.obs["size_factors"] = adata.X.sum(axis=1) / np.median(adata.X.sum(axis=1))
    >>> # Estimate dispersions
    >>> dx.pp.dispersion(adata, size_factor_key="size_factors")

    Notes
    -----
    - Dispersion estimation should be performed on raw counts with size factors for normalization.
    - For very large datasets, consider increasing the batch size if memory allows,
      or decreasing it for memory-constrained environments.
    - The estimated dispersions can be used for differential expression analysis
      with the negative binomial model by providing the `var_key_added` value
      as the `dispersion_key` parameter in the `de` function.
    """
    # Get expression data from the specified layer or X
    X = _get_layer(adata, layer)
    size_factors = adata.obs[size_factor_key].values if size_factor_key else None

    # Get design matrix
    if covariate_keys is not None:
        # Create design matrix using patsy for covariates
        formula = " + ".join(covariate_keys)
        design_matrix = patsy.dmatrix(formula, adata.obs, return_type="dataframe").values
    else:
        # If no covariates, use a simple intercept model
        design_matrix = None

    # Estimate dispersions using the specified method
    dispersions = _estimate_dispersion_batched(
        X=X,
        design_matrix=design_matrix,
        size_factors=size_factors,
        method=method,
        min_disp=dispersion_range[0],
        max_disp=max(dispersion_range[1], X.shape[0]),
        trend_type=trend_type,
        batch_size=batch_size,
        verbose=verbose,
    )

    # Store results in adata.var depending on the method used
    adata.var[var_key_added] = np.nan
    adata.var["dispersions_init"] = np.nan

    mask = dispersions["non_zero_mask"]
    adata.var.loc[mask, var_key_added] = np.array(dispersions["init_dispersions"])
    adata.var.loc[mask, "dispersions_init"] = np.array(dispersions["init_dispersions"])

    if method == "fast":
        return

    adata.var["dispersions_trend"] = np.nan
    adata.var["dispersions_map"] = np.nan

    adata.var.loc[mask, var_key_added] = np.array(dispersions["map_dispersions"])
    adata.var.loc[mask, "dispersions_trend"] = np.array(dispersions["fitted_trend"])
    adata.var.loc[mask, "dispersions_map"] = np.array(dispersions["map_dispersions"])

    if method == "approx":
        return

    adata.var["dispersions_mle"] = np.nan
    adata.var["mle_converged"] = np.nan
    adata.var["mle_converged"] = adata.var["mle_converged"].astype(bool)

    adata.var.loc[mask, "dispersions_mle"] = np.array(dispersions["mle_dispersions"])
    adata.var.loc[mask, "mle_converged"] = np.array(dispersions["mle_converged"])
