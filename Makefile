.PHONY: install lint type test cov docs build release sbom reuse clean audit

PYTHON := uv run python
NOX := uv run nox

install:
	uv sync --extra dev --extra docs

lint:
	$(NOX) -s lint

type:
	$(NOX) -s type

test:
	$(NOX) -s test

cov:
	$(NOX) -s cov

docs:
	$(NOX) -s docs

build:
	$(NOX) -s build

release:
	$(NOX) -s release

sbom:
	$(NOX) -s sbom

reuse:
	$(NOX) -s reuse

audit:
	$(NOX) -s audit

clean:
	rm -rf dist/ build/ site/ .nox/ .coverage htmlcov/ sbom.cdx.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
