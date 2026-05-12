# Reproducibility

This document describes the reproducibility measures in Förmögenhetsanalys.

## Deterministic Seeding

### Master Seed
All randomness is controlled by a single master seed:
- Default: 20251008 (MODEL_SEED)
- Synthetic data: 19960307 (SYNTHETIC_SEED)
- GNN initialization: 42 (GNN_INIT_SEED)

### Seed Derivation
Sub-seeds are derived deterministically using SHA256:
```python
from formogenhetsanalys.seeds import derive_seed

graph_split_seed = derive_seed(20251008, "graph_split")
sampler_seed = derive_seed(20251008, "neighbour_sampler")
```

### Global Seeding
All random number generators are seeded:
- Python `random` module
- NumPy `np.random`
- PyTorch (including CUDA)
- JAX

See `seeds.py` for implementation.

## Content-Addressed DAG

The pipeline uses a content-addressed DAG for reproducibility:
- Each task has a cache key based on function and input hashes
- Tasks are cached when inputs are unchanged
- SHA256 hash of pipeline output provides reproducibility receipt

## Environment Reproducibility

### Python Version
Pinned to Python 3.12 in `.python-version`.

### Dependency Locking
- `uv.lock` locks exact dependency versions
- `pyproject.toml` specifies version ranges
- Reproducible installation via `uv sync`

### Platform Notes
- CUDA operations: Requires deterministic CUDA settings
- CUBLAS_WORKSPACE_CONFIG=:4096:8 for reproducible GEMM
- PyTorch deterministic algorithms enabled

## Code Reproducibility

### No Mutable Defaults
All functions use immutable defaults or None.

### No Hidden State
All randomness explicit through `derive_seed()`.

### Type Checking
Mypy strict mode ensures type correctness.

### Linting
Ruff enforces consistent code style.

## Test Reproducibility

### Deterministic Tests
- Tests use fixed seeds
- No randomness in test data generation without explicit seed
- `pytest-randomly` for random test order with seed

### Coverage
90% coverage gate ensures all code paths tested.

## Data Reproducibility

### Synthetic Data
Generated deterministically with fixed seeds.

### Register Data
Versioned by reference year (e.g., 2022-12-31).

### Asset Prices
Versioned by date range.

## Output Reproducibility

### Receipt Generation
Each pipeline run generates a SHA256 receipt:
```python
results = pipeline.run_synthetic()
receipt = results["receipt_sha256"]
```

### Figure Reproduction
All figures generated with fixed random seeds.

### Table Reproduction
All calculations deterministic.

## Verification

### Determinism Tests
Run `pytest tests/test_determinism.py -v` to verify bit-identical outputs.

### Receipt Comparison
Use `scripts/compare_receipts.py` to compare receipts across runs.

## Known Non-Determinism

### Platform Differences
- Different OS may produce slightly different floating-point results
- Different CPU architectures may have different precision
- Documented in docs/deviations.md

### GPU Non-Determinism
- Some PyTorch operations are non-deterministic on GPU
- Use CPU for full reproducibility
- Documented in docs/deviations.md
