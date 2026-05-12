"""Tests for top-share estimation, decomposition, and DNA adjustment."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from formogenhetsanalys.estimation.decomposition import (
    atkinson,
    gini,
    shapley_decomposition,
    theil,
)
from formogenhetsanalys.estimation.dna_adjustment import (
    align_to_macro_total,
    compute_dna_top_shares,
    dna_adjustment,
    hfcs_benchmark,
)
from formogenhetsanalys.estimation.top_shares import (
    pareto_tail,
    top_share,
    top_shares_bootstrap,
)

SEED = 19960307
RNG = np.random.default_rng(SEED)
WEALTH_500 = RNG.lognormal(13.0, 2.0, 500)


class TestTopShare:
    def test_uniform_distribution(self) -> None:
        w = np.arange(1.0, 101.0)  # Increasing values from 1 to 100
        share = top_share(w, 0.99)
        assert share == pytest.approx(0.01, abs=0.01)

    def test_all_concentrated(self) -> None:
        w = np.zeros(100)
        w[0] = 1.0
        share = top_share(w, 0.99)
        assert share == pytest.approx(1.0)

    def test_empty_array(self) -> None:
        assert top_share(np.array([]), 0.99) == 0.0

    def test_zero_total(self) -> None:
        assert top_share(np.zeros(10), 0.99) == 0.0

    def test_returns_fraction(self) -> None:
        share = top_share(WEALTH_500, 0.99)
        assert 0.0 < share < 1.0

    def test_monotone_in_quantile(self) -> None:
        s99 = top_share(WEALTH_500, 0.99)
        s999 = top_share(WEALTH_500, 0.999)
        assert s99 >= s999

    def test_bootstrap_returns_dict(self) -> None:
        result = top_shares_bootstrap(WEALTH_500, [0.99], n_boot=20, seed=7)
        assert 0.99 in result
        assert "point" in result[0.99]
        assert "ci_lo" in result[0.99]
        assert "ci_hi" in result[0.99]

    def test_bootstrap_ci_ordering(self) -> None:
        result = top_shares_bootstrap(WEALTH_500, [0.99], n_boot=50, seed=7)
        assert result[0.99]["ci_lo"] < result[0.99]["point"] < result[0.99]["ci_hi"]

    def test_pareto_tail_alpha_positive(self) -> None:
        w = RNG.pareto(1.5, size=500) * 1e6 + 1e6
        alpha, scale = pareto_tail(w, 1e6)
        assert alpha > 0

    def test_pareto_tail_raises_on_few_obs(self) -> None:
        with pytest.raises(ValueError, match="at least 2"):
            pareto_tail(np.array([1e7, 1e6, 1e5]), threshold=1e8)


class TestDecomposition:
    def test_gini_equal_distribution(self) -> None:
        assert gini(np.ones(100)) == pytest.approx(0.0, abs=1e-10)

    def test_gini_range(self) -> None:
        g = gini(WEALTH_500)
        assert 0.0 <= g <= 1.0

    def test_gini_single_owner(self) -> None:
        w = np.zeros(100)
        w[0] = 100.0
        assert gini(w) == pytest.approx(0.99, abs=0.005)

    def test_atkinson_equal_distribution(self) -> None:
        assert atkinson(np.ones(100)) == pytest.approx(0.0, abs=1e-10)

    def test_atkinson_range(self) -> None:
        a = atkinson(WEALTH_500, epsilon=0.5)
        assert 0.0 <= a <= 1.0

    def test_theil_equal_distribution(self) -> None:
        assert theil(np.ones(100)) == pytest.approx(0.0, abs=1e-10)

    def test_theil_non_negative(self) -> None:
        assert theil(WEALTH_500) >= 0.0

    def test_shapley_sums_to_total(self) -> None:
        rng = np.random.default_rng(SEED)
        components = {
            "financial": rng.lognormal(11, 1, 200),
            "real_estate": rng.lognormal(12, 1.5, 200),
        }
        total = sum(components.values())
        total_gini = gini(total)
        sv = shapley_decomposition(components)
        assert sum(sv.values()) == pytest.approx(total_gini, rel=0.05)


class TestDNAAdjustment:
    def test_align_to_macro_total(self) -> None:
        w = np.array([100.0, 200.0, 300.0])
        aligned = align_to_macro_total(w, 1200.0)
        assert aligned.sum() == pytest.approx(1200.0, rel=1e-9)

    def test_align_preserves_distribution_shape(self) -> None:
        w = np.array([1.0, 2.0, 3.0, 4.0])
        aligned = align_to_macro_total(w, 100.0)
        assert aligned[0] < aligned[1] < aligned[2] < aligned[3]

    def test_align_zero_total_safe(self) -> None:
        w = np.zeros(5)
        aligned = align_to_macro_total(w, 1000.0)
        np.testing.assert_array_equal(aligned, w)

    def test_hfcs_benchmark_blend(self) -> None:
        blended = hfcs_benchmark(0.25, 0.30, hfcs_weight=0.3)
        assert blended == pytest.approx(0.265)

    def test_hfcs_benchmark_zero_weight(self) -> None:
        blended = hfcs_benchmark(0.25, 0.30, hfcs_weight=0.0)
        assert blended == pytest.approx(0.25)

    def test_hfcs_benchmark_full_weight(self) -> None:
        blended = hfcs_benchmark(0.25, 0.30, hfcs_weight=1.0)
        assert blended == pytest.approx(0.30)

    def test_dna_adjustment_adds_column(self, households_df: pl.DataFrame) -> None:
        result = dna_adjustment(households_df, macro_total_sek=1e12)
        assert "dna_wealth" in result.columns

    def test_dna_adjustment_sum(self, households_df: pl.DataFrame) -> None:
        macro_total = 1e12
        result = dna_adjustment(households_df, macro_total_sek=macro_total)
        assert result["dna_wealth"].sum() == pytest.approx(macro_total, rel=1e-6)

    def test_compute_dna_top_shares_columns(self, households_df: pl.DataFrame) -> None:
        dna_df = dna_adjustment(households_df, macro_total_sek=1e12)
        result = compute_dna_top_shares(dna_df, q_grid=[0.99])
        assert "quantile" in result.columns
        assert "top_share" in result.columns
