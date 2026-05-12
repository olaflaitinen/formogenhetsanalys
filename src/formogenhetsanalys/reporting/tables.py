"""Table output utilities: CSV with UTF-8 BOM, Parquet, and LaTeX."""

from __future__ import annotations

import pathlib

import polars as pl


def to_csv_with_bom(df: pl.DataFrame, path: pathlib.Path) -> None:
    """Write a Polars DataFrame to CSV with UTF-8 BOM for Excel compatibility.

    The UTF-8 BOM (U+FEFF) is prepended so that Microsoft Excel opens the
    file with correct encoding without manual intervention.

    Args:
        df: Polars DataFrame to write.
        path: Destination file path. Parent directories are created if absent.

    Examples:
        >>> import polars as pl, pathlib, tempfile
        >>> with tempfile.TemporaryDirectory() as d:
        ...     p = pathlib.Path(d) / "test.csv"
        ...     to_csv_with_bom(pl.DataFrame({"a": [1, 2]}), p)
        ...     content = p.read_bytes()
        ...     content[:3] == b'\\xef\\xbb\\xbf'
        True
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    csv_bytes = df.write_csv().encode("utf-8")
    bom = b"\xef\xbb\xbf"
    path.write_bytes(bom + csv_bytes)


def to_parquet(df: pl.DataFrame, path: pathlib.Path) -> None:
    """Write a Polars DataFrame to Parquet (Snappy compression).

    Args:
        df: Polars DataFrame to write.
        path: Destination file path.

    Examples:
        >>> import polars as pl, pathlib, tempfile
        >>> with tempfile.TemporaryDirectory() as d:
        ...     p = pathlib.Path(d) / "test.parquet"
        ...     to_parquet(pl.DataFrame({"a": [1, 2]}), p)
        ...     p.exists()
        True
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path, compression="snappy")


def to_latex_table(
    df: pl.DataFrame,
    path: pathlib.Path,
    caption: str = "",
    label: str = "",
) -> None:
    """Write a Polars DataFrame to a LaTeX tabular environment.

    Args:
        df: Polars DataFrame to format.
        path: Destination .tex file path.
        caption: LaTeX table caption string.
        label: LaTeX label for cross-referencing.

    Examples:
        >>> import polars as pl, pathlib, tempfile
        >>> with tempfile.TemporaryDirectory() as d:
        ...     p = pathlib.Path(d) / "table.tex"
        ...     to_latex_table(pl.DataFrame({"A": [1], "B": [2]}), p,
        ...                    caption="Test", label="tab:test")
        ...     p.exists()
        True
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = df.columns
    n_cols = len(cols)
    col_spec = "l" + "r" * (n_cols - 1)

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        f"\\begin{{tabular}}{{{col_spec}}}",
        r"\toprule",
        " & ".join(f"\\textbf{{{c}}}" for c in cols) + r" \\",
        r"\midrule",
    ]

    for row in df.iter_rows():
        lines.append(" & ".join(str(v) for v in row) + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def to_pdf_a_table(df: pl.DataFrame, path: pathlib.Path, title: str = "") -> None:
    """Write a DataFrame as a minimal PDF/A-compatible HTML table.

    A full PDF/A-2u implementation requires WeasyPrint or reportlab with
    ICC colour profiles. This stub writes an accessible HTML representation
    that can be converted by an external tool.

    Args:
        df: Polars DataFrame.
        path: Destination file path (suffix .html).
        title: Page title for accessibility.

    Examples:
        >>> import polars as pl, pathlib, tempfile
        >>> with tempfile.TemporaryDirectory() as d:
        ...     p = pathlib.Path(d) / "table.html"
        ...     to_pdf_a_table(pl.DataFrame({"A": [1]}), p, title="Test")
        ...     p.exists()
        True
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    html_path = path.with_suffix(".html")
    cols = df.columns

    header = "".join(f"<th scope='col'>{c}</th>" for c in cols)
    rows = "".join(
        "<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>" for row in df.iter_rows()
    )

    html = (
        "<!DOCTYPE html>\n"
        "<html lang='en'>\n"
        "<head>\n"
        "<meta charset='UTF-8'>\n"
        f"<title>{title}</title>\n"
        "</head>\n"
        "<body>\n"
        f"<table>\n<thead><tr>{header}</tr></thead>\n"
        f"<tbody>{rows}</tbody>\n</table>\n"
        "</body>\n</html>\n"
    )
    html_path.write_text(html, encoding="utf-8")
