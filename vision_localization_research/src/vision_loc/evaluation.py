"""
Research Evaluation and Benchmarking Module for Vision-Based Localization.

Provides reproducible dataset generation, degradation evaluation, metric computation
(including inlier ratio, latency percentiles, and ground-truth position error),
and structured CSV export without claiming operational military readiness.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import csv
import math
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np

from vision_loc.feature_matcher import VisualFeatureMatcher
from vision_loc.georeference import AffineTransform, CoordinateType, GeoReferenceMetadata


@dataclass(frozen=True)
class TrialResult:
    """Quantitative record of a single benchmark trial."""
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
    total_time_ms: float
    true_center_x_m: Optional[float]
    true_center_y_m: Optional[float]
    est_center_x_m: Optional[float]
    est_center_y_m: Optional[float]
    position_error_m: Optional[float]
    localization_success: bool


@dataclass(frozen=True)
class BenchmarkSummary:
    """Aggregated statistical summary of an experimental evaluation run."""
    total_trials: int
    successful_matches: int
    failed_matches: int
    match_success_rate: float
    successful_localizations: int
    median_time_ms: float
    p95_time_ms: float
    median_position_error_m: Optional[float]
    p95_position_error_m: Optional[float]


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
    # Winding path / road
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
    """
    pairs: List[Dict[str, Any]] = []
    h, w = base_image.shape[:2]

    # 1. Baseline: Pure translation / sub-crop
    center_c, center_r = w // 2, h // 2
    crop_base = base_image[
        center_r - crop_size // 2 : center_r + crop_size // 2,
        center_c - crop_size // 2 : center_c + crop_size // 2,
    ].copy()
    true_x, true_y = georef.pixel_to_map(center_c, center_r)

    pairs.append({
        "pair_id": "pair_01_baseline",
        "category": "Baseline",
        "description": "Standard translation crop with identical visual conditions",
        "query": crop_base,
        "reference": base_image,
        "true_pixel_center": (center_c, center_r),
        "true_map_coord": (true_x, true_y),
    })

    # 2. Brightness Reduction (low light / shadow)
    dark_crop = np.clip(crop_base.astype(np.float32) * 0.55 - 20, 0, 255).astype(np.uint8)
    pairs.append({
        "pair_id": "pair_02_brightness_dark",
        "category": "Illumination",
        "description": "Simulated low-light (45% reduction in brightness)",
        "query": dark_crop,
        "reference": base_image,
        "true_pixel_center": (center_c, center_r),
        "true_map_coord": (true_x, true_y),
    })

    # 3. Brightness Increase (high glare / exposure)
    bright_crop = np.clip(crop_base.astype(np.float32) * 1.35 + 30, 0, 255).astype(np.uint8)
    pairs.append({
        "pair_id": "pair_03_brightness_bright",
        "category": "Illumination",
        "description": "Simulated high glare / overexposure (+35% intensity)",
        "query": bright_crop,
        "reference": base_image,
        "true_pixel_center": (center_c, center_r),
        "true_map_coord": (true_x, true_y),
    })

    # 4. Rotation (20 degrees)
    rot_matrix = cv2.getRotationMatrix2D((crop_size // 2, crop_size // 2), 20.0, 1.0)
    rotated_crop = cv2.warpAffine(crop_base, rot_matrix, (crop_size, crop_size), borderMode=cv2.BORDER_REFLECT)
    pairs.append({
        "pair_id": "pair_04_rotation_20deg",
        "category": "Geometric",
        "description": "20-degree in-plane rotation",
        "query": rotated_crop,
        "reference": base_image,
        "true_pixel_center": (center_c, center_r),
        "true_map_coord": (true_x, true_y),
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
        "true_pixel_center": (center_c, center_r),
        "true_map_coord": (true_x, true_y),
    })

    # 6. Hard Negative: Pure Gaussian noise (uncorrelated)
    uncorrelated = rng_noise.randint(0, 256, (crop_size, crop_size, 3), dtype=np.uint8)
    pairs.append({
        "pair_id": "pair_06_uncorrelated_noise",
        "category": "Hard Negative",
        "description": "Uncorrelated random noise canvas (expected zero match)",
        "query": uncorrelated,
        "reference": base_image,
        "true_pixel_center": None,
        "true_map_coord": None,
    })

    # 7. Hard Negative: Solid blank frame
    blank = np.zeros((crop_size, crop_size, 3), dtype=np.uint8)
    pairs.append({
        "pair_id": "pair_07_blank_frame",
        "category": "Hard Negative",
        "description": "Completely blank zero-feature frame",
        "query": blank,
        "reference": base_image,
        "true_pixel_center": None,
        "true_map_coord": None,
    })

    return pairs


def evaluate_trial(
    matcher: VisualFeatureMatcher,
    pair_data: Dict[str, Any],
    georef: Optional[AffineTransform] = None,
) -> TrialResult:
    """
    Executes a single benchmark evaluation trial and records measured metrics.
    """
    query_img = pair_data["query"]
    ref_img = pair_data["reference"]
    t0 = time.perf_counter()

    metrics, kp_q, kp_r, inliers, homography = matcher.match(query_img, ref_img)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    true_map_coord = pair_data.get("true_map_coord")
    true_x = true_map_coord[0] if true_map_coord else None
    true_y = true_map_coord[1] if true_map_coord else None

    est_x, est_y, pos_err_m = None, None, None
    loc_success = False

    # Position error calculation (only if matching succeeded, homography exists, and ground truth is valid)
    if metrics.status == "SUCCESS" and homography is not None and georef is not None and true_map_coord is not None:
        qh, qw = query_img.shape[:2]
        query_center = np.array([[[qw / 2.0, qh / 2.0]]], dtype=np.float32)
        try:
            mapped_center = cv2.perspectiveTransform(query_center, homography)[0][0]
            est_px, est_py = float(mapped_center[0]), float(mapped_center[1])
            est_x, est_y = georef.pixel_to_map(est_px, est_py)
            pos_err_m = math.sqrt((est_x - true_x) ** 2 + (est_y - true_y) ** 2)
            loc_success = True
        except cv2.error:
            loc_success = False

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
        total_time_ms=round(elapsed_ms, 2),
        true_center_x_m=round(true_x, 3) if true_x is not None else None,
        true_center_y_m=round(true_y, 3) if true_y is not None else None,
        est_center_x_m=round(est_x, 3) if est_x is not None else None,
        est_center_y_m=round(est_y, 3) if est_y is not None else None,
        position_error_m=round(pos_err_m, 3) if pos_err_m is not None else None,
        localization_success=loc_success,
    )


def compute_summary_statistics(results: List[TrialResult]) -> BenchmarkSummary:
    """
    Computes aggregated statistical indicators across all benchmark trials.
    """
    total = len(results)
    if total == 0:
        return BenchmarkSummary(0, 0, 0, 0.0, 0, 0.0, 0.0, None, None)

    successful_matches = sum(1 for r in results if r.status == "SUCCESS")
    failed_matches = total - successful_matches
    match_rate = float(successful_matches) / float(total)

    successful_locs = sum(1 for r in results if r.localization_success)

    latencies = [r.total_time_ms for r in results]
    median_time = float(np.median(latencies))
    p95_time = float(np.percentile(latencies, 95))

    errors = [r.position_error_m for r in results if r.position_error_m is not None]
    median_err = float(np.median(errors)) if errors else None
    p95_err = float(np.percentile(errors, 95)) if errors else None

    return BenchmarkSummary(
        total_trials=total,
        successful_matches=successful_matches,
        failed_matches=failed_matches,
        match_success_rate=round(match_rate, 4),
        successful_localizations=successful_locs,
        median_time_ms=round(median_time, 2),
        p95_time_ms=round(p95_time, 2),
        median_position_error_m=round(median_err, 3) if median_err is not None else None,
        p95_position_error_m=round(p95_err, 3) if p95_err is not None else None,
    )


def export_results_to_csv(results: List[TrialResult], output_path: Path) -> None:
    """Exports trial results table to structured CSV format."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "pair_id", "category", "description", "status",
        "keypoints_query", "keypoints_ref", "tentative_matches",
        "ratio_matches", "geometric_inliers", "inlier_ratio", "total_time_ms",
        "true_center_x_m", "true_center_y_m", "est_center_x_m", "est_center_y_m",
        "position_error_m", "localization_success",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))
