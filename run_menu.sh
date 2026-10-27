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

while true; do
    clear
    echo "========================================================================"
    echo "       NAVZERO / VISION LOCALIZATION - DEFENSE PROJECT CONTROL SUITE    "
    echo "========================================================================"
    echo " Choose a scenario or tool to run on macOS:"
    echo ""
    echo " [1]  Scenario B: Clean Teach & Repeat (V-RTH) [Live Webcam]"
    echo " [2]  Tactical Mission Dispatcher (Fly to Target & Return Home) [Real Map]"
    echo " [3]  Interactive Drone Tracker (Click Map Anywhere to Dispatch)"
    echo " [4]  Autonomous Real-Drone Autopilot & GPS-Jamming Cockpit"
    echo " [5]  Real Aerial Orthophoto Flight Tracker (100% Real Photo Pixels)"
    echo " [6]  Live Physical Webcam Visual Feature Matching Demo"
    echo " [7]  Scenario B: Visual Breadcrumb Return-to-Home (Classic)"
    echo " [8]  Run Research Benchmark Suite (Generate Metrics & Plots)"
    echo " [9]  Streamlit Offline Evaluation Dashboard (Port 8502)"
    echo " [10] NavZero Tactical Ground Control Station (Streamlit Port 8501)"
    echo " [11] Switch Active Terrain Map (Ladakh / CU Campus / Ocean / Punjab)"
    echo " [12] Run Full Automated Pytest Suite"
    echo " [13] Re-Generate Defense Proposal & Explanation PDFs"
    echo " [Q]  Quit"
    echo "========================================================================"
    read -p "Enter choice [1-13 or Q]: " choice

    case "$choice" in
        1)
            echo ""
            echo "Starting Scenario B Clean Teach-and-Repeat..."
            cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_clean_breadcrumb_rth.py
            read -p "Press Enter to return to menu..."
            ;;
        2)
            echo ""
            echo "Starting Tactical Mission Dispatcher..."
            cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_tactical_mission_dispatcher.py
            read -p "Press Enter to return to menu..."
            ;;
        3)
            echo ""
            echo "Starting Interactive Drone Tracker..."
            cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_interactive_map_tracker.py
            read -p "Press Enter to return to menu..."
            ;;
        4)
            echo ""
            echo "Starting Real Drone Flight Simulator..."
            cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_drone_sim.py
            read -p "Press Enter to return to menu..."
            ;;
        5)
            echo ""
            echo "Starting Real Aerial Flight Tracker..."
            cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_real_aerial_tracker.py
            read -p "Press Enter to return to menu..."
            ;;
        6)
            echo ""
            echo "Starting Live Webcam Feature Tracker..."
            cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_live_webcam.py
            read -p "Press Enter to return to menu..."
            ;;
        7)
            echo ""
            echo "Starting Visual Breadcrumbs RTH (Classic)..."
            cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_breadcrumb_rth.py
            read -p "Press Enter to return to menu..."
            ;;
        8)
            echo ""
            echo "Running Benchmark Suite..."
            cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_benchmarks.py
            read -p "Press Enter to return to menu..."
            ;;
        9)
            echo ""
            echo "Launching Streamlit Evaluation Dashboard on http://localhost:8502..."
            cd "$DIR/vision_localization_research" && "$STREAMLIT" run src/vision_loc/dashboard_app.py --server.port 8502
            ;;
        10)
            echo ""
            echo "Launching NavZero Ground Control Station on http://localhost:8501..."
            cd "$DIR/navzero" && "$STREAMLIT" run app.py
            ;;
        11)
            echo ""
            cd "$DIR/vision_localization_research" && "$PYTHON" scripts/switch_terrain_map.py
            read -p "Press Enter to return to menu..."
            ;;
        12)
            echo ""
            echo "Running Pytest Suite..."
            cd "$DIR/vision_localization_research" && "$PYTHON" -m pytest
            read -p "Press Enter to return to menu..."
            ;;
        13)
            echo ""
            echo "Generating PDFs..."
            cd "$DIR"
            "$PYTHON" generate_project_pdf.py
            "$PYTHON" generate_proposal_pdf.py
            "$PYTHON" generate_raunak_proposal.py
            read -p "Press Enter to return to menu..."
            ;;
        [qQ])
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please select from 1-13 or Q."
            sleep 1.5
            ;;
    esac
done
