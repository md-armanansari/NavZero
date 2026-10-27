#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "   INTERACTIVE REAL-MAP DRONE DISPATCHER (LADAKH SECTOR)"
echo "   Proof of Real-Time Computer Vision (Zero Predefined Routes!)"
echo "======================================================================"
echo ""
echo "HOW TO TEST:"
echo "   - CLICK ANYWHERE ON THE MAP with your mouse (e.g. Kargil, Zanskar, Hanle)."
echo "   - The drone instantly jumps there and camera locks new ground features!"
echo "   - Press [J] = Toggle GPS Jamming ON / OFF"
echo "   - Press [R] = Trigger Autonomous Return-to-Home (V-RTH)"
echo "   - Press [Q] = Exit"
echo ""

if [ -f "$DIR/.venv/bin/python" ]; then
    "$DIR/.venv/bin/python" scripts/run_interactive_map_tracker.py
else
    python3 scripts/run_interactive_map_tracker.py
fi

echo ""
read -p "Press Enter to exit..."
