import argparse
import sys
from pathlib import Path

from common import CATEGORIES, check_version, load_changes


def render(version: str, changes: list) -> str:
    lines = [f"# Minecraft Server Patch {version}"]
    for category, label in CATEGORIES:
        entries = [item for item in changes if item.category == category]
        if not entries:
            continue
        lines.extend(("", f"## {label}", ""))
        for item in entries:
            lines.append(f"- {item.change}")
            if item.reason:
                lines.append(f"  - {item.reason}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        version = check_version(args.version)
        changes = load_changes(args.input_dir, require_nonempty=True)
        if args.output.name != f"{version}.md" or args.output.parent.name != version[:4]:
            raise ValueError("output: expected patchnotes/<year>/<version>.md")
        content = render(version, changes)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
