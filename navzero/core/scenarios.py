"""
NavZero Tactical Defense Combat Scenarios.

Defines realistic military UAV operational profiles, threat environments, 
and sensor/EW stress conditions for defense evaluation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from navzero.core.flight_engine import NavZeroFlightEngine, SensorMode, AutopilotState


class ThreatCategory(str, Enum):
    NOMINAL_SURVEILLANCE = "NOMINAL_SURVEILLANCE"
    GNSS_SPOOFING_JAMMING = "GNSS_SPOOFING_JAMMING"
    THERMAL_NIGHT_INFILTRATION = "THERMAL_NIGHT_INFILTRATION"
    SEVERE_EW_WHITEOUT = "SEVERE_EW_WHITEOUT"


@dataclass
class CombatScenario:
    scenario_id: str
    code_name: str
    theater_name: str
    threat_category: ThreatCategory
    threat_level: str
    tactical_briefing: str
    sector_map_name: str
    sensor_mode: SensorMode
    initial_step: int
    gps_healthy: bool
    cloud_coverage_pct: float
    crosswind_mps: float
    target_altitude_m: float
    airspeed_mps: float
    expected_initial_state: AutopilotState
    success_criteria: str


DEFENSE_SCENARIOS: Dict[str, CombatScenario] = {
    "ALPHA_FORWARD_INGRESS": CombatScenario(
        scenario_id="ALPHA_FORWARD_INGRESS",
        code_name="Operation Desert Falcon (Forward Ingress)",
        theater_name="Ladakh Zanskar Sector (LAC Border)",
        threat_category=ThreatCategory.GNSS_SPOOFING_JAMMING,
        threat_level="DEFCON 2 // ACTIVE ELECTRONIC WARFARE",
        tactical_briefing=(
            "High-speed daylight reconnaissance across disputed mountainous terrain. "
            "Hostile EW barrage severs L1/L2 GNSS carrier lock at ingress boundary. "
            "UAV must seamlessly transition to Scenario A (Optical Terrain Relocalization) "
            "and bound position drift to under 2.0 meters CEP."
        ),
        sector_map_name="Ladakh Zanskar Sector (LAC Border)",
        sensor_mode=SensorMode.EO_DAYLIGHT,
        initial_step=40,
        gps_healthy=False,
        cloud_coverage_pct=0.0,
        crosswind_mps=4.0,
        target_altitude_m=120.0,
        airspeed_mps=22.0,
        expected_initial_state=AutopilotState.OPTICAL_TRN,
        success_criteria="Position error < 2.0m, Inlier count > 20, 0 accumulated drift."
    ),
    "BRAVO_RIVER_VALLEY_NIGHT": CombatScenario(
        scenario_id="BRAVO_RIVER_VALLEY_NIGHT",
        code_name="Operation Shadow Talon (River Valley Infiltration)",
        theater_name="High-Altitude Forward Reconnaissance",
        threat_category=ThreatCategory.THERMAL_NIGHT_INFILTRATION,
        threat_level="DEFCON 2 // ZERO LUX NIGHT ENVELOPE",
        tactical_briefing=(
            "Low-altitude night penetration along winding river valley corridor under complete optical darkness. "
            "Standard RGB camera blinded by zero lux ambient lighting. "
            "Autonomous payload engages Long-Wave Infrared (FLIR White-Hot) radiometry, "
            "correlating surface thermal gradients against georeferenced satellite elevation templates."
        ),
        sector_map_name="High-Altitude Forward Reconnaissance",
        sensor_mode=SensorMode.IR_WHITE_HOT,
        initial_step=90,
        gps_healthy=False,
        cloud_coverage_pct=15.0,
        crosswind_mps=7.0,
        target_altitude_m=75.0,
        airspeed_mps=16.0,
        expected_initial_state=AutopilotState.OPTICAL_TRN,
        success_criteria="Thermal lock maintained > 18 inliers, altitude hold 75m, stable heading."
    ),
    "CHARLIE_DEEP_JAMMING_WHITEOUT": CombatScenario(
        scenario_id="CHARLIE_DEEP_JAMMING_WHITEOUT",
        code_name="Operation Ghost Aegis (Deep Jamming & Cloud Whiteout)",
        theater_name="Punjab Western Sector (Farmland)",
        threat_category=ThreatCategory.SEVERE_EW_WHITEOUT,
        threat_level="DEFCON 1 // EXTREME DOUBLE-DENIAL",
        tactical_briefing=(
            "Severe multi-domain denial: hostiles deploy high-power GNSS chirp jammers while dense meteorological "
            "cloud bank / smokescreen obscures ground surface (cloud whiteout > 80%). "
            "With GNSS severed and optical terrain map matching blinded (< 12 inliers), "
            "the system activates Scenario B: Autonomous Visual Breadcrumb Backtracking RTH, "
            "reversing recorded onboard memory keyframes to reach safety."
        ),
        sector_map_name="Punjab Western Sector (Farmland)",
        sensor_mode=SensorMode.IR_IRONBOW,
        initial_step=160,
        gps_healthy=False,
        cloud_coverage_pct=85.0,
        crosswind_mps=12.0,
        target_altitude_m=95.0,
        airspeed_mps=18.0,
        expected_initial_state=AutopilotState.BREADCRUMB_RTH,
        success_criteria="Automatic activation of Scenario B, reverse breadcrumb lock, safe touchdown."
    )
}


def get_combat_scenarios() -> Dict[str, CombatScenario]:
    """Return dictionary of all registered defense combat scenarios."""
    return DEFENSE_SCENARIOS


def get_scenario_by_id(scenario_id: str) -> Optional[CombatScenario]:
    """Retrieve combat scenario configuration by ID."""
    return DEFENSE_SCENARIOS.get(scenario_id)


def apply_scenario_to_engine(engine: NavZeroFlightEngine, scenario: CombatScenario) -> None:
    """
    Apply scenario operational parameters directly to a NavZeroFlightEngine instance.
    """
    engine.sensor_mode = scenario.sensor_mode
    engine.gps_healthy = scenario.gps_healthy
    engine.cloud_coverage_pct = scenario.cloud_coverage_pct
    engine.crosswind_mps = scenario.crosswind_mps
    engine.altitude_agl_m = scenario.target_altitude_m
    engine.airspeed_mps = scenario.airspeed_mps
    
    # Place at scenario initial step
    total = len(engine.trajectory_points)
    if total > 0:
        engine.current_step = scenario.initial_step % total
        engine.state = scenario.expected_initial_state
