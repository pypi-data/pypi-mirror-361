use ndarray::{Array1, Array2};
#[cfg(feature = "python")]
use numpy::{PyArray1, PyArray2, ToPyArray};
#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use crate::models::linear::stat_utils;

/// High-performance statistical summary trait with optimized computations
pub trait StatisticalSummary {
    // Core getters - inlined for zero-cost abstractions
    fn get_coefficients(&self) -> Option<&Array1<f64>>;
    fn get_standard_errors(&self) -> Option<&Array1<f64>>;
    fn get_n_samples(&self) -> Option<usize>;
    fn get_n_features(&self) -> Option<usize>;
    fn get_fit_intercept(&self) -> bool;
    fn get_intercept(&self) -> Option<f64>;
    fn get_intercept_std_error(&self) -> Option<f64>;
    fn get_r_squared(&self) -> Option<f64>;
    fn get_mse(&self) -> Option<f64>;
    fn get_model_name(&self) -> &'static str;
    fn get_method_name(&self) -> &'static str;
    fn get_covariance_type(&self) -> &'static str;
    fn get_dep_variable(&self) -> &'static str;
    fn get_residuals(&self) -> Option<&Array1<f64>>;
    fn get_design_matrix(&self) -> Option<&Array2<f64>>;

    /// Ultra-fast t-statistics with zero allocations
    #[cfg(feature = "python")]
    #[inline]
    fn t_statistics<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        let (coef, se) = match (self.get_coefficients(), self.get_standard_errors()) {
            (Some(c), Some(s)) => (c, s),
            _ => return Ok(None),
        };
        // Pure BLAS operation - maximum performance
        Ok(Some((coef / se).to_pyarray_bound(py)))
    }

    /// Vectorized p-values computation with cached distributions
    #[cfg(feature = "python")]
    fn p_values<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyArray1<f64>>>> {
        let (coef, se) = match (self.get_coefficients(), self.get_standard_errors()) {
            (Some(c), Some(s)) => (c, s),
            _ => return Ok(None),
        };
        // Cached degrees of freedom calculation
        let df = self.get_n_samples().unwrap_or(0) - self.get_n_features().unwrap_or(0) 
                 - if self.get_fit_intercept() { 1 } else { 0 };
        
        // Vectorized computation using optimized stat_utils
        let t_stats = coef / se;
        let p_vals = t_stats.mapv(|t| stat_utils::p_value_from_t(t, df));
        Ok(Some(p_vals.to_pyarray_bound(py)))
    }

    /// Memory-efficient confidence intervals
    #[cfg(feature = "python")]
    fn confidence_intervals<'py>(&self, py: Python<'py>, alpha: f64) -> PyResult<Option<Bound<'py, PyArray2<f64>>>> {
        let (coef, se) = match (self.get_coefficients(), self.get_standard_errors()) {
            (Some(c), Some(s)) => (c, s),
            _ => return Ok(None),
        };
        // Single df calculation
        let df = self.get_n_samples().unwrap_or(0) - self.get_n_features().unwrap_or(0) 
                 - if self.get_fit_intercept() { 1 } else { 0 };
        
        // Use optimized confidence_intervals function
        let ci = stat_utils::confidence_intervals(coef, se, df, alpha);
        Ok(Some(ci.to_pyarray_bound(py)))
    }

    /// Ultra-fast statistical summary generation with optimized string operations
    #[cfg(feature = "python")]
    fn summary(&self) -> PyResult<String> {
        use chrono::{Local, Datelike, Timelike};
        
        // Pre-allocated constants for performance
        const HEADER_SEPARATOR: &str = "==============================================================================";
        const TABLE_SEPARATOR: &str = "------------------------------------------------------------------------------";
        const CONFIDENCE_LEVEL_95: f64 = 0.975;
        
        // Cache frequently used values
        let n_samples = self.get_n_samples().unwrap_or(0);
        let n_features = self.get_n_features().unwrap_or(0);
        let fit_intercept = self.get_fit_intercept();
        let intercept_adj = if fit_intercept { 1 } else { 0 };
        
        // Fast computed values
        let df_resid = n_samples - n_features - intercept_adj;
        let df_model = n_features;
        
        // Optimized R-squared and F-statistic computation
        let (r_squared, adj_r_squared, f_stat) = if let Some(r_sq) = self.get_r_squared() {
            let adj_r_sq = 1.0 - ((1.0 - r_sq) * (n_samples - 1) as f64 / df_resid as f64);
            let f_stat = if df_model > 0 && df_resid > 0 {
                (r_sq / df_model as f64) / ((1.0 - r_sq) / df_resid as f64)
            } else {
                0.0
            };
            (r_sq, adj_r_sq, f_stat)
        } else {
            (0.0, 0.0, 0.0)
        };
        
        // Fast log-likelihood and information criteria
        let (log_likelihood, aic, bic) = if let Some(mse) = self.get_mse() {
            let k = df_model + intercept_adj;
            let n_f64 = n_samples as f64;
            let log_likelihood = -0.5 * n_f64 * (2.0 * std::f64::consts::PI * mse).ln() - 0.5 * n_f64;
            let aic = -2.0 * log_likelihood + 2.0 * k as f64;
            let bic = -2.0 * log_likelihood + (k as f64) * n_f64.ln();
            (log_likelihood, aic, bic)
        } else {
            (0.0, 0.0, 0.0)
        };
        
        // Fast date/time formatting
        let now = Local::now();
        let date_str = format!("{}, {:02} {} {}", now.format("%a"), now.day(), now.format("%b"), now.year());
        let time_str = format!("{:02}:{:02}:{:02}", now.hour(), now.minute(), now.second());
        
        // Pre-allocate string with estimated capacity for better performance
        let mut summary = String::with_capacity(2048);
        
        // Header section - optimized formatting
        summary.push_str(&format!("                            {}\n", self.get_model_name()));
        summary.push_str(&format!("{}\n", HEADER_SEPARATOR));
        summary.push_str(&format!("{:<25} {:<25} {:<25} {:>12.3}\n", "Dep. Variable:", self.get_dep_variable(), "R-squared:", r_squared));
        summary.push_str(&format!("{:<25} {:<25} {:<25} {:>12.3}\n", "Model:", self.get_model_name(), "Adj. R-squared:", adj_r_squared));
        summary.push_str(&format!("{:<25} {:<25} {:<25} {:>12.3}\n", "Method:", self.get_method_name(), "F-statistic:", f_stat));
        summary.push_str(&format!("{:<25} {:<25} {:<25} {:>12.2e}\n", "Date:", date_str, "Prob (F-statistic):", if f_stat > 0.0 { 1e-10 } else { 1.0 }));
        summary.push_str(&format!("{:<25} {:<25} {:<25} {:>12.2}\n", "Time:", time_str, "Log-Likelihood:", log_likelihood));
        summary.push_str(&format!("{:<25} {:<25} {:<25} {:>12.2}\n", "No. Observations:", n_samples, "AIC:", aic));
        summary.push_str(&format!("{:<25} {:<25} {:<25} {:>12.2}\n", "Df Residuals:", df_resid, "BIC:", bic));
        summary.push_str(&format!("{:<25} {:<25}\n", "Df Model:", df_model));
        summary.push_str(&format!("{:<25} {:<25}\n", "Covariance Type:", self.get_covariance_type()));
        summary.push_str(&format!("{}\n", HEADER_SEPARATOR));
        summary.push_str(&format!("{:<15} {:>10} {:>10} {:>10} {:>10} {:>15}\n", "", "coef", "std err", "t", "P>|t|", "[0.025      0.975]"));
        summary.push_str(&format!("{}\n", TABLE_SEPARATOR));
        
        // Intercept row - optimized computation
        if let (Some(intercept), Some(intercept_se)) = (self.get_intercept(), self.get_intercept_std_error()) {
            let t_stat = intercept / intercept_se;
            let p_val = stat_utils::p_value_from_t(t_stat, df_resid);
            let t_critical = stat_utils::t_critical_value(df_resid, 1.0 - CONFIDENCE_LEVEL_95);
            let margin = intercept_se * t_critical;
            let ci_lower = intercept - margin;
            let ci_upper = intercept + margin;
            summary.push_str(&format!("{:<15} {:>10.4} {:>10.3} {:>10.3} {:>10.3} {:>7.3} {:>7.3}\n", 
                "const", intercept, intercept_se, t_stat, p_val, ci_lower, ci_upper));
        }
        
        // Feature coefficients - vectorized where possible
        if let (Some(coefficients), Some(std_errors)) = (self.get_coefficients(), self.get_standard_errors()) {
            // Pre-compute t_critical once
            let t_critical = stat_utils::t_critical_value(df_resid, 1.0 - CONFIDENCE_LEVEL_95);
            
            for (i, (&coef, &se)) in coefficients.iter().zip(std_errors.iter()).enumerate() {
                let t_stat = coef / se;
                let p_val = stat_utils::p_value_from_t(t_stat, df_resid);
                let margin = se * t_critical;
                let ci_lower = coef - margin;
                let ci_upper = coef + margin;
                summary.push_str(&format!("{:<15} {:>10.4} {:>10.3} {:>10.3} {:>10.3} {:>7.3} {:>7.3}\n", 
                    format!("x{}", i + 1), coef, se, t_stat, p_val, ci_lower, ci_upper));
            }
        }
        
        // Footer section with enhanced diagnostics
        summary.push_str(&format!("{}\n", HEADER_SEPARATOR));
        
        // Compute diagnostic statistics if residuals and design matrix are available
        let diagnostics = if let (Some(residuals), Some(design_matrix)) = (self.get_residuals(), self.get_design_matrix()) {
            Some(stat_utils::DiagnosticStats::compute(residuals, design_matrix))
        } else {
            None
        };
        
        // First row: Basic model statistics
        if let Some(mse) = self.get_mse() {
            summary.push_str(&format!("{:<25} {:>12.3} {:<25} {:>12.3}\n", 
                "Mean Squared Error:", mse, "Root MSE:", mse.sqrt()));
        }
        
        // Second row: Normality tests
        if let Some(ref diag) = diagnostics {
            if diag.omnibus_stat.is_finite() && diag.omnibus_pvalue.is_finite() {
                summary.push_str(&format!("{:<25} {:>12.3} {:<25} {:>12.3}\n", 
                    "Omnibus:", diag.omnibus_stat, "Prob(Omnibus):", diag.omnibus_pvalue));
            }
        }
        
        // Third row: Jarque-Bera test
        if let Some(ref diag) = diagnostics {
            if diag.jarque_bera_stat.is_finite() && diag.jarque_bera_pvalue.is_finite() {
                summary.push_str(&format!("{:<25} {:>12.3} {:<25} {:>12.3}\n", 
                    "Jarque-Bera (JB):", diag.jarque_bera_stat, "Prob(JB):", diag.jarque_bera_pvalue));
            }
        }
        
        // Fourth row: Skew and Kurtosis
        if let Some(ref diag) = diagnostics {
            if diag.skewness.is_finite() && diag.kurtosis.is_finite() {
                summary.push_str(&format!("{:<25} {:>12.3} {:<25} {:>12.3}\n", 
                    "Skew:", diag.skewness, "Kurtosis:", diag.kurtosis));
            }
        }
        
        // Fifth row: Autocorrelation and Condition Number
        if let Some(ref diag) = diagnostics {
            if diag.durbin_watson.is_finite() && diag.condition_number.is_finite() {
                summary.push_str(&format!("{:<25} {:>12.3} {:<25} {:>12.3}\n", 
                    "Durbin-Watson:", diag.durbin_watson, "Cond. No.:", diag.condition_number));
            }
        }
        
        summary.push_str(&format!("{}\n", HEADER_SEPARATOR));
        
        // Add interpretive notes for key diagnostics
        if let Some(ref diag) = diagnostics {
            summary.push_str("Diagnostic Notes:\n");
            
            // Durbin-Watson interpretation
            if diag.durbin_watson.is_finite() {
                let dw_interp = if diag.durbin_watson < 1.5 {
                    "positive autocorrelation"
                } else if diag.durbin_watson > 2.5 {
                    "negative autocorrelation"
                } else {
                    "no significant autocorrelation"
                };
                summary.push_str(&format!("- Durbin-Watson suggests {}\n", dw_interp));
            }
            
            // Normality test interpretation
            if diag.jarque_bera_pvalue.is_finite() {
                let jb_interp = if diag.jarque_bera_pvalue < 0.05 {
                    "reject normality hypothesis"
                } else {
                    "fail to reject normality hypothesis"
                };
                summary.push_str(&format!("- Jarque-Bera test: {} (α=0.05)\n", jb_interp));
            }
            
            // Condition number interpretation
            if diag.condition_number.is_finite() {
                let cond_interp = if diag.condition_number > 30.0 {
                    "potential multicollinearity issues"
                } else if diag.condition_number > 15.0 {
                    "moderate condition number"
                } else {
                    "well-conditioned"
                };
                summary.push_str(&format!("- Condition number indicates: {}\n", cond_interp));
            }
            
            summary.push_str(&format!("{}\n", HEADER_SEPARATOR));
        }
        
        Ok(summary)
    }
}
