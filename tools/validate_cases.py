#!/usr/bin/env python3
"""Validator for Pasynkov Debugging Cookbook case metadata and dataset index sync."""

from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED_KEYS = (
    "id", "title", "status", "stack", "versions", "symptoms",
    "expected_behavior", "trigger", "root_cause", "failed_approaches",
    "fix_summary", "verification", "regression_risks", "sources", "upstream",
)
VALID_STATUSES = {"draft", "reproduced", "verified", "obsolete"}
VALID_UPSTREAM_STATUSES = {
    "not-submitted", "issue-opened", "needs-confirmation",
    "mr-opened", "accepted", "rejected",
}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")



def parse_yaml_fallback(text: str) -> dict:
    data = {}
    current_key = None
    for line in text.splitlines():
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("#"):
            continue
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            key, val = line.split(":", 1)
            current_key = key.strip()
            val = val.strip().strip("\"'")
            if val:
                data[current_key] = val
            else:
                data[current_key] = []
        elif current_key and (line_strip.startswith("- ") or line_strip.startswith("* ")):
            item = line_strip[2:].strip().strip("\"'")
            if isinstance(data[current_key], list):
                data[current_key].append(item)
    return data


def load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    return parse_yaml_fallback(text)


def main() -> int:
    errors: list[str] = []
    files = sorted((ROOT / "cases").glob("*/*/case.yml"))
    if not files:
        errors.append("no case.yml files found")

    seen_ids: set[str] = set()
    for path in files:
        rel = path.relative_to(ROOT)
        data = load_yaml(path)
        if not isinstance(data, dict):
            errors.append(f"{rel}: invalid YAML format")
            continue

        for key in REQUIRED_KEYS:
            if key not in data or data[key] is None:
                errors.append(f"{rel}: missing or null required key '{key}'")

        case_id = data.get("id")
        status = data.get("status")
        last_verified = str(data.get("last_verified", ""))

        if case_id in seen_ids:
            errors.append(f"{rel}: duplicate id '{case_id}'")
        if case_id:
            seen_ids.add(case_id)

        if status not in VALID_STATUSES:
            errors.append(f"{rel}: invalid status '{status}' (must be one of {sorted(VALID_STATUSES)})")

        upstream = data.get("upstream")
        if isinstance(upstream, dict):
            up_status = upstream.get("status")
            if up_status not in VALID_UPSTREAM_STATUSES:
                errors.append(f"{rel}: invalid upstream.status '{up_status}' (must be one of {sorted(VALID_UPSTREAM_STATUSES)})")
        elif upstream is not None:
            errors.append(f"{rel}: 'upstream' must be a dictionary")

        if last_verified and not DATE_PATTERN.match(last_verified):

            errors.append(f"{rel}: last_verified date '{last_verified}' must use YYYY-MM-DD format")

        if not path.with_name("README.md").is_file():
            errors.append(f"{rel}: missing README.md in case directory")

    # Check dataset sync using build_dataset.py logic
    try:
        from tools.build_dataset import main as check_datasets
        sys.argv = ["build_dataset.py", "--check"]
        if check_datasets() != 0:
            errors.append("Dataset artifacts (cases_index.json, dataset.jsonl, or README.md catalog) are out of sync. Run 'python3 tools/build_dataset.py' to resolve.")
    except Exception as exc:
        errors.append(f"Failed to check dataset artifact sync: {exc}")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(files)} case(s) and dataset artifacts successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
