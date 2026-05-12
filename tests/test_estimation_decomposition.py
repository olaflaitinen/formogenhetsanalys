"""Tests for inequality decomposition."""

from __future__ import annotations

import numpy as np
import pytest

from formogenhetsanalys.estimation.decomposition import gini, atkinson, theil, shapley_decomposition


SEED = 19960307
RNG = np.random.default_rng(SEED)
WEALTH = RNG.lognormal(13.0, 2.0, 500)


class TestDecomposition:
    def test_gini_equal_distribution(self) -> None:
        assert gini(np.ones(100)) == pytest.approx(0.0, abs=1e-10)

    def test_gini_range(self) -> None:
        g = gini(WEALTH)
        assert 0.0 <= g <= 1.0

    def test_atkinson_equal_distribution(self) -> None:
        assert atkinson(np.ones(100)) == pytest.approx(0.0, abs=1e-10)

    def test_atkinson_range(self) -> None:
        a = atkinson(WEALTH, epsilon=0.5)
        assert 0.0 <= a <= 1.0

    def test_theil_equal_distribution(self) -> None:
        assert theil(np.ones(100)) == pytest.approx(0.0, abs=1e-10)

    def test_theil_non_negative(self) -> None:
        assert theil(WEALTH) >= 0.0

    def test_shapley_sums_to_total(self) -> None:
        rng = np.random.default_rng(SEED)
        components = {
            "financial": rng.lognormal(11, 1, 200),
            "real_estate": rng.lognormal(12, 1.5, 200),
        }
        total_gini = gini(sum(components.values()))
        sv = shapley_decomposition(components)
        assert sum(sv.values()) == pytest.approx(total_gini, rel=0.05)
