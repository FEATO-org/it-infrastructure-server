import argparse
import sys
from pathlib import Path

from common import load_changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("changes/pending"))
    parser.add_argument("--require-nonempty", action="store_true")
    args = parser.parse_args()
    try:
        changes = load_changes(args.input_dir, require_nonempty=args.require_nonempty)
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Validated {len(changes)} change file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
