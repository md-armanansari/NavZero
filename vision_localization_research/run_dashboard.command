#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "   VISION LOCALIZATION RESEARCH - Offline Evaluation Dashboard"
echo "======================================================================"
echo "Launching Streamlit evaluation interface..."

if [ -f "$DIR/.venv/bin/streamlit" ]; then
    "$DIR/.venv/bin/streamlit" run src/vision_loc/dashboard_app.py --server.port 8502
elif command -v streamlit &>/dev/null; then
    streamlit run src/vision_loc/dashboard_app.py --server.port 8502
else
    python3 -m streamlit run src/vision_loc/dashboard_app.py --server.port 8502
fi

echo ""
read -p "Press Enter to exit..."
