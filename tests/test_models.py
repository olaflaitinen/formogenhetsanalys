"""Tests for GNN models, Bayesian priors, variational posteriors, and baselines."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from formogenhetsanalys.models.baselines import (
    ownership_chain_expansion,
    register_aggregate,
    spectral_clustering,
)
from formogenhetsanalys.models.bayesian_priors import BetaPrior, TruncatedNormalPrior
from formogenhetsanalys.models.hetero_gnn import BaseHeteroGNN, get_model
from formogenhetsanalys.models.variational import (
    LowRankPosterior,
    MeanFieldPosterior,
    elbo,
    iwae_bound,
)

SEED = 19960307


class TestBetaPrior:
    def test_init(self) -> None:
        p = BetaPrior(alpha=2.0, beta=5.0)
        assert p.alpha == 2.0
        assert p.beta == 5.0

    def test_invalid_alpha_raises(self) -> None:
        with pytest.raises(ValueError):
            BetaPrior(alpha=-1.0, beta=1.0)

    def test_invalid_beta_raises(self) -> None:
        with pytest.raises(ValueError):
            BetaPrior(alpha=1.0, beta=0.0)

    def test_log_prob_uniform(self) -> None:
        p = BetaPrior(1.0, 1.0)
        lp = float(np.asarray(p.log_prob(0.5)))
        assert lp == pytest.approx(0.0, abs=1e-9)

    def test_sample_count(self) -> None:
        p = BetaPrior(2.0, 5.0)
        s = p.sample(10, seed=42)
        assert len(s) == 10

    def test_sample_range(self) -> None:
        p = BetaPrior(2.0, 5.0)
        s = np.asarray(p.sample(100, seed=42))
        assert (s > 0.0).all() and (s < 1.0).all()

    def test_sample_reproducible(self) -> None:
        p = BetaPrior(2.0, 5.0)
        s1 = np.asarray(p.sample(20, seed=42))
        s2 = np.asarray(p.sample(20, seed=42))
        np.testing.assert_array_almost_equal(s1, s2)


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


class TestMeanFieldPosterior:
    def test_init(self) -> None:
        q = MeanFieldPosterior(n_latent=10, seed=SEED)
        assert q.n_latent == 10

    def test_alpha_positive(self) -> None:
        q = MeanFieldPosterior(n_latent=5, seed=SEED)
        assert (q.alpha > 0).all()

    def test_sample_shape(self) -> None:
        q = MeanFieldPosterior(n_latent=8, seed=SEED)
        s = q.sample(seed=0)
        assert s.shape == (8,)

    def test_sample_in_unit_interval(self) -> None:
        q = MeanFieldPosterior(n_latent=50, seed=SEED)
        s = q.sample(seed=0)
        assert (s > 0).all() and (s < 1).all()

    def test_entropy_scalar(self) -> None:
        q = MeanFieldPosterior(n_latent=5, seed=SEED)
        e = q.entropy()
        assert isinstance(e, float)


class TestLowRankPosterior:
    def test_init(self) -> None:
        q = LowRankPosterior(n_latent=10, rank=2, seed=SEED)
        assert q.mu.shape == (10,)

    def test_covariance_shape(self) -> None:
        q = LowRankPosterior(n_latent=5, rank=2, seed=SEED)
        cov = q.covariance()
        assert cov.shape == (5, 5)

    def test_covariance_symmetric(self) -> None:
        q = LowRankPosterior(n_latent=5, rank=2, seed=SEED)
        cov = q.covariance()
        np.testing.assert_array_almost_equal(cov, cov.T)

    def test_sample_shape(self) -> None:
        q = LowRankPosterior(n_latent=5, rank=2, seed=SEED)
        s = q.sample(seed=0)
        assert s.shape == (5,)

    def test_sample_range(self) -> None:
        q = LowRankPosterior(n_latent=5, rank=2, seed=SEED)
        s = q.sample(seed=0)
        assert (s > 0).all() and (s < 1).all()


class TestELBO:
    def test_elbo_formula(self) -> None:
        assert elbo(-1.0, -0.5, -0.3) == pytest.approx(-1.2)

    def test_iwae_higher_with_lower_log_weight(self) -> None:
        lw = np.array([-1.0, -1.5, -0.8])
        bound = iwae_bound(lw)
        assert bound <= max(lw)


class TestBaselines:
    def test_register_aggregate_passthrough(self, households_df: pl.DataFrame) -> None:
        result = register_aggregate(households_df)
        assert "wealth_estimate" in result.columns
        np.testing.assert_array_almost_equal(
            result["wealth_estimate"].to_numpy(),
            households_df["total_wealth"].to_numpy(),
        )

    def test_ownership_chain_expansion_column(
        self,
        households_df: pl.DataFrame,
        ownership_df: pl.DataFrame,
    ) -> None:
        result = ownership_chain_expansion(households_df, ownership_df)
        assert "wealth_estimate" in result.columns
        assert len(result) == len(households_df)

    def test_spectral_clustering_column(self, households_df: pl.DataFrame) -> None:
        own = pl.DataFrame(
            {"source_id": [], "target_id": [], "ownership_share": []},
        )
        result = spectral_clustering(households_df, own, n_clusters=3, seed=42)
        assert "wealth_estimate" in result.columns
        assert len(result) == len(households_df)


class TestHeteroGNN:
    def test_get_model_rgcn(self) -> None:
        model = get_model(
            "r-gcn",
            ["household", "firm"],
            [("household", "ownership", "firm")],
            hidden_dim=16,
            seed=42,
        )
        assert isinstance(model, BaseHeteroGNN)

    def test_get_model_hetero_gat(self) -> None:
        model = get_model(
            "hetero-gat",
            ["household", "firm"],
            [("household", "ownership", "firm")],
            hidden_dim=16,
            seed=42,
        )
        assert isinstance(model, BaseHeteroGNN)

    def test_get_model_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown architecture"):
            get_model("unknown", ["household"], [])

    def test_forward_stub_returns_dict(self) -> None:
        model = get_model("r-gcn", ["household"], [], hidden_dim=8, seed=42)
        x_dict = {"household": np.ones((5, 4), dtype=np.float32)}
        out = model.forward(x_dict, {})
        assert isinstance(out, dict)
        assert "household" in out

    def test_predict_ownership_share_returns_array(self) -> None:
        model = get_model("r-gcn", ["household", "firm"], [], hidden_dim=8, seed=42)
        graph = {
            "node_features": {
                "household": np.ones((5, 4), dtype=np.float32),
                "firm": np.ones((3, 4), dtype=np.float32),
            },
            "edge_index": {},
        }
        result = model.predict_ownership_share(graph)
        assert result is not None
