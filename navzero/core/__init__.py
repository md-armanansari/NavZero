"""
NavZero Core Navigation and Autonomous Flight Engine.
"""

from navzero.core.flight_engine import (
    NavZeroFlightEngine,
    SensorMode,
    AutopilotState,
    VisualBreadcrumb
)
from navzero.core.geo_utils import GeoReference
from navzero.core.telemetry_bridge import (
    MAVLinkTelemetryBridge,
    NavZeroTacticalPacket,
    VisionPositionEstimate,
    GlobalPositionInt,
    MAVLinkHeartbeat
)

from navzero.core.scenarios import (
    CombatScenario,
    ThreatCategory,
    DEFENSE_SCENARIOS,
    get_combat_scenarios,
    get_scenario_by_id,
    apply_scenario_to_engine
)

__all__ = [
    "NavZeroFlightEngine",
    "SensorMode",
    "AutopilotState",
    "VisualBreadcrumb",
    "GeoReference",
    "MAVLinkTelemetryBridge",
    "NavZeroTacticalPacket",
    "VisionPositionEstimate",
    "GlobalPositionInt",
    "MAVLinkHeartbeat",
    "CombatScenario",
    "ThreatCategory",
    "DEFENSE_SCENARIOS",
    "get_combat_scenarios",
    "get_scenario_by_id",
    "apply_scenario_to_engine"
]

