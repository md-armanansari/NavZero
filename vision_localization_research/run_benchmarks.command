#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "   VISION LOCALIZATION RESEARCH - Automated Benchmark Runner"
echo "======================================================================"
echo "Executing benchmark pipeline with unrecorded warmup and 5 steady-state passes..."

if [ -f "$DIR/.venv/bin/python" ]; then
    "$DIR/.venv/bin/python" scripts/run_benchmarks.py
else
    python3 scripts/run_benchmarks.py
fi

echo ""
read -p "Press Enter to exit..."
