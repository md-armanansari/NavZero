# NavZero: Autonomous Vision-Based GPS-Denied Drone Navigation
## macOS Quickstart & User Guide

This project has been fully configured and optimized to run natively on **macOS (Apple Silicon & Intel)**.

---

### 🚀 What Was Fixed & Changed for Mac:
1. **Created Native macOS Python Virtual Environment:**
   - The original `.venv` folder contained Windows-compiled binaries (`.exe` and `.pyd` files), which cannot run on macOS.
   - Recreated a clean macOS Apple Silicon virtual environment at `vision_localization_research/.venv` using Python 3.12 with all required libraries: `numpy`, `opencv-python` (with native macOS Cocoa GUI support), `streamlit`, `matplotlib`, `pandas`, `pytest`, and `reportlab`.
2. **Fixed Hardcoded Windows Paths:**
   - The PDF generation scripts (`generate_project_pdf.py`, `generate_proposal_pdf.py`, `generate_raunak_proposal.py`) had hardcoded Windows paths (`c:\Users\sharm\...`), causing `[Errno 30] Read-only file system` errors on Mac.
   - Updated them to use dynamic, cross-platform paths based on `Path(__file__).resolve().parent`.
3. **Created Native macOS Launchers (`.command` and `.sh`):**
   - Windows `.bat` files cannot be executed on Mac.
   - Created macOS `.command` launcher scripts (which can be **double-clicked directly from Mac Finder**) and `.sh` scripts (for Terminal execution) for every single demo and dashboard.
4. **Added Master Interactive Launcher:**
   - Created `run_mac.command` at the root folder so you can launch any feature from an interactive menu.

---

## 🎮 How to Run

### Method 1: Master Launcher (Recommended)
Simply **double-click** `run_mac.command` in Finder (or run in Terminal):
```bash
cd "/Users/arman_ansari/Downloads/defence 2"
./run_mac.command
```
This opens an interactive menu:
```
==========================================================================
     NAVZERO: AUTONOMOUS GPS-DENIED OPTICAL DRONE NAVIGATION
     Atmanirbhar Bharat Indigenous Defence Software (macOS Launcher)
==========================================================================

  WEB GROUND STATIONS & EVALUATION DASHBOARDS:
    [1] NavZero Tactical Ground Control Station (Streamlit Web App)
    [2] Research Evaluation Dashboard (Streamlit Web App)

  TACTICAL FLIGHT COCKPIT & TERRAIN SIMULATORS (OpenCV GUI):
    [3] Real Drone Autopilot & GPS-Jamming Cockpit Simulator
    [4] Interactive Ladakh Drone Dispatcher (Click to fly anywhere)
    [5] Tactical Mission Waypoint Navigator (Set Home Base & Target)
    [6] Zero-Map Breadcrumb Return-to-Home (V-RTH)
    [7] Real Aerial Flight 100% Photographic Terrain Tracker
    [8] Live Physical Webcam Visual Matching Engine

  TOOLS, BENCHMARKS & REPORTS:
    [9] Switch Active Terrain Map (Ladakh / CU Campus / Farmland / Ocean)
   [10] Run Benchmark Suite (7 trials + CSV + diagnostic plots)
   [11] Re-generate Defence Project & CU-TBI Incubation Proposal PDFs
   [12] Run All 34 Automated Unit & Integration Tests (pytest)

    [Q] Quit
==========================================================================
```

---

### Method 2: Individual Launchers (Double-Click in Finder)

You can double-click any of the following `.command` files in Finder:

| Feature / Demonstration | Finder Double-Click File | Terminal Command |
| :--- | :--- | :--- |
| **NavZero Ground Control Station** | `navzero/run_navzero.command` | `cd navzero && ./run_navzero.sh` |
| **Research Offline Dashboard** | `vision_localization_research/run_dashboard.command` | `cd vision_localization_research && ./run_dashboard.sh` |
| **Real Drone Autopilot Sim** | `vision_localization_research/run_real_drone_sim.command` | `cd vision_localization_research && ./run_real_drone_sim.sh` |
| **Interactive Ladakh Tracker** | `vision_localization_research/run_interactive_map.command` | `cd vision_localization_research && ./run_interactive_map.sh` |
| **Tactical Mission Dispatcher** | `vision_localization_research/run_tactical_mission.command` | `cd vision_localization_research && ./run_tactical_mission.sh` |
| **Zero-Map Breadcrumb RTH** | `vision_localization_research/run_breadcrumb_rth.command` | `cd vision_localization_research && ./run_breadcrumb_rth.sh` |
| **Real Aerial Photo Tracker** | `vision_localization_research/run_real_aerial_tracker.command` | `cd vision_localization_research && ./run_real_aerial_tracker.sh` |
| **Live Webcam ORB Matcher** | `vision_localization_research/run_live_webcam.command` | `cd vision_localization_research && ./run_live_webcam.sh` |
| **Switch Active Terrain Map** | `vision_localization_research/switch_map.command` | `cd vision_localization_research && ./switch_map.sh` |
| **Run Research Benchmarks** | `vision_localization_research/run_benchmarks.command` | `cd vision_localization_research && ./run_benchmarks.sh` |
| **Run All 34 Unit Tests** | `vision_localization_research/run_tests.command` | `cd vision_localization_research && ./run_tests.sh` |
| **Generate Formal PDFs** | `generate_pdfs.command` | `./generate_pdfs.sh` |

---

## ⌨️ Simulator Keyboard & Mouse Controls

- **Press `[J]`**: Toggle Electronic Warfare GPS Jamming ON / OFF.
- **Press `[R]`**: Trigger Autonomous Visual Return-to-Home (V-RTH).
- **Press `[Q]` or `[ESC]`**: Exit OpenCV simulation window.
- **In Interactive Map (`run_interactive_map`)**:
  - **Left-Click** anywhere on Ladakh terrain: Drone instantly flies there.
  - **Right-Click**: Set new Home Base runway.
- **In Tactical Mission (`run_tactical_mission`)**:
  - **Right-Click**: Set Home Base runway.
  - **Left-Click**: Set Target coordinates (drone takes off and flies autonomously).
- **In Live Webcam Demo (`run_live_webcam`)**:
  - Point camera at a book or phone image.
  - **Press `[S]`**: Snap frame as reference map.
  - Move book around to see real-time ORB green inlier tracking.

---

## 🧪 Automated Verification
All 34 unit and integration tests are verified passing:
```bash
cd vision_localization_research
.venv/bin/pytest -v
# 34 passed in 0.57s
```
