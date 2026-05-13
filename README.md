# Förmögenhetsanalys

**Department of Economics, Stockholm University** | Research Software | EUPL-1.2

[![CI](https://github.com/olaflaitinen/formogenhetsanalys/actions/workflows/ci.yml/badge.svg)](https://github.com/olaflaitinen/formogenhetsanalys/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/olaflaitinen/formogenhetsanalys/branch/main/graph/badge.svg)](https://codecov.io/gh/olaflaitinen/formogenhetsanalys)
[![REUSE status](https://api.reuse.software/badge/github.com/olaflaitinen/formogenhetsanalys)](https://api.reuse.software/info/github.com/olaflaitinen/formogenhetsanalys)
[![Release](https://img.shields.io/github/v/release/olaflaitinen/formogenhetsanalys)](https://github.com/olaflaitinen/formogenhetsanalys/releases)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](https://www.python.org)
[![License: EUPL-1.2](https://img.shields.io/badge/license-EUPL--1.2-blue)](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://olaflaitinen.github.io/formogenhetsanalys)
[![OpenSSF Best Practices](https://img.shields.io/badge/OpenSSF-passing-brightgreen)](https://bestpractices.coreinfrastructure.org)
[![GitHub stars](https://img.shields.io/github/stars/olaflaitinen/formogenhetsanalys?style=social)](https://github.com/olaflaitinen/formogenhetsanalys/stargazers)

---

## Abstract

Förmögenhetsanalys is a Python research-software package for network-aware
estimation and decomposition of wealth concentration in Sweden. Conventional
register-based approaches aggregate wealth at the household level and miss the
indirect ownership of assets held through closely held firms (fåmansföretag),
foundations, and layered ownership chains - a dimension that is especially
significant in the upper tail of the wealth distribution and that has grown in
importance since the repeal of the Swedish wealth tax in 2007.

This framework represents households, individuals, firms, foundations, and assets
as nodes in a typed heterogeneous graph, and ownership, kinship, employment, and
residence relationships as typed edges. On this graph, edge-typed message-passing
graph neural networks with multi-head attention propagate latent wealth signals
across ownership chains, recovering beneficial-ownership shares that are not
directly observable in any single register. Bayesian shrinkage priors (Beta and
truncated-Normal) on latent ownership shares regularise the model on rare
edge types, and variational inference (mean-field, low-rank, and normalising-flow
posteriors) quantifies uncertainty over the recovered shares.

Valuation harmonisation modules reconcile three asset classes - listed equity
(market price with FX adjustment), residential real estate (taxeringsvärde
converted via hedonic indices), and unlisted equity (book value, capitalised
earnings, and transaction multiples) - with sensitivity analyses spanning
valuation-method choices. Distributional National Accounts (DNA) adjustments
align top-share estimates with World Inequality Lab macro totals and with
European Central Bank Household Finance and Consumption Survey benchmarks,
enabling comparisons across the EU-27.

The repository ships deterministic synthetic graph fixtures (seed 19960307)
that mimic the schema of Swedish administrative registers without containing any
real personal data. All functionality is exercised against these fixtures in CI.

---

## Compliance Matrix

| Instrument | Status |
|---|---|
| EUPL-1.2 | Sole licence; full text in `LICENSE` and `LICENSES/EUPL-1.2.txt` |
| GDPR (Regulation (EU) 2016/679) | No personal data; lawful basis documented in `docs/gdpr.md` |
| OSOR good-practice expectations | Catalogue metadata in `docs/osor.md` |
| EC OSS Strategy 2020-2023 (C(2020)7149) | Six principles reflected in `GOVERNANCE.md` |
| Interoperable Europe Act (Reg (EU) 2024/903) | Submission planned within 30 days of v0.1.0 |
| REUSE Specification 3.0 (DEP5 only) | `reuse lint` passes; no per-file SPDX headers |
| FAIR4RS principles | Self-assessment in `docs/fair4rs.md` |
| Swedish legal basis (OSL 2009:400, Lag 2001:99) | Documented in `docs/swedish-legal-basis.md` |
| WCAG 2.2 AA | Documentation conformance statement in `docs/accessibility.md` |
| NIS2 Directive (Directive (EU) 2022/2555) | SDLC controls documented in `SECURITY.md` |

---

## Installation

```bash
# Core package (no GNN or Bayesian extras)
pip install formogenhetsanalys

# With GNN support (PyTorch + PyTorch Geometric)
pip install "formogenhetsanalys[gnn]"

# With Bayesian inference (NumPyro + JAX)
pip install "formogenhetsanalys[bayes]"

# Development environment
pip install uv
uv sync --extra dev --extra docs
```

---

## Quickstart on the Synthetic Graph Fixture

```bash
# Generate the synthetic graph fixture
uv run python scripts/make_synthetic_graph.py

# Build the heterogeneous graph
uv run formogenhetsanalys build-graph --synthetic

# Compute top wealth shares
uv run formogenhetsanalys top-shares --synthetic --quantiles 0.99 0.999 0.9999

# Run the full replication pipeline (dry run)
bash replication/run_all.sh --dry-run
```

---

## Data Policy

This repository contains **no personal data, no real wealth records, and no real
ownership chains**. All data shipped with the repository are deterministic
synthetic graph fixtures generated from a fixed seed (SYNTHETIC_SEED = 19960307).

Processing of Swedish administrative microdata is performed exclusively inside
the SCB secure environment (MONA/SAFE) by authorised researchers. The code is
designed to ingest those datasets when run in that environment. See
`docs/swedish-legal-basis.md` and `docs/gdpr.md` for the legal basis.

---

## Methodology Summary

- **Graph architecture:** typed heterogeneous graph with node types (household,
  individual, firm, foundation, asset) and edge types (ownership, kinship,
  employment, residence).
- **GNN models:** R-GCN, HeteroGAT (default), HeteroTransformer, GraphSAGE.
- **Bayesian priors:** Beta(1,1), Beta(2,5) (default), truncated-Normal on
  latent beneficial-ownership shares.
- **Variational inference:** mean-field (default), low-rank multivariate Normal,
  normalising-flow posteriors; ELBO and IWAE losses.
- **Top-share estimation:** empirical quantiles, Pareto tail fitting, bootstrap
  confidence intervals.
- **Decomposition:** Atkinson, Gini, Theil; Shapley-value attribution.
- **DNA adjustment:** alignment with World Inequality Lab macro totals and ECB
  HFCS cross-country benchmarks.

Full methodology in [docs/methodology.md](https://olaflaitinen.github.io/formogenhetsanalys/methodology/).

---

## Documentation

Full documentation: <https://olaflaitinen.github.io/formogenhetsanalys>

Key pages:
- [Methodology](https://olaflaitinen.github.io/formogenhetsanalys/methodology/)
- [Graph schema](https://olaflaitinen.github.io/formogenhetsanalys/graph-schema/)
- [API reference](https://olaflaitinen.github.io/formogenhetsanalys/api/)
- [Reproducibility](https://olaflaitinen.github.io/formogenhetsanalys/reproducibility/)
- [GDPR](https://olaflaitinen.github.io/formogenhetsanalys/gdpr/)
- [EU compliance](https://olaflaitinen.github.io/formogenhetsanalys/eu-compliance/)

---

## Citation

```bibtex
@software{laitinen_fredriksson_lundstrom_imanov_2026_formogenhetsanalys,
  author    = {Laitinen-Fredriksson Lundstr{\"o}m Imanov, Gustav Olaf Yunus},
  title     = {{F{\"o}rm{\"o}genhetsanalys: graph-aware estimation of wealth
                concentration in Sweden}},
  year      = {2026},
  version   = {0.1.0},
  licence   = {EUPL-1.2},
  url       = {https://github.com/olaflaitinen/formogenhetsanalys},
  orcid     = {0009-0006-5184-0810}
}
```

See [docs/citation.md](https://olaflaitinen.github.io/formogenhetsanalys/citation/)
for APA, Chicago, and RIS formats.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributors must sign off with the
DCO, use Conventional Commits, and sign their commits.

## Security

See [SECURITY.md](SECURITY.md). Report vulnerabilities privately to
[olaf.laitinen@su.se](mailto:olaf.laitinen@su.se).

## Governance

Lead-maintainer model. See [GOVERNANCE.md](GOVERNANCE.md).

---

## Maintainer

Dr. Gustav Olaf Yunus Laitinen-Fredriksson Lundström Imanov, MD, RA, PhD
Research Assistant, Department of Economics, Stockholm University
[olaf.laitinen@su.se](mailto:olaf.laitinen@su.se) |
ORCID [0009-0006-5184-0810](https://orcid.org/0009-0006-5184-0810) |
[@olaflaitinen](https://github.com/olaflaitinen)

---

## Portfolio

This is project 2 of 20 in a research portfolio on income, wealth, taxation,
inequality, and intergenerational mobility in Sweden with an explicit EU framing.

Sibling projects: Inkomstprognos, Skatteprogressivitet, Arvsdynamik,
Mobilitetsmodellen, Inkomstklyftan, Pensionsrättvisa, Kapitalinkomst,
Lönedynamik, Hushållsekonomi, Skattereform, Välfärdsmodellen, Generationsskifte,
Demografiprognos, Mikrosimulering, Toppinkomstandelen, Bolagsskatteanalys,
Skatteflyktsdetektor, Förmånsanalys, Omfördelningsmodellen.

---

Licence: European Union Public Licence v. 1.2 (EUPL-1.2).
Copyright 2025-2026 Dr. Gustav Olaf Yunus Laitinen-Fredriksson Lundström Imanov,
MD, RA, PhD, Department of Economics, Stockholm University.
