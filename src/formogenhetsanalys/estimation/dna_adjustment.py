"""Distributional National Accounts (DNA) adjustment.

Aligns survey/register-based top-share estimates with World Inequality Lab
macro totals and ECB Household Finance and Consumption Survey benchmarks,
following the methodology of Piketty, Saez, and Zucman (2018).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import polars as pl


def align_to_macro_total(
    wealth: np.ndarray[Any, np.dtype[np.float64]],
    macro_total: float,
) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Scale wealth distribution so that sum matches the macro total.

    Args:
        wealth: 1-D array of household wealth values.
        macro_total: Target aggregate wealth from National Accounts.

    Returns:
        Scaled wealth array with the same shape as input.

    Examples:
        >>> import numpy as np
        >>> w = np.array([100.0, 200.0, 300.0])
        >>> aligned = align_to_macro_total(w, 1200.0)
        >>> abs(aligned.sum() - 1200.0) < 1e-6
        True
    """
    w = np.asarray(wealth, dtype=np.float64)
    current_total = np.sum(w)
    if current_total <= 0:
        return w
    return w * (macro_total / current_total)


def hfcs_benchmark(
    top_share_estimate: float,
    hfcs_top_share: float,
    hfcs_weight: float = 0.3,
) -> float:
    """Blend a register-based top-share estimate with an HFCS benchmark.

    The blending uses a weighted average, placing more weight on the register
    estimate (1 - hfcs_weight) and less on the HFCS (hfcs_weight).

    Args:
        top_share_estimate: Register-based top-share estimate.
        hfcs_top_share: Corresponding top-share from the ECB HFCS.
        hfcs_weight: Weight assigned to the HFCS estimate (0 to 1).

    Returns:
        Blended top-share estimate.

    Examples:
        >>> hfcs_benchmark(0.25, 0.30, 0.3)
        0.265
    """
    return (1 - hfcs_weight) * top_share_estimate + hfcs_weight * hfcs_top_share


def dna_adjustment(
    households_df: pl.DataFrame,
    macro_total_sek: float,
    hfcs_benchmarks: dict[float, float] | None = None,
    hfcs_weight: float = 0.3,
) -> pl.DataFrame:
    """Apply full DNA adjustment to household wealth data.

    Steps:
    1. Scale household wealth so the sum matches macro_total_sek.
    2. Optionally blend top-share estimates with HFCS benchmarks.

    Args:
        households_df: DataFrame with column harmonised_wealth or total_wealth.
        macro_total_sek: Aggregate household wealth from Swedish National Accounts (SEK).
        hfcs_benchmarks: Optional dict mapping quantile q to HFCS top-share for that q.
        hfcs_weight: Weight on HFCS in the blending step.

    Returns:
        households_df with column dna_wealth (Float64).

    Examples:
        >>> import polars as pl
        >>> import numpy as np
        >>> hh = pl.DataFrame({
        ...     "household_id": [f"HH{i}" for i in range(10)],
        ...     "total_wealth": np.random.default_rng(0).lognormal(13, 2, 10).tolist()
        ... })
        >>> result = dna_adjustment(hh, macro_total_sek=1e13)
        >>> "dna_wealth" in result.columns
        True
    """
    has_harmonised = "harmonised_wealth" in households_df.columns
    wealth_col = "harmonised_wealth" if has_harmonised else "total_wealth"
    wealth = households_df[wealth_col].to_numpy(allow_copy=True).astype(np.float64)

    aligned = align_to_macro_total(wealth, macro_total_sek)

    if hfcs_benchmarks:
        from formogenhetsanalys.estimation.top_shares import top_share

        for q, hfcs_val in hfcs_benchmarks.items():
            blended = hfcs_benchmark(top_share(aligned, q), hfcs_val, hfcs_weight)
            ratio = blended / top_share(aligned, q) if top_share(aligned, q) > 0 else 1.0
            tail_mask = aligned >= np.quantile(aligned, q)
            aligned = aligned.copy()
            aligned[tail_mask] *= ratio

    return households_df.with_columns(pl.Series("dna_wealth", aligned))


def compute_dna_top_shares(
    dna_df: pl.DataFrame,
    q_grid: list[float] | None = None,
) -> pl.DataFrame:
    """Compute top-share estimates from DNA-adjusted wealth.

    Args:
        dna_df: DataFrame with column dna_wealth.
        q_grid: List of quantile thresholds. Defaults to [0.99, 0.999, 0.9999].

    Returns:
        DataFrame with columns quantile (Float64) and top_share (Float64).

    Examples:
        >>> import polars as pl
        >>> import numpy as np
        >>> w = np.random.default_rng(0).lognormal(13, 2, 1000).tolist()
        >>> dna = pl.DataFrame({"dna_wealth": w})
        >>> result = compute_dna_top_shares(dna)
        >>> "top_share" in result.columns
        True
    """
    from formogenhetsanalys.estimation.top_shares import top_share

    q_grid = q_grid or [0.99, 0.999, 0.9999]
    wealth = dna_df["dna_wealth"].to_numpy(allow_copy=True).astype(np.float64)

    rows = [{"quantile": q, "top_share": top_share(wealth, q)} for q in q_grid]
    return pl.DataFrame(rows)
