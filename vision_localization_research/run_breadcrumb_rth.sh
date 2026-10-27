#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "  SCENARIO B: AUTONOMOUS ZERO-MAP BREADCRUMB RETURN-TO-HOME (V-RTH)"
echo "  100% Zero Pre-Loaded Map Navigation"
echo "======================================================================"
echo ""
echo "Initializing camera and establishing Home Base (Frame 0)..."
echo ""
echo "CONTROLS:"
echo "  [J] = Toggle GPS Jamming ON / OFF"
echo "  [R] = Trigger Emergency Visual Return-to-Home (V-RTH)"
echo "  [Q] = Exit"
echo ""

if [ -f "$DIR/.venv/bin/python" ]; then
    "$DIR/.venv/bin/python" scripts/run_breadcrumb_rth.py
else
    python3 scripts/run_breadcrumb_rth.py
fi
