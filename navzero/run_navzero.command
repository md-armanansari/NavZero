#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "   NavZero: Autonomous Optical GPS-Denied Navigation"
echo "   Atmanirbhar Bharat Indigenous Defence Software (macOS)"
echo "=========================================================="
echo "Starting Tactical Ground Control Station Dashboard..."

if [ -f "$DIR/../vision_localization_research/.venv/bin/streamlit" ]; then
    "$DIR/../vision_localization_research/.venv/bin/streamlit" run app.py
elif [ -f "$DIR/.venv/bin/streamlit" ]; then
    "$DIR/.venv/bin/streamlit" run app.py
elif command -v streamlit &>/dev/null; then
    streamlit run app.py
else
    python3 -m streamlit run app.py
fi

echo ""
read -p "Press Enter to exit..."
