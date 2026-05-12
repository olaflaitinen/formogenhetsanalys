# Governance

Förmögenhetsanalys follows a **lead-maintainer model**.

## Lead Maintainer

Dr. Gustav Olaf Yunus Laitinen-Fredriksson Lundström Imanov, MD, RA, PhD
([olaf.laitinen@su.se](mailto:olaf.laitinen@su.se))
Department of Economics, Stockholm University
ORCID: [0009-0006-5184-0810](https://orcid.org/0009-0006-5184-0810)

The lead maintainer has final say over the project direction, release decisions,
and any unresolved disputes.

## Decision Process

1. **Routine changes** (bug fixes, documentation, dependency bumps) - any
   maintainer may merge after one approval.
2. **Significant changes** (new models, new data sources, API changes, licence
   changes) - require explicit sign-off from the lead maintainer.
3. **Breaking changes** - require an updated CHANGELOG entry, a deprecation
   notice in the prior minor version, and lead-maintainer sign-off.

## Becoming a Maintainer

Contributors who make sustained, high-quality contributions may be invited to
join the MAINTAINERS roster. The lead maintainer issues invitations. Maintainers
are listed in `MAINTAINERS.md`.

## European Commission Open Source Software Strategy Alignment

This project reflects the six operational principles of the European Commission
Open Source Software Strategy 2020-2023 (C(2020)7149 final):

- **Think Open** - default to open-source for new software components.
- **Transform** - adopt open standards and interoperable formats throughout.
- **Share** - publish all code, data schemas, and documentation publicly.
- **Contribute** - upstream fixes and improvements to third-party dependencies.
- **Secure** - apply SDLC security controls; run pip-audit, bandit, CodeQL, and
  OpenSSF Scorecard on every release.
- **Stay in control** - maintain EUPL-1.2 copyleft; evaluate forks via the
  EUPL compatibility matrix before merging external code.

## Interoperable Europe Act (Regulation (EU) 2024/903)

The repository is designed for submission to the Interoperable Europe Portal
within 30 days of v0.1.0. It publishes machine-readable metadata in
`CITATION.cff`, `.zenodo.json`, and `.reuse/dep5`, and adopts open standards
(Parquet, GraphML, CycloneDX SBOM, SPDX via DEP5).

## Licence Governance

The sole licence is EUPL-1.2. Downstream relicensing is permitted under the
compatible licences listed in the EUPL appendix (GPL v2/v3, AGPL v3, OSL v2.1
and v3.0, EPL v1.0 and v2.0, CeCILL v2.0 and v2.1, MPL v2, LGPL v2.1+,
CC BY-SA 3.0 for non-software, EUPL v1.1 and v1.2, LiLiQ-R and LiLiQ-R+).

No contributor may impose additional restrictions beyond those of the EUPL-1.2.

## Third-Party Dependency Licence Compatibility

| Package group | Typical licence | EUPL-1.2 compatible |
|---|---|---|
| PyTorch | BSD-3-Clause | Yes |
| PyTorch Geometric | MIT | Yes |
| NumPy | BSD-3-Clause | Yes |
| Pandas | BSD-3-Clause | Yes |
| Polars | MIT | Yes |
| scikit-learn | BSD-3-Clause | Yes |
| NetworkX | BSD-3-Clause | Yes |
| NumPyro | Apache-2.0 | Yes |
| JAX | Apache-2.0 | Yes |
| Pydantic | MIT | Yes |
| Typer | MIT | Yes |
| structlog | Apache-2.0 | Yes |
| Matplotlib | PSF | Yes |
| MkDocs | BSD-2-Clause | Yes |
| pytest | MIT | Yes |
| Ruff | MIT | Yes |
| mypy | MIT | Yes |
| REUSE tool | Apache-2.0 | Yes |
| Bandit | Apache-2.0 | Yes |

All dependencies are EUPL-1.2 compatible. The full table is maintained here and
audited on every dependency bump via `pip-audit --strict`.

## Code of Conduct Enforcement

Violations of `CODE_OF_CONDUCT.md` are reported to
[olaf.laitinen@su.se](mailto:olaf.laitinen@su.se) with
[olaf.laitinen@gmail.com](mailto:olaf.laitinen@gmail.com) as fallback.
The lead maintainer responds within five business days.
