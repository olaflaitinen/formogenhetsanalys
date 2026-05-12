# Graph Schema

This document describes the heterogeneous graph schema used in Förmögenhetsanalys.

## Node Types

### HouseholdNode
Represents a household with wealth components.

**Fields:**
- `household_id`: Unique household identifier (Utf8)
- `total_wealth`: Total net wealth in SEK (Float64)
- `financial_wealth`: Financial assets in SEK (Float64)
- `real_estate_wealth`: Real estate value in SEK (Float64)
- `business_wealth`: Business ownership value in SEK (Float64)
- `debt`: Total debt in SEK (Float64)
- `year`: Reference year (Int32)

### FirmNode
Represents a company.

**Fields:**
- `firm_id`: Unique firm identifier (Utf8)
- `org_nr`: Swedish organization number (Utf8)
- `is_fåmansföretag`: Whether the firm is a closely-held company (Boolean)
- `equity_book`: Book equity in SEK (Float64)
- `revenue`: Annual revenue in SEK (Float64)
- `profit`: Annual profit in SEK (Float64)
- `sector_code`: NACE sector code (Utf8)
- `year`: Reference year (Int32)

### AssetNode
Represents an asset (real estate, listed equity).

**Fields:**
- `asset_id`: Unique asset identifier (Utf8)
- `asset_type`: Asset type (real_estate, listed_equity, unlisted_equity) (Utf8)
- `value_market`: Market value in SEK (Float64)
- `value_book`: Book value in SEK (Float64)
- `isin`: ISIN code (for securities) (Utf8)
- `year`: Reference year (Int32)

## Edge Types

### OwnershipEdge
Ownership relationship between household/firm and firm/asset.

**Fields:**
- `source_id`: Household or firm identifier (Utf8)
- `target_id`: Firm or asset identifier (Utf8)
- `ownership_share`: Ownership fraction in [0, 1] (Float64)
- `ownership_type`: Type of ownership (direct, indirect) (Utf8)
- `year`: Reference year (Int32)

### KinshipEdge
Familial relationship between individuals (for intergenerational wealth transfer).

**Fields:**
- `source_id`: Individual identifier (Utf8)
- `target_id`: Individual identifier (Utf8)
- `kinship_type`: Relationship type (spouse, parent-child, sibling) (Utf8)
- `year`: Reference year (Int32)

## Edge Type Examples

```
household --[ownership]--> firm
household --[ownership]--> asset
firm --[ownership]--> firm
individual --[kinship]--> individual
```
