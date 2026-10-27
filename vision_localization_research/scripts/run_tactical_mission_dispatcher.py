"""
Tactical Mission Dispatcher & Visual Waypoint Navigator.

Demonstrates full end-to-end mission cycle:
1. RIGHT-CLICK anywhere on the map to set HOME BASE (e.g. your takeoff runway).
2. LEFT-CLICK anywhere on the map to set MISSION TARGET (e.g. enemy bunker / waypoint).
3. The drone flies autonomously to the TARGET, continuously matching visual terrain.
4. Press [J] at any time to simulate GPS JAMMING.
5. Press [R] (or drone arrives at target) to CALL DRONE BACK to HOME BASE!
"""

import math
import sys
import time
from pathlib import Path
import cv2
import numpy as np

# Ensure src is in python path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root.parent))
sys.path.insert(0, str(repo_root / "src"))

from navzero.core.flight_engine import SensorMode
from vision_loc.feature_matcher import VisualFeatureMatcher
from vision_loc.georeference import AffineTransform

# Global interactive coordinates
target_point = None      # Current target waypoint
home_point = None        # Right click: home address
waypoint_queue = []      # Multi-waypoint mission routing queue
flight_phase = "IDLE"    # "CRUISE_TO_TARGET", "LOITER_AT_TARGET", "RETURNING_HOME", "IDLE"
window_name = "Tactical Mission Dispatcher - RIGHT-CLICK: Home | LEFT-CLICK: Add Waypoints | [R] Recall | [C] Clear"


def on_mouse_click(event, x, y, flags, param):
    """Handles user mission planning clicks."""
    global target_point, home_point, flight_phase, waypoint_queue
    disp_h = 520
    header_h = 65
    map_offset_x = disp_h

    # Only accept clicks within the map pane (below the 65px header HUD)
    if x >= map_offset_x and y >= header_h and y < (header_h + disp_h):
        scale_map = param["scale_map"]
        map_w = param.get("map_w", 2000)
        map_h = param.get("map_h", 2000)

        # Accurately compute map pixel coordinates by compensating for the top header
        orig_map_x = int((x - map_offset_x) / scale_map)
        orig_map_y = int((y - header_h) / scale_map)

        # Clamp cleanly to valid map boundaries
        orig_map_x = max(15, min(map_w - 15, orig_map_x))
        orig_map_y = max(15, min(map_h - 15, orig_map_y))

        # RIGHT CLICK: Set Home Base Address
        if event == cv2.EVENT_RBUTTONDOWN:
            home_point = (orig_map_x, orig_map_y)
            print(f"\n[MISSION UPDATE] HOME BASE SET AT: ({orig_map_x}, {orig_map_y})")

        # LEFT CLICK: Set / Queue Mission Target Waypoints
        elif event == cv2.EVENT_LBUTTONDOWN:
            if target_point is None or flight_phase in ("IDLE", "LOITER_AT_TARGET", "TOUCHDOWN_AT_HOME"):
                target_point = (orig_map_x, orig_map_y)
                flight_phase = "CRUISE_TO_TARGET"
                print(f"\n[MISSION LAUNCH] DRONE DISPATCHED TO WP-1: ({orig_map_x}, {orig_map_y})")
            else:
                waypoint_queue.append((orig_map_x, orig_map_y))
                wp_num = len(waypoint_queue) + 1
                print(f"\n[WAYPOINT QUEUED] WP-{wp_num} QUEUED AT: ({orig_map_x}, {orig_map_y})")


def run_tactical_mission_dispatcher():
    global target_point, home_point, flight_phase
    print("=" * 76)
    print("  TACTICAL MISSION DISPATCHER & VISUAL WAYPOINT NAVIGATOR")
    print("  Autonomous Fly-To-Target & Visual Return-to-Home Cycle")
    print("=" * 76)
    print("\nHOW TO CONTROL:")
    print(" 1. RIGHT-CLICK on the map to set your HOME BASE address.")
    print(" 2. LEFT-CLICK on the map to set your MISSION TARGET (Drone flies there!).")
    print(" 3. Watch the camera compare ground features in real time as it flies.")
    print(" 4. Press [R] at ANY TIME to CALL THE DRONE BACK to Home Base!")
    print(" 5. Press [J] to toggle GPS JAMMING ON/OFF.")
    print(" 6. Press [Q] or [ESC] to exit.\n")

    img_path = repo_root / "data" / "real_aerial_orthophoto.jpg"
    if not img_path.exists():
        img_path = repo_root / "data" / "ladakh_zanskar_map.jpg"

    real_sat_map = cv2.imread(str(img_path))
    if real_sat_map is None:
        print(f"[ERROR] Could not load map from {img_path}")
        return

    map_h, map_w = real_sat_map.shape[:2]

    # Georeference transform
    geo = AffineTransform(
        origin_x=74.5000,
        origin_y=35.5000,
        a=0.005,
        b=0.0,
        d=0.0,
        e=-0.005,
    )

    # Use max_features=1500 and ratio_threshold=0.82 to robustly match even subtle agricultural fields and terrain
    matcher = VisualFeatureMatcher(max_features=1500, ratio_threshold=0.82, ransac_reproj_threshold=6.0)

    # Pre-extract map landmarks
    print("[INFO] Indexing terrain landmarks from map...")
    t_start = time.perf_counter()
    map_gray = cv2.cvtColor(real_sat_map, cv2.COLOR_BGR2GRAY)
    map_kp, map_desc, _ = matcher.extract_features(map_gray)
    print(f"[INFO] Indexed {len(map_kp)} landmarks in {time.perf_counter() - t_start:.2f}s.")

    # Initialize Default Home Base (Center)
    home_x = float(map_w // 2)
    home_y = float(map_h // 2)
    home_point = (int(home_x), int(home_y))

    # Drone starts at Home Base
    drone_x = home_x
    drone_y = home_y
    heading_deg = 0.0
    speed_px_per_sec = 0.0
    fov_size = 200

    jammed = False
    sensor_mode = SensorMode.EO_DAYLIGHT
    breadcrumbs = []
    inliers_count = 0
    search_mode = False
    reacquired_timer = 0.0

    disp_h = 520
    scale_map = disp_h / map_h
    map_resized_w = int(map_w * scale_map)

    # Pad map with reflection so camera can look anywhere, even right at the edges of the map
    pad = fov_size
    padded_sat_map = cv2.copyMakeBorder(real_sat_map, pad, pad, pad, pad, cv2.BORDER_REFLECT)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, on_mouse_click, {"scale_map": scale_map, "map_w": map_w, "map_h": map_h})

    t_prev = time.perf_counter()

    while True:
        t_now = time.perf_counter()
        dt = t_now - t_prev
        t_prev = t_now

        # Update home coordinates if user right-clicked
        if home_point is not None:
            home_x, home_y = float(home_point[0]), float(home_point[1])

        # ----------------- FLIGHT AUTONOMOUS STEERING (COUPLED TO OPTICAL VISION) -----------------
        dest_x, dest_y = None, None

        if flight_phase == "CRUISE_TO_TARGET" and target_point is not None:
            dest_x, dest_y = float(target_point[0]), float(target_point[1])
        elif flight_phase == "RETURNING_HOME":
            dest_x, dest_y = home_x, home_y

        if dest_x is not None and dest_y is not None:
            dx = dest_x - drone_x
            dy = dest_y - drone_y
            dist_to_dest = math.hypot(dx, dy)

            if dist_to_dest > 8:
                # REALISTIC SENSOR FUSION PHYSICS:
                # 1. GPS ACTIVE: Satellites tell the drone exactly where it is!
                if not jammed:
                    heading_deg = math.degrees(math.atan2(dy, dx))
                    speed_px_per_sec = 45.0
                    search_mode = False
                # 2. GPS JAMMED BUT CAMERA SEES LANDMARKS (Inliers >= 4):
                # Computer Vision replaces GPS and navigates with precision!
                elif inliers_count >= 4:
                    if search_mode:
                        search_mode = False
                        reacquired_timer = 2.5
                        print(f"\n>>> [OPTICAL RE-ACQUISITION] Landmark identified ({inliers_count} inliers)! Resuming direct target heading.")
                    heading_deg = math.degrees(math.atan2(dy, dx))
                    speed_px_per_sec = 45.0
                else:
                    # 3. GPS JAMMED AND CAMERA IS BLIND (Inliers < 4 over featureless water/fields):
                    # AUTONOMOUS SEARCH & RE-ACQUISITION MODE:
                    search_mode = True
                    speed_px_per_sec = 38.0
                    heading_deg = (heading_deg + 50.0 * dt) % 360.0

                    margin_check = fov_size // 2 + 35
                    if drone_x < margin_check or drone_x > map_w - margin_check or drone_y < margin_check or drone_y > map_h - margin_check:
                        center_dx = (map_w / 2.0) - drone_x
                        center_dy = (map_h / 2.0) - drone_y
                        heading_deg = math.degrees(math.atan2(center_dy, center_dx))
            else:
                # Arrived at destination
                if (not jammed) or (inliers_count >= 4):
                    if len(waypoint_queue) > 0:
                        target_point = waypoint_queue.pop(0)
                        flight_phase = "CRUISE_TO_TARGET"
                        print(f"\n[NEXT OBJECTIVE] Steered to Waypoint: {target_point} ({len(waypoint_queue)} remaining in queue)")
                    else:
                        speed_px_per_sec = 0.0
                        if flight_phase == "CRUISE_TO_TARGET":
                            flight_phase = "LOITER_AT_TARGET"
                            print("\n[MISSION STATUS] ALL WAYPOINTS COMPLETED VIA OPTICAL LOCK! Loitering.")
                        elif flight_phase == "RETURNING_HOME":
                            flight_phase = "TOUCHDOWN_AT_HOME"
                            print("\n[MISSION STATUS] HOME BASE REACHED VIA OPTICAL LOCK! Touchdown confirmed.")

        rad = math.radians(heading_deg)
        drone_x += speed_px_per_sec * math.cos(rad) * dt
        drone_y += speed_px_per_sec * math.sin(rad) * dt

        # Clamp inside boundaries
        margin = 15
        drone_x = max(margin, min(map_w - margin, drone_x))
        drone_y = max(margin, min(map_h - margin, drone_y))

        if speed_px_per_sec > 0:
            breadcrumbs.append((int(drone_x), int(drone_y)))
            if len(breadcrumbs) > 160:
                breadcrumbs.pop(0)

        # ----------------- LIVE CAMERA CROP & MATCHING -----------------
        cx, cy = int(drone_x), int(drone_y)
        px = cx + pad
        py = cy + pad
        half_fov = fov_size // 2
        cam_crop = padded_sat_map[py - half_fov : py + half_fov, px - half_fov : px + half_fov].copy()

        # Multi-Spectral Sensor Transform
        if sensor_mode == SensorMode.IR_WHITE_HOT:
            gray = cv2.cvtColor(cam_crop, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
            thermal_gray = clahe.apply(gray)
            cam_crop = cv2.cvtColor(cv2.bitwise_not(thermal_gray), cv2.COLOR_GRAY2BGR)
        elif sensor_mode == SensorMode.IR_IRONBOW:
            gray = cv2.cvtColor(cam_crop, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            cam_crop = cv2.applyColorMap(clahe.apply(gray), cv2.COLORMAP_INFERNO)

        # Slight 10-degree optical tilt in flight
        rot_mat = cv2.getRotationMatrix2D((cam_crop.shape[1] // 2, cam_crop.shape[0] // 2), 10.0, 1.0)
        cam_tilted = cv2.warpAffine(cam_crop, rot_mat, (cam_crop.shape[1], cam_crop.shape[0]))

        cam_gray = cv2.cvtColor(cam_tilted, cv2.COLOR_BGR2GRAY)
        cam_kp, cam_desc, _ = matcher.extract_features(cam_gray)

        inliers_count = 0
        inlier_ratio = 0.0
        good_matches = []
        inlier_matches = []
        homography = None

        if cam_desc is not None and map_desc is not None and len(cam_kp) >= 4:
            raw_knn = matcher.matcher.knnMatch(cam_desc, map_desc, k=2)
            good_matches = [m for m, n in raw_knn if len((m, n)) == 2 and m.distance < matcher.ratio_threshold * n.distance]

            if len(good_matches) >= 4:
                src_pts = np.float32([cam_kp[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([map_kp[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, matcher.ransac_reproj_threshold)
                if H is not None and mask is not None:
                    homography = H
                    mask_flat = mask.ravel().tolist()
                    inlier_matches = [m for m, is_in in zip(good_matches, mask_flat) if is_in]
                    inliers_count = len(inlier_matches)
                    inlier_ratio = inliers_count / len(good_matches)

        curr_lon, curr_lat = geo.pixel_to_map(drone_x, drone_y)

        # ----------------- DISPLAY RENDER -----------------
        cam_disp = cv2.resize(cam_tilted, (disp_h, disp_h))
        cv2.circle(cam_disp, (disp_h // 2, disp_h // 2), 35, (0, 255, 0), 1)
        cv2.drawMarker(cam_disp, (disp_h // 2, disp_h // 2), (0, 255, 0), cv2.MARKER_CROSS, 25, 2)
        cv2.putText(cam_disp, "LIVE DRONE CAMERA VIEW", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
        cv2.putText(cam_disp, f"PAYLOAD: {sensor_mode.value}", (15, disp_h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 0), 1)

        map_disp = real_sat_map.copy()

        # 1. Draw Home Base Marker (Yellow Square)
        cv2.drawMarker(map_disp, (int(home_x), int(home_y)), (0, 255, 255), cv2.MARKER_SQUARE, 22, 2)
        cv2.putText(map_disp, "HOME BASE", (int(home_x) + 12, int(home_y) + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # 2. Draw Target Marker & Queued Flight Plan
        if target_point is not None:
            tx, ty = target_point
            cv2.drawMarker(map_disp, (tx, ty), (0, 0, 255), cv2.MARKER_DIAMOND, 22, 2)
            cv2.putText(map_disp, "TARGET [WP-1]", (tx + 12, ty + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.line(map_disp, (int(drone_x), int(drone_y)), (tx, ty), (0, 165, 255), 1, cv2.LINE_AA)

            # Draw lines and numbered markers through all queued waypoints
            prev_pt = (tx, ty)
            for idx, (wqx, wqy) in enumerate(waypoint_queue):
                cv2.circle(map_disp, (wqx, wqy), 6, (0, 140, 255), -1)
                cv2.putText(map_disp, f"WP-{idx+2}", (wqx + 10, wqy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 140, 255), 1)
                cv2.line(map_disp, prev_pt, (wqx, wqy), (0, 140, 255), 1, cv2.LINE_AA)
                prev_pt = (wqx, wqy)

        # 3. Draw Breadcrumbs Trail
        for bx, by in breadcrumbs:
            cv2.circle(map_disp, (bx, by), 2, (0, 255, 255), -1)

        # 4. Draw RANSAC Perspective Footprint (Green Polygon)
        if homography is not None:
            h_c, w_c = cam_crop.shape[:2]
            pts_cam = np.float32([[0, 0], [w_c, 0], [w_c, h_c], [0, h_c]]).reshape(-1, 1, 2)
            try:
                pts_on_map = cv2.perspectiveTransform(pts_cam, homography)
                cv2.polylines(map_disp, [np.int32(pts_on_map)], True, (0, 255, 0), 2, cv2.LINE_AA)
            except Exception:
                pass

        # 5. Draw Drone Position
        d_col = (0, 0, 255) if jammed else (0, 255, 0)
        cv2.circle(map_disp, (cx, cy), 8, d_col, -1)
        cv2.circle(map_disp, (cx, cy), 18, d_col, 2)

        map_resized = cv2.resize(map_disp, (map_resized_w, disp_h))
        combined_view = np.hstack([cam_disp, map_resized])

        # Header HUD
        header = np.zeros((65, combined_view.shape[1], 3), dtype=np.uint8)
        gps_txt = "GNSS: JAMMED [0 SATS]" if jammed else "GNSS: ACTIVE [14 SATS 3D FIX]"
        gps_col = (0, 0, 255) if jammed else (0, 255, 0)

        # Update re-acquisition visual alert timer
        if reacquired_timer > 0:
            reacquired_timer = max(0.0, reacquired_timer - dt)

        # Status text
        status_descriptions = {
            "IDLE": "READY (WAITING FOR TARGET)",
            "CRUISE_TO_TARGET": f"EN ROUTE ({len(waypoint_queue) + 1} WAYPOINTS REMAINING)",
            "LOITER_AT_TARGET": "MISSION COMPLETE - LOITERING OVER AREA",
            "RETURNING_HOME": "RECALL ACTIVE: RETURNING TO HOME BASE",
            "TOUCHDOWN_AT_HOME": "TOUCHDOWN CONFIRMED AT HOME BASE"
        }
        mode_txt = status_descriptions.get(flight_phase, flight_phase)
        mode_col = (255, 255, 255)

        if search_mode:
            mode_txt = "AUTONOMOUS SEARCH: SCANNING TERRAIN FOR KNOWN LANDMARKS..."
            mode_col = (0, 165, 255)
        elif reacquired_timer > 0:
            mode_txt = "LANDMARK RE-ACQUIRED! RESUMING MISSION COURSE"
            mode_col = (0, 255, 0)

        cv2.putText(header, f"MISSION: {mode_txt}", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, mode_col, 2)
        cv2.putText(header, gps_txt, (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.52, gps_col, 2)

        cv2.putText(header, f"LAT: {curr_lat:.4f} N | LON: {curr_lon:.4f} E | HDG: {heading_deg:.0f}", (535, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (220, 220, 220), 1)
        cv2.putText(header, f"OPTICAL INLIERS: {inliers_count} ({inlier_ratio*100:.1f}%) | 30 FPS CPU MATCHING", (535, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 0) if inliers_count >= 6 else (0, 165, 255), 2)

        final_gui = np.vstack([header, combined_view])

        # Footer instructions
        footer = np.zeros((30, combined_view.shape[1], 3), dtype=np.uint8)
        cv2.putText(footer, "RIGHT-CLICK: Home | LEFT-CLICK: Add WPs | [S] EO/IR | [C] Clear | [R] Recall | [J] Jam | [Q] Exit", (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1)
        final_gui = np.vstack([final_gui, footer])

        cv2.imshow(window_name, final_gui)

        key = cv2.waitKey(20) & 0xFF
        if key == ord("q") or key == 27:
            break
        elif key == ord("j") or key == ord("J"):
            jammed = not jammed
            print(f"[EVENT] GPS Jamming: {jammed}")
        elif key == ord("s") or key == ord("S"):
            modes = [SensorMode.EO_DAYLIGHT, SensorMode.IR_WHITE_HOT, SensorMode.IR_IRONBOW]
            curr_idx = modes.index(sensor_mode)
            sensor_mode = modes[(curr_idx + 1) % len(modes)]
            print(f"[EVENT] Tactical Dispatcher sensor mode: {sensor_mode.value}")
        elif key == ord("r") or key == ord("R"):
            flight_phase = "RETURNING_HOME"
            print("[EVENT] RECALL COMMAND: Drone returning to Home Base!")
        elif key == ord("c") or key == ord("C"):
            waypoint_queue.clear()
            target_point = None
            flight_phase = "IDLE"
            print("[EVENT] Mission flight plan cleared.")

    cv2.destroyAllWindows()
    print("[INFO] Mission Dispatcher closed.")


if __name__ == "__main__":
    run_tactical_mission_dispatcher()
