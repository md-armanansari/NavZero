#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PYTHON="$DIR/vision_localization_research/.venv/bin/python"
STREAMLIT="$DIR/vision_localization_research/.venv/bin/streamlit"
PYTEST="$DIR/vision_localization_research/.venv/bin/pytest"

if [ ! -f "$PYTHON" ]; then
    PYTHON="python3"
fi
if [ ! -f "$STREAMLIT" ]; then
    STREAMLIT="streamlit"
fi
if [ ! -f "$PYTEST" ]; then
    PYTEST="pytest"
fi

while true; do
    clear
    echo "=========================================================================="
    echo "     NAVZERO: AUTONOMOUS GPS-DENIED OPTICAL DRONE NAVIGATION"
    echo "     Atmanirbhar Bharat Indigenous Defence Software (macOS Launcher)"
    echo "=========================================================================="
    echo ""
    echo "  WEB GROUND STATIONS & EVALUATION DASHBOARDS:"
    echo "    [1] NavZero Tactical Ground Control Station (Streamlit Web App)"
    echo "    [2] Research Evaluation Dashboard (Streamlit Web App)"
    echo ""
    echo "  TACTICAL FLIGHT COCKPIT & TERRAIN SIMULATORS (OpenCV GUI):"
    echo "    [3] Real Drone Autopilot & GPS-Jamming Cockpit Simulator"
    echo "    [4] Interactive Ladakh Drone Dispatcher (Click to fly anywhere)"
    echo "    [5] Tactical Mission Waypoint Navigator (Set Home Base & Target)"
    echo "    [6] Zero-Map Breadcrumb Return-to-Home (V-RTH)"
    echo "    [7] Real Aerial Flight 100% Photographic Terrain Tracker"
    echo "    [8] Live Physical Webcam Visual Matching Engine"
    echo ""
    echo "  TOOLS, BENCHMARKS & REPORTS:"
    echo "    [9] Switch Active Terrain Map (Ladakh / CU Campus / Farmland / Ocean)"
    echo "   [10] Run Benchmark Suite (7 trials + CSV + diagnostic plots)"
    echo "   [11] Re-generate Defence Project & CU-TBI Incubation Proposal PDFs"
    echo "   [12] Run All 34 Automated Unit & Integration Tests (pytest)"
    echo ""
    echo "    [Q] Quit"
    echo "=========================================================================="
    read -p "Select option [1-12 or Q]: " choice

    case "$choice" in
        1)
            echo ""
            echo ">>> Launching NavZero Tactical Ground Control Station on http://localhost:8501 ..."
            (cd "$DIR/navzero" && "$STREAMLIT" run app.py)
            ;;
        2)
            echo ""
            echo ">>> Launching Research Evaluation Dashboard on http://localhost:8502 ..."
            (cd "$DIR/vision_localization_research" && "$STREAMLIT" run src/vision_loc/dashboard_app.py --server.port 8502)
            ;;
        3)
            echo ""
            (cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_drone_sim.py)
            ;;
        4)
            echo ""
            (cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_interactive_map_tracker.py)
            ;;
        5)
            echo ""
            (cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_tactical_mission_dispatcher.py)
            ;;
        6)
            echo ""
            (cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_breadcrumb_rth.py)
            ;;
        7)
            echo ""
            (cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_real_aerial_tracker.py)
            ;;
        8)
            echo ""
            (cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_live_webcam.py)
            ;;
        9)
            echo ""
            (cd "$DIR/vision_localization_research" && "$PYTHON" scripts/switch_terrain_map.py)
            ;;
        10)
            echo ""
            (cd "$DIR/vision_localization_research" && "$PYTHON" scripts/run_benchmarks.py)
            ;;
        11)
            echo ""
            "$PYTHON" "$DIR/generate_project_pdf.py"
            "$PYTHON" "$DIR/generate_proposal_pdf.py"
            "$PYTHON" "$DIR/generate_raunak_proposal.py"
            ;;
        12)
            echo ""
            (cd "$DIR/vision_localization_research" && "$PYTEST" -v)
            ;;
        q|Q)
            echo "Exiting NavZero Launcher. Jai Hind!"
            exit 0
            ;;
        *)
            echo "Invalid selection. Please choose 1-12 or Q."
            ;;
    esac
    echo ""
    read -p "Press Enter to return to menu..."
done
