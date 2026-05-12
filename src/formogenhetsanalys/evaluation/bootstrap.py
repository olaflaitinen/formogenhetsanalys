"""Block bootstrap and jackknife for top-share sensitivity analysis."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np


def block_bootstrap(
    wealth: np.ndarray[Any, np.dtype[np.float64]],
    statistic_fn: Callable[[np.ndarray[Any, np.dtype[np.float64]]], float],
    n_boot: int = 1000,
    block_size: int = 50,
    seed: int = 7,
) -> dict[str, float]:
    """Block bootstrap for a scalar statistic over a wealth distribution.

    Block bootstrap is preferable to IID bootstrap when households are
    spatially or temporally clustered.

    Args:
        wealth: 1-D array of wealth values.
        statistic_fn: Function that takes a 1-D wealth array and returns a float.
        n_boot: Number of bootstrap replications.
        block_size: Number of observations per block.
        seed: Random seed (BOOTSTRAP_SEED = 7).

    Returns:
        Dict with keys 'point', 'ci_lo', 'ci_hi', 'se'.

    Examples:
        >>> import numpy as np
        >>> w = np.random.default_rng(0).lognormal(13, 2, 500)
        >>> from formogenhetsanalys.estimation.top_shares import top_share
        >>> result = block_bootstrap(w, lambda x: top_share(x, 0.99), n_boot=50, seed=7)
        >>> "point" in result
        True
    """
    rng = np.random.default_rng(seed)
    w = np.asarray(wealth, dtype=np.float64)
    n = len(w)
    point = statistic_fn(w)

    n_blocks = int(np.ceil(n / block_size))
    boot_stats = []
    for _ in range(n_boot):
        block_starts = rng.integers(0, max(1, n - block_size + 1), size=n_blocks)
        sample_idx = np.concatenate(
            [np.arange(bs, min(bs + block_size, n)) for bs in block_starts],
        )[:n]
        boot_stats.append(statistic_fn(w[sample_idx]))

    boot_arr = np.array(boot_stats)
    return {
        "point": point,
        "ci_lo": float(np.percentile(boot_arr, 2.5)),
        "ci_hi": float(np.percentile(boot_arr, 97.5)),
        "se": float(np.std(boot_arr)),
    }


def jackknife(
    wealth: np.ndarray[Any, np.dtype[np.float64]],
    statistic_fn: Callable[[np.ndarray[Any, np.dtype[np.float64]]], float],
) -> dict[str, float]:
    """Delete-one jackknife for bias and variance estimation.

    Args:
        wealth: 1-D array of wealth values.
        statistic_fn: Function that takes a 1-D array and returns a float.

    Returns:
        Dict with keys 'point', 'bias', 'se', 'ci_lo', 'ci_hi'.

    Examples:
        >>> import numpy as np
        >>> w = np.arange(1.0, 21.0)
        >>> from formogenhetsanalys.estimation.top_shares import top_share
        >>> result = jackknife(w, lambda x: top_share(x, 0.9))
        >>> "bias" in result
        True
    """
    w = np.asarray(wealth, dtype=np.float64)
    n = len(w)
    point = statistic_fn(w)

    jack_stats = np.array(
        [statistic_fn(np.delete(w, i)) for i in range(n)],
    )
    jack_mean = np.mean(jack_stats)
    bias = (n - 1) * (jack_mean - point)
    se = float(np.sqrt((n - 1) / n * np.sum((jack_stats - jack_mean) ** 2)))

    return {
        "point": point,
        "bias": float(bias),
        "se": se,
        "ci_lo": float(point - 1.96 * se),
        "ci_hi": float(point + 1.96 * se),
    }
