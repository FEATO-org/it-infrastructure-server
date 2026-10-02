import argparse
import json
import sys
from pathlib import Path

from common import CATEGORIES, check_version, load_changes


def units(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def render(version: str, changes: list) -> list[dict]:
    title = f"Minecraft Server Patch {version}"
    payloads: list[dict] = []
    fields: list[dict] = []
    size = units(title)

    def flush() -> None:
        nonlocal fields, size
        if fields:
            payloads.append({"embeds": [{"title": title, "fields": fields}], "allowed_mentions": {"parse": []}})
            fields = []
            size = units(title)

    for category, label in CATEGORIES:
        entries = [item for item in changes if item.category == category]
        if not entries:
            continue
        chunks: list[str] = []
        for item in entries:
            entry = f"・{item.change}"
            if item.reason:
                entry += f"\n  └ {item.reason}"
            if units(entry) > 1024:
                raise ValueError(f"{item.filename}: change/reason: exceeds Discord field limit (1024 characters)")
            if chunks and units(chunks[-1]) + 1 + units(entry) > 1024:
                chunks.append(entry)
            elif chunks:
                chunks[-1] += "\n" + entry
            else:
                chunks.append(entry)
        for chunk in chunks:
            if len(fields) == 25 or size + units(label) + units(chunk) > 6000:
                flush()
            fields.append({"name": label, "value": chunk, "inline": False})
            size += units(label) + units(chunk)
    flush()
    return payloads


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payloads = render(check_version(args.version), load_changes(args.input_dir, require_nonempty=True))
        args.output.write_text(json.dumps(payloads, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
