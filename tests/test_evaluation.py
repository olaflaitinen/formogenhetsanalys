"""Tests for evaluation metrics, bootstrap, and posterior diagnostics."""

from __future__ import annotations

import numpy as np
import pytest

from formogenhetsanalys.estimation.top_shares import top_share
from formogenhetsanalys.evaluation.bootstrap import block_bootstrap, jackknife
from formogenhetsanalys.evaluation.metrics import (
    coverage,
    interval_width,
    reconstruction_mae,
)
from formogenhetsanalys.evaluation.posterior import (
    compute_coverage_and_width,
    pit_histogram,
    posterior_predictive_intervals,
)

SEED = 19960307
RNG = np.random.default_rng(SEED)
WEALTH = RNG.lognormal(13.0, 2.0, 300)


class TestMetrics:
    def test_mae_zero_for_perfect(self) -> None:
        v = np.array([1.0, 2.0, 3.0])
        assert reconstruction_mae(v, v) == pytest.approx(0.0)

    def test_mae_positive(self) -> None:
        true = np.array([1.0, 2.0, 3.0])
        pred = np.array([1.5, 2.0, 2.5])
        mae = reconstruction_mae(true, pred)
        assert mae == pytest.approx(1.0 / 3.0, rel=1e-6)

    def test_coverage_full(self) -> None:
        true = np.array([1.0, 2.0, 3.0])
        lo = np.array([0.5, 1.5, 2.0])
        hi = np.array([1.5, 2.5, 4.0])
        assert coverage(true, lo, hi) == pytest.approx(1.0)

    def test_coverage_none(self) -> None:
        true = np.array([5.0, 6.0])
        lo = np.array([0.0, 0.0])
        hi = np.array([1.0, 1.0])
        assert coverage(true, lo, hi) == pytest.approx(0.0)

    def test_interval_width(self) -> None:
        lo = np.array([0.0, 1.0])
        hi = np.array([1.0, 3.0])
        assert interval_width(lo, hi) == pytest.approx(1.5)


class TestBootstrap:
    def test_block_bootstrap_keys(self) -> None:
        result = block_bootstrap(WEALTH, lambda x: top_share(x, 0.99), n_boot=20, seed=7)
        assert "point" in result
        assert "ci_lo" in result
        assert "ci_hi" in result
        assert "se" in result

    def test_block_bootstrap_ci_ordering(self) -> None:
        result = block_bootstrap(WEALTH, lambda x: top_share(x, 0.99), n_boot=50, seed=7)
        assert result["ci_lo"] <= result["point"] <= result["ci_hi"]

    def test_block_bootstrap_se_positive(self) -> None:
        result = block_bootstrap(WEALTH, lambda x: top_share(x, 0.99), n_boot=30, seed=7)
        assert result["se"] >= 0.0

    def test_jackknife_keys(self) -> None:
        w = np.arange(1.0, 21.0)
        result = jackknife(w, lambda x: top_share(x, 0.9))
        assert "point" in result
        assert "bias" in result
        assert "se" in result

    def test_jackknife_se_non_negative(self) -> None:
        w = np.arange(1.0, 21.0)
        result = jackknife(w, lambda x: top_share(x, 0.9))
        assert result["se"] >= 0.0


class TestPosterior:
    def test_predictive_intervals_shape(self) -> None:
        samples = np.random.default_rng(42).normal(0, 1, (200, 10))
        lo, hi = posterior_predictive_intervals(samples, alpha=0.05)
        assert lo.shape == (10,)
        assert hi.shape == (10,)

    def test_predictive_intervals_ordering(self) -> None:
        samples = np.random.default_rng(42).normal(0, 1, (200, 10))
        lo, hi = posterior_predictive_intervals(samples, alpha=0.05)
        assert (lo <= hi).all()

    def test_pit_histogram_shape(self) -> None:
        rng = np.random.default_rng(42)
        true_vals = rng.uniform(0, 1, 50)
        samples = rng.uniform(0, 1, (500, 50))
        hist = pit_histogram(true_vals, samples, n_bins=10)
        assert "pit_values" in hist
        assert "counts" in hist
        assert len(hist["counts"]) == 10

    def test_pit_values_in_unit_interval(self) -> None:
        rng = np.random.default_rng(42)
        true_vals = rng.uniform(0, 1, 20)
        samples = rng.uniform(0, 1, (100, 20))
        hist = pit_histogram(true_vals, samples)
        assert (hist["pit_values"] >= 0.0).all()
        assert (hist["pit_values"] <= 1.0).all()

    def test_coverage_and_width_keys(self) -> None:
        rng = np.random.default_rng(42)
        true_vals = rng.normal(0, 1, 20)
        samples = rng.normal(0, 1, (500, 20))
        result = compute_coverage_and_width(true_vals, samples)
        assert "coverage" in result
        assert "mean_width" in result

    def test_coverage_in_range(self) -> None:
        rng = np.random.default_rng(42)
        true_vals = rng.normal(0, 1, 20)
        samples = rng.normal(0, 1, (1000, 20))
        result = compute_coverage_and_width(true_vals, samples)
        assert 0.0 <= result["coverage"] <= 1.0
