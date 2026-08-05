#!/usr/bin/env python3
"""Validator for Pasynkov Debugging Cookbook case metadata."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_KEYS = (
    "id", "title", "status", "stack", "versions", "symptoms",
    "expected_behavior", "trigger", "root_cause", "failed_approaches",
    "fix_summary", "verification", "regression_risks", "sources",
)
VALID_STATUSES = {"draft", "reproduced", "verified", "obsolete"}


def scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*([^#\n]+)?$", text)
    return match.group(1).strip().strip("\"'") if match else None


def main() -> int:
    errors: list[str] = []
    files = sorted((ROOT / "cases").glob("*/*/case.yml"))
    if not files:
        errors.append("no case.yml files found")

    seen: set[str] = set()
    for path in files:
        text = path.read_text(encoding="utf-8")
        for key in REQUIRED_KEYS:
            if not re.search(rf"(?m)^{re.escape(key)}:", text):
                errors.append(f"{path.relative_to(ROOT)}: missing '{key}'")
        case_id = scalar(text, "id")
        status = scalar(text, "status")
        if case_id in seen:
            errors.append(f"{path.relative_to(ROOT)}: duplicate id '{case_id}'")
        if case_id:
            seen.add(case_id)
        if status not in VALID_STATUSES:
            errors.append(f"{path.relative_to(ROOT)}: invalid status '{status}'")
        if not path.with_name("README.md").is_file():
            errors.append(f"{path.relative_to(ROOT)}: missing README.md")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated {len(files)} case(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
