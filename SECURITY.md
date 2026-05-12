# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |

## Reporting a Vulnerability

Report security vulnerabilities **privately** to the lead maintainer.

**Primary contact:** [olaf.laitinen@su.se](mailto:olaf.laitinen@su.se)
**Fallback contact:** [olaf.laitinen@gmail.com](mailto:olaf.laitinen@gmail.com)

Do NOT open a public GitHub issue for security vulnerabilities.

Include in your report:
- A clear description of the vulnerability and its potential impact.
- Steps to reproduce.
- Affected versions.
- Any suggested mitigations.

## Disclosure Timeline

- **Day 0** - Report received; acknowledgement within 48 hours.
- **Day 14** - Initial assessment and severity classification communicated.
- **Day 90** - Fix released (or extended deadline agreed with reporter).
- **Day 90+** - Public disclosure coordinated with reporter.

This policy aligns with the [90-day disclosure standard](https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-faq.html).

## NIS2-Aligned Secure Development Lifecycle

This project applies the following controls in line with Directive (EU) 2022/2555 (NIS2):

- **Dependency pinning** - all dependencies pinned via `uv.lock`; updated weekly
  by Dependabot.
- **Vulnerability scanning** - `pip-audit --strict` runs on every CI push and
  pull request; `osv-scanner` runs nightly against `uv.lock`.
- **Static analysis** - `bandit -r src -lll` gates every CI run; CodeQL
  analyses the Python codebase weekly.
- **SBOM** - CycloneDX 1.5 JSON SBOM produced on every release via
  `cyclonedx-py environment`.
- **Signed releases** - release artefacts (sdist and wheel) are signed with
  [sigstore](https://www.sigstore.dev/) via GitHub OIDC trusted publisher.
- **OpenSSF Scorecard** - runs weekly; score published in the README badge.
- **Secret scanning** - gitleaks runs in pre-commit and in CI on every push.
- **No real personal data** - the repository contains no personal data, no real
  wealth records, and no real ownership chains. The `.gitleaks.toml` deny-list
  blocks personnummer, organisationsnummer, and IBAN patterns.
- **GNN weight privacy** - trained model weights from real administrative
  microdata are never committed. Only weights trained on the synthetic graph
  fixture may be committed, and only as CI test artefacts.

## Responsible Disclosure

We follow responsible disclosure. Once a fix is released, a CVE may be
requested from the GitHub Advisory Database if the severity warrants it.
