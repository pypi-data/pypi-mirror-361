"""
Comprehensive tests for GLS functionality
"""

import pytest
import numpy as np
import econometrust
from .conftest import RTOL, ATOL, LOOSE_RTOL, LOOSE_ATOL


class TestGLSBasicFunctionality:
    """Test basic GLS functionality and API."""

    def test_gls_creation(self):
        """Test GLS model creation."""
        gls = econometrust.GLS(fit_intercept=True)
        assert gls.fit_intercept is True
        assert not gls.is_fitted()
        assert gls.coefficients is None
        assert gls.intercept is None

        gls_no_intercept = econometrust.GLS(fit_intercept=False)
        assert gls_no_intercept.fit_intercept is False
        assert not gls_no_intercept.is_fitted()

    def test_gls_repr(self):
        """Test string representation."""
        gls = econometrust.GLS(fit_intercept=True)
        repr_str = repr(gls)
        assert "GLS" in repr_str
        assert "fit_intercept=True" in repr_str or "fit_intercept=true" in repr_str

    def test_unfitted_state(self):
        """Test behavior when model is not fitted."""
        gls = econometrust.GLS()

        # All these should return None for unfitted model
        assert gls.coefficients is None
        assert gls.intercept is None
        assert gls.standard_errors() is None
        assert gls.t_statistics() is None
        assert gls.p_values() is None
        assert gls.confidence_intervals() is None

        # Note: GLS doesn't currently expose these properties like OLS does
        # assert gls.mse is None
        # assert gls.r_squared is None
        # assert gls.residuals is None
        # assert gls.n_samples is None
        # assert gls.n_features is None

    def test_fit_basic(self, small_dataset, heteroscedastic_sigma):
        """Test basic fitting functionality."""
        X, y = small_dataset
        sigma = heteroscedastic_sigma
        gls = econometrust.GLS(fit_intercept=True)

        # Should not raise any exceptions
        gls.fit(X, y, sigma)

        # Should now be fitted
        assert gls.is_fitted()
        assert gls.coefficients is not None
        assert gls.intercept is not None
        # Note: GLS doesn't currently expose n_samples/n_features
        # assert gls.n_samples == X.shape[0]
        # assert gls.n_features == X.shape[1]

    def test_fit_no_intercept(self, small_dataset, heteroscedastic_sigma):
        """Test fitting without intercept."""
        X, y = small_dataset
        sigma = heteroscedastic_sigma
        gls = econometrust.GLS(fit_intercept=False)
        gls.fit(X, y, sigma)

        assert gls.is_fitted()
        assert gls.coefficients is not None
        assert gls.intercept is None  # Should be None when fit_intercept=False
        assert len(gls.coefficients) == X.shape[1]


class TestGLSMathematicalCorrectness:
    """Test mathematical correctness of GLS computations."""

    def test_homoscedastic_equals_ols(self, small_dataset):
        """Test that GLS with identity covariance equals OLS."""
        X, y = small_dataset
        n = X.shape[0]

        # Identity covariance matrix (homoscedastic)
        sigma = np.eye(n, dtype=np.float64, order="C")

        # Fit GLS
        gls = econometrust.GLS(fit_intercept=True)
        gls.fit(X, y, sigma)

        # Fit OLS
        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        # Should give very similar results
        np.testing.assert_allclose(
            gls.coefficients, ols.coefficients, rtol=LOOSE_RTOL, atol=LOOSE_ATOL
        )
        np.testing.assert_allclose(
            gls.intercept, ols.intercept, rtol=LOOSE_RTOL, atol=LOOSE_ATOL
        )

    def test_prediction_accuracy(self, small_dataset, heteroscedastic_sigma):
        """Test prediction accuracy."""
        X, y = small_dataset
        sigma = heteroscedastic_sigma
        gls = econometrust.GLS(fit_intercept=True)
        gls.fit(X, y, sigma)

        # Predictions on training data
        y_pred = gls.predict(X)
        assert y_pred.shape == y.shape

        # Test prediction on new data
        X_new = np.random.randn(20, X.shape[1]).astype(np.float64, order="C")
        y_new_pred = gls.predict(X_new)
        assert y_new_pred.shape == (20,)
        assert np.all(np.isfinite(y_new_pred))

    def test_heteroscedastic_efficiency(self, heteroscedastic_sigma):
        """Test that GLS is more efficient than OLS for heteroscedastic errors."""
        np.random.seed(123)
        n, p = heteroscedastic_sigma.shape[0], 2
        X = np.random.randn(n, p).astype(np.float64, order="C")
        true_coef = np.array([1.0, -0.5])

        # Generate heteroscedastic errors
        L = np.linalg.cholesky(heteroscedastic_sigma)
        errors = L @ np.random.randn(n)
        y = X @ true_coef + errors
        y = y.astype(np.float64)

        # Fit both models
        gls = econometrust.GLS(fit_intercept=False)
        gls.fit(X, y, heteroscedastic_sigma)

        ols = econometrust.OLS(fit_intercept=False)
        ols.fit(X, y)

        # GLS should have smaller standard errors (more efficient)
        gls_se = gls.standard_errors()
        ols_se = ols.standard_errors()

        # At least one coefficient should have smaller SE with GLS
        assert np.any(gls_se < ols_se)


class TestGLSStatisticalInference:
    """Test statistical inference capabilities."""

    def test_standard_errors(self, small_dataset, heteroscedastic_sigma):
        """Test standard error computation."""
        X, y = small_dataset
        sigma = heteroscedastic_sigma
        gls = econometrust.GLS(fit_intercept=True)
        gls.fit(X, y, sigma)

        se = gls.standard_errors()
        assert se is not None
        assert len(se) == X.shape[1]
        assert np.all(se > 0)  # Standard errors should be positive
        assert np.all(np.isfinite(se))

    def test_t_statistics(self, small_dataset, heteroscedastic_sigma):
        """Test t-statistic computation."""
        X, y = small_dataset
        sigma = heteroscedastic_sigma
        gls = econometrust.GLS(fit_intercept=True)
        gls.fit(X, y, sigma)

        t_stats = gls.t_statistics()
        se = gls.standard_errors()

        assert t_stats is not None
        assert len(t_stats) == len(gls.coefficients)

        # Manual calculation: t = coef / se
        t_manual = gls.coefficients / se
        np.testing.assert_allclose(t_stats, t_manual, rtol=LOOSE_RTOL, atol=LOOSE_ATOL)

    def test_p_values(self, small_dataset, heteroscedastic_sigma):
        """Test p-value computation."""
        X, y = small_dataset
        sigma = heteroscedastic_sigma
        gls = econometrust.GLS(fit_intercept=True)
        gls.fit(X, y, sigma)

        p_vals = gls.p_values()
        assert p_vals is not None
        assert len(p_vals) == len(gls.coefficients)
        assert np.all(p_vals >= 0.0)
        assert np.all(p_vals <= 1.0)
        assert np.all(np.isfinite(p_vals))

    def test_confidence_intervals(self, small_dataset, heteroscedastic_sigma):
        """Test confidence interval computation."""
        X, y = small_dataset
        sigma = heteroscedastic_sigma
        gls = econometrust.GLS(fit_intercept=True)
        gls.fit(X, y, sigma)

        # Test default 95% CI
        ci_95 = gls.confidence_intervals()
        assert ci_95 is not None
        assert ci_95.shape == (len(gls.coefficients), 2)

        # Lower bound should be less than upper bound
        assert np.all(ci_95[:, 0] < ci_95[:, 1])

        # Coefficients should be within their confidence intervals
        coef = gls.coefficients
        assert np.all(ci_95[:, 0] <= coef)
        assert np.all(coef <= ci_95[:, 1])

        # Test 99% CI (should be wider)
        ci_99 = gls.confidence_intervals(alpha=0.01)
        assert np.all(ci_99[:, 1] - ci_99[:, 0] >= ci_95[:, 1] - ci_95[:, 0])

    def test_summary_output(self, small_dataset, heteroscedastic_sigma):
        """Test summary string generation."""
        X, y = small_dataset
        sigma = heteroscedastic_sigma
        gls = econometrust.GLS(fit_intercept=True)
        gls.fit(X, y, sigma)

        summary = gls.summary()
        assert isinstance(summary, str)
        assert len(summary) > 0

        # Should contain key statistical information
        assert "GLS Regression Results" in summary
        assert "Coeff" in summary or "coef" in summary
        assert "Std Err" in summary or "std err" in summary
        assert "t" in summary
        assert "P>|t|" in summary


class TestGLSEdgeCases:
    """Test edge cases and error handling."""

    def test_singular_covariance(self, small_dataset):
        """Test with singular covariance matrix."""
        X, y = small_dataset
        n = X.shape[0]

        # Create singular covariance matrix
        sigma = np.ones((n, n), dtype=np.float64, order="C")  # Rank 1

        gls = econometrust.GLS()

        with pytest.raises(Exception):  # Should raise some kind of error
            gls.fit(X, y, sigma)

    def test_mismatched_dimensions(self, small_dataset):
        """Test with mismatched dimensions."""
        X, y = small_dataset
        n = X.shape[0]

        # Wrong sigma size
        sigma_wrong = np.eye(n + 5, dtype=np.float64, order="C")

        gls = econometrust.GLS()

        with pytest.raises(Exception):
            gls.fit(X, y, sigma_wrong)

    def test_non_positive_definite(self, small_dataset):
        """Test with non-positive definite covariance."""
        X, y = small_dataset
        n = X.shape[0]

        # Create a matrix that's not positive definite
        sigma = np.random.randn(n, n).astype(np.float64, order="C")
        sigma = sigma @ sigma.T - 2 * np.eye(n)  # Make negative definite

        gls = econometrust.GLS()

        with pytest.raises(Exception):  # Should detect non-positive definiteness
            gls.fit(X, y, sigma)


class TestGLSDataTypes:
    """Test various data types and array formats."""

    def test_float32_arrays(self, small_dataset):
        """Test with float32 arrays."""
        X, y = small_dataset
        n = X.shape[0]
        sigma = np.eye(n, dtype=np.float32, order="C")

        X_f32 = X.astype(np.float32)
        y_f32 = y.astype(np.float32)

        gls = econometrust.GLS()
        # Should work (might convert internally or raise informative error)
        try:
            gls.fit(X_f32, y_f32, sigma)
            # If it works, results should be reasonable
            assert gls.is_fitted()
        except Exception as e:
            # If it fails, should be a clear error about data types
            assert "float64" in str(e) or "dtype" in str(e) or "PyArray" in str(e)

    def test_non_contiguous_arrays(self, small_dataset):
        """Test with non-contiguous arrays."""
        X, y = small_dataset
        n = X.shape[0]
        sigma = np.eye(n, dtype=np.float64, order="C")

        # Create non-contiguous arrays
        X_nc = X.T.T  # Transpose twice to make non-contiguous
        y_nc = y[::-1][::-1]  # Reverse twice
        sigma_nc = sigma.T.T

        gls = econometrust.GLS()
        gls.fit(X_nc, y_nc, sigma_nc)  # Should handle or convert automatically
        assert gls.is_fitted()


class TestGLSAutocorrelation:
    """Test GLS with autocorrelated errors."""

    def test_autocorrelated_errors(self, autocorrelated_sigma):
        """Test GLS with autocorrelated covariance structure."""
        np.random.seed(456)
        n, p = autocorrelated_sigma.shape[0], 2
        X = np.random.randn(n, p).astype(np.float64, order="C")
        true_coef = np.array([2.0, -1.0])

        # Generate autocorrelated errors
        L = np.linalg.cholesky(autocorrelated_sigma)
        errors = L @ np.random.randn(n)
        y = X @ true_coef + errors
        y = y.astype(np.float64)

        # Fit GLS
        gls = econometrust.GLS(fit_intercept=False)
        gls.fit(X, y, autocorrelated_sigma)

        assert gls.is_fitted()
        assert gls.coefficients is not None
        assert np.all(np.isfinite(gls.coefficients))

        # Should have reasonable R-squared
        assert gls.r_squared is not None
        assert 0 <= gls.r_squared <= 1


class TestGLSPerformance:
    """Performance benchmarks and stress tests for GLS."""

    def test_medium_dataset_performance(self, benchmark_timer):
        """Test performance on medium-sized dataset."""
        np.random.seed(789)
        n, p = 1000, 5  # Smaller than OLS tests due to O(n³) complexity
        X = np.random.randn(n, p).astype(np.float64, order="C")
        true_coef = np.random.randn(p)

        # Create structured covariance (more efficient than dense)
        diag_vars = np.random.uniform(0.5, 2.0, n)
        sigma = np.diag(diag_vars).astype(np.float64, order="C")

        # Generate y
        errors = np.random.randn(n) * np.sqrt(diag_vars)
        y = X @ true_coef + errors
        y = y.astype(np.float64)

        gls = econometrust.GLS(fit_intercept=True)

        timer = benchmark_timer.start()
        gls.fit(X, y, sigma)
        fit_time = timer.stop()

        print(
            f"Medium GLS dataset fit time: {fit_time:.4f}s for {X.shape[0]}×{X.shape[1]}"
        )

        # Should be reasonably fast for structured covariance
        assert fit_time < 2.0  # GLS is slower than OLS

        # Test prediction performance
        timer.start()
        y_pred = gls.predict(X)
        pred_time = timer.stop()

        print(f"Medium GLS dataset predict time: {pred_time:.4f}s")
        assert pred_time < 0.1  # Prediction should still be fast

        # Verify correctness
        assert gls.is_fitted()
        assert gls.r_squared is not None
        assert 0 <= gls.r_squared <= 1


if __name__ == "__main__":
    pytest.main([__file__])
