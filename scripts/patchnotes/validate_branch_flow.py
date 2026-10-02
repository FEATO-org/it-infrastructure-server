"""Keep ordinary changes on develop and permit a narrowly scoped bootstrap."""

import argparse
import subprocess
import sys

from common import VERSION

BOOTSTRAP_BRANCH = "codex/bootstrap-minecraft-release"
BOOTSTRAP_FILES = {
    ".github/workflows/prepare-release.yml",
    ".github/workflows/publish-release.yml",
    ".github/workflows/validate-changes.yml",
    "AGENTS.md",
    "changes/README.md",
    "changes/released/.gitkeep",
    "docs/patch-notes.md",
    "patchnotes/.gitkeep",
}


def validate(base: str, head: str, changed_paths: list[str]) -> None:
    if base == "develop":
        return
    if base != "main":
        raise ValueError(f"unsupported PR base: {base}")
    if head.startswith("deploy/") and VERSION.fullmatch(head.removeprefix("deploy/")):
        return
    if head == BOOTSTRAP_BRANCH:
        unexpected = [
            path for path in changed_paths
            if path not in BOOTSTRAP_FILES
            and not path.startswith("scripts/patchnotes/")
        ]
        if not unexpected:
            return
        raise ValueError("bootstrap must only change release tooling: " + ", ".join(unexpected))
    raise ValueError("ordinary PRs must target develop; main accepts deploy/YYYY-MM-DD.N release PRs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base-sha", required=True)
    args = parser.parse_args()
    try:
        # Include both sides of renames so an allowed file cannot be renamed
        # into a gameplay/configuration path by the bootstrap exception.
        paths = subprocess.check_output(
            ["git", "diff", "--no-renames", "--name-only", "-z", f"{args.base_sha}...HEAD"],
        ).decode().rstrip("\0").split("\0")
        validate(args.base, args.head, [path for path in paths if path])
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"branch flow: {exc}", file=sys.stderr)
        return 1
    print(f"branch flow: {args.head} → {args.base} is allowed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
