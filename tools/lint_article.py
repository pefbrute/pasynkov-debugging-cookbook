#!/usr/bin/env python3
"""
lint_article.py — Linter for case articles in pasynkov-debugging-cookbook.

Checks markdown article files against technical accuracy rules (Rules 7-12).

Usage:
    python3 tools/lint_article.py <path_to_file_or_dir> [--strict]
"""

import argparse
import re
import sys
from pathlib import Path

# Large integer threshold for unflagged numbers in code or log blocks
LARGE_INT_THRESHOLD = 1000

# Patterns for causal claims that need explicit confidence labeling
STRICT_CAUSAL_WORDS = [
    r'\balways\b',
    r'\bguarantees\b',
    r'\bmakes Clutter\b',
    r'\bwill always\b',
]

# Types that require URL citation nearby if mentioned in prose
TYPE_CITATIONS = [
    r'\bguint\b',
    r'\buint32_t\b',
    r'\bgint32\b',
]


def lint_file(file_path: Path, strict: bool = False):
    errors = []
    warnings = []

    content = file_path.read_text(encoding='utf-8')
    lines = content.splitlines()

    in_code_block = False
    code_block_lang = ''
    code_block_lines = []
    code_block_start_line = 0

    in_blockquote = False
    paragraph_lines = []
    paragraph_start = 1

    def check_code_block(lang, lines, start_line):
        block_text = "\n".join(lines)

        # Check for unflagged large numbers in code / log blocks
        has_illustrative = "ILLUSTRATIVE" in block_text

        # Check return values with hardcoded massive constants
        if re.search(r'return\s+4294967296', block_text):
            errors.append((start_line, "Hardcoded large integer literal return (e.g. return 4294967296) disguised as calculation"))

        # Check for raw log tokens with unexplained high values without illustrative comment
        if lang in ['text', '', 'log']:
            for line_idx, line in enumerate(lines):
                # Pattern: status=4294967040 or similar unexplained token = large_num
                matches = re.findall(r'\b(\w+)=(\d{5,})\b', line)
                for token, val in matches:
                    if not has_illustrative and int(val) >= LARGE_INT_THRESHOLD:
                        # Check surrounding text in block for explanation or disclaimer
                        if "anomalous" not in block_text.lower() and "unconfirmed" not in block_text.lower() and "illustrative" not in block_text.lower():
                            errors.append((start_line + line_idx, f"Unexplained log token '{token}={val}' in log block without explanation or ILLUSTRATIVE marker"))

    for line_num, line in enumerate(lines, 1):
        # Code block boundaries
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_lang = line.strip().lstrip('`').strip()
                code_block_lines = []
                code_block_start_line = line_num
            else:
                check_code_block(code_block_lang, code_block_lines, code_block_start_line)
                in_code_block = False
                code_block_lang = ''
                code_block_lines = []
            continue

        if in_code_block:
            code_block_lines.append(line)
            continue

        # Prose checks
        if line.startswith('>'):
            in_blockquote = True
        elif not line.strip():
            in_blockquote = False

        # Rule 8 check: Strong causal claims in prose
        if not in_blockquote and not line.strip().startswith('#'):
            for pattern in STRICT_CAUSAL_WORDS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if line contains explicit OBSERVED or HYPOTHESIS disclaimer
                    if not re.search(r'\b(OBSERVED|HYPOTHESIS|CONFIRMED)\b', line):
                        warnings.append((line_num, f"Causal assertion word matching '{pattern}' used without confidence label (OBSERVED / HYPOTHESIS / CONFIRMED)"))

            # Rule 7 check: Types mentioned without citation
            for type_pat in TYPE_CITATIONS:
                if re.search(type_pat, line):
                    if "http://" not in line and "https://" not in line and "docs" not in line.lower():
                        warnings.append((line_num, f"Internal type '{type_pat}' mentioned in prose without nearby URL citation or documentation link"))

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Lint case article markdown files for technical accuracy.")
    parser.add_argument("target", type=str, help="Path to article markdown file or case directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    target_path = Path(args.target)
    if target_path.is_dir():
        md_files = list(target_path.glob("**/*.md"))
    elif target_path.is_file():
        md_files = [target_path]
    else:
        print(f"Error: Target path '{target_path}' does not exist.")
        sys.exit(1)

    total_errors = 0
    total_warnings = 0

    for md_file in md_files:
        rel_path = md_file
        errors, warnings = lint_file(md_file, args.strict)

        for line_num, msg in errors:
            print(f"ERROR {rel_path}:{line_num} — {msg}")
            total_errors += 1

        for line_num, msg in warnings:
            print(f"WARNING {rel_path}:{line_num} — {msg}")
            total_warnings += 1

    if total_errors > 0 or (args.strict and total_warnings > 0):
        print(f"\n❌ Lint failed: {total_errors} error(s), {total_warnings} warning(s)")
        sys.exit(1)
    else:
        print(f"✅ Lint passed for {len(md_files)} file(s) ({total_warnings} warning(s)).")
        sys.exit(0)


if __name__ == '__main__':
    main()
