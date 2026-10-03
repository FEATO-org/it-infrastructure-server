"""Publish a release, then deliver Discord payloads with conservative retry state."""

from __future__ import annotations

import argparse
from http.client import HTTPException
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from common import check_version

PENDING = "discord-delivery-pending.json"
SENT = "discord-delivery-sent.json"
DISCORD_USER_AGENT = "DiscordBot (https://github.com/FEATO-org/it-infrastructure-server, 1.0)"


def gh(*args: str) -> str:
    return subprocess.check_output(("gh", *args), text=True).strip()


def github_api(endpoint: str, *, allow_not_found: bool = False) -> dict | None:
    result = subprocess.run(("gh", "api", "--include", endpoint), capture_output=True, text=True)
    match = re.match(r"HTTP/\S+ (\d{3})", result.stdout)
    status = int(match.group(1)) if match else None
    if result.returncode:
        if allow_not_found and status == 404:
            return None
        raise ValueError(f"GitHub API request failed (HTTP {status or 'unknown'}); refusing to infer absence")
    _, separator, body = result.stdout.partition("\n\n")
    if not separator or status != 200:
        raise ValueError("GitHub API returned an unexpected response")
    value = json.loads(body)
    if not isinstance(value, dict):
        raise ValueError("GitHub API returned an unexpected JSON value")
    return value


def webhook_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username
                or parsed.password or parsed.fragment or parsed.port not in (None, 443)
                or any(character.isspace() for character in value)):
            raise ValueError
    except ValueError:
        raise ValueError("DISCORD_PATCHNOTE_WEBHOOK_URL must be a valid HTTPS URL") from None
    query = [(key, item) for key, item in parse_qsl(parsed.query) if key != "wait"]
    query.append(("wait", "true"))
    return urlunsplit(parsed._replace(query=urlencode(query)))


def discord_error_code(error: HTTPError) -> int | None:
    if error.fp is None:
        return None
    try:
        body = json.loads(error.read(4096))
    except (OSError, ValueError, TypeError):
        return None
    code = body.get("code") if isinstance(body, dict) else None
    return code if type(code) is int else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--patchnote", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    args = parser.parse_args()
    try:
        version = check_version(args.version)
        tag = f"server-{version}"
        note = args.patchnote.read_text(encoding="utf-8")
        payloads = json.loads(args.payload.read_text(encoding="utf-8"))
        if not payloads or not isinstance(payloads, list):
            raise ValueError("Discord payload is empty")
        endpoint = f"repos/{os.environ['GITHUB_REPOSITORY']}"
        release = github_api(f"{endpoint}/releases/tags/{tag}", allow_not_found=True)
        if release is None:
            # An existing tag without a release is ambiguous: never replace it.
            if github_api(f"{endpoint}/git/ref/tags/{tag}", allow_not_found=True) is not None:
                raise ValueError(f"{tag}: tag exists without a GitHub Release")
            gh("release", "create", tag, "--target", args.commit, "--title", f"Minecraft Server Patch {version}", "--notes-file", str(args.patchnote))
            release = github_api(f"{endpoint}/releases/tags/{tag}")
        if release.get("draft") or release.get("prerelease"):
            raise ValueError(f"{tag}: expected a published, non-prerelease GitHub Release")
        if not isinstance(release.get("body"), str) or release["body"].rstrip("\n") != note.rstrip("\n"):
            raise ValueError(f"{tag}: existing release body differs from patchnote")
        assets = {asset["name"] for asset in release["assets"]}
        if SENT in assets:
            print(f"{tag}: already published to Discord")
            return 0
        if PENDING in assets:
            raise ValueError(f"{tag}: Discord delivery is uncertain; inspect webhook channel before manual retry")
        webhook = webhook_url(os.environ["DISCORD_PATCHNOTE_WEBHOOK_URL"])
        with tempfile.TemporaryDirectory() as temp:
            pending = Path(temp, PENDING)
            pending.write_text(json.dumps({"version": version, "state": "pending"}), encoding="utf-8")
            gh("release", "upload", tag, str(pending))
            # A timeout or crash after Discord accepts a message is ambiguous. The
            # pending asset blocks automatic retries and therefore duplicate posts.
            for payload in payloads:
                try:
                    request = Request(
                        webhook,
                        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                        headers={"Content-Type": "application/json", "User-Agent": DISCORD_USER_AGENT},
                        method="POST",
                    )
                    with urlopen(request, timeout=30) as response:
                        if response.status != 200:
                            raise ValueError(f"Discord returned HTTP {response.status}")
                        confirmation = json.load(response)
                        if not isinstance(confirmation, dict) or not confirmation.get("id"):
                            raise ValueError("Discord did not confirm a message ID")
                except HTTPError as exc:
                    code = discord_error_code(exc)
                    detail = f" (Discord API code {code})" if code is not None else ""
                    raise ValueError(f"Discord returned HTTP {exc.code}{detail}; delivery state requires manual review") from None
                except URLError as exc:
                    raise ValueError(f"Discord delivery uncertain: {type(exc.reason).__name__}") from None
                except (OSError, HTTPException) as exc:
                    raise ValueError(f"Discord delivery uncertain: {type(exc).__name__}") from None
            sent = Path(temp, SENT)
            sent.write_text(json.dumps({"version": version, "state": "sent"}), encoding="utf-8")
            gh("release", "upload", tag, str(sent))
            gh("release", "delete-asset", tag, PENDING, "--yes")
        print(f"{tag}: release and Discord delivery complete")
    except (KeyError, OSError, subprocess.CalledProcessError, ValueError, json.JSONDecodeError) as exc:
        print(f"publish release: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
