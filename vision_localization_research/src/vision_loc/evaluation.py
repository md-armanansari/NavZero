"""
Research Evaluation and Benchmarking Module for Vision-Based Localization.

Provides reproducible dataset generation, degradation evaluation, metric computation
(including inlier ratio, multi-run steady-state latency percentiles, and independent
ground-truth geometric reprojection error).
Does NOT claim real-world geodetic positioning accuracy or operational flight readiness.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import csv
import math
import time

import cv2
import numpy as np

from vision_loc.feature_matcher import VisualFeatureMatcher
from vision_loc.georeference import AffineTransform


@dataclass(frozen=True)
class TrialResult:
    """Quantitative record of a single benchmark trial with multi-run timing."""
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


@dataclass(frozen=True)
class BenchmarkSummary:
    """Aggregated statistical summary of an experimental evaluation run."""
    total_trials: int
    successful_matches: int
    failed_matches: int
    sample_match_success_rate: float
    timing_repetitions_per_trial: int
    median_steady_state_time_ms: float
    p95_steady_state_time_ms: float
    median_pixel_rmse: Optional[float]
    p95_pixel_rmse: Optional[float]
    median_synthetic_grid_error_m: Optional[float]
    p95_synthetic_grid_error_m: Optional[float]
    disclaimer: str


def create_base_synthetic_landscape(width: int = 1200, height: int = 1200, seed: int = 42) -> np.ndarray:
    """
    Generates a deterministic synthetic landscape with high-contrast, multi-scale visual features.
    """
    rng = np.random.RandomState(seed)
    canvas = np.ones((height, width, 3), dtype=np.uint8) * 180

    # Low-frequency terrain variations
    noise_low = cv2.resize(rng.normal(0, 30, (height // 16, width // 16)).astype(np.float32), (width, height))
    canvas = np.clip(canvas.astype(np.float32) + noise_low[:, :, None], 0, 255).astype(np.uint8)

    # Distinct geometric landmarks (roads, rivers, structures)
    road_pts = []
    rx = width // 3
    for ry in range(0, height, 40):
        rx += int(math.sin(ry * 0.02) * 20 + rng.randint(-5, 5))
        road_pts.append([max(10, min(width - 10, rx)), ry])
    cv2.polylines(canvas, [np.array(road_pts, np.int32)], isClosed=False, color=(70, 70, 80), thickness=6)

    # Cross path
    cv2.line(canvas, (100, height // 2), (width - 100, height // 3), (120, 120, 130), 4)

    # High-contrast geometric structures
    for _ in range(25):
        cx = rng.randint(80, width - 80)
        cy = rng.randint(80, height - 80)
        w_box = rng.randint(20, 60)
        h_box = rng.randint(20, 60)
        color = (rng.randint(30, 90), rng.randint(120, 220), rng.randint(40, 100))
        cv2.rectangle(canvas, (cx, cy), (cx + w_box, cy + h_box), color, -1)
        cv2.circle(canvas, (cx + w_box // 2, cy + h_box // 2), max(2, w_box // 4), (20, 20, 20), -1)

    return canvas


def generate_benchmark_pairs(
    base_image: np.ndarray,
    georef: AffineTransform,
    crop_size: int = 350,
) -> List[Dict[str, Any]]:
    """
    Generates a deterministic test suite of image pairs across varying degradation categories.
    Each pair includes an independent known ground-truth affine transformation matrix (T_true_3x3).
    """
    pairs: List[Dict[str, Any]] = []
    h, w = base_image.shape[:2]

    # Baseline: Pure translation / sub-crop
    center_c, center_r = w // 2, h // 2
    crop_x1 = center_c - crop_size // 2
    crop_y1 = center_r - crop_size // 2
    crop_base = base_image[crop_y1 : crop_y1 + crop_size, crop_x1 : crop_x1 + crop_size].copy()

    # Ground-truth mapping: point in crop (qc, qr) -> point in base (qc + crop_x1, qr + crop_y1)
    t_baseline = np.array([
        [1.0, 0.0, float(crop_x1)],
        [0.0, 1.0, float(crop_y1)],
        [0.0, 0.0, 1.0]
    ], dtype=np.float64)

    pairs.append({
        "pair_id": "pair_01_baseline",
        "category": "Baseline",
        "description": "Standard translation crop with identical visual conditions",
        "query": crop_base,
        "reference": base_image,
        "ground_truth_transform": t_baseline,
    })

    # 2. Brightness Reduction (low light / shadow)
    dark_crop = np.clip(crop_base.astype(np.float32) * 0.55 - 20, 0, 255).astype(np.uint8)
    pairs.append({
        "pair_id": "pair_02_brightness_dark",
        "category": "Illumination",
        "description": "Simulated low-light (45% reduction in brightness)",
        "query": dark_crop,
        "reference": base_image,
        "ground_truth_transform": t_baseline,
    })

    # 3. Brightness Increase (high glare / exposure)
    bright_crop = np.clip(crop_base.astype(np.float32) * 1.35 + 30, 0, 255).astype(np.uint8)
    pairs.append({
        "pair_id": "pair_03_brightness_bright",
        "category": "Illumination",
        "description": "Simulated high glare / overexposure (+35% intensity)",
        "query": bright_crop,
        "reference": base_image,
        "ground_truth_transform": t_baseline,
    })

    # 4. Rotation (20 degrees around crop center)
    rot_angle = 20.0
    rot_mat_2x3 = cv2.getRotationMatrix2D((crop_size / 2.0, crop_size / 2.0), rot_angle, 1.0)
    rotated_crop = cv2.warpAffine(crop_base, rot_mat_2x3, (crop_size, crop_size), borderMode=cv2.BORDER_REFLECT)

    # Full ground truth mapping: point in rotated crop -> inverse rotation -> add crop offset
    inv_rot_2x3 = cv2.getRotationMatrix2D((crop_size / 2.0, crop_size / 2.0), -rot_angle, 1.0)
    inv_rot_3x3 = np.vstack([inv_rot_2x3, [0, 0, 1]])
    trans_3x3 = np.array([
        [1.0, 0.0, float(crop_x1)],
        [0.0, 1.0, float(crop_y1)],
        [0.0, 0.0, 1.0]
    ], dtype=np.float64)
    t_rot_true = trans_3x3 @ inv_rot_3x3

    pairs.append({
        "pair_id": "pair_04_rotation_20deg",
        "category": "Geometric",
        "description": "20-degree in-plane rotation",
        "query": rotated_crop,
        "reference": base_image,
        "ground_truth_transform": t_rot_true,
    })

    # 5. Gaussian Sensor Noise
    rng_noise = np.random.RandomState(105)
    noise = rng_noise.normal(0, 20, crop_base.shape).astype(np.float32)
    noisy_crop = np.clip(crop_base.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    pairs.append({
        "pair_id": "pair_05_sensor_noise",
        "category": "Sensor Noise",
        "description": "Additive zero-mean Gaussian sensor noise (sigma=20)",
        "query": noisy_crop,
        "reference": base_image,
        "ground_truth_transform": t_baseline,
    })

    # 6. Hard Negative: Pure Gaussian noise (uncorrelated)
    uncorrelated = rng_noise.randint(0, 256, (crop_size, crop_size, 3), dtype=np.uint8)
    pairs.append({
        "pair_id": "pair_06_uncorrelated_noise",
        "category": "Hard Negative",
        "description": "Uncorrelated random noise canvas (expected zero match)",
        "query": uncorrelated,
        "reference": base_image,
        "ground_truth_transform": None,
    })

    # 7. Hard Negative: Solid blank frame
    blank = np.zeros((crop_size, crop_size, 3), dtype=np.uint8)
    pairs.append({
        "pair_id": "pair_07_blank_frame",
        "category": "Hard Negative",
        "description": "Completely blank zero-feature frame",
        "query": blank,
        "reference": base_image,
        "ground_truth_transform": None,
    })

    return pairs


def calculate_independent_reprojection_error(
    query_w: int,
    query_h: int,
    homography_est: np.ndarray,
    ground_truth_transform: np.ndarray,
    grid_steps: int = 5,
) -> Tuple[int, float]:
    """
    Computes Root Mean Square Error (RMSE) in pixels over an independent uniform
    grid of check points across the query image, comparing the estimated homography
    against the known analytical ground-truth transformation.
    Does NOT reuse detected keypoints or inlier matches.
    """
    # Create independent 5x5 grid of verification points (avoiding outermost border)
    xs = np.linspace(query_w * 0.15, query_w * 0.85, grid_steps)
    ys = np.linspace(query_h * 0.15, query_h * 0.85, grid_steps)
    grid_pts = np.array([[x, y] for x in xs for y in ys], dtype=np.float32).reshape(-1, 1, 2)

    # 1. Map through estimated homography
    est_pts = cv2.perspectiveTransform(grid_pts, homography_est).reshape(-1, 2)

    # 2. Map through known ground truth transformation
    true_pts = cv2.perspectiveTransform(grid_pts, ground_truth_transform.astype(np.float32)).reshape(-1, 2)

    # 3. Calculate Euclidean distance per check point
    diffs = est_pts - true_pts
    squared_errors = np.sum(diffs ** 2, axis=1)
    rmse_pixels = float(np.sqrt(np.mean(squared_errors)))

    return len(grid_pts), rmse_pixels


def evaluate_trial(
    matcher: VisualFeatureMatcher,
    pair_data: Dict[str, Any],
    georef: Optional[AffineTransform] = None,
    timing_repeats: int = 5,
) -> TrialResult:
    """
    Executes an evaluation trial with separate warmup and multi-run steady-state latency timing.
    """
    query_img = pair_data["query"]
    ref_img = pair_data["reference"]
    t_true = pair_data.get("ground_truth_transform")

    # 1. Warmup execution (unrecorded, prevents first-run cache contamination)
    _ = matcher.match(query_img, ref_img)

    # 2. Multi-run steady-state timing
    latencies_ms: List[float] = []
    last_res = None
    for _ in range(timing_repeats):
        t0 = time.perf_counter()
        last_res = matcher.match(query_img, ref_img)
        t_elapsed = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(t_elapsed)

    metrics, kp_q, kp_r, inliers, homography = last_res
    latency_median = float(np.median(latencies_ms))
    latency_std = float(np.std(latencies_ms))

    # 3. Independent Geometric Reprojection Error (Pixels)
    checkpoints_count = 0
    rmse_pixels = None
    synthetic_grid_error_m = None
    geo_success = False

    if metrics.status == "SUCCESS" and homography is not None and t_true is not None:
        qh, qw = query_img.shape[:2]
        checkpoints_count, rmse_pixels = calculate_independent_reprojection_error(
            qw, qh, homography, t_true, grid_steps=5
        )
        geo_success = True

        # If an affine georeference scale is provided, report the synthetic grid scale
        if georef is not None:
            # GSD = pixel scale (e.g. 0.5 meters/pixel)
            gsd = abs(georef.a)
            synthetic_grid_error_m = rmse_pixels * gsd

    return TrialResult(
        pair_id=pair_data["pair_id"],
        category=pair_data["category"],
        description=pair_data["description"],
        status=metrics.status,
        keypoints_query=metrics.keypoints_query_count,
        keypoints_ref=metrics.keypoints_reference_count,
        tentative_matches=metrics.tentative_matches_count,
        ratio_matches=metrics.ratio_filtered_count,
        geometric_inliers=metrics.geometric_inliers_count,
        inlier_ratio=metrics.inlier_ratio,
        timing_repetitions=timing_repeats,
        steady_state_latency_median_ms=round(latency_median, 2),
        steady_state_latency_std_ms=round(latency_std, 2),
        independent_checkpoints_tested=checkpoints_count,
        pixel_reprojection_rmse=round(rmse_pixels, 3) if rmse_pixels is not None else None,
        synthetic_grid_error_m=round(synthetic_grid_error_m, 3) if synthetic_grid_error_m is not None else None,
        geometric_verification_success=geo_success,
    )


def compute_summary_statistics(results: List[TrialResult]) -> BenchmarkSummary:
    """
    Computes statistical indicators across benchmark trials with explicit disclaimers.
    """
    total = len(results)
    if total == 0:
        return BenchmarkSummary(0, 0, 0, 0.0, 0, 0.0, 0.0, None, None, None, None, "No trials tested.")

    successful_matches = sum(1 for r in results if r.status == "SUCCESS")
    failed_matches = total - successful_matches
    match_rate = float(successful_matches) / float(total)

    repeats = results[0].timing_repetitions if results else 0
    steady_latencies = [r.steady_state_latency_median_ms for r in results]
    median_time = float(np.median(steady_latencies))
    p95_time = float(np.percentile(steady_latencies, 95))

    pixel_errors = [r.pixel_reprojection_rmse for r in results if r.pixel_reprojection_rmse is not None]
    median_px_err = float(np.median(pixel_errors)) if pixel_errors else None
    p95_px_err = float(np.percentile(pixel_errors, 95)) if pixel_errors else None

    grid_errors = [r.synthetic_grid_error_m for r in results if r.synthetic_grid_error_m is not None]
    median_grid_err = float(np.median(grid_errors)) if grid_errors else None
    p95_grid_err = float(np.percentile(grid_errors, 95)) if grid_errors else None

    disclaimer = (
        "Notice: The sample match rate and zero false-positive observation apply strictly to this "
        "controlled synthetic 7-pair benchmark. Pixel RMSE is measured on independent 25-point synthetic "
        "grid mappings and does NOT claim real-world geodetic localization accuracy."
    )

    return BenchmarkSummary(
        total_trials=total,
        successful_matches=successful_matches,
        failed_matches=failed_matches,
        sample_match_success_rate=round(match_rate, 4),
        timing_repetitions_per_trial=repeats,
        median_steady_state_time_ms=round(median_time, 2),
        p95_steady_state_time_ms=round(p95_time, 2),
        median_pixel_rmse=round(median_px_err, 3) if median_px_err is not None else None,
        p95_pixel_rmse=round(p95_px_err, 3) if p95_px_err is not None else None,
        median_synthetic_grid_error_m=round(median_grid_err, 3) if median_grid_err is not None else None,
        p95_synthetic_grid_error_m=round(p95_grid_err, 3) if p95_grid_err is not None else None,
        disclaimer=disclaimer,
    )


def export_results_to_csv(results: List[TrialResult], output_path: Path) -> None:
    """Exports trial results table to structured CSV format."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "pair_id", "category", "description", "status",
        "keypoints_query", "keypoints_ref", "tentative_matches",
        "ratio_matches", "geometric_inliers", "inlier_ratio",
        "timing_repetitions", "steady_state_latency_median_ms", "steady_state_latency_std_ms",
        "independent_checkpoints_tested", "pixel_reprojection_rmse",
        "synthetic_grid_error_m", "geometric_verification_success",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))
