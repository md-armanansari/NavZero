"""
Unit Tests for Research Evaluation and Benchmarking Module.
"""
from pathlib import Path
import csv
import pytest
import numpy as np

from vision_loc.evaluation import (
    BenchmarkSummary,
    TrialResult,
    compute_summary_statistics,
    create_base_synthetic_landscape,
    evaluate_trial,
    export_results_to_csv,
    generate_benchmark_pairs,
)
from vision_loc.feature_matcher import VisualFeatureMatcher
from vision_loc.georeference import AffineTransform


def test_synthetic_landscape_is_deterministic():
    """Verify that landscape generation produces identical pixel values with the same seed."""
    img1 = create_base_synthetic_landscape(width=400, height=400, seed=123)
    img2 = create_base_synthetic_landscape(width=400, height=400, seed=123)
    img_diff = create_base_synthetic_landscape(width=400, height=400, seed=456)

    assert np.array_equal(img1, img2)
    assert not np.array_equal(img1, img_diff)


def test_benchmark_pairs_generation():
    """Verify that test pairs include expected categories and valid shapes."""
    georef = AffineTransform(500000.0, 4000000.0, 1.0, 0.0, 0.0, -1.0)
    base_img = create_base_synthetic_landscape(width=600, height=600, seed=42)

    pairs = generate_benchmark_pairs(base_img, georef, crop_size=200)

    assert len(pairs) >= 5
    categories = {p["category"] for p in pairs}
    assert "Baseline" in categories
    assert "Illumination" in categories
    assert "Geometric" in categories
    assert "Hard Negative" in categories


def test_evaluate_trial_baseline_and_hard_negative():
    """Test evaluation on both a normal matching pair and a hard negative blank pair."""
    georef = AffineTransform(500000.0, 4000000.0, 0.5, 0.0, 0.0, -0.5)
    base_img = create_base_synthetic_landscape(width=600, height=600, seed=42)
    pairs = generate_benchmark_pairs(base_img, georef, crop_size=200)

    matcher = VisualFeatureMatcher(max_features=800)

    # 1. Baseline trial
    baseline_pair = next(p for p in pairs if p["pair_id"] == "pair_01_baseline")
    res_base = evaluate_trial(matcher, baseline_pair, georef)

    assert res_base.status == "SUCCESS"
    assert res_base.geometric_inliers >= 4
    assert res_base.localization_success is True
    assert res_base.position_error_m is not None
    # On identical baseline translation crop, error should be near-zero
    assert res_base.position_error_m < 2.0

    # 2. Hard negative blank trial
    blank_pair = next(p for p in pairs if p["pair_id"] == "pair_07_blank_frame")
    res_blank = evaluate_trial(matcher, blank_pair, georef)

    assert res_blank.status == "INSUFFICIENT_FEATURES"
    assert res_blank.geometric_inliers == 0
    assert res_blank.localization_success is False
    assert res_blank.position_error_m is None


def test_compute_summary_statistics():
    """Test calculation of summary statistics (medians, percentiles, rates)."""
    trials = [
        TrialResult(
            pair_id="t1", category="Cat", description="d", status="SUCCESS",
            keypoints_query=100, keypoints_ref=100, tentative_matches=50, ratio_matches=30,
            geometric_inliers=25, inlier_ratio=0.83, total_time_ms=50.0,
            true_center_x_m=0.0, true_center_y_m=0.0, est_center_x_m=0.1, est_center_y_m=0.2,
            position_error_m=0.22, localization_success=True,
        ),
        TrialResult(
            pair_id="t2", category="Cat", description="d", status="SUCCESS",
            keypoints_query=100, keypoints_ref=100, tentative_matches=40, ratio_matches=25,
            geometric_inliers=20, inlier_ratio=0.80, total_time_ms=70.0,
            true_center_x_m=0.0, true_center_y_m=0.0, est_center_x_m=0.3, est_center_y_m=0.4,
            position_error_m=0.50, localization_success=True,
        ),
        TrialResult(
            pair_id="t3", category="Cat", description="d", status="NO_CORRESPONDENCE",
            keypoints_query=10, keypoints_ref=100, tentative_matches=5, ratio_matches=2,
            geometric_inliers=0, inlier_ratio=0.0, total_time_ms=30.0,
            true_center_x_m=None, true_center_y_m=None, est_center_x_m=None, est_center_y_m=None,
            position_error_m=None, localization_success=False,
        ),
    ]

    summary = compute_summary_statistics(trials)

    assert summary.total_trials == 3
    assert summary.successful_matches == 2
    assert summary.failed_matches == 1
    assert summary.match_success_rate == pytest.approx(2 / 3, abs=1e-3)
    assert summary.successful_localizations == 2
    assert summary.median_time_ms == 50.0
    assert summary.median_position_error_m == pytest.approx(0.36, abs=0.01)


def test_export_results_to_csv(tmp_path: Path):
    """Test exporting trials to CSV file format."""
    out_csv = tmp_path / "test_export.csv"
    trials = [
        TrialResult(
            pair_id="test_01", category="TestCat", description="Test Description",
            status="SUCCESS", keypoints_query=100, keypoints_ref=200, tentative_matches=60,
            ratio_matches=40, geometric_inliers=30, inlier_ratio=0.75, total_time_ms=45.2,
            true_center_x_m=500000.0, true_center_y_m=4000000.0,
            est_center_x_m=500000.1, est_center_y_m=4000000.1,
            position_error_m=0.141, localization_success=True,
        )
    ]

    export_results_to_csv(trials, out_csv)

    assert out_csv.exists()
    with out_csv.open("r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 1
        assert reader[0]["pair_id"] == "test_01"
        assert reader[0]["status"] == "SUCCESS"
        assert float(reader[0]["position_error_m"]) == pytest.approx(0.141)
