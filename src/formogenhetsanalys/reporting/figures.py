"""Figure generation using matplotlib (Agg backend for reproducibility)."""

from __future__ import annotations

import pathlib
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


class FigureBuilder:
    """Builder for publication-quality figures.

    Uses the matplotlib Agg backend for deterministic rendering.
    All figures are saved as PNG, SVG, and optionally PDF/A-2u.

    Args:
        output_dir: Directory where figures are written.
        dpi: Resolution for raster output.

    Examples:
        >>> import pathlib
        >>> fb = FigureBuilder(pathlib.Path("reports"))
        >>> fb is not None
        True
    """

    def __init__(self, output_dir: pathlib.Path, dpi: int = 150) -> None:
        self.output_dir = output_dir
        self.dpi = dpi
        output_dir.mkdir(parents=True, exist_ok=True)

    def _save(self, fig: Any, stem: str) -> list[pathlib.Path]:
        paths = []
        for fmt in ("png", "svg"):
            p = self.output_dir / f"{stem}.{fmt}"
            fig.savefig(p, dpi=self.dpi if fmt == "png" else None, bbox_inches="tight")
            paths.append(p)
        plt.close(fig)
        return paths

    def top_share_trajectory(
        self,
        years: list[int],
        shares: list[float],
        ci_lo: list[float] | None = None,
        ci_hi: list[float] | None = None,
        quantile_label: str = "Top 1%",
    ) -> list[pathlib.Path]:
        """Plot a top-share time series with optional confidence band.

        Args:
            years: List of year integers.
            shares: List of top-share point estimates.
            ci_lo: Optional list of lower confidence bounds.
            ci_hi: Optional list of upper confidence bounds.
            quantile_label: Label for the series.

        Returns:
            List of written file paths.

        Examples:
            >>> import pathlib
            >>> import tempfile
            >>> with tempfile.TemporaryDirectory() as d:
            ...     fb = FigureBuilder(pathlib.Path(d))
            ...     paths = fb.top_share_trajectory([2015, 2016], [0.25, 0.26])
            ...     len(paths) == 2
            True
        """
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(years, shares, marker="o", label=quantile_label, color="#1f77b4")
        if ci_lo is not None and ci_hi is not None:
            ax.fill_between(years, ci_lo, ci_hi, alpha=0.25, color="#1f77b4")
        ax.set_xlabel("Year")
        ax.set_ylabel("Top-share")
        ax.set_title(f"Wealth concentration: {quantile_label} share")
        ax.legend()
        fig.tight_layout()
        return self._save(fig, "top_share_trajectory")

    def lorenz_curve(
        self,
        wealth: np.ndarray[Any, np.dtype[np.float64]],
    ) -> list[pathlib.Path]:
        """Plot the Lorenz curve for a wealth distribution.

        Args:
            wealth: 1-D array of wealth values.

        Returns:
            List of written file paths.

        Examples:
            >>> import pathlib, tempfile, numpy as np
            >>> with tempfile.TemporaryDirectory() as d:
            ...     fb = FigureBuilder(pathlib.Path(d))
            ...     paths = fb.lorenz_curve(np.array([1.0, 2.0, 3.0, 10.0]))
            ...     len(paths) == 2
            True
        """
        w = np.sort(np.asarray(wealth, dtype=np.float64))
        n = len(w)
        lorenz_x = np.concatenate([[0.0], np.arange(1, n + 1) / n])
        lorenz_y = np.concatenate([[0.0], np.cumsum(w) / np.sum(w)])

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.plot(lorenz_x, lorenz_y, label="Lorenz curve", color="#1f77b4")
        ax.plot([0, 1], [0, 1], linestyle="--", color="grey", label="Perfect equality")
        ax.set_xlabel("Cumulative population share")
        ax.set_ylabel("Cumulative wealth share")
        ax.set_title("Lorenz curve")
        ax.legend()
        fig.tight_layout()
        return self._save(fig, "lorenz_curve")

    def decomposition_bar(
        self,
        components: dict[str, float],
    ) -> list[pathlib.Path]:
        """Plot a bar chart of Shapley-value decomposition.

        Args:
            components: Dict mapping component name to Shapley value.

        Returns:
            List of written file paths.

        Examples:
            >>> import pathlib, tempfile
            >>> with tempfile.TemporaryDirectory() as d:
            ...     fb = FigureBuilder(pathlib.Path(d))
            ...     paths = fb.decomposition_bar({"financial": 0.15, "real_estate": 0.10})
            ...     len(paths) == 2
            True
        """
        names = list(components)
        vals = [components[n] for n in names]

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(names, vals, color="#1f77b4")
        ax.set_xlabel("Shapley attribution")
        ax.set_title("Wealth-concentration decomposition")
        fig.tight_layout()
        return self._save(fig, "decomposition_bar")
