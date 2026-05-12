# Changelog

All notable changes to Förmögenhetsanalys are documented in this file.

The format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).
Versions follow [PEP 440](https://peps.python.org/pep-0440/) and
[Semantic Versioning 2.0.0](https://semver.org/).
Commits follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

## [Unreleased]

## [0.1.0] - 2026-05-12

### Added

- Initial release of Förmögenhetsanalys v0.1.0.
- Heterogeneous graph schema covering households, individuals, firms, foundations, and assets.
- Graph builder producing `torch_geometric.data.HeteroData` objects.
- Neighbour samplers, mini-batch construction, and train/val/test split utilities.
- GNN architectures: R-GCN, HeteroGAT, HeteroTransformer, GraphSAGE (CPU-only CI).
- Bayesian priors: BetaPrior (Beta(1,1), Beta(2,5)) and TruncatedNormalPrior.
- Variational inference: mean-field, low-rank, and normalising-flow posteriors.
- Valuation modules: listed equity, unlisted equity (book/capitalised/multiples), real estate.
- Valuation harmonisation and sensitivity analysis.
- Top-share estimation with Pareto tail fitting.
- Decomposition: Atkinson, Gini, Theil, Shapley-value attribution.
- Distributional National Accounts adjustment aligned with World Inequality Lab.
- Typer CLI with subcommands: ingest, build-graph, train, evaluate, top-shares, decompose, report, repro, audit, sbom, reuse-check.
- Pydantic v2 configuration model.
- Structlog-based structured logging (JSON in CI, console locally).
- Pipeline DAG with content-addressed outputs.
- Evaluation metrics: MAE reconstruction, Kendall tau ranking, ROC-AUC link prediction, coverage, interval width.
- Block bootstrap and jackknife for top-share sensitivity.
- Posterior-predictive intervals and PIT histograms.
- Reporting: matplotlib figures (PNG/SVG/PDF-A-2u), CSV with UTF-8 BOM, Parquet, LaTeX tables.
- Synthetic graph fixture: 20 000 households, 5 000 firms, 500 foundations, 100 000 assets, 250 000 edges, generated from SYNTHETIC_SEED = 19960307.
- Full test suite with 90 percent coverage gate.
- Determinism tests for synthetic graph generation and GNN weights.
- REUSE 3.0 compliance via DEP5 bulk declaration.
- EUPL-1.2 licence.
- GDPR, Swedish legal basis, DPIA summary, and OSOR documentation.
- FAIR4RS self-assessment.
- MkDocs Material documentation site.
- GitHub Actions CI matrix (ubuntu-22.04, macos-14, windows-2022) on Python 3.11 and 3.12.
- Release workflow with sigstore signing and Zenodo deposition.
- CycloneDX 1.5 JSON SBOM.
- OpenSSF Scorecard and CodeQL analysis.
- Stata 17 replication kit stubs.
- R diagnostic and decomposition-plot stubs.

[Unreleased]: https://github.com/olaflaitinen/formogenhetsanalys/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/olaflaitinen/formogenhetsanalys/releases/tag/v0.1.0
