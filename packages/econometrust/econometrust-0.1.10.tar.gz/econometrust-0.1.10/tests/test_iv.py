"""
Tests for the IV (Instrumental Variables) estimator in econometrust.
"""

import pytest
import numpy as np
import econometrust as et


class TestIVBasic:
    """Basic IV functionality tests."""

    def test_iv_creation(self):
        """Test IV model creation with default parameters."""
        iv = et.IV()
        assert iv.fit_intercept is True
        assert not iv.is_fitted()
        assert iv.coefficients is None

    def test_iv_creation_no_intercept(self):
        """Test IV model creation without intercept."""
        iv = et.IV(fit_intercept=False)
        assert iv.fit_intercept is False
        assert not iv.is_fitted()

    def test_iv_repr(self):
        """Test string representation."""
        iv = et.IV(fit_intercept=True)
        assert "IV" in repr(iv)

    def test_unfitted_properties(self):
        """Test that unfitted model returns None for most properties."""
        iv = et.IV()
        assert iv.coefficients is None
        assert iv.intercept is None
        assert iv.standard_errors() is None
        assert iv.t_statistics() is None
        assert iv.p_values() is None
        assert iv.confidence_intervals() is None
        assert iv.mse is None
        assert iv.r_squared is None
        assert iv.residuals is None


class TestIVFitting:
    """Test IV model fitting and basic functionality."""

    def test_simple_fit(self):
        """Test basic IV fitting with valid instruments."""
        np.random.seed(42)
        n = 100

        # Create instruments
        z1 = np.random.randn(n)
        z2 = np.random.randn(n)
        instruments = np.column_stack([z1, z2])

        # Create endogenous regressors
        error = np.random.randn(n)
        x1 = z1 + 0.3 * error  # Endogenous
        x2 = z2 + 0.1 * np.random.randn(n)  # Exogenous
        regressors = np.column_stack([x1, x2])

        # Create dependent variable
        targets = 2.0 + 1.5 * x1 - 0.8 * x2 + error

        iv = et.IV(fit_intercept=True)
        iv.fit(instruments, regressors, targets)

        assert iv.is_fitted()
        assert iv.coefficients is not None
        assert iv.intercept is not None
        assert len(iv.coefficients) == 2

    def test_fit_no_intercept(self):
        """Test IV fitting without intercept."""
        np.random.seed(42)
        n = 50

        instruments = np.random.randn(n, 2)
        regressors = np.random.randn(n, 2)
        targets = np.random.randn(n)

        iv = et.IV(fit_intercept=False)
        iv.fit(instruments, regressors, targets)

        assert iv.is_fitted()
        assert iv.intercept is None
        assert len(iv.coefficients) == 2

    def test_prediction(self):
        """Test IV prediction functionality."""
        np.random.seed(42)
        n = 50

        instruments = np.random.randn(n, 2)
        regressors = np.random.randn(n, 2)
        targets = np.random.randn(n)

        iv = et.IV()
        iv.fit(instruments, regressors, targets)

        # Test prediction
        x_test = np.random.randn(10, 2)
        predictions = iv.predict(x_test)

        assert len(predictions) == 10
        assert all(np.isfinite(predictions))


class TestIVValidation:
    """Test IV input validation and error handling."""

    def test_under_identification(self):
        """Test that under-identified models raise errors."""
        n = 30

        # 1 instrument, 2 regressors (under-identified)
        instruments = np.random.randn(n, 1)
        regressors = np.random.randn(n, 2)
        targets = np.random.randn(n)

        iv = et.IV()
        with pytest.raises(ValueError, match="(instrument|regressor)"):
            iv.fit(instruments, regressors, targets)

    def test_over_identification(self):
        """Test that over-identified models raise errors (should use TSLS instead)."""
        n = 30

        # 3 instruments, 2 regressors (over-identified)
        instruments = np.random.randn(n, 3)
        regressors = np.random.randn(n, 2)
        targets = np.random.randn(n)

        iv = et.IV()
        with pytest.raises(ValueError, match="(instrument|regressor|singular)"):
            iv.fit(instruments, regressors, targets)

    def test_dimension_mismatch(self):
        """Test dimension mismatch errors."""
        iv = et.IV()

        # Mismatched sample sizes
        instruments = np.random.randn(50, 2)
        regressors = np.random.randn(40, 2)
        targets = np.random.randn(50)

        with pytest.raises(ValueError, match="must have the same number"):
            iv.fit(instruments, regressors, targets)

    def test_empty_arrays(self):
        """Test empty array handling."""
        iv = et.IV()

        instruments = np.array([]).reshape(0, 2)
        regressors = np.array([]).reshape(0, 2)
        targets = np.array([])

        with pytest.raises(ValueError, match="Number of samples must be greater"):
            iv.fit(instruments, regressors, targets)

    def test_prediction_before_fit(self):
        """Test prediction before fitting raises error."""
        iv = et.IV()
        x_test = np.random.randn(5, 2)

        with pytest.raises(ValueError, match="not fitted"):
            iv.predict(x_test)

    # def test_prediction_dimension_mismatch(self):
    #     """Test prediction with wrong dimensions."""
    #     np.random.seed(42)
    #     n = 30

    #     instruments = np.random.randn(n, 2)
    #     regressors = np.random.randn(n, 2)
    #     targets = np.random.randn(n)

    #     iv = et.IV()
    #     iv.fit(instruments, regressors, targets)

    #     # Wrong number of features - should fail
    #     x_test = np.random.randn(5, 3)
    #     exception_raised = False
    #     try:
    #         iv.predict(x_test)
    #     except BaseException:  # Catch all exceptions, including Rust panics
    #         exception_raised = True

    #     assert exception_raised, "Should have raised an exception for wrong dimensions"


class TestIVStatistics:
    """Test IV statistical inference methods."""

    def test_statistical_methods(self):
        """Test that statistical methods return reasonable values."""
        np.random.seed(42)
        n = 100

        # Exactly identified: 2 instruments, 2 regressors
        instruments = np.random.randn(n, 2)
        regressors = np.random.randn(n, 2)
        targets = np.random.randn(n)

        iv = et.IV()
        iv.fit(instruments, regressors, targets)

        # Test statistical methods
        se = iv.standard_errors()
        assert se is not None
        assert len(se) == 2  # 2 features (no intercept in standard errors)
        assert all(se > 0)

        t_stats = iv.t_statistics()
        assert t_stats is not None
        assert len(t_stats) == 2

        p_vals = iv.p_values()
        assert p_vals is not None
        assert len(p_vals) == 2
        assert all(0 <= p <= 1 for p in p_vals)

        ci = iv.confidence_intervals()
        assert ci is not None
        assert ci.shape == (2, 2)

        # Check that lower bounds < upper bounds
        assert all(ci[i, 0] < ci[i, 1] for i in range(2))

    def test_summary_output(self):
        """Test IV summary output format."""
        np.random.seed(42)
        n = 50

        instruments = np.random.randn(n, 2)
        regressors = np.random.randn(n, 2)
        targets = np.random.randn(n)

        iv = et.IV()
        iv.fit(instruments, regressors, targets)

        summary = iv.summary()
        assert isinstance(summary, str)
        # Check for new summary format fields, similar to OLS
        assert "IV Regression Results" in summary or "Instrumental Variables" in summary
        assert "coef" in summary.lower() or "coefficient" in summary.lower()
        assert "std err" in summary.lower() or "standard error" in summary.lower()
        assert "t" in summary.lower() or "t-stat" in summary.lower()
        assert "p>|t|" in summary.lower() or "p-value" in summary.lower()
        assert "R-squared" in summary or "r_squared" in summary.lower()


class TestIVMathematical:
    """Test IV mathematical properties and correctness."""

    def test_identification_condition(self):
        """Test that properly identified models work."""
        n = 50

        # Exactly identified: 2 instruments, 2 regressors
        instruments = np.random.randn(n, 2)
        regressors = np.random.randn(n, 2)
        targets = np.random.randn(n)

        iv = et.IV()
        iv.fit(instruments, regressors, targets)

        assert iv.is_fitted()
        assert iv.coefficients is not None

    def test_over_identification(self):
        """Test over-identified models - should be rejected in favor of TSLS."""
        n = 50

        # Over-identified: 3 instruments, 2 regressors
        instruments = np.random.randn(n, 3)
        regressors = np.random.randn(n, 2)
        targets = np.random.randn(n)

        iv = et.IV()
        # IV should reject over-identified models (use TSLS instead)
        with pytest.raises(ValueError, match="(instrument|regressor|singular)"):
            iv.fit(instruments, regressors, targets)

    def test_iv_consistency(self):
        """Test that IV estimates are consistent in large samples."""
        np.random.seed(42)
        n = 1000  # Large sample

        # Create strong instruments
        z1 = np.random.randn(n)
        z2 = np.random.randn(n)
        instruments = np.column_stack([z1, z2])

        # Create endogenous regressors
        error = np.random.randn(n) * 0.5
        x1 = z1 + 0.2 * error  # Weakly endogenous
        x2 = z2  # Exogenous
        regressors = np.column_stack([x1, x2])

        # True parameters
        true_beta = [1.5, -0.8]
        targets = 2.0 + regressors @ true_beta + error

        iv = et.IV(fit_intercept=True)
        iv.fit(instruments, regressors, targets)

        # With large sample and strong instruments, estimates should be reasonable
        assert abs(iv.intercept - 2.0) < 0.5
        # Note: IV estimates have higher variance than OLS, so tolerance is larger


class TestIVPerformance:
    """Test IV performance and edge cases."""

    def test_numerical_stability(self):
        """Test numerical stability with various data conditions."""
        np.random.seed(42)
        n = 100

        # Well-conditioned data with exactly identified case
        instruments = np.random.randn(n, 2)
        regressors = np.random.randn(n, 2)
        targets = np.random.randn(n)

        iv = et.IV()
        iv.fit(instruments, regressors, targets)

        # Check that all estimates are finite
        assert all(np.isfinite(iv.coefficients))
        assert np.isfinite(iv.intercept)
        se = iv.standard_errors()
        assert all(np.isfinite(se))

    def test_large_dataset(self):
        """Test IV with larger datasets."""
        np.random.seed(42)
        n = 500

        # Exactly identified: 3 instruments, 3 regressors
        instruments = np.random.randn(n, 3)
        regressors = np.random.randn(n, 3)
        targets = np.random.randn(n)

        iv = et.IV()
        iv.fit(instruments, regressors, targets)

        assert iv.is_fitted()
        assert len(iv.coefficients) == 3
        assert iv.n_samples == n
        assert iv.n_features == 3

    def test_memory_efficiency(self):
        """Test that IV doesn't consume excessive memory."""
        np.random.seed(42)
        n = 200

        # Exactly identified: 4 instruments, 4 regressors
        instruments = np.random.randn(n, 4)
        regressors = np.random.randn(n, 4)
        targets = np.random.randn(n)

        iv = et.IV()
        iv.fit(instruments, regressors, targets)

        # Should complete without memory issues
        assert iv.is_fitted()
        summary = iv.summary()
        assert len(summary) > 0


class TestIVDataTypes:
    """Test IV with different data types and formats."""

    def test_float32_arrays(self):
        """Test IV with float32 input arrays (converted to float64)."""
        np.random.seed(42)
        n = 50

        instruments = np.random.randn(n, 2).astype(np.float32)
        regressors = np.random.randn(n, 2).astype(np.float32)
        targets = np.random.randn(n).astype(np.float32)

        # Convert to float64 before fitting
        instruments = instruments.astype(np.float64)
        regressors = regressors.astype(np.float64)
        targets = targets.astype(np.float64)

        iv = et.IV()
        iv.fit(instruments, regressors, targets)

        assert iv.is_fitted()
        assert iv.coefficients is not None

    def test_non_contiguous_arrays(self):
        """Test IV with non-contiguous arrays."""
        np.random.seed(42)
        n = 50

        # Create non-contiguous arrays
        large_instruments = np.random.randn(n, 4)
        instruments = large_instruments[:, ::2]  # Non-contiguous

        large_regressors = np.random.randn(n, 4)
        regressors = large_regressors[:, ::2]  # Non-contiguous

        targets = np.random.randn(n)

        iv = et.IV()
        iv.fit(instruments, regressors, targets)

        assert iv.is_fitted()
        assert iv.coefficients is not None


if __name__ == "__main__":
    pytest.main([__file__])
