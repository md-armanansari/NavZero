"""
Data ingestion and filtering module for the Research Results Dashboard.
Decoupled from Streamlit UI to permit independent unit testing and robust error handling.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv
import math


REQUIRED_CSV_COLUMNS = [
    "pair_id", "category", "description", "status",
    "keypoints_query", "keypoints_ref", "tentative_matches",
    "ratio_matches", "geometric_inliers", "inlier_ratio",
    "timing_repetitions", "steady_state_latency_median_ms", "steady_state_latency_std_ms",
    "independent_checkpoints_tested", "pixel_reprojection_rmse",
    "synthetic_grid_error_m", "geometric_verification_success",
]


@dataclass(frozen=True)
class DashboardRecord:
    """Validated row representation of benchmark trial results."""
    pair_id: str
    category: str
    description: str
    status: str
    keypoints_query: int
    keypoints_ref: int
    tentative_matches: int
    ratio_matches: int
    geometric_inliers: int
    inlier_ratio: float
    timing_repetitions: int
    steady_state_latency_median_ms: float
    steady_state_latency_std_ms: float
    independent_checkpoints_tested: int
    pixel_reprojection_rmse: Optional[float]
    synthetic_grid_error_m: Optional[float]
    geometric_verification_success: bool


def _parse_optional_float(val: Any) -> Optional[float]:
    if val is None or str(val).strip() == "" or str(val).strip().upper() == "N/A":
        return None
    try:
        f = float(val)
        return None if math.isnan(f) else f
    except (ValueError, TypeError):
        return None


def _parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in ("true", "1", "yes")


def load_benchmark_records(csv_path: Path) -> List[DashboardRecord]:
    """
    Loads benchmark trials from CSV, validating column presence and formatting.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If file is empty or missing required schema columns.
    """
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Benchmark results CSV not found: {csv_path}")

    records: List[DashboardRecord] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"CSV file is empty: {csv_path}")

        # Check required columns
        missing_cols = [c for c in REQUIRED_CSV_COLUMNS if c not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"CSV missing required schema columns: {missing_cols}")

        for row in reader:
            record = DashboardRecord(
                pair_id=str(row.get("pair_id", "")),
                category=str(row.get("category", "")),
                description=str(row.get("description", "")),
                status=str(row.get("status", "")),
                keypoints_query=int(row.get("keypoints_query", 0)),
                keypoints_ref=int(row.get("keypoints_ref", 0)),
                tentative_matches=int(row.get("tentative_matches", 0)),
                ratio_matches=int(row.get("ratio_matches", 0)),
                geometric_inliers=int(row.get("geometric_inliers", 0)),
                inlier_ratio=float(row.get("inlier_ratio", 0.0)),
                timing_repetitions=int(row.get("timing_repetitions", 1)),
                steady_state_latency_median_ms=float(row.get("steady_state_latency_median_ms", 0.0)),
                steady_state_latency_std_ms=float(row.get("steady_state_latency_std_ms", 0.0)),
                independent_checkpoints_tested=int(row.get("independent_checkpoints_tested", 0)),
                pixel_reprojection_rmse=_parse_optional_float(row.get("pixel_reprojection_rmse")),
                synthetic_grid_error_m=_parse_optional_float(row.get("synthetic_grid_error_m")),
                geometric_verification_success=_parse_bool(row.get("geometric_verification_success")),
            )
            records.append(record)

    return records


def filter_records(
    records: List[DashboardRecord],
    selected_categories: Optional[List[str]] = None,
    selected_statuses: Optional[List[str]] = None,
) -> List[DashboardRecord]:
    """
    Filters records by category and status while preserving unsuccessful cases.
    """
    filtered = records
    if selected_categories:
        cat_set = set(selected_categories)
        filtered = [r for r in filtered if r.category in cat_set]
    if selected_statuses:
        status_set = set(selected_statuses)
        filtered = [r for r in filtered if r.status in status_set]
    return filtered
