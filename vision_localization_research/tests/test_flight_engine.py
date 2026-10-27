"""
Automated Unit Tests for the Unified NavZeroFlightEngine.
Validates multi-spectral sensors, Catmull-Rom kinematics, Scenario A terrain matching,
Scenario B visual breadcrumb memory buffer, and autonomous failsafe transitions.
"""

import pytest
import numpy as np
import cv2

from navzero.core.geo_utils import GeoReference
from navzero.core.flight_engine import NavZeroFlightEngine, SensorMode, AutopilotState

@pytest.fixture
def synthetic_engine():
    # Create deterministic synthetic high-contrast map for fast testing
    np.random.seed(42)
    test_map = np.full((600, 600, 3), 120, dtype=np.uint8)
    # Draw geometric features for ORB matching
    for i in range(15):
        cv2.circle(test_map, (i * 38 + 25, (i % 5) * 110 + 35), 18, (255, 255, 255), -1)
        cv2.rectangle(test_map, (i * 35 + 10, (i % 4) * 140 + 20), (i * 35 + 30, (i % 4) * 140 + 50), (20, 20, 20), -1)

    geo_ref = GeoReference(34.25, 77.50, 34.10, 77.75, 600, 600)
    return NavZeroFlightEngine(test_map, geo_ref, fov_size=200, detector_type="ORB", total_steps=400)

def test_engine_initialization(synthetic_engine):
    """Verify trajectory generation and reference feature indexing."""
    assert len(synthetic_engine.trajectory_points) == 400
    assert synthetic_engine.map_kp is not None
    assert len(synthetic_engine.map_kp) > 0
    assert synthetic_engine.state == AutopilotState.GPS_NOMINAL

def test_multispectral_sensor_modes(synthetic_engine):
    """Verify EO Daylight, IR Thermal White-Hot, and Ironbow capture pipelines."""
    # 1. EO Daylight
    synthetic_engine.sensor_mode = SensorMode.EO_DAYLIGHT
    frame_eo = synthetic_engine.capture_sensor_frame(300, 300)
    assert frame_eo.shape == (200, 200, 3)

    # 2. IR White-Hot Thermal
    synthetic_engine.sensor_mode = SensorMode.IR_WHITE_HOT
    frame_ir = synthetic_engine.capture_sensor_frame(300, 300)
    assert frame_ir.shape == (200, 200, 3)

    # 3. IR Ironbow False-Color
    synthetic_engine.sensor_mode = SensorMode.IR_IRONBOW
    frame_iron = synthetic_engine.capture_sensor_frame(300, 300)
    assert frame_iron.shape == (200, 200, 3)

def test_flight_step_and_breadcrumb_dropping(synthetic_engine):
    """Verify flight execution and Scenario B breadcrumb accumulation."""
    synthetic_engine.breadcrumb_drop_interval = 5

    for step in range(25):
        telemetry = synthetic_engine.execute_flight_step(step)
        assert "true_lat" in telemetry
        assert "nav_lat" in telemetry
        assert "heading_deg" in telemetry
        assert 0.0 <= telemetry["heading_deg"] <= 360.0
        assert 0.0 <= telemetry["battery_pct"] <= 100.0

    # Ensure breadcrumbs were dropped in buffer
    assert len(synthetic_engine.breadcrumb_buffer) >= 4
    first_crumb = synthetic_engine.breadcrumb_buffer[0]
    assert first_crumb.step_index == 0
    assert first_crumb.frame_crop.shape == (200, 200, 3)

def test_failsafe_state_machine_handover(synthetic_engine):
    """Verify autonomous failover chain from GPS -> Optical TRN -> Breadcrumb RTH."""
    synthetic_engine.breadcrumb_drop_interval = 2
    # Pre-seed flight path with breadcrumbs so RTH memory is primed
    for s in range(6):
        synthetic_engine.execute_flight_step(s)

    # 1. Nominal GPS
    t1 = synthetic_engine.execute_flight_step(10)
    assert t1["state"] == AutopilotState.GPS_NOMINAL

    # 2. Jamming Strikes -> Optical TRN
    synthetic_engine.gps_healthy = False
    t2 = synthetic_engine.execute_flight_step(11)
    # State should transfer to OPTICAL_TRN
    assert t2["state"] in (AutopilotState.OPTICAL_TRN, AutopilotState.ORBIT_SEARCH)

    # 3. Cloud cover / Whiteout -> Breadcrumb RTH
    synthetic_engine.cloud_coverage_pct = 90.0
    t3 = synthetic_engine.execute_flight_step(12)
    assert t3["state"] == AutopilotState.BREADCRUMB_RTH

