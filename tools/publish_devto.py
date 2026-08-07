#!/usr/bin/env python3
"""
Publish an article markdown file to DEV.to via the official DEV.to API.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path


def load_env_file():
    """Attempt to load API keys from ~/.env or local .env if present."""
    env_paths = [Path.home() / ".env", Path.cwd() / ".env"]
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k not in os.environ:
                            os.environ[k] = v


def get_api_key():
    """Retrieve DEV.to API key from environment."""
    load_env_file()
    key = os.getenv("DEVTO_API_KEY") or os.getenv("DEV_TO_API_KEY")
    return key


def parse_frontmatter(content):
    """Simple parser for YAML frontmatter at the top of markdown files."""
    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()
            for line in fm_text.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k == "tags":
                        # Convert comma-separated string or bracketed array
                        v = v.strip("[]")
                        tags = [t.strip().strip("'\"") for t in v.split(",") if t.strip()]
                        frontmatter["tags"] = tags
                    elif k == "published":
                        frontmatter["published"] = v.lower() in ("true", "1", "yes")
                    else:
                        frontmatter[k] = v

    return frontmatter, body


def publish_article(file_path, publish=False):
    key = get_api_key()
    if not key:
        print("ERROR: DEV.to API key not found in environment or ~/.env", file=sys.stderr)
        print("Please add DEVTO_API_KEY=your_key to ~/.env", file=sys.stderr)
        sys.exit(1)

    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    title = fm.get("title")
    if not title:
        # Fallback to first h1 heading
        for line in body.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if not title:
            title = path.stem.replace("_", " ").title()

    tags = fm.get("tags", ["debugging", "linux"])
    if isinstance(tags, list):
        tags = tags[:4]

    canonical_url = fm.get("canonical_url")
    published_state = publish or fm.get("published", False)

    payload = {
        "article": {
            "title": title,
            "body_markdown": content,
            "published": published_state,
            "tags": tags
        }
    }
    if canonical_url:
        payload["article"]["canonical_url"] = canonical_url

    # Check if article already exists for this user via GET /api/articles/me/all
    existing_id = None
    try:
        me_req = urllib.request.Request(
            "https://dev.to/api/articles/me/all",
            headers={"api-key": key, "User-Agent": "Pasynkov-Debugging-Cookbook/1.0"}
        )
        with urllib.request.urlopen(me_req) as me_resp:
            my_articles = json.loads(me_resp.read().decode("utf-8"))
            for art in my_articles:
                if canonical_url and art.get("canonical_url") == canonical_url:
                    existing_id = art["id"]
                    break
                elif art.get("title") == title:
                    existing_id = art["id"]
                    break
    except Exception:
        pass

    req_data = json.dumps(payload).encode("utf-8")
    if existing_id:
        url = f"https://dev.to/api/articles/{existing_id}"
        method = "PUT"
    else:
        url = "https://dev.to/api/articles"
        method = "POST"

    req = urllib.request.Request(
        url,
        data=req_data,
        headers={
            "api-key": key,
            "Content-Type": "application/json",
            "User-Agent": "Pasynkov-Debugging-Cookbook/1.0"
        },
        method=method
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            action_name = "updated" if existing_id else "posted"
            print(f"SUCCESS: Article {action_name} on DEV.to! (ID: {data.get('id')})")
            print(f"Title: {data.get('title')}")
            print(f"URL: {data.get('url')}")
            print(f"Status: {'Published' if data.get('published') else 'Draft'}")
            return data

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP ERROR {e.code}: {e.reason}", file=sys.stderr)
        print(f"Response: {error_body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR publishing to DEV.to: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 publish_devto.py <path_to_markdown_file> [--publish]")
        sys.exit(1)

    file_path = sys.argv[1]
    publish_now = "--publish" in sys.argv

    publish_article(file_path, publish=publish_now)


if __name__ == "__main__":
    main()
