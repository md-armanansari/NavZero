#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "  REAL AERIAL FLIGHT LOCALIZATION TRACKER"
echo "  Processing 100% Real Photographic Pixels (Zero Synthetic Noise)"
echo "======================================================================"
echo ""
echo "Loading high-resolution real aerial orthophoto into OpenCV..."
echo ""
echo "CONTROLS:"
echo "  [J] = Toggle GPS Jamming ON / OFF"
echo "  [R] = Trigger Autonomous Visual Return-to-Home (V-RTH)"
echo "  [Q] = Exit"
echo ""

if [ -f "$DIR/.venv/bin/python" ]; then
    "$DIR/.venv/bin/python" scripts/run_real_aerial_tracker.py
else
    python3 scripts/run_real_aerial_tracker.py
fi
