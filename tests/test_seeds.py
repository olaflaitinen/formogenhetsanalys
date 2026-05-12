"""Tests for reproducibility seed management."""

from __future__ import annotations

import numpy as np
import pytest

from formogenhetsanalys.seeds import (
    GNN_INIT_SEED,
    MODEL_SEED,
    SYNTHETIC_SEED,
    derive_seed,
    set_global_seed,
)


def test_seed_constants_match_spec() -> None:
    assert SYNTHETIC_SEED == 19960307
    assert MODEL_SEED == 20251008
    assert GNN_INIT_SEED == 42


def test_derive_seed_deterministic() -> None:
    s1 = derive_seed(SYNTHETIC_SEED, "wealth_register")
    s2 = derive_seed(SYNTHETIC_SEED, "wealth_register")
    assert s1 == s2


def test_derive_seed_differs_by_name() -> None:
    s1 = derive_seed(SYNTHETIC_SEED, "wealth_register")
    s2 = derive_seed(SYNTHETIC_SEED, "firm_register")
    assert s1 != s2


def test_derive_seed_valid_range() -> None:
    s = derive_seed(SYNTHETIC_SEED, "test")
    assert 0 <= s <= 2**32 - 1


def test_set_global_seed_numpy() -> None:
    set_global_seed(42)
    a = np.random.rand()
    set_global_seed(42)
    b = np.random.rand()
    assert a == pytest.approx(b)
