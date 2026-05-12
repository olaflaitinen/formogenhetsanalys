#!/bin/bash
# Replication script for Förmögenhetsanalys
# Author: Förmögenhetsanalys
# Date: 2025-10-08

set -e

echo "Starting replication..."

# Run Python pipeline
uv run python -m formogenhetsanalys.cli run --synthetic

# Run Stata analysis
cd stata
stata-mp -b do replication.do
cd ..

# Run R analysis
cd R
Rscript diagnostics.R
Rscript decomposition_plots.R
cd ..

# Generate receipts
uv run python scripts/make_synthetic_graph.py

echo "Replication complete."
