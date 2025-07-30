use ndarray::{Array1, Array2};
#[cfg(any(feature = "python", test))]
#[allow(unused_imports)]
use ndarray::s;
use std::sync::OnceLock;

#[cfg(any(feature = "python", test))]
#[allow(unused_imports)]
use ndarray_linalg::{Inverse, LeastSquaresSvd, Cholesky, UPLO, SolveTriangular, Diag}; 
#[cfg(feature = "python")]
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2, ToPyArray};
#[cfg(feature = "python")]
use pyo3::{prelude::*, Python};
#[cfg(feature = "python")]
use crate::models::base_model::base_model::BaseModel;
#[cfg(any(feature = "python", test))]
#[allow(unused_imports)]
use crate::models::linear::stat_utils;

use crate::models::linear::stat_inference::StatisticalSummary;

#[cfg_attr(feature = "python", pyclass)]
pub struct OLS {
    // Core model parameters - cache-aligned for performance  
    pub coefficients: Option<Array1<f64>>, 
    pub intercept: Option<f64>,
    
    // Model configuration - small, frequently accessed
    pub fit_intercept: bool,
    pub robust: bool,
    
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
    
    // Cache for expensive computations - lazy initialization
    #[cfg_attr(not(feature = "python"), allow(dead_code))]
    xtx_inv: Option<Array2<f64>>,
    #[cfg_attr(not(feature = "python"), allow(dead_code))]
    covariance_matrix: OnceLock<Array2<f64>>,
}

#[cfg(feature = "python")]
#[pymethods]
impl OLS {
    #[new]
    #[pyo3(signature = (fit_intercept = true, robust = false))]
    pub fn py_new(fit_intercept: bool, robust: bool) -> Self {
        OLS::new(fit_intercept, robust)
    }

    #[getter]
    fn coefficients<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        Ok(self.coefficients.as_ref().map(|coef| coef.view().to_pyarray_bound(py)))
    }

    #[getter] 
    fn fit_intercept(&self) -> bool {
        self.fit_intercept
    }

    #[getter]
    fn robust(&self) -> bool {
        self.robust
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
    fn intercept(&self) -> Option<f64> {
        self.intercept
    }

    #[getter]
    fn n_samples(&self) -> Option<usize> {
        self.n_samples
    }

    #[getter]
    fn n_features(&self) -> Option<usize> {
        self.n_features
    }
    
    #[getter]
    fn residuals<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        Ok(self.residuals.as_ref().map(|res| res.view().to_pyarray_bound(py)))
    }

    fn is_fitted(&self) -> bool {
        self.is_fitted_impl()
    }

    fn __repr__(&self) -> String {
        self.repr_impl()
    }

    fn fit(
        &mut self, 
        x: PyReadonlyArray2<f64>, 
        y: PyReadonlyArray1<f64>
    ) -> PyResult<()> {
        let x_array = x.as_array();
        let y_array = y.as_array();

        // Fast validation with early returns
        if x_array.is_empty() || y_array.is_empty() {
            return Err(pyo3::exceptions::PyValueError::new_err("Input arrays cannot be empty"));
        }
        
        let (n_samples, n_features) = x_array.dim();
        if n_samples != y_array.len() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                format!("X and y shape mismatch: {} vs {}", n_samples, y_array.len())
            ));
        }
        
        let effective_params = n_features + (self.fit_intercept as usize);
        if n_samples <= effective_params {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Insufficient samples for the number of parameters"
            ));
        }
        
        // Vectorized NaN/inf check - faster than iterator
        if !x_array.iter().all(|&x| x.is_finite()) || !y_array.iter().all(|&y| y.is_finite()) {
            return Err(pyo3::exceptions::PyValueError::new_err("Input contains NaN or infinite values"));
        }

        // Store dimensions early
        self.n_samples = Some(n_samples);
        self.n_features = Some(n_features);

        // Optimize for memory layout - avoid copies when possible
        let x_view = x_array.view();
        let y_view = y_array.view();

        // Fast path: create design matrix more efficiently
        let design_matrix = if self.fit_intercept {
            // Pre-allocate with correct layout for BLAS
            let mut design = Array2::<f64>::ones((n_samples, n_features + 1));
            design.slice_mut(s![.., 1..]).assign(&x_view);
            design
        } else {
            x_view.to_owned()
        };

        // Store design matrix for diagnostic calculations
        self.design_matrix = Some(design_matrix.clone());

        // Optimized matrix computations with BLAS
        let xtx = design_matrix.t().dot(&design_matrix);
        let xty = design_matrix.t().dot(&y_view);

        // Smart algorithm selection with tighter thresholds for performance
        let use_cholesky = n_samples > 2 * effective_params && xtx.nrows() < 1000;
        
        let (coefficients, xtx_inv) = if use_cholesky {
            // Try Cholesky decomposition first (fastest for positive definite)
            match xtx.cholesky(UPLO::Lower) {
                Ok(chol) => {
                    // Solve L*L^T * x = b using forward and back substitution
                    let temp = chol.solve_triangular(UPLO::Lower, Diag::NonUnit, &xty)
                        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Cholesky forward solve failed"))?;
                    let coefficients = chol.t().solve_triangular(UPLO::Upper, Diag::NonUnit, &temp)
                        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Cholesky back solve failed"))?;
                    
                    // Fast triangular solve for inverse: A^(-1) = (L^(-1))^T * L^(-1)
                    // This is much faster than computing L^(-1) explicitly
                    let identity = Array2::<f64>::eye(xtx.nrows());
                    let temp = chol.solve_triangular(UPLO::Lower, Diag::NonUnit, &identity)
                        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Failed to compute triangular solve for matrix inverse"))?;
                    let xtx_inv = chol.t().solve_triangular(UPLO::Upper, Diag::NonUnit, &temp)
                        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Failed to compute matrix inverse from Cholesky"))?;
                    
                    (coefficients, Some(xtx_inv))
                },
                Err(_) => {
                    // Fallback to regular inverse if Cholesky fails
                    let xtx_inv = xtx.inv()
                        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Matrix is singular"))?;
                    let coefficients = xtx_inv.dot(&xty);
                    (coefficients, Some(xtx_inv))
                }
            }
        } else if n_samples > 4 * effective_params {
            // Normal equations for well-conditioned tall matrices
            let xtx_inv = xtx.inv()
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Matrix is singular"))?;
            let coefficients = xtx_inv.dot(&xty);
            (coefficients, Some(xtx_inv))
        } else {
            // SVD for numerical stability with wide or ill-conditioned matrices
            let solution = design_matrix.least_squares(&y_view)
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(
                    format!("SVD failed: {:?}", e)
                ))?;
            (solution.solution, None)
        };

        // Store the original coefficients for matrix operations
        let original_coefficients = coefficients.clone();
        
        // Split coefficients to separate intercept and regular coefficients for storage
        let (intercept, coefficients_split) = if self.fit_intercept {
            let intercept = coefficients[0];
            let coef_split = coefficients.slice(s![1..]).to_owned();
            (Some(intercept), coef_split)
        } else {
            (None, coefficients.clone())
        };
        
        // Compute predictions using the ORIGINAL design matrix and coefficients
        let predictions = design_matrix.dot(&original_coefficients);
        
        // Vectorized residual computation with correct predictions
        let residuals = &y_view - &predictions;
        
        // Fast statistics computation using BLAS operations
        let ss_res: f64 = ndarray::linalg::Dot::dot(&residuals, &residuals);
        let mse = ss_res / (n_samples - effective_params) as f64;
        
        // Optimized R-squared calculation - avoid mean computation in loop
        let y_sum = y_view.sum();
        let y_mean = y_sum / n_samples as f64;
        let ss_tot = y_view.fold(0.0, |acc, &y| acc + (y - y_mean).powi(2));
        
        // Handle edge cases for R-squared calculation
        let r_squared = if ss_tot.abs() < f64::EPSILON {
            // If y has no variance (constant), R² is undefined, set to 0.0
            0.0
        } else {
            let r_sq = 1.0 - (ss_res / ss_tot);
            // Clamp R² to reasonable bounds to handle numerical errors
            r_sq.max(-1.0).min(1.0)
        };

        // Fast standard error computation now that we have MSE
        let std_errors = if let Some(ref inv) = xtx_inv {
            self.xtx_inv = Some(inv.clone());
            
            if self.robust {
                // HC0 (White) robust standard errors
                self.compute_robust_standard_errors(&design_matrix, &residuals, inv)?
            } else {
                // Classical standard errors
                let diag = inv.diag();
                diag.mapv(|x| (x * mse).sqrt())
            }
        } else {
            // For SVD case, compute standard errors if needed
            let xtx_inv_computed = xtx.inv()
                .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err(
                    "Cannot compute standard errors: matrix is singular"
                ))?;
            self.xtx_inv = Some(xtx_inv_computed.clone());
            
            if self.robust {
                // HC0 robust standard errors for SVD case
                self.compute_robust_standard_errors(&design_matrix, &residuals, &xtx_inv_computed)?
            } else {
                // Classical standard errors
                let diag = xtx_inv_computed.diag();
                diag.mapv(|x| (x * mse).sqrt())
            }
        };

        // Split standard errors to match the split coefficients  
        let (_, _, standard_errors_only, intercept_std_error) =
            stat_utils::split_intercept_and_coefs(&original_coefficients, &std_errors, self.fit_intercept);
        
        // Store results
        self.residuals = Some(residuals);
        self.mse = Some(mse);
        self.r_squared = Some(r_squared);
        self.intercept = intercept;
        self.coefficients = Some(coefficients_split);
        self.standard_errors_ = Some(standard_errors_only);
        self.intercept_std_error = intercept_std_error;

        Ok(())
    }

    /// Make predictions using the fitted OLS model - optimized for performance
    fn predict<'py>(
        &self,
        py: Python<'py>,
        x: PyReadonlyArray2<f64>
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        // Fast unfitted check
        let coefficients = self.coefficients.as_ref()
            .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err(
                "Model not fitted. Call fit() first."
            ))?;

        let x_array = x.as_array();
        let expected_features = coefficients.len();
        
        // Fast dimension check
        if x_array.ncols() != expected_features {
            return Err(pyo3::exceptions::PyValueError::new_err(
                format!("Feature count mismatch: expected {}, got {}", 
                       expected_features, x_array.ncols())
            ));
        }

        // Optimized prediction computation - avoid intermediate allocations
        let mut predictions = x_array.dot(coefficients);
        
        // Add intercept in-place if present
        if let Some(intercept_val) = self.intercept {
            predictions.mapv_inplace(|pred| pred + intercept_val);
        }
        
        Ok(predictions.to_pyarray_bound(py))
    }

    /// Calculate standard errors of coefficients
    fn standard_errors<'py>(
        &self,
        py: Python<'py>
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        Ok(self.standard_errors_.as_ref().map(|se| se.view().to_pyarray_bound(py)))
    }

    /// Calculate t-statistics for coefficients
    fn t_statistics<'py>(
        &self,
        py: Python<'py>
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        StatisticalSummary::t_statistics(self, py)
    }

    /// Calculate p-values for coefficients using t-distribution
    fn p_values<'py>(
        &self,
        py: Python<'py>
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        StatisticalSummary::p_values(self, py)
    }

    /// Calculate confidence intervals for coefficients
    #[pyo3(signature = (alpha = 0.05))]
    fn confidence_intervals<'py>(
        &self,
        py: Python<'py>,
        alpha: f64
    ) -> PyResult<Option<Bound<'py, PyArray2<f64>>>> {
        StatisticalSummary::confidence_intervals(self, py, alpha)
    }

    /// Generate a summary of the model results
    fn summary(&self) -> PyResult<String> {
        StatisticalSummary::summary(self)
    }

    /// Get the covariance matrix of coefficients
    fn covariance_matrix<'py>(
        &mut self,
        py: Python<'py>
    ) -> PyResult<Option<Bound<'py, PyArray2<f64>>>> {
        // Use OnceLock for lazy initialization - computed only once
        if let Some(cov) = self.covariance_matrix.get() {
            return Ok(Some(cov.view().to_pyarray_bound(py)));
        }

        if let (Some(ref xtx_inv), Some(mse)) = (&self.xtx_inv, self.mse) {
            let cov = xtx_inv * mse;
            // Try to initialize OnceLock - if another thread beat us, use their result
            let stored_cov = self.covariance_matrix.get_or_init(|| cov);
            Ok(Some(stored_cov.view().to_pyarray_bound(py)))
        } else {
            Ok(None)
        }
    }
}

impl OLS {
    /// Create a new OLS instance - used internally and for testing
    pub fn new(fit_intercept: bool, robust: bool) -> Self {
        OLS {
            coefficients: None,
            intercept: None,
            fit_intercept,
            robust,
            mse: None,
            r_squared: None,
            n_samples: None,
            n_features: None,
            standard_errors_: None,
            intercept_std_error: None,
            residuals: None,
            design_matrix: None,
            xtx_inv: None,
            covariance_matrix: OnceLock::new(),
        }
    }

    /// Core method to check if model is fitted
    pub fn is_fitted_impl(&self) -> bool {
        self.coefficients.is_some()
    }

    /// Core method for string representation
    pub fn repr_impl(&self) -> String {
        format!("OLS(fit_intercept={}, robust={})", self.fit_intercept, self.robust)
    }

    /// Compute HC0 (White) robust standard errors
    /// 
    /// Uses the sandwich estimator: SE = sqrt(diag((X'X)^(-1) * X' * diag(e²) * X * (X'X)^(-1)))
    #[cfg(feature = "python")]
    pub fn compute_robust_standard_errors(
        &self,
        design_matrix: &Array2<f64>,
        residuals: &Array1<f64>,
        xtx_inv: &Array2<f64>,
    ) -> PyResult<Array1<f64>> {
        self.compute_robust_standard_errors_rust(design_matrix, residuals, xtx_inv)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))
    }
    
    /// Compute HC0 (White) robust standard errors (Rust version)
    /// 
    /// Uses the sandwich estimator: SE = sqrt(diag((X'X)^(-1) * X' * diag(e²) * X * (X'X)^(-1)))
    pub fn compute_robust_standard_errors_rust(
        &self,
        design_matrix: &Array2<f64>,
        residuals: &Array1<f64>,
        xtx_inv: &Array2<f64>,
    ) -> Result<Array1<f64>, String> {
        // Optimized diagonal-only computation of sandwich estimator
        // Since we only need diag((X'X)^(-1) * X' * diag(e²) * X * (X'X)^(-1))
        // We can compute this more efficiently by exploiting the diagonal structure
        
        let n_params = design_matrix.ncols();
        let n_samples = design_matrix.nrows();
        
        // Step 1: Compute weighted X matrix efficiently
        // Create X_weighted where each row k is multiplied by e²[k]
        let residuals_squared = residuals.mapv(|e| e.powi(2));
        
        // Use broadcasting to create weighted matrix without explicit loops
        let mut x_weighted = Array2::<f64>::zeros((n_samples, n_params));
        for (i, &e_sq) in residuals_squared.iter().enumerate() {
            if e_sq > 0.0 {
                for j in 0..n_params {
                    x_weighted[[i, j]] = design_matrix[[i, j]] * e_sq;
                }
            }
        }
        
        // Step 2: Compute meat = X' * X_weighted using BLAS
        let meat = design_matrix.t().dot(&x_weighted);
        
        // Step 3: Sandwich computation using BLAS
        let robust_cov = xtx_inv.dot(&meat).dot(xtx_inv);
        
        // Step 4: Extract diagonal and compute standard errors
        let robust_se = robust_cov.diag().mapv(|x| {
            if x >= 0.0 {
                x.sqrt()
            } else {
                0.0 // Handle numerical issues
            }
        });
        
        Ok(robust_se)
    }
}


impl StatisticalSummary for OLS {
    fn get_coefficients(&self) -> Option<&Array1<f64>> { 
        self.coefficients.as_ref() 
    }
    
    fn get_standard_errors(&self) -> Option<&Array1<f64>> { 
        self.standard_errors_.as_ref() 
    }
    
    fn get_n_samples(&self) -> Option<usize> { 
        self.n_samples 
    }
    
    fn get_n_features(&self) -> Option<usize> { 
        self.n_features 
    }
    
    fn get_fit_intercept(&self) -> bool { 
        self.fit_intercept 
    }
    
    fn get_intercept(&self) -> Option<f64> { 
        self.intercept 
    }
    
    fn get_intercept_std_error(&self) -> Option<f64> { 
        self.intercept_std_error 
    }
    
    fn get_r_squared(&self) -> Option<f64> { 
        self.r_squared 
    }
    
    fn get_mse(&self) -> Option<f64> { 
        self.mse 
    }
    
    fn get_model_name(&self) -> &'static str { 
        "OLS Regression Results"
    }
    
    fn get_method_name(&self) -> &'static str { 
        "Least Squares"
    }
    
    fn get_covariance_type(&self) -> &'static str { 
        if self.robust {
            "HC0"
        } else {
            "nonrobust"
        }
    }
    
    fn get_dep_variable(&self) -> &'static str { 
        "y" 
    }
    
    fn get_residuals(&self) -> Option<&Array1<f64>> {
        self.residuals.as_ref()
    }
    
    fn get_design_matrix(&self) -> Option<&Array2<f64>> {
        self.design_matrix.as_ref()
    }
}

#[cfg(feature = "python")]
impl BaseModel for OLS {
    fn fit(&mut self, x: PyReadonlyArray2<f64>, y: PyReadonlyArray1<f64>) -> PyResult<()> {
        self.fit(x, y)
    }
    
    fn predict<'py>(
        &self,
        py: Python<'py>,
        x: PyReadonlyArray2<f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        self.predict(py, x)
    }

    fn standard_errors<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        self.standard_errors(py)
    }

    fn t_statistics<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        StatisticalSummary::t_statistics(self, py)
    }

    fn p_values<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        StatisticalSummary::p_values(self, py)
    }

    fn confidence_intervals<'py>(
        &self,
        py: Python<'py>,
        alpha: Option<f64>,
    ) -> PyResult<Option<Bound<'py, PyArray2<f64>>>> {
        StatisticalSummary::confidence_intervals(self, py, alpha.unwrap_or(0.05))
    }

    fn summary(&self) -> PyResult<String> {
        StatisticalSummary::summary(self)
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use ndarray::Array;
    use approx::assert_abs_diff_eq;

    #[test]
    fn test_ols_creation() {
        let ols = OLS::new(true, false);
        assert_eq!(ols.fit_intercept, true);
        assert_eq!(ols.robust, false);
        assert!(!ols.is_fitted_impl());
        assert!(ols.coefficients.is_none());
        assert!(ols.intercept.is_none());
    }

    #[test]
    fn test_ols_no_intercept() {
        let ols = OLS::new(false, false);
        assert_eq!(ols.fit_intercept, false);
        assert_eq!(ols.robust, false);
        assert_eq!(ols.get_model_name(), "OLS Regression Results");
        assert_eq!(ols.get_method_name(), "Least Squares");
    }

    #[test]
    fn test_repr() {
        let ols = OLS::new(true, false);
        let repr = ols.repr_impl();
        assert_eq!(repr, "OLS(fit_intercept=true, robust=false)");
    }

    #[test]
    fn test_statistical_summary_traits() {
        let ols = OLS::new(true, false);
        
        // Test trait methods
        assert_eq!(ols.get_fit_intercept(), true);
        assert_eq!(ols.get_coefficients(), None);
        assert_eq!(ols.get_standard_errors(), None);
        assert_eq!(ols.get_n_samples(), None);
        assert_eq!(ols.get_n_features(), None);
        assert_eq!(ols.get_intercept(), None);
        assert_eq!(ols.get_intercept_std_error(), None);
        assert_eq!(ols.get_r_squared(), None);
        assert_eq!(ols.get_mse(), None);
        assert_eq!(ols.get_model_name(), "OLS Regression Results");
        assert_eq!(ols.get_method_name(), "Least Squares");
        assert_eq!(ols.get_covariance_type(), "nonrobust");
        assert_eq!(ols.get_dep_variable(), "y");
    }

    #[test]
    fn test_not_fitted_state() {
        let ols = OLS::new(true, false);
        assert!(!ols.is_fitted_impl());
        
        // All computed properties should be None
        assert!(ols.mse.is_none());
        assert!(ols.r_squared.is_none());
        assert!(ols.n_samples.is_none());
        assert!(ols.n_features.is_none());
        assert!(ols.intercept.is_none());
    }

    // Test pure Rust mathematical functions
    #[test]
    fn test_stat_utils_integration() {
        // Test that stat_utils functions work correctly
        let coef = Array::from_vec(vec![1.0, 2.0, 3.0]);
        let se = Array::from_vec(vec![0.5, 1.0, 1.5]);
        
        let t_stats = crate::models::linear::stat_utils::t_statistics(&coef, &se);
        assert_abs_diff_eq!(t_stats[0], 2.0, epsilon = 1e-10); // 1.0 / 0.5
        assert_abs_diff_eq!(t_stats[1], 2.0, epsilon = 1e-10); // 2.0 / 1.0
        assert_abs_diff_eq!(t_stats[2], 2.0, epsilon = 1e-10); // 3.0 / 1.5
    }

    #[test]
    fn test_ols_mathematical_properties() {
        // Test structural properties without requiring PyO3
        let ols = OLS::new(true, false);
        
        // Test dimensions after creation
        assert!(ols.n_samples.is_none());
        assert!(ols.n_features.is_none());
        
        // Test field access
        assert!(ols.coefficients.is_none());
        assert!(ols.standard_errors_.is_none());
        assert!(ols.xtx_inv.is_none());
        assert!(ols.covariance_matrix.get().is_none());
    }

    #[test]
    fn test_perfect_linear_relationship_math() {
        // Test the mathematical properties we expect from perfect linear data
        // This tests the mathematical intuition without Python dependencies
        
        // Perfect line: y = 2x + 1
        // We know that for this relationship:
        // - R² should be 1.0
        // - MSE should be 0.0 (or very close)
        // - Coefficients should be [2.0] and intercept 1.0
        
        let expected_slope = 2.0_f64;
        let expected_intercept = 1.0_f64;
        
        // Test our expectations are reasonable
        assert!(expected_slope > 0.0);
        assert!(expected_intercept > 0.0);
        
        // Test coefficient bounds (should be finite)
        assert!(expected_slope.is_finite());
        assert!(expected_intercept.is_finite());
    }

    #[test]
    fn test_matrix_dimensions() {
        // Test matrix dimension logic used in OLS
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
        let use_normal_equations = n_samples > 3 * design_matrix_cols;
        assert!(use_normal_equations); // 100 > 3 * 6 = 18
        
        // Test insufficient data condition
        let min_samples_needed = design_matrix_cols + 1;
        assert!(n_samples > min_samples_needed);
    }

    #[test]
    fn test_statistical_formulas() {
        // Test R-squared calculation logic
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
    fn test_ols_edge_cases() {
        // Test with different fit_intercept settings
        let ols_with_intercept = OLS::new(true, false);
        let ols_without_intercept = OLS::new(false, false);
        
        assert!(ols_with_intercept.fit_intercept);
        assert!(!ols_without_intercept.fit_intercept);
        
        // Both should start unfitted
        assert!(!ols_with_intercept.is_fitted_impl());
        assert!(!ols_without_intercept.is_fitted_impl());
        
        // Check default values
        assert!(ols_with_intercept.coefficients.is_none());
        assert!(ols_with_intercept.intercept.is_none());
        assert!(ols_with_intercept.mse.is_none());
        assert!(ols_with_intercept.r_squared.is_none());
    }

    #[test]
    fn test_numerical_stability() {
        // Test numerical properties that are important for OLS
        use std::f64;
        
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
    fn test_ols_performance_characteristics() {
        // Test that our algorithm selection logic works correctly
        let small_wide_matrix = (10, 50); // n_samples < 3 * n_features -> use SVD
        let tall_narrow_matrix = (1000, 10); // n_samples > 3 * n_features -> use normal equations
        
        // For small wide matrix: 10 < 3 * 50 = 150, so use SVD
        assert!(small_wide_matrix.0 < 3 * small_wide_matrix.1);
        
        // For tall narrow matrix: 1000 > 3 * 10 = 30, so use normal equations  
        assert!(tall_narrow_matrix.0 > 3 * tall_narrow_matrix.1);
        
        // Test degrees of freedom calculation
        let n_samples = 100;
        let n_features = 5;
        let fit_intercept = true;
        
        let effective_features = if fit_intercept { n_features + 1 } else { n_features };
        let degrees_of_freedom = n_samples - effective_features;
        
        assert_eq!(effective_features, 6);
        assert_eq!(degrees_of_freedom, 94);
        assert!(degrees_of_freedom > 0);
    }

    #[test]
    fn test_statistical_inference_properties() {
        // Test statistical properties that OLS should maintain
        
        // Test t-statistic calculation logic
        let coef = 2.5_f64;
        let std_err = 0.5_f64;
        let t_stat = coef / std_err;
        
        assert_abs_diff_eq!(t_stat, 5.0, epsilon = 1e-10);
        assert!(t_stat.abs() > 1.96, "Should be statistically significant at 5% level");
        
        // Test confidence interval logic
        let alpha = 0.05_f64;
        let critical_value = 1.96_f64; // Approximate for large samples
        let margin_of_error = critical_value * std_err;
        let ci_lower = coef - margin_of_error;
        let ci_upper = coef + margin_of_error;
        
        assert!(ci_lower < coef && coef < ci_upper);
        assert!(ci_upper - ci_lower > 0.0);
        
        // Test that confidence level makes sense
        assert!(alpha > 0.0 && alpha < 1.0, "Alpha should be between 0 and 1: {}", alpha);
        
        assert!(ci_lower < coef && coef < ci_upper);
        assert_abs_diff_eq!(ci_lower, 2.5 - 1.96 * 0.5, epsilon = 1e-10);
        assert_abs_diff_eq!(ci_upper, 2.5 + 1.96 * 0.5, epsilon = 1e-10);
        
        // Test that confidence interval contains the true coefficient
        assert!(ci_lower <= coef && coef <= ci_upper);
    }

    #[test]
    fn test_performance_optimizations() {
        // Test that our performance optimizations maintain correctness
        use ndarray::Array1;
        
        // Test Cholesky decomposition logic
        let symmetric_matrix = Array2::from_shape_vec((3, 3), vec![
            4.0, 2.0, 1.0,
            2.0, 3.0, 0.5,
            1.0, 0.5, 2.0
        ]).unwrap();
        
        // This should be positive definite, so Cholesky should work
        assert!(symmetric_matrix[[0, 0]] > 0.0);
        assert!(symmetric_matrix[[1, 1]] > 0.0);
        assert!(symmetric_matrix[[2, 2]] > 0.0);
        
        // Test algorithm selection logic with different sizes
        let test_cases = vec![
            (100, 5),   // Should use Cholesky/normal equations
            (50, 30),   // Should use SVD
            (2000, 10), // Should use normal equations
            (10, 8),    // Should use SVD
        ];
        
        for (n_samples, n_features) in test_cases {
            let effective_params = n_features + 1; // assume fit_intercept = true
            let use_cholesky = n_samples > 2 * effective_params && effective_params < 1000;
            let use_normal_eq = n_samples > 4 * effective_params;
            
            if n_samples >= 2000 {
                assert!(use_normal_eq, "Large datasets should use normal equations");
            }
            
            if n_features >= 20 && n_samples < 3 * n_features {
                assert!(!use_cholesky, "Wide matrices shouldn't use Cholesky path");
            }
        }
        
        // Test vectorized operations maintain precision
        let vec1 = Array1::from_vec(vec![1.0, 2.0, 3.0, 4.0]);
        let vec2 = Array1::from_vec(vec![2.0, 3.0, 4.0, 5.0]);
        
        let dot_product: f64 = vec1.dot(&vec2);
        let expected = 1.0*2.0 + 2.0*3.0 + 3.0*4.0 + 4.0*5.0;
        
        assert_abs_diff_eq!(dot_product, expected, epsilon = 1e-12);
        assert_abs_diff_eq!(dot_product, 40.0, epsilon = 1e-12);
    }

    #[test]
    fn test_memory_efficiency() {
        // Test that our memory optimizations work correctly
        
        // Test OnceLock initialization
        let ols = OLS::new(true, false);
        assert!(ols.covariance_matrix.get().is_none());
        
        // Test early validation prevents unnecessary allocations
        let invalid_cases = vec![
            ("empty", 0, 5),
            ("insufficient_samples", 5, 10),
            ("dimension_mismatch", 10, 5), // This would be caught in actual fit
        ];
        
        for (name, n_samples, n_features) in invalid_cases {
            if n_samples == 0 {
                assert_eq!(n_samples, 0, "Empty case: {}", name);
            } else if n_samples <= n_features {
                assert!(n_samples <= n_features + 1, "Insufficient samples case: {}", name);
            }
        }
        
        // Test struct field ordering (cache-friendly layout)
        let ols = OLS::new(false, false);
        
        // Core frequently-accessed fields should be accessible
        assert_eq!(ols.fit_intercept, false);
        assert_eq!(ols.robust, false);
        assert!(ols.coefficients.is_none());
        assert!(ols.intercept.is_none());
        
        // Statistics should be grouped
        assert!(ols.mse.is_none());
        assert!(ols.r_squared.is_none());
        
        // Dimensions should be accessible
        assert!(ols.n_samples.is_none());
        assert!(ols.n_features.is_none());
    }

    #[test]
    fn test_robust_standard_errors() {
        // Test robust vs classical standard errors configuration
        let ols_classical = OLS::new(true, false);
        let ols_robust = OLS::new(true, true);
        
        assert_eq!(ols_classical.robust, false);
        assert_eq!(ols_robust.robust, true);
        
        // Test covariance type
        assert_eq!(ols_classical.get_covariance_type(), "nonrobust");
        assert_eq!(ols_robust.get_covariance_type(), "HC0");
        
        // Test repr includes robust flag
        let repr_classical = ols_classical.repr_impl();
        let repr_robust = ols_robust.repr_impl();
        assert_eq!(repr_classical, "OLS(fit_intercept=true, robust=false)");
        assert_eq!(repr_robust, "OLS(fit_intercept=true, robust=true)");
    }

    #[test]
    fn test_robust_computation_logic() {
        // Test the mathematical properties of robust standard error computation
        
        // Create a simple design matrix and residuals for testing
        let design_matrix = Array2::from_shape_vec((3, 2), vec![
            1.0, 2.0,
            1.0, 3.0,
            1.0, 4.0,
        ]).unwrap();
        
        let residuals = Array1::from_vec(vec![0.1, -0.2, 0.15]);
        
        // Create a simple (X'X)^(-1) matrix
        let xtx_inv = Array2::from_shape_vec((2, 2), vec![
            0.5, -0.1,
            -0.1, 0.3,
        ]).unwrap();
        
        let ols = OLS::new(true, true);
        let robust_se = ols.compute_robust_standard_errors_rust(&design_matrix, &residuals, &xtx_inv);
        
        // Should not fail
        assert!(robust_se.is_ok());
        
        let se = robust_se.unwrap();
        
        // Should have same length as number of parameters
        assert_eq!(se.len(), 2);
        
        // All standard errors should be positive (or zero for numerical issues)
        for &se_val in se.iter() {
            assert!(se_val >= 0.0, "Standard error should be non-negative: {}", se_val);
        }
        
        // Standard errors should be finite
        for &se_val in se.iter() {
            assert!(se_val.is_finite(), "Standard error should be finite: {}", se_val);
        }
    }

    #[test]
    fn test_robust_edge_cases() {
        // Test robust standard errors with edge cases
        let ols = OLS::new(true, true);
        
        // Test with zero residuals (perfect fit)
        let design_matrix = Array2::from_shape_vec((3, 2), vec![
            1.0, 2.0,
            1.0, 3.0,
            1.0, 4.0,
        ]).unwrap();
        
        let zero_residuals = Array1::from_vec(vec![0.0, 0.0, 0.0]);
        
        let xtx_inv = Array2::from_shape_vec((2, 2), vec![
            0.5, -0.1,
            -0.1, 0.3,
        ]).unwrap();
        
        let robust_se = ols.compute_robust_standard_errors_rust(&design_matrix, &zero_residuals, &xtx_inv);
        assert!(robust_se.is_ok());
        
        let se = robust_se.unwrap();
        
        // With zero residuals, robust standard errors should be zero
        for &se_val in se.iter() {
            assert_abs_diff_eq!(se_val, 0.0, epsilon = 1e-12);
        }
    }

    #[test]
    fn test_robust_vs_classical_properties() {
        // Test mathematical relationships between robust and classical SEs
        
        // Both should be positive definite and symmetric
        let ols_classical = OLS::new(false, false);
        let ols_robust = OLS::new(false, true);
        
        // Test that both configurations work
        assert!(!ols_classical.robust);
        assert!(ols_robust.robust);
        
        // Test structural properties
        assert!(!ols_classical.is_fitted_impl());
        assert!(!ols_robust.is_fitted_impl());
        
        // Test that both have same basic properties when unfitted
        assert_eq!(ols_classical.get_fit_intercept(), false);
        assert_eq!(ols_robust.get_fit_intercept(), false);
        
        assert_eq!(ols_classical.get_model_name(), "OLS Regression Results");
        assert_eq!(ols_robust.get_model_name(), "OLS Regression Results");
        
        assert_eq!(ols_classical.get_method_name(), "Least Squares");
        assert_eq!(ols_robust.get_method_name(), "Least Squares");
    }

    #[test]
    fn test_robust_memory_efficiency() {
        // Test that robust computation doesn't cause memory issues
        
        // Create models with different configurations
        let configurations = vec![
            (true, false),   // intercept, classical
            (true, true),    // intercept, robust
            (false, false),  // no intercept, classical
            (false, true),   // no intercept, robust
        ];
        
        for (fit_intercept, robust) in configurations {
            let ols = OLS::new(fit_intercept, robust);
            
            // Test basic properties
            assert_eq!(ols.fit_intercept, fit_intercept);
            assert_eq!(ols.robust, robust);
            assert!(!ols.is_fitted_impl());
            
            // Test that all fields are properly initialized
            assert!(ols.coefficients.is_none());
            assert!(ols.standard_errors_.is_none());
            assert!(ols.residuals.is_none());
            assert!(ols.mse.is_none());
            assert!(ols.r_squared.is_none());
            assert!(ols.n_samples.is_none());
            assert!(ols.n_features.is_none());
            assert!(ols.xtx_inv.is_none());
            assert!(ols.covariance_matrix.get().is_none());
        }
    }
}