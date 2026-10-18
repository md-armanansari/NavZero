"""
Visual Feature Matching Module for Aerial Image Research.

Implements ORB feature extraction, Hamming descriptor matching, Lowe's ratio test,
and RANSAC geometric outlier filtering for image-to-image correspondence.
Does NOT perform geographic coordinate estimation or claim positional localization.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Union
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np

from vision_loc.image_inspector import load_image


@dataclass(frozen=True)
class MatchMetrics:
    """Stores quantitative measurements of a feature-matching experiment."""
    keypoints_query_count: int
    keypoints_reference_count: int
    tentative_matches_count: int
    ratio_filtered_count: int
    geometric_inliers_count: int
    inlier_ratio: float
    detection_time_seconds: float
    matching_time_seconds: float
    total_time_seconds: float
    status: str  # "SUCCESS", "INSUFFICIENT_FEATURES", "NO_CORRESPONDENCE", "GEOMETRIC_FIT_FAILED"


class VisualFeatureMatcher:
    """
    CPU-friendly visual feature extractor and matcher.
    Uses ORB (Oriented FAST and Rotated BRIEF) with Hamming distance matching.
    """

    def __init__(
        self,
        max_features: int = 1500,
        scale_factor: float = 1.2,
        n_levels: int = 8,
        ratio_threshold: float = 0.75,
        ransac_reproj_threshold: float = 5.0,
    ):
        """
        Args:
            max_features: Maximum number of features to retain per image.
            scale_factor: Pyramid decimation ratio (> 1.0).
            n_levels: Number of pyramid levels for scale invariance.
            ratio_threshold: Lowe's ratio test threshold (typically 0.70 - 0.80).
            ransac_reproj_threshold: Max allowed reprojection error in pixels for RANSAC inliers.
        """
        self.max_features = max_features
        self.scale_factor = scale_factor
        self.n_levels = n_levels
        self.ratio_threshold = ratio_threshold
        self.ransac_reproj_threshold = ransac_reproj_threshold

        # Initialize ORB detector
        self.detector = cv2.ORB_create(
            nfeatures=max_features,
            scaleFactor=scale_factor,
            nlevels=n_levels,
            edgeThreshold=31,
            firstLevel=0,
            WTA_K=2,
            scoreType=cv2.ORB_HARRIS_SCORE,
            patchSize=31,
            fastThreshold=20,
        )

        # BFMatcher using NORM_HAMMING for binary ORB descriptors
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    def extract_features(
        self, image: np.ndarray
    ) -> Tuple[List[cv2.KeyPoint], Optional[np.ndarray], float]:
        """
        Converts image to grayscale if needed and extracts ORB keypoints and descriptors.

        Returns:
            Tuple of (list of keypoints, descriptor array, elapsed time in seconds).
        """
        t0 = time.perf_counter()

        if image is None or image.size == 0:
            return [], None, 0.0

        if image.ndim == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        keypoints, descriptors = self.detector.detectAndCompute(gray, None)
        t_elapsed = time.perf_counter() - t0

        keypoints = list(keypoints) if keypoints is not None else []
        return keypoints, descriptors, t_elapsed

    def match(
        self,
        query_image: Union[np.ndarray, Path],
        reference_image: Union[np.ndarray, Path],
    ) -> Tuple[MatchMetrics, List[cv2.KeyPoint], List[cv2.KeyPoint], List[cv2.DMatch], Optional[np.ndarray]]:
        """
        Executes the full feature detection, matching, and outlier filtering pipeline.

        Args:
            query_image: Query image array or path to image file.
            reference_image: Reference image array or path to image file.

        Returns:
            Tuple containing:
                - MatchMetrics dataclass
                - Query keypoints
                - Reference keypoints
                - Inlier matches (list of cv2.DMatch)
                - Homography matrix (3x3 float array, or None if failed)
        """
        t_total_start = time.perf_counter()

        # Load images if file paths were provided
        if isinstance(query_image, (str, Path)):
            img_q, _ = load_image(Path(query_image), to_rgb=True)
        else:
            img_q = query_image

        if isinstance(reference_image, (str, Path)):
            img_r, _ = load_image(Path(reference_image), to_rgb=True)
        else:
            img_r = reference_image

        # 1. Feature Detection
        kp_q, des_q, t_det_q = self.extract_features(img_q)
        kp_r, des_r, t_det_r = self.extract_features(img_r)
        detection_time = t_det_q + t_det_r

        # Check for insufficient features (need at least 4 for planar homography)
        if len(kp_q) < 4 or len(kp_r) < 4 or des_q is None or des_r is None:
            total_time = time.perf_counter() - t_total_start
            metrics = MatchMetrics(
                keypoints_query_count=len(kp_q),
                keypoints_reference_count=len(kp_r),
                tentative_matches_count=0,
                ratio_filtered_count=0,
                geometric_inliers_count=0,
                inlier_ratio=0.0,
                detection_time_seconds=detection_time,
                matching_time_seconds=0.0,
                total_time_seconds=total_time,
                status="INSUFFICIENT_FEATURES",
            )
            return metrics, kp_q, kp_r, [], None

        # 2. Descriptor Matching (k=2 nearest neighbors for ratio test)
        t_match_start = time.perf_counter()
        raw_knn_matches = self.matcher.knnMatch(des_q, des_r, k=2)

        # 3. Lowe's Ratio Test
        ratio_matches: List[cv2.DMatch] = []
        for pair in raw_knn_matches:
            if len(pair) == 2:
                m, n = pair
                if m.distance < self.ratio_threshold * n.distance:
                    ratio_matches.append(m)

        tentative_count = len(raw_knn_matches)
        ratio_count = len(ratio_matches)

        if ratio_count < 4:
            match_time = time.perf_counter() - t_match_start
            total_time = time.perf_counter() - t_total_start
            metrics = MatchMetrics(
                keypoints_query_count=len(kp_q),
                keypoints_reference_count=len(kp_r),
                tentative_matches_count=tentative_count,
                ratio_filtered_count=ratio_count,
                geometric_inliers_count=0,
                inlier_ratio=0.0,
                detection_time_seconds=detection_time,
                matching_time_seconds=match_time,
                total_time_seconds=total_time,
                status="NO_CORRESPONDENCE",
            )
            return metrics, kp_q, kp_r, [], None

        # 4. Geometric Outlier Rejection via RANSAC
        src_pts = np.float32([kp_q[m.queryIdx].pt for m in ratio_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_r[m.trainIdx].pt for m in ratio_matches]).reshape(-1, 1, 2)

        homography, mask = cv2.findHomography(
            src_pts, dst_pts, cv2.RANSAC, self.ransac_reproj_threshold
        )
        match_time = time.perf_counter() - t_match_start
        total_time = time.perf_counter() - t_total_start

        if homography is None or mask is None:
            metrics = MatchMetrics(
                keypoints_query_count=len(kp_q),
                keypoints_reference_count=len(kp_r),
                tentative_matches_count=tentative_count,
                ratio_filtered_count=ratio_count,
                geometric_inliers_count=0,
                inlier_ratio=0.0,
                detection_time_seconds=detection_time,
                matching_time_seconds=match_time,
                total_time_seconds=total_time,
                status="GEOMETRIC_FIT_FAILED",
            )
            return metrics, kp_q, kp_r, [], None

        inliers_mask = mask.ravel().tolist()
        inlier_matches = [ratio_matches[i] for i, is_inlier in enumerate(inliers_mask) if is_inlier]
        inlier_count = len(inlier_matches)
        inlier_ratio = float(inlier_count) / float(ratio_count) if ratio_count > 0 else 0.0

        status = "SUCCESS" if inlier_count >= 4 else "NO_CORRESPONDENCE"

        metrics = MatchMetrics(
            keypoints_query_count=len(kp_q),
            keypoints_reference_count=len(kp_r),
            tentative_matches_count=tentative_count,
            ratio_filtered_count=ratio_count,
            geometric_inliers_count=inlier_count,
            inlier_ratio=round(inlier_ratio, 4),
            detection_time_seconds=round(detection_time, 4),
            matching_time_seconds=round(match_time, 4),
            total_time_seconds=round(total_time, 4),
            status=status,
        )

        return metrics, kp_q, kp_r, inlier_matches, homography

    @staticmethod
    def draw_matches_visualization(
        img_q: np.ndarray,
        kp_q: List[cv2.KeyPoint],
        img_r: np.ndarray,
        kp_r: List[cv2.KeyPoint],
        matches: List[cv2.DMatch],
        max_matches_to_draw: int = 50,
        save_path: Optional[Path] = None,
    ) -> np.ndarray:
        """
        Draws visual correspondences connecting inlier keypoints between query and reference images.

        Args:
            img_q: Query image array (RGB).
            kp_q: Query keypoints.
            img_r: Reference image array (RGB).
            kp_r: Reference keypoints.
            matches: Filtered inlier matches to draw.
            max_matches_to_draw: Max number of lines to draw for clarity.
            save_path: Optional path to save visual file.

        Returns:
            Rendered match image as RGB numpy array.
        """
        # Sort matches by descriptor distance (best matches first)
        sorted_matches = sorted(matches, key=lambda m: m.distance)[:max_matches_to_draw]

        # Convert RGB to BGR for OpenCV drawing function
        bgr_q = cv2.cvtColor(img_q, cv2.COLOR_RGB2BGR) if img_q.ndim == 3 else img_q
        bgr_r = cv2.cvtColor(img_r, cv2.COLOR_RGB2BGR) if img_r.ndim == 3 else img_r

        vis_bgr = cv2.drawMatches(
            bgr_q,
            kp_q,
            bgr_r,
            kp_r,
            sorted_matches,
            None,
            matchColor=(0, 255, 0),       # Green correspondence lines
            singlePointColor=(255, 0, 0),  # Blue keypoints
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )

        vis_rgb = cv2.cvtColor(vis_bgr, cv2.COLOR_BGR2RGB)

        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(save_path), vis_bgr)

        return vis_rgb
