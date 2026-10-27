#!/bin/bash
cd "$(dirname "$0")"
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON="$DIR/.venv/bin/python"
    STREAMLIT="$DIR/.venv/bin/streamlit"
elif [ -f "$DIR/../vision_localization_research/.venv/bin/python" ]; then
    PYTHON="$DIR/../vision_localization_research/.venv/bin/python"
    STREAMLIT="$DIR/../vision_localization_research/.venv/bin/streamlit"
elif command -v python3.12 >/dev/null 2>&1; then
    PYTHON="python3.12"
    STREAMLIT="streamlit"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
    STREAMLIT="streamlit"
else
    PYTHON="python"
    STREAMLIT="streamlit"
fi

echo "======================================================================"
echo "   Switch Terrain Map (Ladakh / CU / Ocean / Punjab)"
echo "======================================================================"
"$PYTHON" scripts/switch_terrain_map.py

echo ""
echo "Press Enter to exit..."
read -r
