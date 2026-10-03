import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from common import load_changes, read_change
from generate_patchnote import main as generate
from validate_changes import main as validate


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.source = self.directory / "example.md"
        self.valid = "---\ncategory: feature\nscope: server\nchange: 追加しました。\n---\n"

    def test_invalid_change_fields_report_the_file_and_field(self):
        cases = [
            ("missing opening", self.valid.removeprefix("---\n"), "front matter"),
            ("missing closing", self.valid.removesuffix("---\n"), "front matter"),
            ("category", self.valid.replace("category: feature\n", ""), "category"),
            ("scope", self.valid.replace("scope: server\n", ""), "scope"),
            ("change", self.valid.replace("change: 追加しました。\n", ""), "change"),
            ("unknown category", self.valid.replace("category: feature", "category: other"), "category"),
            ("empty scope", self.valid.replace("scope: server", "scope: ''"), "scope"),
            ("empty change", self.valid.replace("追加しました。", '""'), "change"),
            ("empty reason", self.valid.replace("change:", 'reason: " "\nchange:'), "reason"),
            ("null reason", self.valid.replace("change:", "reason: null\nchange:"), "reason"),
            ("multiline", self.valid.replace("追加しました。", '"first\\nsecond"'), "change"),
            ("trailing newline", self.valid.replace("追加しました。", '"first\\n"'), "change"),
            ("block reason", self.valid.replace("change:", "reason: |+\nchange:"), "reason"),
            ("body", self.valid + "# Extra text\n", "body"),
            ("duplicate", self.valid.replace("change:", "scope: server\nchange:"), "scope"),
        ]
        for label, source, field in cases:
            with self.subTest(label=label):
                self.source.write_text(source, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, rf"example.md: {field}"):
                    read_change(self.source)

    def test_quoted_values_are_decoded(self):
        self.source.write_text("---\ncategory: 'feature'\nscope: \"server\"\nchange: 'It''s added.'\nreason: \"A \\\"quoted\\\" reason.\"\n---\n", encoding="utf-8")
        change = read_change(self.source)
        self.assertEqual(change.change, "It's added.")
        self.assertEqual(change.reason, 'A "quoted" reason.')

    def test_invalid_filenames_and_symlinks_are_rejected(self):
        for name in ("Bad-name.md", "unsafe_name.md", "example.txt"):
            with self.subTest(name=name):
                path = self.directory / name
                path.write_text(self.valid, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "filename"):
                    read_change(path)
                path.unlink()
        self.source.symlink_to(self.directory / "outside.md")
        with self.assertRaisesRegex(ValueError, "regular .md"):
            load_changes(self.directory)

    def test_validator_empty_and_error_exit_codes(self):
        with patch.object(sys, "argv", ["validate", "--input-dir", str(self.directory)]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(validate(), 0)
        error = io.StringIO()
        with patch.object(sys, "argv", ["validate", "--input-dir", str(self.directory), "--require-nonempty"]), contextlib.redirect_stderr(error):
            self.assertEqual(validate(), 1)
        self.assertIn("refusing empty release", error.getvalue())
        self.source.write_text(self.valid.replace("category: feature", "category: other"), encoding="utf-8")
        error = io.StringIO()
        with patch.object(sys, "argv", ["validate", "--input-dir", str(self.directory)]), contextlib.redirect_stderr(error):
            self.assertEqual(validate(), 1)
        self.assertIn("example.md: category", error.getvalue())

    def test_generator_refuses_to_overwrite_a_patchnote(self):
        self.source.write_text(self.valid, encoding="utf-8")
        output = self.directory / "2026" / "2026-09-29.1.md"
        args = ["generate", "--version", "2026-09-29.1", "--input-dir", str(self.directory), "--output", str(output)]
        # Keep generated output outside the input directory.
        pending = self.directory / "pending"
        pending.mkdir()
        self.source.rename(pending / self.source.name)
        args[4] = str(pending)
        with patch.object(sys, "argv", args):
            self.assertEqual(generate(), 0)
        content = output.read_text(encoding="utf-8")
        with patch.object(sys, "argv", args), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(generate(), 1)
        self.assertEqual(output.read_text(encoding="utf-8"), content)


if __name__ == "__main__":
    unittest.main()
