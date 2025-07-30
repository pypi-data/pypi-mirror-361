"""Fast OLS and GLS regression library written in Rust with Python bindings."""

import numpy as np
from typing import Optional

class OLS:
    """Ordinary Least Squares regression.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model.
    robust : bool, default=False
        Whether to use heteroskedasticity-robust (White/HC0) standard errors.
    """

    def __init__(self, fit_intercept: bool = True, robust: bool = False) -> None: ...
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the OLS model.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training data.
        y : np.ndarray, shape (n_samples,)
            Target values.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model is fitted."""
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """Model coefficients. None if not fitted."""
        ...

    @property
    def intercept(self) -> Optional[float]:
        """Model intercept. None if not fitted or fit_intercept=False."""
        ...

    @property
    def fit_intercept(self) -> bool:
        """Whether to calculate the intercept for this model."""
        ...

    @property
    def robust(self) -> bool:
        """Whether to use robust standard errors."""
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using the fitted model.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Input data.

        Returns
        -------
        np.ndarray
            Predicted values.
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of the coefficients."""
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for the coefficients."""
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for the coefficients."""
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for the coefficients.

        Parameters
        ----------
        alpha : float, default=0.05
            Significance level (1 - alpha is the confidence level).

        Returns
        -------
        np.ndarray or None
            Array of shape (n_features, 2) with lower and upper bounds.
        """
        ...

    def summary(self) -> str:
        """Return a formatted summary of the regression results."""
        ...

    def covariance_matrix(self) -> Optional[np.ndarray]:
        """Covariance matrix of the coefficients."""
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error of the residuals."""
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """R-squared value."""
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """Residuals of the fitted model."""
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of samples."""
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of features."""
        ...

    def __repr__(self) -> str: ...

class GLS:
    """Generalized Least Squares regression.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model.
    """

    def __init__(self, fit_intercept: bool = True) -> None: ...
    def fit(self, X: np.ndarray, y: np.ndarray, sigma: np.ndarray) -> None:
        """Fit the GLS model.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training data.
        y : np.ndarray, shape (n_samples,)
            Target values.
        sigma : np.ndarray, shape (n_samples, n_samples)
            Covariance matrix of the residuals.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model is fitted."""
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """Model coefficients. None if not fitted."""
        ...

    @property
    def intercept(self) -> Optional[float]:
        """Model intercept. None if not fitted or fit_intercept=False."""
        ...

    @property
    def fit_intercept(self) -> bool:
        """Whether to calculate the intercept for this model."""
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using the fitted model.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Input data.

        Returns
        -------
        np.ndarray
            Predicted values.
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of the coefficients."""
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for the coefficients."""
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for the coefficients."""
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for the coefficients.

        Parameters
        ----------
        alpha : float, default=0.05
            Significance level (1 - alpha is the confidence level).

        Returns
        -------
        np.ndarray or None
            Array of shape (n_features, 2) with lower and upper bounds.
        """
        ...

    def summary(self) -> str:
        """Return a formatted summary of the regression results."""
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error of the residuals."""
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """R-squared value."""
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """Residuals of the fitted model."""
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of samples."""
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of features."""
        ...

    def __repr__(self) -> str: ...

class WLS:
    """Weighted Least Squares regression.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model.
    """

    def __init__(self, fit_intercept: bool = True) -> None: ...
    def fit(self, X: np.ndarray, y: np.ndarray, weights: np.ndarray) -> None:
        """Fit the WLS model.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training data.
        y : np.ndarray, shape (n_samples,)
            Target values.
        weights : np.ndarray, shape (n_samples,)
            Sample weights. Must be positive.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model is fitted."""
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """Model coefficients. None if not fitted."""
        ...

    @property
    def intercept(self) -> Optional[float]:
        """Model intercept. None if not fitted or fit_intercept=False."""
        ...

    @property
    def fit_intercept(self) -> bool:
        """Whether to calculate the intercept for this model."""
        ...

    @property
    def weights(self) -> Optional[np.ndarray]:
        """Sample weights used for fitting. None if not fitted."""
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using the fitted model.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Input data.

        Returns
        -------
        np.ndarray
            Predicted values.
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of the coefficients."""
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for the coefficients."""
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for the coefficients."""
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for the coefficients.

        Parameters
        ----------
        alpha : float, default=0.05
            Significance level (1 - alpha is the confidence level).

        Returns
        -------
        np.ndarray or None
            Array of shape (n_features, 2) with lower and upper bounds.
        """
        ...

    def summary(self) -> str:
        """Return a formatted summary of the regression results."""
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error of the residuals."""
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """R-squared value."""
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """Residuals of the fitted model."""
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of samples."""
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of features."""
        ...

    def __repr__(self) -> str: ...

class IV:
    """Instrumental Variables regression for exactly identified models.

    The IV estimator is used when regressors are endogenous (correlated with
    the error term). It uses instrumental variables to obtain consistent
    estimates of the parameters.

    This implementation handles exactly identified models where the number of
    instruments equals the number of regressors. For overidentified cases
    (more instruments than regressors), use TSLS estimator instead.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model.

    Notes
    -----
    The IV estimator requires:
    - Strong instruments: instruments must be correlated with regressors
    - Valid instruments: instruments must be uncorrelated with error term
    - Exact identification: number of instruments = number of regressors

    IV estimates generally have higher variance than OLS, requiring larger
    sample sizes for reliable inference.
    """

    def __init__(self, fit_intercept: bool = True) -> None: ...
    def fit(
        self, instruments: np.ndarray, regressors: np.ndarray, targets: np.ndarray
    ) -> None:
        """Fit the IV model for exactly identified case.

        Parameters
        ----------
        instruments : np.ndarray, shape (n_samples, n_instruments)
            Instrumental variables. Must have same number of columns as regressors.
        regressors : np.ndarray, shape (n_samples, n_features)
            Endogenous regressors (variables correlated with error term).
        targets : np.ndarray, shape (n_samples,)
            Target values (dependent variable).

        Raises
        ------
        ValueError
            If number of instruments != number of regressors (not exactly identified).
            If insufficient samples or mismatched dimensions.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model is fitted."""
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """Model coefficients. None if not fitted."""
        ...

    @property
    def intercept(self) -> Optional[float]:
        """Model intercept. None if not fitted or fit_intercept=False."""
        ...

    @property
    def fit_intercept(self) -> bool:
        """Whether to calculate the intercept for this model."""
        ...

    @property
    def instruments(self) -> Optional[np.ndarray]:
        """Instrumental variables used for fitting. None if not fitted."""
        ...

    @property
    def regressors(self) -> Optional[np.ndarray]:
        """Regressors used for fitting. None if not fitted."""
        ...

    def predict(self, regressors: np.ndarray) -> np.ndarray:
        """Make predictions using the fitted model.

        Parameters
        ----------
        regressors : np.ndarray, shape (n_samples, n_features)
            Input data.

        Returns
        -------
        np.ndarray
            Predicted values.
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of the coefficients."""
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for the coefficients."""
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for the coefficients."""
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for the coefficients.

        Parameters
        ----------
        alpha : float, default=0.05
            Significance level (1 - alpha is the confidence level).

        Returns
        -------
        np.ndarray or None
            Array of shape (n_features, 2) with lower and upper bounds.
        """
        ...

    def summary(self) -> str:
        """Return a formatted summary of the regression results."""
        ...

    def covariance_matrix(self) -> Optional[np.ndarray]:
        """Covariance matrix of the coefficients."""
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error of the residuals."""
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """R-squared value."""
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """Residuals of the fitted model."""
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of samples."""
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of features."""
        ...

    def __repr__(self) -> str: ...
