"""Strict, deliberately small parser for single-line change front matter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

CATEGORIES = (
    ("feature", "✨ 新機能"),
    ("content", "📦 コンテンツ追加"),
    ("balance", "⚖️ バランス調整"),
    ("improvement", "🔧 改善"),
    ("fix", "🐛 不具合修正"),
    ("system", "⚙️ システム変更"),
    ("breaking", "⚠️ 重要な変更"),
)
LABELS = dict(CATEGORIES)
VERSION = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\.[1-9][0-9]*\Z")
SAFE_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\.md\Z")
FIELDS = {"category", "scope", "change", "reason"}


@dataclass(frozen=True)
class Change:
    filename: str
    category: str
    scope: str
    change: str
    reason: str | None


def read_change(path: Path) -> Change:
    if not SAFE_NAME.fullmatch(path.name):
        raise ValueError(f"{path}: filename: use safe kebab-case ending in .md")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeError as exc:
        raise ValueError(f"{path}: encoding: use UTF-8") from exc
    if not lines or lines[0] != "---":
        raise ValueError(f"{path}: front matter: add opening ---")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: front matter: add closing ---") from exc
    if any(line.strip() for line in lines[end + 1 :]):
        raise ValueError(f"{path}: body: remove Markdown outside front matter")
    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.fullmatch(r"([a-z]+):[ \t]*(.*)", line)
        if not match:
            raise ValueError(f"{path}: front matter: use one-line key: value fields")
        key, value = match.groups()
        if key not in FIELDS:
            raise ValueError(f"{path}: {key}: remove unsupported field")
        if key in values:
            raise ValueError(f"{path}: {key}: remove duplicate field")
        value = value.strip()
        if not value or value in {"|", ">", "|-", ">-"}:
            raise ValueError(f"{path}: {key}: provide a nonempty one-line value")
        values[key] = value
    for key in ("category", "scope", "change"):
        if key not in values:
            raise ValueError(f"{path}: {key}: add required field")
    if values["category"] not in LABELS:
        raise ValueError(f"{path}: category: use one of {', '.join(LABELS)}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", values["scope"]):
        raise ValueError(f"{path}: scope: use nonempty kebab-case")
    return Change(path.name, values["category"], values["scope"], values["change"], values.get("reason"))


def load_changes(directory: Path, *, require_nonempty: bool = False) -> list[Change]:
    if not directory.is_dir():
        raise ValueError(f"{directory}: input-dir: directory does not exist")
    paths = sorted(directory.iterdir(), key=lambda path: path.name)
    changes = []
    for path in paths:
        if path.name == ".gitkeep":
            continue
        if not path.is_file():
            raise ValueError(f"{path}: filename: expected a regular .md file")
        changes.append(read_change(path))
    if require_nonempty and not changes:
        raise ValueError(f"{directory}: pending: no change files; refusing empty release")
    return changes


def check_version(version: str) -> str:
    if not VERSION.fullmatch(version):
        raise ValueError(f"version: expected YYYY-MM-DD.N, got {version!r}")
    return version
