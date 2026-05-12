"""Nox automation sessions for Förmögenhetsanalys."""

import nox

nox.options.sessions = ["lint", "type", "test"]
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = False

PYTHON_VERSIONS = ["3.11", "3.12"]
SRC = "src"


@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    """Run ruff linter and formatter check."""
    session.install("ruff>=0.5")
    session.run("ruff", "check", SRC, "tests", "scripts", "benchmarks")
    session.run("ruff", "format", "--check", SRC, "tests", "scripts", "benchmarks")


@nox.session(python=PYTHON_VERSIONS)
def type(session: nox.Session) -> None:
    """Run mypy strict type checking."""
    session.install(
        "mypy>=1.10",
        "pydantic>=2.6",
        "typer>=0.12",
        "structlog>=24.1",
        "numpy>=1.26",
        "pandas-stubs>=2.2",
        "types-networkx>=3.3",
    )
    session.install("-e", ".")
    session.run("mypy", "--strict", SRC)


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run the test suite."""
    session.install(
        "pytest>=8",
        "pytest-cov>=5",
        "pytest-xdist>=3.5",
        "pytest-randomly>=3.15",
        "hypothesis>=6.100",
    )
    session.install("-e", ".")
    session.run(
        "pytest",
        "-x",
        "-q",
        "--cov=formogenhetsanalys",
        "--cov-report=term-missing",
        "--cov-branch",
        *session.posargs,
    )


@nox.session(python="3.12")
def cov(session: nox.Session) -> None:
    """Run coverage with fail-under gate."""
    session.install(
        "pytest>=8",
        "pytest-cov>=5",
        "hypothesis>=6.100",
    )
    session.install("-e", ".")
    session.run(
        "pytest",
        "--cov=formogenhetsanalys",
        "--cov-report=term-missing",
        "--cov-branch",
        "--cov-fail-under=90",
    )


@nox.session(python="3.12")
def docs(session: nox.Session) -> None:
    """Build documentation with MkDocs."""
    session.install(
        "mkdocs>=1.6",
        "mkdocs-material>=9.5",
        "mkdocstrings[python]>=0.25",
        "mike>=2",
    )
    session.install("-e", ".")
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12")
def build(session: nox.Session) -> None:
    """Build sdist and wheel."""
    session.install("hatchling>=1.21", "build>=1.0")
    session.run("python", "-m", "build")


@nox.session(python="3.12")
def audit(session: nox.Session) -> None:
    """Run pip-audit and bandit security checks."""
    session.install("pip-audit>=2.7", "bandit>=1.7")
    session.install("-e", ".")
    session.run("pip-audit", "--strict")
    session.run("bandit", "-r", SRC, "-lll")


@nox.session(python="3.12")
def reuse(session: nox.Session) -> None:
    """Check REUSE 3.0 compliance."""
    session.install("reuse>=4")
    session.run("reuse", "lint")


@nox.session(python="3.12")
def sbom(session: nox.Session) -> None:
    """Generate CycloneDX SBOM."""
    session.install("cyclonedx-bom>=4")
    session.install("-e", ".")
    session.run("cyclonedx-py", "environment", "-o", "sbom.cdx.json", "--of", "JSON")


@nox.session(python="3.12")
def release(session: nox.Session) -> None:
    """Build and sign release artefacts (requires sigstore)."""
    session.install("hatchling>=1.21", "build>=1.0", "sigstore>=2.0")
    session.run("python", "-m", "build")
    session.run(
        "sigstore",
        "sign",
        "dist/formogenhetsanalys-0.1.0.tar.gz",
        "dist/formogenhetsanalys-0.1.0-py3-none-any.whl",
    )
