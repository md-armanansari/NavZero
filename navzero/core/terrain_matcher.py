"""
NavZero Core Terrain Matching Engine.
Matches drone optical camera frames to satellite master map using
multi-scale visual feature matching and RANSAC homography.
"""
import cv2
import numpy as np

class TerrainMatcher:
    def __init__(self, satellite_map, geo_ref, method="SIFT"):
        """
        satellite_map: BGR image of the full mission area
        geo_ref: GeoReference instance
        method: "SIFT" (high accuracy) or "ORB" (ultra-fast for low-end CPUs)
        """
        self.satellite_map = satellite_map
        self.geo_ref = geo_ref
        self.method = method
        
        # Convert map to grayscale for matching
        self.sat_gray = cv2.cvtColor(satellite_map, cv2.COLOR_BGR2GRAY)
        
        # Initialize Feature Detector
        if method == "SIFT":
            self.detector = cv2.SIFT_create(nfeatures=2500)
            index_params = dict(algorithm=1, trees=5) # FLANN KDTree
            search_params = dict(checks=50)
            self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
        else: # ORB
            self.detector = cv2.ORB_create(nfeatures=2500)
            self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            
        # Precompute keypoints and descriptors of the satellite map (done once at boot)
        self.sat_kp, self.sat_des = self.detector.detectAndCompute(self.sat_gray, None)

    def match_frame(self, frame_bgr):
        """
        Processes a single camera frame from the drone.
        Returns:
            dict with:
                - success: bool
                - est_px, est_py: estimated drone position on satellite map
                - est_lat, est_lon: estimated GPS coordinates
                - confidence: float 0-100%
                - inlier_count: int
                - match_vis: visual image with matching points
        """
        frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        frame_h, frame_w = frame_gray.shape
        
        # 1. Detect frame features
        frame_kp, frame_des = self.detector.detectAndCompute(frame_gray, None)
        
        if frame_des is None or len(frame_kp) < 10 or self.sat_des is None:
            return {"success": False, "confidence": 0.0, "reason": "Insufficient features"}
            
        # 2. Match descriptors with ratio test (Lowe's ratio test)
        try:
            matches = self.matcher.knnMatch(frame_des, self.sat_des, k=2)
        except Exception:
            return {"success": False, "confidence": 0.0, "reason": "Matcher error"}
            
        good_matches = []
        for m_n in matches:
            if len(m_n) == 2:
                m, n = m_n
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)
                    
        # 3. Minimum inliers check for reliable pose estimation
        min_inliers = 10
        if len(good_matches) < min_inliers:
            return {
                "success": False, 
                "confidence": min(100.0, (len(good_matches) / min_inliers) * 40.0),
                "inlier_count": len(good_matches),
                "reason": "Low inliers"
            }
            
        # 4. Compute Homography via RANSAC
        src_pts = np.float32([frame_kp[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([self.sat_kp[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if H is None:
            return {"success": False, "confidence": 20.0, "inlier_count": len(good_matches), "reason": "RANSAC failed"}
            
        inliers_mask = mask.ravel().tolist()
        num_inliers = sum(inliers_mask)
        
        if num_inliers < 8:
            return {"success": False, "confidence": 30.0, "inlier_count": num_inliers, "reason": "RANSAC low inliers"}
            
        # 5. Project Drone Center Point (optical axis center) onto Satellite Map
        drone_center = np.array([[[frame_w / 2.0, frame_h / 2.0]]], dtype=np.float32)
        est_sat_pt = cv2.perspectiveTransform(drone_center, H)[0][0]
        est_px, est_py = float(est_sat_pt[0]), float(est_sat_pt[1])
        
        # 6. Convert Pixel to Lat/Lon
        est_lat, est_lon = self.geo_ref.pixel_to_latlon(est_px, est_py)
        
        # 7. Confidence Score (based on inlier count & distribution)
        confidence = min(99.4, 45.0 + (num_inliers * 1.8))
        
        # 8. Create Match Visualization
        draw_matches = [m for idx, m in enumerate(good_matches) if inliers_mask[idx]]
        # Take top 30 inliers for clean visual presentation
        draw_matches = sorted(draw_matches, key=lambda x: x.distance)[:30]
        vis_img = cv2.drawMatches(frame_bgr, frame_kp, self.satellite_map, self.sat_kp, draw_matches, None,
                                  flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
                                  matchColor=(0, 255, 0))
                                  
        return {
            "success": True,
            "est_px": est_px,
            "est_py": est_py,
            "est_lat": est_lat,
            "est_lon": est_lon,
            "confidence": confidence,
            "inlier_count": num_inliers,
            "match_vis": vis_img
        }
