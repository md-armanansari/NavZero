"""
Live Real-Drone Autopilot Bridge & Cockpit Visualizer.
Directly interfaced with NavZeroFlightEngine:
- Continuous Catmull-Rom spline trajectory execution
- Multi-spectral nadir camera pipeline (EO Daylight / FLIR White-Hot Thermal / Ironbow)
- Scenario A Optical Terrain-Referenced Navigation (ORB + RANSAC)
- Scenario B Visual Breadcrumbs buffer memory
- Military Aviation HUD with artificial horizon, compass tape, and airspeed/alt tapes
"""

import math
import sys
import time
from pathlib import Path
import cv2
import numpy as np

# Ensure root and src are in python path
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "vision_localization_research" / "src"))

from navzero.core.flight_engine import (
    NavZeroFlightEngine,
    SensorMode,
    AutopilotState
)
from navzero.core.geo_utils import GeoReference


def generate_recon_map(w=1600, h=1200):
    """Generates a textured high-contrast aerial map representing high-altitude terrain."""
    np.random.seed(42)
    base = np.zeros((h, w, 3), dtype=np.uint8)
    base[:] = (130, 145, 155)  # Rocky gray-brown

    # Add procedural mountain ridges and river valleys
    noise = np.random.randint(-25, 25, (h, w, 3), dtype=np.int16)
    base = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Draw river valley
    pts = np.array([[100, 200], [500, 450], [900, 600], [1400, 1000]], np.int32)
    cv2.polylines(base, [pts], False, (180, 130, 90), 22, cv2.LINE_AA)

    # Tactical runway / Forward Landing Ground
    cv2.rectangle(base, (650, 480), (1050, 560), (55, 55, 55), -1)
    cv2.line(base, (670, 520), (1030, 520), (220, 220, 220), 4)

    # Road network
    cv2.line(base, (200, 1000), (850, 520), (90, 90, 90), 8)
    cv2.line(base, (850, 520), (1500, 200), (90, 90, 90), 8)

    # Military outpost structures
    for (ox, oy) in [(720, 440), (760, 440), (810, 430), (980, 590), (1020, 600)]:
        cv2.rectangle(base, (ox, oy), (ox + 30, oy + 25), (40, 75, 45), -1)

    return base


def run_drone_mission_sim():
    print("=" * 74)
    print("  AUTONOMOUS REAL-DRONE FLIGHT & TELEMETRY SIMULATOR (UNIFIED)")
    print("  Testing GPS Jamming, Multi-Spectral FLIR & Visual Breadcrumbs")
    print("=" * 74)
    print("\nCONTROLS:")
    print(" [J] = TOGGLE GNSS JAMMING ON / OFF")
    print(" [R] = ENGAGE AUTONOMOUS RETURN-TO-HOME (SCENARIO B RTH)")
    print(" [S] = CYCLE MULTI-SPECTRAL SENSOR (EO / IR WHITE-HOT / IRONBOW)")
    print(" [P] = TOGGLE ORBIT PATROL LOITER MODE")
    print(" [+/-] = ADJUST AIRSPEED (5 to 35 m/s)")
    print(" [Q] or [ESC] = QUIT\n")

    # Load high-altitude terrain raster
    data_dir = repo_root / "vision_localization_research" / "data"
    map_path = data_dir / "ladakh_zanskar_map.jpg"
    if map_path.exists():
        sat_map = cv2.imread(str(map_path))
    else:
        sat_map = generate_recon_map()

    map_h, map_w = sat_map.shape[:2]

    # Georeference initialization
    geo_ref = GeoReference(
        top_left_lat=34.2500, top_left_lon=77.5000,
        bottom_right_lat=34.1000, bottom_right_lon=77.7500,
        map_width=map_w, map_height=map_h
    )

    # Initialize Unified Flight Engine
    engine = NavZeroFlightEngine(sat_map, geo_ref, fov_size=280, detector_type="ORB", total_steps=400)
    engine.breadcrumb_drop_interval = 8

    window_name = "NavZero Tactical Aviation Cockpit // STANAG-4586"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    step = 0
    patrol_mode = False
    orbit_angle = 0.0

    while True:
        # Step engine simulation
        telemetry = engine.execute_flight_step(step)
        step = (step + 1) % len(engine.trajectory_points)

        sensor_frame = telemetry["sensor_frame"]
        state = telemetry["state"]
        jammed = not telemetry["gps_healthy"]
        inliers = telemetry["inlier_count"]
        hdg = telemetry["heading_deg"]

        # Handle Patrol Orbit
        if patrol_mode:
            orbit_angle = (orbit_angle + 5.0) % 360.0
            hdg = orbit_angle

        # ----------------- COCKPIT RENDER -----------------
        # Left side: Downward Drone Camera with Military Aviation HUD
        cam_disp = cv2.resize(sensor_frame, (500, 500))
        ch, cw = cam_disp.shape[:2]
        cx, cy = cw // 2, ch // 2

        hud_color = (0, 0, 255) if jammed else (0, 255, 120)
        if state == AutopilotState.BREADCRUMB_RTH:
            hud_color = (0, 165, 255)  # Orange for RTH

        # 1. Artificial Horizon Pitch Waterline (Aircraft Reticle)
        cv2.line(cam_disp, (cx - 50, cy), (cx - 15, cy), hud_color, 2)
        cv2.line(cam_disp, (cx + 15, cy), (cx + 50, cy), hud_color, 2)
        cv2.circle(cam_disp, (cx, cy), 5, hud_color, 1)
        # Pitch ticks (+10 deg, -10 deg)
        cv2.line(cam_disp, (cx - 25, cy - 25), (cx + 25, cy - 25), hud_color, 1)
        cv2.putText(cam_disp, "+10", (cx + 30, cy - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.35, hud_color, 1)
        cv2.line(cam_disp, (cx - 25, cy + 25), (cx + 25, cy + 25), hud_color, 1)
        cv2.putText(cam_disp, "-10", (cx + 30, cy + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.35, hud_color, 1)

        # 2. Compass Heading Tape (Top of camera)
        hdg_val = int(hdg) % 360
        cv2.rectangle(cam_disp, (cx - 65, 8), (cx + 65, 30), (20, 25, 20), -1)
        cv2.rectangle(cam_disp, (cx - 65, 8), (cx + 65, 30), hud_color, 1)
        hdg_str = f"HDG: {hdg_val:03d} DEG"
        cv2.putText(cam_disp, hdg_str, (cx - 55, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, hud_color, 1)

        # 3. Altitude & Airspeed Tapes
        cv2.putText(cam_disp, f"IAS: {telemetry['airspeed_kmh']:.0f}KMH", (12, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.42, hud_color, 1)
        cv2.putText(cam_disp, f"ALT: {telemetry['altitude_agl_m']:.0f}M", (cw - 85, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.42, hud_color, 1)

        # 4. Payload indicator
        cv2.putText(cam_disp, f"SENSOR: {telemetry['sensor_mode'].value}", (12, ch - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.42, hud_color, 1)
        cv2.putText(cam_disp, f"CRUMBS: {telemetry['breadcrumbs_count']}", (cw - 110, ch - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.42, hud_color, 1)

        # Right side: Satellite Map with Drone Position, Spline & Breadcrumbs
        map_disp = cv2.resize(sat_map, (660, 500))
        scale_x = 660 / map_w
        scale_y = 500 / map_h

        # Draw trajectory spline
        pts = np.array(engine.trajectory_points[:step + 1], dtype=np.float32)
        if len(pts) > 1:
            scaled_pts = np.column_stack([pts[:, 0] * scale_x, pts[:, 1] * scale_y]).astype(np.int32)
            cv2.polylines(map_disp, [scaled_pts], isClosed=False, color=(180, 210, 150), thickness=2)

        # Draw Scenario B breadcrumb memory footprints
        for crumb in engine.breadcrumb_buffer:
            bx, by = int(crumb.true_px * scale_x), int(crumb.true_py * scale_y)
            cv2.circle(map_disp, (bx, by), 3, (0, 220, 255), -1)

        # Draw current drone position on map
        d_cx = int(telemetry["true_px"] * scale_x)
        d_cy = int(telemetry["true_py"] * scale_y)
        marker_col = (0, 0, 255) if jammed else (0, 255, 0)
        if state == AutopilotState.BREADCRUMB_RTH:
            marker_col = (0, 165, 255)

        cv2.circle(map_disp, (d_cx, d_cy), 8, marker_col, -1)
        cv2.circle(map_disp, (d_cx, d_cy), 18, marker_col, 2)
        cv2.putText(map_disp, f"UAV-01 [{state.value}]", (d_cx + 12, d_cy - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, marker_col, 1)

        # Combine side-by-side
        cockpit = np.hstack([cam_disp, map_disp])

        # Top Telemetry Bar
        top_bar = np.zeros((65, cockpit.shape[1], 3), dtype=np.uint8)
        gps_color = (0, 0, 255) if jammed else (0, 255, 0)
        gps_txt = "GNSS: JAMMED [0 SATS]" if jammed else "GNSS: ACTIVE [14 SATS 3D FIX]"
        mode_txt = "AUTO-RETURN (SCENARIO B RTH)" if state == AutopilotState.BREADCRUMB_RTH else (
            "ORBIT PATROL" if patrol_mode else state.value
        )

        cv2.putText(top_bar, f"MISSION: {mode_txt}", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(top_bar, gps_txt, (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.52, gps_color, 2)

        cv2.putText(top_bar, f"ALT: {telemetry['altitude_agl_m']:.0f}m | SPD: {telemetry['airspeed_kmh']:.0f} km/h | HDG: {hdg_val:03d}", (495, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1)
        cv2.putText(top_bar, f"OPTICAL INLIERS: {inliers} ({telemetry['confidence_pct']:.1f}%) | BATT: {telemetry['battery_pct']:.1f}% | CEP: {telemetry['err_meters']:.1f}m", (495, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 0) if inliers >= 10 else (0, 165, 255), 2)

        final_ui = np.vstack([top_bar, cockpit])

        # Bottom Instructions Footer
        footer = np.zeros((30, cockpit.shape[1], 3), dtype=np.uint8)
        cv2.putText(footer, "[J] Jam GNSS | [R] Scenario B RTH | [S] Cycle EO/IR | [P] Orbit Patrol | [+/-] Airspeed | [Q] Exit", (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1)
        final_ui = np.vstack([final_ui, footer])

        cv2.imshow(window_name, final_ui)
        key = cv2.waitKey(35) & 0xFF

        if key == ord('q') or key == ord('Q') or key == 27:
            break
        elif key == ord('j') or key == ord('J'):
            engine.gps_healthy = not engine.gps_healthy
            print(f"[EVENT] GNSS Jamming toggled. Healthy: {engine.gps_healthy}")
        elif key == ord('r') or key == ord('R'):
            engine.gps_healthy = False
            engine.cloud_coverage_pct = 90.0  # Force optical failsafe to RTH
            print("[EVENT] Emergency Return-to-Home engaged via Visual Breadcrumbs buffer!")
        elif key == ord('s') or key == ord('S'):
            # Cycle through EO/IR sensor modes
            modes = [SensorMode.EO_DAYLIGHT, SensorMode.IR_WHITE_HOT, SensorMode.IR_IRONBOW]
            curr_idx = modes.index(engine.sensor_mode)
            engine.sensor_mode = modes[(curr_idx + 1) % len(modes)]
            print(f"[EVENT] Sensor payload switched to: {engine.sensor_mode.value}")
        elif key == ord('p') or key == ord('P'):
            patrol_mode = not patrol_mode
            print(f"[EVENT] Orbit Patrol mode switched to: {patrol_mode}")
        elif key == ord('+') or key == ord('='):
            engine.speed_mps = min(35.0, engine.speed_mps + 2.0)
        elif key == ord('-') or key == ord('_'):
            engine.speed_mps = max(5.0, engine.speed_mps - 2.0)

    cv2.destroyAllWindows()
    print("[INFO] Flight simulator closed.")


if __name__ == "__main__":
    run_drone_mission_sim()
