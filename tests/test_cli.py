"""Tests for CLI commands."""

from __future__ import annotations

import pathlib
import tempfile

import polars as pl
import pytest
from typer.testing import CliRunner

from formogenhetsanalys.cli import app

runner = CliRunner()


class TestCLI:
    def test_version(self) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout

    def test_ingest_synthetic(self, tmp_path: pathlib.Path) -> None:
        result = runner.invoke(app, ["ingest", "--synthetic", "--data-root", str(tmp_path)])
        assert result.exit_code == 0

    def test_report(self, tmp_path: pathlib.Path) -> None:
        result = runner.invoke(app, ["report", "--output-dir", str(tmp_path)])
        assert result.exit_code == 0
