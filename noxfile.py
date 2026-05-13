"""Nox automation sessions for Förmögenhetsanalys."""

import nox

nox.options.sessions = ["lint", "typecheck", "test"]
nox.options.reuse_existing_virtualenvs = True

PYTHON_VERSIONS = ["3.11", "3.12"]
SRC = "src"


@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    """Run ruff linter and formatter check."""
    session.install("ruff>=0.5")
    session.run("ruff", "check", SRC, "tests", "scripts", "benchmarks")
    session.run("ruff", "format", "--check", SRC, "tests", "scripts", "benchmarks")


@nox.session(python="3.12")
def typecheck(session: nox.Session) -> None:
    """Run mypy strict type checking."""
    session.install(".[dev]")
    session.run("mypy", "--strict", SRC)


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run the test suite."""
    session.install(".[dev]")
    session.run(
        "pytest",
        "-x",
        "-q",
        "--tb=short",
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
    """Generate CycloneDX SBOM via uvx (isolated to avoid jsonschema conflict)."""
    session.install(".")
    session.run("uvx", "cyclonedx-bom", "environment", "-o", "sbom.cdx.json", external=True)


@nox.session(python="3.12")
def release(session: nox.Session) -> None:
    """Prepare release: build + verify CITATION.cff."""
    session.install("hatchling>=1.21", "build>=1.2")
    session.run("python", "-m", "build")
    session.run("uvx", "cffconvert", "--validate", "CITATION.cff", external=True)
