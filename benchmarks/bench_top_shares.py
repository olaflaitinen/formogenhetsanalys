"""Benchmark top share estimation performance."""

from __future__ import annotations

import time

import numpy as np

from formogenhetsanalys.estimation.top_shares import top_share, top_shares_bootstrap


def bench_top_share_simple() -> None:
    """Benchmark simple top share calculation."""
    rng = np.random.default_rng(42)
    wealth = rng.lognormal(13.0, 2.0, 1_000_000)

    start = time.time()
    for _ in range(100):
        top_share(wealth, 0.99)
    elapsed = time.time() - start
    print(f"Top share (100 iterations, 1M obs): {elapsed:.2f}s")


def bench_top_share_bootstrap() -> None:
    """Benchmark bootstrap top share calculation."""
    rng = np.random.default_rng(42)
    wealth = rng.lognormal(13.0, 2.0, 100_000)

    start = time.time()
    top_shares_bootstrap(wealth, [0.99, 0.999], n_boot=200, seed=7)
    elapsed = time.time() - start
    print(f"Bootstrap top shares (200 bootstraps, 100K obs): {elapsed:.2f}s")


if __name__ == "__main__":
    bench_top_share_simple()
    bench_top_share_bootstrap()
