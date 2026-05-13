"""Compare actual receipts with expected receipts for reproducibility verification."""

from __future__ import annotations

import hashlib
import json
import pathlib


def compute_file_hash(filepath: pathlib.Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


def load_receipts(receipts_path: pathlib.Path) -> dict[str, str]:
    """Load receipts JSON file."""
    with open(receipts_path) as f:
        return json.load(f)


def compare_receipts(expected_path: pathlib.Path, actual_path: pathlib.Path) -> None:
    """Compare expected and actual receipts."""
    expected = load_receipts(expected_path)
    actual = load_receipts(actual_path)

    print("Comparing receipts...")
    print(f"Expected: {expected_path}")
    print(f"Actual: {actual_path}")
    print()

    mismatches = []
    for key in expected:
        if key not in actual:
            mismatches.append(f"Missing key: {key}")
        elif actual[key] != expected[key]:
            mismatches.append(f"Mismatch for {key}: expected {expected[key]}, got {actual[key]}")

    if mismatches:
        print("Receipts DO NOT match:")
        for m in mismatches:
            print(f"  - {m}")
        raise SystemExit(1)
    print("All receipts match successfully!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare receipts for reproducibility")
    parser.add_argument("expected", type=pathlib.Path, help="Expected receipts JSON")
    parser.add_argument("actual", type=pathlib.Path, help="Actual receipts JSON")
    args = parser.parse_args()

    compare_receipts(args.expected, args.actual)
