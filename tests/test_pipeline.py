"""Integration tests for the pipeline runner and DAG."""

from __future__ import annotations

import pathlib

import pytest

from formogenhetsanalys.config import Config
from formogenhetsanalys.pipelines.dag import DAG, Task
from formogenhetsanalys.pipelines.runner import Pipeline

SEED = 19960307


class TestConfig:
    def test_default_seeds(self, tmp_path: pathlib.Path) -> None:
        cfg = Config(data_root=tmp_path)
        assert cfg.seed == 20251008

    def test_custom_seed(self, tmp_path: pathlib.Path) -> None:
        cfg = Config(data_root=tmp_path, seed=99)
        assert cfg.seed == 99

    def test_architecture_default(self, tmp_path: pathlib.Path) -> None:
        cfg = Config(data_root=tmp_path)
        assert cfg.gnn_architecture in ("r-gcn", "hetero-gat", "hetero-transformer", "graphsage")

    def test_valuation_default(self, tmp_path: pathlib.Path) -> None:
        cfg = Config(data_root=tmp_path)
        assert cfg.valuation in ("market", "book", "capitalised", "hedonic")


class TestDAG:
    def test_task_creation(self) -> None:
        t = Task(name="t1", fn=lambda: 42, inputs=[])
        assert t.name == "t1"

    def test_task_cache_key_deterministic(self) -> None:
        t = Task(name="t1", fn=lambda: 42, inputs=[])
        k1 = t.cache_key({})
        k2 = t.cache_key({})
        assert k1 == k2

    def test_task_cache_key_differs_with_input(self) -> None:
        t = Task(name="t1", fn=lambda: 42, inputs=["dep"])
        k1 = t.cache_key({"dep": "abc"})
        k2 = t.cache_key({"dep": "xyz"})
        assert k1 != k2

    def test_dag_run_single_task(self) -> None:
        dag = DAG()
        dag.add_task(Task(name="root", fn=lambda **_: 42, inputs=[]))
        results = dag.run()
        assert results["root"] == 42

    def test_dag_run_chained_tasks(self) -> None:
        dag = DAG()
        dag.add_task(Task(name="a", fn=lambda **_: 10, inputs=[]))
        dag.add_task(Task(name="b", fn=lambda a, **_: a + 5, inputs=["a"]))
        results = dag.run()
        assert results["b"] == 15

    def test_dag_topological_order(self) -> None:
        order = []
        dag = DAG()
        dag.add_task(Task(name="a", fn=lambda **_: order.append("a") or 1, inputs=[]))
        dag.add_task(Task(name="b", fn=lambda a, **_: order.append("b") or 2, inputs=["a"]))
        dag.add_task(Task(name="c", fn=lambda b, **_: order.append("c") or 3, inputs=["b"]))
        dag.run()
        assert order == ["a", "b", "c"]

    def test_dag_duplicate_task_raises(self) -> None:
        dag = DAG()
        dag.add_task(Task(name="dup", fn=lambda **_: 1, inputs=[]))
        with pytest.raises(ValueError, match="Duplicate"):
            dag.add_task(Task(name="dup", fn=lambda **_: 2, inputs=[]))

    def test_dag_cycle_raises(self) -> None:
        dag = DAG()
        dag.add_task(Task(name="a", fn=lambda b, **_: b, inputs=["b"]))
        dag.add_task(Task(name="b", fn=lambda a, **_: a, inputs=["a"]))
        with pytest.raises(ValueError, match="Cycle"):
            dag.run()


class TestPipeline:
    def test_pipeline_creation(self, default_config: Config) -> None:
        p = Pipeline(default_config)
        assert p is not None

    def test_run_synthetic_keys(self, default_config: Config) -> None:
        p = Pipeline(default_config)
        result = p.run_synthetic()
        assert "top_shares" in result
        assert "gini" in result
        assert "decomposition" in result
        assert "receipt_sha256" in result

    def test_run_synthetic_gini_range(self, default_config: Config) -> None:
        p = Pipeline(default_config)
        result = p.run_synthetic()
        assert 0.0 < result["gini"] < 1.0

    def test_run_synthetic_receipt_is_hex(self, default_config: Config) -> None:
        p = Pipeline(default_config)
        result = p.run_synthetic()
        receipt = result["receipt_sha256"]
        assert len(receipt) == 64
        int(receipt, 16)

    def test_run_synthetic_reproducible(self, default_config: Config) -> None:
        p1 = Pipeline(default_config)
        p2 = Pipeline(default_config)
        r1 = p1.run_synthetic()
        r2 = p2.run_synthetic()
        assert r1["receipt_sha256"] == r2["receipt_sha256"]

    def test_load_synthetic_parquet_missing(
        self, tmp_path: pathlib.Path,
    ) -> None:
        cfg = Config(data_root=tmp_path)
        p = Pipeline(cfg)
        assert p.load_synthetic_parquet() is None
