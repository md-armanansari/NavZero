"""
Unit and Integration Tests for Visual Feature Matcher Module.
"""
from pathlib import Path
import pytest
import numpy as np
import cv2

from vision_loc.feature_matcher import (
    VisualFeatureMatcher,
    MatchMetrics,
)


def create_patterned_image(size: int = 400) -> np.ndarray:
    """Creates a deterministic patterned image with rich visual corners and edges."""
    img = np.ones((size, size, 3), dtype=np.uint8) * 200
    
    # Add high-contrast geometric shapes
    cv2.rectangle(img, (50, 50), (150, 150), (20, 20, 20), -1)
    cv2.circle(img, (280, 100), 40, (50, 150, 50), -1)
    cv2.circle(img, (120, 280), 50, (30, 30, 180), -1)
    
    # Add distinct cross-lines and checker patterns
    for i in range(200, 350, 20):
        cv2.line(img, (i, 200), (i + 15, 350), (0, 0, 0), 2)
        cv2.line(img, (200, i), (350, i + 15), (0, 0, 0), 2)
        
    return img


def test_matcher_successful_pair():
    """Test matching between a reference image and a transformed crop of itself."""
    ref_img = create_patterned_image(size=500)
    
    # Query is a sub-crop shifted by (40, 40)
    query_img = ref_img[40:440, 40:440].copy()
    
    matcher = VisualFeatureMatcher(max_features=1000)
    metrics, kp_q, kp_r, inliers, homography = matcher.match(query_img, ref_img)

    assert isinstance(metrics, MatchMetrics)
    assert metrics.status == "SUCCESS"
    assert metrics.keypoints_query_count > 20
    assert metrics.keypoints_reference_count > 20
    assert metrics.tentative_matches_count > 0
    assert metrics.geometric_inliers_count >= 4
    assert 0.0 < metrics.inlier_ratio <= 1.0
    assert metrics.total_time_seconds > 0.0
    assert homography is not None
    assert homography.shape == (3, 3)


def test_matcher_dissimilar_images_returns_no_correspondence():
    """Test that two completely dissimilar patterns produce zero or near-zero geometric inliers."""
    # Image 1: Geometric circles and squares
    img_a = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.circle(img_a, (150, 150), 80, (255, 255, 255), -1)
    
    # Image 2: Uncorrelated random noise
    np.random.seed(42)
    img_b = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)

    matcher = VisualFeatureMatcher(max_features=500)
    metrics, kp_q, kp_r, inliers, homography = matcher.match(img_a, img_b)

    assert metrics.status in ("NO_CORRESPONDENCE", "INSUFFICIENT_FEATURES")
    assert metrics.geometric_inliers_count < 4
    assert homography is None


def test_matcher_empty_blank_image_handles_cleanly():
    """Test that a blank image (zero features) does not crash or raise exceptions."""
    blank_img = np.zeros((300, 300, 3), dtype=np.uint8)
    valid_img = create_patterned_image(300)

    matcher = VisualFeatureMatcher()
    metrics, kp_q, kp_r, inliers, homography = matcher.match(blank_img, valid_img)

    assert metrics.status == "INSUFFICIENT_FEATURES"
    assert metrics.geometric_inliers_count == 0
    assert metrics.inlier_ratio == 0.0
    assert homography is None
    assert inliers == []


def test_matcher_invalid_empty_numpy_array():
    """Test passing a 0-sized array."""
    empty_arr = np.array([])
    valid_img = create_patterned_image(200)

    matcher = VisualFeatureMatcher()
    metrics, kp_q, kp_r, inliers, homography = matcher.match(empty_arr, valid_img)

    assert metrics.status == "INSUFFICIENT_FEATURES"
    assert metrics.keypoints_query_count == 0


def test_draw_matches_visualization(tmp_path: Path):
    """Test that correspondence visualization creates a valid output image without error."""
    ref_img = create_patterned_image(size=400)
    query_img = ref_img[30:350, 30:350].copy()

    matcher = VisualFeatureMatcher(max_features=800)
    metrics, kp_q, kp_r, inliers, H = matcher.match(query_img, ref_img)

    save_file = tmp_path / "match_visualization.png"
    vis = matcher.draw_matches_visualization(
        query_img, kp_q, ref_img, kp_r, inliers, max_matches_to_draw=25, save_path=save_file
    )

    assert isinstance(vis, np.ndarray)
    assert vis.ndim == 3
    # Width of visualization is query width + reference width
    assert vis.shape[1] == query_img.shape[1] + ref_img.shape[1]
    assert save_file.exists()
    assert save_file.stat().st_size > 0
