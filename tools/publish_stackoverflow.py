#!/usr/bin/env python3
"""
Publish a Question + Self-Answer pair to Stack Overflow / Stack Overflow на русском via the official Stack Exchange API v2.3.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import gzip
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


def get_credentials():
    load_env_file()
    token = os.getenv("STACKOVERFLOW_ACCESS_TOKEN") or os.getenv("STACKEXCHANGE_ACCESS_TOKEN")
    key = os.getenv("STACKEXCHANGE_APP_KEY")
    return token, key


def parse_qa_markdown(file_path, section_title="1. Stack Overflow (English)"):
    """Parse a markdown file containing Stack Overflow Question and Answer sections."""
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    
    # Split text into sections or locate Question and Answer headers
    title = None
    tags = "gnome-shell;gjs;clutter"
    question_body = ""
    answer_body = ""

    current_mode = None
    q_lines = []
    a_lines = []

    for line in text.splitlines():
        if line.startswith("**Title**:") or line.startswith("**Заголовок** Court"):
            title = line.split(":", 1)[1].strip().strip("`")
        elif line.startswith("**Title**:") or line.startswith("**Заголовок**"):
            title = line.split(":", 1)[1].strip().strip("`")
        elif line.startswith("**Tags**:") or line.startswith("**Метки**"):
            raw_tags = line.split(":", 1)[1].strip()
            # Convert space/backtick tags e.g. `gnome-shell` `gjs` -> gnome-shell;gjs
            raw_tags = raw_tags.replace("`", " ").replace(",", " ")
            tag_list = [t.strip() for t in raw_tags.split() if t.strip()]
            tags = ";".join(tag_list[:5])
        elif line.startswith("### Question") or line.startswith("### Вопрос"):
            current_mode = "question"
        elif line.startswith("### Answer") or line.startswith("### Ответ"):
            current_mode = "answer"
        elif current_mode == "question":
            q_lines.append(line)
        elif current_mode == "answer":
            a_lines.append(line)

    question_body = "\n".join(q_lines).strip()
    answer_body = "\n".join(a_lines).strip()

    if not title:
        print("ERROR: Could not parse Question Title from markdown file.", file=sys.stderr)
        sys.exit(1)

    return title, tags, question_body, answer_body


def post_stackexchange_api(endpoint, data_dict):
    """Send POST request to Stack Exchange API, handling gzipped responses."""
    encoded_data = urllib.parse.urlencode(data_dict).encode("utf-8")
    url = f"https://api.stackexchange.com/2.3/{endpoint}"

    req = urllib.request.Request(
        url,
        data=encoded_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Pasynkov-Debugging-Cookbook/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            raw_res = resp.read()
            if resp.info().get("Content-Encoding") == "gzip":
                raw_res = gzip.decompress(raw_res)
            data = json.loads(raw_res.decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        raw_res = e.read()
        if e.headers.get("Content-Encoding") == "gzip":
            raw_res = gzip.decompress(raw_res)
        error_body = raw_res.decode("utf-8")
        print(f"HTTP ERROR {e.code}: {e.reason}", file=sys.stderr)
        print(f"Response: {error_body}", file=sys.stderr)
        sys.exit(1)


def publish_qa(file_path, site="stackoverflow"):
    token, key = get_credentials()
    if not token:
        print("ERROR: STACKOVERFLOW_ACCESS_TOKEN not found in environment or ~/.env", file=sys.stderr)
        print("Please add STACKOVERFLOW_ACCESS_TOKEN=your_token to ~/.env", file=sys.stderr)
        sys.exit(1)

    title, tags, q_body, a_body = parse_qa_markdown(file_path)

    print(f"Publishing Question to {site}...")
    q_data_params = {
        "site": site,
        "title": title,
        "body": q_body,
        "tags": tags,
        "access_token": token
    }
    if key:
        q_data_params["key"] = key

    res_q = post_stackexchange_api("questions/add", q_data_params)
    items = res_q.get("items", [])
    if not items:
        print(f"ERROR creating question: {res_q}", file=sys.stderr)
        sys.exit(1)

    question_id = items[0]["question_id"]
    question_link = items[0]["link"]
    print(f"SUCCESS: Question created! ID: {question_id}, Link: {question_link}")

    print(f"Publishing Self-Answer to Question #{question_id}...")
    a_data_params = {
        "site": site,
        "body": a_body,
        "access_token": token
    }
    if key:
        a_data_params["key"] = key

    res_a = post_stackexchange_api(f"questions/{question_id}/answers/add", a_data_params)
    a_items = res_a.get("items", [])
    if not a_items:
        print(f"ERROR creating answer: {res_a}", file=sys.stderr)
        sys.exit(1)

    answer_id = a_items[0]["answer_id"]
    print(f"SUCCESS: Self-Answer posted! Answer ID: {answer_id}")
    print(f"Full Q&A URL: {question_link}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 publish_stackoverflow.py <path_to_qa_file> [--site stackoverflow|ru.stackoverflow]")
        sys.exit(1)

    file_path = sys.argv[1]
    site = "ru.stackoverflow" if "--ru" in sys.argv else "stackoverflow"

    publish_qa(file_path, site=site)


if __name__ == "__main__":
    main()
