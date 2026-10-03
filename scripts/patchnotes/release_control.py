"""Small Git/GitHub checks used by release workflows."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

from common import check_version


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def next_version() -> str:
    date = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")
    refs = command("git", "ls-remote", "--heads", "--tags", "origin")
    numbers = []
    for line in refs.splitlines():
        ref = line.split("\t")[-1]
        match = re.fullmatch(rf"refs/(?:heads/deploy/{date}|tags/server-{date})\.([1-9][0-9]*)", ref)
        if match:
            numbers.append(int(match.group(1)))
    return f"{date}.{max(numbers, default=0) + 1}"


def detect(before: str, after: str) -> str | None:
    added = command("git", "diff", "--diff-filter=A", "--name-only", before, after).splitlines()
    notes = [path for path in added if path.startswith("patchnotes/") and path.endswith(".md")]
    if not notes:
        return None
    if len(notes) != 1:
        raise ValueError(f"push added {len(notes)} patchnotes; expected exactly one")
    match = re.fullmatch(r"patchnotes/([0-9]{4})/([0-9]{4}-[0-9]{2}-[0-9]{2}\.[1-9][0-9]*)\.md", notes[0])
    if not match or match.group(1) != match.group(2)[:4]:
        raise ValueError(f"invalid added patchnote path: {notes[0]}")
    version = match.group(2)
    check_version(version)
    repository = os.environ["GITHUB_REPOSITORY"]
    pulls = json.loads(command("gh", "api", f"repos/{repository}/commits/{after}/pulls"))
    matching = [pr for pr in pulls if pr.get("merged_at") and pr.get("merge_commit_sha") == after and pr["base"]["ref"] == "main" and pr["head"]["ref"] == f"deploy/{version}"]
    if len(matching) != 1:
        raise ValueError(f"{version}: expected one merged deploy/{version} → main PR associated with commit")
    if not Path(f"changes/released/{version}").is_dir():
        raise ValueError(f"{version}: released changes directory is missing")
    return version


def resume(version: str) -> str:
    check_version(version)
    commit = command("git", "rev-parse", "--verify", f"refs/tags/server-{version}^{{commit}}")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("release tag did not resolve to a commit")
    command("git", "merge-base", "--is-ancestor", commit, "HEAD")
    if detect(f"{commit}^", commit) != version:
        raise ValueError(f"{version}: release tag does not match the merged release PR")
    return commit


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("next-version")
    select = sub.add_parser("detect")
    select.add_argument("--before", required=True)
    select.add_argument("--after", required=True)
    recovery = sub.add_parser("resume")
    recovery.add_argument("--version", required=True)
    args = parser.parse_args()
    try:
        if args.action == "next-version":
            print(next_version())
        else:
            if args.action == "resume":
                if os.environ.get("GITHUB_REF") != "refs/heads/main":
                    raise ValueError("recovery must run on main")
                commit = resume(args.version)
                version = args.version
            else:
                commit = args.after
                version = detect(args.before, args.after)
            output = os.environ["GITHUB_OUTPUT"]
            with open(output, "a", encoding="utf-8") as handle:
                handle.write(f"publish={'true' if version else 'false'}\n")
                if version:
                    handle.write(f"version={version}\n")
                    handle.write(f"commit={commit}\n")
    except (KeyError, OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"release control: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
