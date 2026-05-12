# Methodology

This document describes the methodological approach for wealth concentration estimation in Förmögenhetsanalys.

## Overview

The methodology combines:
1. **Register data**: Wealth register, firm register, ownership chains
2. **Graph modeling**: Heterogeneous graphs linking households, firms, and assets
3. **GNN inference**: Neural networks to predict hidden ownership
4. **Bayesian quantification**: Uncertainty bounds via variational inference
5. **DNA adjustment**: Alignment with macro totals

## Graph Construction

The wealth network is modeled as a heterogeneous graph:
- **Nodes**: Households, firms, assets
- **Edges**: Ownership relationships, kinship relationships

Node features include wealth components, sector codes, and firm characteristics.

## Valuation Methods

### Listed Equity
- Market price valuation using closing prices
- FX adjustment for foreign holdings

### Unlisted Equity
- Book value method
- Capitalised earnings (sector-specific P/E multiples)
- Transaction multiples (sector-specific revenue/EBITDA)

### Real Estate
- Taxeringsvärde to market conversion
- Hedonic index adjustment

## GNN Architectures

We support several heterogeneous GNN architectures:
- **RGCN**: Relational Graph Convolutional Network
- **HeteroGAT**: Heterogeneous Graph Attention Network
- **HeteroTransformer**: Transformer-based heterogeneous graph network
- **GraphSAGEHetero**: GraphSAGE adapted for heterogeneous graphs

## Inequality Metrics

- **Top shares**: Fraction of wealth held by top quantiles
- **Gini coefficient**: Standard inequality measure
- **Atkinson index**: Social welfare-based inequality
- **Theil index**: Entropy-based inequality

## DNA Adjustment

Distributional National Accounts adjustment aligns micro-data with macro totals using:
- HFCS benchmark blending
- Top-share constraints
- Scaling factors
