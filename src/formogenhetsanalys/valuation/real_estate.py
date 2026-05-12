"""Valuation of residential real estate.

Converts taxeringsvärde (assessed value) to market value using either
a fixed purchase coefficient or a hedonic price index.
"""

from __future__ import annotations

import numpy as np
import polars as pl

DEFAULT_PURCHASE_COEFFICIENT: float = 0.75


def taxeringsvarde_to_market(
    taxeringsvarde: pl.Series,
    purchase_coefficient: float = DEFAULT_PURCHASE_COEFFICIENT,
) -> pl.Series:
    """Convert taxeringsvärde to estimated market value using a fixed coefficient.

    The purchase coefficient (köpeskillingskoefficient) is published annually
    by SCB and varies by property type and municipality. The default 0.75 is
    a rough national average for single-family dwellings.

    Args:
        taxeringsvarde: Series of assessed values in SEK.
        purchase_coefficient: Ratio of assessed value to market value.

    Returns:
        Series of estimated market values in SEK.

    Examples:
        >>> import polars as pl
        >>> v = taxeringsvarde_to_market(pl.Series([2e6]))
        >>> float(v[0])
        2666666.6666666665
    """
    market = taxeringsvarde.to_numpy(allow_copy=True).astype(np.float64) / purchase_coefficient
    return pl.Series("value_sek", market)


def apply_hedonic_index(
    base_value: pl.Series,
    index_base: float,
    index_target: float,
) -> pl.Series:
    """Revalue real estate from a base year to a target year using a hedonic index.

    Args:
        base_value: Series of property values in SEK at the base-year index level.
        index_base: Price index value at the base year (e.g. 100.0).
        index_target: Price index value at the target year.

    Returns:
        Series of revalued properties in SEK at the target-year level.

    Examples:
        >>> import polars as pl
        >>> v = apply_hedonic_index(pl.Series([1e6]), 100.0, 150.0)
        >>> float(v[0])
        1500000.0
    """
    if index_base <= 0:
        raise ValueError(f"index_base must be positive, got {index_base}")
    ratio = index_target / index_base
    return pl.Series("value_sek", base_value.to_numpy(allow_copy=True).astype(np.float64) * ratio)


def municipality_coefficient(municipality_code: str) -> float:
    """Return a municipality-specific purchase coefficient.

    A stub mapping: production use would load this from an SCB table.

    Args:
        municipality_code: Four-digit Swedish municipality code (kommunkod).

    Returns:
        Purchase coefficient for that municipality (default 0.75 if unknown).

    Examples:
        >>> municipality_coefficient("0180")
        0.68
    """
    coefficients: dict[str, float] = {
        "0180": 0.68,
        "0181": 0.70,
        "1480": 0.72,
        "1281": 0.73,
        "0380": 0.74,
    }
    return coefficients.get(municipality_code, DEFAULT_PURCHASE_COEFFICIENT)
