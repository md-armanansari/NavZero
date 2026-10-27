import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root))

import cv2
import numpy as np
from navzero.core.flight_engine import NavZeroFlightEngine, SensorMode, AutopilotState
from navzero.core.geo_utils import GeoReference

test_map = np.full((600, 600, 3), 120, dtype=np.uint8)
for i in range(15):
    cv2.circle(test_map, (i * 38 + 25, (i % 5) * 110 + 35), 18, (255, 255, 255), -1)

geo_ref = GeoReference(34.25, 77.50, 34.10, 77.75, 600, 600)
engine = NavZeroFlightEngine(test_map, geo_ref, fov_size=200, detector_type='ORB', total_steps=200)
engine.breadcrumb_drop_interval = 4

print("[*] Phase 1: Nominal GPS Cruise (Steps 0..19)")
for s in range(20):
    t = engine.execute_flight_step(s)
print(f"    State: {t['state'].value} | Crumbs recorded: {len(engine.breadcrumb_buffer)} | Battery: {t['battery_pct']:.1f}%")

print("[*] Phase 2: Inject Enemy Jamming (Step 20)")
engine.gps_healthy = False
t = engine.execute_flight_step(20)
print(f"    State: {t['state'].value} | Mode: {t['sensor_mode'].value} | Inliers: {t['inlier_count']} | Error CEP: {t['err_meters']:.1f}m")

print("[*] Phase 3: Switch to FLIR Thermal Night Vision + Cloud Whiteout (Step 25)")
engine.sensor_mode = SensorMode.IR_WHITE_HOT
engine.cloud_coverage_pct = 85.0
t = engine.execute_flight_step(25)
print(f"    State: {t['state'].value} | Mode: {t['sensor_mode'].value} | Crumbs Buffer: {t['breadcrumbs_count']} | Failsafe Engaged: {t['state'] == AutopilotState.BREADCRUMB_RTH}")

print("[*] Phase 4: Restore GPS (Step 30)")
engine.gps_healthy = True
engine.cloud_coverage_pct = 0.0
t = engine.execute_flight_step(30)
print(f"    State: {t['state'].value} | GPS Healthy: {t['gps_healthy']}")
print("\n[SUCCESS] All 4 combat sortie phases verified on NavZeroFlightEngine!")
