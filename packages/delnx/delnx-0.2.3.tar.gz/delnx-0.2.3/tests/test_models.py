import warnings

import jax.numpy as jnp
import numpy as np
import pytest

from delnx.models import (
    DispersionEstimator,
    LinearRegression,
    LogisticRegression,
    NegativeBinomialRegression,
)


# Test fixtures and utilities
@pytest.fixture
def linear_data():
    """Generate synthetic linear regression data."""
    np.random.seed(42)
    n_samples, n_features = 100, 3
    X = np.random.randn(n_samples, n_features)
    # Add intercept column
    X = np.column_stack([np.ones(n_samples), X])
    true_coef = np.array([2.0, 1.5, -0.8, 0.5])
    y = X @ true_coef + 0.1 * np.random.randn(n_samples)

    return {
        "X": jnp.array(X),
        "y": jnp.array(y),
        "true_coef": jnp.array(true_coef),
        "n_samples": n_samples,
        "n_features": n_features + 1,  # +1 for intercept
    }


@pytest.fixture
def logistic_data():
    """Generate synthetic logistic regression data."""
    np.random.seed(42)
    n_samples, n_features = 200, 2
    X = np.random.randn(n_samples, n_features)
    X = np.column_stack([np.ones(n_samples), X])
    true_coef = np.array([0.5, 1.2, -0.7])
    logits = X @ true_coef
    probs = 1 / (1 + np.exp(-logits))
    y = np.random.binomial(1, probs)

    return {
        "X": jnp.array(X),
        "y": jnp.array(y),
        "true_coef": jnp.array(true_coef),
        "n_samples": n_samples,
        "n_features": n_features + 1,
    }


@pytest.fixture
def count_data():
    """Generate synthetic count data for negative binomial regression."""
    np.random.seed(42)
    n_samples, n_features = 150, 2
    X = np.random.randn(n_samples, n_features)
    X = np.column_stack([np.ones(n_samples), X])
    size_factors = np.random.uniform(0.5, 2.0, size=n_samples)
    true_coef = np.array([2.0, 0.5, -0.3])
    true_dispersion = 0.1

    # Generate negative binomial data
    mu = np.exp(X @ true_coef)
    r = 1 / true_dispersion
    p = r / (r + mu)
    y = np.random.negative_binomial(r, p)

    return {
        "X": jnp.array(X),
        "y": jnp.array(y),
        "true_coef": jnp.array(true_coef),
        "true_dispersion": true_dispersion,
        "size_factors": jnp.array(size_factors),
        "n_samples": n_samples,
        "n_features": n_features + 1,
    }


@pytest.fixture
def dispersion_data():
    """Generate data for dispersion estimation tests."""
    np.random.seed(42)
    n_genes, n_samples = 100, 50

    # True parameters
    true_mu = np.random.exponential(scale=100, size=n_genes)
    true_dispersions = np.random.gamma(shape=2.0, scale=0.05, size=n_genes)
    size_factors = np.random.uniform(0.5, 2.0, size=n_samples)

    # Generate count matrix
    counts = np.zeros((n_samples, n_genes))
    for i in range(n_genes):
        mu = true_mu[i]
        disp = true_dispersions[i]
        r = 1.0 / disp
        p = r / (r + mu)
        counts[:, i] = np.random.negative_binomial(r, p, size=n_samples)

    return {
        "counts": jnp.array(counts),
        "true_mu": jnp.array(true_mu),
        "true_dispersions": jnp.array(true_dispersions),
        "size_factors": jnp.array(size_factors),
        "n_genes": n_genes,
        "n_samples": n_samples,
    }


class TestLinearRegression:
    """Test suite for LinearRegression class."""

    def test_initialization(self):
        """Test LinearRegression initialization."""
        # Default initialization
        reg = LinearRegression()
        assert isinstance(reg.maxiter, int)
        assert isinstance(reg.tol, float)
        assert isinstance(reg.optimizer, str)
        assert not reg.skip_stats

        # Custom initialization
        reg_custom = LinearRegression(maxiter=50, tol=1e-8, skip_stats=True)
        assert reg_custom.maxiter == 50
        assert reg_custom.tol == 1e-8
        assert reg_custom.skip_stats

    def test_fit_basic(self, linear_data):
        """Test basic fitting functionality."""
        reg = LinearRegression()
        result = reg.fit(linear_data["X"], linear_data["y"])

        # Check return structure
        required_keys = ["coef", "llf", "se", "stat", "pval"]
        assert all(key in result for key in required_keys)

        # Check coefficient shape
        assert result["coef"].shape == (linear_data["n_features"],)

        # Check coefficient accuracy (should be close to true values)
        np.testing.assert_allclose(result["coef"], linear_data["true_coef"], rtol=0.1, atol=0.1)

        # Check that log-likelihood is finite
        assert jnp.isfinite(result["llf"])

        # Check standard errors
        assert result["se"] is not None
        assert result["se"].shape == (linear_data["n_features"],)
        assert jnp.all(result["se"] > 0)

    def test_fit_skip_stats(self, linear_data):
        """Test fitting with Wald test skipped."""
        reg = LinearRegression(skip_stats=True)
        result = reg.fit(linear_data["X"], linear_data["y"])

        # Should have coefficients and log-likelihood
        assert "coef" in result
        assert "llf" in result

        # Should not have Wald test results
        assert result["se"] is None
        assert result["stat"] is None
        assert result["pval"] is None

    def test_negative_log_likelihood(self, linear_data):
        """Test negative log-likelihood computation."""
        reg = LinearRegression()
        nll = reg._negative_log_likelihood(linear_data["true_coef"], linear_data["X"], linear_data["y"])

        assert jnp.isfinite(nll)
        assert nll > 0  # Should be positive

    def test_exact_solution(self, linear_data):
        """Test exact OLS solution."""
        reg = LinearRegression()
        params = reg._exact_solution(linear_data["X"], linear_data["y"])

        assert params.shape == (linear_data["n_features"],)
        # Should be close to true coefficients
        np.testing.assert_allclose(params, linear_data["true_coef"], rtol=0.1, atol=0.1)

    def test_covariance_matrix(self, linear_data):
        """Test covariance matrix computation."""
        reg = LinearRegression()
        params = reg._exact_solution(linear_data["X"], linear_data["y"])
        cov = reg._compute_cov_matrix(linear_data["X"], params, linear_data["y"])

        # Should be square matrix
        n_features = linear_data["n_features"]
        assert cov.shape == (n_features, n_features)

        # Should be positive semidefinite (diagonal elements > 0)
        assert jnp.all(jnp.diag(cov) > 0)

    def test_edge_cases(self):
        """Test edge cases for LinearRegression."""
        reg = LinearRegression()

        # Perfect fit case
        X = jnp.array([[1, 1], [1, 2], [1, 3]])
        y = jnp.array([2, 4, 6])  # Perfect linear relationship
        result = reg.fit(X, y)

        assert jnp.isfinite(result["llf"])
        np.testing.assert_allclose(result["coef"], [0, 2], atol=1e-6)

    def test_predict(self):
        """Test LinearRegression.predict with and without intercept."""
        reg = LinearRegression()

        # Test with intercept
        X_with_intercept = jnp.array([[1.0, 2.0], [1.0, 3.0], [1.0, 4.0]])
        params_with_intercept = jnp.array([1.0, 0.5])  # intercept=1.0, slope=0.5
        offset = jnp.array([0.1, 0.2, 0.3])

        # Without offset
        pred_no_offset = reg.predict(X_with_intercept, params_with_intercept)
        expected_no_offset = jnp.array([2.0, 2.5, 3.0])  # [1 + 0.5*2, 1 + 0.5*3, 1 + 0.5*4]
        assert jnp.allclose(pred_no_offset, expected_no_offset)

        # With offset
        pred_with_offset = reg.predict(X_with_intercept, params_with_intercept, offset=offset)
        expected_with_offset = jnp.array([2.1, 2.7, 3.3])  # [2.0 + 0.1, 2.5 + 0.2, 3.0 + 0.3]
        assert jnp.allclose(pred_with_offset, expected_with_offset)

        # Test without intercept (no constant column)
        X_no_intercept = jnp.array([[2.0], [3.0], [4.0]])
        params_no_intercept = jnp.array([0.5])  # slope only

        pred_no_intercept = reg.predict(X_no_intercept, params_no_intercept)
        expected_no_intercept = jnp.array([1.0, 1.5, 2.0])  # [0.5*2, 0.5*3, 0.5*4]
        assert jnp.allclose(pred_no_intercept, expected_no_intercept)


class TestLogisticRegression:
    """Test suite for LogisticRegression class."""

    def test_initialization(self):
        """Test LogisticRegression initialization."""
        reg = LogisticRegression()
        assert reg.optimizer == "BFGS"

        reg_irls = LogisticRegression(optimizer="IRLS")
        assert reg_irls.optimizer == "IRLS"

    def test_fit_bfgs(self, logistic_data):
        """Test fitting with BFGS optimizer."""
        reg = LogisticRegression(optimizer="BFGS")
        result = reg.fit(logistic_data["X"], logistic_data["y"])

        # Check return structure
        required_keys = ["coef", "llf", "se", "stat", "pval"]
        assert all(key in result for key in required_keys)

        # Check coefficient shape
        assert result["coef"].shape == (logistic_data["n_features"],)

        # Coefficients should be reasonably close to true values
        np.testing.assert_allclose(
            result["coef"],
            logistic_data["true_coef"],
            rtol=0.3,
            atol=0.3,  # More tolerant for logistic regression
        )

        # Check log-likelihood is negative (as expected for logistic)
        assert jnp.isfinite(result["llf"])

    def test_fit_irls(self, logistic_data):
        """Test fitting with IRLS optimizer."""
        reg = LogisticRegression(optimizer="IRLS", maxiter=50)
        result = reg.fit(logistic_data["X"], logistic_data["y"])

        # Should converge to similar results as BFGS
        assert result["coef"].shape == (logistic_data["n_features"],)
        assert jnp.isfinite(result["llf"])

    def test_weight_function(self, logistic_data):
        """Test IRLS weight function."""
        reg = LogisticRegression()
        beta = jnp.zeros(logistic_data["n_features"])
        weights = reg._weight_fn(logistic_data["X"], beta)

        assert weights.shape == (logistic_data["n_samples"],)
        assert jnp.all(weights >= 0)
        assert jnp.all(weights <= 0.25)  # Max weight for logistic is 0.25

    def test_working_residuals(self, logistic_data):
        """Test IRLS working residuals function."""
        reg = LogisticRegression()
        beta = jnp.zeros(logistic_data["n_features"])
        resid = reg._working_resid_fn(logistic_data["X"], logistic_data["y"], beta)

        assert resid.shape == (logistic_data["n_samples"],)
        assert jnp.all(jnp.isfinite(resid))

    def test_negative_log_likelihood(self, logistic_data):
        """Test negative log-likelihood computation."""
        reg = LogisticRegression()
        nll = reg._negative_log_likelihood(logistic_data["true_coef"], logistic_data["X"], logistic_data["y"])

        assert jnp.isfinite(nll)
        assert nll > 0

    def test_invalid_optimizer(self, logistic_data):
        """Test invalid optimizer raises error."""
        reg = LogisticRegression(optimizer="INVALID")

        with pytest.raises(ValueError, match="Unsupported optimizer"):
            reg.fit(logistic_data["X"], logistic_data["y"])

    def test_predict(self):
        """Test LogisticRegression.predict with and without intercept."""
        reg = LogisticRegression()

        # Test with intercept
        X_with_intercept = jnp.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
        params_with_intercept = jnp.array([0.0, 1.0])  # intercept=0.0, slope=1.0
        offset = jnp.array([0.5, -0.5, 0.0])

        # Without offset
        pred_no_offset = reg.predict(X_with_intercept, params_with_intercept)
        # Logits: [0, 1, 2], sigmoid([0, 1, 2]) = [0.5, 0.731, 0.881]
        expected_no_offset = jnp.array([0.5, 0.7310585786, 0.8807970779])
        assert jnp.allclose(pred_no_offset, expected_no_offset, rtol=1e-6)

        # With offset
        pred_with_offset = reg.predict(X_with_intercept, params_with_intercept, offset=offset)
        # Logits: [0 + 0.5, 1 - 0.5, 2 + 0.0] = [0.5, 0.5, 2.0]
        expected_with_offset = jnp.array([0.6224593312, 0.6224593312, 0.8807970779])
        assert jnp.allclose(pred_with_offset, expected_with_offset, rtol=1e-6)

        # Test without intercept
        X_no_intercept = jnp.array([[1.0], [2.0], [3.0]])
        params_no_intercept = jnp.array([0.5])  # slope only

        pred_no_intercept = reg.predict(X_no_intercept, params_no_intercept)
        # Logits: [0.5, 1.0, 1.5], sigmoid values
        expected_no_intercept = jnp.array([0.6224593312, 0.7310585786, 0.8175744762])
        assert jnp.allclose(pred_no_intercept, expected_no_intercept, rtol=1e-6)

        # Check probabilities are in [0, 1]
        assert jnp.all(pred_no_offset >= 0.0) and jnp.all(pred_no_offset <= 1.0)
        assert jnp.all(pred_with_offset >= 0.0) and jnp.all(pred_with_offset <= 1.0)
        assert jnp.all(pred_no_intercept >= 0.0) and jnp.all(pred_no_intercept <= 1.0)


class TestNegativeBinomialRegression:
    """Test suite for NegativeBinomialRegression class."""

    def test_initialization(self):
        """Test NegativeBinomialRegression initialization."""
        # Default initialization
        reg = NegativeBinomialRegression()
        assert reg.dispersion is None
        assert isinstance(reg.dispersion_range, tuple)

        # Custom initialization
        reg_custom = NegativeBinomialRegression(dispersion=0.1)
        assert reg_custom.dispersion == 0.1

    def test_fit_with_fixed_dispersion(self, count_data):
        """Test fitting with fixed dispersion parameter."""
        reg = NegativeBinomialRegression(dispersion=0.1, optimizer="BFGS")
        result = reg.fit(count_data["X"], count_data["y"])

        # Check return structure
        required_keys = ["coef", "llf", "se", "stat", "pval"]
        assert all(key in result for key in required_keys)

        # Check coefficient shape
        assert result["coef"].shape == (count_data["n_features"],)

        # Check log-likelihood
        assert jnp.isfinite(result["llf"])

    def test_fit_with_estimated_dispersion(self, count_data):
        """Test fitting with estimated dispersion parameter."""
        reg = NegativeBinomialRegression(dispersion=None)
        result = reg.fit(count_data["X"], count_data["y"])

        # Check return structure
        required_keys = ["coef", "llf", "se", "stat", "pval"]
        assert all(key in result for key in required_keys)

        # Check coefficient shape
        assert result["coef"].shape == (count_data["n_features"],)

        # Check log-likelihood
        assert jnp.isfinite(result["llf"])

    def test_fit_with_full_dispersion(self, count_data):
        """Test fitting with provided full dispersion estimates."""
        reg = NegativeBinomialRegression(dispersion=count_data["true_dispersion"], optimizer="BFGS")
        result = reg.fit(count_data["X"], count_data["y"])

        # Check return structure
        required_keys = ["coef", "llf", "se", "stat", "pval"]
        assert all(key in result for key in required_keys)

        # Check coefficient shape
        assert result["coef"].shape == (count_data["n_features"],)

        # Check log-likelihood
        assert jnp.isfinite(result["llf"])

    def test_fit_with_offset(self, count_data):
        """Test fitting with an offset term."""
        reg = NegativeBinomialRegression(dispersion=0.1, optimizer="BFGS")
        offset = jnp.log(count_data["size_factors"])

        # Fit with offset
        result = reg.fit(count_data["X"], count_data["y"], offset=offset)

        # Check return structure
        required_keys = ["coef", "llf", "se", "stat", "pval"]
        assert all(key in result for key in required_keys)

        # Check coefficient shape
        assert result["coef"].shape == (count_data["n_features"],)

        # Check log-likelihood
        assert jnp.isfinite(result["llf"])

        # Fit without offset
        result_no_offset = reg.fit(count_data["X"], count_data["y"])

        # Check that coefficients are not identical -> offset is used
        assert not jnp.allclose(result["coef"], result_no_offset["coef"])

    def test_weight_function(self, count_data):
        """Test IRLS weight function."""
        reg = NegativeBinomialRegression(dispersion=0.1)
        beta = jnp.array([1.0, 0.5, -0.2])
        weights = reg._weight_fn(count_data["X"], beta, dispersion=0.1)

        assert weights.shape == (count_data["n_samples"],)
        assert jnp.all(weights > 0)
        assert jnp.all(jnp.isfinite(weights))

    def test_working_residuals(self, count_data):
        """Test IRLS working residuals function."""
        reg = NegativeBinomialRegression(dispersion=0.1)
        beta = jnp.array([1.0, 0.5, -0.2])
        resid = reg._working_resid_fn(count_data["X"], count_data["y"], beta, dispersion=0.1)

        assert resid.shape == (count_data["n_samples"],)
        assert jnp.all(jnp.isfinite(resid))

    def test_negative_log_likelihood(self, count_data):
        """Test negative log-likelihood computation."""
        reg = NegativeBinomialRegression()
        nll = reg._negative_log_likelihood(
            count_data["true_coef"], count_data["X"], count_data["y"], dispersion=count_data["true_dispersion"]
        )

        assert jnp.isfinite(nll)
        assert nll > 0

    def test_dispersion_clipping(self, count_data):
        """Test dispersion parameter clipping."""
        reg = NegativeBinomialRegression(dispersion_range=(0.01, 1.0))

        # Test with dispersion outside range
        nll = reg._negative_log_likelihood(
            count_data["true_coef"],
            count_data["X"],
            count_data["y"],
            dispersion=100.0,  # Should be clipped to 1.0
        )

        assert jnp.isfinite(nll)

    def test_predict(self):
        """Test NegativeBinomialRegression.predict with and without intercept."""
        reg = NegativeBinomialRegression()

        # Test with intercept
        X_with_intercept = jnp.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
        params_with_intercept = jnp.array([1.0, 0.5])  # intercept=1.0, slope=0.5
        offset = jnp.array([0.5, -0.5, 0.0])  # log(size_factors)

        # Without offset
        pred_no_offset = reg.predict(X_with_intercept, params_with_intercept)
        # Linear predictors: [1, 1.5, 2], exp([1, 1.5, 2]) = [2.718, 4.482, 7.389]
        expected_no_offset = jnp.array([2.7182818285, 4.4816890703, 7.3890560989])
        assert jnp.allclose(pred_no_offset, expected_no_offset, rtol=1e-6)

        # With offset
        pred_with_offset = reg.predict(X_with_intercept, params_with_intercept, offset=offset)
        # Linear predictors with offset: [1 + 0.5, 1.5 - 0.5, 2 + 0.0] = [1.5, 1.0, 2.0]
        expected_with_offset = jnp.array([4.4816890703, 2.7182818285, 7.3890560989])
        assert jnp.allclose(pred_with_offset, expected_with_offset, rtol=1e-6)

        # Test without intercept
        X_no_intercept = jnp.array([[1.0], [2.0], [3.0]])
        params_no_intercept = jnp.array([0.5])  # slope only

        pred_no_intercept = reg.predict(X_no_intercept, params_no_intercept)
        # Linear predictors: [0.5, 1.0, 1.5], exp([0.5, 1.0, 1.5]) = [1.649, 2.718, 4.482]
        expected_no_intercept = jnp.array([1.6487212707, 2.7182818285, 4.4816890703])
        assert jnp.allclose(pred_no_intercept, expected_no_intercept, rtol=1e-6)

        # Check all predictions are positive
        assert jnp.all(pred_no_offset > 0.0)
        assert jnp.all(pred_with_offset > 0.0)
        assert jnp.all(pred_no_intercept > 0.0)


class TestDispersionEstimator:
    """Test suite for DispersionEstimator class."""

    @pytest.fixture
    def estimator(self):
        """Create a DispersionEstimator instance with default parameters."""
        return DispersionEstimator(design_matrix=jnp.ones((10, 1)), size_factors=jnp.ones(10))

    @pytest.fixture
    def custom_estimator(self):
        """Create a DispersionEstimator instance with custom parameters."""
        return DispersionEstimator(
            design_matrix=jnp.ones((10, 1)), size_factors=jnp.ones(10), min_disp=1e-6, max_disp=20.0, min_mu=1.0
        )

    @pytest.fixture
    def synthetic_data(self):
        """Create synthetic data that follows negative binomial distribution."""
        np.random.seed(42)
        n_samples, n_genes = 20, 8

        # True parameters
        true_dispersions = np.array([0.1, 0.2, 0.15, 0.3, 0.25, 0.12, 0.18, 0.22])
        true_means = np.array([20, 50, 30, 80, 40, 25, 60, 35])

        # Size factors
        size_factors = np.random.uniform(0.7, 1.5, n_samples)

        # Design matrix (intercept + 1 covariate)
        covariate = np.random.randn(n_samples)
        design_matrix = np.column_stack([np.ones(n_samples), covariate])

        # Generate counts following negative binomial
        counts = np.zeros((n_samples, n_genes))
        for i, (mu, alpha) in enumerate(zip(true_means, true_dispersions, strict=False)):
            # Adjust mean by size factors
            sample_means = mu * size_factors
            # Generate NB counts: parameterized as (n, p) where n=1/alpha, p=n/(n+mu)
            for j in range(n_samples):
                r = 1.0 / alpha
                p = r / (r + sample_means[j])
                counts[j, i] = np.random.negative_binomial(r, p)

        # Normalized counts
        normed_counts = counts / size_factors[:, np.newaxis]

        synthetic_data = {
            "counts": jnp.array(counts),
            "normed_counts": jnp.array(normed_counts),
            "design_matrix": jnp.array(design_matrix),
            "size_factors": jnp.array(size_factors),
            "true_dispersions": true_dispersions,
            "true_means": true_means,
            "n_samples": n_samples,
            "n_genes": n_genes,
        }

        return synthetic_data

    @pytest.fixture
    def minimal_data(self):
        """Create minimal valid test data."""
        counts = jnp.array([[5, 10], [8, 12], [6, 9], [7, 11]])
        size_factors = jnp.array([1.0, 1.2, 0.9, 1.1])
        design_matrix = jnp.array([[1.0], [1.0], [1.0], [1.0]])  # Intercept only
        normed_counts = counts / size_factors[:, jnp.newaxis]

        return {
            "counts": counts,
            "normed_counts": normed_counts,
            "design_matrix": design_matrix,
            "size_factors": size_factors,
        }

    def test_initialization(self, custom_estimator):
        """Test DispersionEstimator initialization with custom parameters."""
        assert custom_estimator.min_disp == 1e-6
        assert custom_estimator.max_disp == 20.0
        assert custom_estimator.min_mu == 1.0

    def test_invalid_initialization(self):
        """Test that invalid parameters raise appropriate errors."""
        with pytest.raises(ValueError, match="Design matrix must be 2D"):
            DispersionEstimator(
                design_matrix=jnp.array([1, 2, 3]),  # 1D array
                size_factors=jnp.ones(3),
            )

        with pytest.raises(ValueError, match="Size factors must be 1D"):
            DispersionEstimator(
                design_matrix=jnp.ones((3, 1)),
                size_factors=jnp.array([[1.0], [1.2], [0.9]]),  # 2D array
            )

        with pytest.raises(ValueError, match="match the number of samples in the design matrix"):
            DispersionEstimator(
                design_matrix=jnp.ones((3, 1)),
                size_factors=jnp.array([1.0, 1.2]),  # Mismatched size factors
            )

        with pytest.raises(ValueError, match="Invalid dispersion range:"):
            DispersionEstimator(
                design_matrix=jnp.ones((3, 1)),
                size_factors=jnp.ones(3),
                min_disp=0.1,
                max_disp=0.05,  # min_disp > max_disp
            )

        with pytest.raises(ValueError, match="Invalid dispersion range:"):
            DispersionEstimator(
                design_matrix=jnp.ones((3, 1)),
                size_factors=jnp.ones(3),
                min_disp=-0.1,  # Negative min_disp
                max_disp=0.1,
            )

    def test_fit_moments_dispersions_basic(self, minimal_data):
        """Test basic moments dispersion estimation."""
        estimator = DispersionEstimator(
            design_matrix=minimal_data["design_matrix"],
            size_factors=minimal_data["size_factors"],
        )
        dispersions = estimator.fit_moments_dispersions(minimal_data["normed_counts"])

        assert dispersions.shape == (2,)  # Two genes
        assert bool(jnp.all(jnp.isfinite(dispersions)))

    def test_fit_moments_dispersions_realistic(self, synthetic_data):
        """Test moments dispersion estimation with realistic data."""
        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )
        dispersions = estimator.fit_moments_dispersions(synthetic_data["normed_counts"])

        assert dispersions.shape == (synthetic_data["n_genes"],)
        assert bool(jnp.all(jnp.isfinite(dispersions)))

        # Check that estimates are in reasonable range (not exact due to sampling)
        assert bool(jnp.all(dispersions < 1.0))  # Should be reasonable for our data

    def test_fit_moments_dispersions_zero_handling(self):
        """Test moments dispersion estimation handles zero counts gracefully."""
        # Data with some zero counts
        counts_with_zeros = jnp.array([[0, 5], [0, 8], [1, 6], [0, 7]])
        size_factors = jnp.ones(4)

        estimator = DispersionEstimator(
            design_matrix=jnp.ones((4, 1)),  # Intercept only
            size_factors=size_factors,
        )
        dispersions = estimator.fit_moments_dispersions(counts_with_zeros)

        assert dispersions.shape == (2,)
        assert bool(jnp.all(jnp.isfinite(dispersions)))

    def test_fit_initial_dispersions(self, synthetic_data):
        """Test initial dispersion estimation (minimum of rough and moments)."""
        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )
        initial_dispersions = estimator.fit_initial_dispersions(synthetic_data["normed_counts"])

        assert initial_dispersions.shape == (synthetic_data["n_genes"],)
        assert bool(jnp.all(jnp.isfinite(initial_dispersions)))
        assert bool(jnp.all(initial_dispersions >= estimator.min_disp))
        assert bool(jnp.all(initial_dispersions <= estimator.max_disp))

    def test_fit_mean_dispersion_trend_constant(self):
        """Test mean dispersion trend fitting returns constant values."""
        # Create some dispersions
        dispersions = jnp.array([0.1, 0.2, 0.15, 0.3, 0.25])

        # The mean trend should return a constant value for all genes
        estimator = DispersionEstimator(
            design_matrix=jnp.ones((5, 1)),  # Intercept only
            size_factors=jnp.ones(5),
        )
        trend = estimator.fit_mean_dispersion_trend(dispersions)

        assert trend.shape == dispersions.shape
        assert bool(jnp.all(jnp.isfinite(trend)))

        # All values should be the same (constant trend)
        assert bool(jnp.allclose(trend, trend[0]))

        # Value should be reasonable
        assert estimator.min_disp <= float(trend[0]) <= estimator.max_disp

    def test_fit_dispersion_trend_interface_mean(self):
        """Test the main dispersion trend interface with mean method."""
        dispersions = jnp.array([0.1, 0.2, 0.15, 0.3])
        normed_means = jnp.array([20.0, 50.0, 30.0, 80.0])

        estimator = DispersionEstimator(
            design_matrix=jnp.ones((4, 1)),  # Intercept only
            size_factors=jnp.ones(4),
        )
        trend = estimator.fit_dispersion_trend(dispersions, normed_means, trend_type="mean")

        assert trend.shape == dispersions.shape
        assert bool(jnp.all(jnp.isfinite(trend)))
        assert bool(jnp.allclose(trend, trend[0]))  # Should be constant

    def test_fit_dispersion_trend_invalid_type(self):
        """Test that invalid trend types raise appropriate errors."""
        dispersions = jnp.array([0.1, 0.2, 0.3])
        normed_means = jnp.array([10.0, 20.0, 30.0])

        estimator = DispersionEstimator(
            design_matrix=jnp.ones((3, 1)),  # Intercept only
            size_factors=jnp.ones(3),
        )

        with pytest.raises(ValueError, match="Unknown trend_type"):
            estimator.fit_dispersion_trend(dispersions, normed_means, trend_type="invalid")

    def test_dispersion_bounds_enforcement(self):
        """Test that custom bounds are properly enforced."""
        # Data that would normally give dispersions outside this range
        extreme_counts = jnp.array([[1, 100], [2, 200], [1, 150], [3, 180]])

        restrictive_estimator = DispersionEstimator(
            design_matrix=jnp.ones((4, 1)),  # Intercept only
            size_factors=jnp.ones(4),
            # Very restrictive bounds
            min_disp=0.15,
            max_disp=0.25,
        )

        dispersions = restrictive_estimator.fit_initial_dispersions(extreme_counts)

        # Should be clipped to the specified range
        assert bool(jnp.all(dispersions >= 0.15))
        assert bool(jnp.all(dispersions <= 0.25))

    def test_edge_case_all_zeros(self):
        """Test handling of all-zero count data."""
        zero_counts = jnp.zeros((5, 3))
        size_factors = jnp.ones(5)

        estimator = DispersionEstimator(
            design_matrix=jnp.ones((5, 1)),  # Intercept only
            size_factors=size_factors,
        )
        dispersions = estimator.fit_initial_dispersions(zero_counts)

        assert dispersions.shape == (3,)
        assert bool(jnp.all(jnp.isfinite(dispersions)))
        assert bool(jnp.all(dispersions >= estimator.min_disp))

    def test_edge_case_very_small_counts(self):
        """Test handling of very small count values."""
        small_counts = jnp.array([[0, 1, 0], [1, 0, 1], [0, 1, 0], [1, 1, 1]])
        size_factors = jnp.ones(4)

        estimator = DispersionEstimator(
            design_matrix=jnp.ones((4, 1)),  # Intercept only
            size_factors=size_factors,
        )
        dispersions = estimator.fit_moments_dispersions(small_counts)

        assert dispersions.shape == (3,)
        assert bool(jnp.all(jnp.isfinite(dispersions)))

    def test_edge_case_very_large_counts(self):
        """Test handling of very large count values."""
        large_counts = jnp.array([[1000, 1500], [1200, 1800], [1100, 1600], [1300, 1700]])
        size_factors = jnp.ones(4)

        estimator = DispersionEstimator(
            design_matrix=jnp.ones((4, 1)),  # Intercept only
            size_factors=size_factors,
        )
        dispersions = estimator.fit_moments_dispersions(large_counts)

        assert dispersions.shape == (2,)
        assert bool(jnp.all(jnp.isfinite(dispersions)))
        assert bool(jnp.all(dispersions >= estimator.min_disp))

    def test_size_factor_effects(self):
        """Test that different size factors properly affect dispersion estimation."""
        # Same raw counts but different size factors
        counts = jnp.array([[10, 20], [10, 20], [10, 20], [10, 20]])

        # Uniform size factors
        uniform_sf = jnp.ones(4)
        estimator = DispersionEstimator(
            design_matrix=jnp.ones((4, 1)),  # Intercept only
            size_factors=uniform_sf,
        )
        disp_uniform = estimator.fit_moments_dispersions(counts)

        # Variable size factors (this should increase apparent variance)
        variable_sf = jnp.array([0.5, 1.0, 1.5, 2.0])
        estimator = DispersionEstimator(
            design_matrix=jnp.ones((4, 1)),  # Intercept only
            size_factors=variable_sf,
        )
        disp_variable = estimator.fit_moments_dispersions(counts)

        assert disp_uniform.shape == disp_variable.shape == (2,)
        assert bool(jnp.all(jnp.isfinite(disp_uniform)))
        assert bool(jnp.all(jnp.isfinite(disp_variable)))

    def test_single_gene_vs_batch_consistency(self, synthetic_data):
        """Test that single gene processing gives same results as batch processing."""
        # Test with first gene only
        single_gene_counts = synthetic_data["normed_counts"][:, 0:1]
        single_gene_sf = synthetic_data["size_factors"]

        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"][:, 0:1],  # Intercept only
            size_factors=single_gene_sf,
        )

        single_disp = estimator.fit_moments_dispersions(single_gene_counts)

        # Test with all genes
        all_disp = estimator.fit_moments_dispersions(synthetic_data["normed_counts"])

        # First dispersion should be very close
        assert bool(jnp.allclose(single_disp[0], all_disp[0], rtol=1e-10))

    def test_dispersion_reasonableness_with_known_data(self):
        """Test dispersion estimation with data where we know the expected range."""
        # Create data with controlled variance
        np.random.seed(123)

        # Low dispersion scenario (Poisson-like)
        mu = 50.0
        low_disp_data = np.random.poisson(mu, size=(20, 1))
        size_factors = np.ones(20)

        estimator = DispersionEstimator(
            design_matrix=jnp.ones((20, 1)),  # Intercept only
            size_factors=size_factors,
        )
        low_disp = estimator.fit_moments_dispersions(jnp.array(low_disp_data))

        # Should be relatively small dispersion
        assert float(low_disp[0]) < 0.5  # Poisson should have low dispersion

        # High variance scenario
        high_var_data = np.array([[10], [100], [5], [150], [8], [200], [12], [180]])

        high_disp = estimator.fit_moments_dispersions(jnp.array(high_var_data))

        # Should have higher dispersion due to high variance
        assert float(high_disp[0]) > float(low_disp[0])

    def test_shape_validation(self):
        """Test that all methods return correct shapes."""
        counts = jnp.array([[5, 10, 15], [8, 12, 18], [6, 9, 14], [7, 11, 16]])
        size_factors = jnp.array([1.0, 1.1, 0.9, 1.05])
        design_matrix = jnp.array([[1.0, 0.5], [1.0, -0.2], [1.0, 0.8], [1.0, -0.4]])
        normed_counts = counts / size_factors[:, jnp.newaxis]

        estimator = DispersionEstimator(
            design_matrix=design_matrix,
            size_factors=size_factors,
        )

        # Test moments dispersions
        moments_disp = estimator.fit_moments_dispersions(normed_counts)
        assert moments_disp.shape == (3,)

        # Test initial dispersions
        initial_disp = estimator.fit_initial_dispersions(normed_counts)
        assert initial_disp.shape == (3,)

        # Test trend fitting
        dispersions = jnp.array([0.1, 0.2, 0.15])
        normed_means = jnp.array([10.0, 20.0, 15.0])

        trend = estimator.fit_dispersion_trend(dispersions, normed_means, trend_type="mean")
        assert trend.shape == (3,)

    def test_fit_rough_dispersions_basic(self, synthetic_data):
        """Test basic rough dispersions estimation."""
        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )

        rough_dispersions = estimator.fit_rough_dispersions(synthetic_data["normed_counts"])

        assert rough_dispersions.shape == (synthetic_data["n_genes"],)
        assert bool(jnp.all(jnp.isfinite(rough_dispersions)))
        assert bool(jnp.all(rough_dispersions >= estimator.min_disp))

        # Rough dispersions should be reasonable estimates
        assert bool(jnp.all(rough_dispersions <= 2.0))  # Not too extreme

    def test_fit_rough_dispersions_single_gene(self, synthetic_data):
        """Test rough dispersions for single gene."""
        single_gene_normed = synthetic_data["normed_counts"][:, 0]

        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )
        single_rough = estimator.fit_rough_dispersions_single_gene(single_gene_normed)

        # Should be scalar
        assert single_rough.shape == ()
        assert bool(jnp.isfinite(single_rough))
        assert float(single_rough) >= estimator.min_disp

    def test_fit_rough_dispersions_consistency(self, synthetic_data):
        """Test consistency between single and batch rough dispersions."""
        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )

        # Batch processing
        batch_rough = estimator.fit_rough_dispersions(synthetic_data["normed_counts"])

        # Single gene processing for first gene
        single_rough = estimator.fit_rough_dispersions_single_gene(synthetic_data["normed_counts"][:, 0])

        # Should be very close
        assert bool(jnp.allclose(batch_rough[0], single_rough, rtol=1e-10))

    def test_fit_rough_dispersions_design_matrix_effects(self):
        """Test that design matrix complexity affects rough dispersions."""
        counts = jnp.array([[10, 20], [15, 25], [12, 22], [18, 28], [14, 24]])
        size_factors = jnp.ones(5)
        normed_counts = counts / size_factors[:, jnp.newaxis]

        # Simple design (intercept only)
        simple_design = jnp.ones((5, 1))
        estimator = DispersionEstimator(
            design_matrix=simple_design,
            size_factors=size_factors,
        )
        rough_simple = estimator.fit_rough_dispersions(normed_counts)

        # Complex design (intercept + covariate)
        complex_design = jnp.array([[1, 0], [1, 1], [1, 0.5], [1, -0.5], [1, -1]])
        estimator = DispersionEstimator(
            design_matrix=complex_design,
            size_factors=size_factors,
        )
        rough_complex = estimator.fit_rough_dispersions(normed_counts)

        assert rough_simple.shape == rough_complex.shape == (2,)
        assert bool(jnp.all(jnp.isfinite(rough_simple)))
        assert bool(jnp.all(jnp.isfinite(rough_complex)))

    def test_fit_mu_basic(self, synthetic_data):
        """Test basic mu (mean) estimation."""
        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )

        mu_estimates = estimator.fit_mu(synthetic_data["counts"])

        assert mu_estimates.shape == synthetic_data["counts"].shape
        assert bool(jnp.all(jnp.isfinite(mu_estimates)))
        assert bool(jnp.all(mu_estimates >= estimator.min_mu))

        # Mu estimates should be positive and reasonable
        assert bool(jnp.all(mu_estimates > 0))

    def test_fit_mu_single_gene(self, synthetic_data):
        """Test single gene mu estimation."""
        single_gene_counts = synthetic_data["counts"][:, 0]

        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )

        mu_single = estimator.fit_mu_single_gene(single_gene_counts)

        assert mu_single.shape == (synthetic_data["n_samples"],)
        assert bool(jnp.all(jnp.isfinite(mu_single)))
        assert bool(jnp.all(mu_single >= estimator.min_mu))

    def test_fit_mu_consistency(self, synthetic_data):
        """Test consistency between single and batch mu estimation."""
        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )

        # Batch processing
        batch_mu = estimator.fit_mu(synthetic_data["counts"])

        # Single gene processing
        single_mu = estimator.fit_mu_single_gene(synthetic_data["counts"][:, 0])

        # Should match for first gene
        assert bool(jnp.allclose(batch_mu[:, 0], single_mu, rtol=1e-10))

    def test_fit_parametric_dispersion_trend_basic(self):
        """Test parametric dispersion trend fitting."""
        # Create dispersions with clear 1/mean relationship
        normed_means = jnp.array([10.0, 20.0, 50.0, 100.0])
        # Dispersions should follow α₀ + α₁/μ pattern
        dispersions = 0.1 + 2.0 / normed_means + jnp.array([0.01, -0.01, 0.005, -0.005])  # Add small noise

        estimator = DispersionEstimator(
            design_matrix=jnp.ones((4, 1)),  # Intercept only
            size_factors=jnp.ones(4),
        )

        trend = estimator.fit_parametric_dispersion_trend(dispersions, normed_means)

        assert trend.shape == dispersions.shape
        assert bool(jnp.all(jnp.isfinite(trend)))
        assert bool(jnp.all(trend > 0))

        # Trend should be smoother than original dispersions
        # (reduces the noise we added)
        original_var = float(jnp.var(dispersions))
        trend_var = float(jnp.var(trend))
        assert trend_var < original_var

    def test_fit_parametric_trend_convergence_fallback(self):
        """Test parametric trend fallback to mean when convergence fails."""
        # Create problematic data that might not converge
        normed_means = jnp.array([1e-6, 1e6, 1e-6, 1e6])  # Extreme means
        dispersions = jnp.array([100.0, 1e-8, 100.0, 1e-8])  # Extreme dispersions

        estimator = DispersionEstimator(
            design_matrix=jnp.ones((4, 1)),  # Intercept only
            size_factors=jnp.ones(4),
        )

        # Should handle gracefully and potentially fall back to mean trend
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Suppress convergence warnings
            trend = estimator.fit_parametric_dispersion_trend(dispersions, normed_means)

        assert trend.shape == dispersions.shape
        assert bool(jnp.all(jnp.isfinite(trend)))
        assert bool(jnp.all(trend >= estimator.min_disp))

    def test_fit_dispersion_prior_basic(self, synthetic_data):
        """Test dispersion prior variance estimation."""
        dispersions = jnp.array([0.15, 0.22, 0.18, 0.25, 0.20])
        trend = jnp.array([0.16, 0.20, 0.19, 0.23, 0.21])

        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )

        prior_var = estimator.fit_dispersion_prior(dispersions, trend)

        assert isinstance(prior_var, float)
        assert prior_var > 0
        assert prior_var >= 0.25  # Should be at least the minimum
        assert jnp.isfinite(prior_var)

    def test_fit_dispersion_prior_low_dof_warning(self):
        """Test warning when degrees of freedom are low."""
        dispersions = jnp.array([0.1, 0.2])
        trend = jnp.array([0.12, 0.18])
        # Very low DOF design matrix (2 samples, 2 covariates = 0 DOF)
        low_dof_design = jnp.array([[1, 0], [1, 1]])

        estimator = DispersionEstimator(
            design_matrix=low_dof_design,
            size_factors=jnp.ones(2),
        )

        with pytest.warns(UserWarning, match="degrees of freedom"):
            prior_var = estimator.fit_dispersion_prior(dispersions, trend)

        assert isinstance(prior_var, float)
        assert prior_var >= 0.25

    def test_fit_dispersion_prior_different_dispersions(self):
        """Test prior estimation with different dispersion ranges."""
        # Low dispersions
        low_dispersions = jnp.array([0.01, 0.02, 0.015, 0.025]) * 100  # Scale above min_disp threshold
        low_trend = jnp.array([0.012, 0.018, 0.016, 0.022]) * 100

        # High dispersions
        high_dispersions = jnp.array([0.5, 0.8, 0.6, 0.9])
        high_trend = jnp.array([0.52, 0.75, 0.62, 0.85])

        design_matrix = jnp.array([[1, 0], [1, 1], [1, 0.5], [1, -0.5]])  # Sufficient DOF

        estimator = DispersionEstimator(
            design_matrix=design_matrix,
            size_factors=jnp.ones(4),
        )

        prior_low = estimator.fit_dispersion_prior(low_dispersions, low_trend)
        prior_high = estimator.fit_dispersion_prior(high_dispersions, high_trend)

        assert isinstance(prior_low, float) and isinstance(prior_high, float)
        assert prior_low > 0 and prior_high > 0
        # Higher dispersions typically lead to higher prior variance
        assert prior_high >= prior_low

    def test_fit_MAP_dispersions_basic(self, synthetic_data):
        """Test basic MAP dispersion estimation."""
        # Use subset of data for faster testing
        subset_counts = synthetic_data["counts"][:, :3]
        subset_genes = 3

        dispersions = jnp.array([0.15, 0.25, 0.20])
        trend = jnp.array([0.18, 0.22, 0.19])
        mu_hat = jnp.ones((synthetic_data["n_samples"], subset_genes)) * 20.0

        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"][:, :3],  # Use first 3 genes
            size_factors=synthetic_data["size_factors"],
        )

        map_dispersions, success = estimator.fit_MAP_dispersions(subset_counts, dispersions, trend, mu_hat)

        assert map_dispersions.shape == (subset_genes,)
        assert success.dtype == jnp.bool
        assert bool(jnp.all(jnp.isfinite(map_dispersions)))
        assert bool(jnp.all(map_dispersions >= estimator.min_disp))
        assert bool(jnp.all(map_dispersions <= estimator.max_disp))

    def test_fit_MAP_dispersions_shrinkage_effect(self):
        """Test that MAP estimation provides reasonable shrinkage toward trend."""
        # Create simple test case
        counts = jnp.array([[10, 20], [15, 25], [12, 22], [18, 28]])
        design_matrix = jnp.array([[1, 0], [1, 1], [1, 0.5], [1, -0.5]])

        # Initial dispersions that are far from trend
        dispersions = jnp.array([0.5, 0.8])  # High dispersions
        trend = jnp.array([0.2, 0.25])  # Lower trend values
        mu_hat = jnp.array([[15.0, 22.0], [18.0, 26.0], [14.0, 24.0], [20.0, 30.0]])

        estimator = DispersionEstimator(
            design_matrix=design_matrix,
            size_factors=jnp.ones(4),  # Uniform size factors
        )

        map_dispersions, success = estimator.fit_MAP_dispersions(counts, dispersions, trend, mu_hat)

        assert map_dispersions.shape == (2,)
        assert bool(jnp.all(jnp.isfinite(map_dispersions)))
        assert success.dtype == jnp.bool

        # MAP estimates should be between initial dispersions and trend (shrinkage effect)
        # This is a basic sanity check - exact shrinkage depends on data
        assert bool(jnp.all(map_dispersions <= dispersions))

    def test_fit_MAP_dispersions_different_priors(self):
        """Test MAP dispersions with different prior strengths."""
        counts = jnp.array([[8, 15], [12, 18], [10, 16], [14, 20]])
        design_matrix = jnp.array([[1, 0], [1, 1], [1, 0.5], [1, -0.5]])
        dispersions = jnp.array([0.3, 0.4])
        trend = jnp.array([0.2, 0.25])
        mu_hat = jnp.array([[10.0, 17.0], [13.0, 19.0], [11.0, 18.0], [15.0, 21.0]])

        estimator = DispersionEstimator(
            design_matrix=design_matrix,
            size_factors=jnp.ones(4),  # Uniform size factors
        )

        # The prior variance is computed internally based on the data
        # We test that different input dispersions give reasonable results
        map_disp1, _ = estimator.fit_MAP_dispersions(counts, dispersions, trend, mu_hat)

        # Different initial dispersions
        dispersions2 = jnp.array([0.1, 0.15])  # Closer to trend
        map_disp2, success = estimator.fit_MAP_dispersions(counts, dispersions2, trend, mu_hat)

        assert success.dtype == jnp.bool
        assert map_disp1.shape == map_disp2.shape == (2,)
        assert bool(jnp.all(jnp.isfinite(map_disp1)))
        assert bool(jnp.all(jnp.isfinite(map_disp2)))

    def test_complete_dispersion_workflow(self, synthetic_data):
        """Test the complete dispersion estimation workflow."""
        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )

        # Step 1: Initial dispersions
        initial_disp = estimator.fit_initial_dispersions(synthetic_data["normed_counts"])

        # Step 2: Mu estimation
        mu_hat = estimator.fit_mu(synthetic_data["counts"])

        # Step 3: Trend fitting
        normed_means = jnp.mean(synthetic_data["normed_counts"], axis=0)
        trend = estimator.fit_dispersion_trend(initial_disp, normed_means, trend_type="mean")

        # Step 4: MAP estimation
        map_dispersions, success = estimator.fit_MAP_dispersions(synthetic_data["counts"], initial_disp, trend, mu_hat)

        # Verify all steps completed successfully
        assert success.dtype == jnp.bool
        assert initial_disp.shape == (synthetic_data["n_genes"],)
        assert mu_hat.shape == synthetic_data["counts"].shape
        assert trend.shape == (synthetic_data["n_genes"],)
        assert map_dispersions.shape == (synthetic_data["n_genes"],)

        # All results should be finite and within bounds
        for result in [initial_disp, trend, map_dispersions]:
            assert bool(jnp.all(jnp.isfinite(result)))
            assert bool(jnp.all(result >= estimator.min_disp))
            assert bool(jnp.all(result <= estimator.max_disp))

        assert bool(jnp.all(jnp.isfinite(mu_hat)))
        assert bool(jnp.all(mu_hat >= estimator.min_mu))

    def test_workflow_with_different_trend_types(self, synthetic_data):
        """Test workflow with both trend types."""
        estimator = DispersionEstimator(
            design_matrix=synthetic_data["design_matrix"],
            size_factors=synthetic_data["size_factors"],
        )

        # Get initial estimates
        initial_disp = estimator.fit_initial_dispersions(synthetic_data["normed_counts"])
        normed_means = jnp.mean(synthetic_data["normed_counts"], axis=0)

        # Test mean trend
        trend_mean = estimator.fit_dispersion_trend(initial_disp, normed_means, trend_type="mean")

        # Test parametric trend (may fall back to mean if convergence fails)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            trend_param = estimator.fit_dispersion_trend(initial_disp, normed_means, trend_type="parametric")

        assert trend_mean.shape == trend_param.shape == (8,)
        assert bool(jnp.all(jnp.isfinite(trend_mean)))
        assert bool(jnp.all(jnp.isfinite(trend_param)))
