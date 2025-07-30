use ndarray::{s, Array1, Array2, ArrayView1, ArrayView2};
use ndarray_linalg::Inverse;
#[cfg(feature = "python")]
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2, ToPyArray};
#[cfg(feature = "python")]
use pyo3::{prelude::*, exceptions::PyValueError, Python, PyResult, Bound};
#[cfg(feature = "python")]
use crate::models::base_model::base_model::BaseModel;
use crate::models::linear::stat_inference::StatisticalSummary;
use crate::models::linear::stat_utils;

/// Instrumental Variables (IV) regression estimator for exactly identified models.
///
/// The IV estimator is used when some regressors are endogenous (correlated with the error term).
/// It uses instrumental variables to obtain consistent estimates of the parameters.
/// 
/// This implementation handles exactly identified models where the number of instruments
/// equals the number of regressors. For overidentified cases (more instruments than regressors),
/// use the TSLS (Two-Stage Least Squares) estimator instead.
///
/// The IV estimator solves: β̂ = (Z'X)⁻¹Z'y
/// where Z are the instruments, X are the regressors, and y is the dependent variable.
#[cfg_attr(feature = "python", pyclass(name = "IV"))]
#[derive(Debug)]
pub struct IV {
    pub fit_intercept: bool,
    pub fitted: bool,
    pub coefficients: Option<Array1<f64>>,
    pub intercept: Option<f64>,
    pub standard_errors_: Option<Array1<f64>>,
    pub intercept_std_error: Option<f64>,
    pub mse: Option<f64>,
    pub r_squared: Option<f64>,
    pub n_samples: Option<usize>,
    pub n_features: Option<usize>,
    pub residuals: Option<Array1<f64>>,
    pub design_matrix: Option<Array2<f64>>,
    pub instruments: Option<Array2<f64>>,
    pub regressors: Option<Array2<f64>>,
    pub targets: Option<Array1<f64>>,
    pub covariance_matrix: Option<Array2<f64>>,
}

impl Default for IV {
    fn default() -> Self {
        Self::new(true)
    }
}

impl IV {
    /// Create a new IV estimator.
    pub fn new(fit_intercept: bool) -> Self {
        IV {
            fit_intercept,
            fitted: false,
            coefficients: None,
            intercept: None,
            standard_errors_: None,
            intercept_std_error: None,
            mse: None,
            r_squared: None,
            n_samples: None,
            n_features: None,
            residuals: None,
            design_matrix: None,
            instruments: None,
            regressors: None,
            targets: None,
            covariance_matrix: None,
        }
    }

    /// Fit the IV model using instrumental variables.
    pub fn fit_impl(
        &mut self,
        instruments: ArrayView2<f64>,
        regressors: ArrayView2<f64>,
        targets: ArrayView1<f64>,
    ) -> Result<(), String> {
        self.validate_data(&instruments, &regressors, &targets)?;

        let n_samples = instruments.nrows();
        let n_instruments = instruments.ncols();
        let n_features = regressors.ncols();

        // Add intercept to instruments and regressors if requested
        let (z_matrix, x_matrix) = if self.fit_intercept {
            // For IV estimation, we add intercept to both Z and X matrices
            // but we need to be careful about the construction to avoid singularity
            let mut z_design = Array2::<f64>::ones((n_samples, n_instruments + 1));
            z_design.slice_mut(s![.., 1..]).assign(&instruments);
            
            let mut x_design = Array2::<f64>::ones((n_samples, n_features + 1));
            x_design.slice_mut(s![.., 1..]).assign(&regressors);
            
            (z_design, x_design)
        } else {
            (instruments.to_owned(), regressors.to_owned())
        };

        // Compute Z'X and Z'y
        let zt_x = z_matrix.t().dot(&x_matrix);
        let zt_y = z_matrix.t().dot(&targets);

        // Solve for IV coefficients: β̂ = (Z'X)⁻¹Z'y
        let zt_x_inv = zt_x.inv().map_err(|_| {
            "Z'X matrix is singular. This indicates under-identification: 
             Check that instruments are sufficiently correlated with regressors."
        })?;

        // Compute IV coefficients: β̂ = (Z'X)⁻¹Z'y
        let all_coefficients = zt_x_inv.dot(&zt_y);

        // Split coefficients and intercept
        let (intercept, coefficients) = if self.fit_intercept {
            let intercept = Some(all_coefficients[0]);
            let coefficients = all_coefficients.slice(s![1..]).to_owned();
            (intercept, coefficients)
        } else {
            (None, all_coefficients)
        };

        // Compute residuals: ε̂ = y - Xβ̂
        let y_pred = if self.fit_intercept {
            regressors.dot(&coefficients) + intercept.unwrap()
        } else {
            regressors.dot(&coefficients)
        };
        let residuals = &targets.to_owned() - &y_pred;

        // Store fitted values
        self.coefficients = Some(coefficients);
        self.intercept = intercept;
        self.residuals = Some(residuals.clone());
        self.instruments = Some(instruments.to_owned());
        self.regressors = Some(regressors.to_owned());
        self.targets = Some(targets.to_owned());
        self.n_samples = Some(n_samples);
        self.n_features = Some(n_features);

        // Compute covariance matrix and statistics
        self.compute_covariance_matrix()?;
        self.compute_diagnostics()?;
        let covariance_matrix = self.covariance_matrix.as_ref().unwrap().clone();
        self.compute_standard_errors(&covariance_matrix)?;

        self.fitted = true;
        Ok(())
    }

    /// Compute the covariance matrix of the IV estimator.
    fn compute_covariance_matrix(&mut self) -> Result<(), String> {
        let residuals = self.residuals.as_ref().unwrap();
        let instruments = self.instruments.as_ref().unwrap();
        let regressors = self.regressors.as_ref().unwrap();

        let n_samples = instruments.nrows();
        let effective_params = if self.fit_intercept {
            regressors.ncols() + 1
        } else {
            regressors.ncols()
        };

        // Estimate error variance
        let degrees_of_freedom = n_samples - effective_params;
        if degrees_of_freedom == 0 {
            return Err("Insufficient degrees of freedom for covariance estimation".to_string());
        }

        let sigma_squared = residuals.dot(residuals) / degrees_of_freedom as f64;

        // Build matrices with intercept if needed
        let (z_matrix, x_matrix) = if self.fit_intercept {
            let mut z_design = Array2::<f64>::ones((n_samples, instruments.ncols() + 1));
            z_design.slice_mut(s![.., 1..]).assign(&instruments);
            
            let mut x_design = Array2::<f64>::ones((n_samples, regressors.ncols() + 1));
            x_design.slice_mut(s![.., 1..]).assign(&regressors);
            
            (z_design, x_design)
        } else {
            (instruments.clone(), regressors.clone())
        };

        // For IV estimator, the covariance matrix is: σ²(X'Z(Z'Z)⁻¹Z'X)⁻¹
        let zt_z = z_matrix.t().dot(&z_matrix);
        let zt_x = z_matrix.t().dot(&x_matrix);
        let xt_z = x_matrix.t().dot(&z_matrix);
        
        let zt_z_inv = zt_z.inv().map_err(|_| "Z'Z matrix is singular")?;
        let xt_z_ztz_inv = xt_z.dot(&zt_z_inv);
        let xt_z_ztz_inv_zt_x = xt_z_ztz_inv.dot(&zt_x);
        
        let covariance_matrix = sigma_squared * xt_z_ztz_inv_zt_x.inv()
            .map_err(|_| "X'Z(Z'Z)⁻¹Z'X matrix is singular")?;

        self.covariance_matrix = Some(covariance_matrix);
        Ok(())
    }

    /// Compute standard errors from covariance matrix
    fn compute_standard_errors(&mut self, covariance_matrix: &Array2<f64>) -> Result<(), String> {
        let coefficients = self.coefficients.as_ref().unwrap();
        
        // Compute standard errors from covariance matrix diagonal
        // The covariance matrix already includes sigma_squared, so we just take sqrt of diagonal
        let variance_diagonal = covariance_matrix.diag();
        let std_errors = variance_diagonal.mapv(|x| x.sqrt());
        
        // Split standard errors to separate intercept and regular coefficients
        let (_, _, standard_errors_only, intercept_std_error) =
            stat_utils::split_intercept_and_coefs(coefficients, &std_errors, self.fit_intercept);
        
        self.standard_errors_ = Some(standard_errors_only);
        self.intercept_std_error = intercept_std_error;
        
        Ok(())
    }

    /// Compute diagnostic statistics
    fn compute_diagnostics(&mut self) -> Result<(), String> {
        let residuals = self.residuals.as_ref().unwrap();
        let targets = self.targets.as_ref().unwrap();
        let n_samples = targets.len();
        let n_features = self.n_features.unwrap();
        let n_params = if self.fit_intercept { n_features + 1 } else { n_features };
        
        // Compute MSE
        let ss_res: f64 = residuals.iter().map(|r| r * r).sum();
        let mse = ss_res / (n_samples - n_params) as f64;
        
        // For IV, R-squared can be negative, so we need to be careful
        // Compute predicted values for R-squared calculation
        let regressors = self.regressors.as_ref().unwrap();
        let coefficients = self.coefficients.as_ref().unwrap();
        let y_pred = if self.fit_intercept {
            regressors.dot(coefficients) + self.intercept.unwrap()
        } else {
            regressors.dot(coefficients)
        };
        
        // Standard R-squared calculation
        let y_mean = targets.mean().unwrap();
        let ss_tot: f64 = targets.iter().map(|y| (y - y_mean).powi(2)).sum();
        let ss_res_for_r2: f64 = targets.iter().zip(y_pred.iter())
            .map(|(y, pred)| (y - pred).powi(2))
            .sum();
        
        let r_squared = if ss_tot.abs() < f64::EPSILON {
            // If y has no variance, R² is undefined, but set to 0.0
            0.0
        } else {
            1.0 - (ss_res_for_r2 / ss_tot)
        };
        
        self.mse = Some(mse);
        self.r_squared = Some(r_squared);
        
        Ok(())
    }

    /// Validate input data dimensions and requirements
    fn validate_data(
        &self,
        instruments: &ArrayView2<f64>,
        regressors: &ArrayView2<f64>,
        targets: &ArrayView1<f64>,
    ) -> Result<(), String> {
        let n_samples = targets.len();
        
        if instruments.nrows() != n_samples {
            return Err("Instruments and targets must have the same number of samples".to_string());
        }
        
        if regressors.nrows() != n_samples {
            return Err("Regressors and targets must have the same number of samples".to_string());
        }
        
        // For IV estimator, we need exactly the same number of instruments as regressors (exact identification)
        if instruments.ncols() != regressors.ncols() {
            return Err("IV estimator requires exactly the same number of instruments as regressors (exact identification). For overidentified cases, use TSLS estimator.".to_string());
        }
        
        if n_samples <= regressors.ncols() {
            return Err("Number of samples must be greater than number of regressors".to_string());
        }
        
        Ok(())
    }
}

impl StatisticalSummary for IV {
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
        "IV"
    }

    fn get_method_name(&self) -> &'static str {
        "Instrumental Variables"
    }

    fn get_covariance_type(&self) -> &'static str {
        "nonrobust"
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
impl BaseModel for IV {
    fn fit(&mut self, instruments: PyReadonlyArray2<f64>, targets: PyReadonlyArray1<f64>) -> PyResult<()> {
        // For IV, we need both instruments and regressors, but BaseModel only has x and y
        // This is a limitation of the BaseModel trait for IV
        // We'll implement the Python bindings separately with proper fit method
        Err(PyValueError::new_err("Use IV.fit_iv() method instead"))
    }

    fn predict<'py>(
        &self,
        py: Python<'py>,
        regressors: PyReadonlyArray2<f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>> {
        if !self.fitted {
            return Err(PyValueError::new_err("Model not fitted"));
        }

        let x = regressors.as_array();
        let coefficients = self.coefficients.as_ref().unwrap();

        let predictions = if self.fit_intercept {
            x.dot(coefficients) + self.intercept.unwrap()
        } else {
            x.dot(coefficients)
        };

        Ok(predictions.to_pyarray_bound(py))
    }

    fn standard_errors<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        Ok(self.standard_errors_.as_ref().map(|se| se.view().to_pyarray_bound(py)))
    }

    fn t_statistics<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        StatisticalSummary::t_statistics(self, py)
    }

    fn p_values<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        StatisticalSummary::p_values(self, py)
    }

    fn confidence_intervals<'py>(
        &self,
        py: Python<'py>,
        alpha: Option<f64>,
    ) -> PyResult<Option<Bound<'py, PyArray2<f64>>>> {
        let alpha_val = alpha.unwrap_or(0.05);
        StatisticalSummary::confidence_intervals(self, py, alpha_val)
    }

    fn summary(&self) -> PyResult<String> {
        StatisticalSummary::summary(self)
    }
}

#[cfg(feature = "python")]
#[pymethods]
impl IV {
    #[new]
    #[pyo3(signature = (fit_intercept = true))]
    fn py_new(fit_intercept: bool) -> Self {
        IV::new(fit_intercept)
    }

    fn fit(
        &mut self,
        instruments: PyReadonlyArray2<f64>,
        regressors: PyReadonlyArray2<f64>,
        targets: PyReadonlyArray1<f64>,
    ) -> PyResult<()> {
        self.fit_impl(
            instruments.as_array(),
            regressors.as_array(),
            targets.as_array(),
        )
        .map_err(|e| PyValueError::new_err(e))
    }

    fn is_fitted(&self) -> bool {
        self.fitted
    }

    #[getter]
    fn coefficients<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyArray1<f64>>> {
        self.coefficients.as_ref().map(|coef| coef.view().to_pyarray_bound(py))
    }

    #[getter]
    fn fit_intercept(&self) -> bool {
        self.fit_intercept
    }

    #[getter]
    fn intercept(&self) -> Option<f64> {
        self.intercept
    }

    #[getter]
    fn instruments<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyArray2<f64>>> {
        self.instruments.as_ref().map(|inst| inst.view().to_pyarray_bound(py))
    }

    #[getter]
    fn regressors<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyArray2<f64>>> {
        self.regressors.as_ref().map(|reg| reg.view().to_pyarray_bound(py))
    }

    fn predict<'py>(&self, py: Python<'py>, regressors: PyReadonlyArray2<f64>) -> PyResult<Bound<'py, PyArray1<f64>>> {
        BaseModel::predict(self, py, regressors)
    }

    fn standard_errors<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        BaseModel::standard_errors(self, py)
    }

    fn t_statistics<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        BaseModel::t_statistics(self, py)
    }

    fn p_values<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        BaseModel::p_values(self, py)
    }

    #[pyo3(signature = (alpha = 0.05))]
    fn confidence_intervals<'py>(&self, py: Python<'py>, alpha: f64) -> PyResult<Option<Bound<'py, PyArray2<f64>>>> {
        BaseModel::confidence_intervals(self, py, Some(alpha))
    }

    fn summary(&self) -> PyResult<String> {
        BaseModel::summary(self)
    }

    #[getter]
    fn covariance_matrix<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyArray2<f64>>> {
        self.covariance_matrix.as_ref().map(|cov| cov.view().to_pyarray_bound(py))
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
    fn residuals<'py>(&self, py: Python<'py>) -> Option<Bound<'py, PyArray1<f64>>> {
        self.residuals.as_ref().map(|res| res.view().to_pyarray_bound(py))
    }

    #[getter]
    fn n_samples(&self) -> Option<usize> {
        self.n_samples
    }

    #[getter]
    fn n_features(&self) -> Option<usize> {
        self.n_features
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ndarray::array;

    #[test]
    fn test_iv_new() {
        let iv = IV::new(true);
        assert_eq!(iv.fit_intercept, true);
        assert!(!iv.fitted);
        assert!(iv.coefficients.is_none());
    }

    #[test]
    fn test_iv_simple_fit() {
        let mut iv = IV::new(true);
        
        // Create valid IV test data with strong instruments
        // Instruments should be correlated with regressors but uncorrelated with error
        let instruments = array![
            [1.0, 0.3],
            [2.0, 0.7], 
            [3.0, 1.1],
            [4.0, 1.5],
            [5.0, 1.9],
            [6.0, 2.3]
        ];
        
        // Regressors are related to instruments (but endogenous)
        let regressors = array![
            [1.1, 0.5],
            [2.2, 0.9],
            [3.1, 1.3],
            [4.2, 1.7],
            [5.1, 2.1],
            [6.2, 2.5]
        ];
        
        // Targets with a clear relationship
        let targets = array![2.0, 4.5, 6.8, 9.1, 11.4, 13.7];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        assert!(result.is_ok(), "IV fitting should succeed: {:?}", result);
        assert!(iv.fitted);
        assert!(iv.coefficients.is_some());
        assert!(iv.intercept.is_some());
        assert!(iv.mse.is_some());
        assert!(iv.r_squared.is_some());
    }

    #[test]
    fn test_iv_validation() {
        let iv = IV::new(true);
        
        // Test dimension mismatch between instruments and targets
        let instruments = array![[1.0], [2.0]];
        let regressors = array![[1.0], [2.0], [3.0]];
        let targets = array![1.0, 2.0];
        
        let result = iv.validate_data(&instruments.view(), &regressors.view(), &targets.view());
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Regressors and targets must have the same number"));
        
        // Test dimension mismatch between regressors and targets
        let instruments = array![[1.0], [2.0]];
        let regressors = array![[1.0], [2.0]];
        let targets = array![1.0, 2.0, 3.0];
        
        let result = iv.validate_data(&instruments.view(), &regressors.view(), &targets.view());
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Instruments and targets must have the same number"));
        
        // Test exact identification requirement (IV needs same number of instruments as regressors)
        let instruments = array![[1.0], [2.0], [3.0]];
        let regressors = array![[1.0, 0.5], [2.0, 1.0], [3.0, 1.5]];
        let targets = array![1.0, 2.0, 3.0];
        
        let result = iv.validate_data(&instruments.view(), &regressors.view(), &targets.view());
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("exactly the same number of instruments as regressors"));
        
        // Test insufficient samples
        let instruments = array![[1.0, 0.5]];
        let regressors = array![[1.0, 0.5]];
        let targets = array![1.0];
        
        let result = iv.validate_data(&instruments.view(), &regressors.view(), &targets.view());
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Number of samples must be greater"));
    }

    #[test]
    fn test_iv_no_intercept() {
        let mut iv = IV::new(false);
        
        // Create test data without intercept - ensure instruments are well-conditioned
        let instruments = array![
            [2.0, 3.0],
            [4.0, 1.0],
            [6.0, 5.0],
            [8.0, 2.0],
            [10.0, 7.0]
        ];
        
        let regressors = array![
            [2.1, 3.1],
            [4.2, 1.1],
            [6.1, 5.1],
            [8.2, 2.1],
            [10.1, 7.1]
        ];
        
        let targets = array![4.0, 8.5, 12.8, 17.1, 21.4];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        if let Err(ref e) = result {
            println!("Error in no intercept test: {}", e);
        }
        assert!(result.is_ok());
        assert!(iv.fitted);
        assert!(iv.coefficients.is_some());
        assert!(iv.intercept.is_none());
        assert_eq!(iv.coefficients.as_ref().unwrap().len(), 2);
    }

    #[test]
    fn test_iv_single_regressor() {
        let mut iv = IV::new(true);
        
        // Single regressor with single instrument
        let instruments = array![
            [1.0],
            [2.0],
            [3.0],
            [4.0],
            [5.0]
        ];
        
        let regressors = array![
            [1.1],
            [2.1],
            [3.1],
            [4.1],
            [5.1]
        ];
        
        let targets = array![2.0, 4.0, 6.0, 8.0, 10.0];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        assert!(result.is_ok());
        assert!(iv.fitted);
        assert_eq!(iv.coefficients.as_ref().unwrap().len(), 1);
    }

    #[test]
    fn test_iv_covariance_matrix_properties() {
        let mut iv = IV::new(true);
        
        // Create well-conditioned instruments that are not linearly dependent
        let instruments = array![
            [1.0, 2.0],
            [2.0, 1.0],
            [3.0, 4.0],
            [4.0, 3.0],
            [5.0, 6.0],
            [6.0, 5.0]
        ];
        
        let regressors = array![
            [1.1, 2.1],
            [2.1, 1.1],
            [3.1, 4.1],
            [4.1, 3.1],
            [5.1, 6.1],
            [6.1, 5.1]
        ];
        
        let targets = array![2.5, 4.2, 6.0, 7.8, 9.5, 11.2];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        if let Err(ref e) = result {
            println!("Error in covariance matrix properties test: {}", e);
        }
        assert!(result.is_ok());
        let cov_matrix = iv.covariance_matrix.as_ref().unwrap();
        
        // Check covariance matrix is square
        assert_eq!(cov_matrix.nrows(), cov_matrix.ncols());
        
        // Check diagonal elements are positive (variances)
        for i in 0..cov_matrix.nrows() {
            assert!(cov_matrix[[i, i]] > 0.0, "Variance should be positive");
        }
        
        // Check matrix is symmetric (within tolerance)
        for i in 0..cov_matrix.nrows() {
            for j in 0..cov_matrix.ncols() {
                let diff = (cov_matrix[[i, j]] - cov_matrix[[j, i]]).abs();
                assert!(diff < 1e-8, "Covariance matrix should be symmetric");
            }
        }
    }

    #[test]
    fn test_iv_statistical_summary() {
        let mut iv = IV::new(true);
        
        let instruments = array![
            [1.0, 0.8],
            [2.0, 1.6],
            [3.0, 2.4],
            [4.0, 3.2],
            [5.0, 4.0],
            [6.0, 4.8]
        ];
        
        let regressors = array![
            [1.1, 0.9],
            [2.1, 1.7],
            [3.1, 2.5],
            [4.1, 3.3],
            [5.1, 4.1],
            [6.1, 4.9]
        ];
        
        let targets = array![3.0, 5.0, 7.0, 9.0, 11.0, 13.0];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        assert!(result.is_ok());
        
        // Test statistical summary methods
        assert!(iv.get_coefficients().is_some());
        assert!(iv.get_standard_errors().is_some());
        assert!(iv.get_n_samples().is_some());
        assert!(iv.get_n_features().is_some());
        assert_eq!(iv.get_fit_intercept(), true);
        assert!(iv.get_intercept().is_some());
        assert!(iv.get_intercept_std_error().is_some());
        assert!(iv.get_r_squared().is_some());
        assert!(iv.get_mse().is_some());
        assert_eq!(iv.get_model_name(), "IV");
        assert_eq!(iv.get_method_name(), "Instrumental Variables");
        assert_eq!(iv.get_covariance_type(), "nonrobust");
        assert!(iv.get_residuals().is_some());
        
        // Check dimensions
        assert_eq!(iv.get_n_samples().unwrap(), 6);
        assert_eq!(iv.get_n_features().unwrap(), 2);
        assert_eq!(iv.get_coefficients().unwrap().len(), 2);
        assert_eq!(iv.get_standard_errors().unwrap().len(), 2);
    }

    #[test]
    fn test_iv_zero_variance_targets() {
        let mut iv = IV::new(true);
        
        // Use well-conditioned instruments
        let instruments = array![
            [1.0, 3.0],
            [2.0, 1.0],
            [3.0, 4.0],
            [4.0, 2.0]
        ];
        
        let regressors = array![
            [1.1, 3.1],
            [2.1, 1.1],
            [3.1, 4.1],
            [4.1, 2.1]
        ];
        
        let targets = array![5.0, 5.0, 5.0, 5.0]; // Zero variance
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        if let Err(ref e) = result {
            println!("Error in zero variance test: {}", e);
        }
        assert!(result.is_ok());
        assert_eq!(iv.get_r_squared().unwrap(), 0.0); // R-squared should be 0 for zero variance
    }

    #[test]
    fn test_iv_exactly_identified_case() {
        let mut iv = IV::new(true);
        
        // Exactly identified case: 2 instruments for 2 regressors + intercept
        let instruments = array![
            [1.0, 3.0],
            [2.0, 1.0],
            [3.0, 4.0],
            [4.0, 2.0],
            [5.0, 6.0],
            [6.0, 5.0]
        ];
        
        // Regressors correlated with but different from instruments
        let regressors = array![
            [1.1, 3.1],
            [2.1, 1.1],
            [3.1, 4.1],
            [4.1, 2.1],
            [5.1, 6.1],
            [6.1, 5.1]
        ];
        
        let targets = array![3.0, 6.0, 9.0, 12.0, 15.0, 18.0];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        assert!(result.is_ok());
        assert!(iv.fitted);
        
        // Should produce reasonable estimates for exactly identified case
        let r_squared = iv.r_squared.unwrap();
        assert!(r_squared > 0.3); // Should have decent fit
    }

    #[test]
    fn test_iv_singular_matrix_handling() {
        let mut iv = IV::new(true);
        
        // Create singular instruments (linearly dependent columns)
        let instruments = array![
            [1.0, 2.0],  // Second column is 2x first
            [2.0, 4.0],
            [3.0, 6.0],
            [4.0, 8.0]
        ];
        
        let regressors = array![
            [1.1, 1.5],
            [2.1, 2.5],
            [3.1, 3.5],
            [4.1, 4.5]
        ];
        
        let targets = array![2.0, 4.0, 6.0, 8.0];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        // Should handle singular matrix gracefully
        if result.is_err() {
            let error_msg = result.unwrap_err();
            assert!(error_msg.contains("singular") || error_msg.contains("identification"));
        }
    }



    #[test]
    fn test_iv_perfect_instruments() {
        let mut iv = IV::new(true);
        
        // Create strongly correlated but well-conditioned instruments
        let instruments = array![
            [1.0, 3.0],
            [2.0, 1.0], 
            [3.0, 4.0],
            [4.0, 2.0],
            [5.0, 6.0],
            [6.0, 5.0]
        ];
        
        // Regressors correlated with instruments but not identical
        let regressors = array![
            [1.05, 3.02],
            [2.03, 1.01], 
            [2.98, 4.01],
            [4.02, 2.01],
            [4.97, 6.02],
            [6.01, 4.99]
        ];
        
        // Linear relationship: y = 1 + 2*x1 + 1.5*x2
        let targets = array![
            1.0 + 2.0 * 1.05 + 1.5 * 3.02,  // 7.63
            1.0 + 2.0 * 2.03 + 1.5 * 1.01,  // 6.575
            1.0 + 2.0 * 2.98 + 1.5 * 4.01,  // 12.975
            1.0 + 2.0 * 4.02 + 1.5 * 2.01,  // 12.055
            1.0 + 2.0 * 4.97 + 1.5 * 6.02,  // 19.97
            1.0 + 2.0 * 6.01 + 1.5 * 4.99   // 20.505
        ];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        if let Err(ref e) = result {
            println!("Error in perfect instruments test: {}", e);
        }
        assert!(result.is_ok());
        
        // With good instruments, should get reasonable estimates
        let coefficients = iv.coefficients.as_ref().unwrap();
        let intercept = iv.intercept.unwrap();
        
        // Check that estimates are in reasonable range
        assert!(intercept > -2.0 && intercept < 4.0, "Intercept should be reasonable, got {}", intercept);
        assert!(coefficients[0] > 0.5 && coefficients[0] < 4.0, "First coefficient should be reasonable, got {}", coefficients[0]);
        assert!(coefficients[1] > 0.5 && coefficients[1] < 3.0, "Second coefficient should be reasonable, got {}", coefficients[1]);
        
        // R-squared should be reasonably high
        let r_squared = iv.r_squared.unwrap();
        assert!(r_squared > 0.5, "R-squared should be reasonably high, got {}", r_squared);
    }

    #[test]
    fn test_iv_insufficient_samples() {
        let mut iv = IV::new(true);
        
        // Too few samples relative to parameters
        let instruments = array![[1.0, 0.5], [2.0, 1.0]];  // 2 samples
        let regressors = array![[1.1, 0.8], [2.1, 1.2]];   // 2 features + intercept = 3 params
        let targets = array![2.5, 4.2];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        // Should fail due to insufficient samples
        assert!(result.is_err());
    }

    #[test]
    fn test_iv_singular_matrix() {
        let mut iv = IV::new(true);
        
        // Create linearly dependent instruments
        let instruments = array![
            [1.0, 2.0],
            [2.0, 4.0],  // Second column is 2x first column
            [3.0, 6.0],
            [4.0, 8.0]
        ];
        
        let regressors = array![
            [1.1, 0.5],
            [2.1, 1.0],
            [3.1, 1.5],
            [4.1, 2.0]
        ];
        
        let targets = array![2.5, 4.2, 5.8, 7.1];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        // Should fail due to singular Z'X matrix
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("singular"));
    }

    #[test]
    fn test_iv_covariance_matrix() {
        let mut iv = IV::new(true);
        
        // Use well-conditioned instruments
        let instruments = array![
            [1.0, 3.0],
            [2.0, 1.0], 
            [3.0, 2.0],
            [4.0, 5.0],
            [5.0, 4.0]
        ];
        
        let regressors = array![
            [1.2, 3.1],
            [2.2, 1.1],
            [3.2, 2.2],
            [4.2, 5.1],
            [5.2, 4.1]
        ];
        
        let targets = array![3.0, 5.5, 8.0, 10.5, 13.0];
        
        iv.fit_impl(instruments.view(), regressors.view(), targets.view()).unwrap();
        
        // Check that covariance matrix exists and has correct dimensions
        let cov_matrix = iv.covariance_matrix.as_ref().unwrap();
        assert_eq!(cov_matrix.nrows(), 3); // 2 features + intercept
        assert_eq!(cov_matrix.ncols(), 3);
        
        // Covariance matrix should be symmetric
        for i in 0..cov_matrix.nrows() {
            for j in 0..cov_matrix.ncols() {
                let diff = (cov_matrix[[i, j]] - cov_matrix[[j, i]]).abs();
                assert!(diff < 1e-8, "Covariance matrix should be symmetric");
            }
        }
        
        // Diagonal elements should be positive (variances)
        for i in 0..cov_matrix.nrows() {
            assert!(cov_matrix[[i, i]] > 0.0);
        }
    }

    #[test]
    fn test_iv_edge_case_exact_identification() {
        let mut iv = IV::new(false); // No intercept for exact identification
        
        // Exactly identified case: 2 instruments for 2 regressors
        let instruments = array![
            [1.0, 0.0],
            [0.0, 1.0],
            [2.0, 0.5],
            [1.5, 2.0],
            [3.0, 1.0]
        ];
        
        let regressors = array![
            [1.1, 0.1],
            [0.1, 1.1],
            [2.1, 0.6],
            [1.6, 2.1],
            [3.1, 1.1]
        ];
        
        let targets = array![2.2, 2.2, 5.4, 5.4, 7.4];
        
        let result = iv.fit_impl(
            instruments.view(),
            regressors.view(),
            targets.view(),
        );
        
        assert!(result.is_ok());
        assert!(iv.fitted);
        assert!(iv.coefficients.is_some());
        assert_eq!(iv.coefficients.as_ref().unwrap().len(), 2);
    }


}
