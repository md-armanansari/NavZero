"""
Autonomous Visual Breadcrumb Return-to-Home Engine (Scenario B - Zero Maps).

Demonstrates 100% Zero-Map Autonomous Navigation:
1. Snaps Home Takeoff Pad (Frame 0).
2. As drone/camera moves into unknown territory, automatically drops visual breadcrumbs.
3. When 'J' is pressed (GPS + Radio Lost), engages Autonomous Return-to-Home (V-RTH).
4. Retraces its exact visual breadcrumb steps in reverse order all the way back to Frame 0!
5. Works on your laptop webcam OR physical camera without any pre-loaded map files.
"""

import math
import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import cv2
import numpy as np

# Ensure src is in python path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from vision_loc.feature_matcher import VisualFeatureMatcher


@dataclass
class VisualBreadcrumb:
    """A visual footprint dropped by the drone along its outbound flight."""
    id: int
    image_gray: np.ndarray
    keypoints: List[cv2.KeyPoint]
    descriptors: np.ndarray
    timestamp: float
    simulated_x: float
    simulated_y: float


def run_breadcrumb_demo():
    print("=" * 72)
    print("  SCENARIO B: AUTONOMOUS VISUAL BREADCRUMB RETURN-TO-HOME (V-RTH)")
    print("  100% Zero-Map Navigation - Navigating Purely by Visual Footprints")
    print("=" * 72)
    print("\nHOW IT WORKS:")
    print(" 1. Point webcam at floor/desk. It automatically locks 'HOME_BASE' (Frame 0).")
    print(" 2. Move camera across room/desk. It automatically drops visual breadcrumbs.")
    print(" 3. Press [J] (Simulate GPS Jammed / Signal Lost).")
    print(" 4. Press [R] (Trigger Emergency Visual Return-to-Home).")
    print("    Watch the system guide you step-by-step back to Frame 0!")
    print(" 5. Press [Q] or [ESC] to exit.\n")

    matcher = VisualFeatureMatcher(max_features=600, ratio_threshold=0.75, ransac_reproj_threshold=5.0)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam (tried index 0 and 1).")
        print("[HINT] On macOS, make sure Camera permission is granted:")
        print("       System Settings -> Privacy & Security -> Camera -> Terminal / IDE")
        return

    # Warmup
    ret, frame = cap.read()
    if not ret or frame is None:
        cap.release()
        cap = cv2.VideoCapture(1)
        if cap.isOpened():
            ret, frame = cap.read()
    if not ret or frame is None:
        print("[ERROR] Camera frame capture failed.")
        print("[HINT] On macOS, make sure Camera permission is granted:")
        print("       System Settings -> Privacy & Security -> Camera -> Terminal / IDE")
        cap.release()
        return

    # Step 1: Capture Takeoff Base (Frame 0)
    home_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    home_kp, home_desc, _ = matcher.extract_features(home_gray)

    breadcrumbs: List[VisualBreadcrumb] = []
    breadcrumbs.append(
        VisualBreadcrumb(
            id=0,
            image_gray=home_gray,
            keypoints=home_kp,
            descriptors=home_desc,
            timestamp=time.perf_counter(),
            simulated_x=0.0,
            simulated_y=0.0,
        )
    )

    print("[INFO] HOME_BASE (Takeoff Point) established successfully!")

    last_breadcrumb_time = time.perf_counter()
    jammed = False
    rth_active = False
    current_target_crumb_idx = 0
    sim_dist = 0.0

    window_name = "Scenario B: Autonomous Zero-Map Visual Breadcrumbs Engine"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        curr_kp, curr_desc, _ = matcher.extract_features(curr_gray)

        t_now = time.perf_counter()

        # In Outbound mode: automatically drop breadcrumbs every 2.5 seconds if moving
        if not rth_active and (t_now - last_breadcrumb_time) > 2.5 and len(breadcrumbs) < 20:
            if curr_desc is not None and len(curr_kp) >= 10:
                sim_dist += 45.0  # Simulated 45 meters forward
                breadcrumbs.append(
                    VisualBreadcrumb(
                        id=len(breadcrumbs),
                        image_gray=curr_gray,
                        keypoints=curr_kp,
                        descriptors=curr_desc,
                        timestamp=t_now,
                        simulated_x=sim_dist,
                        simulated_y=sim_dist * 0.3,
                    )
                )
                last_breadcrumb_time = t_now
                print(f"[BREADCRUMB] Dropped Visual Footprint #{len(breadcrumbs)-1} (Distance: {sim_dist:.0f}m)")

        # In RTH mode: Target the previous breadcrumbs in reverse order
        if rth_active:
            if current_target_crumb_idx < 0:
                current_target_crumb_idx = 0
            target_crumb = breadcrumbs[current_target_crumb_idx]
        else:
            # Normal mode: Compare with the most recent breadcrumb
            target_crumb = breadcrumbs[-1]

        # Match live camera with target breadcrumb
        inliers_count = 0
        inlier_ratio = 0.0
        good_matches = []
        inlier_matches = []
        guidance_text = "MAINTAINING OUTBOUND CRUISE"
        guidance_color = (200, 200, 200)

        if curr_desc is not None and target_crumb.descriptors is not None and len(curr_kp) >= 4:
            raw_knn = matcher.matcher.knnMatch(curr_desc, target_crumb.descriptors, k=2)
            good_matches = [m for m, n in raw_knn if len((m, n)) == 2 and m.distance < matcher.ratio_threshold * n.distance]

            if len(good_matches) >= 4:
                src_pts = np.float32([curr_kp[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([target_crumb.keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, matcher.ransac_reproj_threshold)
                if H is not None and mask is not None:
                    mask_flat = mask.ravel().tolist()
                    inlier_matches = [m for m, is_in in zip(good_matches, mask_flat) if is_in]
                    inliers_count = len(inlier_matches)
                    inlier_ratio = inliers_count / len(good_matches)

                    if rth_active:
                        if inliers_count >= 15:
                            guidance_text = f"LOCKED CRUMB #{target_crumb.id} -> STEPPING CLOSER TO HOME"
                            guidance_color = (0, 255, 0)
                            # If we matched crumb #N closely, advance to crumb #(N-1)
                            if current_target_crumb_idx > 0:
                                current_target_crumb_idx -= 1
                            else:
                                guidance_text = "TOUCHDOWN CONFIRMED: RETURNED TO EXACT HOME BASE!"
                                guidance_color = (0, 255, 0)
                        else:
                            guidance_text = f"SEARCHING CRUMB #{target_crumb.id} (STEER TOWARD PREVIOUS VIEW)"
                            guidance_color = (0, 165, 255)

        # ----------------- COCKPIT RENDER -----------------
        disp_h = 420
        # Left: Live Camera View
        cam_resized = cv2.resize(frame, (int(frame.shape[1] * (disp_h / frame.shape[0])), disp_h))

        # Right: Target Breadcrumb Image (Memory)
        crumb_bgr = cv2.cvtColor(target_crumb.image_gray, cv2.COLOR_GRAY2BGR)
        crumb_resized = cv2.resize(crumb_bgr, (int(crumb_bgr.shape[1] * (disp_h / crumb_bgr.shape[0])), disp_h))

        # Draw matches side by side
        vis = cv2.drawMatches(
            cam_resized,
            [cv2.KeyPoint(kp.pt[0] * (disp_h / frame.shape[0]), kp.pt[1] * (disp_h / frame.shape[0]), kp.size) for kp in curr_kp],
            crumb_resized,
            [cv2.KeyPoint(kp.pt[0] * (disp_h / crumb_bgr.shape[0]), kp.pt[1] * (disp_h / crumb_bgr.shape[0]), kp.size) for kp in target_crumb.keypoints],
            inlier_matches if len(inlier_matches) > 0 else good_matches[:20],
            None,
            matchColor=(0, 255, 0) if len(inlier_matches) >= 6 else (0, 140, 255),
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )

        # Telemetry HUD
        hud = np.zeros((70, vis.shape[1], 3), dtype=np.uint8)
        gps_stat = "GPS: JAMMED [0 SATS]" if jammed else "GPS: ACTIVE [14 SATS]"
        gps_col = (0, 0, 255) if jammed else (0, 255, 0)
        mode_stat = f"AUTONOMOUS RETURN (V-RTH to Crumb #{target_crumb.id})" if rth_active else "OUTBOUND FLIGHT (LOGGING BREADCRUMBS)"

        cv2.putText(hud, f"MISSION: {mode_stat}", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(hud, gps_stat, (15, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.55, gps_col, 2)

        cv2.putText(hud, f"BREADCRUMBS LOGGED: {len(breadcrumbs)} | ACTIVE TARGET: CRUMB #{target_crumb.id}", (480, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)
        cv2.putText(hud, f"OPTICAL INLIERS: {inliers_count} ({inlier_ratio*100:.1f}%) | {guidance_text}", (480, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.48, guidance_color, 2)

        final_frame = np.vstack([hud, vis])

        # Bottom Controls
        footer = np.zeros((30, final_frame.shape[1], 3), dtype=np.uint8)
        cv2.putText(footer, "Press [J] to Jam GPS | Press [R] to Engage Return-to-Home | [Q] to Exit", (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)
        final_frame = np.vstack([final_frame, footer])

        cv2.imshow(window_name, final_frame)

        key = cv2.waitKey(20) & 0xFF
        if key == ord("q") or key == 27:
            break
        elif key == ord("j") or key == ord("J"):
            jammed = not jammed
            print(f"[EVENT] GPS Jamming: {jammed}")
        elif key == ord("r") or key == ord("R"):
            rth_active = not rth_active
            if rth_active:
                current_target_crumb_idx = len(breadcrumbs) - 1
            print(f"[EVENT] Autonomous Visual Return-to-Home switched to: {rth_active}")

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Breadcrumb Engine closed.")


if __name__ == "__main__":
    run_breadcrumb_demo()
