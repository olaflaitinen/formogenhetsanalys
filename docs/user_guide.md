# User Guide

This guide explains how to use Förmögenhetsanalys to estimate wealth concentration in Sweden using graph-aware methods.

## Installation

```bash
# Clone the repository
git clone https://github.com/olaflaitinen/formogenhetsanalys.git
cd formogenhetsanalys

# Install with uv
pip install uv
uv sync

# Install with pip
pip install -e .
```

## Quick Start

### Running the Pipeline

```python
from formogenhetsanalys import Config, Pipeline, set_global_seed

# Configure the pipeline
config = Config(
    data_root=pathlib.Path("data/synthetic"),
    seed=19960307,
    gnn_architecture="r-gcn",
    valuation="market",
)

# Set the global seed for reproducibility
set_global_seed(config.seed)

# Run the synthetic pipeline
pipeline = Pipeline(config)
results = pipeline.run_synthetic()

print(f"Top-1% share: {results['top_shares'][0.99]}")
print(f"Gini coefficient: {results['gini']}")
```

### Using the CLI

```bash
# Run the full pipeline on synthetic data
formogenhetsanalys ingest --synthetic
formogenhetsanalys run --synthetic
formogenhetsanalys decompose --synthetic
formogenhetsanalys report --output-dir reports/
```

## Data Format

### Wealth Register

The wealth register should be a Parquet file with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| household_id | Utf8 | Unique household identifier |
| total_wealth | Float64 | Total net wealth in SEK |
| financial_wealth | Float64 | Financial assets in SEK |
| real_estate_wealth | Float64 | Real estate value in SEK |
| business_wealth | Float64 | Business ownership value in SEK |
| debt | Float64 | Total debt in SEK |

### Firm Register

The firm register should be a Parquet file with:

| Column | Type | Description |
|--------|------|-------------|
| firm_id | Utf8 | Unique firm identifier |
| org_nr | Utf8 | Swedish organization number |
| is_fåmansföretag | Boolean | Whether the firm is a closely-held company |
| equity_book | Float64 | Book equity in SEK |
| revenue | Float64 | Annual revenue in SEK |
| profit | Float64 | Annual profit in SEK |
| sector_code | Utf8 | NACE sector code |

### Ownership Edges

The ownership graph edges should include:

| Column | Type | Description |
|--------|------|-------------|
| source_id | Utf8 | Household or firm identifier |
| target_id | Utf8 | Firm or asset identifier |
| ownership_share | Float64 | Ownership fraction in [0, 1] |
| ownership_type | Utf8 | Type of ownership (direct, indirect) |

## Wealth Valuation Methods

### Listed Equity

```python
from formogenhetsanalys.valuation.listed_equity import value_listed_equity

holdings_df = pl.DataFrame({
    "isin": ["SE0001"],
    "quantity": [100.0],
    "currency": ["SEK"],
})

prices_df = pl.DataFrame({
    "isin": ["SE0001"],
    "date": [pl.lit("2022-12-31").str.to_date()],
    "close_price": [150.0],
})

valued = value_listed_equity(holdings_df, prices_df)
```

### Unlisted Equity

```python
from formogenhetsanalys.valuation.unlisted_equity import (
    book_value,
    capitalised_earnings,
    transaction_multiples,
)

# Book value method
valued_book = book_value(equity_series)

# Capitalised earnings method
valued_cap = capitalised_earnings(profit_series, sector_series)

# Transaction multiples method
valued_mult = transaction_multiples(revenue_series, sector_series)
```

### Real Estate

```python
from formogenhetsanalys.valuation.real_estate import taxeringsvarde_to_market

# Convert tax assessment value to market value
market_value = taxeringsvarde_to_market(taxeringsvarde_series, coefficient=0.75)
```

## Estimation Methods

### Top Shares

```python
from formogenhetsanalys.estimation.top_shares import top_share, top_shares_bootstrap

# Simple top share
top_1pct = top_share(wealth_array, quantile=0.99)

# Bootstrap confidence intervals
result = top_shares_bootstrap(wealth_array, quantiles=[0.99, 0.999], n_boot=200, seed=42)
print(f"Point estimate: {result[0.99]['point']}")
print(f"95% CI: [{result[0.99]['ci_lo']}, {result[0.99]['ci_hi']}]")
```

### Inequality Indices

```python
from formogenhetsanalys.estimation.decomposition import gini, atkinson, theil

g = gini(wealth_array)
a = atkinson(wealth_array, epsilon=0.5)
t = theil(wealth_array)
```

### DNA Adjustment

```python
from formogenhetsanalys.estimation.dna_adjustment import dna_adjustment

# Align micro data to macro totals
adjusted = dna_adjustment(
    households_df,
    macro_total_sek=1.5e12,
    hfcs_benchmarks={0.99: 0.25},
    hfcs_weight=0.3,
)
```

## Graph Neural Networks

### Building the Graph

```python
from formogenhetsanalys.graph.builder import build_graph

graph = build_graph(
    households_df=households_df,
    firms_df=firms_df,
    assets_df=assets_df,
    ownership_df=ownership_df,
)
```

### Training a GNN

```python
from formogenhetsanalys.models.hetero_gnn import get_model

model = get_model(
    architecture="r-gcn",
    node_types=["household", "firm"],
    edge_types=[("household", "ownership", "firm")],
    hidden_dim=64,
    num_layers=2,
    seed=42,
)

# Forward pass
embeddings = model.forward(node_features, edge_index_dict)
```

## Reporting

### Generating Figures

```python
from formogenhetsanalys.reporting.figures import FigureBuilder

fb = FigureBuilder(output_dir=pathlib.Path("reports/figures"))
fb.top_share_trajectory(years=[2015, 2016, 2017], shares=[0.25, 0.26, 0.24])
fb.lorenz_curve(wealth_array)
```

### Generating Tables

```python
from formogenhetsanalys.reporting.tables import to_csv_with_bom, to_latex_table

to_csv_with_bom(results_df, pathlib.Path("reports/table.csv"))
to_latex_table(results_df, pathlib.Path("reports/table.tex"))
```

## Reproducibility

All randomness is controlled through the seed system:

```python
from formogenhetsanalys.seeds import set_global_seed, derive_seed

# Set master seed
set_global_seed(19960307)

# Derive deterministic sub-seeds for components
graph_split_seed = derive_seed(19960307, "graph_split")
sampler_seed = derive_seed(19960307, "neighbour_sampler")
```

## License

This project is licensed under EUPL-1.2. See LICENSE for details.
