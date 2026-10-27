#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "  LIVE PHYSICAL WEBCAM DEMO - GPS-DENIED VISUAL LOCALIZATION"
echo "======================================================================"
echo ""
echo "Starting OpenCV real-time visual tracker..."
echo ""
echo "HOW TO TEST:"
echo "1. Point webcam at any book, printed photo, or phone screen."
echo "2. Press 'S' on your keyboard to SNAP that as your Target Reference."
echo "3. Move the book/phone around - watch green RANSAC inliers track live!"
echo "4. Press 'Q' or ESC in the camera window to exit."
echo ""

if [ -f "$DIR/.venv/bin/python" ]; then
    "$DIR/.venv/bin/python" scripts/run_live_webcam.py
else
    python3 scripts/run_live_webcam.py
fi

echo ""
read -p "Press Enter to exit..."
