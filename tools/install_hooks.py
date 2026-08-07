#!/usr/bin/env python3
"""
install_hooks.sh alternative — installs git hooks for this repo.
Run: python3 tools/install_hooks.py
"""
import shutil
import stat
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
hooks_dir = repo_root / ".git" / "hooks"
tools_dir = repo_root / "tools"

if not hooks_dir.exists():
    print("ERROR: .git/hooks directory not found. Are you in a git repo?")
    sys.exit(1)

hook_src = tools_dir / "pre-commit.hook"
hook_dst = hooks_dir / "pre-commit"

if not hook_src.exists():
    print(f"ERROR: {hook_src} not found")
    sys.exit(1)

shutil.copy2(hook_src, hook_dst)
hook_dst.chmod(hook_dst.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

print(f"✅ Installed pre-commit hook: {hook_dst}")
print("   The hook will run lint_article.py on modified .md files before each commit.")
print("   To test: python3 tools/lint_article.py cases/<id>/article.md")
