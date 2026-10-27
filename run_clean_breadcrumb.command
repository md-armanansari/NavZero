#!/bin/bash
cd "$(dirname "$0")"
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$DIR/vision_localization_research/.venv/bin/python" ]; then
    PYTHON="$DIR/vision_localization_research/.venv/bin/python"
    STREAMLIT="$DIR/vision_localization_research/.venv/bin/streamlit"
elif [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON="$DIR/.venv/bin/python"
    STREAMLIT="$DIR/.venv/bin/streamlit"
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
echo "  PROJECT NAVZERO - SCENARIO B: CLEAN TEACH-AND-REPEAT RETURN-TO-HOME"
echo "  Phase 1: Record Trail Quietly -> Phase 2: Compare in Reverse on Return"
echo "======================================================================"
echo ""
cd "$DIR/vision_localization_research"
"$PYTHON" scripts/run_clean_breadcrumb_rth.py

echo ""
echo "Press Enter to exit..."
read -r
