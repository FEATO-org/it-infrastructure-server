import json
import os
import unittest
from unittest.mock import patch

from release_control import detect


class ReleaseDetectionTests(unittest.TestCase):
    def test_ordinary_push_does_not_publish(self):
        with patch("release_control.command", return_value="docs/example.md") as command:
            self.assertIsNone(detect("before", "after"))
            command.assert_called_once()

    def test_ambiguous_patchnotes_are_rejected(self):
        paths = "patchnotes/2026/2026-09-29.1.md\npatchnotes/2026/2026-09-29.2.md"
        with patch("release_control.command", return_value=paths) as command:
            with self.assertRaisesRegex(ValueError, "expected exactly one"):
                detect("before", "after")
            command.assert_called_once()

    def test_only_the_release_pr_merge_commit_is_published(self):
        pr = {"merged_at": "date", "merge_commit_sha": "after", "base": {"ref": "main"}, "head": {"ref": "deploy/2026-09-29.1"}}
        for merge_sha, expected in (("after", True), ("older", False)):
            with self.subTest(merge_sha=merge_sha), patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/repo"}), patch("release_control.Path.is_dir", return_value=True), patch("release_control.command", side_effect=["patchnotes/2026/2026-09-29.1.md", json.dumps([{**pr, "merge_commit_sha": merge_sha}])]):
                if expected:
                    self.assertEqual(detect("before", "after"), "2026-09-29.1")
                else:
                    with self.assertRaisesRegex(ValueError, "expected one merged"):
                        detect("before", "after")


if __name__ == "__main__":
    unittest.main()
