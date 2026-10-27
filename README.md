# NavZero: Autonomous Vision-Based GPS-Denied Drone Navigation

**Indigenous Atmanirbhar Defence Software**  
*Targeted for Indian Armed Forces (Army, Air Force, Navy) UAVs operating in Electronic Warfare (EW) hostile and GPS-jammed environments.*

---

## 🎯 The Military Problem
Hostile Electronic Warfare units along border sectors (such as Ladakh / LAC and Western border / LoC) routinely jam and spoof satellite signals (GPS, GLONASS, NavIC). When drones lose GPS:
- Autopilots drift or trigger failsafe crashes.
- Loitering munitions (kamikaze drones) miss critical targets.
- Surveillance missions abort prematurely.
- Traditional Ring Laser Gyro inertial systems cost upwards of ₹40–60 Lakhs per drone, making mass attritable drone deployment impossible.

---

## 💡 The NavZero Solution
**NavZero** turns standard optical/thermal reconnaissance cameras into a **jam-proof optical guidance system** using pure edge computer vision:
1. **Zero Hardware Dependency:** Uses existing onboard optical cameras and low-cost edge processors (Raspberry Pi / Jetson / standard CPU).
2. **Optical Terrain Matching:** Matches live camera frames against pre-cached satellite ortho-tiles and Digital Elevation Models (DEM) using high-speed ORB/SIFT feature matching and RANSAC Homography.
3. **Drift-Free Geo-Referencing:** Calculates sub-meter coordinates completely independent of satellite signals.
4. **Autonomous Zero-Map Return-To-Home (V-RTH):** Retraces optical breadcrumbs when operating over unmapped hostile territory.

---

## 📁 Repository Structure
```
NavZero/
├── HOW_TO_RUN_ON_MAC.md             # Complete macOS setup and user guide
├── run_mac.command                  # Master interactive macOS double-click launcher
├── run_mac.sh                       # Master macOS terminal launcher
├── requirements.txt                 # Unified project dependencies
├── generate_project_pdf.py          # Complete defense project explanation PDF generator
├── generate_proposal_pdf.py         # CU-TBI incubation proposal PDF generator
├── generate_raunak_proposal.py      # Personalized founder proposal PDF generator
├── generate_pdfs.command            # Double-click script to generate all PDFs on Mac
├── navzero/                         # Tactical Ground Control Station (GCS)
│   ├── app.py                       # Streamlit Tactical GCS web dashboard
│   ├── run_navzero.command          # macOS one-click launcher
│   ├── run_navzero.sh               # Linux/macOS launcher
│   ├── run_navzero.bat              # Windows launcher
│   └── core/                        # Core simulator and matching modules
│       ├── geo_utils.py             # Affine coordinate projection
│       ├── map_generator.py         # Synthetic terrain generator
│       ├── terrain_matcher.py       # SIFT/ORB feature matching engine
│       └── flight_simulator.py      # Flight kinematics & EW jamming sim
└── vision_localization_research/    # Research suite & real-time simulators
    ├── docs/
    │   └── RESEARCH_REPORT.md       # Comprehensive research specification
    ├── data/                        # High-resolution satellite & aerial maps
    ├── experiments/                 # Benchmark CSVs, diagnostic plots & reports
    ├── scripts/                     # Interactive OpenCV simulators & benchmarks
    │   ├── run_drone_sim.py         # Autopilot cockpit telemetry loop
    │   ├── run_interactive_map_tracker.py  # Click-to-fly Ladakh dispatcher
    │   ├── run_tactical_mission_dispatcher.py # Waypoint & home base mission planner
    │   ├── run_breadcrumb_rth.py    # Zero-map reverse visual navigation
    │   ├── run_real_aerial_tracker.py # 100% photographic orthophoto tracker
    │   ├── run_live_webcam.py       # Real-time laptop webcam feature tracker
    │   ├── run_benchmarks.py        # Automated benchmark runner
    │   └── switch_terrain_map.py    # Terrain switcher (Ladakh / CU Campus / Farmland / Ocean)
    ├── src/vision_loc/              # Pure Python research library
    │   ├── feature_matcher.py       # ORB + Hamming + RANSAC pipeline
    │   ├── georeference.py          # 6-parameter GDAL affine transformations
    │   ├── evaluation.py            # Latency, RMSE, and repeatability testing
    │   ├── image_inspector.py       # Format inspection & memory-safe plotting
    │   └── dashboard_app.py         # Streamlit research evaluation dashboard
    └── tests/                       # 34 automated unit & integration tests
```

---

## 🚀 Quickstart

### On macOS
Double-click `run_mac.command` in Finder or run in Terminal:
```bash
./run_mac.command
```
Or launch any individual module directly (e.g. `navzero/run_navzero.command` or `vision_localization_research/run_dashboard.command`).

### On Windows
Run any of the batch files:
- `navzero/run_navzero.bat`: Launches the Tactical GCS Dashboard.
- `vision_localization_research/run_dashboard.bat`: Launches the Research Evaluation Dashboard.
- `vision_localization_research/run_real_drone_sim.bat`: Launches the drone cockpit simulator.

---

## 🧪 Testing & Verification
Run the 34 unit & integration tests:
```bash
cd vision_localization_research
pytest -v
```

---

## 📜 License & Acknowledgments
Developed for indigenous UAV navigation research and incubation at Chandigarh University Technology Business Incubator (CU-TBI). Aligned with iDEX DISC and Make-in-India MoD problem statements.
