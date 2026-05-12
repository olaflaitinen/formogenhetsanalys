# FAIR4RS Compliance

This document describes compliance with FAIR (Findable, Accessible, Interoperable, Reusable) principles for research software.

## Findable

### Persistent Identifier
- DOI assigned via Zenodo (.zenodo.json configured)
- Versioned releases with semantic versioning
- Citation metadata in CITATION.cff
- Registered on GitHub with proper metadata

### Rich Metadata
- Comprehensive documentation in docs/
- README.md with installation and usage
- GOVERNANCE.md with project metadata
- CODE_OF_CONDUCT.md and MAINTAINERS.md

### Searchable
- Indexed by GitHub search
- Zenodo metadata indexed by search engines
- Keywords: wealth, inequality, GNN, Sweden, register data

## Accessible

### Open Access
- All source code available under EUPL-1.2
- Documentation available under CC-BY-4.0
- Synthetic data available under CC0-1.0
- Repository publicly accessible on GitHub

### Authentication/Authorization
- No authentication required for access
- Register data requires SCB microdata access (separate process)
- API access planned for synthetic data

### Protocol
- Standard Git protocol for code access
- HTTPS for web interface
- SSH for push access with authentication
- Zenodo for DOI resolution

## Interoperable

### Standard Formats
- Python 3.12 (standard version)
- Parquet for data (standard columnar format)
- GraphML for graphs (standard graph format)
- CSV with UTF-8 BOM (Excel compatible)
- PDF/A-2u for long-term preservation

### Vocabulary
- Standard Python data science stack (NumPy, Polars, Pydantic)
- PyTorch Geometric for GNNs
- Standard inequality metrics (Gini, Atkinson, Theil)
- NACE sector codes for industry classification

### References
- External dependencies properly declared in pyproject.toml
- License texts in LICENSES/ directory
- Citation of related work in documentation
- References to data sources in docs/data.md

## Reusable

### Clear License
- EUPL-1.2 for code (clear copyleft terms)
- CC0-1.0 for synthetic data (public domain)
- CC-BY-4.0 for documentation (attribution required)
- REUSE 3.0 compliance verified

### Associated Documentation
- User guide in docs/user_guide.md
- API reference in docs/api.md
- Architecture documentation in docs/architecture.md
- Methodology in docs/methodology.md

### Standards Compliance
- PEP 8 for Python code style
- Type hints throughout codebase
- Docstrings in Google style
- Conventional Commits for changelog

### Quality Assurance
- 160 unit tests
- 90% coverage gate
- Ruff linting
- Mypy type checking
- CI/CD automated checks

## Provenance

### Version Control
- Git history preserved
- Signed commits recommended (CONTRIBUTING.md)
- Release tags with semantic versioning
- Zenodo snapshots for DOI

### Attribution
- CITATION.cff with author list
- Maintainer information in MAINTAINERS.md
- License notices in all files
- Attribution of external dependencies

## FAIR4RS Score: EXCELLENT

All four FAIR principles are met with strong implementation.
