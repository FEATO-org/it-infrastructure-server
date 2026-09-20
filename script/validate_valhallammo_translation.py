#!/usr/bin/env python3
"""ValhallaMMO JAR内の英語原本と追跡中の日本語訳の互換性を検査する。"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

TOKEN_RE = re.compile(r"%[A-Za-z0-9_]+%|\{[A-Za-z0-9_]+\}|</?[A-Za-z][^>]*>")

def load_json_bytes(data: bytes, label: str):
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{label}: duplicate key: {key}")
            result[key] = value
        return result
    return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicates)

def compare(source, translated, path, errors):
    if isinstance(source, dict):
        if not isinstance(translated, dict):
            errors.append(f"{path}: expected object")
            return
        missing = sorted(set(source) - set(translated))
        extra = sorted(set(translated) - set(source))
        if missing:
            errors.append(f"{path}: missing keys: {missing}")
        if extra:
            errors.append(f"{path}: extra keys: {extra}")
        for key in source.keys() & translated.keys():
            compare(source[key], translated[key], f"{path}.{key}", errors)
    elif isinstance(source, list):
        if not isinstance(translated, list):
            errors.append(f"{path}: expected list")
            return
        if len(source) != len(translated):
            errors.append(f"{path}: list length {len(translated)} != {len(source)}")
            return
        for index, (left, right) in enumerate(zip(source, translated)):
            compare(left, right, f"{path}[{index}]", errors)
    elif isinstance(source, str):
        if not isinstance(translated, str):
            errors.append(f"{path}: expected string")
            return
        left = sorted(TOKEN_RE.findall(source))
        right = sorted(TOKEN_RE.findall(translated))
        if left != right:
            errors.append(f"{path}: placeholders {right} != {left}")
    elif type(source) is not type(translated):
        errors.append(f"{path}: type {type(translated).__name__} != {type(source).__name__}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("jar", type=Path)
    parser.add_argument("main_translation", type=Path)
    parser.add_argument("materials_translation", type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(args.jar) as archive:
        english_main = load_json_bytes(archive.read("languages/en-us.json"), "languages/en-us.json")
        english_materials = load_json_bytes(
            archive.read("languages/materials/en-us.json"), "languages/materials/en-us.json"
        )
    japanese_main = load_json_bytes(args.main_translation.read_bytes(), str(args.main_translation))
    japanese_materials = load_json_bytes(
        args.materials_translation.read_bytes(), str(args.materials_translation)
    )
    errors = []
    compare(english_main, japanese_main, "main", errors)
    compare(english_materials, japanese_materials, "materials", errors)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"FAILED: {len(errors)} incompatibilities", file=sys.stderr)
        return 1
    print(
        "PASS: ValhallaMMO translation schema and placeholders match "
        f"(main={len(english_main)}, materials={len(english_materials)})"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
