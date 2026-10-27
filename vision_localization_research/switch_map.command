#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "  Switch Terrain Map (Ladakh / CU Campus / Farmland / Ocean)"
echo "======================================================================"

if [ -f "$DIR/.venv/bin/python" ]; then
    "$DIR/.venv/bin/python" scripts/switch_terrain_map.py
else
    python3 scripts/switch_terrain_map.py
fi

echo ""
read -p "Press Enter to exit..."
