"""Posterior-predictive diagnostics for Bayesian wealth models."""

from __future__ import annotations

from typing import Any

import numpy as np


def posterior_predictive_intervals(
    posterior_samples: np.ndarray[Any, np.dtype[np.float64]],
    alpha: float = 0.05,
) -> tuple[np.ndarray[Any, np.dtype[np.float64]], np.ndarray[Any, np.dtype[np.float64]]]:
    """Compute posterior-predictive credible intervals from MCMC or VI samples.

    Args:
        posterior_samples: Array of shape (n_samples, n_variables) with
            posterior draws.
        alpha: Significance level; returns (alpha/2, 1-alpha/2) quantiles.

    Returns:
        Tuple (lo, hi) each of shape (n_variables,).

    Examples:
        >>> import numpy as np
        >>> s = np.random.default_rng(0).normal(0, 1, (1000, 5))
        >>> lo, hi = posterior_predictive_intervals(s)
        >>> lo.shape == (5,)
        True
    """
    samples = np.asarray(posterior_samples, dtype=np.float64)
    lo = np.percentile(samples, 100 * alpha / 2, axis=0)
    hi = np.percentile(samples, 100 * (1 - alpha / 2), axis=0)
    return lo, hi


def pit_histogram(
    true_values: np.ndarray[Any, np.dtype[np.float64]],
    posterior_samples: np.ndarray[Any, np.dtype[np.float64]],
    n_bins: int = 10,
) -> dict[str, Any]:
    """Compute Probability Integral Transform (PIT) histogram for calibration.

    For each observation, the PIT value is the fraction of posterior samples
    that are less than or equal to the true value. A well-calibrated model
    produces a uniform PIT distribution.

    Args:
        true_values: 1-D array of n observed values.
        posterior_samples: Array of shape (n_samples, n) with posterior draws.
        n_bins: Number of histogram bins.

    Returns:
        Dict with keys 'pit_values' (1-D), 'counts' (1-D), 'bin_edges' (1-D).

    Examples:
        >>> import numpy as np
        >>> true = np.array([0.5, 0.3, 0.8])
        >>> samples = np.random.default_rng(0).uniform(0, 1, (100, 3))
        >>> hist = pit_histogram(true, samples)
        >>> "pit_values" in hist
        True
    """
    tv = np.asarray(true_values, dtype=np.float64)
    ps = np.asarray(posterior_samples, dtype=np.float64)

    pit_vals = np.mean(ps <= tv[np.newaxis, :], axis=0)

    counts, bin_edges = np.histogram(pit_vals, bins=n_bins, range=(0.0, 1.0))

    return {
        "pit_values": pit_vals,
        "counts": counts,
        "bin_edges": bin_edges,
    }


def compute_coverage_and_width(
    true_values: np.ndarray[Any, np.dtype[np.float64]],
    posterior_samples: np.ndarray[Any, np.dtype[np.float64]],
    alpha: float = 0.05,
) -> dict[str, float]:
    """Compute credible-interval coverage and mean width from posterior samples.

    Args:
        true_values: 1-D array of n observed values.
        posterior_samples: Array of shape (n_samples, n).
        alpha: Significance level for the credible interval.

    Returns:
        Dict with keys 'coverage' and 'mean_width'.

    Examples:
        >>> import numpy as np
        >>> true = np.array([0.5, 0.3, 0.8])
        >>> samples = np.random.default_rng(0).uniform(0, 1, (1000, 3))
        >>> result = compute_coverage_and_width(true, samples)
        >>> 0.0 <= result["coverage"] <= 1.0
        True
    """
    from formogenhetsanalys.evaluation.metrics import coverage, interval_width

    lo, hi = posterior_predictive_intervals(posterior_samples, alpha)
    cov = coverage(true_values, lo, hi)
    width = interval_width(lo, hi)
    return {"coverage": cov, "mean_width": width}
