"""Asset-price reference series readers.

Provides readers for SCB Fastighetsprisindex, OMX Stockholm indices, and
Riksbanken bond-yield series. All readers return Polars DataFrames with a
standardised date column and a float value column.
"""

from __future__ import annotations

import pathlib

import numpy as np
import polars as pl


def read_fastighetsprisindex(path: pathlib.Path) -> pl.DataFrame:
    """Read SCB Fastighetsprisindex (residential real-estate price index).

    Args:
        path: Path to a CSV or Parquet file with columns date (Date) and index_value (Float64).

    Returns:
        Polars DataFrame with columns: date, fastighetsprisindex.

    Raises:
        FileNotFoundError: If path does not exist.

    Examples:
        >>> import pathlib
        >>> # df = read_fastighetsprisindex(pathlib.Path("data/fastighetsprisindex.csv"))
    """
    if not path.exists():
        raise FileNotFoundError(f"Fastighetsprisindex file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".parquet":
        df = pl.read_parquet(path)
    else:
        df = pl.read_csv(path, try_parse_dates=True)

    return df.rename({c: c for c in df.columns}).select(
        ["date", pl.col(df.columns[-1]).alias("fastighetsprisindex")],
    )


def read_omx_index(path: pathlib.Path) -> pl.DataFrame:
    """Read OMX Stockholm equity-index series.

    Args:
        path: Path to a CSV or Parquet file with columns date (Date) and close (Float64).

    Returns:
        Polars DataFrame with columns: date, omx_close.

    Raises:
        FileNotFoundError: If path does not exist.

    Examples:
        >>> import pathlib
        >>> # df = read_omx_index(pathlib.Path("data/omx_stockholm.csv"))
    """
    if not path.exists():
        raise FileNotFoundError(f"OMX index file not found: {path}")

    suffix = path.suffix.lower()
    df = pl.read_parquet(path) if suffix == ".parquet" else pl.read_csv(path, try_parse_dates=True)
    return df.select(["date", pl.col("close").alias("omx_close")])


def read_riksbanken_yields(path: pathlib.Path) -> pl.DataFrame:
    """Read Riksbanken government bond yield series.

    Args:
        path: Path to a CSV or Parquet file with columns date (Date) and yield_10y (Float64).

    Returns:
        Polars DataFrame with columns: date, yield_10y.

    Raises:
        FileNotFoundError: If path does not exist.

    Examples:
        >>> import pathlib
        >>> # df = read_riksbanken_yields(pathlib.Path("data/riksbanken_yields.csv"))
    """
    if not path.exists():
        raise FileNotFoundError(f"Riksbanken yields file not found: {path}")

    suffix = path.suffix.lower()
    df = pl.read_parquet(path) if suffix == ".parquet" else pl.read_csv(path, try_parse_dates=True)
    return df.select(["date", "yield_10y"])


def synthetic_asset_prices(
    start_year: int = 2000,
    end_year: int = 2023,
    seed: int = 19960307,
) -> dict[str, pl.DataFrame]:
    """Generate synthetic asset-price reference series.

    Args:
        start_year: First year of the series.
        end_year: Last year of the series.
        seed: Random seed.

    Returns:
        Dictionary with keys 'fastighetsprisindex', 'omx', 'yields'.

    Examples:
        >>> prices = synthetic_asset_prices(seed=42)
        >>> "fastighetsprisindex" in prices
        True
    """
    rng = np.random.default_rng(seed + 100)
    years = list(range(start_year, end_year + 1))
    n = len(years)

    dates = [f"{y}-12-31" for y in years]

    re_returns = rng.normal(loc=0.05, scale=0.08, size=n)
    re_index = 100.0 * np.cumprod(1 + re_returns)

    eq_returns = rng.normal(loc=0.07, scale=0.18, size=n)
    eq_index = 100.0 * np.cumprod(1 + eq_returns)

    yields = np.clip(rng.normal(loc=0.03, scale=0.02, size=n), 0.001, 0.15)

    dates_pl = pl.Series("date", dates).str.to_date()

    return {
        "fastighetsprisindex": pl.DataFrame({"date": dates_pl, "fastighetsprisindex": re_index}),
        "omx": pl.DataFrame({"date": dates_pl, "omx_close": eq_index}),
        "yields": pl.DataFrame({"date": dates_pl, "yield_10y": yields}),
    }


def get_valuation_multiplier(
    asset_prices: dict[str, pl.DataFrame],
    year: int,
    asset_type: str,
    base_year: int | None = None,
) -> float:
    """Compute a valuation multiplier for a given asset type and year.

    Args:
        asset_prices: Dictionary from synthetic_asset_prices or real readers.
        year: Target valuation year.
        asset_type: One of 'real_estate', 'equity', 'bond'.
        base_year: Reference year for index normalisation; defaults to 2010.

    Returns:
        Float multiplier relative to base_year.

    Examples:
        >>> prices = synthetic_asset_prices(seed=42)
        >>> m = get_valuation_multiplier(prices, 2022, "equity")
        >>> isinstance(m, float)
        True
    """
    base = base_year or 2010
    key_map = {
        "real_estate": ("fastighetsprisindex", "fastighetsprisindex"),
        "equity": ("omx", "omx_close"),
        "bond": ("yields", "yield_10y"),
    }
    if asset_type not in key_map:
        raise ValueError(f"Unknown asset_type: {asset_type}. Choose from {list(key_map)}")

    df_key, col = key_map[asset_type]
    df = asset_prices[df_key]

    def _get_val(y: int) -> float:
        filtered = df.filter(pl.col("date").dt.year() == y)
        if filtered.is_empty():
            raise ValueError(f"No data for year {y} in {df_key}")
        return float(filtered[col][0])

    return _get_val(year) / _get_val(base)
