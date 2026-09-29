"""Publish a release, then deliver Discord payloads with conservative retry state."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from common import check_version

PENDING = "discord-delivery-pending.json"
SENT = "discord-delivery-sent.json"


def gh(*args: str) -> str:
    return subprocess.check_output(("gh", *args), text=True).strip()


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
        webhook = os.environ["DISCORD_PATCHNOTE_WEBHOOK_URL"]
        if not webhook.startswith("https://"):
            raise ValueError("DISCORD_PATCHNOTE_WEBHOOK_URL must be HTTPS")
        try:
            release = json.loads(gh("release", "view", tag, "--json", "body,assets"))
        except subprocess.CalledProcessError:
            # An existing tag without a release is ambiguous: never replace it.
            try:
                gh("api", f"repos/{os.environ['GITHUB_REPOSITORY']}/git/ref/tags/{tag}")
            except subprocess.CalledProcessError:
                pass
            else:
                raise ValueError(f"{tag}: tag exists without a GitHub Release")
            gh("release", "create", tag, "--target", args.commit, "--title", f"Minecraft Server Patch {version}", "--notes-file", str(args.patchnote))
            release = json.loads(gh("release", "view", tag, "--json", "body,assets"))
        if release["body"].rstrip("\n") != note.rstrip("\n"):
            raise ValueError(f"{tag}: existing release body differs from patchnote")
        assets = {asset["name"] for asset in release["assets"]}
        if SENT in assets:
            print(f"{tag}: already published to Discord")
            return 0
        if PENDING in assets:
            raise ValueError(f"{tag}: Discord delivery is uncertain; inspect webhook channel before manual retry")
        with tempfile.TemporaryDirectory() as temp:
            pending = Path(temp, PENDING)
            pending.write_text(json.dumps({"version": version, "state": "pending"}), encoding="utf-8")
            gh("release", "upload", tag, str(pending))
            # A timeout or crash after Discord accepts a message is ambiguous. The
            # pending asset blocks automatic retries and therefore duplicate posts.
            for payload in payloads:
                request = Request(webhook + ("&" if "?" in webhook else "?") + "wait=true", data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                try:
                    with urlopen(request, timeout=30) as response:
                        if response.status != 200:
                            raise ValueError(f"Discord returned HTTP {response.status}")
                        if not json.load(response).get("id"):
                            raise ValueError("Discord did not confirm a message ID")
                except HTTPError as exc:
                    raise ValueError(f"Discord returned HTTP {exc.code}; delivery state requires manual review") from None
                except URLError as exc:
                    raise ValueError(f"Discord delivery uncertain: {type(exc.reason).__name__}") from None
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
