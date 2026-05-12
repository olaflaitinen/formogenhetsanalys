"""Shared pytest fixtures for the Förmögenhetsanalys test suite."""

from __future__ import annotations

import pathlib

import numpy as np
import polars as pl
import pytest

from formogenhetsanalys.config import Config

SYNTHETIC_SEED = 19960307


@pytest.fixture(scope="session")
def rng() -> np.random.Generator:
    """Session-scoped NumPy random generator with SYNTHETIC_SEED."""
    return np.random.default_rng(SYNTHETIC_SEED)


@pytest.fixture(scope="session")
def small_wealth_array(rng: np.random.Generator) -> np.ndarray[object, np.dtype[np.float64]]:
    """Log-normal wealth array with 500 observations."""
    return rng.lognormal(mean=13.0, sigma=2.0, size=500)


@pytest.fixture(scope="session")
def households_df() -> pl.DataFrame:
    """Synthetic household DataFrame (200 rows)."""
    from formogenhetsanalys.ingestion.wealth_register import synthetic_wealth_register

    return synthetic_wealth_register(n=200, seed=SYNTHETIC_SEED)


@pytest.fixture(scope="session")
def firms_df() -> pl.DataFrame:
    """Synthetic firm DataFrame (50 rows)."""
    from formogenhetsanalys.ingestion.firm_register import synthetic_firm_register

    return synthetic_firm_register(n=50, seed=SYNTHETIC_SEED)


@pytest.fixture(scope="session")
def ownership_df(households_df: pl.DataFrame, firms_df: pl.DataFrame) -> pl.DataFrame:
    """Synthetic ownership-edge DataFrame."""
    rng = np.random.default_rng(SYNTHETIC_SEED + 1)
    hh_ids = households_df["household_id"].to_list()
    firm_ids = firms_df["firm_id"].to_list()
    n_edges = 300
    src = [
        hh_ids[i % len(hh_ids)]
        for i in rng.integers(0, len(hh_ids), size=n_edges).tolist()
    ]
    dst = [
        firm_ids[i % len(firm_ids)]
        for i in rng.integers(0, len(firm_ids), size=n_edges).tolist()
    ]
    shares = rng.dirichlet(np.ones(n_edges), size=1)[0].tolist()
    return pl.DataFrame(
        {
            "source_id": src,
            "target_id": dst,
            "ownership_share": shares,
            "source_type": ["household"] * n_edges,
            "target_type": ["firm"] * n_edges,
        },
    )


@pytest.fixture(scope="session")
def default_config(tmp_path_factory: pytest.TempPathFactory) -> Config:
    """Default Config pointed at a temporary data_root."""
    data_root = tmp_path_factory.mktemp("data")
    return Config(data_root=pathlib.Path(data_root))


@pytest.fixture(scope="session")
def tmp_reports(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """Temporary reports directory."""
    return tmp_path_factory.mktemp("reports")
