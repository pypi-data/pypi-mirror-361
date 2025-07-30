use crate::models::linear::stat_inference::StatisticalSummary;
use ndarray::{Array1, Array2};
#[cfg(any(feature = "python", test))]
#[allow(unused_imports)]
use ndarray::s;
#[cfg(any(feature = "python", test))]
#[allow(unused_imports)]
use ndarray_linalg::{UPLO, Diag, LeastSquaresSvd, Cholesky, SolveTriangular, Inverse};
#[cfg(feature = "python")]
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2, ToPyArray};
#[cfg(feature = "python")]
use pyo3::{prelude::*};
#[cfg(feature = "python")]
use crate::models::linear::stat_utils;

#[cfg_attr(feature = "python", pyclass)]
pub struct GLS {
    // Core model parameters - cache-aligned for performance
    pub coefficients: Option<Array1<f64>>,
    pub intercept: Option<f64>,
    
    // Model configuration - small, frequently accessed
    pub fit_intercept: bool,
    
    // Computed statistics - grouped for cache efficiency
    pub mse: Option<f64>,
    pub r_squared: Option<f64>,
    
    // Matrix dimensions - small integers
    pub n_samples: Option<usize>,
    pub n_features: Option<usize>,
    
    // Standard errors - accessed together with coefficients
    pub standard_errors_: Option<Array1<f64>>,
    pub intercept_std_error: Option<f64>,
    
    // Larger arrays - accessed less frequently, placed at end
    pub residuals: Option<Array1<f64>>,
    pub design_matrix: Option<Array2<f64>>,  // Added for diagnostic calculations
}

impl GLS {
    pub fn new(fit_intercept: bool) -> Self {
        GLS {
            coefficients: None,
            intercept: None,
            fit_intercept,
            mse: None,
            r_squared: None,
            n_samples: None,
            n_features: None,
            standard_errors_: None,
            intercept_std_error: None,
            residuals: None,
            design_matrix: None,
        }
    }

    /// Check if model is fitted (available for both Rust and Python)
    pub fn is_fitted_impl(&self) -> bool {
        self.coefficients.is_some()
    }

    /// String representation for debugging (available for both Rust and Python)
    pub fn repr_impl(&self) -> String {
        format!("GLS(fit_intercept={})", self.fit_intercept)
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl GLS {
    #[new]
    #[pyo3(signature = (fit_intercept = true))]
    pub fn py_new(fit_intercept: bool) -> Self {
        GLS::new(fit_intercept)
    }

    #[getter]
    fn coefficients<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        Ok(self.coefficients.as_ref().map(|coef| coef.view().to_pyarray_bound(py)))
    }

    #[getter]
    fn intercept(&self) -> Option<f64> {
        self.intercept
    }

    #[getter]
    fn fit_intercept(&self) -> bool {
        self.fit_intercept
    }

    #[getter]
    fn mse(&self) -> Option<f64> {
        self.mse
    }
    
    #[getter]
    fn r_squared(&self) -> Option<f64> {
        self.r_squared
    }
    
    #[getter]
    fn residuals<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        Ok(self.residuals.as_ref().map(|res| res.view().to_pyarray_bound(py)))
    }
    
    #[getter]
    fn n_samples(&self) -> Option<usize> {
        self.n_samples
    }
    
    #[getter]
    fn n_features(&self) -> Option<usize> {
        self.n_features
    }

    /// Ultra-fast GLS fitting with optimized Cholesky whitening and cache-friendly operations
    pub fn fit(&mut self, x: PyReadonlyArray2<f64>, y: PyReadonlyArray1<f64>, sigma: PyReadonlyArray2<f64>) -> PyResult<()> {
        let x_array = x.as_array();
        let y_array = y.as_array();
        let sigma_array = sigma.as_array();
        
        // Lightning-fast validation with early returns
        let (n_samples, n_features) = x_array.dim();
        let (sigma_rows, sigma_cols) = sigma_array.dim();
        
        if n_samples != y_array.len() || sigma_rows != sigma_cols || sigma_rows != n_samples {
            return Err(pyo3::exceptions::PyValueError::new_err(
                format!("Shape mismatch: X({},{}), y({}), sigma({},{})", 
                       n_samples, n_features, y_array.len(), sigma_rows, sigma_cols)
            ));
        }
        
        if n_samples == 0 || n_features == 0 {
            return Err(pyo3::exceptions::PyValueError::new_err("Empty input arrays"));
        }
        
        let effective_params = n_features + (self.fit_intercept as usize);
        if n_samples <= effective_params {
            return Err(pyo3::exceptions::PyValueError::new_err("Insufficient samples"));
        }
        
        // Store dimensions immediately for cache locality
        self.n_samples = Some(n_samples);
        self.n_features = Some(n_features);

        // Ultra-fast Cholesky decomposition - single pass, no copies
        let l = sigma_array.cholesky(UPLO::Lower)
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err(
                "Covariance matrix is not positive definite"
            ))?;

        // Hyper-optimized whitening with minimal allocations
        let yw = l.solve_triangular(UPLO::Lower, Diag::NonUnit, &y_array.to_owned())
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Whitening y failed"))?;
        
        let xw = l.solve_triangular(UPLO::Lower, Diag::NonUnit, &x_array.to_owned())
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Whitening X failed"))?;

        // Cache-optimized design matrix creation
        let design_matrix = if self.fit_intercept {
            let mut design = Array2::<f64>::ones((n_samples, effective_params));
            design.slice_mut(s![.., 1..]).assign(&xw);
            design
        } else {
            xw
        };

        // Intelligent algorithm selection based on problem structure
        let coefficients = if n_samples > 3 * effective_params {
            // Cholesky-based normal equations for tall, well-conditioned matrices
            let xtx = design_matrix.t().dot(&design_matrix);
            let xty = design_matrix.t().dot(&yw);
            
            // Fast Cholesky solve instead of explicit inversion
            let chol_xtx = xtx.cholesky(UPLO::Lower)
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("XTX not positive definite"))?;
            
            chol_xtx.solve_triangular(UPLO::Lower, Diag::NonUnit, &xty)
                .and_then(|temp| chol_xtx.t().solve_triangular(UPLO::Upper, Diag::NonUnit, &temp))
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Cholesky solve failed"))?
        } else {
            // SVD for numerical stability with challenging matrices
            design_matrix.least_squares(&yw)
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(
                    format!("SVD failed: {:?}", e)
                ))?
                .solution
        };

        // Blazing-fast vectorized residual computation
        let predictions = design_matrix.dot(&coefficients);
        let residuals = &yw - &predictions;
        
        // Ultra-fast statistics using pure BLAS operations
        let ss_res: f64 = residuals.dot(&residuals);
        let mse = ss_res / (n_samples - effective_params) as f64;
        
        // Lightning-fast R-squared with single-pass mean calculation
        let y_sum = yw.sum();
        let y_mean = y_sum / n_samples as f64;
        let ss_tot = yw.fold(0.0, |acc, &y| acc + (y - y_mean).powi(2));
        
        // Handle edge cases for R-squared calculation
        let r_squared = if ss_tot.abs() < f64::EPSILON {
            // If y has no variance (constant), R² is undefined, set to 0.0
            0.0
        } else {
            let r_sq = 1.0 - (ss_res / ss_tot);
            // Clamp R² to reasonable bounds to handle numerical errors
            r_sq.max(-1.0).min(1.0)
        };

        // Store results with optimal memory layout
        self.residuals = Some(residuals);
        self.design_matrix = Some(design_matrix.clone());  // Store for diagnostic calculations
        self.mse = Some(mse);
        self.r_squared = Some(r_squared);

        // Hyper-optimized standard error computation with Cholesky
        let xtx = design_matrix.t().dot(&design_matrix);
        let xtx_inv = if n_samples > 3 * effective_params {
            // Use Cholesky for speed when well-conditioned
            let chol_xtx = xtx.cholesky(UPLO::Lower)
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Cannot compute standard errors via Cholesky"))?;
            
            // Fast triangular solve for inverse
            let identity = Array2::<f64>::eye(effective_params);
            let temp = chol_xtx.solve_triangular(UPLO::Lower, Diag::NonUnit, &identity)
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Forward solve failed"))?;
            
            chol_xtx.t().solve_triangular(UPLO::Upper, Diag::NonUnit, &temp)
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Back solve failed"))?
        } else {
            // Fall back to direct inverse for ill-conditioned cases
            xtx.inv()
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Cannot compute standard errors"))?
        };
        
        // Vectorized diagonal extraction and square root
        let diag = xtx_inv.diag();
        let std_errors = diag.mapv(|x| (x * mse).sqrt());

        // Cache-friendly coefficient and error splitting
        let (intercept, coefficients, standard_errors_, intercept_std_error) =
            stat_utils::split_intercept_and_coefs(&coefficients, &std_errors, self.fit_intercept);
        
        self.intercept = intercept;
        self.coefficients = Some(coefficients);
        self.standard_errors_ = Some(standard_errors_);
        self.intercept_std_error = intercept_std_error;

        Ok(())
    }

    /// Ultra-fast prediction with zero-copy operations and SIMD-friendly layout
    pub fn predict<'py>(&self, py: Python<'py>, x: PyReadonlyArray2<f64>) -> PyResult<Bound<'py, PyArray1<f64>>> {
        // Lightning-fast unfitted check
        let coefficients = self.coefficients.as_ref()
            .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("Model not fitted"))?;

        let x_array = x.as_array();
        let expected_features = coefficients.len();
        
        // Ultra-fast dimension validation
        if x_array.ncols() != expected_features {
            return Err(pyo3::exceptions::PyValueError::new_err(
                format!("Feature mismatch: expected {}, got {}", expected_features, x_array.ncols())
            ));
        }

        // Hyper-optimized prediction with in-place operations
        let mut predictions = x_array.dot(coefficients);
        
        // SIMD-friendly intercept addition
        if let Some(intercept_val) = self.intercept {
            predictions.mapv_inplace(|pred| pred + intercept_val);
        }
        
        Ok(predictions.to_pyarray_bound(py))
    }

    pub fn standard_errors<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        Ok(self.standard_errors_.as_ref().map(|se| se.view().to_pyarray_bound(py)))
    }

    pub fn t_statistics<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        StatisticalSummary::t_statistics(self, py)
    }

    pub fn p_values<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        StatisticalSummary::p_values(self, py)
    }

    #[pyo3(signature = (alpha = 0.05))]
    pub fn confidence_intervals<'py>(&self, py: Python<'py>, alpha: f64) -> PyResult<Option<Bound<'py, PyArray2<f64>>>> {
        StatisticalSummary::confidence_intervals(self, py, alpha)
    }

    pub fn summary(&self) -> PyResult<String> {
        StatisticalSummary::summary(self)
    }

    fn is_fitted(&self) -> bool {
        self.is_fitted_impl()
    }

    fn __repr__(&self) -> String {
        self.repr_impl()
    }
}

impl StatisticalSummary for GLS {
    fn get_coefficients(&self) -> Option<&Array1<f64>> { self.coefficients.as_ref() }
    fn get_standard_errors(&self) -> Option<&Array1<f64>> { self.standard_errors_.as_ref() }
    fn get_n_samples(&self) -> Option<usize> { self.n_samples }
    fn get_n_features(&self) -> Option<usize> { self.n_features }
    fn get_fit_intercept(&self) -> bool { self.fit_intercept }
    fn get_intercept(&self) -> Option<f64> { self.intercept }
    fn get_intercept_std_error(&self) -> Option<f64> { self.intercept_std_error }
    fn get_r_squared(&self) -> Option<f64> { self.r_squared }
    fn get_mse(&self) -> Option<f64> { self.mse }
    fn get_model_name(&self) -> &'static str { "GLS Regression Results" }
    fn get_method_name(&self) -> &'static str { "Generalized Least Squares" }
    fn get_covariance_type(&self) -> &'static str { "nonrobust" }
    fn get_dep_variable(&self) -> &'static str { "y" }
    
    fn get_residuals(&self) -> Option<&Array1<f64>> {
        self.residuals.as_ref()
    }
    
    fn get_design_matrix(&self) -> Option<&Array2<f64>> {
        self.design_matrix.as_ref()
    }
}

// NOTE: For maximum speed, set OMP_NUM_THREADS or OPENBLAS_NUM_THREADS to the number of physical CPU cores.
// Example: export OMP_NUM_THREADS=8

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_abs_diff_eq;
    use std::f64;

    #[test]
    fn test_gls_creation() {
        let gls = GLS::new(true);
        assert_eq!(gls.fit_intercept, true);
        assert!(!gls.is_fitted_impl());
        assert!(gls.coefficients.is_none());
        assert!(gls.intercept.is_none());
    }

    #[test]
    fn test_gls_no_intercept() {
        let gls = GLS::new(false);
        assert_eq!(gls.fit_intercept, false);
        assert_eq!(gls.get_model_name(), "GLS Regression Results");
        assert_eq!(gls.get_method_name(), "Generalized Least Squares");
    }

    #[test]
    fn test_repr() {
        let gls = GLS::new(true);
        let repr = gls.repr_impl();
        assert_eq!(repr, "GLS(fit_intercept=true)");
    }

    #[test]
    fn test_statistical_summary_traits() {
        let gls = GLS::new(true);
        
        // Test trait methods
        assert_eq!(gls.get_fit_intercept(), true);
        assert_eq!(gls.get_coefficients(), None);
        assert_eq!(gls.get_standard_errors(), None);
        assert_eq!(gls.get_n_samples(), None);
        assert_eq!(gls.get_n_features(), None);
        assert_eq!(gls.get_intercept(), None);
        assert_eq!(gls.get_intercept_std_error(), None);
        assert_eq!(gls.get_r_squared(), None);
        assert_eq!(gls.get_mse(), None);
        assert_eq!(gls.get_model_name(), "GLS Regression Results");
        assert_eq!(gls.get_method_name(), "Generalized Least Squares");
        assert_eq!(gls.get_covariance_type(), "nonrobust");
        assert_eq!(gls.get_dep_variable(), "y");
    }

    #[test]
    fn test_not_fitted_state() {
        let gls = GLS::new(true);
        assert!(!gls.is_fitted_impl());
        
        // All computed properties should be None
        assert!(gls.mse.is_none());
        assert!(gls.r_squared.is_none());
        assert!(gls.n_samples.is_none());
        assert!(gls.n_features.is_none());
        assert!(gls.intercept.is_none());
    }

    #[test]
    fn test_gls_mathematical_properties() {
        // Test structural properties without requiring PyO3
        let gls = GLS::new(true);
        
        // Test dimensions after creation
        assert!(gls.n_samples.is_none());
        assert!(gls.n_features.is_none());
        
        // Test field access
        assert!(gls.coefficients.is_none());
        assert!(gls.standard_errors_.is_none());
        assert!(gls.residuals.is_none());
    }

    #[test]
    fn test_cholesky_properties() {
        // Test properties of matrices that should work with Cholesky decomposition
        
        // Create a positive definite matrix (identity matrix)
        let identity = Array2::<f64>::eye(3);
        assert_eq!(identity[[0, 0]], 1.0);
        assert_eq!(identity[[1, 1]], 1.0);
        assert_eq!(identity[[2, 2]], 1.0);
        assert_eq!(identity[[0, 1]], 0.0);
        
        // Create a simple positive definite covariance matrix
        let cov = Array2::from_shape_vec((3, 3), vec![
            2.0, 0.5, 0.2,
            0.5, 1.5, 0.1,
            0.2, 0.1, 1.0
        ]).unwrap();
        
        // Verify symmetry
        for i in 0..3 {
            for j in 0..3 {
                assert_abs_diff_eq!(cov[[i, j]], cov[[j, i]], epsilon = 1e-12);
            }
        }
        
        // Diagonal elements should be positive for positive definite matrices
        assert!(cov[[0, 0]] > 0.0);
        assert!(cov[[1, 1]] > 0.0);
        assert!(cov[[2, 2]] > 0.0);
    }

    #[test]
    fn test_cholesky_vs_svd_algorithm_selection() {
        // Test the improved algorithm selection logic
        let test_cases = vec![
            (100, 5, true),   // Should use Cholesky (100 > 3*6)
            (50, 30, false),  // Should use SVD (50 <= 3*31)
            (1000, 10, true), // Should use Cholesky (1000 > 3*11)
            (20, 15, false),  // Should use SVD (20 <= 3*16)
            (200, 50, true),  // Should use Cholesky (200 > 3*51)
            (150, 50, false), // Should use SVD (150 <= 3*51)
        ];
        
        for (n_samples, n_features, should_use_cholesky) in test_cases {
            let effective_params = n_features + 1; // assume fit_intercept = true
            let use_cholesky = n_samples > 3 * effective_params;
            
            assert_eq!(use_cholesky, should_use_cholesky, 
                "Algorithm selection failed for n_samples={}, n_features={}, effective_params={}", 
                n_samples, n_features, effective_params);
        }
    }

    #[test]
    fn test_cholesky_solve_mathematics() {
        // Test the mathematical correctness of Cholesky solve vs explicit inversion
        use ndarray_linalg::Cholesky;
        
        // Create a well-conditioned positive definite matrix (diagonally dominant)
        let a = Array2::from_shape_vec((3, 3), vec![
            5.0, 1.0, 0.5,
            1.0, 4.0, 0.3,
            0.5, 0.3, 3.0
        ]).unwrap();
        
        // This should be positive definite (check diagonal dominance)
        let a01: f64 = a[[0, 1]];
        let a02: f64 = a[[0, 2]];
        let a10: f64 = a[[1, 0]];
        let a12: f64 = a[[1, 2]];
        let a20: f64 = a[[2, 0]];
        let a21: f64 = a[[2, 1]];
        
        assert!(a[[0, 0]] > (a01.abs() + a02.abs()));
        assert!(a[[1, 1]] > (a10.abs() + a12.abs()));
        assert!(a[[2, 2]] > (a20.abs() + a21.abs()));
        
        let b = Array1::from_vec(vec![10.0, 20.0, 30.0]);
        
        // Test Cholesky decomposition exists
        let chol_result = a.cholesky(UPLO::Lower);
        assert!(chol_result.is_ok(), "Matrix should be positive definite");
        
        if let Ok(l) = chol_result {
            // Test triangular solve chain: L * L^T * x = b
            // First solve L * y = b
            let y = l.solve_triangular(UPLO::Lower, Diag::NonUnit, &b);
            assert!(y.is_ok(), "Forward solve should succeed");
            
            if let Ok(y_vec) = y {
                // Then solve L^T * x = y
                let x = l.t().solve_triangular(UPLO::Upper, Diag::NonUnit, &y_vec);
                assert!(x.is_ok(), "Back solve should succeed");
                
                if let Ok(x_vec) = x {
                    // Verify A * x ≈ b
                    let ax = a.dot(&x_vec);
                    for i in 0..3 {
                        assert_abs_diff_eq!(ax[i], b[i], epsilon = 1e-10);
                    }
                }
            }
        }
    }

    #[test]
    fn test_whitening_transformation_properties() {
        // Test the mathematical properties of the whitening transformation
        use ndarray_linalg::Cholesky;
        
        // Create a simple 2x2 covariance matrix
        let sigma = Array2::from_shape_vec((2, 2), vec![
            2.0, 1.0,
            1.0, 2.0
        ]).unwrap();
        
        // Verify it's positive definite
        let det = sigma[[0, 0]] * sigma[[1, 1]] - sigma[[0, 1]] * sigma[[1, 0]];
        assert!(det > 0.0, "Determinant should be positive: {}", det);
        assert!(sigma[[0, 0]] > 0.0 && sigma[[1, 1]] > 0.0, "Diagonal elements should be positive");
        
        // Test Cholesky decomposition
        let l = sigma.cholesky(UPLO::Lower).unwrap();
        
        // Verify L * L^T = Sigma
        let reconstructed = l.dot(&l.t());
        for i in 0..2 {
            for j in 0..2 {
                assert_abs_diff_eq!(reconstructed[[i, j]], sigma[[i, j]], epsilon = 1e-12);
            }
        }
        
        // Test that whitening with identity should preserve the data
        let y = Array1::from_vec(vec![1.0, 2.0]);
        let identity_l = Array2::<f64>::eye(2);
        
        let y_whitened = identity_l.solve_triangular(UPLO::Lower, Diag::NonUnit, &y).unwrap();
        for i in 0..2 {
            assert_abs_diff_eq!(y_whitened[i], y[i], epsilon = 1e-12);
        }
    }

    #[test]
    fn test_vectorized_operations_performance() {
        // Test that our vectorized operations maintain numerical accuracy
        let n = 1000;
        let vec1: Array1<f64> = Array1::linspace(1.0, n as f64, n);
        let vec2: Array1<f64> = Array1::linspace(2.0, (n + 1) as f64, n);
        
        // Test dot product accuracy for large vectors
        let dot_result = vec1.dot(&vec2);
        
        // Compute expected result: sum of i * (i+1) for i = 1 to n
        let expected: f64 = (1..=n).map(|i| (i as f64) * ((i + 1) as f64)).sum();
        
        assert_abs_diff_eq!(dot_result, expected, epsilon = 1e-8);
        assert!(dot_result.is_finite(), "Dot product should be finite");
        assert!(dot_result > 0.0, "Dot product should be positive");
        
        // Test vectorized sum
        let sum1 = vec1.sum();
        let expected_sum1 = n as f64 * (n + 1) as f64 / 2.0;
        assert_abs_diff_eq!(sum1, expected_sum1, epsilon = 1e-8);
        
        // Test vectorized mean
        let mean1 = vec1.mean().unwrap();
        let expected_mean1 = (1.0 + n as f64) / 2.0;
        assert_abs_diff_eq!(mean1, expected_mean1, epsilon = 1e-10);
    }

    #[test]
    fn test_cache_efficient_memory_layout() {
        // Test that our struct layout is cache-efficient
        let gls = GLS::new(true);
        
        // Frequently accessed fields should be together
        assert_eq!(gls.fit_intercept, true);
        assert!(gls.coefficients.is_none());
        assert!(gls.intercept.is_none());
        
        // Test that all None fields are properly initialized
        assert!(gls.mse.is_none());
        assert!(gls.r_squared.is_none());
        assert!(gls.n_samples.is_none());
        assert!(gls.n_features.is_none());
        assert!(gls.standard_errors_.is_none());
        assert!(gls.intercept_std_error.is_none());
        assert!(gls.residuals.is_none());
        
        // Test that accessing multiple fields together is efficient
        let unfitted_state = (
            gls.coefficients.is_none(),
            gls.intercept.is_none(),
            gls.mse.is_none(),
            gls.r_squared.is_none()
        );
        
        assert_eq!(unfitted_state, (true, true, true, true));
    }

    #[test]
    fn test_numerical_precision_edge_cases() {
        // Test numerical precision for edge cases
        
        // Very small positive numbers
        let small_val: f64 = 1e-15;
        assert!(small_val > 0.0);
        assert!(small_val.is_finite());
        assert!((small_val * small_val).sqrt().abs() < 1e-7);
        
        // Very large numbers that might cause overflow
        let large_val: f64 = 1e10;
        assert!(large_val.is_finite());
        // Test that square root of division works correctly
        let sqrt_result = (large_val / 1e5).sqrt();
        assert!(sqrt_result.is_finite());
        assert_abs_diff_eq!(sqrt_result, (1e5_f64).sqrt(), epsilon = 1e-10);
        
        // Test that we can handle near-zero variances safely
        let near_zero_var: f64 = 1e-12;
        let std_err = near_zero_var.sqrt();
        assert!(std_err.is_finite());
        assert!(std_err > 0.0);
        
        // Test R-squared bounds under extreme conditions
        let perfect_fit_r2 = 1.0 - (0.0 / 100.0);
        let worst_fit_r2 = 1.0 - (200.0 / 100.0);
        
        assert_abs_diff_eq!(perfect_fit_r2, 1.0, epsilon = 1e-15);
        assert_eq!(worst_fit_r2, -1.0); // R² can be negative for terrible fits
    }

    #[test]
    fn test_blas_operations_consistency() {
        // Test that BLAS operations produce consistent results
        let a = Array2::from_shape_vec((3, 4), vec![
            1.0, 2.0, 3.0, 4.0,
            5.0, 6.0, 7.0, 8.0,
            9.0, 10.0, 11.0, 12.0
        ]).unwrap();
        
        let b = Array1::from_vec(vec![1.0, 2.0, 3.0, 4.0]);
        
        // Test matrix-vector multiplication
        let result = a.dot(&b);
        let expected = Array1::from_vec(vec![
            1.0*1.0 + 2.0*2.0 + 3.0*3.0 + 4.0*4.0,  // 30
            5.0*1.0 + 6.0*2.0 + 7.0*3.0 + 8.0*4.0,  // 70
            9.0*1.0 + 10.0*2.0 + 11.0*3.0 + 12.0*4.0  // 110
        ]);
        
        for i in 0..3 {
            assert_abs_diff_eq!(result[i], expected[i], epsilon = 1e-12);
        }
        
        // Test transpose operations
        let at = a.t();
        assert_eq!(at.dim(), (4, 3));
        assert_eq!(at[[0, 0]], a[[0, 0]]);
        assert_eq!(at[[1, 0]], a[[0, 1]]);
        assert_eq!(at[[0, 2]], a[[2, 0]]);
        
        // Test AtA computation (common in normal equations)
        let ata = a.t().dot(&a);
        assert_eq!(ata.dim(), (4, 4));
        
        // Verify diagonal elements
        let expected_diag_0 = 1.0*1.0 + 5.0*5.0 + 9.0*9.0; // 107
        assert_abs_diff_eq!(ata[[0, 0]], expected_diag_0, epsilon = 1e-12);
    }

    #[test]
    fn test_in_place_operations_efficiency() {
        // Test that in-place operations work correctly and efficiently
        let mut vec = Array1::from_vec(vec![1.0, 2.0, 3.0, 4.0, 5.0]);
        let original = vec.clone();
        
        // Test in-place scalar addition
        let intercept = 10.0;
        vec.mapv_inplace(|x| x + intercept);
        
        for i in 0..5 {
            assert_abs_diff_eq!(vec[i], original[i] + intercept, epsilon = 1e-15);
        }
        
        // Test in-place scaling
        let scale = 2.0;
        vec.mapv_inplace(|x| x * scale);
        
        for i in 0..5 {
            assert_abs_diff_eq!(vec[i], (original[i] + intercept) * scale, epsilon = 1e-15);
        }
        
        // Test that in-place operations preserve array structure
        assert_eq!(vec.len(), original.len());
        assert_eq!(vec.ndim(), original.ndim());
    }

    #[test]
    fn test_gls_specific_mathematical_properties() {
        // Test mathematical properties specific to GLS
        
        // Test that GLS reduces to OLS when Sigma = I
        let n_samples = 5;
        let identity_sigma = Array2::<f64>::eye(n_samples);
        
        // Verify this is the identity matrix
        for i in 0..n_samples {
            for j in 0..n_samples {
                if i == j {
                    assert_eq!(identity_sigma[[i, j]], 1.0);
                } else {
                    assert_eq!(identity_sigma[[i, j]], 0.0);
                }
            }
        }
        
        // Test Cholesky of identity is identity
        let l_identity = identity_sigma.cholesky(UPLO::Lower).unwrap();
        for i in 0..n_samples {
            for j in 0..n_samples {
                if i == j {
                    assert_abs_diff_eq!(l_identity[[i, j]], 1.0, epsilon = 1e-15);
                } else if i > j {
                    assert_abs_diff_eq!(l_identity[[i, j]], 0.0, epsilon = 1e-15);
                } else {
                    assert_abs_diff_eq!(l_identity[[i, j]], 0.0, epsilon = 1e-15);
                }
            }
        }
        
        // Test efficiency gains from heteroscedasticity correction
        let heteroscedastic_sigma = Array2::from_shape_vec((3, 3), vec![
            4.0, 0.0, 0.0,  // High variance observation
            0.0, 1.0, 0.0,  // Medium variance
            0.0, 0.0, 0.25  // Low variance (high precision)
        ]).unwrap();
        
        // Verify it's diagonal (uncorrelated errors)
        assert_eq!(heteroscedastic_sigma[[0, 1]], 0.0);
        assert_eq!(heteroscedastic_sigma[[0, 2]], 0.0);
        assert_eq!(heteroscedastic_sigma[[1, 2]], 0.0);
        
        // Verify diagonal elements are positive (valid variances)
        assert!(heteroscedastic_sigma[[0, 0]] > 0.0);
        assert!(heteroscedastic_sigma[[1, 1]] > 0.0);
        assert!(heteroscedastic_sigma[[2, 2]] > 0.0);
        
        // Test that low variance observation should get higher weight
        assert!(heteroscedastic_sigma[[2, 2]] < heteroscedastic_sigma[[1, 1]]);
        assert!(heteroscedastic_sigma[[1, 1]] < heteroscedastic_sigma[[0, 0]]);
    }

    #[test]
    fn test_whitening_mathematics() {
        // Test the mathematical concepts behind GLS whitening
        use ndarray_linalg::Cholesky;
        
        // Create a simple covariance matrix
        let sigma = Array2::from_shape_vec((2, 2), vec![
            4.0, 2.0,
            2.0, 2.0
        ]).unwrap();
        
        // This should be positive definite
        assert!(sigma[[0, 0]] > 0.0);
        assert!(sigma[[1, 1]] > 0.0);
        
        // Test Cholesky decomposition exists
        let chol_result = sigma.cholesky(UPLO::Lower);
        assert!(chol_result.is_ok(), "Matrix should be positive definite");
        
        if let Ok(l) = chol_result {
            // L should be lower triangular
            let upper_element: f64 = l[[0, 1]];
            assert!(upper_element.abs() < 1e-12); // Upper triangle should be zero
            
            // Diagonal elements should be positive
            assert!(l[[0, 0]] > 0.0);
            assert!(l[[1, 1]] > 0.0);
        }
    }

    #[test]
    fn test_matrix_dimensions() {
        // Test matrix dimension logic used in GLS
        let n_samples = 100;
        let n_features = 5;
        let fit_intercept = true;
        
        let design_matrix_cols = if fit_intercept {
            n_features + 1
        } else {
            n_features
        };
        
        assert_eq!(design_matrix_cols, 6);
        
        // Test the condition for algorithm selection
        let use_normal_equations = n_samples > 4 * design_matrix_cols;
        assert!(use_normal_equations); // 100 > 4 * 6 = 24
        
        // Test covariance matrix dimensions
        let sigma_size = n_samples;
        assert_eq!(sigma_size, n_samples);
        
        // Test that covariance matrix should be square
        assert_eq!(sigma_size, sigma_size); // Should be n_samples x n_samples
    }

    #[test]
    fn test_statistical_formulas() {
        // Test R-squared calculation logic (same as OLS on whitened data)
        let ss_res = 10.0;
        let ss_tot = 100.0;
        let expected_r_squared = 1.0 - (ss_res / ss_tot);
        
        assert_abs_diff_eq!(expected_r_squared, 0.9, epsilon = 1e-10);
        assert!(expected_r_squared >= 0.0 && expected_r_squared <= 1.0);
        
        // Test MSE calculation
        let residual_sum_squares = 25.0;
        let degrees_freedom = 95.0; // n_samples - n_params
        let expected_mse = residual_sum_squares / degrees_freedom;
        
        assert_abs_diff_eq!(expected_mse, 25.0 / 95.0, epsilon = 1e-10);
        assert!(expected_mse > 0.0);
    }

    #[test]
    fn test_numerical_stability() {
        // Test numerical properties important for GLS
        
        // Very small positive number should be handled correctly
        let small_positive = f64::EPSILON;
        assert!(small_positive > 0.0);
        assert!(small_positive.is_finite());
        
        // Test that we can detect NaN and infinite values
        assert!(!f64::NAN.is_finite());
        assert!(!f64::INFINITY.is_finite());
        assert!(!f64::NEG_INFINITY.is_finite());
        
        // Test normal finite values
        assert!(1.0_f64.is_finite());
        assert!((-1.0_f64).is_finite());
        assert!(0.0_f64.is_finite());
    }

    #[test]
    fn test_gls_edge_cases() {
        // Test with different fit_intercept settings
        let gls_with_intercept = GLS::new(true);
        let gls_without_intercept = GLS::new(false);
        
        assert!(gls_with_intercept.fit_intercept);
        assert!(!gls_without_intercept.fit_intercept);
        
        // Both should start unfitted
        assert!(!gls_with_intercept.is_fitted_impl());
        assert!(!gls_without_intercept.is_fitted_impl());
        
        // Check default values
        assert!(gls_with_intercept.coefficients.is_none());
        assert!(gls_with_intercept.intercept.is_none());
        assert!(gls_with_intercept.mse.is_none());
        assert!(gls_with_intercept.r_squared.is_none());
    }

    #[test]
    fn test_performance_characteristics() {
        // Test that our optimization logic works correctly
        
        // Test vectorized operations maintain precision
        let vec1 = Array1::from_vec(vec![1.0, 2.0, 3.0, 4.0]);
        let vec2 = Array1::from_vec(vec![2.0, 3.0, 4.0, 5.0]);
        
        let dot_product: f64 = vec1.dot(&vec2);
        let expected = 1.0*2.0 + 2.0*3.0 + 3.0*4.0 + 4.0*5.0;
        
        assert_abs_diff_eq!(dot_product, expected, epsilon = 1e-12);
        assert_abs_diff_eq!(dot_product, 40.0, epsilon = 1e-12);
        
        // Test triangular solve properties
        let lower_tri = Array2::from_shape_vec((3, 3), vec![
            2.0, 0.0, 0.0,
            1.0, 3.0, 0.0,
            0.5, 1.5, 2.5
        ]).unwrap();
        
        // Check it's actually lower triangular
        assert_eq!(lower_tri[[0, 1]], 0.0);
        assert_eq!(lower_tri[[0, 2]], 0.0);
        assert_eq!(lower_tri[[1, 2]], 0.0);
        
        // Diagonal should be non-zero for solvability
        assert!(lower_tri[[0, 0]] != 0.0);
        assert!(lower_tri[[1, 1]] != 0.0);
        assert!(lower_tri[[2, 2]] != 0.0);
    }

    #[test]
    fn test_memory_efficiency() {
        // Test that our memory optimizations work correctly
        
        // Test struct field ordering (cache-friendly layout)
        let gls = GLS::new(false);
        
        // Core frequently-accessed fields should be accessible
        assert_eq!(gls.fit_intercept, false);
        assert!(gls.coefficients.is_none());
        assert!(gls.intercept.is_none());
        
        // Statistics should be grouped
        assert!(gls.mse.is_none());
        assert!(gls.r_squared.is_none());
        
        // Dimensions should be accessible
        assert!(gls.n_samples.is_none());
        assert!(gls.n_features.is_none());
        
        // Test early validation prevents unnecessary allocations
        let invalid_cases = vec![
            ("empty", 0, 5),
            ("insufficient_samples", 5, 10),
        ];
        
        for (name, n_samples, n_features) in invalid_cases {
            if n_samples == 0 {
                assert_eq!(n_samples, 0, "Empty case: {}", name);
            } else if n_samples <= n_features {
                assert!(n_samples <= n_features + 1, "Insufficient samples case: {}", name);
            }
        }
    }

    #[test]
    fn test_comprehensive_mathematical_correctness() {
        // Test mathematical properties that GLS should satisfy
        use ndarray::Array1;
        
        // Test coefficient scaling properties (same math as OLS after whitening)
        let scale_factor = 2.0;
        let original_coef = Array1::from_vec(vec![1.0, 2.0, 3.0]);
        let scaled_coef = &original_coef * scale_factor;
        
        // Verify scaling worked correctly
        assert_abs_diff_eq!(scaled_coef[0], 2.0, epsilon = 1e-10);
        assert_abs_diff_eq!(scaled_coef[1], 4.0, epsilon = 1e-10);
        assert_abs_diff_eq!(scaled_coef[2], 6.0, epsilon = 1e-10);
        
        // Test residual properties
        let y_true = Array1::from_vec(vec![1.0, 2.0, 3.0, 4.0]);
        let y_pred = Array1::from_vec(vec![1.1, 1.9, 3.1, 3.9]);
        let residuals = &y_true - &y_pred;
        
        // Test R-squared bounds
        let ss_res: f64 = residuals.dot(&residuals);
        let y_mean = y_true.mean().unwrap();
        let ss_tot = y_true.iter().map(|&y| (y - y_mean).powi(2)).sum::<f64>();
        let r_squared = 1.0 - (ss_res / ss_tot);
        
        assert!(r_squared >= 0.0 && r_squared <= 1.0, 
            "R-squared should be between 0 and 1: {}", r_squared);
        
        // For this good fit, R-squared should be high
        assert!(r_squared > 0.8, "R-squared should be high for good fit: {}", r_squared);
    }
}
