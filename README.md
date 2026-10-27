# NavZero: Autonomous Optical Navigation for Defense UAVs

**Indigenous Software for GPS-Denied and Electronic Warfare Hostile Environments**

---

## 🎯 Problem Statement
In modern border conflicts (e.g. along the LAC and LoC), adversary forces use powerful **GPS and radio frequency jammers** to disrupt military drone operations.

When a standard drone enters a jammed area:
- Satellite signals (GPS, NavIC, GLONASS) and remote-control links are completely blocked.
- The drone loses its coordinates, gets trapped, and drifts off-course or crashes into enemy territory.
- Dedicated hardware inertial sensors (like Ring Laser Gyros) cost upwards of ₹40–50 Lakhs per drone, making them unfeasible for mass-produced tactical or attritable UAVs.

---

## 💡 Proposed Solution
**NavZero** is an edge-compute computer vision software that enables defense drones to complete their missions and return home safely **without relying on GPS or external communication**.

### How It Works:
1. **Clicks Photos in Flight:** As the drone flies toward its mission target, the software captures ground imagery every second using the downward reconnaissance camera (like dropping visual breadcrumbs).
2. **Feature Extraction:** Computer vision algorithms (ORB/SIFT) extract distinctive visual landmarks (road junctions, ridges, river bends, runway markings).
3. **Autonomous Safe Return (Even if Connection is Lost):** The moment GPS or remote connectivity is jammed, the drone turns around, matches live camera frames in reverse against the photos taken on the way in, and navigates straight back to base camp on its own.
4. **Pre-Loaded Map Matching (Scenario A):** When pre-cached satellite maps are available, the software continuously estimates sub-meter coordinates by matching live camera pixels against the map.

```text
1. MISSION FLIGHT:   Drone captures photos every second:   [Photo 1] ──▶ [Photo 2] ──▶ [Photo 3] ──▶ [TARGET]
                                                                                                 │
2. ENEMY GPS JAMMED: Remote link & satellite signals cut! ❌                                       │ (Signal Lost!)
                                                                                                 ▼
3. SAFE RETURN HOME: Drone matches ground photos in reverse: [BASE] ◀── [Photo 1] ◀── [Photo 2] ◀── [Photo 3]
```

---

## 📁 Repository Structure
```
NavZero/
├── run_windows.bat                  # Master interactive Windows launcher
├── run_mac.command                  # Master interactive macOS launcher
├── requirements.txt                 # Unified project dependencies
├── navzero/                         # Tactical Ground Control Station (GCS)
│   ├── app.py                       # Streamlit Tactical GCS web dashboard
│   ├── run_navzero.bat              # Windows launcher
│   ├── run_navzero.sh               # Shell launcher
│   └── core/                        # Simulator & visual matching modules
│       ├── geo_utils.py             # Affine coordinate projection
│       ├── map_generator.py         # Synthetic terrain generator
│       ├── terrain_matcher.py       # SIFT/ORB feature matching engine
│       └── flight_simulator.py      # Flight kinematics & EW jamming sim
└── vision_localization_research/    # Research suite & real-time simulators
    ├── docs/                        # Full technical specifications
    ├── data/                        # Satellite & aerial terrain maps
    ├── experiments/                 # Benchmark CSVs, plots & reports
    ├── scripts/                     # Interactive flight simulators & tools
    │   ├── run_drone_sim.py         # Real drone cockpit telemetry simulator
    │   ├── run_interactive_map_tracker.py  # Click-to-fly terrain dispatcher
    │   ├── run_tactical_mission_dispatcher.py # Waypoint & home base mission planner
    │   ├── run_breadcrumb_rth.py    # Zero-map reverse visual navigation
    │   ├── run_real_aerial_tracker.py # 100% photographic orthophoto tracker
    │   ├── run_live_webcam.py       # Laptop webcam physical feature tracker
    │   ├── run_benchmarks.py        # Automated benchmark runner
    │   └── switch_terrain_map.py    # Terrain switcher (Ladakh / Campus / Farmland / Ocean)
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

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Tactical Ground Control Station
```bash
streamlit run navzero/app.py
```
Open `http://localhost:8501` to view the live optical feed, tactical map, and test GPS jamming fallback.

### 3. Launch Drone Cockpit Simulator
```bash
python vision_localization_research/scripts/run_drone_sim.py
```
* **`[J]`**: Toggle Electronic Warfare GPS Jamming ON / OFF
* **`[R]`**: Engage Autonomous Visual Return-to-Home (V-RTH)
* **`[Q]`**: Exit

---

## 🧪 Testing & Verification
Run the 34 automated unit and integration tests:
```bash
pytest vision_localization_research/tests -v
```

---

## 📜 Acknowledgments
Developed for indigenous UAV navigation research and incubation at Chandigarh University Technology Business Incubator (CU-TBI). Aligned with iDEX DISC and Make-in-India MoD problem statements.
