#[cfg(feature = "python")]
use pyo3::prelude::*;
pub mod models;

#[cfg(feature = "python")]
use models::linear::ols::OLS;
#[cfg(feature = "python")]
use models::linear::gls::GLS;
#[cfg(feature = "python")]
use models::linear::wls::WLS;
#[cfg(feature = "python")]
use models::linear::iv::IV;

/// Python module definition
#[cfg(feature = "python")]
#[pymodule]
fn econometrust(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add the OLS class
    m.add_class::<OLS>()?;
    // Add the GLS class
    m.add_class::<GLS>()?;
    // Add the WLS class
    m.add_class::<WLS>()?;
    // Add the IV class
    m.add_class::<IV>()?;
    
    Ok(())
}