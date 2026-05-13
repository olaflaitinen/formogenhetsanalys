"""Tests for graph schema dataclasses."""

from __future__ import annotations

from formogenhetsanalys.graph.schema import (
    FirmNode,
    HouseholdNode,
)


class TestHouseholdNode:
    def test_creation(self) -> None:
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


class TestFirmNode:
    def test_creation(self) -> None:
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
