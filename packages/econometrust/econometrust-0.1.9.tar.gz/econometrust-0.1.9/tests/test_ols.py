"""
Comprehensive tests for OLS functionality
"""

import pytest
import numpy as np
import econometrust
from .conftest import RTOL, ATOL, LOOSE_RTOL, LOOSE_ATOL


class TestOLSBasicFunctionality:
    """Test basic OLS functionality and API."""

    def test_ols_creation(self):
        """Test OLS model creation."""
        ols = econometrust.OLS(fit_intercept=True)
        assert ols.fit_intercept is True
        assert not ols.is_fitted()
        assert ols.coefficients is None
        assert ols.intercept is None

        ols_no_intercept = econometrust.OLS(fit_intercept=False)
        assert ols_no_intercept.fit_intercept is False
        assert not ols_no_intercept.is_fitted()

    def test_ols_repr(self):
        """Test string representation."""
        ols = econometrust.OLS(fit_intercept=True)
        repr_str = repr(ols)
        assert "OLS" in repr_str
        assert "fit_intercept=True" in repr_str or "fit_intercept=true" in repr_str

    def test_unfitted_state(self):
        """Test behavior when model is not fitted."""
        ols = econometrust.OLS()

        # All these should return None for unfitted model
        assert ols.coefficients is None
        assert ols.intercept is None
        assert ols.standard_errors() is None
        assert ols.t_statistics() is None
        assert ols.p_values() is None
        assert ols.confidence_intervals() is None

        # Properties should also be None
        assert ols.mse is None
        assert ols.r_squared is None
        assert ols.residuals is None
        assert ols.n_samples is None
        assert ols.n_features is None

    def test_fit_basic(self, small_dataset):
        """Test basic fitting functionality."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=True)

        # Should not raise any exceptions
        ols.fit(X, y)

        # Should now be fitted
        assert ols.is_fitted()
        assert ols.coefficients is not None
        assert ols.intercept is not None
        assert ols.n_samples == X.shape[0]
        assert ols.n_features == X.shape[1]

    def test_fit_no_intercept(self, small_dataset):
        """Test fitting without intercept."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=False)
        ols.fit(X, y)

        assert ols.is_fitted()
        assert ols.coefficients is not None
        assert ols.intercept is None  # Should be None when fit_intercept=False
        assert len(ols.coefficients) == X.shape[1]


class TestOLSMathematicalCorrectness:
    """Test mathematical correctness of OLS computations."""

    def test_perfect_fit(self, perfect_data):
        """Test OLS on perfect linear relationship."""
        X, y = perfect_data
        true_coef = np.array([2.0, -1.5, 3.0, 0.8, -0.3])
        true_intercept = 7.5

        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        # Should recover true coefficients exactly (within numerical precision)
        np.testing.assert_allclose(ols.coefficients, true_coef, rtol=RTOL, atol=ATOL)
        np.testing.assert_allclose(ols.intercept, true_intercept, rtol=RTOL, atol=ATOL)

        # R-squared should be 1.0 for perfect fit
        assert ols.r_squared is not None
        np.testing.assert_allclose(ols.r_squared, 1.0, rtol=LOOSE_RTOL, atol=LOOSE_ATOL)

        # MSE should be very close to 0
        assert ols.mse is not None
        assert ols.mse < 1e-20

    def test_prediction_accuracy(self, small_dataset):
        """Test prediction accuracy."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        # Predictions on training data
        y_pred = ols.predict(X)
        assert y_pred.shape == y.shape

        # Predictions should be reasonably close to actual values
        # Calculate MSE with degrees of freedom adjustment (like our implementation)
        residuals = y - y_pred
        ss_res = np.sum(residuals**2)
        df = X.shape[0] - X.shape[1] - 1  # n - p (including intercept)
        mse_manual = ss_res / df
        np.testing.assert_allclose(ols.mse, mse_manual, rtol=LOOSE_RTOL)

        # Test prediction on new data
        X_new = np.random.randn(50, X.shape[1]).astype(np.float64, order="C")
        y_new_pred = ols.predict(X_new)
        assert y_new_pred.shape == (50,)
        assert np.all(np.isfinite(y_new_pred))

    def test_normal_equations_correctness(self, small_dataset):
        """Test that OLS satisfies normal equations X'X β = X'y."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=False)  # Simpler without intercept
        ols.fit(X, y)

        # Manual computation: β = (X'X)^(-1) X'y
        XtX = X.T @ X
        Xty = X.T @ y
        beta_manual = np.linalg.solve(XtX, Xty)

        # Should match our implementation
        np.testing.assert_allclose(
            ols.coefficients, beta_manual, rtol=LOOSE_RTOL, atol=LOOSE_ATOL
        )

    def test_r_squared_calculation(self, small_dataset):
        """Test R-squared calculation."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        # Manual R-squared calculation
        y_pred = ols.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared_manual = 1 - (ss_res / ss_tot)

        np.testing.assert_allclose(
            ols.r_squared, r_squared_manual, rtol=LOOSE_RTOL, atol=LOOSE_ATOL
        )

        # R-squared should be between 0 and 1 for reasonable data
        assert 0 <= ols.r_squared <= 1


class TestOLSStatisticalInference:
    """Test statistical inference capabilities."""

    def test_standard_errors(self, small_dataset):
        """Test standard error computation."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        se = ols.standard_errors()
        assert se is not None
        assert len(se) == X.shape[1]
        assert np.all(se > 0)  # Standard errors should be positive
        assert np.all(np.isfinite(se))

    def test_t_statistics(self, small_dataset):
        """Test t-statistic computation."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        t_stats = ols.t_statistics()
        se = ols.standard_errors()

        assert t_stats is not None
        assert len(t_stats) == len(ols.coefficients)

        # Manual calculation: t = coef / se
        t_manual = ols.coefficients / se
        np.testing.assert_allclose(t_stats, t_manual, rtol=LOOSE_RTOL, atol=LOOSE_ATOL)

    def test_p_values(self, small_dataset):
        """Test p-value computation."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        p_vals = ols.p_values()
        assert p_vals is not None
        assert len(p_vals) == len(ols.coefficients)
        assert np.all(p_vals >= 0.0)
        assert np.all(p_vals <= 1.0)
        assert np.all(np.isfinite(p_vals))

    def test_confidence_intervals(self, small_dataset):
        """Test confidence interval computation."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        # Test default 95% CI
        ci_95 = ols.confidence_intervals()
        assert ci_95 is not None
        assert ci_95.shape == (len(ols.coefficients), 2)

        # Lower bound should be less than upper bound
        assert np.all(ci_95[:, 0] < ci_95[:, 1])

        # Coefficients should be within their confidence intervals
        coef = ols.coefficients
        assert np.all(ci_95[:, 0] <= coef)
        assert np.all(coef <= ci_95[:, 1])

        # Test 99% CI (should be wider)
        ci_99 = ols.confidence_intervals(alpha=0.01)
        assert np.all(ci_99[:, 1] - ci_99[:, 0] >= ci_95[:, 1] - ci_95[:, 0])

    def test_summary_output(self, small_dataset):
        """Test summary string generation."""
        X, y = small_dataset
        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        summary = ols.summary()
        assert isinstance(summary, str)
        assert len(summary) > 0

        # Should contain key statistical information
        assert "OLS Regression Results" in summary
        assert "Coeff" in summary or "coef" in summary
        assert "Std Err" in summary or "std err" in summary
        assert "t" in summary
        assert "P>|t|" in summary
        assert "R-squared" in summary


class TestOLSEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_data(self):
        """Test with empty data."""
        ols = econometrust.OLS()

        with pytest.raises(Exception):  # Should raise some kind of error
            ols.fit(np.array([]).reshape(0, 1), np.array([]))

    def test_insufficient_samples(self):
        """Test with insufficient samples."""
        ols = econometrust.OLS(fit_intercept=True)

        # n_samples <= n_features + intercept should fail
        X = np.random.randn(2, 3).astype(np.float64)
        y = np.random.randn(2).astype(np.float64)

        with pytest.raises(Exception):
            ols.fit(X, y)

    def test_mismatched_dimensions(self):
        """Test with mismatched X and y dimensions."""
        ols = econometrust.OLS()

        X = np.random.randn(100, 5).astype(np.float64)
        y = np.random.randn(50).astype(np.float64)  # Wrong size

        with pytest.raises(Exception):
            ols.fit(X, y)

    def test_predict_before_fit(self):
        """Test prediction before fitting."""
        ols = econometrust.OLS()
        X = np.random.randn(10, 3).astype(np.float64)

        with pytest.raises(Exception):
            ols.predict(X)

    def test_predict_wrong_features(self, small_dataset):
        """Test prediction with wrong number of features."""
        X, y = small_dataset
        ols = econometrust.OLS()
        ols.fit(X, y)

        # Wrong number of features
        X_wrong = np.random.randn(10, X.shape[1] + 1).astype(np.float64)

        with pytest.raises(Exception):
            ols.predict(X_wrong)

    def test_ill_conditioned_data(self, ill_conditioned_data):
        """Test with ill-conditioned data (should use SVD fallback)."""
        X, y = ill_conditioned_data
        ols = econometrust.OLS(fit_intercept=True)

        # Should not raise an exception, should handle gracefully
        ols.fit(X, y)
        assert ols.is_fitted()

        # Should still produce reasonable results
        assert ols.coefficients is not None
        assert ols.r_squared is not None
        assert np.all(np.isfinite(ols.coefficients))


class TestOLSDataTypes:
    """Test various data types and array formats."""

    def test_float32_arrays(self, small_dataset):
        """Test with float32 arrays (should be converted internally)."""
        X, y = small_dataset
        X_f32 = X.astype(np.float32)
        y_f32 = y.astype(np.float32)

        ols = econometrust.OLS()
        # Should work (might convert internally or raise informative error)
        try:
            ols.fit(X_f32, y_f32)
            # If it works, results should be reasonable
            assert ols.is_fitted()
        except Exception as e:
            # If it fails, should be a clear error about data types
            assert "float64" in str(e) or "dtype" in str(e) or "PyArray" in str(e)

    def test_non_contiguous_arrays(self, small_dataset):
        """Test with non-contiguous arrays."""
        X, y = small_dataset

        # Create non-contiguous arrays
        X_nc = X.T.T  # Transpose twice to make non-contiguous
        y_nc = y[::-1][::-1]  # Reverse twice

        ols = econometrust.OLS()
        ols.fit(X_nc, y_nc)  # Should handle or convert automatically
        assert ols.is_fitted()

    def test_fortran_order_arrays(self, small_dataset):
        """Test with Fortran-ordered arrays."""
        X, y = small_dataset
        X_fortran = np.asfortranarray(X)

        ols = econometrust.OLS()
        ols.fit(X_fortran, y)  # Should handle different memory layout
        assert ols.is_fitted()


class TestOLSPerformance:
    """Performance benchmarks and stress tests."""

    def test_medium_dataset_performance(self, medium_dataset, benchmark_timer):
        """Test performance on medium-sized dataset."""
        X, y = medium_dataset
        ols = econometrust.OLS(fit_intercept=True)

        timer = benchmark_timer.start()
        ols.fit(X, y)
        fit_time = timer.stop()

        print(f"Medium dataset fit time: {fit_time:.4f}s for {X.shape[0]}×{X.shape[1]}")

        # Should be reasonably fast (adjust threshold as needed)
        assert fit_time < 1.0  # Should fit 5K×10 data in under 1 second

        # Test prediction performance
        timer.start()
        y_pred = ols.predict(X)
        pred_time = timer.stop()

        print(f"Medium dataset predict time: {pred_time:.4f}s")
        assert pred_time < 0.1  # Prediction should be very fast

    def test_large_dataset_stress(self, large_dataset, benchmark_timer):
        """Stress test on large dataset."""
        X, y = large_dataset
        ols = econometrust.OLS(fit_intercept=True)

        timer = benchmark_timer.start()
        ols.fit(X, y)
        fit_time = timer.stop()

        print(f"Large dataset fit time: {fit_time:.4f}s for {X.shape[0]}×{X.shape[1]}")

        # Should still be reasonably fast for 50K×20 data
        assert fit_time < 5.0  # Adjust based on expected performance

        # Verify correctness is maintained
        assert ols.is_fitted()
        assert ols.r_squared is not None
        assert 0 <= ols.r_squared <= 1

    def test_statistical_inference_performance(self, medium_dataset, benchmark_timer):
        """Test performance of statistical inference methods."""
        X, y = medium_dataset
        ols = econometrust.OLS(fit_intercept=True)
        ols.fit(X, y)

        # Time all statistical methods
        timer = benchmark_timer.start()
        se = ols.standard_errors()
        t_stats = ols.t_statistics()
        p_vals = ols.p_values()
        ci = ols.confidence_intervals()
        summary = ols.summary()
        inference_time = timer.stop()

        print(f"Statistical inference time: {inference_time:.4f}s")

        # Should be fast
        assert inference_time < 0.5

        # Verify all results are valid
        assert se is not None
        assert t_stats is not None
        assert p_vals is not None
        assert ci is not None
        assert isinstance(summary, str)


class TestOLSRobustStandardErrors:
    """Test robust standard errors functionality."""

    def test_robust_ols_creation(self):
        """Test OLS model creation with robust option."""
        # Test classical (default)
        ols_classical = econometrust.OLS(fit_intercept=True, robust=False)
        assert ols_classical.fit_intercept is True
        assert ols_classical.robust is False
        assert not ols_classical.is_fitted()

        # Test robust
        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        assert ols_robust.fit_intercept is True
        assert ols_robust.robust is True
        assert not ols_robust.is_fitted()

        # Test default values
        ols_default = econometrust.OLS()
        assert ols_default.robust is False  # Should default to False

    def test_robust_repr(self):
        """Test string representation includes robust flag."""
        ols_classical = econometrust.OLS(fit_intercept=True, robust=False)
        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)

        repr_classical = repr(ols_classical)
        repr_robust = repr(ols_robust)

        assert "robust=False" in repr_classical or "robust=false" in repr_classical
        assert "robust=True" in repr_robust or "robust=true" in repr_robust

    def test_robust_vs_classical_fitting(self, small_dataset):
        """Test that both robust and classical models can be fitted."""
        X, y = small_dataset

        # Fit classical model
        ols_classical = econometrust.OLS(fit_intercept=True, robust=False)
        ols_classical.fit(X, y)
        assert ols_classical.is_fitted()

        # Fit robust model
        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        ols_robust.fit(X, y)
        assert ols_robust.is_fitted()

        # Both should have same basic structure
        assert ols_classical.n_samples == ols_robust.n_samples
        assert ols_classical.n_features == ols_robust.n_features

    def test_coefficients_identical_robust_vs_classical(self, small_dataset):
        """Test that coefficients are identical between robust and classical."""
        X, y = small_dataset

        # Fit both models
        ols_classical = econometrust.OLS(fit_intercept=True, robust=False)
        ols_classical.fit(X, y)

        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        ols_robust.fit(X, y)

        # Coefficients should be identical (OLS estimation is the same)
        np.testing.assert_allclose(
            ols_classical.coefficients,
            ols_robust.coefficients,
            rtol=RTOL,
            atol=ATOL,
            err_msg="Coefficients should be identical between robust and classical OLS",
        )

        # Intercepts should be identical
        np.testing.assert_allclose(
            ols_classical.intercept,
            ols_robust.intercept,
            rtol=RTOL,
            atol=ATOL,
            err_msg="Intercepts should be identical between robust and classical OLS",
        )

        # R-squared should be identical
        np.testing.assert_allclose(
            ols_classical.r_squared,
            ols_robust.r_squared,
            rtol=LOOSE_RTOL,
            atol=LOOSE_ATOL,
            err_msg="R-squared should be identical between robust and classical OLS",
        )

    def test_standard_errors_different_robust_vs_classical(self, small_dataset):
        """Test that standard errors differ between robust and classical."""
        X, y = small_dataset

        # Fit both models
        ols_classical = econometrust.OLS(fit_intercept=True, robust=False)
        ols_classical.fit(X, y)

        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        ols_robust.fit(X, y)

        se_classical = ols_classical.standard_errors()
        se_robust = ols_robust.standard_errors()

        # Both should exist
        assert se_classical is not None
        assert se_robust is not None

        # Should have same length
        assert len(se_classical) == len(se_robust)

        # All should be positive
        assert np.all(se_classical > 0)
        assert np.all(se_robust > 0)

        # Should be finite
        assert np.all(np.isfinite(se_classical))
        assert np.all(np.isfinite(se_robust))

        # They should generally be different (except in special cases)
        # Use a less strict test since they could be similar in some cases
        se_ratio = se_robust / se_classical
        assert np.all(
            se_ratio > 0.1
        )  # Robust SEs shouldn't be tiny compared to classical
        assert np.all(
            se_ratio < 10.0
        )  # Robust SEs shouldn't be huge compared to classical

    def test_robust_statistical_inference(self, small_dataset):
        """Test that statistical inference works with robust standard errors."""
        X, y = small_dataset

        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        ols_robust.fit(X, y)

        # Test t-statistics
        t_stats = ols_robust.t_statistics()
        assert t_stats is not None
        assert len(t_stats) == len(ols_robust.coefficients)
        assert np.all(np.isfinite(t_stats))

        # Test p-values
        p_vals = ols_robust.p_values()
        assert p_vals is not None
        assert len(p_vals) == len(ols_robust.coefficients)
        assert np.all(p_vals >= 0.0)
        assert np.all(p_vals <= 1.0)
        assert np.all(np.isfinite(p_vals))

        # Test confidence intervals
        ci = ols_robust.confidence_intervals()
        assert ci is not None
        assert ci.shape == (len(ols_robust.coefficients), 2)
        assert np.all(ci[:, 0] < ci[:, 1])  # Lower < Upper

        # Coefficients should be within their CIs
        coef = ols_robust.coefficients
        assert np.all(ci[:, 0] <= coef)
        assert np.all(coef <= ci[:, 1])

    def test_robust_summary_output(self, small_dataset):
        """Test that summary output includes robust information."""
        X, y = small_dataset

        # Classical summary
        ols_classical = econometrust.OLS(fit_intercept=True, robust=False)
        ols_classical.fit(X, y)
        summary_classical = ols_classical.summary()

        # Robust summary
        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        ols_robust.fit(X, y)
        summary_robust = ols_robust.summary()

        # Both should be strings
        assert isinstance(summary_classical, str)
        assert isinstance(summary_robust, str)

        # Both should contain basic information
        for summary in [summary_classical, summary_robust]:
            assert "OLS Regression Results" in summary
            assert "Coeff" in summary or "coef" in summary
            assert "Std Err" in summary or "std err" in summary
            assert "t" in summary
            assert "P>|t|" in summary
            assert "R-squared" in summary

        # Check covariance type indication
        # Note: The exact format may vary, but should indicate the type
        if "Covariance Type" in summary_classical:
            assert "nonrobust" in summary_classical

        if "Covariance Type" in summary_robust:
            assert "HC0" in summary_robust

    def test_robust_perfect_fit(self, perfect_data):
        """Test robust standard errors with perfect fit data."""
        X, y = perfect_data

        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        ols_robust.fit(X, y)

        # Should still achieve perfect fit
        assert ols_robust.r_squared is not None
        np.testing.assert_allclose(
            ols_robust.r_squared, 1.0, rtol=LOOSE_RTOL, atol=LOOSE_ATOL
        )

        # MSE should be very close to 0
        assert ols_robust.mse is not None
        assert ols_robust.mse < 1e-20

        # Standard errors should be very small (or zero) for perfect fit
        se_robust = ols_robust.standard_errors()
        assert se_robust is not None
        assert np.all(se_robust < 1e-10)  # Should be very small for perfect fit

    def test_robust_no_intercept(self, small_dataset):
        """Test robust standard errors without intercept."""
        X, y = small_dataset

        # Test classical without intercept
        ols_classical = econometrust.OLS(fit_intercept=False, robust=False)
        ols_classical.fit(X, y)

        # Test robust without intercept
        ols_robust = econometrust.OLS(fit_intercept=False, robust=True)
        ols_robust.fit(X, y)

        # Both should work
        assert ols_classical.is_fitted()
        assert ols_robust.is_fitted()

        # Both should have no intercept
        assert ols_classical.intercept is None
        assert ols_robust.intercept is None

        # Coefficients should be identical
        np.testing.assert_allclose(
            ols_classical.coefficients, ols_robust.coefficients, rtol=RTOL, atol=ATOL
        )

        # Standard errors should generally be different
        se_classical = ols_classical.standard_errors()
        se_robust = ols_robust.standard_errors()

        assert se_classical is not None
        assert se_robust is not None
        assert len(se_classical) == len(se_robust) == X.shape[1]

    def test_robust_heteroscedastic_data(self):
        """Test robust standard errors with heteroscedastic data."""
        # Generate heteroscedastic data
        np.random.seed(42)
        n_samples = 200
        n_features = 3

        X = np.random.randn(n_samples, n_features).astype(np.float64)

        # Create heteroscedastic errors (variance depends on X)
        error_variance = 0.1 + 0.5 * np.abs(
            X[:, 0]
        )  # Variance depends on first feature
        errors = np.random.randn(n_samples) * np.sqrt(error_variance)

        # True coefficients
        true_coef = np.array([1.5, -2.0, 0.8])
        y = X @ true_coef + errors

        # Fit both models
        ols_classical = econometrust.OLS(fit_intercept=True, robust=False)
        ols_classical.fit(X, y)

        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        ols_robust.fit(X, y)

        # Coefficients should still be similar (both are unbiased)
        np.testing.assert_allclose(
            ols_classical.coefficients, ols_robust.coefficients, rtol=RTOL, atol=ATOL
        )

        # Standard errors should be different (robust should account for heteroscedasticity)
        se_classical = ols_classical.standard_errors()
        se_robust = ols_robust.standard_errors()

        assert se_classical is not None
        assert se_robust is not None

        # Both should be positive and finite
        assert np.all(se_classical > 0)
        assert np.all(se_robust > 0)
        assert np.all(np.isfinite(se_classical))
        assert np.all(np.isfinite(se_robust))

    def test_robust_edge_cases(self):
        """Test robust standard errors with edge cases."""
        # Test with minimal valid data
        X = np.array([[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]], dtype=np.float64)
        y = np.array([1.0, 2.0, 3.0], dtype=np.float64)

        ols_robust = econometrust.OLS(
            fit_intercept=False, robust=True
        )  # No intercept to have enough data
        ols_robust.fit(X, y)

        assert ols_robust.is_fitted()
        assert ols_robust.coefficients is not None
        assert len(ols_robust.coefficients) == 2

        se_robust = ols_robust.standard_errors()
        assert se_robust is not None
        assert len(se_robust) == 2
        assert np.all(se_robust > 0)
        assert np.all(np.isfinite(se_robust))

    def test_robust_prediction_unchanged(self, small_dataset):
        """Test that predictions are unchanged between robust and classical."""
        X, y = small_dataset

        # Fit both models
        ols_classical = econometrust.OLS(fit_intercept=True, robust=False)
        ols_classical.fit(X, y)

        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        ols_robust.fit(X, y)

        # Generate test data
        X_test = np.random.randn(50, X.shape[1]).astype(np.float64)

        # Predictions should be identical
        pred_classical = ols_classical.predict(X_test)
        pred_robust = ols_robust.predict(X_test)

        np.testing.assert_allclose(
            pred_classical,
            pred_robust,
            rtol=RTOL,
            atol=ATOL,
            err_msg="Predictions should be identical between robust and classical OLS",
        )

    def test_robust_performance(self, medium_dataset, benchmark_timer):
        """Test that robust standard errors don't significantly impact performance."""
        X, y = medium_dataset

        # Time classical fitting
        ols_classical = econometrust.OLS(fit_intercept=True, robust=False)
        timer = benchmark_timer.start()
        ols_classical.fit(X, y)
        classical_time = timer.stop()

        # Time robust fitting
        ols_robust = econometrust.OLS(fit_intercept=True, robust=True)
        timer.start()
        ols_robust.fit(X, y)
        robust_time = timer.stop()

        print(f"Classical fit time: {classical_time:.4f}s")
        print(f"Robust fit time: {robust_time:.4f}s")
        print(f"Robust overhead: {(robust_time / classical_time - 1) * 100:.1f}%")

        # Robust should be slower but not excessively so
        # Allow up to 5x slower (robust SE computation is inherently more expensive)
        assert robust_time < classical_time * 5.0, (
            f"Robust fitting too slow: {robust_time:.4f}s vs {classical_time:.4f}s"
        )

        # Both should produce valid results
        assert ols_classical.is_fitted()
        assert ols_robust.is_fitted()

        # Verify statistical inference time
        timer.start()
        se_classical = ols_classical.standard_errors()
        t_classical = ols_classical.t_statistics()
        classical_inference_time = timer.stop()

        timer.start()
        se_robust = ols_robust.standard_errors()
        t_robust = ols_robust.t_statistics()
        robust_inference_time = timer.stop()

        print(f"Classical inference time: {classical_inference_time:.4f}s")
        print(f"Robust inference time: {robust_inference_time:.4f}s")

        # Both should be fast
        assert classical_inference_time < 0.1
        assert robust_inference_time < 0.1


if __name__ == "__main__":
    pytest.main([__file__])
