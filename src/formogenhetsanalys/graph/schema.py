"""Typed schema for the heterogeneous ownership graph.

Node types: household, individual, firm, foundation, asset.
Edge types: ownership, kinship, employment, residence.

Each class is a frozen dataclass carrying the typed attribute schema for its
node or edge type. The schema is used by the graph builder to validate inputs
and by the GNN to construct type-aware feature matrices.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HouseholdNode:
    """Schema for a household node.

    Attributes:
        household_id: Unique household identifier string.
        total_wealth: Total observed wealth in SEK.
        financial_wealth: Financial-asset component of total wealth.
        real_estate_wealth: Real-estate component.
        business_wealth: Business-ownership component.
        debt: Total liabilities.
        year: Reference year.

    Examples:
        >>> n = HouseholdNode("HH0000001", 1e6, 3e5, 5e5, 2e5, 1e5, 2022)
        >>> n.year
        2022
    """

    household_id: str
    total_wealth: float
    financial_wealth: float
    real_estate_wealth: float
    business_wealth: float
    debt: float
    year: int


@dataclass(frozen=True)
class IndividualNode:
    """Schema for an individual node.

    Attributes:
        individual_id: Unique individual identifier.
        household_id: Parent household identifier.
        age: Age in reference year.
        gender: Coded gender (0/1).
        income: Gross income in SEK.
        year: Reference year.

    Examples:
        >>> n = IndividualNode("IND001", "HH0000001", 45, 1, 5e5, 2022)
        >>> n.age
        45
    """

    individual_id: str
    household_id: str
    age: int
    gender: int
    income: float
    year: int


@dataclass(frozen=True)
class FirmNode:
    """Schema for a firm node.

    Attributes:
        firm_id: Unique firm identifier.
        org_nr: Swedish organisationsnummer.
        is_fåmansföretag: Whether the firm is a closely held company.
        equity_book: Book equity in SEK.
        revenue: Annual revenue in SEK.
        profit: Pre-tax profit in SEK.
        sector_code: SNI sector code (single character).
        year: Reference year.

    Examples:
        >>> n = FirmNode("FIRM000001", "556000-1234", True, 1e7, 5e6, 5e5, "K", 2022)
        >>> n.is_fåmansföretag
        True
    """

    firm_id: str
    org_nr: str
    is_fåmansföretag: bool
    equity_book: float
    revenue: float
    profit: float
    sector_code: str
    year: int


@dataclass(frozen=True)
class FoundationNode:
    """Schema for a foundation node.

    Attributes:
        foundation_id: Unique foundation identifier.
        org_nr: Swedish organisationsnummer.
        total_assets: Total assets in SEK.
        purpose_code: Foundation purpose classification.
        year: Reference year.

    Examples:
        >>> n = FoundationNode("FND00001", "802000-1234", 5e8, "charitable", 2022)
        >>> n.total_assets
        500000000.0
    """

    foundation_id: str
    org_nr: str
    total_assets: float
    purpose_code: str
    year: int


@dataclass(frozen=True)
class AssetNode:
    """Schema for an asset node.

    Attributes:
        asset_id: Unique asset identifier.
        asset_type: One of 'listed_equity', 'unlisted_equity', 'real_estate', 'bond', 'other'.
        value_market: Market value in SEK (may be NaN for unlisted).
        value_book: Book value in SEK.
        isin: ISIN code for listed equity (may be empty string).
        year: Reference year.

    Examples:
        >>> n = AssetNode("AST00001", "listed_equity", 1e5, 9e4, "SE0000108656", 2022)
        >>> n.asset_type
        'listed_equity'
    """

    asset_id: str
    asset_type: str
    value_market: float
    value_book: float
    isin: str
    year: int


@dataclass(frozen=True)
class OwnershipEdge:
    """Schema for a directed ownership edge (owner -> owned).

    Attributes:
        source_id: Identifier of the owning entity.
        target_id: Identifier of the owned entity.
        ownership_share: Fraction of target owned by source (0 to 1).
        ownership_type: One of 'direct', 'indirect', 'beneficial'.
        year: Reference year.

    Examples:
        >>> e = OwnershipEdge("HH0000001", "FIRM000001", 0.8, "direct", 2022)
        >>> e.ownership_share
        0.8
    """

    source_id: str
    target_id: str
    ownership_share: float
    ownership_type: str
    year: int


@dataclass(frozen=True)
class KinshipEdge:
    """Schema for an undirected kinship edge between individuals.

    Attributes:
        source_id: First individual identifier.
        target_id: Second individual identifier.
        kinship_type: One of 'parent', 'child', 'sibling', 'spouse'.
        year: Reference year.

    Examples:
        >>> e = KinshipEdge("IND001", "IND002", "parent", 2022)
        >>> e.kinship_type
        'parent'
    """

    source_id: str
    target_id: str
    kinship_type: str
    year: int


@dataclass(frozen=True)
class EmploymentEdge:
    """Schema for a directed employment edge (individual -> firm).

    Attributes:
        individual_id: Employed individual identifier.
        firm_id: Employer firm identifier.
        is_owner_manager: Whether the individual is both owner and manager.
        wage: Annual wage in SEK.
        year: Reference year.

    Examples:
        >>> e = EmploymentEdge("IND001", "FIRM000001", True, 8e5, 2022)
        >>> e.is_owner_manager
        True
    """

    individual_id: str
    firm_id: str
    is_owner_manager: bool
    wage: float
    year: int


@dataclass(frozen=True)
class ResidenceEdge:
    """Schema for a directed residence edge (individual -> household).

    Attributes:
        individual_id: Resident individual identifier.
        household_id: Household identifier.
        is_head: Whether the individual is the household head.
        year: Reference year.

    Examples:
        >>> e = ResidenceEdge("IND001", "HH0000001", True, 2022)
        >>> e.is_head
        True
    """

    individual_id: str
    household_id: str
    is_head: bool
    year: int


NODE_TYPES: tuple[str, ...] = ("household", "individual", "firm", "foundation", "asset")
EDGE_TYPES: tuple[tuple[str, str, str], ...] = (
    ("household", "ownership", "firm"),
    ("household", "ownership", "foundation"),
    ("household", "ownership", "asset"),
    ("individual", "ownership", "firm"),
    ("individual", "ownership", "asset"),
    ("firm", "ownership", "firm"),
    ("firm", "ownership", "asset"),
    ("foundation", "ownership", "firm"),
    ("foundation", "ownership", "asset"),
    ("individual", "kinship", "individual"),
    ("individual", "employment", "firm"),
    ("individual", "residence", "household"),
)
