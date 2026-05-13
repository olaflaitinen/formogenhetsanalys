"""Tests for graph builder."""

from __future__ import annotations

import polars as pl

from formogenhetsanalys.graph.builder import build_graph
from formogenhetsanalys.ingestion.firm_register import synthetic_firm_register
from formogenhetsanalys.ingestion.wealth_register import synthetic_wealth_register

SEED = 19960307


class TestGraphBuilder:
    def test_build_graph_returns_something(self) -> None:
        households_df = synthetic_wealth_register(n=100, seed=SEED)
        firms_df = synthetic_firm_register(n=50, seed=SEED)
        assets_df = pl.DataFrame(
            {
                "asset_id": ["A1"],
                "value_market": [1_000_000.0],
                "value_book": [900_000.0],
                "asset_type": ["real_estate"],
                "isin": [""],
                "year": [2022],
            }
        )
        ownership_df = pl.DataFrame(
            {
                "source_id": [],
                "target_id": [],
                "ownership_share": [],
                "ownership_type": [],
                "year": [],
            }
        )
        graph = build_graph(households_df, firms_df, assets_df, ownership_df)
        assert graph is not None
