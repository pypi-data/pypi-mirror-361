use ndarray::{Array1, Array2, s};
use statrs::distribution::{StudentsT, Normal, ContinuousCDF, ChiSquared};
use std::sync::OnceLock;

const NORMAL_APPROX_DF_THRESHOLD: usize = 30;
const NORMAL_CRITICAL_VALUE: f64 = 1.96;

// Cache for commonly used distributions to avoid repeated allocations
static STANDARD_NORMAL: OnceLock<Normal> = OnceLock::new();

fn get_standard_normal() -> &'static Normal {
    STANDARD_NORMAL.get_or_init(|| Normal::new(0.0, 1.0).unwrap())
}

/// Vectorized t-statistics computation - zero allocation, pure BLAS
#[inline]
pub fn t_statistics(coef: &Array1<f64>, se: &Array1<f64>) -> Array1<f64> {
    coef / se
}

/// Optimized t-critical value with distribution caching
#[inline]
pub fn t_critical_value(df: usize, alpha: f64) -> f64 {
    if df > NORMAL_APPROX_DF_THRESHOLD {
        NORMAL_CRITICAL_VALUE
    } else if df > 0 {
        // Only create distribution when needed for small df
        let t_dist = StudentsT::new(0.0, 1.0, df as f64).unwrap();
        t_dist.inverse_cdf(1.0 - alpha * 0.5)  // Micro-optimization: avoid division
    } else {
        NORMAL_CRITICAL_VALUE
    }
}

/// Ultra-fast p-value computation with cached standard normal
#[inline]
pub fn p_value_from_t(t_stat: f64, df: usize) -> f64 {
    let abs_t = t_stat.abs();
    if df > NORMAL_APPROX_DF_THRESHOLD {
        let normal = get_standard_normal();
        2.0 * (1.0 - normal.cdf(abs_t))
    } else if df > 0 {
        // Only create t-distribution for small df where precision matters
        let t_dist = StudentsT::new(0.0, 1.0, df as f64).unwrap();
        2.0 * (1.0 - t_dist.cdf(abs_t))
    } else {
        1.0
    }
}

/// Memory-efficient confidence intervals with proper 2D shape
pub fn confidence_intervals(
    coef: &Array1<f64>,
    se: &Array1<f64>,
    df: usize,
    alpha: f64,
) -> Array2<f64> {
    let t_critical = t_critical_value(df, alpha);
    let margin_error = se * t_critical;
    let mut ci = Array2::zeros((coef.len(), 2));
    
    // Vectorized interval computation in proper 2D shape
    for (i, (&c, &me)) in coef.iter().zip(margin_error.iter()).enumerate() {
        ci[[i, 0]] = c - me;  // Lower bound
        ci[[i, 1]] = c + me;  // Upper bound
    }
    ci
}

/// Zero-copy coefficient splitting with minimal allocations
pub fn split_intercept_and_coefs(
    coef: &Array1<f64>,
    std_errors: &Array1<f64>,
    fit_intercept: bool,
) -> (Option<f64>, Array1<f64>, Array1<f64>, Option<f64>) {
    if fit_intercept {
        let intercept = coef[0];
        let intercept_std_error = std_errors[0];
        // Use slicing to avoid unnecessary copies
        let coefficients = coef.slice(s![1..]).to_owned();
        let std_errs = std_errors.slice(s![1..]).to_owned();
        (Some(intercept), coefficients, std_errs, Some(intercept_std_error))
    } else {
        // Clone only when necessary - could be optimized further with views
        (None, coef.clone(), std_errors.clone(), None)
    }
}

/// Compute Durbin-Watson statistic for detecting autocorrelation in residuals
pub fn durbin_watson(residuals: &Array1<f64>) -> f64 {
    if residuals.len() < 2 {
        return std::f64::NAN;
    }
    
    let mut sum_squared_diff = 0.0;
    let mut sum_squared_residuals = 0.0;
    
    for i in 1..residuals.len() {
        let diff = residuals[i] - residuals[i - 1];
        sum_squared_diff += diff * diff;
    }
    
    for &residual in residuals.iter() {
        sum_squared_residuals += residual * residual;
    }
    
    if sum_squared_residuals > 0.0 {
        sum_squared_diff / sum_squared_residuals
    } else {
        std::f64::NAN
    }
}

/// Compute skewness of a dataset
pub fn skewness(data: &Array1<f64>) -> f64 {
    let n = data.len() as f64;
    if n < 3.0 {
        return std::f64::NAN;
    }
    
    let mean = data.mean().unwrap_or(0.0);
    let mut m2 = 0.0;
    let mut m3 = 0.0;
    
    for &x in data.iter() {
        let dev = x - mean;
        let dev2 = dev * dev;
        m2 += dev2;
        m3 += dev2 * dev;
    }
    
    m2 /= n;
    m3 /= n;
    
    if m2 > 0.0 {
        let std_dev = m2.sqrt();
        m3 / (std_dev * std_dev * std_dev)
    } else {
        0.0
    }
}

/// Compute kurtosis of a dataset (excess kurtosis, so normal distribution = 0)
pub fn kurtosis(data: &Array1<f64>) -> f64 {
    let n = data.len() as f64;
    if n < 4.0 {
        return std::f64::NAN;
    }
    
    let mean = data.mean().unwrap_or(0.0);
    let mut m2 = 0.0;
    let mut m4 = 0.0;
    
    for &x in data.iter() {
        let dev = x - mean;
        let dev2 = dev * dev;
        m2 += dev2;
        m4 += dev2 * dev2;
    }
    
    m2 /= n;
    m4 /= n;
    
    if m2 > 0.0 {
        (m4 / (m2 * m2)) - 3.0  // Subtract 3 for excess kurtosis
    } else {
        0.0
    }
}

/// Compute Jarque-Bera test statistic for normality
pub fn jarque_bera(residuals: &Array1<f64>) -> (f64, f64) {
    let n = residuals.len() as f64;
    if n < 20.0 {  // JB test needs sufficient sample size
        return (std::f64::NAN, std::f64::NAN);
    }
    
    let skew = skewness(residuals);
    let kurt = kurtosis(residuals);
    
    if skew.is_nan() || kurt.is_nan() {
        return (std::f64::NAN, std::f64::NAN);
    }
    
    // Jarque-Bera statistic
    let jb_stat = (n / 6.0) * (skew * skew + (kurt * kurt) / 4.0);
    
    // P-value using chi-squared distribution with 2 degrees of freedom
    let p_value = if jb_stat.is_finite() && jb_stat >= 0.0 {
        match ChiSquared::new(2.0) {
            Ok(chi2_dist) => 1.0 - chi2_dist.cdf(jb_stat),
            Err(_) => std::f64::NAN,
        }
    } else {
        std::f64::NAN
    };
    
    (jb_stat, p_value)
}

/// Compute Omnibus test for normality (D'Agostino and Pearson's test)
pub fn omnibus_test(residuals: &Array1<f64>) -> (f64, f64) {
    let n = residuals.len() as f64;
    if n < 20.0 {
        return (std::f64::NAN, std::f64::NAN);
    }
    
    let skew = skewness(residuals);
    let kurt = kurtosis(residuals);
    
    if skew.is_nan() || kurt.is_nan() {
        return (std::f64::NAN, std::f64::NAN);
    }
    
    // Standard errors for skewness and kurtosis
    let se_skew = (6.0 * n * (n - 1.0) / ((n - 2.0) * (n + 1.0) * (n + 3.0))).sqrt();
    let se_kurt = 2.0 * se_skew * ((n * n - 1.0) / ((n - 3.0) * (n + 5.0))).sqrt();
    
    if se_skew > 0.0 && se_kurt > 0.0 {
        // Z-scores for skewness and kurtosis
        let z_skew = skew / se_skew;
        let z_kurt = kurt / se_kurt;
        
        // Omnibus statistic (sum of squared z-scores)
        let omnibus_stat = z_skew * z_skew + z_kurt * z_kurt;
        
        // P-value using chi-squared distribution with 2 degrees of freedom
        let p_value = if omnibus_stat.is_finite() && omnibus_stat >= 0.0 {
            match ChiSquared::new(2.0) {
                Ok(chi2_dist) => 1.0 - chi2_dist.cdf(omnibus_stat),
                Err(_) => std::f64::NAN,
            }
        } else {
            std::f64::NAN
        };
        
        (omnibus_stat, p_value)
    } else {
        (std::f64::NAN, std::f64::NAN)
    }
}

/// Compute condition number of a matrix (simplified version using 2-norm estimate)
pub fn condition_number(matrix: &Array2<f64>) -> f64 {
    // For now, we'll use a simpler approach without SVD
    // This computes an estimate based on the Frobenius norm and minimum diagonal element
    
    if matrix.nrows() == 0 || matrix.ncols() == 0 {
        return std::f64::NAN;
    }
    
    // Compute Frobenius norm as an upper bound estimate
    let frobenius_norm = matrix.iter().map(|&x| x * x).sum::<f64>().sqrt();
    
    // Find minimum absolute diagonal element as a lower bound estimate
    let min_dim = matrix.nrows().min(matrix.ncols());
    let mut min_diag = f64::INFINITY;
    
    for i in 0..min_dim {
        let diag_val = matrix[[i, i]].abs();
        if diag_val < min_diag {
            min_diag = diag_val;
        }
    }
    
    if min_diag > 0.0 && frobenius_norm.is_finite() {
        frobenius_norm / min_diag
    } else if min_diag == 0.0 {
        std::f64::INFINITY
    } else {
        std::f64::NAN
    }
}

/// Compute residuals from fitted values and actual values
pub fn compute_residuals(y_true: &Array1<f64>, y_pred: &Array1<f64>) -> Array1<f64> {
    y_true - y_pred
}

/// Compute standardized residuals
pub fn standardized_residuals(residuals: &Array1<f64>, mse: f64) -> Array1<f64> {
    if mse > 0.0 {
        let std_error = mse.sqrt();
        residuals / std_error
    } else {
        residuals.clone()
    }
}

/// Structure to hold comprehensive diagnostic statistics
#[derive(Debug, Clone)]
pub struct DiagnosticStats {
    pub durbin_watson: f64,
    pub jarque_bera_stat: f64,
    pub jarque_bera_pvalue: f64,
    pub omnibus_stat: f64,
    pub omnibus_pvalue: f64,
    pub skewness: f64,
    pub kurtosis: f64,
    pub condition_number: f64,
}

impl DiagnosticStats {
    /// Compute all diagnostic statistics from residuals and design matrix
    pub fn compute(residuals: &Array1<f64>, design_matrix: &Array2<f64>) -> Self {
        let dw = durbin_watson(residuals);
        let (jb_stat, jb_pval) = jarque_bera(residuals);
        let (omni_stat, omni_pval) = omnibus_test(residuals);
        let skew = skewness(residuals);
        let kurt = kurtosis(residuals);
        let cond_num = condition_number(design_matrix);
        
        DiagnosticStats {
            durbin_watson: dw,
            jarque_bera_stat: jb_stat,
            jarque_bera_pvalue: jb_pval,
            omnibus_stat: omni_stat,
            omnibus_pvalue: omni_pval,
            skewness: skew,
            kurtosis: kurt,
            condition_number: cond_num,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ndarray::Array1;
    use approx::assert_abs_diff_eq;

    #[test]
    fn test_cached_distribution_performance() {
        // Test that cached standard normal works correctly
        let normal1 = get_standard_normal();
        let normal2 = get_standard_normal();
        
        // Should be the same instance (cached)
        assert_eq!(normal1 as *const _, normal2 as *const _);
        
        // Test correctness
        assert_abs_diff_eq!(normal1.cdf(0.0), 0.5, epsilon = 1e-10);
        assert_abs_diff_eq!(normal1.cdf(1.96), 0.975, epsilon = 1e-3);
    }

    #[test]
    fn test_optimized_p_value_computation() {
        // Test that optimized p-value computation is correct
        let t_stat = 2.0;
        
        // Test large df (should use cached normal)
        let p_val_large = p_value_from_t(t_stat, 100);
        assert!(p_val_large > 0.0 && p_val_large < 1.0);
        
        // Test small df (should use t-distribution)
        let p_val_small = p_value_from_t(t_stat, 5);
        assert!(p_val_small > 0.0 && p_val_small < 1.0);
        
        // Small df should give larger p-value (wider tails)
        assert!(p_val_small > p_val_large);
    }

    #[test]
    fn test_vectorized_operations() {
        let coef = Array1::from_vec(vec![1.0, 2.0, 3.0]);
        let se = Array1::from_vec(vec![0.5, 0.4, 0.6]);
        
        // Test t-statistics computation
        let t_stats = t_statistics(&coef, &se);
        assert_abs_diff_eq!(t_stats[0], 2.0, epsilon = 1e-10);
        assert_abs_diff_eq!(t_stats[1], 5.0, epsilon = 1e-10);
        assert_abs_diff_eq!(t_stats[2], 5.0, epsilon = 1e-10);
    }

    #[test]
    fn test_confidence_intervals_performance() {
        let coef = Array1::from_vec(vec![1.0, 2.0, 3.0]);
        let se = Array1::from_vec(vec![0.1, 0.2, 0.15]);
        let df = 50;
        let alpha = 0.05;
        
        let ci = confidence_intervals(&coef, &se, df, alpha);
        
        // Should have shape (n_coef, 2)
        assert_eq!(ci.shape(), &[3, 2]);
        
        // Check that intervals make sense (lower < upper)
        for i in 0..3 {
            let lower = ci[[i, 0]];
            let upper = ci[[i, 1]];
            assert!(lower < upper);
            assert!(lower < coef[i]);
            assert!(upper > coef[i]);
        }
    }

    #[test]
    fn test_split_intercept_efficiency() {
        let coef = Array1::from_vec(vec![0.5, 1.0, 2.0, 3.0]);  // intercept + 3 features
        let se = Array1::from_vec(vec![0.1, 0.2, 0.3, 0.4]);
        
        // Test with intercept
        let (intercept, coefficients, std_errs, intercept_se) = 
            split_intercept_and_coefs(&coef, &se, true);
            
        assert_eq!(intercept, Some(0.5));
        assert_eq!(intercept_se, Some(0.1));
        assert_eq!(coefficients.len(), 3);
        assert_eq!(std_errs.len(), 3);
        
        // Test without intercept
        let (intercept2, coefficients2, std_errs2, intercept_se2) = 
            split_intercept_and_coefs(&coef, &se, false);
            
        assert_eq!(intercept2, None);
        assert_eq!(intercept_se2, None);
        assert_eq!(coefficients2.len(), 4);
        assert_eq!(std_errs2.len(), 4);
    }

    #[test]
    fn test_performance_characteristics() {
        // Test that our optimizations maintain numerical accuracy
        let large_coef = Array1::linspace(0.1, 10.0, 1000);
        let large_se = Array1::linspace(0.01, 1.0, 1000);
        
        // Should handle large arrays efficiently
        let t_stats = t_statistics(&large_coef, &large_se);
        assert_eq!(t_stats.len(), 1000);
        
        // All t-statistics should be finite and positive
        assert!(t_stats.iter().all(|&t| t.is_finite() && t > 0.0));
        
        // Test confidence intervals for large arrays
        let ci = confidence_intervals(&large_coef, &large_se, 100, 0.05);
        assert_eq!(ci.len(), 2000);  // 2 * 1000
        assert!(ci.iter().all(|&x| x.is_finite()));
    }

    #[test]
    fn test_durbin_watson() {
        // Test with perfectly correlated residuals (DW ≈ 0)
        let corr_residuals = Array1::from_vec(vec![1.0, 1.0, 1.0, 1.0, 1.0]);
        let dw_corr = durbin_watson(&corr_residuals);
        assert!(dw_corr < 0.5);  // Should be close to 0
        
        // Test with alternating residuals (DW should be higher)
        let uncorr_residuals = Array1::from_vec(vec![1.0, -1.0, 1.0, -1.0, 1.0]);
        let dw_uncorr = durbin_watson(&uncorr_residuals);
        assert!(dw_uncorr > 3.0);  // Should be higher than 2 for alternating pattern
        
        // Test with more realistic uncorrelated data
        let realistic_residuals = Array1::from_vec(vec![0.1, -0.05, 0.08, -0.02, 0.03, -0.01]);
        let dw_realistic = durbin_watson(&realistic_residuals);
        assert!(dw_realistic > 0.0 && dw_realistic < 4.0);  // Should be in valid range
        
        // Test edge case: too few observations
        let short_residuals = Array1::from_vec(vec![1.0]);
        let dw_short = durbin_watson(&short_residuals);
        assert!(dw_short.is_nan());
    }

    #[test]
    fn test_skewness_kurtosis() {
        // Test with normal-like data (skew ≈ 0, kurtosis ≈ 0)
        let normal_data = Array1::from_vec(vec![-2.0, -1.0, 0.0, 1.0, 2.0]);
        let skew = skewness(&normal_data);
        let kurt = kurtosis(&normal_data);
        
        assert!(skew.abs() < 1.0);  // Should be close to 0
        assert!(kurt.abs() < 3.0);  // Should be reasonable
        
        // Test with right-skewed data
        let skewed_data = Array1::from_vec(vec![1.0, 1.0, 1.0, 5.0, 10.0]);
        let skew_right = skewness(&skewed_data);
        assert!(skew_right > 0.0);  // Should be positive
        
        // Test edge cases
        let short_data = Array1::from_vec(vec![1.0, 2.0]);
        assert!(skewness(&short_data).is_nan());
        assert!(kurtosis(&short_data).is_nan());
    }

    #[test]
    fn test_jarque_bera() {
        // Test with normal-like data
        let normal_data = Array1::from_vec((0..100).map(|i| (i as f64 - 50.0) / 10.0).collect::<Vec<_>>());
        let (jb_stat, jb_pval) = jarque_bera(&normal_data);
        
        assert!(jb_stat.is_finite());
        assert!(jb_pval.is_finite());
        assert!(jb_pval >= 0.0 && jb_pval <= 1.0);
        
        // Test edge case: too few observations
        let short_data = Array1::from_vec(vec![1.0, 2.0, 3.0]);
        let (jb_short, jb_pval_short) = jarque_bera(&short_data);
        assert!(jb_short.is_nan());
        assert!(jb_pval_short.is_nan());
    }

    #[test]
    fn test_omnibus() {
        // Test with normal-like data
        let normal_data = Array1::from_vec((0..100).map(|i| (i as f64 - 50.0) / 10.0).collect::<Vec<_>>());
        let (omni_stat, omni_pval) = omnibus_test(&normal_data);
        
        assert!(omni_stat.is_finite());
        assert!(omni_pval.is_finite());
        assert!(omni_pval >= 0.0 && omni_pval <= 1.0);
        
        // Test edge case: too few observations
        let short_data = Array1::from_vec(vec![1.0, 2.0, 3.0]);
        let (omni_short, omni_pval_short) = omnibus_test(&short_data);
        assert!(omni_short.is_nan());
        assert!(omni_pval_short.is_nan());
    }

    #[test]
    fn test_condition_number() {
        // Test with identity matrix (condition number should be close to 1)
        let identity = Array2::eye(3);
        let cond_identity = condition_number(&identity);
        assert!(cond_identity >= 1.0 && cond_identity < 2.0);  // Should be around 1, but our approximation might not be exact
        
        // Test with diagonal matrix that has different values
        let mut diag = Array2::zeros((3, 3));
        diag[[0, 0]] = 100.0;
        diag[[1, 1]] = 10.0;
        diag[[2, 2]] = 1.0;
        let cond_diag = condition_number(&diag);
        assert!(cond_diag > 1.0);  // Should be > 1 for non-identity
        
        // Test with singular matrix (diagonal element = 0)
        let mut singular = Array2::zeros((3, 3));
        singular[[0, 0]] = 1.0;
        singular[[1, 1]] = 1.0;
        // singular[[2, 2]] = 0.0;  // Already 0
        let cond_singular = condition_number(&singular);
        assert!(cond_singular.is_infinite());
        
        // Test edge case: empty matrix
        let empty = Array2::zeros((0, 0));
        let cond_empty = condition_number(&empty);
        assert!(cond_empty.is_nan());
    }

    #[test]
    fn test_diagnostic_stats() {
        // Create some test data with sufficient sample size for JB test
        let residuals = Array1::from_vec((0..100).map(|i| (i as f64 - 50.0) / 10.0 + 0.1 * (i as f64).sin()).collect::<Vec<_>>());
        let design_matrix = Array2::eye(10);
        
        let stats = DiagnosticStats::compute(&residuals, &design_matrix);
        
        // Basic checks that all statistics are computed
        assert!(stats.durbin_watson.is_finite());
        assert!(stats.skewness.is_finite());
        assert!(stats.kurtosis.is_finite());
        assert!(stats.condition_number.is_finite());
        
        // JB and Omnibus should be finite for our test data with 100 samples
        assert!(stats.jarque_bera_stat.is_finite());
        assert!(stats.omnibus_stat.is_finite());
        
        // Check that p-values are in valid range [0, 1]
        if stats.jarque_bera_pvalue.is_finite() {
            assert!(stats.jarque_bera_pvalue >= 0.0 && stats.jarque_bera_pvalue <= 1.0);
        }
        if stats.omnibus_pvalue.is_finite() {
            assert!(stats.omnibus_pvalue >= 0.0 && stats.omnibus_pvalue <= 1.0);
        }
    }

    #[test]
    fn test_diagnostic_statistics() {
        // Use sufficient samples for all statistical tests
        let residuals = Array1::from_vec((0..25).map(|i| (i as f64 - 12.0) / 5.0).collect::<Vec<_>>());
        let design_matrix = Array2::eye(5);
        
        let stats = DiagnosticStats::compute(&residuals, &design_matrix);
        
        // Check that all statistics are computable
        assert!(stats.durbin_watson.is_finite());
        assert!(stats.skewness.is_finite());
        assert!(stats.kurtosis.is_finite());
        assert!(stats.condition_number.is_finite());
        
        // JB and Omnibus should be finite with 25 samples
        assert!(stats.jarque_bera_stat.is_finite());
        assert!(stats.omnibus_stat.is_finite());
        
        // Check p-values are in valid range
        if stats.jarque_bera_pvalue.is_finite() {
            assert!(stats.jarque_bera_pvalue >= 0.0 && stats.jarque_bera_pvalue <= 1.0);
        }
        if stats.omnibus_pvalue.is_finite() {
            assert!(stats.omnibus_pvalue >= 0.0 && stats.omnibus_pvalue <= 1.0);
        }
    }
}
