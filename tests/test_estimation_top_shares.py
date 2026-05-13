"""Tests for top share estimation."""

from __future__ import annotations

import numpy as np
import pytest

from formogenhetsanalys.estimation.top_shares import top_share, top_shares_bootstrap

SEED = 19960307
RNG = np.random.default_rng(SEED)
WEALTH = RNG.lognormal(13.0, 2.0, 500)


class TestTopShare:
    def test_increasing_values(self) -> None:
        w = np.arange(1.0, 101.0)
        share = top_share(w, 0.99)
        assert share == pytest.approx(0.01, abs=0.01)

    def test_all_concentrated(self) -> None:
        w = np.zeros(100)
        w[0] = 1.0
        share = top_share(w, 0.99)
        assert share == pytest.approx(1.0)

    def test_bootstrap_returns_dict(self) -> None:
        result = top_shares_bootstrap(WEALTH, [0.99], n_boot=20, seed=7)
        assert 0.99 in result
        assert "point" in result[0.99]
        assert "ci_lo" in result[0.99]
        assert "ci_hi" in result[0.99]

    def test_bootstrap_ci_ordering(self) -> None:
        result = top_shares_bootstrap(WEALTH, [0.99], n_boot=50, seed=7)
        assert result[0.99]["ci_lo"] < result[0.99]["point"] < result[0.99]["ci_hi"]
