"""Generate CHANGELOG.md from git commit history."""

from __future__ import annotations

import subprocess
import re


def get_commits_since_tag(tag: str = "v0.1.0") -> list[dict[str, str]]:
    """Get commits since the given tag."""
    result = subprocess.run(
        ["git", "log", f"{tag}..HEAD", "--pretty=format:%h %s"],
        capture_output=True,
        text=True,
    )
    commits = []
    for line in result.stdout.strip().split("\n"):
        if line:
            hash, message = line.split(" ", 1)
            commits.append({"hash": hash, "message": message})
    return commits


def categorize_commit(message: str) -> str:
    """Categorize commit message using conventional commits."""
    match = re.match(r"(\w+)(\(.+\))?:\s*(.+)", message)
    if match:
        type_ = match.group(1)
        if type_ in ("feat", "fix"):
            return type_
        elif type_ in ("docs", "chore", "refactor"):
            return "other"
    return "other"


def generate_changelog() -> str:
    """Generate changelog markdown."""
    commits = get_commits_since_tag()
    features = [c for c in commits if categorize_commit(c["message"]) == "feat"]
    fixes = [c for c in commits if categorize_commit(c["message"]) == "fix"]
    others = [c for c in commits if categorize_commit(c["message"]) == "other"]

    changelog = "# Changelog\n\n"
    changelog += "## Unreleased\n\n"

    if features:
        changelog += "### Features\n"
        for c in features:
            changelog += f"- {c['message']} ({c['hash']})\n"
        changelog += "\n"

    if fixes:
        changelog += "### Bug Fixes\n"
        for c in fixes:
            changelog += f"- {c['message']} ({c['hash']})\n"
        changelog += "\n"

    if others:
        changelog += "### Other\n"
        for c in others:
            changelog += f"- {c['message']} ({c['hash']})\n"

    return changelog


if __name__ == "__main__":
    print(generate_changelog())
