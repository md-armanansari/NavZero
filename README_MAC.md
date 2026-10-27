# NavZero / Vision Localization — Mac Quickstart Guide

This project is now fully configured and validated for **macOS (Apple Silicon & Intel)**.

---

## 🚀 How to Run on Mac

You have two simple ways to run any part of the project on macOS:

### Option 1: Double-Click in macOS Finder (`.command` files)
Just double-click any `.command` file directly in Finder (it opens macOS Terminal automatically):
- **`run_menu.command`** *(Recommended)*: An interactive control suite offering a menu of all 13 demos, benchmarks, dashboards, and tests with 1 click.
- **`run_clean_breadcrumb.command`**: Scenario B Clean Teach-and-Repeat Return-to-Home.
- **`run_navzero.command`**: NavZero Tactical Ground Control Station (Streamlit UI on port 8501).
- **`run_dashboard.command`**: Vision-Loc Offline Evaluation Dashboard (Streamlit UI on port 8502).

In the `vision_localization_research` folder, each `.bat` file now has an equivalent `.command` and `.sh` file:
- `run_tactical_mission.command`
- `run_interactive_map.command`
- `run_real_drone_sim.command`
- `run_real_aerial_tracker.command`
- `run_live_webcam.command`
- `run_breadcrumb_rth.command`
- `run_benchmarks.command`
- `switch_map.command`

---

### Option 2: Run in Terminal (`.sh` files)
From your Terminal:
```bash
cd "/Users/arman_ansari/Downloads/defence 3"

# Interactive Master Menu:
./run_menu.sh

# Or directly run any specific demo:
./run_clean_breadcrumb.sh
./run_navzero.sh
./run_dashboard.sh
```

---

## 🛠️ What Was Fixed for macOS

1. **Native macOS Virtual Environment**:
   - Replaced Windows-only `.venv` (which contained Windows `.exe` and `.pyd` binaries) with a native macOS Python 3.12 virtual environment in `vision_localization_research/.venv`.
   - Installed all required packages: `opencv-python`, `numpy`, `matplotlib`, `pytest`, `streamlit`, `pandas`, `pillow`, `reportlab`, and `pymavlink`.
   - A backup of the Windows environment is preserved in `.venv_windows_backup` to ensure cross-platform safety.

2. **Cross-Platform Launchers (`.command` and `.sh`)**:
   - Created native macOS double-clickable `.command` launchers and `.sh` shell scripts corresponding to all existing `.bat` files.
   - Scripts automatically locate the virtual environment (`.venv/bin/python` and `.venv/bin/streamlit`) without needing manual environment activation.

3. **Hardcoded Windows Paths**:
   - Replaced hardcoded `c:\Users\sharm\...` paths in `generate_project_pdf.py`, `generate_proposal_pdf.py`, and `generate_raunak_proposal.py` with dynamic, cross-platform path resolution (`Path(__file__).resolve().parent`).

4. **Webcam Handling on macOS**:
   - Added automatic fallback between camera indices (`0` and `1`) in `run_clean_breadcrumb_rth.py`, `run_breadcrumb_rth.py`, and `run_live_webcam.py`.
   - Added clear diagnostic hints if macOS Camera permissions need to be enabled in *System Settings → Privacy & Security → Camera*.

5. **Validation & Testing**:
   - Executed full test suite: **34 / 34 unit tests passing**.
   - Verified automated research benchmark pipeline (`run_benchmarks.py`).
   - Verified Streamlit servers for both NavZero and the research dashboard.
   - Verified PDF generation scripts.
