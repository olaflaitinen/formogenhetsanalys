# Architecture Overview

This document describes the architecture of Förmögenhetsanalys, a graph-aware wealth concentration estimation system.

## System Overview

Förmögenhetsanalys estimates wealth concentration in Sweden by:
1. Ingesting register data on households, firms, and ownership relationships
2. Building a heterogeneous graph linking households, firms, and assets
3. Applying valuation methods to estimate market values
4. Using GNNs and baseline models to estimate hidden ownership
5. Computing inequality metrics and top shares
6. Aligning micro-data with macro totals via DNA adjustment
7. Generating reports with figures and tables

## Package Structure

```
src/formogenhetsanalys/
├── __init__.py          # Package entry point, re-exports Config, Pipeline
├── _version.py          # Version string
├── config.py            # Pydantic Config model with all pipeline parameters
├── seeds.py             # Global seed management and deterministic sub-seed derivation
├── logging.py           # Structlog configuration
├── cli.py               # Typer CLI commands
├── paths.py             # Path constants (SYNTHETIC_ROOT, etc.)
├── ingestion/           # Data ingestion and synthetic data generation
│   ├── wealth_register.py
│   ├── firm_register.py
│   ├── asset_prices.py
│   └── manifest.py
├── graph/               # Graph schema, builder, loaders, sampling
│   ├── schema.py        # Pydantic node and edge types
│   ├── builder.py       # Convert tabular data to torch_geometric HeteroData
│   ├── loaders.py       # Train/val/test splits, mini-batching
│   └── sampling.py      # Negative-edge sampling
├── valuation/           # Asset valuation methods
│   ├── listed_equity.py
│   ├── unlisted_equity.py
│   ├── real_estate.py
│   └── harmonisation.py
├── models/              # GNN architectures and Bayesian models
│   ├── hetero_gnn.py    # RGCN, HeteroGAT, HeteroTransformer, GraphSAGEHetero
│   ├── bayesian_priors.py
│   ├── variational.py
│   └── baselines.py
├── estimation/          # Top shares, inequality indices, DNA adjustment
│   ├── top_shares.py
│   ├── decomposition.py
│   └── dna_adjustment.py
├── pipelines/           # DAG orchestration and full pipeline runner
│   ├── dag.py           # Content-addressed DAG with task caching
│   └── runner.py        # Full estimation pipeline
├── evaluation/          # Metrics, bootstrap, posterior diagnostics
│   ├── metrics.py
│   ├── bootstrap.py
│   └── posterior.py
└── reporting/           # Figures, tables, PDF/A output
    ├── figures.py
    ├── tables.py
    └── pdf_a.py
```

## Graph Schema

The graph is a heterogeneous graph with the following node and edge types:

### Node Types

- **HouseholdNode**: Represents a household with wealth components
  - Fields: household_id, total_wealth, financial_wealth, real_estate_wealth, business_wealth, debt, year

- **FirmNode**: Represents a company
  - Fields: firm_id, org_nr, is_fåmansföretag, equity_book, revenue, profit, sector_code, year

- **AssetNode**: Represents an asset (real estate, listed equity)
  - Fields: asset_id, asset_type, value_market, value_book, isin, year

### Edge Types

- **OwnershipEdge**: Ownership relationship between household/firm and firm/asset
  - Fields: source_id, target_id, ownership_share, ownership_type, year

- **KinshipEdge**: Familial relationship between individuals (for intergenerational wealth transfer)
  - Fields: source_id, target_id, kinship_type, year

## Valuation Methods

### Listed Equity
- Market price valuation using closing prices on valuation date
- Optional FX adjustment for foreign-listed securities

### Unlisted Equity
- Book value method: Use reported equity book value
- Capitalised earnings: Apply sector-specific P/E multiples
- Transaction multiples: Apply sector-specific revenue/EBITDA multiples

### Real Estate
- Taxeringsvärde to market conversion using purchase coefficients
- Hedonic index adjustment for price trends

### Harmonisation
- Blend multiple valuation methods
- Sensitivity analysis across methods

## GNN Architectures

The package supports several heterogeneous GNN architectures:

- **RGCN**: Relational Graph Convolutional Network (Schlichtkrull et al., 2018)
- **HeteroGAT**: Heterogeneous Graph Attention Network
- **HeteroTransformer**: Transformer-based heterogeneous graph network
- **GraphSAGEHetero**: GraphSAGE adapted for heterogeneous graphs

All architectures support CPU-only operation via stub implementations when torch/torch_geometric are not available.

## Bayesian Inference

### Priors
- **BetaPrior**: For ownership share parameters in (0, 1)
- **TruncatedNormalPrior**: For valuation multipliers in [0, 1]

### Posteriors
- **MeanFieldPosterior**: Mean-field Beta variational family
- **LowRankPosterior**: Low-rank multivariate Normal for correlated parameters

### Inference
- ELBO (Evidence Lower Bound) optimization
- IWAE (Importance Weighted Autoencoder) bound

## Baseline Models

- **register_aggregate**: Use register-reported wealth directly
- **ownership_chain_expansion**: Expand ownership chains to estimate hidden ownership
- **spectral_clustering**: Cluster firms and assign aggregate cluster wealth

## Estimation Pipeline

1. **Ingestion**: Load wealth register, firm register, ownership edges
2. **Graph Building**: Convert tabular data to HeteroData
3. **Valuation**: Apply valuation methods to estimate market values
4. **GNN Training**: Train heterogeneous GNN on ownership prediction task
5. **Ownership Inference**: Predict hidden ownership shares
6. **Wealth Estimation**: Combine direct and inferred ownership
7. **DNA Adjustment**: Align micro-data to macro totals
8. **Metric Computation**: Compute top shares, Gini, Atkinson, Theil
9. **Reporting**: Generate figures and tables

## Reproducibility

All randomness is controlled through a deterministic seed hierarchy:

- Master seed: Config.seed (default: 20251008)
- Sub-seeds: Derived via SHA256 hash for each namespace (graph_split, neighbour_sampler, etc.)
- Global seeding: NumPy, PyTorch (including CUDA), JAX, Python random

## Content-Addressed DAG

The pipeline uses a content-addressed DAG for task orchestration:

- Each task has a cache key based on its function and input hashes
- Tasks are cached and reused when inputs are unchanged
- Topological sort ensures correct execution order
- Content-addressing enables reproducible receipts via SHA256

## Evaluation Metrics

- **Reconstruction MAE**: Mean absolute error of wealth reconstruction
- **Kendall tau**: Rank correlation of predicted vs true wealth
- **ROC-AUC**: Link prediction performance
- **Coverage**: Fraction of true values inside prediction intervals
- **Interval Width**: Mean width of prediction intervals

## Reporting

### Figures
- Top-share trajectories over time
- Lorenz curves
- Decomposition bar charts
- All generated as PDF and PNG

### Tables
- CSV with UTF-8 BOM for Excel compatibility
- Parquet for programmatic access
- LaTeX for publications
- Minimal PDF/A-compatible HTML

## License and Compliance

- Primary licence: EUPL-1.2
- Synthetic data: CC0-1.0
- Documentation: CC-BY-4.0
- REUSE 3.0 compliance via .reuse/dep5
- No personal data or real wealth records committed
