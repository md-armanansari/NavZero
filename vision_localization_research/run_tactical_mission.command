#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "   TACTICAL MISSION DISPATCHER & VISUAL WAYPOINT NAVIGATOR"
echo "======================================================================"
echo ""
echo "HOW TO TEST:"
echo "   1. RIGHT-CLICK on the map to set HOME BASE (e.g. runway)."
echo "   2. LEFT-CLICK on the map to set MISSION TARGET."
echo "      -> Drone flies autonomously to target, matching terrain at 30 FPS!"
echo "   3. Press [R] at ANY TIME to CALL THE DRONE BACK to Home Base!"
echo "   4. Press [J] = Toggle GPS Jamming ON / OFF"
echo "   5. Press [Q] = Exit"
echo ""

if [ -f "$DIR/.venv/bin/python" ]; then
    "$DIR/.venv/bin/python" scripts/run_tactical_mission_dispatcher.py
else
    python3 scripts/run_tactical_mission_dispatcher.py
fi

echo ""
read -p "Press Enter to exit..."
