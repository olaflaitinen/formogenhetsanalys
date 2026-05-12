"""Top-share estimation for the wealth distribution.

Provides point estimates, bootstrap confidence intervals, and Pareto-tail
fitting for the upper tail of the wealth distribution.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def top_share(
    wealth: np.ndarray[Any, np.dtype[np.float64]],
    q: float,
) -> float:
    """Compute the share of total wealth held by the top (1-q) fraction.

    Args:
        wealth: 1-D array of wealth values (non-negative). Negative values are
            treated as zero for the denominator but included as-is in the numerator.
        q: Quantile threshold. top_share(wealth, 0.99) gives the top-1-percent share.

    Returns:
        Float in [0, 1] representing the top-share of total wealth.

    Examples:
        >>> import numpy as np
        >>> w = np.array([1.0, 2.0, 3.0, 4.0, 10.0])
        >>> top_share(w, 0.8)
        0.5
    """
    if len(wealth) == 0:
        return 0.0
    w = np.asarray(wealth, dtype=np.float64)
    total = np.sum(np.maximum(w, 0.0))
    if total <= 0:
        return 0.0
    threshold = np.quantile(w, q)
    top_wealth = np.sum(w[w >= threshold])
    return float(top_wealth / total)


def top_shares_bootstrap(
    wealth: np.ndarray[Any, np.dtype[np.float64]],
    q_grid: list[float],
    n_boot: int = 1000,
    seed: int = 7,
) -> dict[float, dict[str, float]]:
    """Bootstrap confidence intervals for top shares at multiple quantile levels.

    Args:
        wealth: 1-D array of wealth values.
        q_grid: List of quantile thresholds (e.g. [0.99, 0.999]).
        n_boot: Number of bootstrap replications.
        seed: Random seed (BOOTSTRAP_SEED = 7).

    Returns:
        Dict mapping each q to a dict with keys 'point', 'ci_lo', 'ci_hi'.

    Examples:
        >>> import numpy as np
        >>> w = np.random.default_rng(0).lognormal(13, 2, 500)
        >>> result = top_shares_bootstrap(w, [0.99], n_boot=100, seed=7)
        >>> "point" in result[0.99]
        True
    """
    rng = np.random.default_rng(seed)
    w = np.asarray(wealth, dtype=np.float64)
    n = len(w)
    out: dict[float, dict[str, float]] = {}

    for q in q_grid:
        point = top_share(w, q)
        boot_shares = np.array(
            [top_share(rng.choice(w, size=n, replace=True), q) for _ in range(n_boot)],
        )
        out[q] = {
            "point": point,
            "ci_lo": float(np.percentile(boot_shares, 2.5)),
            "ci_hi": float(np.percentile(boot_shares, 97.5)),
        }

    return out


def pareto_tail(
    wealth: np.ndarray[Any, np.dtype[np.float64]],
    threshold: float,
) -> tuple[float, float]:
    """Fit a Pareto tail above the threshold using maximum-likelihood estimation.

    Args:
        wealth: 1-D array of wealth values.
        threshold: Minimum value for inclusion in the tail.

    Returns:
        Tuple (alpha, scale) where alpha is the Pareto tail index and scale
        is the minimum value estimate (equal to threshold).

    Raises:
        ValueError: If fewer than 2 observations exceed the threshold.

    Examples:
        >>> import numpy as np
        >>> rng = np.random.default_rng(0)
        >>> w = rng.pareto(1.5, size=1000) * 1e6 + 1e6
        >>> alpha, scale = pareto_tail(w, 1e6)
        >>> 1.0 < alpha < 3.0
        True
    """
    w = np.asarray(wealth, dtype=np.float64)
    tail = w[w >= threshold]
    if len(tail) < 2:
        msg = f"Need at least 2 observations above threshold {threshold}, got {len(tail)}"
        raise ValueError(msg)
    alpha_mle = float(len(tail) / np.sum(np.log(tail / threshold)))
    return alpha_mle, float(threshold)
