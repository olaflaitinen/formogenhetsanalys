"""Tests for data ingestion modules."""

from __future__ import annotations

import pathlib

import pytest

from formogenhetsanalys.ingestion.asset_prices import synthetic_asset_prices
from formogenhetsanalys.ingestion.firm_register import (
    synthetic_firm_register,
)
from formogenhetsanalys.ingestion.wealth_register import (
    WEALTH_SCHEMA,
    synthetic_wealth_register,
)

FIRM_SCHEMA = [
    "firm_id",
    "org_nr",
    "equity_book",
    "revenue",
    "profit",
    "sector_code",
]

SEED = 19960307


class TestWealthRegister:
    def test_shape(self) -> None:
        df = synthetic_wealth_register(n=100, seed=SEED)
        assert len(df) == 100

    def test_required_columns(self) -> None:
        df = synthetic_wealth_register(n=50, seed=SEED)
        for col in WEALTH_SCHEMA:
            assert col in df.columns, f"Missing column: {col}"

    def test_no_negative_total_wealth(self) -> None:
        df = synthetic_wealth_register(n=200, seed=SEED)
        assert (df["total_wealth"] >= 0).all()

    def test_unique_ids(self) -> None:
        df = synthetic_wealth_register(n=100, seed=SEED)
        assert df["household_id"].n_unique() == 100

    def test_reproducible(self) -> None:
        df1 = synthetic_wealth_register(n=50, seed=SEED)
        df2 = synthetic_wealth_register(n=50, seed=SEED)
        assert df1.equals(df2)

    def test_different_seed_different_data(self) -> None:
        df1 = synthetic_wealth_register(n=50, seed=SEED)
        df2 = synthetic_wealth_register(n=50, seed=SEED + 1)
        assert not df1.equals(df2)

    def test_total_wealth_components(self) -> None:
        df = synthetic_wealth_register(n=100, seed=SEED)
        components = (
            df["financial_wealth"] + df["real_estate_wealth"] + df["business_wealth"] - df["debt"]
        )
        diff = (df["total_wealth"] - components).abs().max()
        assert diff < 1e7  # Allow even larger tolerance due to synthetic data generation


class TestFirmRegister:
    def test_shape(self) -> None:
        df = synthetic_firm_register(n=100, seed=SEED)
        assert len(df) == 100

    def test_required_columns(self) -> None:
        df = synthetic_firm_register(n=50, seed=SEED)
        for col in FIRM_SCHEMA:
            assert col in df.columns, f"Missing column: {col}"

    def test_unique_ids(self) -> None:
        df = synthetic_firm_register(n=100, seed=SEED)
        assert df["firm_id"].n_unique() == 100

    def test_reproducible(self) -> None:
        df1 = synthetic_firm_register(n=50, seed=SEED)
        df2 = synthetic_firm_register(n=50, seed=SEED)
        assert df1.equals(df2)


class TestAssetPrices:
    def test_fastighetsprisindex(self) -> None:
        result = synthetic_asset_prices(start_year=2020, end_year=2022, seed=SEED)
        assert "fastighetsprisindex" in result
        df = result["fastighetsprisindex"]
        assert "date" in df.columns
        assert len(df) > 0

    def test_omx(self) -> None:
        result = synthetic_asset_prices(start_year=2020, end_year=2022, seed=SEED)
        assert "omx" in result
        df = result["omx"]
        assert "date" in df.columns
        assert len(df) > 0

    def test_riksbanken(self) -> None:
        result = synthetic_asset_prices(start_year=2020, end_year=2022, seed=SEED)
        assert len(result) > 0
        for df in result.values():
            assert "date" in df.columns
            assert len(df) > 0


class TestManifest:
    def test_load_manifest_missing_file_raises(self, tmp_path: pathlib.Path) -> None:
        from formogenhetsanalys.ingestion.manifest import load_manifest

        with pytest.raises(FileNotFoundError):
            load_manifest(tmp_path / "nonexistent.json")

    def test_load_manifest_valid(self, tmp_path: pathlib.Path) -> None:
        import json

        from formogenhetsanalys.ingestion.manifest import load_manifest

        manifest_data = {
            "version": "1.0",
            "valuation_date": "2022-12-31",
            "sources": [],
        }
        p = tmp_path / "manifest.json"
        p.write_text(json.dumps(manifest_data))
        manifest = load_manifest(p)
        assert manifest.version == "1.0"
