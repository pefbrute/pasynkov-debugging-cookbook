#!/usr/bin/env python3
"""Build machine-readable indexes (cases_index.json, dataset.jsonl) and update README.md catalog table."""

import argparse
import json
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_KEYS = (
    "id", "title", "status", "stack", "versions", "symptoms",
    "expected_behavior", "trigger", "root_cause", "failed_approaches",
    "fix_summary", "verification", "regression_risks", "sources", "upstream",
)



def parse_yaml_fallback(text: str) -> dict:
    """Basic YAML parser fallback if PyYAML is not installed."""
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


def load_case_yml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    return parse_yaml_fallback(text)


def capitalize_stack(stack: list[str] | str) -> str:
    if isinstance(stack, list):
        if not stack:
            return "General"
        primary = stack[0]
    else:
        primary = str(stack)
    mapping = {
        "gnome-shell": "GNOME Shell",
        "gjs": "GNOME Shell",
        "clutter": "GNOME Shell",
        "python": "Python",
        "flutter": "Flutter",
        "android": "Android",
        "linux": "Linux",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "docker": "Docker",
        "postgres": "PostgreSQL",
    }
    return mapping.get(primary.lower(), primary.replace("-", " ").title())


def build_catalog_table(cases: list[dict]) -> str:
    lines = [
        "| Stack | Case | Status |",
        "|---|---|---|",
    ]
    for case in cases:
        stack_display = capitalize_stack(case.get("stack", []))
        title = case.get("title", "")
        rel_path = case.get("rel_path", "")
        status = str(case.get("status", "")).capitalize()
        lines.append(f"| {stack_display} | [{title}]({rel_path}/) | {status} |")
    return "\n".join(lines)


def build_instruction_record(case: dict) -> dict:
    stack = ", ".join(case["stack"]) if isinstance(case.get("stack"), list) else str(case.get("stack"))
    symptoms = "; ".join(case["symptoms"]) if isinstance(case.get("symptoms"), list) else str(case.get("symptoms"))
    versions = case.get("versions", {})
    if isinstance(versions, dict):
        vers_str = f"OS: {versions.get('os', 'N/A')}, Runtime: {versions.get('runtime', 'N/A')}"
    else:
        vers_str = str(versions)

    user_input = (
        f"Stack: {stack}\n"
        f"Versions: {vers_str}\n"
        f"Symptom: {symptoms}\n"
        f"Trigger: {case.get('trigger', '')}"
    )

    return {
        "id": case.get("id"),
        "system": (
            "You are an expert software engineer and debugging assistant. "
            "Use empirical evidence and verified root causes to diagnose software failures, "
            "avoid disproven approaches, and provide minimal effective fixes."
        ),
        "input": user_input,
        "target_diagnosis": {
            "expected_behavior": case.get("expected_behavior"),
            "root_cause": case.get("root_cause"),
            "failed_approaches": case.get("failed_approaches"),
            "fix_summary": case.get("fix_summary"),
            "verification": case.get("verification"),
            "regression_risks": case.get("regression_risks"),
            "sources": case.get("sources"),
            "upstream": case.get("upstream"),
        },

    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build dataset artifacts and sync catalog")
    parser.add_argument("--check", action="store_true", help="Check if generated artifacts are up to date without writing")
    args = parser.parse_args()

    files = sorted((ROOT / "cases").glob("*/*/case.yml"))
    cases = []
    dataset_records = []

    for path in files:
        case_data = load_case_yml(path)
        rel_dir = path.parent.relative_to(ROOT).as_posix()
        case_data["rel_path"] = rel_dir
        cases.append(case_data)
        dataset_records.append(build_instruction_record(case_data))

    cases_index_json = json.dumps(cases, indent=2, ensure_ascii=False) + "\n"
    dataset_jsonl = "\n".join(json.dumps(rec, ensure_ascii=False) for rec in dataset_records) + "\n"

    # Catalog table update in README.md
    readme_path = ROOT / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")
    table_markdown = build_catalog_table(cases)
    
    pattern = r"(<!-- CASE_CATALOG_START -->\n)(.*?)(<!-- CASE_CATALOG_END -->)"
    if re.search(pattern, readme_text, flags=re.DOTALL):
        new_readme_text = re.sub(pattern, f"\\1{table_markdown}\n\\3", readme_text, flags=re.DOTALL)
    else:
        new_readme_text = readme_text

    index_file = ROOT / "cases_index.json"
    dataset_file = ROOT / "dataset.jsonl"

    if args.check:
        dirty = False
        if not index_file.is_file() or index_file.read_text(encoding="utf-8") != cases_index_json:
            print("cases_index.json is out of date")
            dirty = True
        if not dataset_file.is_file() or dataset_file.read_text(encoding="utf-8") != dataset_jsonl:
            print("dataset.jsonl is out of date")
            dirty = True
        if readme_text != new_readme_text:
            print("README.md catalog table is out of date")
            dirty = True
        if dirty:
            return 1
        print("All dataset artifacts are up to date.")
        return 0

    index_file.write_text(cases_index_json, encoding="utf-8")
    dataset_file.write_text(dataset_jsonl, encoding="utf-8")
    readme_path.write_text(new_readme_text, encoding="utf-8")

    print(f"Generated cases_index.json ({len(cases)} cases)")
    print(f"Generated dataset.jsonl ({len(dataset_records)} records)")
    print("Updated README.md catalog table successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
