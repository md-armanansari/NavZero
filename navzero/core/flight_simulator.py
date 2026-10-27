"""
Drone Flight and Electronic Warfare Jamming Simulator for NavZero.
Simulates drone camera optical capture, trajectory, and GPS jamming events.
"""
import cv2
import numpy as np

class DroneSimulator:
    def __init__(self, satellite_map, geo_ref, fov_size=380):
        self.satellite_map = satellite_map
        self.geo_ref = geo_ref
        self.fov_size = fov_size # Width/height of drone camera field of view in map pixels
        self.map_h, self.map_w = satellite_map.shape[:2]
        
        # Scale tactical waypoints smoothly to actual map dimensions with margin
        margin = max(fov_size // 2 + 20, 60)
        rel_pts = [
            (0.18, 0.22),
            (0.45, 0.60),
            (0.75, 0.70),
            (0.82, 0.35),
            (0.55, 0.18),
            (0.18, 0.22)
        ]
        self.waypoints = [
            (margin + rx * (self.map_w - 2 * margin), margin + ry * (self.map_h - 2 * margin))
            for rx, ry in rel_pts
        ]
        
        self.step_idx = 0
        self.total_steps = 200
        self.trajectory_points = self._generate_dense_trajectory()
        
    def _generate_dense_trajectory(self):
        """Generates smooth interpolated points connecting waypoints"""
        points = []
        num_segs = len(self.waypoints) - 1
        steps_per_seg = self.total_steps // num_segs
        
        for i in range(num_segs):
            p1 = np.array(self.waypoints[i])
            p2 = np.array(self.waypoints[i+1])
            for t in np.linspace(0, 1, steps_per_seg, endpoint=False):
                pt = (1 - t) * p1 + t * p2
                # Add slight crosswind drift
                pt[0] += np.sin(t * 10) * 8
                pt[1] += np.cos(t * 10) * 8
                points.append(pt)
        return points

    def get_frame(self, step):
        """
        Returns:
            - camera_frame: BGR image seen by the drone camera
            - true_px, true_py: True drone position in map pixels
            - true_lat, true_lon: Ground truth coordinates
        """
        idx = step % len(self.trajectory_points)
        cx, cy = self.trajectory_points[idx]
        
        half = self.fov_size // 2
        x1 = max(0, int(cx - half))
        y1 = max(0, int(cy - half))
        x2 = min(self.map_w, int(cx + half))
        y2 = min(self.map_h, int(cy + half))
        
        crop = self.satellite_map[y1:y2, x1:x2].copy()
        
        # If crop hits boundary, pad it
        if crop.shape[0] != self.fov_size or crop.shape[1] != self.fov_size:
            crop = cv2.resize(crop, (self.fov_size, self.fov_size))
            
        # Add slight atmospheric haze / optical noise
        noise = np.random.normal(0, 3, crop.shape).astype(np.float32)
        camera_frame = np.clip(crop.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        
        true_lat, true_lon = self.geo_ref.pixel_to_latlon(cx, cy)
        return camera_frame, (cx, cy), (true_lat, true_lon)
