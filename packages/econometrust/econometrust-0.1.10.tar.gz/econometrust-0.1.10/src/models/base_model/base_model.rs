#[cfg(feature = "python")]
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
#[cfg(feature = "python")]
use pyo3::{PyResult, Python, Bound};

/// Base trait for all econometric models
#[cfg(feature = "python")]
pub trait BaseModel {
    /// Fit the model to training data
    fn fit(
        &mut self,
        x: PyReadonlyArray2<f64>,
        y: PyReadonlyArray1<f64>,
    ) -> PyResult<()>;
    
    /// Make predictions on new data
    fn predict<'py>(
        &self,
        py: Python<'py>,
        x: PyReadonlyArray2<f64>,
    ) -> PyResult<Bound<'py, PyArray1<f64>>>;
    
    /// Calculate standard errors of coefficients
    fn standard_errors<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>>;
    
    /// Calculate t-statistics for coefficients
    fn t_statistics<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>>;
    
    /// Calculate p-values for coefficients
    fn p_values<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Option<Bound<'py, PyArray1<f64>>>>;
    
    /// Calculate confidence intervals for coefficients
    fn confidence_intervals<'py>(
        &self,
        py: Python<'py>,
        alpha: Option<f64>,
    ) -> PyResult<Option<Bound<'py, PyArray2<f64>>>>;
    
    /// Generate a summary of the model results
    fn summary(&self) -> PyResult<String>;
}
