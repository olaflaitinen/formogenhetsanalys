# Contributing to Förmögenhetsanalys

Thank you for your interest in contributing. This document describes the process
and requirements that must be met before a contribution can be merged.

## Legal Requirements

### Developer Certificate of Origin (DCO)

Every commit must carry a DCO sign-off line:

```
Signed-off-by: Full Name <email@example.com>
```

Add it automatically with `git commit -s`. By signing off you certify that you
wrote the contribution or have the right to submit it under the EUPL-1.2 licence,
as per the [DCO 1.1](https://developercertificate.org/).

### Signed Commits

Commits must be GPG- or SSH-signed. Configure signing:

```bash
git config --global commit.gpgsign true
git config --global user.signingkey <YOUR_KEY_ID>
```

### EUPL-1.2 Compatibility

All new dependencies must be EUPL-1.2 compatible (see the compatible licences
listed in the EUPL appendix). Check against `docs/governance.md` before adding
a dependency.

## Commit Format

This repository enforces [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

Format: `<type>(<scope>): <description>`

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`,
`build`, `ci`, `chore`, `revert`.

Example: `feat(models): add low-rank variational posterior`

Breaking changes must use `BREAKING CHANGE:` footer or `!` suffix.

## Branching Policy

- `main` is the stable branch; direct pushes are blocked.
- Feature branches: `feat/<short-description>`.
- Bug-fix branches: `fix/<short-description>`.
- Documentation branches: `docs/<short-description>`.
- Open a pull request against `main`; at least one review is required.

## Development Setup

```bash
# Install uv (if not already installed)
pip install uv

# Clone and enter the repository
git clone https://github.com/olaflaitinen/formogenhetsanalys.git
cd formogenhetsanalys

# Install all extras
uv sync --extra dev --extra docs

# Install pre-commit hooks
uv run pre-commit install

# Fetch canonical licence texts (CC-BY-4.0)
uv run python scripts/fetch_licenses.py

# Run the full check suite via nox
uv run nox -s lint type test cov docs reuse audit
```

## REUSE Compliance

Every file must be covered by `.reuse/dep5`. Do NOT add per-file SPDX headers.
After adding new files, run `uv run reuse lint` and fix any uncovered paths by
adding a paragraph to `.reuse/dep5`.

## GDPR - No Personal Data

No personal data, real wealth records, real ownership chains, or trained model
weights derived from real data may be committed at any time. Run
`uv run gitleaks detect --source .` before pushing.

## GNN Reproducibility

When modifying training code, ensure deterministic outputs:

- Call `set_global_seed(seed)` before any tensor allocation.
- Set `torch.use_deterministic_algorithms(True)`.
- Set environment variable `CUBLAS_WORKSPACE_CONFIG=:4096:8`.
- Set `torch.backends.cudnn.deterministic = True`.
- Set `torch.backends.cudnn.benchmark = False`.
- Use JAX with `jax.config.update("jax_enable_x64", True)` for double precision.

Run `pytest tests/test_determinism.py -v` to verify. Two independent runs with
the same seed must produce bit-identical GNN weights on the same platform and
wheel set. Document any unavoidable non-determinism in `docs/reproducibility.md`.

## Code Style

- Line length: 100 characters (Python), 120 characters (YAML/TOML).
- Formatter: `ruff format` (sole formatter; do not use black or isort separately).
- Linter: `ruff check` with rule sets E, F, I, B, UP, SIM, PL, S, A, COM,
  PIE, RET, TCH, ARG, DTZ.
- Type checker: `mypy --strict`.
- Docstrings: Google style, parsed by mkdocstrings.
- No `print()` outside `cli.py`. No bare `except`. No mutable defaults.
- Use `pathlib.Path`; all randomness via `seeds.derive_seed`.

## Testing

- Add at least one unit test for every public function or class.
- Use `hypothesis` for property-based tests on graph builders and valuation routines.
- Coverage gate: 90 percent (lines and branches).
- Run: `pytest -x -q --cov=formogenhetsanalys --cov-branch --cov-fail-under=90`.

## Documentation

- Add or update the relevant page in `docs/` for any user-visible change.
- Run `mkdocs build --strict` to verify no broken links.

## Reporting Issues

Use the GitHub issue templates in `.github/ISSUE_TEMPLATE/`. For security
vulnerabilities see `SECURITY.md`.
