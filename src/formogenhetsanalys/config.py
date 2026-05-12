"""Configuration model for Förmögenhetsanalys.

All pipeline parameters are expressed through this Pydantic v2 model so that
configuration is validated at start-up and serialisable to JSON/YAML.
"""

from __future__ import annotations

import pathlib
from typing import Literal

from pydantic import BaseModel, Field


class Config(BaseModel):
    """Top-level configuration for the Förmögenhetsanalys pipeline.

    Attributes:
        data_root: Root directory for all data artefacts.
        seed: Master random seed passed to seeds.set_global_seed.
        gnn_architecture: Which heterogeneous GNN architecture to use.
        bayesian_prior: Prior distribution on latent beneficial-ownership shares.
        posterior: Variational posterior family.
        valuation: Asset-valuation method.
        n_jobs: Number of parallel workers (1 = serial).
        device: Compute device for PyTorch.

    Examples:
        >>> cfg = Config(data_root=pathlib.Path("data"))
        >>> cfg.seed
        20251008
    """

    data_root: pathlib.Path = Field(
        default=pathlib.Path("data"),
        description="Root directory for data artefacts.",
    )
    seed: int = Field(
        default=20251008,
        ge=0,
        description="Master random seed.",
    )
    gnn_architecture: Literal["r-gcn", "hetero-gat", "hetero-transformer", "graphsage"] = Field(
        default="hetero-gat",
        description="Heterogeneous GNN architecture.",
    )
    bayesian_prior: Literal["beta-uniform", "beta-2-5", "truncated-normal"] = Field(
        default="beta-2-5",
        description="Prior distribution on latent ownership shares.",
    )
    posterior: Literal["mean-field", "low-rank", "flow"] = Field(
        default="mean-field",
        description="Variational posterior family.",
    )
    valuation: Literal["market", "book", "capitalised", "hedonic"] = Field(
        default="market",
        description="Asset-valuation method.",
    )
    n_jobs: int = Field(
        default=1,
        ge=1,
        description="Number of parallel workers.",
    )
    device: Literal["cpu", "cuda", "mps"] = Field(
        default="cpu",
        description="Compute device for PyTorch tensors.",
    )

    model_config = {"frozen": True}
