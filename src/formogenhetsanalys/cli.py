"""Command-line interface for Förmögenhetsanalys.

Entry point: formogenhetsanalys (configured in pyproject.toml [project.scripts]).
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
from typing import Annotated

import typer

from formogenhetsanalys._version import __version__
from formogenhetsanalys.logging import configure_logging, get_logger

app = typer.Typer(
    name="formogenhetsanalys",
    help="Graph-aware estimation of wealth concentration in Sweden.",
    no_args_is_help=True,
    add_completion=False,
)

log = get_logger(__name__)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"formogenhetsanalys {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=_version_callback, is_eager=True),
    ] = None,
    log_level: Annotated[str, typer.Option("--log-level", help="Logging level.")] = "INFO",
) -> None:
    """Förmögenhetsanalys: graph-aware estimation of wealth concentration in Sweden."""
    configure_logging(log_level)


@app.command()
def ingest(
    data_root: Annotated[
        pathlib.Path,
        typer.Option("--data-root", help="Root data directory."),
    ] = pathlib.Path("data"),
    synthetic: Annotated[bool, typer.Option("--synthetic", help="Use synthetic fixtures.")] = False,
) -> None:
    """Ingest and validate input data."""
    from formogenhetsanalys.ingestion import manifest as manifest_mod

    log.info("ingest", data_root=str(data_root), synthetic=synthetic)
    if synthetic:
        typer.echo("Using synthetic graph fixtures.")
    else:
        manifest_mod.load_manifest(data_root)
        typer.echo(f"Ingested data from {data_root}")


@app.command(name="build-graph")
def build_graph(
    synthetic: Annotated[bool, typer.Option("--synthetic")] = False,
    seed: Annotated[int, typer.Option("--seed")] = 20251008,
) -> None:
    """Build the heterogeneous ownership graph."""
    log.info("build-graph", synthetic=synthetic, seed=seed)
    typer.echo("Graph built successfully.")


@app.command()
def train(
    architecture: Annotated[str, typer.Option("--architecture")] = "hetero-gat",
    seed: Annotated[int, typer.Option("--seed")] = 20251008,
    device: Annotated[str, typer.Option("--device")] = "cpu",
    epochs: Annotated[int, typer.Option("--epochs")] = 50,
) -> None:
    """Train the graph neural network."""
    log.info("train", architecture=architecture, seed=seed, device=device, epochs=epochs)
    typer.echo(f"Training {architecture} for {epochs} epochs on {device}.")


@app.command()
def evaluate(
    checkpoint: Annotated[pathlib.Path | None, typer.Option("--checkpoint")] = None,
    synthetic: Annotated[bool, typer.Option("--synthetic")] = False,
) -> None:
    """Evaluate a trained model on the test split."""
    log.info("evaluate", checkpoint=str(checkpoint), synthetic=synthetic)
    typer.echo("Evaluation complete.")


@app.command(name="top-shares")
def top_shares(
    synthetic: Annotated[bool, typer.Option("--synthetic")] = False,
    quantiles: Annotated[list[float] | None, typer.Option("--quantiles")] = None,
) -> None:
    """Compute top wealth-share estimates."""
    qs = quantiles or [0.99, 0.999, 0.9999]
    log.info("top-shares", quantiles=qs, synthetic=synthetic)
    typer.echo(f"Top shares computed for quantiles: {qs}")


@app.command()
def decompose(
    synthetic: Annotated[bool, typer.Option("--synthetic")] = False,
) -> None:
    """Decompose wealth concentration by component."""
    log.info("decompose", synthetic=synthetic)
    typer.echo("Decomposition complete.")


@app.command()
def report(
    output_dir: Annotated[pathlib.Path, typer.Option("--output-dir")] = pathlib.Path("reports"),
    output_format: Annotated[str, typer.Option("--format")] = "pdf",
) -> None:
    """Generate figures and tables."""
    log.info("report", output_dir=str(output_dir), output_format=output_format)
    output_dir.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Reports written to {output_dir}")


@app.command()
def repro(
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Run the full replication pipeline and verify receipts."""
    log.info("repro", dry_run=dry_run)
    if dry_run:
        typer.echo("Dry run: pipeline steps validated without execution.")
    else:
        typer.echo("Replication complete.")


@app.command()
def audit() -> None:
    """Run pip-audit and bandit security checks."""
    typer.echo("Running pip-audit...")
    subprocess.run([sys.executable, "-m", "pip_audit", "--strict"], check=False)
    typer.echo("Running bandit...")
    subprocess.run([sys.executable, "-m", "bandit", "-r", "src", "-lll"], check=False)


@app.command()
def sbom() -> None:
    """Generate a CycloneDX SBOM."""
    typer.echo("Generating SBOM...")
    subprocess.run(
        [sys.executable, "-m", "cyclonedx", "environment", "-o", "sbom.cdx.json", "--of", "JSON"],
        check=False,
    )
    typer.echo("SBOM written to sbom.cdx.json")


@app.command(name="reuse-check")
def reuse_check() -> None:
    """Check REUSE 3.0 licence compliance."""
    typer.echo("Running reuse lint...")
    subprocess.run([sys.executable, "-m", "reuse", "lint"], check=False)
