"""Tests for asset valuation modules."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from formogenhetsanalys.valuation.harmonisation import harmonise_valuations, sensitivity_grid
from formogenhetsanalys.valuation.listed_equity import fx_adjust, value_listed_equity
from formogenhetsanalys.valuation.real_estate import (
    apply_hedonic_index,
    municipality_coefficient,
    taxeringsvarde_to_market,
)
from formogenhetsanalys.valuation.unlisted_equity import (
    book_value,
    capitalised_earnings,
    transaction_multiples,
)


class TestListedEquity:
    def test_basic_valuation(self) -> None:
        holdings = pl.DataFrame(
            {"isin": ["SE0001"], "quantity": [100.0], "currency": ["SEK"]},
        )
        prices = pl.DataFrame(
            {
                "isin": ["SE0001"],
                "date": pl.Series(["2022-12-31"]).str.to_date(),
                "close_price": [150.0],
                "currency": ["SEK"],
            },
        )
        result = value_listed_equity(holdings, prices)
        assert "value_sek" in result.columns
        assert float(result["value_sek"][0]) == pytest.approx(15_000.0)

    def test_fx_adjust_sek_rate_one(self) -> None:
        v = np.array([100.0, 200.0])
        result = fx_adjust(v, 1.0)
        np.testing.assert_array_almost_equal(result, v)

    def test_fx_adjust_conversion(self) -> None:
        v = np.array([100.0])
        result = fx_adjust(v, 0.1)
        assert result[0] == pytest.approx(1000.0)


class TestUnlistedEquity:
    def test_book_value_passthrough(self) -> None:
        s = pl.Series([1e6, 2e6])
        result = book_value(s)
        np.testing.assert_array_almost_equal(result.to_numpy(), s.to_numpy())

    def test_capitalised_earnings_known_sector(self) -> None:
        profit = pl.Series([1e5])
        sector = pl.Series(["K"])
        result = capitalised_earnings(profit, sector)
        assert float(result[0]) == pytest.approx(1e5 * 18.0)

    def test_capitalised_earnings_default_sector(self) -> None:
        profit = pl.Series([1e5])
        sector = pl.Series(["Z"])
        result = capitalised_earnings(profit, sector)
        assert float(result[0]) == pytest.approx(1e5 * 14.0)

    def test_capitalised_earnings_override(self) -> None:
        profit = pl.Series([1e5])
        sector = pl.Series(["K"])
        result = capitalised_earnings(profit, sector, pe_override=10.0)
        assert float(result[0]) == pytest.approx(1e5 * 10.0)

    def test_capitalised_earnings_non_negative(self) -> None:
        profit = pl.Series([-1e5])
        sector = pl.Series(["K"])
        result = capitalised_earnings(profit, sector)
        assert float(result[0]) == 0.0

    def test_transaction_multiples_known_sector(self) -> None:
        revenue = pl.Series([2e6])
        sector = pl.Series(["J"])
        result = transaction_multiples(revenue, sector)
        assert float(result[0]) == pytest.approx(2e6 * 4.0)

    def test_transaction_multiples_non_negative(self) -> None:
        revenue = pl.Series([-1e6])
        sector = pl.Series(["J"])
        result = transaction_multiples(revenue, sector)
        assert float(result[0]) == 0.0


class TestRealEstate:
    def test_taxeringsvarde_to_market_default_coefficient(self) -> None:
        tv = pl.Series([2_000_000.0])
        result = taxeringsvarde_to_market(tv)
        expected = 2_000_000.0 / 0.75
        assert float(result[0]) == pytest.approx(expected)

    def test_taxeringsvarde_to_market_custom_coefficient(self) -> None:
        tv = pl.Series([1_000_000.0])
        result = taxeringsvarde_to_market(tv, purchase_coefficient=0.5)
        assert float(result[0]) == pytest.approx(2_000_000.0)

    def test_hedonic_index_same_level(self) -> None:
        base = pl.Series([1_000_000.0])
        result = apply_hedonic_index(base, 100.0, 100.0)
        assert float(result[0]) == pytest.approx(1_000_000.0)

    def test_hedonic_index_appreciation(self) -> None:
        base = pl.Series([1_000_000.0])
        result = apply_hedonic_index(base, 100.0, 150.0)
        assert float(result[0]) == pytest.approx(1_500_000.0)

    def test_hedonic_index_zero_base_raises(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            apply_hedonic_index(pl.Series([1e6]), 0.0, 100.0)

    def test_municipality_coefficient_known(self) -> None:
        c = municipality_coefficient("0180")
        assert c == pytest.approx(0.68)

    def test_municipality_coefficient_default(self) -> None:
        c = municipality_coefficient("9999")
        assert c == pytest.approx(0.75)


class TestHarmonisation:
    def test_harmonise_adds_column(
        self, households_df: pl.DataFrame, firms_df: pl.DataFrame,
    ) -> None:
        result = harmonise_valuations(households_df, firms_df)
        assert "harmonised_wealth" in result.columns

    def test_harmonise_book_method(
        self, households_df: pl.DataFrame, firms_df: pl.DataFrame,
    ) -> None:
        result = harmonise_valuations(households_df, firms_df, method="book")
        tw = households_df["total_wealth"].to_numpy()
        hw = result["harmonised_wealth"].to_numpy()
        np.testing.assert_array_almost_equal(tw, hw)

    def test_sensitivity_grid_returns_all_methods(
        self, households_df: pl.DataFrame, firms_df: pl.DataFrame,
    ) -> None:
        grid = sensitivity_grid(households_df, firms_df)
        assert "method" in grid.columns
        assert "top_1pct_share" in grid.columns
        assert len(grid) == 3
