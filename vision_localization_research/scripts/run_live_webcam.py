"""
Live Physical Webcam Localization & Feature Matcher Proof.

Run this to physically demonstrate the exact computer vision pipeline
using your laptop webcam in real-time at 30 FPS.
"""

import sys
import time
from pathlib import Path
import cv2
import numpy as np

# Ensure src is in python path
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root / "src"))

from vision_loc.feature_matcher import VisualFeatureMatcher


def create_sample_reference(sample_path: Path):
    """Creates a high-contrast reference target if none exists."""
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (235, 235, 235)  # Light gray background

    # Geometric defense flight grid and text
    cv2.rectangle(img, (50, 50), (590, 430), (40, 40, 40), 3)
    cv2.circle(img, (320, 240), 90, (0, 102, 204), 4)
    cv2.drawMarker(img, (320, 240), (0, 0, 180), cv2.MARKER_CROSS, 40, 3)

    cv2.rectangle(img, (80, 80), (220, 180), (60, 120, 60), -1)
    cv2.circle(img, (480, 140), 45, (180, 80, 40), -1)
    cv2.circle(img, (160, 340), 55, (30, 80, 180), -1)

    cv2.putText(img, "REFERENCE TARGET", (80, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(img, "UAV RUNWAY A-1", (370, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2)
    cv2.putText(img, "LAT: 34.1526 N | LON: 77.5771 E", (120, 410), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (50, 50, 50), 2)

    cv2.imwrite(str(sample_path), img)
    return img


def run_live_webcam_demo():
    print("=" * 70)
    print("  LIVE PHYSICAL WEBCAM DEMONSTRATION")
    print("  Defense Visual Localization & Feature Matching Engine")
    print("=" * 70)
    print("\nHOW IT WORKS:")
    print("1. Press 'S' to SNAP the current camera frame as your Reference Target,")
    print("   OR show any book/printed image/phone screen to the camera.")
    print("2. Move or tilt the object — watch green RANSAC inliers track it live!")
    print("3. Real FPS, Inlier counts, and Reprojection are computed on your CPU.")
    print("4. Press 'Q' or 'ESC' to exit.\n")

    ref_dir = repo_root / "data"
    default_ref_path = ref_dir / "reference_target.png"

    matcher = VisualFeatureMatcher(max_features=800, ratio_threshold=0.75, ransac_reproj_threshold=5.0)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam (index 0).")
        return

    # Warmup camera
    ret, frame = cap.read()
    if not ret or frame is None:
        print("[ERROR] Failed to read frame from webcam.")
        cap.release()
        return

    # Check for default reference image or create sample
    if default_ref_path.exists():
        ref_bgr = cv2.imread(str(default_ref_path))
    else:
        ref_bgr = create_sample_reference(default_ref_path)

    ref_gray = cv2.cvtColor(ref_bgr, cv2.COLOR_BGR2GRAY)
    ref_kp, ref_desc = matcher.extract_features(ref_gray)

    fps_history = []
    mode = "DEFAULT_TARGET"

    print("[INFO] Live tracking started. OpenCV window opened.")

    while True:
        start_time = time.perf_counter()
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        query_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        query_kp, query_desc = matcher.extract_features(query_gray)

        inliers_count = 0
        inlier_ratio = 0.0
        good_matches = []
        inlier_matches = []
        homography = None

        if (
            ref_desc is not None
            and query_desc is not None
            and len(ref_kp) >= 4
            and len(query_kp) >= 4
        ):
            tentative = matcher.match_descriptors(query_desc, ref_desc)
            good_matches = matcher.filter_ratio(tentative)

            if len(good_matches) >= 4:
                H, mask, inliers_count, inlier_ratio = matcher.estimate_geometry_ransac(
                    query_kp, ref_kp, good_matches
                )
                if H is not None and mask is not None:
                    homography = H
                    inlier_matches = [m for m, inlier in zip(good_matches, mask) if inlier]

        # Draw Side-by-Side Match Visualization
        # Resize both to same height for clean display
        disp_h = 420
        scale_ref = disp_h / ref_bgr.shape[0]
        scale_query = disp_h / frame.shape[0]

        ref_resized = cv2.resize(ref_bgr, (int(ref_bgr.shape[1] * scale_ref), disp_h))
        frame_resized = cv2.resize(frame, (int(frame.shape[1] * scale_query), disp_h))

        # Re-scale keypoints for drawing on resized images
        scaled_ref_kp = [
            cv2.KeyPoint(kp.pt[0] * scale_ref, kp.pt[1] * scale_ref, kp.size * scale_ref)
            for kp in ref_kp
        ]
        scaled_query_kp = [
            cv2.KeyPoint(kp.pt[0] * scale_query, kp.pt[1] * scale_query, kp.size * scale_query)
            for kp in query_kp
        ]

        # Draw inlier matches in green
        matches_to_draw = inlier_matches if len(inlier_matches) > 0 else good_matches[:30]
        match_color = (0, 255, 0) if len(inlier_matches) >= 4 else (0, 165, 255)

        vis = cv2.drawMatches(
            frame_resized,
            scaled_query_kp,
            ref_resized,
            scaled_ref_kp,
            matches_to_draw,
            None,
            matchColor=match_color,
            singlePointColor=(120, 120, 120),
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )

        # Draw bounding polygon if homography exists
        if homography is not None:
            h_ref, w_ref = ref_bgr.shape[:2]
            pts_ref = np.float32([[0, 0], [w_ref, 0], [w_ref, h_ref], [0, h_ref]]).reshape(-1, 1, 2)
            try:
                H_inv = np.linalg.inv(homography)
                pts_in_query = cv2.perspectiveTransform(pts_ref, H_inv)
                # Rescale to query resized window
                pts_in_vis = pts_in_query.copy()
                pts_in_vis[:, 0, 0] *= scale_query
                pts_in_vis[:, 0, 1] *= scale_query
                cv2.polylines(vis, [np.int32(pts_in_vis)], True, (0, 255, 255), 3, cv2.LINE_AA)
            except np.linalg.LinAlgError:
                pass

        elapsed = time.perf_counter() - start_time
        fps = 1.0 / elapsed if elapsed > 0 else 0
        fps_history.append(fps)
        if len(fps_history) > 15:
            fps_history.pop(0)
        avg_fps = sum(fps_history) / len(fps_history)

        # Overlay Telemetry HUD
        hud_bg = vis.copy()
        cv2.rectangle(hud_bg, (0, 0), (vis.shape[1], 45), (20, 20, 20), -1)
        cv2.addWeighted(hud_bg, 0.85, vis, 0.15, 0, vis)

        status_text = "LOCKED (RANSAC HOMOGRAPHY)" if len(inlier_matches) >= 4 else "SEARCHING CORRESPONDENCES..."
        status_color = (0, 255, 0) if len(inlier_matches) >= 4 else (0, 165, 255)

        cv2.putText(
            vis,
            f"LIVE UAV CAMERA (LEFT)  vs  MAP REFERENCE (RIGHT) | {status_text}",
            (15, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            status_color,
            2,
        )
        cv2.putText(
            vis,
            f"FPS: {avg_fps:.1f} | Inliers: {inliers_count} | Ratio: {inlier_ratio*100:.1f}% | Press 'S' to Snap Target | 'Q' to Exit",
            (15, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (220, 220, 220),
            1,
        )

        cv2.imshow("Live Defense Visual Feature Matching & Localization Proof", vis)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break
        elif key == ord("s"):
            # Snap current camera frame as reference target!
            print("\n[SNAP] Captured new reference image from webcam!")
            ref_bgr = frame.copy()
            ref_gray = cv2.cvtColor(ref_bgr, cv2.COLOR_BGR2GRAY)
            ref_kp, ref_desc = matcher.extract_features(ref_gray)
            cv2.imwrite(str(default_ref_path), ref_bgr)
            mode = "USER_SNAPPED_TARGET"

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Webcam released. Demo closed cleanly.")


if __name__ == "__main__":
    run_live_webcam_demo()
