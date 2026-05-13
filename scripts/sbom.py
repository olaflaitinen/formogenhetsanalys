"""Generate Software Bill of Materials (SBOM) using CycloneDX."""

from __future__ import annotations

import subprocess
import sys


def main() -> None:
    """Generate SBOM using cyclonedx-py."""
    result = subprocess.run(  # noqa: S603 S607
        ["cyclonedx-py", "environment", "-o", "sbom.cdx.json", "--of", "JSON"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"Error generating SBOM: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print("SBOM generated: sbom.cdx.json")


if __name__ == "__main__":
    main()
