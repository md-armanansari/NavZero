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

### 🧠 Autonomous Perception & MAVLink Bridge Architecture:
```text
┌─────────────────────────┐      ┌───────────────────────────────┐
│   Downward CMOS Camera  │      │ Pre-Loaded Georeferenced Map  │
│    (Live 30 FPS Feed)   │      │   (Satellite / Aerial Ortho)  │
└────────────┬────────────┘      └──────────────┬────────────────┘
             │                                  │
             ▼                                  ▼
      [ ORB Feature ]                    [ ORB Feature ]
      [  Extraction ]                    [  Extraction ]
             │                                  │
             └─────────────────┬────────────────┘
                               │
                               ▼
                [ Bitwise Hamming Matching & ]
                [   Lowe's 0.75 Ratio Test   ]
                               │
                               ▼
                [ Projective RANSAC Filter  ]
                [ (Rejects sensor noise/fog)]
                               │
                               ▼
                [ 6-Parameter GDAL Affine   ]
                [ Coordinate Transformation ]
                               │
                               ▼
                [ Lat/Lon Coordinate Stream ]
                [     (30 Hz Update Rate)   ]
                               │
                               ▼
              ┌────────────────────────────────────┐
              │ MAVLink VISION_POSITION_ESTIMATE   │
              │   (UART Serial to Drone Pixhawk)   │
              └────────────────────────────────────┘
```


---

## 📁 Repository Structure
```
NavZero/
├── run_windows.bat                  # Master interactive Windows launcher
├── launch_gcs_station.bat           # 1-Click launcher for Tactical GCS Web Station
├── launch_ladakh_dispatcher.bat     # 1-Click launcher for Multi-Waypoint Dispatcher
├── run_mac.command                  # Master interactive macOS launcher
├── requirements.txt                 # Unified project dependencies
├── navzero/                         # Tactical Ground Control Station (GCS)
│   ├── app.py                       # Streamlit Tactical GCS web dashboard
│   ├── run_navzero.bat              # Windows launcher
│   ├── run_navzero.sh               # Shell launcher
│   └── core/                        # Unified Autopilot & Perception Stack
│       ├── __init__.py              # Core package exports
│       ├── flight_engine.py         # Unified NavZeroFlightEngine & Autonomous Failsafe
│       ├── telemetry_bridge.py      # STANAG-4586 MAVLink UDP socket bridge (Port 14550)
│       ├── geo_utils.py             # Affine coordinate projection & WGS-84 conversion
│       ├── map_generator.py         # Synthetic terrain generator
│       ├── terrain_matcher.py       # SIFT/ORB feature matching engine
│       └── flight_simulator.py      # Catmull-Rom spline trajectory & EW jamming sim
└── vision_localization_research/    # Research suite & real-time simulators
    ├── docs/                        # Full technical specifications
    ├── data/                        # Satellite & aerial terrain maps
    ├── experiments/                 # Benchmark CSVs, plots & reports
    ├── scripts/                     # Interactive flight simulators & tools
    │   ├── run_drone_sim.py         # 30 FPS Aviation HUD cockpit simulator
    │   ├── run_interactive_map_tracker.py  # Click-to-fly terrain dispatcher
    │   ├── run_tactical_mission_dispatcher.py # Multi-waypoint mission planner & RTH
    │   ├── run_breadcrumb_rth.py    # Zero-map reverse visual navigation
    │   ├── run_clean_breadcrumb_rth.py # Clean teach-and-repeat reverse homing
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
    └── tests/                       # 49 automated unit & integration tests
```

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Tactical Ground Control Station (GCS)
Double-click `launch_gcs_station.bat` or run:
```bash
streamlit run navzero/app.py
```
* **Unified Flight Core:** Driven by `NavZeroFlightEngine` with 400-point continuous Catmull-Rom spline flight and STANAG-4586 telemetry.
* **Multi-Spectral Payloads:** Select between `☀️ EO Daylight`, `🌙 IR FLIR White-Hot` (thermal night vision), and `🔥 IR Ironbow`.
* **MAVLink Network Stream:** Live UDP broadcast on port `14550` (`VISION_POSITION_ESTIMATE`, `GLOBAL_POSITION_INT`).
* **Interactive EW Controls:** Toggle `🚨 INJECT ENEMY JAMMING` to simulate EW attacks with real-time audio alerts.
* **Environmental Stress:** Inject dynamic crosswinds (up to 20 m/s) and cloud obscuration / whiteout (up to 100%).
* **Scenario B Memory Buffer:** Visual breadcrumbs are stored in high-speed RAM; view live keyframe footprints in the collapsible gallery.
* **Mission Export:** Click `📥 EXPORT MISSION FLIGHT LOG` to download geodetic CSV telemetry for battlefield debriefing.

### 3. Launch Tactical Ladakh Multi-Waypoint Dispatcher
Double-click `launch_ladakh_dispatcher.bat` or run:
```bash
python vision_localization_research/scripts/run_tactical_mission_dispatcher.py
```
* **Right-Click**: Set Home Base runway location on the satellite map
* **Left-Click**: Add mission waypoints (`WP-1`, `WP-2`, `WP-3`...) — drone navigates sequentially
* **`[S]`**: Cycle Multi-Spectral Sensor Payloads (`☀️ EO Daylight` / `🌙 IR FLIR White-Hot` / `🔥 IR Ironbow`)
* **`[C]`**: Clear current flight plan
* **`[J]`**: Toggle Electronic Warfare GPS Jamming ON / OFF (demonstrates optical lock fallback)
* **`[R]`**: Trigger Autonomous Return-to-Home (drone retraces course back to runway)
* **`[Q]`**: Exit

*(Note: The 30 FPS aviation HUD cockpit is also available via `python vision_localization_research/scripts/run_drone_sim.py`)*

### 4. MAVLink / STANAG-4586 Telemetry Network Bridge (Port 14550)
The flight computer broadcasts real-time telemetry over UDP on localhost port `14550`:
- **`VISION_POSITION_ESTIMATE (#102)`**: Transmits local NED metric position and Euler orientation calculated via PnP homography.
- **`GLOBAL_POSITION_INT (#33)`**: Emits geodetic WGS-84 coordinates scaled to $1\times 10^{-7}$ degrees.
- **`NAVZERO_TACTICAL_STATUS (#188)`**: Emits inlier count, confidence %, sensor payload mode, and visual memory buffer depth.
Compatible out-of-the-box with **QGroundControl**, **MissionPlanner**, and **ArduPilot/PX4 SITL**.

---

## 🧪 Testing & Verification
Run the 49 automated unit and integration tests:
```bash
pytest vision_localization_research/tests -v
```

---

## 📜 Acknowledgments
Developed for indigenous UAV navigation research and incubation at Chandigarh University Technology Business Incubator (CU-TBI). Aligned with iDEX DISC and Make-in-India MoD problem statements.
