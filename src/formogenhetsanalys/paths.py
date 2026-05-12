"""Canonical path constants for Förmögenhetsanalys.

All path references in the package should import from this module rather than
constructing paths ad-hoc, so that layout changes need only be made here.
"""

from __future__ import annotations

import pathlib

_PACKAGE_ROOT = pathlib.Path(__file__).parent
_REPO_ROOT = _PACKAGE_ROOT.parent.parent

DATA_ROOT: pathlib.Path = _REPO_ROOT / "data"
SYNTHETIC_ROOT: pathlib.Path = DATA_ROOT / "synthetic"
REPORTS_ROOT: pathlib.Path = _REPO_ROOT / "reports"
CHECKPOINT_ROOT: pathlib.Path = _REPO_ROOT / "checkpoints"

__all__ = [
    "DATA_ROOT",
    "SYNTHETIC_ROOT",
    "REPORTS_ROOT",
    "CHECKPOINT_ROOT",
]
