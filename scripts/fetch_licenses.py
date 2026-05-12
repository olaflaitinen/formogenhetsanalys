"""Fetch canonical licence texts from upstream sources.

Run this script once after a clean clone to refresh LICENSES/CC-BY-4.0.txt
from the Creative Commons canonical source. The EUPL-1.2 and CC0-1.0 texts
are committed verbatim and do not require network access.

Deviation documented in docs/deviations.md: DEV-001.
"""

import hashlib
import pathlib
import sys
import urllib.request

LICENSES_DIR = pathlib.Path(__file__).parent.parent / "LICENSES"

SOURCES: dict[str, str] = {
    "CC-BY-4.0.txt": "https://creativecommons.org/licenses/by/4.0/legalcode.txt",
}


def fetch(filename: str, url: str) -> None:
    target = LICENSES_DIR / filename
    print(f"Fetching {url} -> {target}")
    with urllib.request.urlopen(url) as response:  # noqa: S310
        data = response.read()
    target.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    print(f"  Written {len(data)} bytes  SHA-256: {digest}")


def main() -> None:
    LICENSES_DIR.mkdir(parents=True, exist_ok=True)
    for filename, url in SOURCES.items():
        fetch(filename, url)
    print("Done.")


if __name__ == "__main__":
    sys.exit(main())
