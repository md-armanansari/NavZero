"""
Test suite for NavZero defense combat mission presets and threat profiles.
"""

import numpy as np
import pytest
from navzero.core.flight_engine import NavZeroFlightEngine, SensorMode, AutopilotState
from navzero.core.geo_utils import GeoReference
from navzero.core.scenarios import (
    CombatScenario,
    ThreatCategory,
    DEFENSE_SCENARIOS,
    get_combat_scenarios,
    get_scenario_by_id,
    apply_scenario_to_engine
)


@pytest.fixture
def test_engine():
    synthetic_map = np.zeros((500, 500, 3), dtype=np.uint8)
    geo_ref = GeoReference(34.25, 77.50, 34.10, 77.75, 500, 500)
    return NavZeroFlightEngine(synthetic_map, geo_ref, fov_size=150, total_steps=200)


def test_scenario_registry_completeness():
    scenarios = get_combat_scenarios()
    assert len(scenarios) >= 3
    assert "ALPHA_FORWARD_INGRESS" in scenarios
    assert "BRAVO_RIVER_VALLEY_NIGHT" in scenarios
    assert "CHARLIE_DEEP_JAMMING_WHITEOUT" in scenarios


def test_scenario_properties():
    alpha = get_scenario_by_id("ALPHA_FORWARD_INGRESS")
    assert alpha is not None
    assert alpha.threat_category == ThreatCategory.GNSS_SPOOFING_JAMMING
    assert alpha.sensor_mode == SensorMode.EO_DAYLIGHT
    assert alpha.gps_healthy is False
    assert alpha.target_altitude_m == 120.0
    assert alpha.airspeed_mps == 22.0

    bravo = get_scenario_by_id("BRAVO_RIVER_VALLEY_NIGHT")
    assert bravo is not None
    assert bravo.threat_category == ThreatCategory.THERMAL_NIGHT_INFILTRATION
    assert bravo.sensor_mode == SensorMode.IR_WHITE_HOT
    assert bravo.target_altitude_m == 75.0

    charlie = get_scenario_by_id("CHARLIE_DEEP_JAMMING_WHITEOUT")
    assert charlie is not None
    assert charlie.threat_category == ThreatCategory.SEVERE_EW_WHITEOUT
    assert charlie.cloud_coverage_pct > 80.0


def test_apply_scenario_to_engine(test_engine):
    charlie = get_scenario_by_id("CHARLIE_DEEP_JAMMING_WHITEOUT")
    apply_scenario_to_engine(test_engine, charlie)

    assert test_engine.sensor_mode == SensorMode.IR_IRONBOW
    assert test_engine.gps_healthy is False
    assert test_engine.cloud_coverage_pct == 85.0
    assert test_engine.crosswind_mps == 12.0
    assert test_engine.altitude_agl_m == 95.0
    assert test_engine.airspeed_mps == 18.0
    assert test_engine.current_step == 160
    assert test_engine.state == AutopilotState.BREADCRUMB_RTH


def test_invalid_scenario_id():
    assert get_scenario_by_id("NON_EXISTENT_SCENARIO") is None
