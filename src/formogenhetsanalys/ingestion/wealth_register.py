"""Wealth-register ingestion and synthetic-data generation."""

from __future__ import annotations

import pathlib

import numpy as np
import polars as pl

WEALTH_SCHEMA: list[str] = [
    "household_id",
    "total_wealth",
    "financial_wealth",
    "real_estate_wealth",
    "business_wealth",
    "debt",
]


def read_wealth_register(path: pathlib.Path) -> pl.DataFrame:
    """Read and validate a wealth-register Parquet file.

    Expected columns: household_id (Utf8), year (Int32), total_wealth (Float64),
    financial_wealth (Float64), real_estate_wealth (Float64),
    business_wealth (Float64), debt (Float64).

    Args:
        path: Path to a Parquet file conforming to the wealth-register schema.

    Returns:
        A validated Polars DataFrame.

    Raises:
        FileNotFoundError: If path does not exist.
        ValueError: If required columns are missing.

    Examples:
        >>> import pathlib
        >>> df = read_wealth_register(pathlib.Path("data/synthetic/households.parquet"))
    """
    if not path.exists():
        raise FileNotFoundError(f"Wealth register not found: {path}")

    df = pl.read_parquet(path)

    required = {"household_id", "total_wealth"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def synthetic_wealth_register(n: int = 20000, seed: int = 19960307) -> pl.DataFrame:
    """Generate a synthetic wealth-register DataFrame.

    The synthetic distribution approximates a log-normal body with a Pareto
    upper tail (tail index alpha ~ 1.5) calibrated to Swedish wealth data.

    Args:
        n: Number of households to generate.
        seed: Random seed for reproducibility.

    Returns:
        A Polars DataFrame with wealth-register schema.

    Examples:
        >>> df = synthetic_wealth_register(n=100, seed=42)
        >>> "household_id" in df.columns
        True
    """
    rng = np.random.default_rng(seed)

    household_ids = [f"HH{i:07d}" for i in range(n)]

    log_wealth = rng.normal(loc=13.5, scale=1.8, size=n)
    total_wealth = np.exp(log_wealth)

    pareto_mask = rng.random(n) < 0.02
    pareto_multiplier = rng.pareto(1.5, size=n) + 1
    total_wealth[pareto_mask] *= pareto_multiplier[pareto_mask] * 10

    financial_frac = rng.beta(2, 3, size=n)
    real_estate_frac = rng.beta(3, 2, size=n) * (1 - financial_frac)
    business_frac = np.clip(1 - financial_frac - real_estate_frac, 0, 1)

    debt_ratio = rng.beta(2, 5, size=n)
    debt = total_wealth * debt_ratio

    return pl.DataFrame(
        {
            "household_id": household_ids,
            "year": [2022] * n,
            "total_wealth": total_wealth,
            "financial_wealth": total_wealth * financial_frac,
            "real_estate_wealth": total_wealth * real_estate_frac,
            "business_wealth": total_wealth * business_frac,
            "debt": debt,
        },
    )
