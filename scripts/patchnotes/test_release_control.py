import json
import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from release_control import detect, main, resume


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


class ReleaseRecoveryTests(unittest.TestCase):
    def test_recovery_uses_existing_tag_and_requires_main_ancestry(self):
        commit = "a" * 40
        with patch("release_control.command", side_effect=[commit, ""]) as command, patch("release_control.detect", return_value="2026-10-03.2") as detect_mock:
            self.assertEqual(resume("2026-10-03.2"), commit)
            self.assertEqual(command.call_args_list[0].args, ("git", "rev-parse", "--verify", "refs/tags/server-2026-10-03.2^{commit}"))
            self.assertEqual(command.call_args_list[1].args, ("git", "merge-base", "--is-ancestor", commit, "HEAD"))
            detect_mock.assert_called_once_with(f"{commit}^", commit)

    def test_recovery_rejects_missing_tag_non_main_commit_or_wrong_release(self):
        commit = "a" * 40
        for responses in ([subprocess.CalledProcessError(1, "git")], [commit, subprocess.CalledProcessError(1, "git")]):
            with self.subTest(responses=responses), patch("release_control.command", side_effect=responses), patch("release_control.detect") as detect_mock:
                with self.assertRaises(subprocess.CalledProcessError):
                    resume("2026-10-03.2")
                detect_mock.assert_not_called()
        with patch("release_control.command", side_effect=[commit, ""]), patch("release_control.detect", return_value="2026-10-03.1"):
            with self.assertRaisesRegex(ValueError, "does not match"):
                resume("2026-10-03.2")

    def test_recovery_runs_only_on_main_and_outputs_original_release_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            args = ["control", "resume", "--version", "2026-10-03.2"]
            with patch.object(sys, "argv", args), patch("release_control.resume", return_value="a" * 40) as recover, patch.dict(os.environ, {"GITHUB_REF": "refs/heads/develop", "GITHUB_OUTPUT": str(output)}), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(), 1)
                recover.assert_not_called()
            self.assertFalse(output.exists())
            with patch.object(sys, "argv", args), patch("release_control.resume", return_value="a" * 40), patch.dict(os.environ, {"GITHUB_REF": "refs/heads/main", "GITHUB_OUTPUT": str(output)}):
                self.assertEqual(main(), 0)
            self.assertEqual(output.read_text(), f"publish=true\nversion=2026-10-03.2\ncommit={'a' * 40}\n")


if __name__ == "__main__":
    unittest.main()
