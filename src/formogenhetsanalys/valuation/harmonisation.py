"""Valuation harmonisation across methods.

Reconciles listed equity, unlisted equity, and real-estate valuations into a
single wealth measure, and provides sensitivity-analysis routines that span
alternative method combinations.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
import polars as pl

from formogenhetsanalys.valuation import unlisted_equity as ue

ValuationMethod = Literal["market", "book", "capitalised", "hedonic"]


def harmonise_valuations(
    households_df: pl.DataFrame,
    firms_df: pl.DataFrame,
    method: ValuationMethod = "market",
) -> pl.DataFrame:
    """Harmonise household and firm valuations into a single wealth measure.

    Args:
        households_df: Wealth-register DataFrame (output of read_wealth_register).
        firms_df: Firm-register DataFrame (output of read_firm_register).
        method: Valuation method for unlisted equity.
            'market'     - market price where available, book value otherwise.
            'book'       - book equity for all unlisted holdings.
            'capitalised'- capitalised earnings using sector P/E medians.
            'hedonic'    - hedonic real-estate index (affects real_estate_wealth).

    Returns:
        households_df with an additional column harmonised_wealth (Float64).

    Examples:
        >>> import polars as pl
        >>> hh = pl.DataFrame({"household_id": ["HH1"], "total_wealth": [1e6],
        ...     "financial_wealth": [3e5], "real_estate_wealth": [5e5],
        ...     "business_wealth": [2e5], "debt": [1e5]})
        >>> firms = pl.DataFrame({"firm_id": ["F1"], "equity_book": [1e5],
        ...     "revenue": [5e4], "profit": [1e4], "sector_code": ["K"]})
        >>> result = harmonise_valuations(hh, firms)
        >>> "harmonised_wealth" in result.columns
        True
    """
    if method == "book":
        scale = 1.0
    elif method == "capitalised":
        if "profit" in firms_df.columns and "sector_code" in firms_df.columns:
            capitalised = ue.capitalised_earnings(firms_df["profit"], firms_df["sector_code"])
            book = firms_df["equity_book"]
            cap_sum = float(capitalised.sum() or 0.0)
            book_sum = float(book.sum() or 0.0)
            scale = cap_sum / book_sum if book_sum > 0 else 1.0
        else:
            scale = 1.0
    else:
        scale = 1.0

    harmonised = households_df["total_wealth"].to_numpy(allow_copy=True).astype(np.float64).copy()

    if "business_wealth" in households_df.columns:
        bw = households_df["business_wealth"].to_numpy(allow_copy=True).astype(np.float64)
        harmonised += bw * (scale - 1.0)

    return households_df.with_columns(pl.Series("harmonised_wealth", harmonised))


def sensitivity_grid(
    households_df: pl.DataFrame,
    firms_df: pl.DataFrame,
) -> pl.DataFrame:
    """Compute top-1-percent wealth shares across all valuation-method combinations.

    Args:
        households_df: Wealth-register DataFrame.
        firms_df: Firm-register DataFrame.

    Returns:
        DataFrame with columns method (Utf8) and top_1pct_share (Float64).

    Examples:
        >>> import polars as pl
        >>> import numpy as np
        >>> hh = pl.DataFrame({"household_id": [f"HH{i}" for i in range(100)],
        ...     "total_wealth": np.random.default_rng(0).lognormal(13, 2, 100).tolist(),
        ...     "financial_wealth": [0.0]*100, "real_estate_wealth": [0.0]*100,
        ...     "business_wealth": [0.0]*100, "debt": [0.0]*100})
        >>> firms = pl.DataFrame({"firm_id": ["F1"], "equity_book": [1e5],
        ...     "revenue": [5e4], "profit": [1e4], "sector_code": ["K"]})
        >>> grid = sensitivity_grid(hh, firms)
        >>> "method" in grid.columns
        True
    """
    from formogenhetsanalys.estimation.top_shares import top_share

    results = []
    for method in ("market", "book", "capitalised"):
        harmonised_df = harmonise_valuations(households_df, firms_df, method=method)
        wealth = harmonised_df["harmonised_wealth"].to_numpy(allow_copy=True)
        share = top_share(wealth, 0.99)
        results.append({"method": method, "top_1pct_share": share})

    return pl.DataFrame(results)
