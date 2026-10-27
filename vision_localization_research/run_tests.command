#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "  RUNNING 34 AUTOMATED RESEARCH UNIT & INTEGRATION TESTS (pytest)"
echo "======================================================================"

if [ -f "$DIR/.venv/bin/pytest" ]; then
    "$DIR/.venv/bin/pytest" -v
else
    python3 -m pytest -v
fi

echo ""
read -p "Press Enter to exit..."
