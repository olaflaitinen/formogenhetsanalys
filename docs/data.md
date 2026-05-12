# Data Sources

This document describes the data sources used in Förmögenhetsanalys.

## Register Data

### Wealth Register (Skatteverket)
- **Coverage**: All Swedish households with wealth above reporting threshold
- **Contents**: Financial assets, real estate, business wealth, debt
- **Update frequency**: Annual
- **Availability**: SCB (Statistics Sweden) microdata access

### Firm Register (Bolagsverket)
- **Coverage**: All registered companies in Sweden
- **Contents**: Equity book value, revenue, profit, sector classification
- **Update frequency**: Quarterly
- **Availability**: SCB microdata access

### Ownership Chains
- **Coverage**: Direct and indirect ownership between households and firms
- **Contents**: Ownership shares, ownership types
- **Update frequency**: Annual
- **Availability**: SCB microdata access

## Synthetic Data

For testing and demonstration, the package includes synthetic data generation functions:
- `synthetic_wealth_register(n, seed)`: Generate household wealth data
- `synthetic_firm_register(n, seed)`: Generate firm data
- `synthetic_asset_prices(start_year, end_year, seed)`: Generate price series

## Asset Price Data

### Fastighetsprisindex (SCB)
- **Description**: Real estate price index by region
- **Frequency**: Monthly
- **Coverage**: Nationwide, regional breakdowns

### OMX Stockholm (Nasdaq)
- **Description**: Stock market index
- **Frequency**: Daily
- **Coverage**: Listed Swedish companies

### Riksbanken Exchange Rates
- **Description**: SEK exchange rates
- **Frequency**: Daily
- **Coverage**: Major currencies

## Data Access

All real register data requires:
- SCB microdata access agreement
- GDPR compliance
- Ethics committee approval

Synthetic data is freely available under CC0-1.0.
