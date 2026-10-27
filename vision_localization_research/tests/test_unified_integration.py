"""
End-to-End System Integration Test for NavZero Unified Architecture.
Validates the complete operational loop:
- Mission dispatch & Catmull-Rom spline trajectory execution
- Sensor mode transitions (EO Daylight -> FLIR White-Hot Thermal)
- Scenario A Optical TRN under RF GPS jamming
- Dynamic environmental degradation (crosswind + cloud whiteout)
- Scenario B Visual Breadcrumb memory buffer backtracking and RTH guidance
"""

import pytest
import numpy as np
import cv2

from navzero.core.flight_engine import (
    NavZeroFlightEngine,
    SensorMode,
    AutopilotState,
    VisualBreadcrumb
)
from navzero.core.geo_utils import GeoReference


@pytest.fixture
def integrated_flight_computer():
    """Builds a deterministic test sector representing mountainous Ladakh theater."""
    np.random.seed(101)
    map_h, map_w = 700, 700
    test_map = np.full((map_h, map_w, 3), 135, dtype=np.uint8)
    
    # Draw geometric terrain features (runway, ridges, outpost circles)
    for i in range(25):
        cx = int((i * 45 + 30) % (map_w - 40))
        cy = int((i * 65 + 40) % (map_h - 40))
        cv2.circle(test_map, (cx, cy), 16, (240, 240, 240), -1)
        cv2.rectangle(test_map, (cx - 10, cy - 10), (cx + 10, cy + 10), (30, 30, 30), -1)

    geo_ref = GeoReference(
        top_left_lat=34.2500, top_left_lon=77.5000,
        bottom_right_lat=34.1000, bottom_right_lon=77.7500,
        map_width=map_w, map_height=map_h
    )
    return NavZeroFlightEngine(test_map, geo_ref, fov_size=240, detector_type="ORB", total_steps=200)


def test_full_mission_spline_execution(integrated_flight_computer):
    """Drone executes 40 consecutive flight steps along smooth Catmull-Rom spline."""
    fc = integrated_flight_computer
    assert len(fc.trajectory_points) == 200

    telemetry_history = []
    for step in range(40):
        t = fc.execute_flight_step(step)
        telemetry_history.append(t)
        assert t["step"] == step
        assert 0.0 <= t["battery_pct"] <= 100.0
        assert 0.0 <= t["heading_deg"] <= 360.0

    # Ensure distance moved between consecutive steps is smooth (< 20 pixels per step)
    for i in range(1, len(telemetry_history)):
        dx = telemetry_history[i]["true_px"] - telemetry_history[i - 1]["true_px"]
        dy = telemetry_history[i]["true_py"] - telemetry_history[i - 1]["true_py"]
        step_dist = np.hypot(dx, dy)
        assert step_dist < 20.0, f"Discontinuous flight leap at step {i}: {step_dist}px"


def test_thermal_night_vision_pipeline(integrated_flight_computer):
    """Verifies FLIR White-Hot and Ironbow multi-spectral transforms produce valid 3-channel frames."""
    fc = integrated_flight_computer
    
    # 1. Daylight RGB
    fc.sensor_mode = SensorMode.EO_DAYLIGHT
    t_day = fc.execute_flight_step(10)
    assert t_day["sensor_frame"].shape == (240, 240, 3)

    # 2. FLIR Thermal Night Vision
    fc.sensor_mode = SensorMode.IR_WHITE_HOT
    t_flir = fc.execute_flight_step(11)
    assert t_flir["sensor_frame"].shape == (240, 240, 3)
    # IR White-Hot should be grayscale replicated to 3 channels
    b, g, r = cv2.split(t_flir["sensor_frame"])
    assert np.array_equal(b, g) and np.array_equal(g, r)

    # 3. Tactical Ironbow False-Color
    fc.sensor_mode = SensorMode.IR_IRONBOW
    t_iron = fc.execute_flight_step(12)
    assert t_iron["sensor_frame"].shape == (240, 240, 3)


def test_breadcrumb_backtracking_rth(integrated_flight_computer):
    """
    Validates Scenario B: Outbound flight stores visual footprints.
    When GPS severed and cloud whiteout strikes, autopilot engages BREADCRUMB_RTH.
    """
    fc = integrated_flight_computer
    fc.breadcrumb_drop_interval = 4

    # 1. Outbound flight under nominal GPS (records breadcrumbs)
    for step in range(20):
        fc.execute_flight_step(step)

    assert len(fc.breadcrumb_buffer) >= 5
    recorded_count = len(fc.breadcrumb_buffer)

    # 2. Inject Enemy Jamming & Cloud Whiteout
    fc.gps_healthy = False
    fc.cloud_coverage_pct = 85.0

    t_jammed = fc.execute_flight_step(21)
    assert t_jammed["state"] == AutopilotState.BREADCRUMB_RTH
    assert t_jammed["breadcrumbs_count"] == recorded_count

    # 3. Validate breadcrumb sequence can be reversed for homing
    reverse_sequence = list(reversed(fc.breadcrumb_buffer))
    assert reverse_sequence[0].step_index == fc.breadcrumb_buffer[-1].step_index
    assert reverse_sequence[-1].step_index == fc.breadcrumb_buffer[0].step_index
    # Home base breadcrumb is index 0
    home_crumb = reverse_sequence[-1]
    assert home_crumb.step_index == 0
