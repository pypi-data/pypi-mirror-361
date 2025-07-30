"""
Test configuration and fixtures for econometrust
"""

import pytest
import numpy as np
import econometrust
from typing import Tuple, Generator


@pytest.fixture
def random_seed() -> Generator[None, None, None]:
    """Set random seed for reproducible tests."""
    np.random.seed(42)
    yield
    np.random.seed()  # Reset


@pytest.fixture
def small_dataset() -> Tuple[np.ndarray, np.ndarray]:
    """Small dataset for basic functionality tests."""
    np.random.seed(42)
    n_samples, n_features = 100, 3
    X = np.random.randn(n_samples, n_features).astype(np.float64, order="C")
    true_coef = np.array([1.5, -2.0, 0.5])
    true_intercept = 10.0
    y = X @ true_coef + true_intercept + 0.1 * np.random.randn(n_samples)
    return X, y.astype(np.float64)


@pytest.fixture
def medium_dataset() -> Tuple[np.ndarray, np.ndarray]:
    """Medium dataset for performance tests."""
    np.random.seed(123)
    n_samples, n_features = 5000, 10
    X = np.random.randn(n_samples, n_features).astype(np.float64, order="C")
    true_coef = np.random.randn(n_features)
    true_intercept = 5.0
    y = X @ true_coef + true_intercept + 0.2 * np.random.randn(n_samples)
    return X, y.astype(np.float64)


@pytest.fixture
def large_dataset() -> Tuple[np.ndarray, np.ndarray]:
    """Large dataset for stress testing."""
    np.random.seed(456)
    n_samples, n_features = 50000, 20
    X = np.random.randn(n_samples, n_features).astype(np.float64, order="C")
    true_coef = np.random.randn(n_features) * 0.5
    true_intercept = -2.0
    y = X @ true_coef + true_intercept + 0.5 * np.random.randn(n_samples)
    return X, y.astype(np.float64)


@pytest.fixture
def perfect_data() -> Tuple[np.ndarray, np.ndarray]:
    """Perfect linear relationship for exact tests."""
    np.random.seed(789)
    n_samples, n_features = 200, 5
    X = np.random.randn(n_samples, n_features).astype(np.float64, order="C")
    true_coef = np.array([2.0, -1.5, 3.0, 0.8, -0.3])
    true_intercept = 7.5
    y = X @ true_coef + true_intercept  # No noise
    return X, y.astype(np.float64)


@pytest.fixture
def heteroscedastic_sigma() -> np.ndarray:
    """Heteroscedastic covariance matrix for GLS tests."""
    n = 100
    # Create diagonal matrix with varying variances
    variances = np.linspace(0.5, 2.0, n)
    sigma = np.diag(variances).astype(np.float64, order="C")
    return sigma


@pytest.fixture
def autocorrelated_sigma() -> np.ndarray:
    """Autocorrelated covariance matrix for GLS tests."""
    n = 50
    rho = 0.7
    sigma = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            sigma[i, j] = rho ** abs(i - j)
    return sigma.astype(np.float64, order="C")


@pytest.fixture
def ill_conditioned_data() -> Tuple[np.ndarray, np.ndarray]:
    """Ill-conditioned data to test SVD fallback."""
    np.random.seed(999)
    n_samples, n_features = 100, 5
    X = np.random.randn(n_samples, n_features).astype(np.float64, order="C")
    # Make columns nearly linearly dependent
    X[:, 1] = X[:, 0] + 1e-10 * np.random.randn(n_samples)
    X[:, 2] = 0.5 * X[:, 0] + 0.5 * X[:, 3] + 1e-12 * np.random.randn(n_samples)

    true_coef = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = X @ true_coef + 0.01 * np.random.randn(n_samples)
    return X, y.astype(np.float64)


# Performance timing fixture
@pytest.fixture
def benchmark_timer():
    """Simple timer for performance benchmarks."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.perf_counter()
            return self

        def stop(self):
            self.end_time = time.perf_counter()
            return self.elapsed()

        def elapsed(self):
            if self.start_time is None:
                return 0.0
            end = self.end_time if self.end_time else time.perf_counter()
            return end - self.start_time

    return Timer()


# Tolerance settings for numerical comparisons
RTOL = 1e-10  # Relative tolerance
ATOL = 1e-12  # Absolute tolerance
LOOSE_RTOL = 1e-6  # For less precise comparisons
LOOSE_ATOL = 1e-8  # For less precise comparisons
