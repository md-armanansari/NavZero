"""
End-to-End MAVLink & Autopilot Network Integration Test.
Validates live UDP broadcasting from NavZeroFlightEngine to GCS listener clients.
"""

import sys
import time
from pathlib import Path
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root))

import pytest
import numpy as np
import cv2

from navzero.core.flight_engine import (
    NavZeroFlightEngine,
    SensorMode,
    AutopilotState
)
from navzero.core.geo_utils import GeoReference
from navzero.core.telemetry_bridge import (
    MAVLinkTelemetryBridge,
    NavZeroTacticalPacket,
    VisionPositionEstimate
)


def test_mavlink_live_flight_telemetry_broadcast():
    """Validates real-time packet streaming during active flight execution."""
    # 1. Create flight map and engine
    test_map = np.full((400, 400, 3), 130, dtype=np.uint8)
    for i in range(8):
        cv2.circle(test_map, (i * 45 + 30, (i % 3) * 110 + 40), 18, (250, 250, 250), -1)

    geo_ref = GeoReference(34.25, 77.50, 34.10, 77.75, 400, 400)
    
    # 2. Bind Telemetry Bridge
    bridge = MAVLinkTelemetryBridge(host="127.0.0.1", port=0, is_server=True)
    engine = NavZeroFlightEngine(
        test_map, geo_ref, fov_size=180, total_steps=80,
        telemetry_bridge=bridge
    )

    received_packets = []
    bridge.subscribe(lambda pkt: received_packets.append(pkt))

    # 3. Execute nominal cruise flight steps
    for step in range(5):
        engine.execute_flight_step(step)

    assert len(received_packets) >= 5
    first_pkt = received_packets[0]
    last_pkt = received_packets[-1]
    assert first_pkt.step == 0
    assert last_pkt.step == 4
    assert last_pkt.state == "GPS_NOMINAL"
    assert last_pkt.sensor_mode == "EO_DAYLIGHT"
    assert last_pkt.gps_healthy is True

    # 4. Inject EW Jamming and verify broadcast stream reflects failover
    engine.gps_healthy = False
    engine.execute_flight_step(5)
    jammed_pkt = received_packets[-1]
    assert jammed_pkt.step == 5
    assert jammed_pkt.gps_healthy is False
    assert jammed_pkt.state in ("OPTICAL_TRN", "ORBIT_SEARCH")

    # 5. Switch to FLIR thermal night vision and verify broadcast stream
    engine.sensor_mode = SensorMode.IR_WHITE_HOT
    engine.execute_flight_step(6)
    flir_pkt = received_packets[-1]
    assert flir_pkt.step == 6
    assert flir_pkt.sensor_mode == "IR_WHITE_HOT"

    # 6. Test MAVLink #102 VISION_POSITION_ESTIMATE export
    vision_msg = engine.to_mavlink_vision_estimate(local_x_m=24.5, local_y_m=-18.2)
    assert isinstance(vision_msg, VisionPositionEstimate)
    assert vision_msg.x_m == 24.5
    assert vision_msg.y_m == -18.2
    assert vision_msg.z_m == -engine.alt_m

    bridge.stop()
