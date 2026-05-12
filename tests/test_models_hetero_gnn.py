"""Tests for heterogeneous GNN models."""

from __future__ import annotations

import numpy as np
import pytest

from formogenhetsanalys.models.hetero_gnn import get_model, BaseHeteroGNN


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

    def test_forward_stub(self) -> None:
        model = get_model("r-gcn", ["household"], [], hidden_dim=8, seed=42)
        x_dict = {"household": np.ones((5, 4), dtype=np.float32)}
        out = model.forward(x_dict, {})
        assert isinstance(out, dict)
