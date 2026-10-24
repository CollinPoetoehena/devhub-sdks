"""Validate independent stable release tags before publishing artifacts."""

import argparse
import re
import tomllib
from pathlib import Path

VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
MODULE = "github.com/CollinPoetoehena/devhub-sdks/go"


def validate_release(root: Path, tag: str) -> str:
    """Return the ecosystem for a valid stable tag, or raise ValueError."""
    match = re.fullmatch(rf"(python|go)/v({VERSION})", tag)
    if match is None:
        raise ValueError("Expected python/vMAJOR.MINOR.PATCH or go/vMAJOR.MINOR.PATCH")
    ecosystem, version = match.groups()
    if ecosystem == "python":
        project = tomllib.loads((root / "python/pyproject.toml").read_text(encoding="utf-8"))[
            "project"
        ]
        if project["version"] != version:
            raise ValueError(
                f"Tag version {version} differs from Python version {project['version']}"
            )
    else:
        module_file = (root / "go/go.mod").read_text(encoding="utf-8")
        module = re.search(r"^module\s+(\S+)\s*$", module_file, re.MULTILINE)
        if module is None or module[1] != MODULE:
            raise ValueError(f"Expected Go module path {MODULE}")
        if int(version.split(".")[0]) >= 2:
            raise ValueError("Go v2+ needs a deliberate module-path and release-workflow migration")
    return ecosystem


def main() -> None:
    """Report invalid release input as a failed command, without publishing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    args = parser.parse_args()
    try:
        ecosystem = validate_release(Path(__file__).resolve().parents[1], args.tag)
    except ValueError as error:
        parser.error(str(error))
    print(f"Validated {ecosystem} release: {args.tag}")


if __name__ == "__main__":
    main()
