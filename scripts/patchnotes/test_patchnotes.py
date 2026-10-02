import json
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from common import load_changes
from generate_discord_payload import render as render_discord, units
from generate_patchnote import render as render_markdown
from release_control import next_version


class PatchnoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def add(self, name, category, change, reason=None):
        value = f"---\ncategory: {category}\nscope: test\nchange: {change}\n"
        if reason is not None:
            value += f"reason: {reason}\n"
        (self.directory / f"{name}.md").write_text(value + "---\n", encoding="utf-8")

    def test_order_and_optional_reason(self):
        self.add("z-fix", "fix", "直しました。")
        self.add("b-feature", "feature", "Bを追加しました。", "必要だったためです。")
        self.add("a-feature", "feature", "Aを追加しました。")
        changes = load_changes(self.directory, require_nonempty=True)
        note = render_markdown("2026-09-29.1", changes)
        self.assertEqual(note, render_markdown("2026-09-29.1", load_changes(self.directory)))
        self.assertLess(note.index("Aを追加"), note.index("Bを追加"))
        self.assertLess(note.index("## ✨"), note.index("## 🐛"))
        self.assertNotIn("## ⚖️", note)
        self.assertIn("  - 必要だったためです。", note)
        payload = render_discord("2026-09-29.1", changes)
        self.assertIn("  └ 必要だったためです。", json.dumps(payload, ensure_ascii=False))
        self.assertNotIn("└", json.dumps(render_discord("2026-09-29.1", [changes[0]]), ensure_ascii=False))

    def test_invalid_and_empty(self):
        with self.assertRaisesRegex(ValueError, "no change files"):
            load_changes(self.directory, require_nonempty=True)
        self.add("invalid", "unknown", "変更しました。")
        with self.assertRaisesRegex(ValueError, "category"):
            load_changes(self.directory)
        (self.directory / "invalid.md").write_text("---\ncategory: feature\nscope: test\n---\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "change"):
            load_changes(self.directory)

    def test_discord_splitting(self):
        for number in range(15):
            self.add(f"long-{number:02}", "content", f"{number}番目" + "あ" * 600)
        changes = load_changes(self.directory)
        payloads = render_discord("2026-09-29.1", changes)
        self.assertGreater(len(payloads), 1)
        for payload in payloads:
            embed = payload["embeds"][0]
            self.assertLessEqual(len(embed["fields"]), 25)
            self.assertLessEqual(units(embed["title"]) + sum(units(field["name"]) + units(field["value"]) for field in embed["fields"]), 6000)
            self.assertTrue(all(units(field["value"]) <= 1024 for field in embed["fields"]))

    def test_version_counts_tags_and_deploy_branches(self):
        today = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")
        refs = f"abc\trefs/tags/server-{today}.1\nabc\trefs/heads/deploy/{today}.2\nabc\trefs/tags/server-{today}.2^{{}}"
        with patch("release_control.command", return_value=refs):
            self.assertEqual(next_version(), f"{today}.3")


if __name__ == "__main__":
    unittest.main()
