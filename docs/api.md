# API Reference

This page provides an overview of the main public APIs in Förmögenhetsanalys.

## Core

### `Config`

Configuration model for the pipeline.

```python
from formogenhetsanalys import Config

config = Config(
    data_root=pathlib.Path("data"),
    seed=19960307,
    gnn_architecture="r-gcn",
    bayesian_prior="beta-2-5",
    posterior="mean-field",
    valuation="market",
    n_jobs=1,
    device="cpu",
)
```

**Fields:**
- `data_root`: Path to data directory
- `seed`: Master random seed
- `gnn_architecture`: GNN architecture (r-gcn, hetero-gat, hetero-transformer, graphsage)
- `bayesian_prior`: Prior distribution type
- `posterior`: Variational posterior type
- `valuation`: Valuation method
- `n_jobs`: Number of parallel jobs
- `device`: Device for GNN (cpu, cuda)

### `Pipeline`

Main pipeline orchestrator.

```python
from formogenhetsanalys import Pipeline

pipeline = Pipeline(config)
results = pipeline.run_synthetic()
```

**Methods:**
- `run_synthetic()`: Run pipeline on synthetic data
- `load_synthetic_parquet()`: Load pre-computed synthetic results

### `set_global_seed`

Set global seed for all random number generators.

```python
from formogenhetsanalys import set_global_seed

set_global_seed(19960307)
```

## Ingestion

### `synthetic_wealth_register`

Generate synthetic household wealth data.

```python
from formogenhetsanalys.ingestion.wealth_register import synthetic_wealth_register

df = synthetic_wealth_register(n=200, seed=19960307)
```

### `synthetic_firm_register`

Generate synthetic firm data.

```python
from formogenhetsanalys.ingestion.firm_register import synthetic_firm_register

df = synthetic_firm_register(n=50, seed=19960307)
```

### `synthetic_asset_prices`

Generate synthetic asset price series.

```python
from formogenhetsanalys.ingestion.asset_prices import synthetic_asset_prices

prices = synthetic_asset_prices(start_year=2020, end_year=2023, seed=19960307)
```

## Graph

### `build_graph`

Build heterogeneous graph from tabular data.

```python
from formogenhetsanalys.graph.builder import build_graph

graph = build_graph(
    households_df=households_df,
    firms_df=firms_df,
    assets_df=assets_df,
    ownership_df=ownership_df,
)
```

### `get_model`

Factory function for GNN architectures.

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
```

## Valuation

### `value_listed_equity`

Value listed equity holdings at market price.

```python
from formogenhetsanalys.valuation.listed_equity import value_listed_equity

valued = value_listed_equity(holdings_df, price_series_df, fx_rates_df, "2022-12-31")
```

### `capitalised_earnings`

Valuation using capitalised earnings method.

```python
from formogenhetsanalys.valuation.unlisted_equity import capitalised_earnings

valued = capitalised_earnings(profit_series, sector_series, pe_override=18.0)
```

### `taxeringsvarde_to_market`

Convert tax assessment value to market value.

```python
from formogenhetsanalys.valuation.real_estate import taxeringsvarde_to_market

market_value = taxeringsvarde_to_market(taxeringsvarde_series, coefficient=0.75)
```

### `harmonise_valuations`

Harmonise multiple valuation methods.

```python
from formogenhetsanalys.valuation.harmonisation import harmonise_valuations

harmonised = harmonise_valuations(households_df, firms_df, method="book")
```

## Estimation

### `top_share`

Compute top quantile share of wealth.

```python
from formogenhetsanalys.estimation.top_shares import top_share

share = top_share(wealth_array, quantile=0.99)
```

### `top_shares_bootstrap`

Bootstrap confidence intervals for top shares.

```python
from formogenhetsanalys.estimation.top_shares import top_shares_bootstrap

result = top_shares_bootstrap(wealth_array, quantiles=[0.99, 0.999], n_boot=200, seed=42)
```

### `gini`, `atkinson`, `theil`

Inequality indices.

```python
from formogenhetsanalys.estimation.decomposition import gini, atkinson, theil

g = gini(wealth_array)
a = atkinson(wealth_array, epsilon=0.5)
t = theil(wealth_array)
```

### `dna_adjustment`

Distributional National Accounts adjustment.

```python
from formogenhetsanalys.estimation.dna_adjustment import dna_adjustment

adjusted = dna_adjustment(households_df, macro_total_sek=1.5e12)
```

## Reporting

### `FigureBuilder`

Generate publication-quality figures.

```python
from formogenhetsanalys.reporting.figures import FigureBuilder

fb = FigureBuilder(output_dir=pathlib.Path("reports/figures"))
fb.top_share_trajectory(years=[2015, 2016, 2017], shares=[0.25, 0.26, 0.24])
fb.lorenz_curve(wealth_array)
```

### `to_csv_with_bom`, `to_parquet`, `to_latex_table`

Export tables in various formats.

```python
from formogenhetsanalys.reporting.tables import (
    to_csv_with_bom,
    to_parquet,
    to_latex_table,
)

to_csv_with_bom(df, pathlib.Path("table.csv"))
to_parquet(df, pathlib.Path("table.parquet"))
to_latex_table(df, pathlib.Path("table.tex"))
```

## Seeds

### `derive_seed`

Derive deterministic sub-seed from master seed.

```python
from formogenhetsanalys.seeds import derive_seed

graph_seed = derive_seed(19960307, "graph_split")
```

### `SYNTHETIC_SEED`, `MODEL_SEED`, `GNN_INIT_SEED`

Standard seed constants.

```python
from formogenhetsanalys.seeds import SYNTHETIC_SEED, MODEL_SEED, GNN_INIT_SEED

print(SYNTHETIC_SEED)  # 19960307
print(MODEL_SEED)      # 20251008
print(GNN_INIT_SEED)   # 42
```

For detailed docstrings, use `help()` or your IDE's autocomplete.
