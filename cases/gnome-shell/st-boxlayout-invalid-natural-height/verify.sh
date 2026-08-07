#!/usr/bin/env bash
set -euo pipefail

CASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$CASE_DIR/../../.." && pwd)"

echo "[1/3] Checking JS syntax for reproduction, broken, and fixed implementations..."
if command -v node >/dev/null 2>&1; then
    node --check "$CASE_DIR/reproduction/extension.js"
    node --check "$CASE_DIR/broken/extension.js"
    node --check "$CASE_DIR/fixed/extension.js"
    echo "  ✓ JS syntax valid."
else
    echo "  ! Node.js not found, skipping JS syntax check."
fi

echo "[2/3] Checking metadata files..."
if [ -f "$CASE_DIR/case.yml" ] && [ -f "$CASE_DIR/README.md" ] && [ -f "$CASE_DIR/reproduction/metadata.json" ]; then
    echo "  ✓ Metadata files present."
else
    echo "  ✗ Missing metadata files!"
    exit 1
fi

echo "[3/3] Running project validator..."
python3 "$ROOT_DIR/tools/validate_cases.py"

echo "✓ Case verification successful!"
