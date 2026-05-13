"""Benchmark GNN training performance."""

from __future__ import annotations

import time

import numpy as np

from formogenhetsanalys.models.hetero_gnn import get_model
from formogenhetsanalys.seeds import set_global_seed


def bench_rgcn_training() -> None:
    """Benchmark RGCN training time."""
    set_global_seed(42)
    model = get_model(
        "r-gcn",
        ["household", "firm"],
        [("household", "ownership", "firm")],
        hidden_dim=64,
        seed=42,
    )

    x_dict = {
        "household": np.random.rand(1000, 32).astype(np.float32),
        "firm": np.random.rand(500, 16).astype(np.float32),
    }

    start = time.time()
    for _ in range(10):
        model.forward(x_dict, {})
    elapsed = time.time() - start
    print(f"RGCN training (10 epochs): {elapsed:.2f}s")


if __name__ == "__main__":
    bench_rgcn_training()
