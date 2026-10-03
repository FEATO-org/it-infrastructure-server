import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import publish_release


class GitHubApiTests(unittest.TestCase):
    def test_only_http_404_means_not_found(self):
        for status in (404, 401, 403, 500):
            with self.subTest(status=status):
                result = subprocess.CompletedProcess([], 1, f"HTTP/2.0 {status} Error\n\n{{}}", "private error")
                with patch("publish_release.subprocess.run", return_value=result):
                    if status == 404:
                        self.assertIsNone(publish_release.github_api("endpoint", allow_not_found=True))
                    else:
                        with self.assertRaisesRegex(ValueError, "refusing to infer absence"):
                            publish_release.github_api("endpoint", allow_not_found=True)

    def test_network_failure_is_not_absence(self):
        result = subprocess.CompletedProcess([], 1, "", "network failure")
        with patch("publish_release.subprocess.run", return_value=result):
            with self.assertRaisesRegex(ValueError, "HTTP unknown"):
                publish_release.github_api("endpoint", allow_not_found=True)

    def test_successful_api_response(self):
        result = subprocess.CompletedProcess([], 0, 'HTTP/2.0 200 OK\nContent-Type: application/json\n\n{"body":"note"}', "")
        with patch("publish_release.subprocess.run", return_value=result):
            self.assertEqual(publish_release.github_api("endpoint"), {"body": "note"})


class PublishReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        directory = Path(self.temp.name)
        self.note = directory / "note.md"
        self.payload = directory / "payload.json"
        self.note.write_text("# Minecraft Server Patch 2026-09-29.1\n", encoding="utf-8")
        self.payload.write_text(json.dumps([{"embeds": [{"title": "Test"}]}]), encoding="utf-8")
        self.release = {"body": self.note.read_text(), "assets": [], "draft": False, "prerelease": False}
        contexts = contextlib.ExitStack()
        self.addCleanup(contexts.close)
        self.api = contexts.enter_context(patch("publish_release.github_api", return_value=self.release))
        self.gh = contexts.enter_context(patch("publish_release.gh", return_value=""))
        self.open = contexts.enter_context(patch("publish_release.urlopen"))
        response = io.BytesIO(b'{"id":"message-id"}')
        response.status = 200
        self.open.return_value = response
        contexts.enter_context(patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "owner/repo",
            "DISCORD_PATCHNOTE_WEBHOOK_URL": "https://discord.com/api/webhooks/example/private-token",
        }))

    def run_publish(self, *extra_args):
        args = ["publish", "--version", "2026-09-29.1", "--commit", "a" * 40,
                "--patchnote", str(self.note), "--payload", str(self.payload), *extra_args]
        output = io.StringIO()
        with patch.object(sys, "argv", args), contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            return publish_release.main(), output.getvalue()

    def test_existing_sent_marker_skips_all_external_writes(self):
        self.release["assets"] = [{"name": publish_release.SENT}, {"name": publish_release.PENDING}]
        self.assertEqual(self.run_publish()[0], 0)
        self.gh.assert_not_called()
        self.open.assert_not_called()

    def test_pending_marker_blocks_automatic_retry(self):
        self.release["assets"] = [{"name": publish_release.PENDING}]
        code, output = self.run_publish()
        self.assertEqual(code, 1)
        self.assertIn("delivery is uncertain", output)
        self.gh.assert_not_called()
        self.open.assert_not_called()

    def test_missing_release_and_tag_create_one_release_then_send(self):
        self.api.side_effect = [None, None, self.release]
        self.assertEqual(self.run_publish()[0], 0)
        self.assertEqual([call.args[:2] for call in self.gh.call_args_list], [
            ("release", "create"), ("release", "upload"),
            ("release", "upload"), ("release", "delete-asset"),
        ])
        self.open.assert_called_once()

    def test_existing_release_can_finish_discord_delivery(self):
        self.assertEqual(self.run_publish()[0], 0)
        self.assertNotIn(("release", "create"), [call.args[:2] for call in self.gh.call_args_list])
        self.open.assert_called_once()
        request = self.open.call_args.args[0]
        self.assertEqual(request.get_header("User-agent"), publish_release.DISCORD_USER_AGENT)
        self.assertTrue(request.get_header("User-agent").startswith("DiscordBot ("))
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(request.get_method(), "POST")

    def test_orphan_tag_and_api_errors_cannot_create_a_release(self):
        for responses in ([None, {"ref": "tag"}], [ValueError("API unavailable")], [None, ValueError("API unavailable")]):
            with self.subTest(responses=responses):
                self.api.side_effect = responses
                self.assertEqual(self.run_publish()[0], 1)
                self.gh.assert_not_called()
                self.open.assert_not_called()

    def test_mismatched_or_unpublished_release_is_rejected(self):
        for change in ({"body": "wrong"}, {"draft": True}, {"prerelease": True}):
            with self.subTest(change=change):
                self.api.return_value = {**self.release, **change}
                self.assertEqual(self.run_publish()[0], 1)
                self.gh.assert_not_called()
                self.open.assert_not_called()

    def test_discord_failure_keeps_pending_and_does_not_leak_url(self):
        secret_url = os.environ["DISCORD_PATCHNOTE_WEBHOOK_URL"]
        self.open.side_effect = HTTPError(secret_url, 429, "Too many requests", {}, None)
        code, output = self.run_publish()
        self.assertEqual(code, 1)
        self.assertIn("HTTP 429", output)
        self.assertNotIn(secret_url, output)
        self.assertEqual([call.args[:2] for call in self.gh.call_args_list], [("release", "upload")])
        self.assertEqual(Path(self.gh.call_args.args[3]).name, publish_release.PENDING)

    def test_timeout_message_cannot_leak_secret(self):
        self.open.side_effect = TimeoutError(os.environ["DISCORD_PATCHNOTE_WEBHOOK_URL"])
        code, output = self.run_publish()
        self.assertEqual(code, 1)
        self.assertIn("TimeoutError", output)
        self.assertNotIn("private-token", output)

    def test_discord_json_error_logs_only_numeric_code(self):
        secret_url = os.environ["DISCORD_PATCHNOTE_WEBHOOK_URL"]
        body = json.dumps({"code": 40333, "message": secret_url}).encode()
        self.open.side_effect = HTTPError(secret_url, 403, "Forbidden", {}, io.BytesIO(body))
        code, output = self.run_publish()
        self.assertEqual(code, 1)
        self.assertIn("Discord API code 40333", output)
        self.assertNotIn("private-token", output)
        self.assertEqual([call.args[:2] for call in self.gh.call_args_list], [("release", "upload")])

    def test_discord_non_numeric_or_html_errors_are_not_logged(self):
        secret_url = os.environ["DISCORD_PATCHNOTE_WEBHOOK_URL"]
        bodies = [b"<html>private-token</html>", json.dumps({"code": secret_url}).encode(), b"[]"]
        for body in bodies:
            with self.subTest(body=body):
                self.open.side_effect = HTTPError(secret_url, 403, "Forbidden", {}, io.BytesIO(body))
                code, output = self.run_publish()
                self.assertEqual(code, 1)
                self.assertIn("HTTP 403", output)
                self.assertNotIn("Discord API code", output)
                self.assertNotIn("private-token", output)

    def test_invalid_webhook_is_rejected_before_writes(self):
        with patch.dict(os.environ, {"DISCORD_PATCHNOTE_WEBHOOK_URL": "https://private-token@discord.com/bad"}):
            code, output = self.run_publish()
        self.assertEqual(code, 1)
        self.assertNotIn("private-token", output)
        self.gh.assert_not_called()
        self.open.assert_not_called()

    def test_manual_recovery_replaces_pending_then_sends_without_creating_release(self):
        self.release["assets"] = [{"name": publish_release.PENDING}]
        self.assertEqual(self.run_publish("--existing-release-only", "--retry-undelivered")[0], 0)
        self.assertEqual([call.args[:2] for call in self.gh.call_args_list], [
            ("release", "delete-asset"), ("release", "upload"),
            ("release", "upload"), ("release", "delete-asset"),
        ])
        self.open.assert_called_once()

    def test_manual_recovery_cannot_create_missing_release(self):
        self.api.return_value = None
        code, output = self.run_publish("--existing-release-only", "--retry-undelivered")
        self.assertEqual(code, 1)
        self.assertIn("requires an existing GitHub Release", output)
        self.gh.assert_not_called()
        self.open.assert_not_called()

    def test_manual_recovery_skips_already_sent_release(self):
        self.release["assets"] = [{"name": publish_release.SENT}]
        self.assertEqual(self.run_publish("--existing-release-only", "--retry-undelivered")[0], 0)
        self.gh.assert_not_called()
        self.open.assert_not_called()

    def test_manual_recovery_preserves_pending_when_webhook_is_invalid(self):
        self.release["assets"] = [{"name": publish_release.PENDING}]
        with patch.dict(os.environ, {"DISCORD_PATCHNOTE_WEBHOOK_URL": "invalid"}):
            self.assertEqual(self.run_publish("--existing-release-only", "--retry-undelivered")[0], 1)
        self.gh.assert_not_called()
        self.open.assert_not_called()

    def test_retry_requires_existing_release_only(self):
        self.assertEqual(self.run_publish("--retry-undelivered")[0], 1)
        self.api.assert_not_called()
        self.gh.assert_not_called()
        self.open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
