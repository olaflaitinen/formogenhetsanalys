# Förmögenhetsanalys

Graph-aware estimation of wealth concentration in Sweden.

## Overview

Förmögenhetsanalys is a research package for estimating wealth distribution and inequality in Sweden using heterogeneous graph neural networks. It combines register data, ownership networks, and Bayesian inference to produce robust estimates of top shares, Gini coefficients, and other inequality metrics.

## Features

- **Graph-based wealth modeling**: Heterogeneous graphs linking households, firms, and assets
- **Multiple valuation methods**: Market price, book value, capitalised earnings, transaction multiples
- **GNN architectures**: RGCN, HeteroGAT, HeteroTransformer, GraphSAGEHetero
- **Bayesian inference**: Beta and truncated Normal priors with variational posteriors
- **DNA adjustment**: Align micro-data with macro totals using Distributional National Accounts
- **Reproducibility**: Deterministic seed management and content-addressed DAG
- **Reporting**: PDF/A-2u compliant output with figures and tables

## Installation

```bash
git clone https://github.com/olaflaitinen/formogenhetsanalys.git
cd formogenhetsanalys
pip install uv
uv sync
```

## Quick Start

```python
from formogenhetsanalys import Config, Pipeline, set_global_seed
import pathlib

config = Config(
    data_root=pathlib.Path("data/synthetic"),
    seed=19960307,
    gnn_architecture="r-gcn",
)

set_global_seed(config.seed)
pipeline = Pipeline(config)
results = pipeline.run_synthetic()

print(f"Top-1% share: {results['top_shares'][0.99]}")
print(f"Gini: {results['gini']}")
```

## Documentation

- [User Guide](user_guide.md) - How to use the package
- [Architecture](architecture.md) - System architecture and design
- [API Reference](api.md) - API documentation

## Citation

```bibtex
@software{formogenhetsanalys2025,
  author = {Laitinen-Fredriksson Lundström Imanov, Gustav Olaf Yunus},
  title = {Förmögenhetsanalys: Graph-Aware Wealth Concentration Estimation},
  year = {2025},
  url = {https://github.com/olaflaitinen/formogenhetsanalys},
  license = {EUPL-1.2}
}
```

## License

This project is licensed under the European Union Public Licence 1.2 (EUPL-1.2). See [LICENSE](../LICENSE) for details.

## Contact

Maintainer: Dr. Gustav Olaf Yunus Laitinen-Fredriksson Lundström Imanov

Repository: https://github.com/olaflaitinen/formogenhetsanalys
