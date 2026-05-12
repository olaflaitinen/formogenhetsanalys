# OSOR Compliance

This document describes compliance with the Open Source Software for European Research (OSOR) guidelines.

## Open Source Licensing

### Primary License: EUPL-1.2
- European Union Public Licence version 1.2
- Compatible with GPL-2.0-or-later
- Strong copyleft, requires derivative works to use compatible license
- Chosen for EU research projects

### Secondary Licenses
- **Synthetic data**: CC0-1.0 (public domain dedication)
- **Documentation**: CC-BY-4.0 (attribution required)
- **Licenses directory**: Canonical EUPL-1.2, CC0-1.0, CC-BY-4.0 texts

## Dependency Licensing

All dependencies are EUPL-1.2 compatible:
- Python 3.12: PSF License (compatible)
- NumPy: BSD-3-Clause (compatible)
- Polars: MIT (compatible)
- Pydantic: MIT (compatible)
- Structlog: Apache-2.0 (compatible)
- Typer: MIT (compatible)

See GOVERNANCE.md for full dependency list with license compatibility analysis.

## Open Development Practices

### Public Repository
- Repository hosted on GitHub
- All development is public
- Issues and pull requests welcome
- Contribution guidelines in CONTRIBUTING.md

### Transparency
- All code is open source
- Documentation is publicly available
- Development process is transparent
- Decision-making documented in GOVERNANCE.md

### Code Quality
- Linting with ruff
- Type checking with mypy
- Comprehensive test suite (160 tests)
- 90% coverage gate

## European Interoperability

### Data Formats
- Parquet (columnar storage)
- GraphML (graph interchange)
- CSV with UTF-8 BOM (Excel compatibility)
- PDF/A-2u (long-term preservation)

### Standards Compliance
- REUSE 3.0 for license metadata
- SPDX identifiers for licenses
- Semantic versioning (SemVer)
- Conventional Commits for changelog

### Accessibility
- Documentation in English and Swedish (planned)
- Screen reader compatible HTML output
- High contrast figures
- Alt text for all images

## Community Engagement

### Issue Templates
- Bug reports
- Feature requests
- Security vulnerabilities

### Contribution Process
- DCO sign-off required
- Signed commits preferred
- Code review mandatory
- Contributor licensing agreement via DCO

## Continuous Integration

### Automated Checks
- Linting (ruff)
- Type checking (mypy)
- Testing (pytest)
- Security scanning (pip-audit, bandit)
- REUSE compliance (reuse lint)
