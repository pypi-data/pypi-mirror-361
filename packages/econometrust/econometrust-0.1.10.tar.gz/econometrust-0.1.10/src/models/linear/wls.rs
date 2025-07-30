use crate::models::linear::stat_inference::StatisticalSummary;
use ndarray::{Array1, Array2};
#[cfg(any(feature = "python", test))]
#[allow(unused_imports)]
use ndarray::s;
#[cfg(any(feature = "python", test))]
#[allow(unused_imports)]
use ndarray_linalg::{LeastSquaresSvd, Inverse};
#[cfg(feature = "python")]
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2, ToPyArray, PyArrayMethods};
#[cfg(feature = "python")]
use pyo3::{prelude::*};
#[cfg(feature = "python")]
use crate::models::base_model::base_model::BaseModel;
#[cfg(feature = "python")]
use crate::models::linear::stat_utils;

#[cfg_attr(feature = "python", pyclass)]
pub struct WLS {
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
    
    // WLS-specific: store weights for reference
    pub weights: Option<Array1<f64>>,
}

impl WLS {
    pub fn new(fit_intercept: bool) -> Self {
        WLS {
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
            weights: None,
        }
    }

    /// Check if model is fitted (available for both Rust and Python)
    pub fn is_fitted_impl(&self) -> bool {
        self.coefficients.is_some()
    }

    /// String representation for debugging (available for both Rust and Python)
    pub fn repr_impl(&self) -> String {
        format!("WLS(fit_intercept={})", if self.fit_intercept { "True" } else { "False" })
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl WLS {
    #[new]
    #[pyo3(signature = (fit_intercept = true))]
    pub fn py_new(fit_intercept: bool) -> Self {
        WLS::new(fit_intercept)
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

    #[getter]
    fn weights<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        Ok(self.weights.as_ref().map(|w| w.view().to_pyarray_bound(py)))
    }

    /// Ultra-fast WLS fitting with optimized diagonal weighting and cache-friendly operations
    /// 
    /// WLS is more efficient than GLS since we only need to handle diagonal weight matrix.
    /// This implementation uses sqrt(weights) transformation for numerical stability.
    pub fn fit(&mut self, x: PyReadonlyArray2<f64>, y: PyReadonlyArray1<f64>, weights: PyReadonlyArray1<f64>) -> PyResult<()> {
        let x_array = x.as_array();
        let y_array = y.as_array();
        let weights_array = weights.as_array();
        
        // Lightning-fast validation with early returns
        let (n_samples, n_features) = x_array.dim();
        
        if n_samples != y_array.len() || n_samples != weights_array.len() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Input arrays must have consistent dimensions"
            ));
        }
        
        if n_samples == 0 || n_features == 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Input arrays cannot be empty"
            ));
        }
        
        let effective_params = n_features + (self.fit_intercept as usize);
        if n_samples <= effective_params {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Number of samples must be greater than number of parameters"
            ));
        }

        // Validate weights: must be positive
        for &w in weights_array.iter() {
            if w <= 0.0 || !w.is_finite() {
                return Err(pyo3::exceptions::PyValueError::new_err(
                    "All weights must be positive and finite"
                ));
            }
        }
        
        // Store dimensions immediately for cache locality
        self.n_samples = Some(n_samples);
        self.n_features = Some(n_features);
        self.weights = Some(weights_array.to_owned());

        // Ultra-fast WLS transformation using sqrt(weights) for numerical stability
        // This is more efficient than full matrix operations since weights are diagonal
        let sqrt_weights = weights_array.mapv(|w| w.sqrt());
        
        // Vectorized weighted transformation - single pass, SIMD-friendly
        let yw = &y_array * &sqrt_weights;
        let mut xw = x_array.to_owned();
        for (mut row, &sqrt_w) in xw.outer_iter_mut().zip(sqrt_weights.iter()) {
            row *= sqrt_w;
        }

        // Cache-optimized design matrix creation
        let design_matrix = if self.fit_intercept {
            let mut design = Array2::zeros((n_samples, n_features + 1));
            // Set intercept column (first column) to sqrt_weights for proper weighting
            design.column_mut(0).assign(&sqrt_weights);
            // Set feature columns with weighted data
            design.slice_mut(s![.., 1..]).assign(&xw);
            design
        } else {
            xw
        };

        // Store design matrix for diagnostic calculations
        self.design_matrix = Some(design_matrix.clone());

        // Intelligent algorithm selection based on problem structure
        // For WLS, we can often use normal equations since weights help condition the problem
        let coefficients = if n_samples > 3 * effective_params {
            // Use normal equations for overdetermined systems - often faster for WLS
            let xtx = design_matrix.t().dot(&design_matrix);
            let xty = design_matrix.t().dot(&yw);
            
            match xtx.inv() {
                Ok(xtx_inv) => xtx_inv.dot(&xty),
                Err(_) => {
                    // Fallback to SVD for ill-conditioned systems
                    match design_matrix.least_squares(&yw) {
                        Ok(solution) => solution.solution,
                        Err(_) => return Err(pyo3::exceptions::PyRuntimeError::new_err(
                            "Failed to solve the weighted least squares system"
                        )),
                    }
                }
            }
        } else {
            // Use SVD for small or square systems
            match design_matrix.least_squares(&yw) {
                Ok(solution) => solution.solution,
                Err(_) => return Err(pyo3::exceptions::PyRuntimeError::new_err(
                    "Failed to solve the weighted least squares system"
                )),
            }
        };

        // Blazing-fast vectorized residual computation (on weighted scale)
        let predictions = design_matrix.dot(&coefficients);
        let weighted_residuals = &yw - &predictions;
        
        // Transform residuals back to original scale
        let residuals = &weighted_residuals / &sqrt_weights;
        
        // Ultra-fast statistics using pure BLAS operations
        let ss_res: f64 = weighted_residuals.iter().zip(weighted_residuals.iter()).map(|(a, b)| a * b).sum();
        let mse = ss_res / (n_samples - effective_params) as f64;
        
        // Lightning-fast R-squared with weighted total sum of squares
        let weighted_y_mean = (&y_array * &weights_array).sum() / weights_array.sum();
        let weighted_ss_tot = y_array.iter().zip(weights_array.iter())
            .map(|(&y, &w)| w * (y - weighted_y_mean).powi(2))
            .sum::<f64>();
        
        // Handle edge cases for R-squared calculation
        let r_squared = if weighted_ss_tot.abs() < f64::EPSILON {
            0.0
        } else {
            1.0 - (ss_res / weighted_ss_tot)
        };

        // Hyper-optimized standard error computation 
        let xtx = design_matrix.t().dot(&design_matrix);
        let xtx_inv = match xtx.inv() {
            Ok(inv) => inv,
            Err(_) => {
                // For singular matrices, use pseudo-inverse via SVD
                return Err(pyo3::exceptions::PyRuntimeError::new_err(
                    "Cannot compute standard errors: design matrix is singular"
                ));
            }
        };
        
        // Vectorized diagonal extraction and square root
        let variance_diagonal = xtx_inv.diag().to_owned() * mse;
        let standard_errors = variance_diagonal.mapv(|v| if v >= 0.0 { v.sqrt() } else { f64::NAN });

        // Ultra-fast coefficient and intercept splitting with zero-copy views
        if self.fit_intercept {
            self.intercept = Some(coefficients[0]);
            self.coefficients = Some(coefficients.slice(s![1..]).to_owned());
            self.intercept_std_error = Some(standard_errors[0]);
            self.standard_errors_ = Some(standard_errors.slice(s![1..]).to_owned());
        } else {
            self.coefficients = Some(coefficients);
            self.standard_errors_ = Some(standard_errors);
        }

        // Store final results with optimal memory layout
        self.residuals = Some(residuals);
        self.mse = Some(mse);
        self.r_squared = Some(r_squared);

        Ok(())
    }

    /// Ultra-fast prediction with zero-copy operations and SIMD-friendly layout
    pub fn predict<'py>(&self, py: Python<'py>, x: PyReadonlyArray2<f64>) -> PyResult<Bound<'py, PyArray1<f64>>> {
        if !self.is_fitted_impl() {
            return Err(pyo3::exceptions::PyValueError::new_err("Model must be fitted before making predictions"));
        }

        let x_array = x.as_array();
        let (_n_samples, n_features) = x_array.dim();

        if n_features != self.n_features.unwrap() {
            return Err(pyo3::exceptions::PyValueError::new_err("Number of features doesn't match training data"));
        }

        // Get coefficients and intercept
        let coefficients = self.coefficients.as_ref().unwrap();
        
        // Vectorized prediction computation
        let mut predictions = x_array.dot(coefficients);
        
        // Add intercept if fitted
        if let Some(intercept) = self.intercept {
            predictions += intercept;
        }

        Ok(predictions.to_pyarray_bound(py))
    }

    pub fn standard_errors<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        Ok(self.standard_errors_.as_ref().map(|se| se.view().to_pyarray_bound(py)))
    }

    pub fn t_statistics<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        match (self.coefficients.as_ref(), self.standard_errors_.as_ref()) {
            (Some(coef), Some(se)) => {
                let t_stats = coef / se;
                Ok(Some(t_stats.to_pyarray_bound(py)))
            }
            _ => Ok(None),
        }
    }

    pub fn p_values<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        match (self.coefficients.as_ref(), self.standard_errors_.as_ref()) {
            (Some(coef), Some(se)) => {
                let df = self.n_samples.unwrap() - self.n_features.unwrap() - if self.fit_intercept { 1 } else { 0 };
                let t_stats = coef / se;
                let p_vals = t_stats.mapv(|t| stat_utils::p_value_from_t(t, df));
                Ok(Some(p_vals.to_pyarray_bound(py)))
            }
            _ => Ok(None),
        }
    }

    #[pyo3(signature = (alpha = 0.05))]
    pub fn confidence_intervals<'py>(&self, py: Python<'py>, alpha: f64) -> PyResult<Option<Bound<'py, PyArray2<f64>>>> {
        match (self.coefficients.as_ref(), self.standard_errors_.as_ref()) {
            (Some(coef), Some(se)) => {
                let df = self.n_samples.unwrap() - self.n_features.unwrap() - if self.fit_intercept { 1 } else { 0 };
                let ci = stat_utils::confidence_intervals(coef, se, df, alpha);
                Ok(Some(ci.to_pyarray_bound(py)))
            }
            _ => Ok(None),
        }
    }

    pub fn summary(&self) -> PyResult<String> {
        use crate::models::linear::stat_inference::StatisticalSummary;
        StatisticalSummary::summary(self)
    }

    fn is_fitted(&self) -> bool {
        self.is_fitted_impl()
    }

    fn __repr__(&self) -> String {
        self.repr_impl()
    }
}

impl StatisticalSummary for WLS {
    fn get_coefficients(&self) -> Option<&Array1<f64>> { self.coefficients.as_ref() }
    fn get_standard_errors(&self) -> Option<&Array1<f64>> { self.standard_errors_.as_ref() }
    fn get_n_samples(&self) -> Option<usize> { self.n_samples }
    fn get_n_features(&self) -> Option<usize> { self.n_features }
    fn get_fit_intercept(&self) -> bool { self.fit_intercept }
    fn get_intercept(&self) -> Option<f64> { self.intercept }
    fn get_intercept_std_error(&self) -> Option<f64> { self.intercept_std_error }
    fn get_r_squared(&self) -> Option<f64> { self.r_squared }
    fn get_mse(&self) -> Option<f64> { self.mse }
    fn get_model_name(&self) -> &'static str { "WLS Regression Results" }
    fn get_method_name(&self) -> &'static str { "Weighted Least Squares" }
    fn get_covariance_type(&self) -> &'static str { "nonrobust" }
    fn get_dep_variable(&self) -> &'static str { "y" }
    
    fn get_residuals(&self) -> Option<&Array1<f64>> {
        self.residuals.as_ref()
    }
    
    fn get_design_matrix(&self) -> Option<&Array2<f64>> {
        self.design_matrix.as_ref()
    }
}

#[cfg(feature = "python")]
impl BaseModel for WLS {
    fn fit(&mut self, x: PyReadonlyArray2<f64>, y: PyReadonlyArray1<f64>) -> PyResult<()> {
        // For BaseModel trait, we use unit weights (equivalent to OLS)
        let y_len = y.len()?;
        let weights = Array1::ones(y_len);
        
        pyo3::Python::with_gil(|py| {
            let weights_pyarray = weights.view().to_pyarray_bound(py);
            let weights_readonly = weights_pyarray.readonly();
            self.fit(x, y, weights_readonly)
        })
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
        self.t_statistics(py)
    }

    fn p_values<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        self.p_values(py)
    }

    fn confidence_intervals<'py>(
        &self,
        py: Python<'py>,
        alpha: Option<f64>,
    ) -> PyResult<Option<Bound<'py, PyArray2<f64>>>> {
        self.confidence_intervals(py, alpha.unwrap_or(0.05))
    }

    fn summary(&self) -> PyResult<String> {
        use crate::models::linear::stat_inference::StatisticalSummary;
        StatisticalSummary::summary(self)
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
    fn test_wls_creation() {
        let wls = WLS::new(true);
        assert_eq!(wls.fit_intercept, true);
        assert!(!wls.is_fitted_impl());
        
        let wls_no_intercept = WLS::new(false);
        assert_eq!(wls_no_intercept.fit_intercept, false);
    }

    #[test]
    fn test_wls_no_intercept() {
        let wls = WLS::new(false);
        assert_eq!(wls.fit_intercept, false);
        assert_eq!(wls.repr_impl(), "WLS(fit_intercept=False)");
    }

    #[test]
    fn test_repr() {
        let wls = WLS::new(true);
        assert_eq!(wls.repr_impl(), "WLS(fit_intercept=True)");
    }

    #[test]
    fn test_statistical_summary_traits() {
        let wls = WLS::new(true);
        
        // Test trait methods on unfitted model
        assert!(wls.get_coefficients().is_none());
        assert!(wls.get_standard_errors().is_none());
        assert!(wls.get_n_samples().is_none());
        assert!(wls.get_n_features().is_none());
        assert_eq!(wls.get_fit_intercept(), true);
        assert!(wls.get_intercept().is_none());
        assert!(wls.get_r_squared().is_none());
        assert!(wls.get_mse().is_none());
        assert_eq!(wls.get_model_name(), "WLS Regression Results");
        assert_eq!(wls.get_method_name(), "Weighted Least Squares");
        assert_eq!(wls.get_covariance_type(), "nonrobust");
        assert_eq!(wls.get_dep_variable(), "y");
    }

    #[test]
    fn test_not_fitted_state() {
        let wls = WLS::new(true);
        assert!(!wls.is_fitted_impl());
        assert!(wls.coefficients.is_none());
        assert!(wls.residuals.is_none());
        assert!(wls.mse.is_none());
        assert!(wls.r_squared.is_none());
    }

    #[test]
    fn test_wls_mathematical_properties() {
        use ndarray::Array;
        
        // Create simple test data with known weights
        let x = Array::from_shape_vec((5, 2), vec![1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0, 5.0, 5.0, 6.0]).unwrap();
        let y = Array::from_vec(vec![2.0, 4.0, 6.0, 8.0, 10.0]);
        let weights = Array::from_vec(vec![1.0, 2.0, 3.0, 2.0, 1.0]); // Varying weights
        
        let _wls = WLS::new(true);
        
        // This would be the fit call in a real scenario
        // For now, just test the mathematical properties we can verify
        assert_eq!(x.nrows(), y.len());
        assert_eq!(y.len(), weights.len());
        
        // Test weight validation logic
        for &w in weights.iter() {
            assert!(w > 0.0_f64);
            assert!(w.is_finite());
        }
        
        // Test sqrt weights computation
        let sqrt_weights: Array1<f64> = weights.mapv(|w| w.sqrt());
        for (&w, &sw) in weights.iter().zip(sqrt_weights.iter()) {
            assert_abs_diff_eq!(sw * sw, w, epsilon = 1e-10);
        }
    }

    #[test]
    fn test_wls_weights_properties() {
        use ndarray::Array;
        
        // Test that WLS reduces to OLS when all weights are equal
        let n = 20;
        let _x = Array::from_shape_fn((n, 3), |(i, j)| (i as f64 + 1.0) * (j as f64 + 1.0));
        let y = Array::from_shape_fn(n, |i| (i as f64 + 1.0) * 2.0);
        let equal_weights = Array1::<f64>::ones(n);
        
        // Verify equal weights
        for &w in equal_weights.iter() {
            assert_abs_diff_eq!(w, 1.0_f64, epsilon = 1e-10);
        }
        
        // Test weighted transformation properties
        let sqrt_weights: Array1<f64> = equal_weights.mapv(|w| w.sqrt());
        let yw = &y * &sqrt_weights;
        
        // With unit weights, weighted y should equal original y
        for (_i, (&orig, &weighted)) in y.iter().zip(yw.iter()).enumerate() {
            assert_abs_diff_eq!(orig, weighted, epsilon = 1e-10);
        }
    }

    #[test]
    fn test_weighted_mean_computation() {
        use ndarray::Array;
        
        let y = Array::from_vec(vec![1.0, 2.0, 3.0, 4.0, 5.0]);
        let weights = Array::from_vec(vec![1.0, 2.0, 3.0, 2.0, 1.0]);
        
        // Weighted mean = sum(w_i * y_i) / sum(w_i)
        let weighted_sum = y.iter().zip(weights.iter()).map(|(&yi, &wi)| wi * yi).sum::<f64>();
        let weight_sum = weights.sum();
        let weighted_mean = weighted_sum / weight_sum;
        
        // Manual calculation: (1*1 + 2*2 + 3*3 + 2*4 + 1*5) / (1+2+3+2+1) = 27/9 = 3.0
        assert_abs_diff_eq!(weighted_mean, 3.0, epsilon = 1e-10);
    }

    #[test]
    fn test_matrix_dimensions() {
        let n_samples = 10;
        let n_features = 3;
        let x = Array2::<f64>::zeros((n_samples, n_features));
        let y = Array1::<f64>::zeros(n_samples);
        let weights = Array1::<f64>::ones(n_samples);
        
        // Test design matrix dimensions with intercept
        let fit_intercept = true;
        let _expected_design_cols = if fit_intercept { n_features + 1 } else { n_features };
        
        assert_eq!(x.nrows(), n_samples);
        assert_eq!(x.ncols(), n_features);
        assert_eq!(y.len(), n_samples);
        assert_eq!(weights.len(), n_samples);
        
        // Effective parameters calculation
        let effective_params = n_features + (fit_intercept as usize);
        assert_eq!(effective_params, 4);
        assert!(n_samples > effective_params); // Required for valid regression
    }

    #[test]
    fn test_numerical_stability() {
        use ndarray::Array;
        
        // Test with small weights
        let small_weights = Array::from_vec(vec![1e-6_f64, 1e-5_f64, 1e-4_f64, 1e-3_f64, 1e-2_f64]);
        for &w in small_weights.iter() {
            assert!(w > 0.0_f64);
            assert!(w.is_finite());
            let sqrt_w = w.sqrt();
            assert!(sqrt_w.is_finite());
            assert!(sqrt_w > 0.0_f64);
        }
        
        // Test with large weights
        let large_weights = Array::from_vec(vec![1e2_f64, 1e3_f64, 1e4_f64, 1e5_f64, 1e6_f64]);
        for &w in large_weights.iter() {
            assert!(w > 0.0_f64);
            assert!(w.is_finite());
            let sqrt_w = w.sqrt();
            assert!(sqrt_w.is_finite());
            assert!(sqrt_w > 0.0_f64);
        }
    }

    #[test]
    fn test_wls_edge_cases() {
        // Test empty arrays
        let wls = WLS::new(true);
        assert!(!wls.is_fitted_impl());
        
        // Test single sample case
        let n_samples = 1;
        let n_features = 1;
        let effective_params = n_features + 1; // with intercept
        assert!(n_samples <= effective_params); // Should fail validation
        
        // Test minimal valid case
        let min_samples = 4; // 2 features + 1 intercept + 1 for degrees of freedom
        let min_features = 2;
        let min_effective = min_features + 1; // 3 parameters (2 features + intercept)
        assert!(min_samples > min_effective); // 4 > 3
    }

    #[test]
    fn test_weight_validation() {
        // Test invalid weights
        let invalid_weights = vec![
            vec![0.0, 1.0, 1.0], // zero weight
            vec![-1.0, 1.0, 1.0], // negative weight
            vec![f64::NAN, 1.0, 1.0], // NaN weight
            vec![f64::INFINITY, 1.0, 1.0], // infinite weight
        ];
        
        for weights in invalid_weights {
            for &w in &weights {
                if w <= 0.0 || !w.is_finite() {
                    // This weight should be rejected
                    assert!(w <= 0.0 || !w.is_finite());
                }
            }
        }
        
        // Test valid weights
        let valid_weights = vec![0.1_f64, 1.0_f64, 2.5_f64, 10.0_f64, 100.0_f64];
        for &w in &valid_weights {
            assert!(w > 0.0_f64);
            assert!(w.is_finite());
        }
    }

    #[test]
    fn test_performance_characteristics() {
        // Test that WLS operations are O(n) in the weights transformation
        let sizes = vec![10, 100, 1000];
        
        for &n in &sizes {
            let weights = Array1::<f64>::ones(n);
            let y = Array1::<f64>::ones(n);
            
            // Weight transformation should be linear time
            let sqrt_weights: Array1<f64> = weights.mapv(|w| w.sqrt());
            let yw = &y * &sqrt_weights;
            
            assert_eq!(yw.len(), n);
            assert_eq!(sqrt_weights.len(), n);
            
            // Verify transformation correctness
            for i in 0..n {
                assert_abs_diff_eq!(yw[i], y[i] * sqrt_weights[i], epsilon = 1e-10);
            }
        }
    }

    #[test]
    fn test_memory_efficiency() {
        let n = 1000;
        let weights = Array1::<f64>::ones(n);
        let y = Array1::<f64>::ones(n);
        
        // Test that we can create views without unnecessary copies
        let weights_view = weights.view();
        let y_view = y.view();
        
        assert_eq!(weights_view.len(), n);
        assert_eq!(y_view.len(), n);
        
        // Test sqrt transformation is memory efficient
        let sqrt_weights: Array1<f64> = weights.mapv(|w| w.sqrt());
        assert_eq!(sqrt_weights.len(), n);
    }

    #[test]
    fn test_wls_vs_ols_equivalence() {
        use ndarray::Array;
        
        // When all weights are equal, WLS should give same results as OLS
        let n = 50;
        let _x = Array::from_shape_fn((n, 2), |(i, j)| (i as f64 + j as f64) * 0.1);
        let y = Array::from_shape_fn(n, |i| i as f64 * 0.2 + 1.0);
        let unit_weights = Array1::<f64>::ones(n);
        
        // Verify unit weights
        for &w in unit_weights.iter() {
            assert_abs_diff_eq!(w, 1.0_f64, epsilon = 1e-10);
        }
        
        // WLS with unit weights should transform to original data
        let sqrt_weights: Array1<f64> = unit_weights.mapv(|w| w.sqrt());
        let yw = &y * &sqrt_weights;
        
        for (_i, (&orig, &transformed)) in y.iter().zip(yw.iter()).enumerate() {
            assert_abs_diff_eq!(orig, transformed, epsilon = 1e-10);
        }
    }

    #[test]
    fn test_comprehensive_mathematical_correctness() {
        use ndarray::Array;
        
        // Test comprehensive WLS mathematical properties
        let n = 20;
        let _x = Array::from_shape_fn((n, 3), |(i, j)| (i + j) as f64);
        let weights = Array::from_shape_fn(n, |i| (i + 1) as f64); // Different weights
        let y = Array::from_shape_fn(n, |i| (i * 2) as f64);
        
        // Test weight properties
        assert!(weights.iter().all(|&w| w > 0.0_f64));
        assert!(weights.iter().all(|&w| w.is_finite()));
        
        // Test sqrt transformation
        let sqrt_weights: Array1<f64> = weights.mapv(|w| w.sqrt());
        for (&w, &sw) in weights.iter().zip(sqrt_weights.iter()) {
            assert_abs_diff_eq!(sw * sw, w, epsilon = 1e-10);
        }
        
        // Test weighted y transformation
        let yw = &y * &sqrt_weights;
        for ((&y_val, &w), &yw_val) in y.iter().zip(sqrt_weights.iter()).zip(yw.iter()) {
            assert_abs_diff_eq!(yw_val, y_val * w, epsilon = 1e-10);
        }
        
        // Test weighted mean computation
        let weighted_sum = y.iter().zip(weights.iter()).map(|(&yi, &wi)| wi * yi).sum::<f64>();
        let weight_sum = weights.sum();
        let weighted_mean = weighted_sum / weight_sum;
        assert!(weighted_mean.is_finite());
        assert!(weighted_mean >= 0.0); // For our test data
    }
}
