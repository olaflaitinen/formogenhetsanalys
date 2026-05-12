"""Data manifest model and validation utilities."""

from __future__ import annotations

import pathlib

from pydantic import BaseModel, Field


class Manifest(BaseModel):
    """Schema-validated manifest for an input data collection.

    Attributes:
        version: Manifest schema version string.
        data_root: Root directory for this dataset collection.
        households_path: Relative path to households Parquet file.
        firms_path: Relative path to firms Parquet file.
        assets_path: Relative path to assets Parquet file.
        edges_ownership_path: Relative path to ownership edges Parquet file.
        edges_kinship_path: Relative path to kinship edges Parquet file.
        graph_path: Relative path to GraphML file.
        description: Human-readable description of the dataset.

    Examples:
        >>> m = Manifest(version="1.0", data_root=pathlib.Path("data/synthetic"))
        >>> m.version
        '1.0'
    """

    version: str = Field(default="1.0", description="Manifest schema version.")
    data_root: pathlib.Path = Field(description="Root directory for this dataset.")
    households_path: pathlib.Path | None = Field(
        default=None,
        description="Path to households Parquet.",
    )
    firms_path: pathlib.Path | None = Field(
        default=None,
        description="Path to firms Parquet.",
    )
    assets_path: pathlib.Path | None = Field(
        default=None,
        description="Path to assets Parquet.",
    )
    edges_ownership_path: pathlib.Path | None = Field(
        default=None,
        description="Path to ownership-edge Parquet.",
    )
    edges_kinship_path: pathlib.Path | None = Field(
        default=None,
        description="Path to kinship-edge Parquet.",
    )
    graph_path: pathlib.Path | None = Field(
        default=None,
        description="Path to GraphML file.",
    )
    description: str = Field(default="", description="Human-readable description.")

    model_config = {"frozen": True}


def load_manifest(data_root: pathlib.Path) -> Manifest:
    """Load and validate a manifest from a data root directory.

    Looks for a manifest.json file; if absent, constructs a default manifest
    from standard file names found in data_root.

    Args:
        data_root: Directory to inspect.

    Returns:
        A validated Manifest instance.

    Raises:
        FileNotFoundError: If data_root does not exist.

    Examples:
        >>> import pathlib
        >>> m = load_manifest(pathlib.Path("data/synthetic"))
    """
    if not data_root.exists():
        raise FileNotFoundError(f"Data root not found: {data_root}")

    def _maybe(name: str) -> pathlib.Path | None:
        p = data_root / name
        return p if p.exists() else None

    return Manifest(
        data_root=data_root,
        households_path=_maybe("households.parquet"),
        firms_path=_maybe("firms.parquet"),
        assets_path=_maybe("assets.parquet"),
        edges_ownership_path=_maybe("edges_ownership.parquet"),
        edges_kinship_path=_maybe("edges_kinship.parquet"),
        graph_path=_maybe("graph.graphml"),
    )


def validate_against_schema(manifest: Manifest) -> list[str]:
    """Validate that all paths declared in a manifest actually exist.

    Args:
        manifest: A Manifest instance to validate.

    Returns:
        A list of validation error messages; empty if the manifest is valid.

    Examples:
        >>> import pathlib
        >>> m = Manifest(version="1.0", data_root=pathlib.Path("data/synthetic"))
        >>> validate_against_schema(m)
        []
    """
    errors: list[str] = []
    for field_name in (
        "households_path",
        "firms_path",
        "assets_path",
        "edges_ownership_path",
        "edges_kinship_path",
        "graph_path",
    ):
        val = getattr(manifest, field_name)
        if val is not None and not val.exists():
            errors.append(f"{field_name} declared but not found: {val}")
    return errors
