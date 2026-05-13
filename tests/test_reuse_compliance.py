"""Tests for REUSE 3.0 compliance."""

from __future__ import annotations

import subprocess


class TestReuseCompliance:
    def test_reuse_lint(self) -> None:
        """Verify that reuse lint passes."""
        result = subprocess.run(["reuse", "lint"], capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"reuse lint failed: {result.stdout}\n{result.stderr}"
