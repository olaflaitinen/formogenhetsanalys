"""Valuation of listed equity holdings.

Market-price valuation with optional FX adjustment for foreign-listed securities.
"""

from __future__ import annotations

import numpy as np
import polars as pl
from numpy.typing import NDArray


def value_listed_equity(
    holdings_df: pl.DataFrame,
    price_series: pl.DataFrame,
    fx_rates: pl.DataFrame | None = None,
    valuation_date: str = "2022-12-31",
) -> pl.DataFrame:
    """Value listed equity holdings at market price on the valuation date.

    Args:
        holdings_df: DataFrame with columns isin (Utf8), quantity (Float64),
            currency (Utf8). One row per holding.
        price_series: DataFrame with columns isin (Utf8), date (Date),
            close_price (Float64), currency (Utf8).
        fx_rates: Optional DataFrame with columns currency (Utf8), date (Date),
            sek_rate (Float64). If None all holdings assumed SEK-denominated.
        valuation_date: ISO 8601 date string for the valuation snapshot.

    Returns:
        holdings_df with an additional column value_sek (Float64).

    Examples:
        >>> import polars as pl
        >>> h = pl.DataFrame({"isin": ["SE0000108656"], "quantity": [100.0],
        ...     "currency": ["SEK"]})
        >>> p = pl.DataFrame({"isin": ["SE0000108656"],
        ...     "date": pl.Series(["2022-12-31"]).str.to_date(),
        ...     "close_price": [150.0], "currency": ["SEK"]})
        >>> result = value_listed_equity(h, p)
        >>> float(result["value_sek"][0])
        15000.0
    """
    snap = price_series.filter(
        pl.col("date") == pl.lit(valuation_date).str.to_date(),
    ).select(["isin", "close_price"])

    df = holdings_df.join(snap, on="isin", how="left")

    if fx_rates is not None:
        fx_snap = fx_rates.filter(
            pl.col("date") == pl.lit(valuation_date).str.to_date(),
        ).select(["currency", "sek_rate"])
        df = df.join(fx_snap, on="currency", how="left")
        df = df.with_columns(
            pl.col("sek_rate").fill_null(1.0).alias("sek_rate"),
        )
    else:
        df = df.with_columns(pl.lit(1.0).alias("sek_rate"))

    return df.with_columns(
        (pl.col("quantity") * pl.col("close_price") * pl.col("sek_rate")).alias("value_sek"),
    )


def fx_adjust(
    value_local: NDArray[np.float64],
    sek_rate: float,
) -> NDArray[np.float64]:
    """Apply FX adjustment to convert local-currency values to SEK.

    Args:
        value_local: Array of values in the local currency.
        sek_rate: Exchange rate: units of local currency per 1 SEK.

    Returns:
        Array of values in SEK.

    Examples:
        >>> import numpy as np
        >>> v = np.array([100.0, 200.0])
        >>> fx_adjust(v, 0.1)
        array([1000., 2000.])
    """
    return value_local / sek_rate
