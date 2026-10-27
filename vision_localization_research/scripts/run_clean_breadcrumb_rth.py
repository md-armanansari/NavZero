"""
Scenario B (Clean Teach-and-Repeat): Zero-Map Autonomous Return-to-Home.

1. OUTBOUND PHASE (Teach Mode):
   - Only captures the visual trail quietly into onboard memory.
   - Shows clean single-camera view without confusing comparison lines.
   - Drops a visual breadcrumb (frozen keyframe + 256-bit hashes) every 1.5 seconds.
   - Shows thumbnail gallery of stored footprints at the bottom.

2. INBOUND PHASE (Repeat / Return-to-Home Mode):
   - Triggered by pressing [R] (or [J] for GPS loss).
   - Screen splits into Dual-View: Live Camera (Left) vs Stored Path Footprints (Right).
   - Re-matches each stored footprint one-by-one in reverse order (#N -> #N-1 ... -> #0).
   - Holds each verified lock for 1.5 seconds so judges clearly see the step-by-step retreat.
   - You can also press [SPACE] to manually step through stored images one-by-one!
"""

import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List
import cv2
import numpy as np

# Ensure src is in python path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from vision_loc.feature_matcher import VisualFeatureMatcher


@dataclass
class VisualBreadcrumb:
    id: int
    image_gray: np.ndarray
    keypoints: List[cv2.KeyPoint]
    descriptors: np.ndarray
    timestamp: float


def run_clean_breadcrumb_demo():
    print("=" * 74)
    print("  SCENARIO B: CLEAN TEACH-AND-REPEAT VISUAL BREADCRUMBS (V-RTH)")
    print("  Phase 1: Record trail quietly -> Phase 2: Compare ONE-BY-ONE in reverse")
    print("=" * 74)
    print("\nHOW IT WORKS:")
    print(" 1. Point webcam at starting spot (Home Base). It locks Crumb #0.")
    print(" 2. Slowly pan camera across your desk/room. It logs footprints every 1.5s.")
    print(" 3. Press [R] (or [J]): Watch the system match each stored image ONE-BY-ONE!")
    print(" 4. Press [SPACE] to manually step to the next stored breadcrumb.")
    print(" 5. Press [Q] or [ESC] to exit.\n")

    matcher = VisualFeatureMatcher(max_features=600, ratio_threshold=0.75, ransac_reproj_threshold=5.0)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam index 0.")
        return

    # Warmup
    ret, frame = cap.read()
    if not ret or frame is None:
        print("[ERROR] Camera frame capture failed.")
        cap.release()
        return

    # Capture Takeoff Base (Frame 0)
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
        )
    )

    print("[INFO] HOME_BASE (Takeoff Point) established as Crumb #0!")

    last_breadcrumb_time = time.perf_counter()
    flash_crumb_id = 0
    flash_timer = 1.0
    jammed = False
    rth_active = False
    current_target_crumb_idx = 0
    step_dwell_timer = 0.0  # Holds visual lock for 1.8 seconds so user can see it!

    window_name = "Scenario B: Visual Teach-and-Repeat (V-RTH)"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    t_prev = time.perf_counter()

    while True:
        t_now = time.perf_counter()
        dt = t_now - t_prev
        t_prev = t_now

        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        curr_kp, curr_desc, _ = matcher.extract_features(curr_gray)

        if flash_timer > 0:
            flash_timer = max(0.0, flash_timer - dt)

        # ----------------- PHASE 1: OUTBOUND FLIGHT (RECORD TRAIL) -----------------
        if not rth_active:
            # Drop breadcrumb every 1.5 seconds for quick responsive logging
            if (t_now - last_breadcrumb_time) > 1.5 and len(breadcrumbs) < 20:
                if curr_desc is not None and len(curr_kp) >= 10:
                    new_crumb = VisualBreadcrumb(
                        id=len(breadcrumbs),
                        image_gray=curr_gray,
                        keypoints=curr_kp,
                        descriptors=curr_desc,
                        timestamp=t_now,
                    )
                    breadcrumbs.append(new_crumb)
                    last_breadcrumb_time = t_now
                    flash_crumb_id = new_crumb.id
                    flash_timer = 1.0
                    print(f"[OUTBOUND] Stored Footprint #{new_crumb.id} in memory bank.")

            disp_h = 440
            scale = disp_h / frame.shape[0]
            disp_w = int(frame.shape[1] * scale)
            live_disp = cv2.resize(frame, (disp_w, disp_h))

            # HUD Crosshair
            ch_x, ch_y = disp_w // 2, disp_h // 2
            cv2.drawMarker(live_disp, (ch_x, ch_y), (0, 255, 0), cv2.MARKER_CROSS, 30, 2)
            cv2.circle(live_disp, (ch_x, ch_y), 40, (0, 255, 0), 1)

            # Flash notification banner when a new crumb is dropped
            if flash_timer > 0:
                cv2.rectangle(live_disp, (10, disp_h - 60), (disp_w - 10, disp_h - 15), (0, 100, 0), -1)
                cv2.putText(
                    live_disp,
                    f">>> FOOTPRINT #{flash_crumb_id} LOGGED INTO ONBOARD RAM <<<",
                    (25, disp_h - 26),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.62,
                    (0, 255, 255),
                    2,
                )

            # Top Header
            header = np.zeros((65, disp_w, 3), dtype=np.uint8)
            gps_txt = "GPS: JAMMED [0 SATS]" if jammed else "GPS: ACTIVE [14 SATS]"
            gps_col = (0, 0, 255) if jammed else (0, 255, 0)

            cv2.putText(header, "PHASE 1: OUTBOUND FLIGHT (RECORDING TRAIL)", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
            cv2.putText(header, gps_txt, (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.52, gps_col, 2)

            cv2.putText(
                header,
                f"STORED MEMORY: {len(breadcrumbs)} FOOTPRINTS | READY TO RETURN",
                (disp_w - 530, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (0, 255, 0),
                2,
            )

            # Thumbnail Filmstrip of Stored Breadcrumbs
            strip_h = 70
            filmstrip = np.zeros((strip_h, disp_w, 3), dtype=np.uint8)
            thumb_w = 60
            for i, b in enumerate(breadcrumbs[:12]):
                tx = 15 + i * (thumb_w + 10)
                if tx + thumb_w < disp_w - 10:
                    t_bgr = cv2.cvtColor(b.image_gray, cv2.COLOR_GRAY2BGR)
                    t_res = cv2.resize(t_bgr, (thumb_w, strip_h - 20))
                    filmstrip[15 : 15 + t_res.shape[0], tx : tx + thumb_w] = t_res
                    cv2.rectangle(filmstrip, (tx, 15), (tx + thumb_w, 15 + t_res.shape[0]), (100, 100, 100), 1)
                    cv2.putText(filmstrip, f"#{b.id}", (tx + 5, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)

            # Bottom Footer
            footer = np.zeros((32, disp_w, 3), dtype=np.uint8)
            cv2.putText(footer, "Move camera to log path | Press [R] to Return-to-Home | [J] Jam GPS | [Q] Exit", (15, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

            final_gui = np.vstack([header, live_disp, filmstrip, footer])

        # ----------------- PHASE 2: RETURN-TO-HOME (COMPARE ONE-BY-ONE) -----------------
        else:
            if current_target_crumb_idx < 0:
                current_target_crumb_idx = 0
            target_crumb = breadcrumbs[current_target_crumb_idx]

            inliers_count = 0
            inlier_ratio = 0.0
            good_matches = []
            inlier_matches = []

            # Step dwell countdown
            if step_dwell_timer > 0:
                step_dwell_timer = max(0.0, step_dwell_timer - dt)
                if step_dwell_timer == 0.0:
                    # Time to step to the next older breadcrumb!
                    if current_target_crumb_idx > 0:
                        current_target_crumb_idx -= 1
                        target_crumb = breadcrumbs[current_target_crumb_idx]
                        print(f"[V-RTH] Advanced to earlier waypoint: Crumb #{current_target_crumb_idx}")

            guidance_text = f"SEARCHING CRUMB #{target_crumb.id}..."
            guidance_color = (0, 165, 255)

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

                        # Match lock threshold
                        if inliers_count >= 10:
                            if current_target_crumb_idx > 0:
                                if step_dwell_timer <= 0.0:
                                    step_dwell_timer = 1.8  # Hold on screen for 1.8s so user sees the match!
                                guidance_text = f"LOCKED CRUMB #{target_crumb.id}! ADVANCING TO #{current_target_crumb_idx - 1} IN {step_dwell_timer:.1f}s"
                                guidance_color = (0, 255, 0)
                            else:
                                guidance_text = "TOUCHDOWN CONFIRMED: RETURNED TO EXACT HOME BASE!"
                                guidance_color = (0, 255, 0)

            disp_h = 380
            cam_resized = cv2.resize(frame, (int(frame.shape[1] * (disp_h / frame.shape[0])), disp_h))
            crumb_bgr = cv2.cvtColor(target_crumb.image_gray, cv2.COLOR_GRAY2BGR)
            crumb_resized = cv2.resize(crumb_bgr, (int(crumb_bgr.shape[1] * (disp_h / crumb_bgr.shape[0])), disp_h))

            # Match side-by-side during Return
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

            # Labels on the two panes
            cv2.putText(vis, "LIVE DRONE CAMERA", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
            cv2.putText(vis, f"STORED MEMORY: CRUMB #{target_crumb.id}", (cam_resized.shape[1] + 15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

            # Top Header
            header = np.zeros((65, vis.shape[1], 3), dtype=np.uint8)
            cv2.putText(
                header,
                f"PHASE 2: AUTONOMOUS RETURN (RETRACING TO CRUMB #{target_crumb.id})",
                (15, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                header,
                f"ACTIVE TARGET: #{target_crumb.id} OF {len(breadcrumbs)-1} | INLIERS: {inliers_count} ({inlier_ratio*100:.1f}%)",
                (15, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (0, 255, 0) if inliers_count >= 8 else (0, 165, 255),
                2,
            )

            cv2.putText(header, guidance_text, (vis.shape[1] - 560, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.52, guidance_color, 2)

            # Thumbnail Filmstrip with Active Crumb Highlighted
            strip_h = 70
            filmstrip = np.zeros((strip_h, vis.shape[1], 3), dtype=np.uint8)
            thumb_w = 60
            for i, b in enumerate(breadcrumbs[:12]):
                tx = 15 + i * (thumb_w + 10)
                if tx + thumb_w < vis.shape[1] - 10:
                    t_bgr = cv2.cvtColor(b.image_gray, cv2.COLOR_GRAY2BGR)
                    t_res = cv2.resize(t_bgr, (thumb_w, strip_h - 20))
                    filmstrip[15 : 15 + t_res.shape[0], tx : tx + thumb_w] = t_res
                    if b.id == target_crumb.id:
                        # Highlight active comparison target in bold yellow!
                        cv2.rectangle(filmstrip, (tx - 2, 13), (tx + thumb_w + 2, 17 + t_res.shape[0]), (0, 255, 255), 2)
                        cv2.putText(filmstrip, f"#{b.id}*", (tx + 5, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 255), 2)
                    else:
                        cv2.rectangle(filmstrip, (tx, 15), (tx + thumb_w, 15 + t_res.shape[0]), (80, 80, 80), 1)
                        cv2.putText(filmstrip, f"#{b.id}", (tx + 5, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1)

            footer = np.zeros((32, vis.shape[1], 3), dtype=np.uint8)
            cv2.putText(footer, "[SPACE]: Step to Previous Crumb | [R]: Toggle Cruise | [Q]: Exit", (15, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

            final_gui = np.vstack([header, vis, filmstrip, footer])

        cv2.imshow(window_name, final_gui)

        key = cv2.waitKey(20) & 0xFF
        if key == ord("q") or key == 27:
            break
        elif key == ord("j") or key == ord("J"):
            jammed = not jammed
            print(f"[EVENT] GPS Jammed toggle: {jammed}")
            if jammed and not rth_active:
                rth_active = True
                current_target_crumb_idx = max(0, len(breadcrumbs) - 1)
                step_dwell_timer = 0.0
                print(f"[EVENT] LOST GPS: Auto-engaging Return-to-Home! Target Crumb #{current_target_crumb_idx}")
        elif key == ord("r") or key == ord("R"):
            rth_active = not rth_active
            if rth_active:
                current_target_crumb_idx = max(0, len(breadcrumbs) - 1)
                step_dwell_timer = 0.0
                print(f"[EVENT] RETURN-TO-HOME ENGAGED! Retracing from Crumb #{current_target_crumb_idx} back to Home Base!")
            else:
                print("[EVENT] Returned to manual outbound cruise.")
        elif key == 32:  # SPACEBAR: Manually step to previous breadcrumb!
            if rth_active and current_target_crumb_idx > 0:
                current_target_crumb_idx -= 1
                step_dwell_timer = 0.0
                print(f"[MANUAL STEP] User advanced to Crumb #{current_target_crumb_idx}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_clean_breadcrumb_demo()
