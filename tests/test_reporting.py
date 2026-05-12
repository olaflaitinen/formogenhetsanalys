"""Tests for reporting: figures, tables, and PDF/A."""

from __future__ import annotations

import pathlib

import numpy as np
import polars as pl

from formogenhetsanalys.reporting.figures import FigureBuilder
from formogenhetsanalys.reporting.pdf_a import figures_to_pdf_a, render_pdf_a
from formogenhetsanalys.reporting.tables import to_csv_with_bom, to_latex_table, to_parquet


class TestFigures:
    def test_top_share_trajectory(self, tmp_path: pathlib.Path) -> None:
        fb = FigureBuilder(tmp_path)
        paths = fb.top_share_trajectory([2015, 2016, 2017], [0.25, 0.26, 0.24])
        assert len(paths) == 2
        for p in paths:
            assert p.exists()

    def test_top_share_trajectory_with_ci(self, tmp_path: pathlib.Path) -> None:
        fb = FigureBuilder(tmp_path / "with_ci")
        paths = fb.top_share_trajectory(
            [2015, 2016],
            [0.25, 0.26],
            ci_lo=[0.22, 0.23],
            ci_hi=[0.28, 0.29],
        )
        assert all(p.exists() for p in paths)

    def test_lorenz_curve(self, tmp_path: pathlib.Path) -> None:
        fb = FigureBuilder(tmp_path / "lorenz")
        w = np.array([1.0, 2.0, 5.0, 10.0, 100.0])
        paths = fb.lorenz_curve(w)
        assert all(p.exists() for p in paths)

    def test_decomposition_bar(self, tmp_path: pathlib.Path) -> None:
        fb = FigureBuilder(tmp_path / "decomp")
        paths = fb.decomposition_bar({"financial": 0.15, "real_estate": 0.10})
        assert all(p.exists() for p in paths)


class TestTables:
    def test_csv_bom_prefix(self, tmp_path: pathlib.Path) -> None:
        df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
        p = tmp_path / "test.csv"
        to_csv_with_bom(df, p)
        assert p.exists()
        content = p.read_bytes()
        assert content[:3] == b"\xef\xbb\xbf"

    def test_csv_readable_polars(self, tmp_path: pathlib.Path) -> None:
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        p = tmp_path / "test.csv"
        to_csv_with_bom(df, p)
        loaded = pl.read_csv(p, encoding="utf8-lossy")
        assert "x" in loaded.columns
        assert len(loaded) == 2

    def test_parquet_roundtrip(self, tmp_path: pathlib.Path) -> None:
        df = pl.DataFrame({"a": [1, 2, 3], "b": [4.0, 5.0, 6.0]})
        p = tmp_path / "test.parquet"
        to_parquet(df, p)
        assert p.exists()
        loaded = pl.read_parquet(p)
        assert df.equals(loaded)

    def test_latex_table_contains_toprule(self, tmp_path: pathlib.Path) -> None:
        df = pl.DataFrame({"A": [1], "B": [2]})
        p = tmp_path / "table.tex"
        to_latex_table(df, p, caption="Test", label="tab:test")
        content = p.read_text()
        assert r"\toprule" in content
        assert r"\bottomrule" in content

    def test_latex_table_header(self, tmp_path: pathlib.Path) -> None:
        df = pl.DataFrame({"ColA": [1], "ColB": [2]})
        p = tmp_path / "table.tex"
        to_latex_table(df, p)
        content = p.read_text()
        assert "ColA" in content
        assert "ColB" in content


class TestPDFA:
    def test_render_pdf_a_creates_file(self, tmp_path: pathlib.Path) -> None:
        html = "<html><body>Hello</body></html>"
        out = render_pdf_a(html, tmp_path / "report.pdf", title="Test")
        assert out.exists()

    def test_figures_to_pdf_a_empty_list(self, tmp_path: pathlib.Path) -> None:
        out = figures_to_pdf_a([], tmp_path / "figs.pdf", title="Empty")
        assert out.exists()

    def test_figures_to_pdf_a_with_existing_figure(
        self, tmp_path: pathlib.Path,
    ) -> None:
        fb = FigureBuilder(tmp_path / "figs")
        fig_paths = fb.lorenz_curve(np.array([1.0, 2.0, 5.0, 10.0, 20.0]))
        png_paths = [p for p in fig_paths if p.suffix == ".png"]
        out = figures_to_pdf_a(png_paths, tmp_path / "bundle.pdf", title="Bundle")
        assert out.exists()
