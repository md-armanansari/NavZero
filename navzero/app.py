import streamlit as st
import cv2
import numpy as np

from core.geo_utils import GeoReference
from core.map_generator import generate_tactical_terrain
from core.terrain_matcher import TerrainMatcher
from core.flight_simulator import DroneSimulator

# Simple, clean, human-made UI
st.set_page_config(page_title="Vision-Based Drone Navigation (GPS-Denied)", layout="wide")

st.title("Vision-Based GPS-Denied Drone Navigation")
st.write(
    "A computer vision prototype that estimates drone coordinates using visual terrain matching "
    "when GPS signal is lost or jammed."
)

# Load core modules
@st.cache_resource
def init_system():
    geo_ref = GeoReference()
    sat_map = generate_tactical_terrain(1600, 1600, seed=42)
    sim = DroneSimulator(sat_map, geo_ref, fov_size=320)
    matcher = TerrainMatcher(sat_map, geo_ref, method="SIFT")
    return geo_ref, sat_map, sim, matcher

geo_ref, sat_map, sim, matcher = init_system()

# Simple Sidebar Controls
st.sidebar.header("Simulation Settings")
step = st.sidebar.slider("Drone Flight Step", min_value=0, max_value=150, value=20)
jam_gps = st.sidebar.checkbox("Simulate GPS Jamming / Blackout", value=False)

st.sidebar.markdown("---")
st.sidebar.write("**How this demo works:**")
st.sidebar.write("1. Drone camera captures ground terrain.")
st.sidebar.write("2. OpenCV extracts visual landmarks (SIFT keypoints).")
st.sidebar.write("3. Compares landmarks to saved satellite map.")
st.sidebar.write("4. Calculates Lat/Lon even if GPS fails.")

# Get camera frame at current step
cam_frame, (true_px, true_py), (true_lat, true_lon) = sim.get_frame(step)

# Run OpenCV terrain matcher
result = matcher.match_frame(cam_frame)

# Display Status Banner
if jam_gps:
    st.error("⚠️ GPS Status: JAMMED / NO SIGNAL — Falling back to Camera Vision Navigation")
else:
    st.success("✅ GPS Status: CONNECTED [14 SATS 3D FIX] — Normal satellite navigation active")

# Two-column layout: Camera view and Map view
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Drone Camera View (Down-Facing)")
    
    # Simple crosshair overlay
    display_frame = cam_frame.copy()
    h, w = display_frame.shape[:2]
    cv2.circle(display_frame, (w // 2, h // 2), 20, (0, 255, 0), 2)
    cv2.line(display_frame, (w // 2 - 30, h // 2), (w // 2 + 30, h // 2), (0, 255, 0), 1)
    cv2.line(display_frame, (w // 2, h // 2 - 30), (w // 2, h // 2 + 30), (0, 255, 0), 1)
    
    st.image(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB), caption="Live optical feed from drone", use_container_width=True)

with col2:
    st.subheader("2. Satellite Reference Map & Position Tracker")
    
    map_view = sat_map.copy()
    
    # Draw flight path taken
    for i in range(1, len(sim.trajectory_points)):
        pt1 = tuple(sim.trajectory_points[i-1].astype(int))
        pt2 = tuple(sim.trajectory_points[i].astype(int))
        cv2.line(map_view, pt1, pt2, (100, 100, 100), 1)
        
    # Draw drone position on map
    if jam_gps:
        # GPS is dead, show estimated position from camera
        if result["success"]:
            ex, ey = int(result["est_px"]), int(result["est_py"])
            cv2.circle(map_view, (ex, ey), 18, (255, 255, 0), 3) # Cyan circle for Vision Fix
            cv2.putText(map_view, "Drone (Vision Fix)", (ex + 25, ey), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    else:
        # GPS is working normally
        cv2.circle(map_view, (int(true_px), int(true_py)), 18, (0, 255, 0), 3) # Green circle for GPS Fix
        cv2.putText(map_view, "Drone (GPS Fix)", (int(true_px) + 25, int(true_py)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Crop map view around the drone so it's easy to see
    crop_size = 350
    cx = max(crop_size, min(1600 - crop_size, int(true_px)))
    cy = max(crop_size, min(1600 - crop_size, int(true_py)))
    cropped_map = map_view[cy - crop_size : cy + crop_size, cx - crop_size : cx + crop_size]
    
    st.image(cv2.cvtColor(cropped_map, cv2.COLOR_BGR2RGB), caption="Satellite map with estimated position", use_container_width=True)

# Simple, readable data table
st.subheader("Coordinates & Accuracy Comparison")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**True Location (Ground Truth):**")
    st.write(f"Latitude: `{true_lat:.5f}° N`")
    st.write(f"Longitude: `{true_lon:.5f}° E`")

with c2:
    st.markdown("**GPS Receiver Output:**")
    if jam_gps:
        st.write("Latitude: `None (Signal Lost)`")
        st.write("Longitude: `None (Signal Lost)`")
    else:
        st.write(f"Latitude: `{true_lat:.5f}° N`")
        st.write(f"Longitude: `{true_lon:.5f}° E`")

with c3:
    st.markdown("**Our Vision Algorithm Output:**")
    if result["success"]:
        est_lat = result["est_lat"]
        est_lon = result["est_lon"]
        err_px = np.sqrt((result["est_px"] - true_px)**2 + (result["est_py"] - true_py)**2)
        err_meters = err_px * 7.5
        
        st.write(f"Latitude: `{est_lat:.5f}° N`")
        st.write(f"Longitude: `{est_lon:.5f}° E`")
        st.write(f"Estimated Error: `{err_meters:.1f} meters`")
    else:
        st.write("Status: `Searching for landmark matches...`")

# Feature Matches Explanation
with st.expander("Show OpenCV Feature Matching (SIFT + RANSAC)"):
    st.write("This shows the actual keypoints matched between the drone camera frame (left) and the satellite map (right):")
    if result.get("match_vis") is not None:
        vis = cv2.resize(result["match_vis"], (1000, 400))
        st.image(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB), use_container_width=True)
