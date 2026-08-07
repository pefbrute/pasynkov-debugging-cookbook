#!/usr/bin/env python3
"""CLI script to generate a new debugging case template with auto-detected system specs."""

import argparse
import datetime
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cmd(cmd: str) -> str:
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""


def get_system_specs() -> dict:
    # OS
    lsb = run_cmd("lsb_release -d")
    if ":" in lsb:
        os_name = lsb.split(":", 1)[1].strip()
    else:
        os_name = "Ubuntu 22.04.5 LTS"
    arch = run_cmd("uname -m") or "x86_64"
    os_str = f"{os_name} (Linux {arch})"

    # GNOME Shell & GJS
    gnome_ver = run_cmd("gnome-shell --version") or "GNOME Shell 42.9"
    gjs_ver = run_cmd("gjs --version") or "1.72.4"
    if gjs_ver.startswith("gjs "):
        gjs_ver = gjs_ver[4:].strip()
    if "GNOME Shell" in gnome_ver:
        gs_num = gnome_ver.replace("GNOME Shell", "").strip()
        runtime_str = f"GNOME Shell {gs_num} (GJS {gjs_ver})"
        session_str = f"Wayland and X11 GNOME Shell {gs_num} Sessions"
    else:
        runtime_str = f"{gnome_ver} (GJS {gjs_ver})"
        session_str = "Wayland and X11 GNOME Shell Sessions"

    # CPU & GPU
    cpu = run_cmd("lscpu | grep 'Model name:' | head -n 1")
    if ":" in cpu:
        cpu_name = cpu.split(":", 1)[1].strip()
    else:
        cpu_name = "13th Gen Intel Core i7-1355U"

    gpu = run_cmd("lspci | grep -i vga | head -n 1")
    if "Intel" in gpu:
        gpu_name = "Intel Raptor Lake Graphics"
    elif ":" in gpu:
        gpu_name = gpu.split(":", 1)[1].strip()
    else:
        gpu_name = "Integrated Graphics"

    hardware_str = f"{cpu_name} / {gpu_name}"

    return {
        "os": os_str,
        "runtime": runtime_str,
        "hardware": hardware_str,
        "session": session_str,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a new debugging case template")
    parser.add_argument("case_id", help="Unique ID of the case (e.g. gnome-shell-custom-popup-focus)")
    parser.add_argument("--title", help="Short descriptive title of the issue", default=None)
    parser.add_argument("--stack", help="Primary tech stack (default: gnome-shell)", default="gnome-shell")
    parser.add_argument("--no-build", action="store_true", help="Skip running build_dataset.py after creation")
    args = parser.parse_args()

    case_id = args.case_id.strip().lower()
    # Sanitize case_id for folder name
    folder_name = case_id
    if folder_name.startswith(f"{args.stack}-"):
        folder_name = folder_name[len(args.stack) + 1:]

    target_dir = ROOT / "cases" / args.stack / folder_name
    if target_dir.exists():
        print(f"Error: Case directory already exists at {target_dir}")
        return 1

    specs = get_system_specs()
    today = datetime.date.today().isoformat()
    title = args.title or case_id.replace("-", " ").title()

    # Build case.yml content
    case_yml_content = f"""id: {case_id}
title: "{title}"
status: verified
stack:
  - {args.stack}
  - gjs
  - clutter
versions:
  os: "{specs['os']}"
  runtime: "{specs['runtime']}"
  dependencies:
    mutter: ">= 42.0"
environment:
  hardware: "{specs['hardware']}"
  extra: "{specs['session']}"
symptoms:
  - "Describe observed error symptom or unexpected behavior"
expected_behavior: "Describe the expected correct behavior"
trigger: "Describe how to reproduce or trigger the issue"
root_cause: "Explain the underlying root cause discovered during debugging"
failed_approaches:
  - approach: "Disproven or naive approach that failed"
    result: "Exact failure result or error message"
fix_summary: "Minimal effective fix summary"
verification:
  automated: true
  command: "node --check extension.js"
  manual_steps:
    - "Step 1 to manually verify fix"
    - "Step 2 to manually verify fix"
regression_risks:
  - "Potential regression risk or edge case to watch out for"
sources:
  - "https://gjs.guide/"
upstream:
  project: "GNOME/gnome-shell"
  issue: null
  merge_request: null
  status: not-submitted
last_verified: "{today}"
"""

    # Build README.md content
    readme_content = f"""# {title}

## Short answer

Provide a concise 1-2 sentence explanation of the solution.

## Environment

- **OS**: {specs['os']}
- **Runtime**: {specs['runtime']}
- **Hardware**: {specs['hardware']}
- **Session**: Wayland & X11

## Fix

```javascript
// Minimal effective fix code snippet
```

## Verification

1. Step 1
2. Step 2
"""

    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "case.yml").write_text(case_yml_content, encoding="utf-8")
    (target_dir / "README.md").write_text(readme_content, encoding="utf-8")

    print(f"✅ Created new case template in {target_dir.relative_to(ROOT)}")
    print(f"   - case.yml ({specs['os']}, {specs['runtime']})")
    print(f"   - README.md")

    if not args.no_build:
        print("\n🔄 Rebuilding dataset artifacts (cases_index.json, dataset.jsonl)...")
        build_script = ROOT / "tools" / "build_dataset.py"
        res = subprocess.run([sys.executable, str(build_script)], capture_output=True, text=True)
        print(res.stdout.strip())
        if res.returncode != 0:
            print(res.stderr.strip(), file=sys.stderr)
            return res.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
