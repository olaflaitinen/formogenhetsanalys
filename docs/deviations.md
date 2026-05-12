# Deviations from Standards

This document documents deviations from standard practices in Förmögenhetsanalys.

## DEV-001: License Text Fetching

### Deviation
The CC-BY-4.0 license text is fetched from the Creative Commons canonical source via network, while EUPL-1.2 and CC0-1.0 are committed verbatim.

### Rationale
CC-BY-4.0 is updated more frequently than EUPL-1.2. Fetching ensures we have the latest version.

### Mitigation
- SHA256 hash verification after fetch
- Script: `scripts/fetch_licenses.py`
- Documented in fetch_licenses.py docstring

### Status
Accepted deviation. Documented in scripts/fetch_licenses.py.

## DEV-002: Deferred Imports

### Deviation
Some imports are not at the top-level of files (PLC0415 ruff violation ignored).

### Rationale
Optional dependencies (torch, torch_geometric, jax) may not be installed. Deferring imports allows graceful fallback to stub implementations.

### Affected Files
- cli.py
- estimation/dna_adjustment.py
- estimation/decomposition.py
- evaluation/metrics.py
- evaluation/posterior.py
- graph/builder.py
- graph/sampling.py
- models/bayesian_priors.py
- models/hetero_gnn.py
- models/variational.py
- pipelines/runner.py
- reporting/pdf_a.py
- seeds.py
- valuation/harmonisation.py

### Status
Accepted deviation. Per-file ignores in pyproject.toml.

## DEV-003: Magic Values

### Deviation
Magic values used in comparisons (PLR2004 ruff violation ignored).

### Rationale
Constants like 1e-12 for numerical tolerance are self-explanatory in context.

### Affected Files
- estimation/decomposition.py
- estimation/top_shares.py

### Status
Accepted deviation. Per-file ignores in pyproject.toml.

## DEV-004: Zip Without Strict

### Deviation
zip() calls without explicit strict= parameter (B905 ruff violation ignored).

### Rationale
Backward compatibility with Python < 3.10. Default behavior is acceptable.

### Affected Files
- graph/sampling.py
- models/variational.py
- models/baselines.py

### Status
Accepted deviation. Per-file ignores in pyproject.toml.

## DEV-005: Non-ASCII Characters

### Deviation
Non-ASCII characters in source code (PLC2401 ruff violation ignored).

### Rationale
Swedish domain terms (å, ä, ö, företag) require non-ASCII characters for accuracy.

### Affected Files
- graph/schema.py (is_fåmansföretag)
- valuation/harmonisation.py (method names)

### Status
Accepted deviation. Global ignore in pyproject.toml.

## DEV-006: Type Checking Block Imports

### Deviation
Imports in TYPE_CHECKING blocks treated as runtime imports (TC00x ruff violations ignored).

### Rationale
Type hints need these imports at type-checking time but not at runtime.

### Status
Accepted deviation. Global ignore in pyproject.toml.

## DEV-007: Ternary Operator Preference

### Deviation
if/else blocks instead of ternary operators (SIM108 ruff violation ignored).

### Rationale
Ternary operators can reduce readability for complex conditions.

### Status
Accepted deviation. Global ignore in pyproject.toml.

## DEV-008: Unused Arguments

### Deviation
Some function arguments are intentionally unused (ARG001, ARG002 ruff violations ignored).

### Rationale
Required by API design for consistency or future use.

### Affected Files
- cli.py
- pipelines/runner.py
- models/baselines.py
- ingestion/asset_prices.py
- models/hetero_gnn.py

### Status
Accepted deviation. Per-file ignores in pyproject.toml.

## DEV-009: Line Length

### Deviation
Some lines exceed 100 characters (E501 ruff violation ignored).

### Rationale
Some URLs, long variable names, or mathematical expressions cannot be reasonably shortened.

### Affected Files
- models/hetero_gnn.py

### Status
Accepted deviation. Per-file ignore in pyproject.toml.

## DEV-010: Pydantic Module Subclassing

### Deviation
Class cannot subclass Module due to torch.nn.Module being Any (mypy misc error ignored).

### Rationale
Pydantic stub for torch.nn.Module causes this. Type ignore added.

### Affected Files
- models/hetero_gnn.py

### Status
Accepted deviation. Type ignore comment in source.

## Future Deviations

Any new deviations will be documented here with:
- DEV-XXX identifier
- Description of deviation
- Rationale
- Mitigation
- Status
