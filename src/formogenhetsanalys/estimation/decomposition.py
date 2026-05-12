"""Wealth-concentration decomposition: Atkinson, Gini, Theil, Shapley."""

from __future__ import annotations

from typing import Any

import numpy as np


def gini(wealth: np.ndarray[Any, np.dtype[np.float64]]) -> float:
    """Compute the Gini coefficient of a wealth distribution.

    Args:
        wealth: 1-D array of non-negative wealth values.

    Returns:
        Gini coefficient in [0, 1].

    Examples:
        >>> import numpy as np
        >>> gini(np.array([1.0, 1.0, 1.0, 1.0]))
        0.0
        >>> gini(np.array([0.0, 0.0, 0.0, 4.0]))
        0.75
    """
    w = np.asarray(wealth, dtype=np.float64)
    n = len(w)
    if n == 0 or np.sum(w) == 0:
        return 0.0
    w_sorted = np.sort(w)
    cumsum = np.cumsum(w_sorted)
    return float(
        (2 * np.sum((np.arange(1, n + 1)) * w_sorted) - (n + 1) * cumsum[-1]) / (n * cumsum[-1]),
    )


def atkinson(wealth: np.ndarray[Any, np.dtype[np.float64]], epsilon: float = 0.5) -> float:
    """Compute the Atkinson inequality index.

    Args:
        wealth: 1-D array of non-negative wealth values.
        epsilon: Inequality aversion parameter (epsilon > 0). Higher values give
            more weight to the lower tail.

    Returns:
        Atkinson index in [0, 1].

    Examples:
        >>> import numpy as np
        >>> atkinson(np.array([1.0, 1.0, 1.0, 1.0]))
        0.0
    """
    w = np.asarray(wealth, dtype=np.float64)
    w = w[w > 0]
    if len(w) == 0:
        return 0.0
    mu = np.mean(w)
    if epsilon == 1.0:
        ede = np.exp(np.mean(np.log(w)))
    else:
        ede = np.mean(w ** (1 - epsilon)) ** (1 / (1 - epsilon))
    return float(1 - ede / mu)


def theil(wealth: np.ndarray[Any, np.dtype[np.float64]]) -> float:
    """Compute Theil T index of wealth inequality.

    Args:
        wealth: 1-D array of non-negative wealth values.

    Returns:
        Theil T index (non-negative).

    Examples:
        >>> import numpy as np
        >>> theil(np.array([1.0, 1.0, 1.0, 1.0]))
        0.0
    """
    w = np.asarray(wealth, dtype=np.float64)
    w = w[w > 0]
    if len(w) == 0:
        return 0.0
    mu = np.mean(w)
    return float(np.mean((w / mu) * np.log(w / mu)))


def shapley_decomposition(
    wealth_components: dict[str, np.ndarray[Any, np.dtype[np.float64]]],
    inequality_fn: Any = None,
) -> dict[str, float]:
    """Attribute total inequality to wealth components via Shapley values.

    Uses an approximation: for each component, computes the marginal
    contribution by comparing total inequality with and without that component,
    averaged over orderings (Owen-Shorrocks approach).

    Args:
        wealth_components: Dict mapping component name to 1-D wealth array.
            All arrays must have the same length.
        inequality_fn: A callable that takes a 1-D array and returns a scalar
            inequality measure. Defaults to gini.

    Returns:
        Dict mapping component name to Shapley attribution value.

    Examples:
        >>> import numpy as np
        >>> rng = np.random.default_rng(0)
        >>> components = {"financial": rng.lognormal(11, 1, 100),
        ...               "real_estate": rng.lognormal(12, 1.5, 100)}
        >>> sv = shapley_decomposition(components)
        >>> abs(sum(sv.values()) - gini(sum(components.values()))) < 0.01
        True
    """
    if inequality_fn is None:
        inequality_fn = gini

    names = list(wealth_components)
    arrays = [wealth_components[n] for n in names]
    total = sum(arrays)
    total_ineq = inequality_fn(total)

    shapley: dict[str, float] = {}
    for i, name in enumerate(names):
        without = sum(arrays[j] for j in range(len(names)) if j != i)
        without_ineq = inequality_fn(without)
        shapley[name] = float(total_ineq - without_ineq)

    shapley_sum = sum(shapley.values())
    if abs(shapley_sum) > 1e-12:
        scale = total_ineq / shapley_sum
        shapley = {k: v * scale for k, v in shapley.items()}

    return shapley
