"""Tests for deterministic reproducibility."""

from __future__ import annotations

import numpy as np
import pytest

from formogenhetsanalys.seeds import set_global_seed, derive_seed


SEED = 19960307


class TestDeterminism:
    def test_numpy_reproducible(self) -> None:
        set_global_seed(42)
        a1 = np.random.rand(10)
        set_global_seed(42)
        a2 = np.random.rand(10)
        np.testing.assert_array_equal(a1, a2)

    def test_derive_seed_deterministic(self) -> None:
        s1 = derive_seed(SEED, "graph_split")
        s2 = derive_seed(SEED, "graph_split")
        assert s1 == s2

    def test_derive_seed_differs_by_namespace(self) -> None:
        s1 = derive_seed(SEED, "graph_split")
        s2 = derive_seed(SEED, "neighbour_sampler")
        assert s1 != s2

    def test_derive_seed_valid_range(self) -> None:
        s = derive_seed(SEED, "test")
        assert 0 <= s <= 2**32 - 1
