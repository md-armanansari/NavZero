"""
High-resolution Tactical Satellite Map Generator for NavZero.
Generates a realistic terrain map with roads, rivers, ridges, and military outposts
if offline satellite imagery is not supplied.
"""
import cv2
import numpy as np

def generate_tactical_terrain(width=2000, height=2000, seed=42):
    """
    Creates realistic high-detail satellite-like terrain with Perlin-style noise,
    river networks, winding roads, elevation contours, and landmarks.
    """
    np.random.seed(seed)
    
    # 1. Base terrain elevation texture (mountainous Ladakh style)
    base = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Generate multi-scale noise for realistic rugged terrain
    low_res = cv2.resize(np.random.normal(120, 30, (height//16, width//16)).astype(np.float32), (width, height))
    mid_res = cv2.resize(np.random.normal(0, 15, (height//4, width//4)).astype(np.float32), (width, height))
    high_res = np.random.normal(0, 5, (height, width)).astype(np.float32)
    
    elevation = np.clip(low_res + mid_res + high_res, 30, 240)
    
    # Colorize: Browns, Tans, Greys of Himalayan rocky terrain
    r = np.clip(elevation * 1.1 + 10, 0, 255).astype(np.uint8)
    g = np.clip(elevation * 0.95 + 5, 0, 255).astype(np.uint8)
    b = np.clip(elevation * 0.75 - 10, 0, 255).astype(np.uint8)
    terrain = cv2.merge([b, g, r])

    # 2. Add River / Stream (dark bluish-gray winding path)
    river_points = []
    x = int(width * 0.2)
    for y in range(0, height, 40):
        x += int(np.sin(y * 0.015) * 25 + np.random.randint(-10, 10))
        x = max(50, min(width - 50, x))
        river_points.append([x, y])
    river_pts = np.array(river_points, np.int32).reshape((-1, 1, 2))
    cv2.polylines(terrain, [river_pts], isClosed=False, color=(90, 80, 50), thickness=16, lineType=cv2.LINE_AA)

    # 3. Add Mountain Strategic Road / Highway (dusty pale asphalt)
    road_points = []
    rx = int(width * 0.6)
    for ry in range(0, height, 50):
        rx += int(np.cos(ry * 0.01) * 35 + np.random.randint(-5, 5))
        rx = max(50, min(width - 50, rx))
        road_points.append([rx, ry])
    road_pts = np.array(road_points, np.int32).reshape((-1, 1, 2))
    cv2.polylines(terrain, [road_pts], isClosed=False, color=(140, 150, 160), thickness=8, lineType=cv2.LINE_AA)
    
    # Cross branch road
    cross_road = np.array([[road_points[len(road_points)//2][0], road_points[len(road_points)//2][1]], 
                           [width - 100, height // 3]], np.int32).reshape((-1, 1, 2))
    cv2.polylines(terrain, [cross_road], isClosed=False, color=(140, 150, 160), thickness=6, lineType=cv2.LINE_AA)

    # 4. Add Landmark Structures (Tactical bunkers, Helipads, Bridge)
    # Bridge over river
    mid_idx = len(river_points) // 2
    bx, by = river_points[mid_idx]
    cv2.rectangle(terrain, (bx - 20, by - 10), (bx + 20, by + 10), (180, 180, 190), -1)
    
    # Helipad circle
    cv2.circle(terrain, (int(width * 0.75), int(height * 0.4)), 30, (190, 190, 200), 4, lineType=cv2.LINE_AA)
    cv2.circle(terrain, (int(width * 0.75), int(height * 0.4)), 8, (210, 210, 220), -1)

    # 5. Add Natural Rock Formations and Ridge Details
    for _ in range(40):
        cx = np.random.randint(50, width - 50)
        cy = np.random.randint(50, height - 50)
        radius = np.random.randint(15, 60)
        color_offset = np.random.randint(-25, 25)
        color = (int(np.clip(100 + color_offset, 0, 255)), 
                 int(np.clip(110 + color_offset, 0, 255)), 
                 int(np.clip(130 + color_offset, 0, 255)))
        cv2.ellipse(terrain, (int(cx), int(cy)), (int(radius), int(radius//2)), int(np.random.randint(0, 180)), 0, 360, color, -1)

    return terrain
