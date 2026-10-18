"""
Unit Tests for Research Evaluation and Benchmarking Module (Validated).
"""
from pathlib import Path
import csv
import pytest
import numpy as np

from vision_loc.evaluation import (
    BenchmarkSummary,
    TrialResult,
    calculate_independent_reprojection_error,
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
    """Verify that test pairs include expected categories and analytical transformation matrices."""
    georef = AffineTransform(500000.0, 4000000.0, 1.0, 0.0, 0.0, -1.0)
    base_img = create_base_synthetic_landscape(width=600, height=600, seed=42)

    pairs = generate_benchmark_pairs(base_img, georef, crop_size=200)

    assert len(pairs) >= 5
    categories = {p["category"] for p in pairs}
    assert "Baseline" in categories
    assert "Illumination" in categories
    assert "Geometric" in categories
    assert "Hard Negative" in categories

    # Baseline must have an analytical 3x3 transformation
    baseline = next(p for p in pairs if p["pair_id"] == "pair_01_baseline")
    assert baseline["ground_truth_transform"].shape == (3, 3)


def test_independent_reprojection_error_calculation():
    """Verify calculation of independent RMSE over grid of check points."""
    # Test identical homography (0.0 pixel error)
    h_identity = np.eye(3, dtype=np.float32)
    t_identity = np.eye(3, dtype=np.float32)

    n_pts, rmse = calculate_independent_reprojection_error(200, 200, h_identity, t_identity, grid_steps=5)
    assert n_pts == 25
    assert rmse == pytest.approx(0.0, abs=1e-6)

    # Test homography shifted by exactly 3.0 pixels in X and 4.0 pixels in Y (RMSE = 5.0 px)
    h_shifted = np.array([
        [1.0, 0.0, 3.0],
        [0.0, 1.0, 4.0],
        [0.0, 0.0, 1.0]
    ], dtype=np.float32)

    n_pts, rmse_shift = calculate_independent_reprojection_error(200, 200, h_shifted, t_identity, grid_steps=5)
    assert rmse_shift == pytest.approx(5.0, abs=1e-5)


def test_evaluate_trial_steady_state_timing_and_failure_handling():
    """Test multi-run timing and graceful failure handling on hard negatives."""
    georef = AffineTransform(500000.0, 4000000.0, 0.5, 0.0, 0.0, -0.5)
    base_img = create_base_synthetic_landscape(width=600, height=600, seed=42)
    pairs = generate_benchmark_pairs(base_img, georef, crop_size=200)

    matcher = VisualFeatureMatcher(max_features=800)

    # 1. Baseline trial with 3 steady-state repetitions
    baseline_pair = next(p for p in pairs if p["pair_id"] == "pair_01_baseline")
    res_base = evaluate_trial(matcher, baseline_pair, georef, timing_repeats=3)

    assert res_base.status == "SUCCESS"
    assert res_base.timing_repetitions == 3
    assert res_base.steady_state_latency_median_ms > 0.0
    assert res_base.pixel_reprojection_rmse is not None
    # On identical baseline crop, reprojection error against ground truth should be sub-pixel
    assert res_base.pixel_reprojection_rmse < 1.0
    assert res_base.synthetic_grid_error_m == pytest.approx(res_base.pixel_reprojection_rmse * 0.5, abs=1e-3)

    # 2. Hard negative blank trial
    blank_pair = next(p for p in pairs if p["pair_id"] == "pair_07_blank_frame")
    res_blank = evaluate_trial(matcher, blank_pair, georef, timing_repeats=2)

    assert res_blank.status == "INSUFFICIENT_FEATURES"
    assert res_blank.geometric_inliers == 0
    assert res_blank.pixel_reprojection_rmse is None
    assert res_blank.synthetic_grid_error_m is None
    assert res_blank.geometric_verification_success is False


def test_compute_summary_statistics():
    """Test calculation of summary statistics (medians, percentiles, rates)."""
    trials = [
        TrialResult(
            pair_id="t1", category="Cat", description="d", status="SUCCESS",
            keypoints_query=100, keypoints_ref=100, tentative_matches=50, ratio_matches=30,
            geometric_inliers=25, inlier_ratio=0.83, timing_repetitions=3,
            steady_state_latency_median_ms=50.0, steady_state_latency_std_ms=2.1,
            independent_checkpoints_tested=25, pixel_reprojection_rmse=0.40,
            synthetic_grid_error_m=0.20, geometric_verification_success=True,
        ),
        TrialResult(
            pair_id="t2", category="Cat", description="d", status="SUCCESS",
            keypoints_query=100, keypoints_ref=100, tentative_matches=40, ratio_matches=25,
            geometric_inliers=20, inlier_ratio=0.80, timing_repetitions=3,
            steady_state_latency_median_ms=70.0, steady_state_latency_std_ms=3.0,
            independent_checkpoints_tested=25, pixel_reprojection_rmse=0.80,
            synthetic_grid_error_m=0.40, geometric_verification_success=True,
        ),
        TrialResult(
            pair_id="t3", category="Cat", description="d", status="NO_CORRESPONDENCE",
            keypoints_query=10, keypoints_ref=100, tentative_matches=5, ratio_matches=2,
            geometric_inliers=0, inlier_ratio=0.0, timing_repetitions=3,
            steady_state_latency_median_ms=30.0, steady_state_latency_std_ms=1.5,
            independent_checkpoints_tested=0, pixel_reprojection_rmse=None,
            synthetic_grid_error_m=None, geometric_verification_success=False,
        ),
    ]

    summary = compute_summary_statistics(trials)

    assert summary.total_trials == 3
    assert summary.successful_matches == 2
    assert summary.failed_matches == 1
    assert summary.sample_match_success_rate == pytest.approx(2 / 3, abs=1e-3)
    assert summary.median_steady_state_time_ms == 50.0
    assert summary.median_pixel_rmse == pytest.approx(0.60, abs=0.01)
    assert summary.median_synthetic_grid_error_m == pytest.approx(0.30, abs=0.01)
    assert "Notice:" in summary.disclaimer


def test_export_results_to_csv(tmp_path: Path):
    """Test exporting trials to CSV file format."""
    out_csv = tmp_path / "test_export.csv"
    trials = [
        TrialResult(
            pair_id="test_01", category="TestCat", description="Test Description",
            status="SUCCESS", keypoints_query=100, keypoints_ref=200, tentative_matches=60,
            ratio_matches=40, geometric_inliers=30, inlier_ratio=0.75, timing_repetitions=5,
            steady_state_latency_median_ms=45.2, steady_state_latency_std_ms=1.8,
            independent_checkpoints_tested=25, pixel_reprojection_rmse=0.35,
            synthetic_grid_error_m=0.175, geometric_verification_success=True,
        )
    ]

    export_results_to_csv(trials, out_csv)

    assert out_csv.exists()
    with out_csv.open("r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 1
        assert reader[0]["pair_id"] == "test_01"
        assert reader[0]["status"] == "SUCCESS"
        assert float(reader[0]["pixel_reprojection_rmse"]) == pytest.approx(0.35)
        assert float(reader[0]["synthetic_grid_error_m"]) == pytest.approx(0.175)
