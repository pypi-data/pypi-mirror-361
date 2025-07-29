"""Differential expression testing module.

This module provides functions for differential expression analysis between
condition levels in single-cell or bulk RNA-seq data. It implements various
statistical methods including:

- Logistic regression with likelihood ratio tests
- Negative binomial regression for count data
- ANOVA-based linear models
- DESeq2-style analysis

The implementation supports multiple computational backends for performance
optimization (JAX, statsmodels, cuML), size factor normalization via offset terms,
and grouped analysis for cell type-specific differential expression.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from anndata import AnnData
from scipy.sparse import csr_matrix, issparse

import delnx as dx
from delnx._constants import SUPPORTED_BACKENDS
from delnx._logging import logger
from delnx._typing import Backends, ComparisonMode, DataType, Method
from delnx._utils import _get_layer

from ._de_tests import _run_de, _run_deseq2
from ._effects import _batched_auroc, _log2fc
from ._jax_tests import _run_batched_de
from ._utils import _check_method_and_data_type, _infer_data_type, _prepare_model_data, _validate_conditions


def _grouped_de(
    adata: AnnData,
    condition_key: str,
    group_key: str,
    reference: str | tuple[str, str] | None = None,
    size_factor_key: str | None = None,
    dispersion_key: str | None = None,
    covariate_keys: list[str] | None = None,
    method: Method = "lr",
    backend: Backends = "jax",
    mode: ComparisonMode = "all_vs_all",
    layer: str | None = None,
    data_type: DataType = "auto",
    log2fc_threshold: float = 0.0,
    min_samples: int = 1,
    multitest_method: str = "fdr_bh",
    n_cpus: int = 1,
    batch_size: int = 2048,
    optimizer: str = "BFGS",
    maxiter: int = 100,
    verbose: bool = True,
):
    """Perform differential expression analysis for each group separately.

    This internal function implements the grouped differential expression analysis
    workflow. It runs DE tests for each unique group in `adata.obs[group_key]`
    (e.g., cell types) and combines the results into a single DataFrame with a
    'group' column indicating the group identity.

    Parameters
    ----------
    adata : AnnData
        AnnData object containing expression data and metadata.
    condition_key : str
        Column name in `adata.obs` containing condition labels.
    group_key : str
        Column name in `adata.obs` defining the groups for separate DE analysis.
    reference : str | tuple[str, str] | None, default=None
        Reference condition or specific comparison pair.
    size_factor_key : str | None, default=None
        Column name in `adata.obs` containing size factors for normalization.
    dispersion_key : str | None, default=None
        Column name in `adata.var` containing precomputed dispersions.
    covariate_keys : list[str] | None, default=None
        List of column names in `adata.obs` to include as covariates.
    method : Method, default='lr'
        Statistical method for differential expression testing.
    backend : Backends, default='jax'
        Computational backend for model fitting.
    mode : ComparisonMode, default='all_vs_all'
        Comparison strategy for condition levels.
    layer : str | None, default=None
        Layer in `adata.layers` to use for expression data.
    data_type : DataType, default='auto'
        Type of expression data.
    log2fc_threshold : float, default=0.0
        Minimum absolute log2 fold change threshold.
    min_samples : int, default=2
        Minimum number of samples required per condition level.
    multitest_method : str, default='fdr_bh'
        Method for multiple testing correction.
    n_cpus : int, default=1
        Number of parallel jobs.
    batch_size : int, default=2048
        Number of features to process per batch.
    optimizer : str, default='BFGS'
        Optimization algorithm for model fitting.
    maxiter : int, default=100
        Maximum number of iterations for optimization.
    verbose : bool, default=True
        Whether to print progress information.

    Returns
    -------
    pd.DataFrame
        Combined differential expression results with an additional 'group' column.
    """
    results = []
    for group in adata.obs[group_key].unique():
        logger.info(f"Running DE for group: {group}", verbose=verbose)

        mask = adata.obs[group_key].values == group
        if sum(mask) < (min_samples * 2):
            logger.warning("Skipping group {group} with < {min_samples * 2} samples", verbose=verbose)
            continue

        # Run DE for group with error handling
        try:
            group_results = de(
                adata=adata[mask, :],
                condition_key=condition_key,
                reference=reference,
                group_key=None,
                method=method,
                backend=backend,
                size_factor_key=size_factor_key,
                dispersion_key=dispersion_key,
                covariate_keys=covariate_keys,
                mode=mode,
                layer=layer,
                data_type=data_type,
                log2fc_threshold=log2fc_threshold,
                min_samples=min_samples,
                multitest_method=multitest_method,
                n_cpus=n_cpus,
                batch_size=batch_size,
                optimizer=optimizer,
                maxiter=maxiter,
                verbose=verbose,
            )
            group_results["group"] = group
            results.append(group_results)

        except ValueError as e:
            logger.warning(
                f"Differential expression analysis failed for group '{group}': {str(e)}. Skipping this group.",
                verbose=verbose,
            )
            continue

    results = pd.concat(results, axis=0).reset_index(drop=True)

    # Check if any results are valid
    if len(results) == 0 or results["pval"].isna().all():
        raise ValueError(
            "Differential expression analysis failed for all groups. Please check the input data or set `verbose=True` for more details."
        )

    # Perform multiple testing correction
    padj = sm.stats.multipletests(
        results["pval"][results["pval"].notna()].values,
        method=multitest_method,
    )[1]
    results["padj"] = np.nan  # Initialize with NaN
    results.loc[results["pval"].notna(), "padj"] = padj

    if mode == "continuous":
        # For continuous mode, we don't have test/ref conditions
        results = results.sort_values(by=["group", "padj", "coef"]).reset_index(drop=True)

    else:
        # Sort by group, test condition, reference condition, and adjusted p-value
        results = results.sort_values(
            by=["group", "test_condition", "ref_condition", "padj", "log2fc"],
        ).reset_index(drop=True)

    return results


def de(
    adata: AnnData,
    condition_key: str,
    group_key: str | None = None,
    reference: str | tuple[str, str] | None = None,
    size_factor_key: str | None = None,
    dispersion_key: str | None = None,
    covariate_keys: list[str] | None = None,
    method: Method = "lr",
    backend: Backends = "jax",
    mode: ComparisonMode = "all_vs_all",
    layer: str | None = None,
    data_type: DataType = "auto",
    log2fc_threshold: float = 0.0,
    min_samples: int = 1,
    multitest_method: str = "fdr_bh",
    n_cpus: int = 1,
    batch_size: int = 2048,
    optimizer: str = "BFGS",
    maxiter: int = 100,
    verbose: bool = True,
) -> pd.DataFrame:
    """Perform differential expression analysis.

    This function runs differential expression testing using various statistical methods
    and backends. It supports both single and grouped comparisons with multiple
    testing correction. The function is flexible and can handle different data types,
    normalization strategies, and computational backends.

    Parameters
    ----------
    adata : AnnData
        Annotated data object containing expression data and metadata.
    condition_key : str
        Column name in `adata.obs` containing condition labels for comparison.
    group_key : str | None, default=None
        Column name in `adata.obs` for grouped differential expression testing
        (e.g., cell type). If provided, DE testing is performed separately for
        each group.
    reference : str | tuple[str, str] | None, default=None
        Reference condition for comparison. Can be:
            - Single string: reference condition for all comparisons
            - Tuple (reference, comparison): specific pair to compare
            - :obj:`None`: automatically determined based on mode
    size_factor_key : str | None, default=None
        Column name in `adata.obs` containing size factors for normalization. When using a negative binomial model, this is used as an offset term to account for library size differences. If not provided, size are computed internally based on library size normalization.
    dispersion_key : str | None, default=None
        Column name in `adata.var` containing precomputed dispersions. Only used for negative binomial methods. If not provided, the function will estimate gene-wise dispersions.
    covariate_keys : list[str] | None, default=None
        List of column names in `adata.obs` to include as covariates in the model.
    method : Method, default='lr'
        Method for differential expression testing:
            - "lr": Constructs a logistic regression model predicting group membership based on each feature individually and compares this to a null model with a likelihood ratio test. Recommended for log-normalized single-cell data.
            - "deseq2": DESeq2 method (through PyDESeq2) based on a model using the negative binomial distribution. Recommended for (pseudo-)bulk RNA-seq count data.
            - "negbinom": Wald test based on a negative binomial regression model. Recommended for count single-cell and bulk RNA-seq data.
            - "anova": ANOVA based on linear model. Recommended for log-normalized or scaled single-cell data.
            - "anova_residual": Linear model with residual F-test. Recommended for log-normalized or scaled single-cell data
            - "binomial": Likelihood ratio test based on a binomial regression model. Recommended for binary data such as single-cell and bulk ATAC-seq.
    backend : Backends, default='jax'
        Computational backend for linear model-based methods:
            - "jax": Custom JAX implementation (batched, GPU-accelerated)
            - "statsmodels": Standard statsmodels implementation
            - "cuml": cuML for GPU-accelerated logistic regression
    mode : ComparisonMode, default='all_vs_all'
        Comparison strategy:
            - "all_vs_all": Compare all pairs of condition levels
            - "all_vs_ref": Compare all levels against reference
            - "1_vs_1": Compare only reference vs comparison (requires tuple reference)
            - "continuous": Compare continuous condition levels (e.g., time points).
    layer : str | None, default=None
        Layer name in :attr:`~anndata.AnnData.layers` to use for expression data.
        If :obj:`None`, uses :attr:`~anndata.AnnData.X`.
    data_type : DataType, default='auto'
        Type of expression data:
            - "auto": Automatically infer from data
            - "counts": Raw count data
            - "lognorm": Log-normalized data (log1p of normalized counts)
            - "binary": Binary expression data
            - "scaled": Scaled data (e.g., z-scores)
    log2fc_threshold : float, default=0.0
        Minimum absolute log2 fold change threshold for feature inclusion.
        Features below this threshold are excluded from testing.
    min_samples : int, default=2
        Minimum number of samples required per condition level.
        Comparisons with fewer samples are skipped.
    multitest_method : str, default='fdr_bh'
        Method for multiple testing correction. Accepts any method supported by :func:`statsmodels.stats.multipletests`. Common options include:
            - "fdr_bh": Benjamini-Hochberg FDR correction
            - "bonferroni": Bonferroni correction
    n_cpus : int, default=1
        Number of CPUs for parallel processing with non-JAX backends.
    batch_size : int, default=2048
        Number of features to process per batch. Reduce for memory-constrained
        environments or very large datasets (>1M samples).
    optimizer : str, default='BFGS'
        Optimization algorithm for JAX backend:
            - "BFGS": BFGS optimizer via :func:`jax.scipy.optimize.minimize`
            - "IRLS": Iteratively reweighted least squares (experimental)
    maxiter : int, default=100
        Maximum number of optimization iterations.
    verbose : bool, default=True
        Whether to print progress messages and warnings.

    Returns
    -------
    :obj:`pandas.DataFrame` with differential expression results with columns:

            - "feature": Feature/gene names
            - "test_condition": Test condition label
            - "ref_condition": Reference condition label
            - "log2fc": Log2 fold change (test vs reference)
            - "auroc": Area under ROC curve
            - "coef": Model coefficient
            - "pval": Raw p-value
            - "padj": Adjusted p-value (multiple testing corrected)
            - "group": Group label (only for grouped DE)

    Raises
    ------
    ValueError
        If required keys are missing from adata.obs/var, if method and data_type
        are incompatible, or if no valid comparisons are found.

    Examples
    --------
    Basic differential expression between two conditions:

    >>> results = de(adata, condition_key="treatment", reference="control", mode="all_vs_ref")

    Pairwise DE testing between all conditions:

    >>> results = de(adata, condition_key="treatment", mode="all_vs_all")

    Grouped DE by cell type with covariates:

    >>> results = de(
    ...     adata, condition_key="disease_state", group_key="cell_type", covariate_keys=["age", "sex"], method="deseq2"
    ... )

    Testing on count data with a negative binomial model:

    >>> results = de(
    ...     adata,
    ...     condition_key="condition",
    ...     method="negbinom",
    ...     size_factor_key="size_factors",
    ...     dispersion_key="dispersions",
    ...     layer="counts",
    ... )

    Using other methods and backends:

    >>> results = de(adata, method="binomial", backend="statsmodels", condition_key="treatment")
    >>> results = de(adata, method="anova", condition_key="treatment", data_type="lognorm")
    >>> results = de(adata, method="lr", backend="cuml", condition_key="treatment")
    >>> results = de(adata, method="deseq2", condition_key="treatment", layer="counts")

    Notes
    -----
    - Method and data type compatibility:
        - "deseq2" and "negbinom" require count data
        - "binomial" requires binary data
        - "lr" works best with log-normalized or binary data
        - "anova" methods work best with log-normalized data
    - Backend options:
        - "jax" provides batched, GPU-accelerated testing with the following methods: "lr", "negbinom", "anova", "anova_residual"
        - "statsmodels" uses statsmodels (https://www.statsmodels.org/) implementations of regression models with the following methods: "lr", "negbinom", "anova", "anova_residual", "binomial"
        - "cuml" provides GPU-accelerated logistic regression with the "lr" method
    - The "deseq2" method ignores the `backend` parameter and always uses the PyDESeq2 implementation.
    - Size factors and dispersion parameters should be pre-computed for the "negbinom" method.
    - Multiple testing correction is applied across all comparisons
    """
    # Validate inputs
    if condition_key not in adata.obs.columns:
        raise ValueError(f"Condition key '{condition_key}' not found in adata.obs")
    if covariate_keys is not None:
        for col in covariate_keys:
            if col not in adata.obs.columns:
                raise ValueError(f"Covariate '{col}' not found in adata.obs")
    if size_factor_key is not None and size_factor_key not in adata.obs.columns:
        raise ValueError(f"Size factors key '{size_factor_key}' not found in adata.obs")
    if dispersion_key is not None and dispersion_key not in adata.var.columns:
        raise ValueError(f"Dispersions key '{dispersion_key}' not found in adata.var")

    # Get condition values
    condition_values = adata.obs[condition_key].values

    # Get size factors and compute if not provided
    if size_factor_key is None and method == "negbinom":
        dx.pp.size_factors(adata, method="library_size")
        size_factor_key = "size_factors"

    size_factors = adata.obs[size_factor_key].values if size_factor_key else None

    # Get dispersions
    dispersions = adata.var[dispersion_key].values if dispersion_key else None

    # Validate conditions and get comparison levels
    comparisons = _validate_conditions(condition_values, reference, mode)

    # Get expression matrix
    X = _get_layer(adata, layer)

    # Infer data type if auto
    if data_type == "auto":
        data_type = _infer_data_type(X)
        logger.info(f"Inferred data type: {data_type}", verbose=verbose)
    else:
        logger.info(f"Using specified data type: {data_type}", verbose=verbose)

    # Validate method and data type combinations
    _check_method_and_data_type(method, data_type)

    if backend not in SUPPORTED_BACKENDS:
        raise ValueError(f"Unsupported backend: {backend}. Supported backends are 'jax', 'statsmodels', 'cuml'.")

    if method == "deseq2" and mode == "continuous":
        raise ValueError(
            "The 'deseq2' method does not support continuous mode. Please use 'all_vs_all', 'all_vs_ref', or '1_vs_1'."
        )

    # Check if grouping requested
    if group_key is not None:
        if group_key not in adata.obs.columns:
            raise ValueError(f"Group by key '{group_key}' not found in adata.obs")
        return _grouped_de(
            adata=adata,
            condition_key=condition_key,
            reference=reference,
            group_key=group_key,
            size_factor_key=size_factor_key,
            dispersion_key=dispersion_key,
            covariate_keys=covariate_keys,
            method=method,
            backend=backend,
            mode=mode,
            layer=layer,
            data_type=data_type,
            log2fc_threshold=log2fc_threshold,
            min_samples=min_samples,
            multitest_method=multitest_method,
            n_cpus=n_cpus,
            batch_size=batch_size,
            optimizer=optimizer,
            maxiter=maxiter,
            verbose=verbose,
        )

    if method == "deseq2":
        # Run PyDESeq2
        return _run_deseq2(
            adata=adata,
            condition_key=condition_key,
            comparisons=comparisons,
            covariate_keys=covariate_keys,
            multitest_method=multitest_method,
            layer=layer,
            n_cpus=n_cpus,
            verbose=verbose,
        )

    # Run tests for each comparison
    results = []
    for group1, group2 in comparisons:
        # In continuous mode, use the condition column directly
        # and don't subset by comparison groups
        if mode == "continuous":
            all_mask = np.ones(adata.n_obs, dtype=bool)
            logger.info("Testing continuous condition", verbose=verbose)

        else:
            logger.info(f"Testing {group1} vs {group2}", verbose=verbose)
            # Get cell masks
            mask1 = adata.obs[condition_key].values == group1
            mask2 = adata.obs[condition_key].values == group2

            if np.sum(mask1) < min_samples or np.sum(mask2) < min_samples:
                logger.warning(
                    f"Skipping comparison {group1} vs {group2} with < {min_samples} samples", verbose=verbose
                )
                results.append(pd.DataFrame())
                continue

            all_mask = mask1 | mask2

        # Get data for tests
        X_comp = X[all_mask, :]
        sf_comp = size_factors[all_mask] if size_factors is not None else None

        if data_type == "counts" and size_factors is not None:
            X_norm = X_comp / sf_comp[:, np.newaxis]
            X_norm = csr_matrix(X_norm) if issparse(X_comp) else X_norm
        else:
            X_norm = X_comp

        model_data = _prepare_model_data(
            adata[all_mask, :],
            condition_key=condition_key,
            reference=group2,
            mode=mode,
            covariate_keys=covariate_keys,
        )

        # Check if genes are non-zero
        feature_mask = np.array(X_comp.sum(axis=0) > 0).flatten()

        # Dont filter by log2fc in continuous mode
        if mode != "continuous":
            condition_mask = model_data[condition_key].values == 1

            # Calculate log2 fold change
            log2fc = _log2fc(X=X_norm, condition_mask=condition_mask, data_type=data_type)
            # Clip log2fc to avoid extreme values
            log2fc = np.clip(log2fc, -10, 10)

            # Apply log2fc threshold
            feature_mask = (np.abs(log2fc) > log2fc_threshold) & feature_mask

        logger.info(f"Running DE for {np.sum(feature_mask)} features", verbose=verbose)

        X_comp = X_comp[:, feature_mask]
        X_norm = X_norm[:, feature_mask]
        feature_names = adata.var_names[feature_mask].values

        if backend == "jax":
            # Run batched DE test
            group_results = _run_batched_de(
                X=X_comp,
                model_data=model_data,
                feature_names=feature_names,
                method=method,
                condition_key=condition_key,
                dispersions=dispersions,
                size_factors=sf_comp,
                covariate_keys=covariate_keys,
                batch_size=batch_size,
                optimizer=optimizer,
                maxiter=maxiter,
                verbose=verbose,
            )

        else:
            # Run test per gene
            group_results = _run_de(
                X=X_comp,
                model_data=model_data,
                feature_names=feature_names,
                method=method,
                backend=backend,
                condition_key=condition_key,
                size_factors=sf_comp,
                covariate_keys=covariate_keys,
                n_cpus=n_cpus,
                verbose=verbose,
            )

        group_results["feature"] = group_results["feature"].astype(str)

        # Add comparison info if appropriate
        if mode != "continuous":
            group_results["test_condition"] = group1
            group_results["ref_condition"] = group2
            auroc = _batched_auroc(X=X_norm, groups=model_data[condition_key].values, batch_size=batch_size)
            auroc_df = pd.DataFrame(
                {
                    "feature": feature_names,
                    "auroc": auroc,
                }
            )
            logfc_df = pd.DataFrame(
                {
                    "log2fc": log2fc[feature_mask],
                    "feature": feature_names,
                }
            )
            group_results = group_results.merge(
                logfc_df,
                on="feature",
                how="left",
            ).merge(
                auroc_df,
                on="feature",
                how="left",
            )

        results.append(group_results)

    results = pd.concat(results, axis=0).reset_index(drop=True)

    # Check if any valid comparisons were found (length > 0 and not all pvals are NaN)
    if len(results) == 0 or results["pval"].isna().all():
        raise ValueError(
            "Differential expression analysis failed for all comparisons. Please check the input data or set `verbose=True` for more details."
        )

    # Clip p-values at 1e-50
    results["pval"] = np.clip(results["pval"], 1e-50, 1)

    # Perform multiple testing correction
    padj = sm.stats.multipletests(
        results["pval"][results["pval"].notna()].values,
        method=multitest_method,
    )[1]
    results["padj"] = np.nan  # Initialize with NaN
    results.loc[results["pval"].notna(), "padj"] = padj

    if mode == "continuous":
        # For continuous mode, we don't have test/ref conditions
        results = results.sort_values(by=["padj", "coef"]).reset_index(drop=True)

        # Reorder columns
        return results[
            [
                "feature",
                "coef",
                "pval",
                "padj",
            ]
        ].copy()

    else:
        results = results.sort_values(
            by=["test_condition", "ref_condition", "padj", "log2fc"],
        ).reset_index(drop=True)

        # Reorder columns
        return results[
            [
                "feature",
                "test_condition",
                "ref_condition",
                "log2fc",
                "auroc",
                "coef",
                "pval",
                "padj",
            ]
        ].copy()
