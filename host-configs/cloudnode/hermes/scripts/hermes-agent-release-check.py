#!/usr/bin/env python3
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

REPO_API = "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest"
COMPARE_API = "https://api.github.com/repos/NousResearch/hermes-agent/compare"
_REPO = "NousResearch/hermes-agent"


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))).expanduser()


def state_path() -> Path:
    return hermes_home() / "cron" / "hermes-agent-release-state.json"


def fetch_latest() -> dict:
    req = Request(
        REPO_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Hermes-Agent-Release-Checker",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_state() -> dict:
    p = state_path()
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def save_state(state: dict) -> None:
    p = state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2, sort_keys=True))


def main() -> None:
    try:
        latest = fetch_latest()
    except (HTTPError, URLError, TimeoutError, Exception) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 1

    state = load_state()
    previous_tag = state.get("last_seen_tag")
    current_tag = latest.get("tag_name")
    body = latest.get("body") or ""
    body_excerpt = body[:4000]

    changed = previous_tag not in (None, current_tag)

    # Check commit drift: how far ahead main is past the latest tag
    behind_main = None
    if current_tag:
        try:
            compare_url = f"{COMPARE_API}/{current_tag}...main"
            req = Request(
                compare_url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "Hermes-Agent-Release-Checker",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            with urlopen(req, timeout=15) as resp:
                compare_data = json.loads(resp.read().decode("utf-8"))
            behind_main = compare_data.get("total_commits", 0)
        except Exception:
            behind_main = None

    save_state(
        {
            "last_seen_tag": current_tag,
            "last_seen_name": latest.get("name"),
            "last_seen_published_at": latest.get("published_at"),
            "last_seen_html_url": latest.get("html_url"),
        }
    )

    print(
        json.dumps(
            {
                "ok": True,
                "changed": changed,
                "behind_main": behind_main,
                "previous_tag": previous_tag,
                "latest": {
                    "tag_name": current_tag,
                    "name": latest.get("name"),
                    "published_at": latest.get("published_at"),
                    "html_url": latest.get("html_url"),
                    "body_excerpt": body_excerpt,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
