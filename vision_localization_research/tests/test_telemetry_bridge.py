"""
Automated Unit Tests for NavZero MAVLink & Tactical Telemetry Bridge.
Validates binary packet serialization, UDP transport loopback, subscriber dispatch,
and corruption resilience.
"""

import sys
import time
from pathlib import Path
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root))

import pytest
from navzero.core.telemetry_bridge import (
    MAVLinkTelemetryBridge,
    NavZeroTacticalPacket,
    VisionPositionEstimate,
    GlobalPositionInt,
    MAVLinkHeartbeat,
    MAVAutopilot,
    MAVState
)


def test_packet_serialization_roundtrip():
    """Verifies NavZeroTacticalPacket serializes to binary and reconstructs identically."""
    pkt = NavZeroTacticalPacket(
        step=42,
        state="OPTICAL_TRN",
        sensor_mode="IR_WHITE_HOT",
        gps_healthy=False,
        true_lat=34.2185,
        true_lon=77.5842,
        est_lat=34.2184,
        est_lon=77.5843,
        err_meters=1.65,
        heading_deg=135.0,
        airspeed_kmh=68.5,
        altitude_agl_m=120.0,
        battery_pct=88.4,
        inlier_count=345,
        confidence_pct=98.2,
        breadcrumbs_count=12
    )

    data = pkt.serialize()
    assert isinstance(data, bytes)
    assert len(data) > 8
    # Check 4-byte magic NVZ0
    assert data[:4] == b"NVZ0"

    recovered = NavZeroTacticalPacket.deserialize(data)
    assert recovered is not None
    assert recovered.step == 42
    assert recovered.state == "OPTICAL_TRN"
    assert recovered.sensor_mode == "IR_WHITE_HOT"
    assert recovered.gps_healthy is False
    assert pytest.approx(recovered.true_lat, 0.0001) == 34.2185
    assert pytest.approx(recovered.true_lon, 0.0001) == 77.5842
    assert recovered.inlier_count == 345
    assert recovered.breadcrumbs_count == 12


def test_corrupt_packet_handling():
    """Verifies corrupted or truncated packets fail gracefully without exceptions."""
    # 1. Truncated data (< 8 bytes)
    assert NavZeroTacticalPacket.deserialize(b"NVZ") is None

    # 2. Invalid magic header
    bad_header = b"XXXX" + (100).to_bytes(4, "big") + b"dummy"
    assert NavZeroTacticalPacket.deserialize(bad_header) is None

    # 3. Truncated payload
    good_magic = b"NVZ0" + (100).to_bytes(4, "big") + b"short_data"
    assert NavZeroTacticalPacket.deserialize(good_magic) is None


def test_udp_socket_broadcast_and_subscription():
    """Verifies end-to-end UDP network socket dispatch between flight engine and GCS."""
    server = MAVLinkTelemetryBridge(host="127.0.0.1", port=0, is_server=True)
    assigned_port = server.port
    server.start_listener()

    received_packets = []

    def on_telemetry(pkt: NavZeroTacticalPacket):
        received_packets.append(pkt)

    server.subscribe(on_telemetry)

    test_pkt = NavZeroTacticalPacket(
        step=99,
        state="BREADCRUMB_RTH",
        sensor_mode="IR_IRONBOW",
        inlier_count=412,
        breadcrumbs_count=24
    )

    # Broadcast packet to server port
    server.broadcast_telemetry(test_pkt, target_port=assigned_port)

    # Wait briefly for UDP packet delivery
    deadline = time.time() + 1.5
    while len(received_packets) == 0 and time.time() < deadline:
        time.sleep(0.05)

    server.stop()

    assert len(received_packets) >= 1
    rx = received_packets[0]
    assert rx.step == 99
    assert rx.state == "BREADCRUMB_RTH"
    assert rx.sensor_mode == "IR_IRONBOW"
    assert rx.inlier_count == 412
    assert rx.breadcrumbs_count == 24


def test_mavlink_standard_structures():
    """Verifies STANAG-4586 / MAVLink standard data structures."""
    heartbeat = MAVLinkHeartbeat()
    assert heartbeat.autopilot == MAVAutopilot.NAVZERO_INDIGENOUS
    assert heartbeat.system_status == MAVState.ACTIVE

    vision_pnp = VisionPositionEstimate(
        usec=int(time.time() * 1e6),
        x_m=12.5,
        y_m=-8.2,
        z_m=-120.0,
        yaw_rad=0.785
    )
    assert vision_pnp.z_m == -120.0
    assert vision_pnp.covariance_diag == (0.05, 0.05, 0.1)

    gps_int = GlobalPositionInt(
        time_boot_ms=15000,
        lat_deg7=341500000,
        lon_deg7=776000000,
        alt_mm=3500000,
        relative_alt_mm=120000,
        vx_cms=1800,
        vy_cms=0,
        vz_cms=0,
        hdg_cdeg=4500
    )
    assert gps_int.lat_deg7 == 341500000
    assert gps_int.relative_alt_mm == 120000
