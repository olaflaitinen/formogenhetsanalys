"""Valuation of unlisted equity.

Implements three methods:
- book_value: equity book value from balance sheet.
- capitalised_earnings: P/E times sector median earnings yield.
- transaction_multiples: revenue or EBITDA multiples from sector comparables.
"""

from __future__ import annotations

import numpy as np
import polars as pl

SECTOR_PE_MEDIANS: dict[str, float] = {
    "K": 18.0,
    "G": 14.0,
    "C": 12.0,
    "F": 10.0,
    "M": 16.0,
    "N": 13.0,
    "J": 22.0,
    "H": 11.0,
    "I": 15.0,
    "L": 20.0,
    "DEFAULT": 14.0,
}

SECTOR_REVENUE_MULTIPLES: dict[str, float] = {
    "K": 3.5,
    "G": 0.8,
    "C": 0.6,
    "F": 0.5,
    "M": 2.0,
    "N": 1.2,
    "J": 4.0,
    "H": 0.7,
    "I": 1.5,
    "L": 5.0,
    "DEFAULT": 1.0,
}


def book_value(equity_book: pl.Series) -> pl.Series:
    """Return book equity as the valuation.

    Args:
        equity_book: Series of book equity values in SEK.

    Returns:
        Series of valuations equal to equity_book.

    Examples:
        >>> import polars as pl
        >>> book_value(pl.Series([1e6, 2e6]))[0]
        1000000.0
    """
    return equity_book.alias("value_sek")


def capitalised_earnings(
    profit: pl.Series,
    sector_code: pl.Series,
    pe_override: float | None = None,
) -> pl.Series:
    """Value unlisted equity by capitalising earnings at a sector-median P/E.

    Args:
        profit: Annual pre-tax profit in SEK.
        sector_code: SNI sector code for each firm.
        pe_override: If provided, use this P/E for all firms instead of
            sector medians.

    Returns:
        Series of valuations in SEK.

    Examples:
        >>> import polars as pl
        >>> v = capitalised_earnings(pl.Series([1e5]), pl.Series(["K"]))
        >>> float(v[0])
        1800000.0
    """
    if pe_override is not None:
        pe_arr = np.full(len(profit), pe_override)
    else:
        pe_arr = np.array(
            [SECTOR_PE_MEDIANS.get(str(s), SECTOR_PE_MEDIANS["DEFAULT"]) for s in sector_code],
            dtype=np.float64,
        )

    values = profit.to_numpy(allow_copy=True).astype(np.float64) * pe_arr
    return pl.Series("value_sek", np.maximum(values, 0.0))


def transaction_multiples(
    revenue: pl.Series,
    sector_code: pl.Series,
    multiple_override: float | None = None,
) -> pl.Series:
    """Value unlisted equity by applying sector-median revenue multiples.

    Args:
        revenue: Annual revenue in SEK.
        sector_code: SNI sector code for each firm.
        multiple_override: If provided, use this multiple for all firms.

    Returns:
        Series of valuations in SEK.

    Examples:
        >>> import polars as pl
        >>> v = transaction_multiples(pl.Series([2e6]), pl.Series(["J"]))
        >>> float(v[0])
        8000000.0
    """
    if multiple_override is not None:
        mult_arr = np.full(len(revenue), multiple_override)
    else:
        mult_arr = np.array(
            [
                SECTOR_REVENUE_MULTIPLES.get(str(s), SECTOR_REVENUE_MULTIPLES["DEFAULT"])
                for s in sector_code
            ],
            dtype=np.float64,
        )

    values = revenue.to_numpy(allow_copy=True).astype(np.float64) * mult_arr
    return pl.Series("value_sek", np.maximum(values, 0.0))
