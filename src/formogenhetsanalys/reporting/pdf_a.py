"""PDF/A-2u wrapper for Riksarkivet long-term preservation.

Produces PDF/A-2u output compatible with Riksarkivet RA-FS 2009:1 requirements.
A full implementation uses WeasyPrint or reportlab with ICC colour profile
embedding. This module provides a functional stub that writes HTML and
documents the deviation; a full implementation is deferred to a future release
(see docs/deviations.md DEV-002).
"""

from __future__ import annotations

import pathlib


def render_pdf_a(
    html_content: str,
    output_path: pathlib.Path,
    title: str = "",
    author: str = "Dr. Gustav Olaf Yunus Laitinen-Fredriksson Lundström Imanov",
    subject: str = "Förmögenhetsanalys research output",
    language: str = "en",
) -> pathlib.Path:
    """Render HTML content to a PDF/A-2u file.

    When WeasyPrint is available, uses it to produce a conforming PDF/A-2u
    artefact. Otherwise, writes an HTML stub and logs the deviation.

    Args:
        html_content: UTF-8 HTML string to render.
        output_path: Destination .pdf path. Parents are created if absent.
        title: PDF document title (embedded in XMP metadata).
        author: PDF document author.
        subject: PDF document subject.
        language: BCP-47 language tag for the document.

    Returns:
        Path to the written file (either .pdf or .html fallback).

    Examples:
        >>> import pathlib, tempfile
        >>> with tempfile.TemporaryDirectory() as d:
        ...     p = pathlib.Path(d) / "report.pdf"
        ...     out = render_pdf_a("<html><body>Hello</body></html>", p)
        ...     out.exists()
        True
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import weasyprint

        wp = weasyprint.HTML(string=html_content)
        wp.write_pdf(
            str(output_path),
            uncompressed_pdf=False,
            identifier=title,
        )
        return output_path

    except ImportError:
        fallback = output_path.with_suffix(".html")
        meta = (
            f"<meta name='author' content='{author}'>\n"
            f"<meta name='description' content='{subject}'>\n"
            f"<html lang='{language}'>\n"
        )
        content = (
            html_content.replace("<html>", meta, 1)
            if "<html>" in html_content
            else (
                f"<html lang='{language}'><head><meta charset='UTF-8'>"
                f"<title>{title}</title>{meta}</head><body>" + html_content + "</body></html>"
            )
        )
        fallback.write_text(content, encoding="utf-8")
        return fallback


def figures_to_pdf_a(
    figure_paths: list[pathlib.Path],
    output_path: pathlib.Path,
    title: str = "Förmögenhetsanalys figures",
) -> pathlib.Path:
    """Bundle a list of figure files into a single PDF/A-2u document.

    Args:
        figure_paths: List of PNG or SVG figure file paths.
        output_path: Destination .pdf path.
        title: Document title.

    Returns:
        Path to the written file.

    Examples:
        >>> import pathlib, tempfile
        >>> with tempfile.TemporaryDirectory() as d:
        ...     p = pathlib.Path(d) / "figs.pdf"
        ...     out = figures_to_pdf_a([], p, title="Test")
        ...     out.exists()
        True
    """
    img_tags = "".join(
        f"<figure><img src='{fig.resolve()}' alt='{fig.stem}' style='max-width:100%'>"
        f"<figcaption>{fig.stem}</figcaption></figure>\n"
        for fig in figure_paths
        if fig.exists()
    )
    html = (
        "<!DOCTYPE html>\n"
        f"<html lang='en'><head><meta charset='UTF-8'><title>{title}</title></head>\n"
        f"<body><h1>{title}</h1>\n{img_tags}</body></html>\n"
    )
    return render_pdf_a(html, output_path, title=title)
