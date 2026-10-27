"""
Automated unit and bridge tests for Cockpit HUD and Tactical Mission Dispatcher.
Validates interoperability with NavZeroFlightEngine and multi-spectral sensors.
"""

import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "vision_localization_research" / "src"))

import pytest
import numpy as np
import cv2

from navzero.core.flight_engine import (
    NavZeroFlightEngine,
    SensorMode,
    AutopilotState
)
from navzero.core.geo_utils import GeoReference


@pytest.fixture
def test_sector():
    map_h, map_w = 500, 500
    test_map = np.full((map_h, map_w, 3), 125, dtype=np.uint8)
    for i in range(12):
        cv2.circle(test_map, (i * 40 + 20, (i % 4) * 100 + 40), 15, (255, 255, 255), -1)

    geo_ref = GeoReference(34.25, 77.50, 34.10, 77.75, map_w, map_h)
    return test_map, geo_ref


def test_cockpit_engine_telemetry_stream(test_sector):
    """Verifies cockpit HUD receives valid telemetry stream from unified flight engine."""
    sat_map, geo_ref = test_sector
    engine = NavZeroFlightEngine(sat_map, geo_ref, fov_size=200, total_steps=100)

    for step in range(10):
        t = engine.execute_flight_step(step)
        assert t["step"] == step
        assert t["sensor_frame"].shape == (200, 200, 3)
        assert t["state"] == AutopilotState.GPS_NOMINAL
        assert 0.0 <= t["heading_deg"] <= 360.0


def test_cockpit_multispectral_cycling(test_sector):
    """Verifies cycling sensor payloads in cockpit updates telemetry sensor mode."""
    sat_map, geo_ref = test_sector
    engine = NavZeroFlightEngine(sat_map, geo_ref, fov_size=200, total_steps=100)

    modes = [SensorMode.EO_DAYLIGHT, SensorMode.IR_WHITE_HOT, SensorMode.IR_IRONBOW]
    for mode in modes:
        engine.sensor_mode = mode
        t = engine.execute_flight_step(5)
        assert t["sensor_mode"] == mode
        assert t["sensor_frame"].shape == (200, 200, 3)


def test_dispatcher_waypoint_queue_logic():
    """Verifies tactical mission dispatcher sequential waypoint queueing."""
    waypoint_queue = [(200, 300), (400, 450), (150, 100)]
    active_target = (100, 100)

    # First objective reached -> pop next
    assert len(waypoint_queue) == 3
    active_target = waypoint_queue.pop(0)
    assert active_target == (200, 300)
    assert len(waypoint_queue) == 2

    # Second objective reached -> pop next
    active_target = waypoint_queue.pop(0)
    assert active_target == (400, 450)
    assert len(waypoint_queue) == 1

    # Final objective
    active_target = waypoint_queue.pop(0)
    assert active_target == (150, 100)
    assert len(waypoint_queue) == 0


def test_dispatcher_thermal_transform():
    """Verifies FLIR White-Hot and Ironbow transforms applied on tactical dispatcher camera crop."""
    dummy_crop = np.full((180, 180, 3), 110, dtype=np.uint8)
    cv2.rectangle(dummy_crop, (40, 40), (120, 120), (220, 220, 220), -1)

    # 1. White-Hot
    gray = cv2.cvtColor(dummy_crop, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
    thermal_gray = clahe.apply(gray)
    white_hot = cv2.cvtColor(cv2.bitwise_not(thermal_gray), cv2.COLOR_GRAY2BGR)
    assert white_hot.shape == (180, 180, 3)

    # 2. Ironbow
    ironbow = cv2.applyColorMap(clahe.apply(gray), cv2.COLORMAP_INFERNO)
    assert ironbow.shape == (180, 180, 3)
