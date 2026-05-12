"""Tests for graph schema, builder, loaders, and sampling."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from formogenhetsanalys.graph.builder import build_graph
from formogenhetsanalys.graph.loaders import (
    make_mini_batches,
    train_val_test_split,
)
from formogenhetsanalys.graph.sampling import (
    corrupt_edges,
    sample_negative_edges,
)
from formogenhetsanalys.graph.schema import (
    AssetNode,
    FirmNode,
    HouseholdNode,
    KinshipEdge,
    OwnershipEdge,
)

SEED = 19960307


class TestSchema:
    def test_household_node_creation(self) -> None:
        node = HouseholdNode(
            household_id="HH001",
            total_wealth=1_000_000.0,
            financial_wealth=300_000.0,
            real_estate_wealth=500_000.0,
            business_wealth=200_000.0,
            debt=100_000.0,
            year=2022,
        )
        assert node.household_id == "HH001"
        assert node.total_wealth == pytest.approx(1_000_000.0)

    def test_firm_node_creation(self) -> None:
        node = FirmNode(
            firm_id="F001",
            org_nr="556001-1234",
            is_fåmansföretag=True,
            equity_book=500_000.0,
            revenue=1_000_000.0,
            profit=100_000.0,
            sector_code="K",
            year=2022,
        )
        assert node.firm_id == "F001"
        assert node.org_nr == "556001-1234"

    def test_asset_node_creation(self) -> None:
        node = AssetNode(
            asset_id="A001",
            asset_type="real_estate",
            value_market=2_000_000.0,
            value_book=1_800_000.0,
            isin="",
            year=2022,
        )
        assert node.asset_id == "A001"

    def test_ownership_edge(self) -> None:
        edge = OwnershipEdge(
            source_id="HH001",
            target_id="F001",
            ownership_share=0.65,
            ownership_type="direct",
            year=2022,
        )
        assert edge.ownership_share == pytest.approx(0.65)

    def test_kinship_edge(self) -> None:
        edge = KinshipEdge(
            source_id="IND001",
            target_id="IND002",
            kinship_type="spouse",
            year=2022,
        )
        assert edge.kinship_type == "spouse"


class TestLoaders:
    def test_train_val_test_split_sizes(self) -> None:
        tr, va, te = train_val_test_split(100, train_frac=0.7, val_frac=0.15, seed=SEED)
        assert len(tr) + len(va) + len(te) == 100

    def test_train_val_test_split_no_overlap(self) -> None:
        tr, va, te = train_val_test_split(100, seed=SEED)
        assert len(set(tr) & set(va)) == 0
        assert len(set(tr) & set(te)) == 0
        assert len(set(va) & set(te)) == 0

    def test_train_val_test_split_reproducible(self) -> None:
        tr1, va1, te1 = train_val_test_split(100, seed=SEED)
        tr2, va2, te2 = train_val_test_split(100, seed=SEED)
        np.testing.assert_array_equal(tr1, tr2)

    def test_mini_batches_count(self) -> None:
        idx = np.arange(100)
        batches = make_mini_batches(idx, batch_size=32, shuffle=False)
        assert len(batches) == 4

    def test_mini_batches_cover_all(self) -> None:
        idx = np.arange(100)
        batches = make_mini_batches(idx, batch_size=30, shuffle=False)
        all_idx = np.concatenate(batches)
        assert set(all_idx.tolist()) == set(range(100))

    def test_mini_batches_shuffle_reproducible(self) -> None:
        idx = np.arange(100)
        b1 = make_mini_batches(idx, batch_size=50, shuffle=True, seed=42)
        b2 = make_mini_batches(idx, batch_size=50, shuffle=True, seed=42)
        np.testing.assert_array_equal(b1[0], b2[0])


class TestSampling:
    def test_negative_edges_count(self) -> None:
        src = np.arange(10, dtype=np.int64)
        dst = np.arange(10, dtype=np.int64)
        ns, nd = sample_negative_edges((src, dst), 15, 15, num_neg=10, seed=42)
        assert len(ns) == 10
        assert len(nd) == 10

    def test_negative_edges_not_in_positives(self) -> None:
        src = np.array([0, 1, 2], dtype=np.int64)
        dst = np.array([0, 1, 2], dtype=np.int64)
        pos_set = set(zip(src.tolist(), dst.tolist(), strict=False))
        ns, nd = sample_negative_edges((src, dst), 10, 10, num_neg=20, seed=42)
        for s, d in zip(ns.tolist(), nd.tolist(), strict=False):
            assert (s, d) not in pos_set

    def test_corrupt_edges_same_length(self) -> None:
        src = np.array([0, 1, 2], dtype=np.int64)
        dst = np.array([3, 4, 5], dtype=np.int64)
        cs, cd = corrupt_edges((src, dst), 10, seed=42)
        assert len(cs) == 3
        assert len(cd) == 3
        np.testing.assert_array_equal(cs, src)


class TestBuilder:
    def test_build_graph_returns_something(
        self,
        households_df: pl.DataFrame,
        firms_df: pl.DataFrame,
        ownership_df: pl.DataFrame,
    ) -> None:
        assets_df = pl.DataFrame(
            {
                "asset_id": ["A1"],
                "value_market": [1_000_000.0],
                "value_book": [900_000.0],
            },
        )
        graph = build_graph(households_df, firms_df, assets_df, ownership_df)
        assert graph is not None

    def test_build_graph_empty_ownership(
        self,
        households_df: pl.DataFrame,
        firms_df: pl.DataFrame,
    ) -> None:
        assets_df = pl.DataFrame(
            {"asset_id": ["A1"], "value_market": [1e6], "value_book": [9e5]},
        )
        empty_own = pl.DataFrame(
            {
                "source_id": [],
                "target_id": [],
                "ownership_share": [],
                "source_type": [],
                "target_type": [],
            },
        )
        graph = build_graph(households_df, firms_df, assets_df, empty_own)
        assert graph is not None
