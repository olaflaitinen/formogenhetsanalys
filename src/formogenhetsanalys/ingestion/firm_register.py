"""Firm-register ingestion and synthetic-data generation."""

from __future__ import annotations

import pathlib

import numpy as np
import polars as pl

FIRM_SCHEMA: list[str] = [
    "firm_id",
    "org_number",
    "equity_book",
    "revenue",
    "profit",
    "sector_code",
]


def read_firm_register(path: pathlib.Path) -> pl.DataFrame:
    """Read and validate a firm-register Parquet file.

    Expected columns: firm_id (Utf8), org_nr (Utf8), year (Int32),
    is_fåmansföretag (Boolean), equity_book (Float64),
    revenue (Float64), profit (Float64), sector_code (Utf8).

    Args:
        path: Path to a Parquet file conforming to the firm-register schema.

    Returns:
        A validated Polars DataFrame.

    Raises:
        FileNotFoundError: If path does not exist.
        ValueError: If required columns are missing.

    Examples:
        >>> import pathlib
        >>> df = read_firm_register(pathlib.Path("data/synthetic/firms.parquet"))
    """
    if not path.exists():
        raise FileNotFoundError(f"Firm register not found: {path}")

    df = pl.read_parquet(path)

    required = {"firm_id", "equity_book"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


def synthetic_firm_register(n: int = 5000, seed: int = 19960307) -> pl.DataFrame:
    """Generate a synthetic firm-register DataFrame.

    Args:
        n: Number of firms to generate.
        seed: Random seed for reproducibility.

    Returns:
        A Polars DataFrame with firm-register schema.

    Examples:
        >>> df = synthetic_firm_register(n=50, seed=42)
        >>> "firm_id" in df.columns
        True
    """
    rng = np.random.default_rng(seed + 1)

    firm_ids = [f"FIRM{i:06d}" for i in range(n)]
    org_nrs = [f"{rng.integers(100000, 999999)}-{rng.integers(1000, 9999)}" for _ in range(n)]

    equity_book = np.exp(rng.normal(loc=14.0, scale=2.0, size=n))
    revenue = equity_book * rng.lognormal(mean=0.5, sigma=0.8, size=n)
    profit = revenue * rng.beta(2, 8, size=n) - revenue * 0.1

    sectors = ["K", "G", "C", "F", "M", "N", "J", "H", "I", "L"]
    sector_codes = rng.choice(sectors, size=n)

    is_fåmansföretag = rng.random(n) < 0.65

    return pl.DataFrame(
        {
            "firm_id": firm_ids,
            "org_nr": org_nrs,
            "year": [2022] * n,
            "is_fåmansföretag": is_fåmansföretag.tolist(),
            "equity_book": equity_book,
            "revenue": revenue,
            "profit": profit,
            "sector_code": sector_codes.tolist(),
        },
    )
