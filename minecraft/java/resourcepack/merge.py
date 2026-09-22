#!/usr/bin/env python3
"""Merge resource packs without modifying their assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile
import zipfile


PACK_META = json.dumps(
    {
        "pack": {
            "min_format": [88, 0],
            "max_format": 88,
            "description": "FEATO Server Resource Pack",
        }
    },
    ensure_ascii=False,
    separators=(",", ":"),
).encode("utf-8")


def safe_member_path(name: str) -> PurePosixPath:
    if not name or "\\" in name or name.startswith(("/", "\\")):
        raise ValueError(f"unsafe archive path: {name!r}")
    path = PurePosixPath(name)
    if path == PurePosixPath(".") or path.is_absolute() or ".." in path.parts or (path.parts and path.parts[0].endswith(":")):
        raise ValueError(f"unsafe archive path: {name!r}")
    return path


def is_language_file(path: PurePosixPath) -> bool:
    parts = path.parts
    return len(parts) == 4 and parts[0] == "assets" and parts[2] == "lang" and path.suffix == ".json"


def is_sound_registry(path: PurePosixPath) -> bool:
    parts = path.parts
    return len(parts) == 3 and parts[0] == "assets" and path.name == "sounds.json"


def is_mergeable_json(path: PurePosixPath) -> bool:
    return is_language_file(path) or is_sound_registry(path)


def parse_mergeable_json(path: PurePosixPath, data: bytes) -> dict[str, object]:
    def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
        parsed: dict[str, object] = {}
        for key, value in pairs:
            if key in parsed:
                raise ValueError(f"duplicate key in resource-pack language file {path}: {key!r}")
            parsed[key] = value
        return parsed

    try:
        parsed = json.loads(data.decode("utf-8-sig"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid mergeable resource-pack JSON file: {path}") from error
    if not isinstance(parsed, dict):
        raise ValueError(f"mergeable resource-pack JSON file must contain an object: {path}")
    if is_language_file(path) and not all(isinstance(key, str) and isinstance(value, str) for key, value in parsed.items()):
        raise ValueError(f"resource-pack language file must contain a string-to-string object: {path}")
    return parsed


def merge_json_files(path: PurePosixPath, previous: bytes, incoming: bytes) -> bytes:
    merged = parse_mergeable_json(path, previous)
    for key, value in parse_mergeable_json(path, incoming).items():
        if key in merged and merged[key] != value:
            raise ValueError(f"conflicting resource-pack JSON entry: {path} key {key!r}")
        merged[key] = value
    return (json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def add_file(files: dict[PurePosixPath, bytes], path: PurePosixPath, data: bytes) -> None:
    if path in {PurePosixPath("pack.mcmeta"), PurePosixPath("pack.png"), PurePosixPath("version.txt")}:
        return
    previous = files.get(path)
    if previous is not None and previous != data:
        if not is_mergeable_json(path):
            raise ValueError(f"conflicting resource-pack file: {path}")
        data = merge_json_files(path, previous, data)
    files[path] = data


def read_zip(source: Path, files: dict[PurePosixPath, bytes]) -> None:
    with zipfile.ZipFile(source) as archive:
        for info in archive.infolist():
            path = safe_member_path(info.filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"symlink entries are not allowed: {info.filename!r}")
            if info.is_dir():
                continue
            if mode and not stat.S_ISREG(mode):
                raise ValueError(f"non-regular archive entry: {info.filename!r}")
            add_file(files, path, archive.read(info))


def read_directory(source: Path, files: dict[PurePosixPath, bytes]) -> None:
    root = source.resolve()
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        if any((current_path / directory).is_symlink() for directory in directories):
            raise ValueError(f"symlink directory in input: {current_path}")
        for filename in filenames:
            candidate = current_path / filename
            if candidate.is_symlink() or not candidate.is_file():
                raise ValueError(f"non-regular file in input: {candidate}")
            relative = candidate.relative_to(root)
            path = safe_member_path(relative.as_posix())
            add_file(files, path, candidate.read_bytes())


def collect_files(sources: list[Path]) -> dict[PurePosixPath, bytes]:
    files: dict[PurePosixPath, bytes] = {}
    for source in sources:
        if source.is_symlink():
            raise ValueError(f"symlink input is not allowed: {source}")
        if source.is_dir():
            read_directory(source, files)
        elif source.is_file() and zipfile.is_zipfile(source):
            read_zip(source, files)
        else:
            raise ValueError(f"input is not a resource-pack directory or zip: {source}")
    return files


def write_output(output: Path, files: dict[PurePosixPath, bytes], icon: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temporary_path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("pack.mcmeta", PACK_META)
            if icon.is_file():
                if icon.is_symlink():
                    raise ValueError(f"override icon must not be a symlink: {icon}")
                archive.write(icon, "pack.png")
            for path in sorted(files):
                archive.writestr(path.as_posix(), files[path])
        digest = hashlib.sha1(temporary_path.read_bytes()).hexdigest()
        os.replace(temporary_path, output)
        sha1_file = output.with_name(f"{output.name}.sha1")
        if sha1_file.is_symlink():
            raise ValueError(f"SHA-1 output must not be a symlink: {sha1_file}")
        sha1_file.write_text(f"{digest}\n", encoding="ascii")
        return digest
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Safely merge Minecraft resource packs.")
    parser.add_argument("--output", required=True, type=Path, help="Merged resource-pack zip path")
    parser.add_argument("sources", nargs="+", type=Path, help="Input zip files or directories, in merge order")
    arguments = parser.parse_args()

    files = collect_files(arguments.sources)
    icon = Path(__file__).resolve().parent / "overrides" / "pack.png"
    digest = write_output(arguments.output, files, icon)
    print(f"Wrote {arguments.output} ({digest})")


if __name__ == "__main__":
    main()
