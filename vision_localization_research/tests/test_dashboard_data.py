"""
Unit Tests for Dashboard Data Ingestion and Filtering Module.
"""
from pathlib import Path
import pytest

from vision_loc.dashboard_data import (
    DashboardRecord,
    filter_records,
    load_benchmark_records,
)


def test_load_actual_benchmark_csv():
    """Verify loading the actual generated benchmark_results.csv from Milestone 5."""
    csv_file = Path(__file__).resolve().parent.parent / "experiments" / "benchmark_results.csv"
    assert csv_file.is_file(), "experiments/benchmark_results.csv must exist from Milestone 5"

    records = load_benchmark_records(csv_file)
    assert len(records) == 7

    # Verify first baseline record
    base = records[0]
    assert base.pair_id == "pair_01_baseline"
    assert base.category == "Baseline"
    assert base.status == "SUCCESS"
    assert base.geometric_inliers == 101
    assert base.pixel_reprojection_rmse is not None
    assert base.geometric_verification_success is True

    # Verify hard negative record preserves N/A error values
    blank = records[6]
    assert blank.pair_id == "pair_07_blank_frame"
    assert blank.status == "INSUFFICIENT_FEATURES"
    assert blank.geometric_inliers == 0
    assert blank.pixel_reprojection_rmse is None
    assert blank.synthetic_grid_error_m is None
    assert blank.geometric_verification_success is False


def test_missing_csv_file_raises_filenotfound(tmp_path: Path):
    """Verify that a non-existent CSV path raises FileNotFoundError."""
    missing = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError, match="not found"):
        load_benchmark_records(missing)


def test_empty_csv_file_raises_valueerror(tmp_path: Path):
    """Verify that a 0-byte CSV raises ValueError."""
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    with pytest.raises(ValueError, match="empty"):
        load_benchmark_records(empty)


def test_malformed_csv_missing_columns_raises_valueerror(tmp_path: Path):
    """Verify that a CSV missing required schema headers raises ValueError."""
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("pair_id,category,status\np1,Cat,SUCCESS\n")
    with pytest.raises(ValueError, match="missing required schema columns"):
        load_benchmark_records(bad_csv)


def test_filter_records_by_category_and_status():
    """Test filtering records while preserving failed trials."""
    records = [
        DashboardRecord("p1", "Illumination", "desc", "SUCCESS", 100, 100, 50, 30, 20, 0.66, 5, 50.0, 2.0, 25, 1.2, 0.6, True),
        DashboardRecord("p2", "Illumination", "desc", "SUCCESS", 100, 100, 40, 25, 15, 0.60, 5, 55.0, 2.5, 25, 1.8, 0.9, True),
        DashboardRecord("p3", "Hard Negative", "desc", "NO_CORRESPONDENCE", 10, 100, 5, 0, 0, 0.0, 5, 45.0, 1.0, 0, None, None, False),
    ]

    # Filter by category
    illum = filter_records(records, selected_categories=["Illumination"])
    assert len(illum) == 2
    assert all(r.category == "Illumination" for r in illum)

    # Filter by status (preserving failure)
    failed = filter_records(records, selected_statuses=["NO_CORRESPONDENCE"])
    assert len(failed) == 1
    assert failed[0].pair_id == "p3"
    assert failed[0].pixel_reprojection_rmse is None
