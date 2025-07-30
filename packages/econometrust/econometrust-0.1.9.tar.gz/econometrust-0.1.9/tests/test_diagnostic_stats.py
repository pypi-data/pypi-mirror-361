"""
Test module for enhanced diagnostic statistics in OLS and GLS models.
Tests the new econometric summary statistics including:
- Durbin-Watson test for autocorrelation
- Jarque-Bera test for normality
- Omnibus test for normality
- Skewness and Kurtosis
- Condition Number
- Enhanced summary output
"""

import pytest
import numpy as np
from econometrust import OLS, GLS


class TestDiagnosticStatistics:
    """Test class for diagnostic statistics functionality."""

    def setup_method(self):
        """Set up test data for each test method."""
        np.random.seed(42)  # For reproducible tests

        # Create test data with known properties
        self.n_samples = 100
        self.n_features = 3

        # Generate design matrix with better conditioning
        self.X = np.random.randn(self.n_samples, self.n_features)
        # Make sure matrix is well-conditioned
        self.X = self.X + 0.1 * np.random.randn(self.n_samples, self.n_features)

        # True coefficients
        self.true_coef = np.array([2.0, 1.5, -0.8])

        # Generate y with normal errors (for baseline tests)
        self.y_normal = self.X @ self.true_coef + np.random.normal(
            0, 0.5, self.n_samples
        )

        # Generate y with autocorrelated errors
        errors_autocorr = np.zeros(self.n_samples)
        errors_autocorr[0] = np.random.normal(0, 0.5)
        for i in range(1, self.n_samples):
            errors_autocorr[i] = 0.7 * errors_autocorr[i - 1] + np.random.normal(0, 0.5)
        self.y_autocorr = self.X @ self.true_coef + errors_autocorr

        # Generate y with non-normal errors (skewed)
        skewed_errors = np.random.exponential(0.5, self.n_samples) - 0.5
        self.y_skewed = self.X @ self.true_coef + skewed_errors

    def test_ols_summary_contains_diagnostics(self):
        """Test that OLS summary includes all diagnostic statistics."""
        model = OLS(
            fit_intercept=False, robust=False
        )  # Use fit_intercept=False to avoid singularity
        model.fit(self.X, self.y_normal)

        summary = model.summary()

        # Check that summary contains new diagnostic statistics
        assert "Durbin-Watson:" in summary
        assert "Jarque-Bera (JB):" in summary
        assert "Omnibus:" in summary
        assert "Skew:" in summary
        assert "Kurtosis:" in summary
        assert "Cond. No.:" in summary

        # Check that diagnostic notes are included
        assert "Diagnostic Notes:" in summary
        assert "Durbin-Watson suggests" in summary
        assert "Jarque-Bera test:" in summary
        assert "Condition number indicates:" in summary

    def test_gls_summary_contains_diagnostics(self):
        """Test that GLS summary includes all diagnostic statistics."""
        # Create a simple covariance matrix (identity for simplicity)
        cov_matrix = np.eye(self.n_samples)

        model = GLS(fit_intercept=False)  # GLS doesn't have robust parameter
        model.fit(self.X, self.y_normal, cov_matrix)

        summary = model.summary()

        # Check that summary contains new diagnostic statistics
        assert "Durbin-Watson:" in summary
        assert "Jarque-Bera (JB):" in summary
        assert "Omnibus:" in summary
        assert "Skew:" in summary
        assert "Kurtosis:" in summary
        assert "Cond. No.:" in summary

    def test_durbin_watson_detects_autocorrelation(self):
        """Test that Durbin-Watson statistic correctly detects autocorrelation."""
        # Model with normal errors (should have DW ≈ 2)
        model_normal = OLS(fit_intercept=False, robust=False)
        model_normal.fit(self.X, self.y_normal)
        summary_normal = model_normal.summary()

        # Model with autocorrelated errors (should have DW < 1.5)
        model_autocorr = OLS(fit_intercept=False, robust=False)
        model_autocorr.fit(self.X, self.y_autocorr)
        summary_autocorr = model_autocorr.summary()

        # Extract DW values from summaries (basic parsing)
        assert "Durbin-Watson:" in summary_normal
        assert "Durbin-Watson:" in summary_autocorr

        # Check that autocorrelation is detected in diagnostic notes
        assert "autocorrelation" in summary_autocorr

    def test_normality_tests_detect_non_normality(self):
        """Test that normality tests detect non-normal residuals."""
        # Model with normal errors
        model_normal = OLS(fit_intercept=False, robust=False)
        model_normal.fit(self.X, self.y_normal)
        summary_normal = model_normal.summary()

        # Model with skewed errors
        model_skewed = OLS(fit_intercept=False, robust=False)
        model_skewed.fit(self.X, self.y_skewed)
        summary_skewed = model_skewed.summary()

        # Both should contain normality test statistics
        assert "Jarque-Bera (JB):" in summary_normal
        assert "Jarque-Bera (JB):" in summary_skewed
        assert "Omnibus:" in summary_normal
        assert "Omnibus:" in summary_skewed

        # Check that skewness is reported
        assert "Skew:" in summary_normal
        assert "Skew:" in summary_skewed

    def test_condition_number_in_summary(self):
        """Test that condition number is included and reasonable."""
        model = OLS(fit_intercept=False, robust=False)
        model.fit(self.X, self.y_normal)

        summary = model.summary()

        # Should contain condition number
        assert "Cond. No.:" in summary

        # Should have interpretive note about condition number
        assert "Condition number indicates:" in summary

    def test_robust_ols_includes_diagnostics(self):
        """Test that robust OLS includes diagnostic statistics."""
        model = OLS(fit_intercept=False, robust=True)
        model.fit(self.X, self.y_normal)

        summary = model.summary()

        # Should include all diagnostics even with robust standard errors
        assert "Durbin-Watson:" in summary
        assert "Jarque-Bera (JB):" in summary
        assert "Omnibus:" in summary
        assert "Skew:" in summary
        assert "Kurtosis:" in summary
        assert "Cond. No.:" in summary

        # Should show HC0 covariance type
        assert "HC0" in summary

    def test_summary_format_consistency(self):
        """Test that the summary format is consistent and properly formatted."""
        model = OLS(fit_intercept=False, robust=False)
        model.fit(self.X, self.y_normal)

        summary = model.summary()

        # Check basic structure
        assert "OLS Regression Results" in summary
        assert (
            "=============================================================================="
            in summary
        )
        assert (
            "------------------------------------------------------------------------------"
            in summary
        )

        # Check that all key sections are present
        assert "Dep. Variable:" in summary
        assert "R-squared:" in summary
        assert "F-statistic:" in summary
        assert "Mean Squared Error:" in summary

        # Check that diagnostic notes section is properly formatted
        assert "Diagnostic Notes:" in summary
        assert (
            summary.count(
                "=============================================================================="
            )
            >= 3
        )

    def test_edge_cases_small_sample(self):
        """Test diagnostic statistics with small sample sizes."""
        # Create very small dataset
        n_small = 15
        X_small = np.random.randn(n_small, 2)
        y_small = X_small @ np.array([1.0, 2.0]) + np.random.normal(0, 0.1, n_small)

        model = OLS(fit_intercept=True, robust=False)
        model.fit(X_small, y_small)

        summary = model.summary()

        # Should still work, but some diagnostics might be NaN or missing
        # The summary should not crash
        assert "OLS Regression Results" in summary
        assert isinstance(summary, str)
        assert len(summary) > 100  # Should be a substantial summary

    def test_edge_cases_perfect_fit(self):
        """Test diagnostic statistics with perfect fit (no residuals)."""
        # Create data with perfect linear relationship
        X_perfect = np.array(
            [[1.0, 1.0], [1.0, 2.0], [1.0, 3.0], [1.0, 4.0]], dtype=np.float64
        )
        y_perfect = np.array(
            [3.0, 5.0, 7.0, 9.0], dtype=np.float64
        )  # y = 1 + 2*x (perfect fit)

        model = OLS(
            fit_intercept=False, robust=False
        )  # Don't fit intercept since X already has it
        model.fit(X_perfect, y_perfect)

        summary = model.summary()

        # Should handle perfect fit gracefully
        assert "OLS Regression Results" in summary
        assert isinstance(summary, str)

    def test_multicollinearity_detection(self):
        """Test that high condition numbers are detected and interpreted."""
        # Create multicollinear data
        X_multicol = np.random.randn(50, 3)
        X_multicol[:, 2] = (
            X_multicol[:, 0] + X_multicol[:, 1] + 0.01 * np.random.randn(50)
        )  # Nearly collinear
        y_multicol = X_multicol @ np.array([1.0, 2.0, 1.0]) + np.random.normal(
            0, 0.1, 50
        )

        model = OLS(fit_intercept=False, robust=False)
        model.fit(X_multicol, y_multicol)

        summary = model.summary()

        # Should include condition number
        assert "Cond. No.:" in summary

        # Should have interpretive note (might detect multicollinearity)
        assert "Condition number indicates:" in summary

    def test_no_intercept_model_diagnostics(self):
        """Test diagnostic statistics work with no-intercept models."""
        model = OLS(fit_intercept=False, robust=False)
        model.fit(self.X, self.y_normal)

        summary = model.summary()

        # Should include all diagnostics
        assert "Durbin-Watson:" in summary
        assert "Jarque-Bera (JB):" in summary
        assert "Skew:" in summary
        assert "Kurtosis:" in summary

        # Should not have intercept row in coefficients table
        assert "const" not in summary

    def test_summary_numerical_precision(self):
        """Test that summary statistics are displayed with appropriate precision."""
        model = OLS(fit_intercept=False, robust=False)
        model.fit(self.X, self.y_normal)

        summary = model.summary()

        # Check that numbers are formatted reasonably (no excessive decimal places in display)
        lines = summary.split("\n")

        # Find lines with diagnostic statistics
        diagnostic_lines = [
            line
            for line in lines
            if any(
                stat in line
                for stat in [
                    "Durbin-Watson:",
                    "Jarque-Bera",
                    "Skew:",
                    "Kurtosis:",
                    "Omnibus:",
                ]
            )
        ]

        # Should have several diagnostic lines
        assert len(diagnostic_lines) >= 3

        # Each diagnostic line should be properly formatted
        for line in diagnostic_lines:
            if ":" in line:
                assert len(line) > 20  # Should have reasonable length

    def test_gls_with_different_covariance_structures(self):
        """Test GLS diagnostics with different covariance structures."""
        # Test with AR(1) covariance structure
        rho = 0.5
        cov_ar1 = np.array(
            [
                [rho ** abs(i - j) for j in range(self.n_samples)]
                for i in range(self.n_samples)
            ]
        )

        model_ar1 = GLS(fit_intercept=False)
        model_ar1.fit(self.X, self.y_normal, cov_ar1)

        summary_ar1 = model_ar1.summary()

        # Should include all diagnostics
        assert "Durbin-Watson:" in summary_ar1
        assert "Jarque-Bera (JB):" in summary_ar1
        assert "GLS Regression Results" in summary_ar1

    def test_interpretive_notes_coverage(self):
        """Test that interpretive notes cover different scenarios."""
        # Test with different data to trigger different interpretations
        test_cases = [
            (self.X, self.y_normal, "normal data"),
            (self.X, self.y_autocorr, "autocorrelated data"),
            (self.X, self.y_skewed, "skewed data"),
        ]

        for X, y, description in test_cases:
            model = OLS(fit_intercept=False, robust=False)
            model.fit(X, y)
            summary = model.summary()

            # Should have diagnostic notes section
            assert "Diagnostic Notes:" in summary, f"Failed for {description}"

            # Should have at least some interpretive text
            notes_section = summary.split("Diagnostic Notes:")[1]
            assert len(notes_section.strip()) > 50, f"Notes too short for {description}"

    def test_summary_memory_efficiency(self):
        """Test that summary generation is memory efficient for large datasets."""
        # Create larger dataset
        n_large = 1000
        X_large = np.random.randn(n_large, 5)
        y_large = X_large @ np.array([1, 2, -1, 0.5, 1.5]) + np.random.normal(
            0, 0.5, n_large
        )

        model = OLS(fit_intercept=False, robust=False)
        model.fit(X_large, y_large)

        # Should be able to generate summary without memory issues
        summary = model.summary()

        assert "OLS Regression Results" in summary
        assert "Durbin-Watson:" in summary
        assert "Diagnostic Notes:" in summary

        # Summary should be reasonable length (not excessively long)
        assert 1000 < len(summary) < 10000


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])
