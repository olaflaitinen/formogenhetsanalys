"""Tests for Bayesian priors."""

from __future__ import annotations

import numpy as np
import pytest

from formogenhetsanalys.models.bayesian_priors import BetaPrior, TruncatedNormalPrior


class TestBetaPrior:
    def test_init(self) -> None:
        p = BetaPrior(alpha=2.0, beta=5.0)
        assert p.alpha == 2.0
        assert p.beta == 5.0

    def test_invalid_alpha_raises(self) -> None:
        with pytest.raises(ValueError):
            BetaPrior(alpha=-1.0, beta=1.0)

    def test_sample_count(self) -> None:
        p = BetaPrior(2.0, 5.0)
        s = p.sample(10, seed=42)
        assert len(s) == 10

    def test_sample_range(self) -> None:
        p = BetaPrior(2.0, 5.0)
        s = np.asarray(p.sample(100, seed=42))
        assert (s > 0.0).all() and (s < 1.0).all()


class TestTruncatedNormalPrior:
    def test_init(self) -> None:
        p = TruncatedNormalPrior(loc=0.5, scale=0.2)
        assert p.loc == 0.5

    def test_invalid_scale_raises(self) -> None:
        with pytest.raises(ValueError):
            TruncatedNormalPrior(loc=0.5, scale=0.0)

    def test_sample_in_unit_interval(self) -> None:
        p = TruncatedNormalPrior(0.5, 0.2)
        s = np.asarray(p.sample(100, seed=42))
        assert (s >= 0.0).all() and (s <= 1.0).all()
