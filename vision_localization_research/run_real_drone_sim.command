#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "   AUTONOMOUS REAL-DRONE FLIGHT & GPS-JAMMING SIMULATOR"
echo "======================================================================"
echo "Launching flight computer and visual telemetry loop..."
echo ""
echo "CONTROLS:"
echo "   [J] = Toggle GPS Jamming ON / OFF"
echo "   [R] = Trigger Autonomous Visual Return-to-Home (V-RTH)"
echo "   [Q] = Exit simulator"
echo ""

if [ -f "$DIR/.venv/bin/python" ]; then
    "$DIR/.venv/bin/python" scripts/run_drone_sim.py
else
    python3 scripts/run_drone_sim.py
fi

echo ""
read -p "Press Enter to exit..."
