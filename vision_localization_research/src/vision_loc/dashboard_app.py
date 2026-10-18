"""
VISION LOCALIZATION RESEARCH
Offline Computer Vision Evaluation Dashboard.

A scientific evaluation dashboard visualizing actual benchmark results,
reprojection error, latency, and failure cases without simulated military controls.
"""
from pathlib import Path
import sys

# Ensure src is in python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

import pandas as pd
import streamlit as st
from PIL import Image

from vision_loc.dashboard_data import filter_records, load_benchmark_records


# Configure Page
st.set_page_config(
    page_title="Vision Localization Research - Evaluation Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Research Theme with Restrained Accents)
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e6edf3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.82rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 600;
        color: #f0f6fc;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #8b949e;
        margin-top: 4px;
    }
    .disclaimer-box {
        background-color: #1c2128;
        border-left: 4px solid #f0883e;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 14px 0;
        font-size: 0.88rem;
        color: #c9d1d9;
    }
    .limitation-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


# Header
st.markdown("## 🔬 VISION LOCALIZATION RESEARCH")
st.caption("Offline Computer Vision Evaluation & Reproducible Benchmark Framework")

# Paths
csv_path = project_root / "experiments" / "benchmark_results.csv"
plots_path = project_root / "experiments" / "plots" / "evaluation_metrics_plot.png"

# Load actual data
if not csv_path.is_file():
    st.error(f"Benchmark results file not found at: `{csv_path}`. Run `scripts/run_benchmarks.py` first.")
    st.stop()

try:
    records = load_benchmark_records(csv_path)
except Exception as e:
    st.error(f"Error loading benchmark records: {e}")
    st.stop()

# Sidebar: Filters
st.sidebar.markdown("### 📊 Benchmark Filters")
categories = sorted(list({r.category for r in records}))
statuses = sorted(list({r.status for r in records}))

selected_cats = st.sidebar.multiselect("Filter by Category", categories, default=categories)
selected_stats = st.sidebar.multiselect("Filter by Status", statuses, default=statuses)

filtered_records = filter_records(records, selected_cats, selected_stats)

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ Dataset Origin")
st.sidebar.caption(
    "Benchmark trials are generated deterministically using synthetic multiscale landscape textures "
    "with controlled illumination, rotation, noise, and hard-negative cases."
)


# Section A: Research Overview
st.markdown("### A. Research Overview")

total_trials = len(records)
successful_matches = sum(1 for r in records if r.status == "SUCCESS")
failed_matches = total_trials - successful_matches
match_rate = (successful_matches / total_trials * 100.0) if total_trials > 0 else 0.0

latencies = [r.steady_state_latency_median_ms for r in records]
median_latency = pd.Series(latencies).median() if latencies else 0.0

rmse_values = [r.pixel_reprojection_rmse for r in records if r.pixel_reprojection_rmse is not None]
median_rmse = pd.Series(rmse_values).median() if rmse_values else 0.0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Trials</div>
        <div class="metric-value">{total_trials}</div>
        <div class="metric-sub">{successful_matches} Pass / {failed_matches} Fail</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Sample Match Rate</div>
        <div class="metric-value">{match_rate:.1f}%</div>
        <div class="metric-sub">5 of 7 Pairs Verified</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Median Steady Latency</div>
        <div class="metric-value">{median_latency:.1f} ms</div>
        <div class="metric-sub">5 Repetitions / Trial</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Median Reproj. RMSE</div>
        <div class="metric-value">{median_rmse:.2f} px</div>
        <div class="metric-sub">25 Checkpoints / Pair</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">CPU Hardware Target</div>
        <div class="metric-value">Intel / AMD</div>
        <div class="metric-sub">Zero GPU Requirement</div>
    </div>
    """, unsafe_allow_html=True)

# Synthetic-Data Disclaimer
st.markdown("""
<div class="disclaimer-box">
    <strong>Scientific Methodology Disclaimer:</strong><br>
    The match rates and reprojection errors reported here are measured strictly on a controlled synthetic 7-pair
    degradation benchmark. Pixel reprojection RMSE is measured on independent 25-point check grids.
    These figures demonstrate algorithm stability on synthetic rasters and do <strong>NOT</strong> establish
    real-world geodetic localization accuracy or operational GPS-denied navigation capability.
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# Section B: Experiment Results Table
st.markdown("### B. Experiment Results Table")

# Format records for display
table_data = []
for r in filtered_records:
    rmse_str = f"{r.pixel_reprojection_rmse:.2f}" if r.pixel_reprojection_rmse is not None else "N/A"
    grid_err_str = f"{r.synthetic_grid_error_m:.2f}" if r.synthetic_grid_error_m is not None else "N/A"
    table_data.append({
        "Trial ID": r.pair_id,
        "Category": r.category,
        "Status": r.status,
        "Keypoints (Q/R)": f"{r.keypoints_query} / {r.keypoints_ref}",
        "Inliers (RANSAC)": r.geometric_inliers,
        "Inlier Ratio": f"{r.inlier_ratio * 100:.1f}%",
        "Pixel RMSE (px)": rmse_str,
        "Synthetic Grid Err (m)": grid_err_str,
        "Latency (ms)": f"{r.steady_state_latency_median_ms:.1f} ± {r.steady_state_latency_std_ms:.1f}",
    })

df_display = pd.DataFrame(table_data)
st.dataframe(df_display, use_container_width=True, hide_index=True)

st.caption(f"Showing {len(filtered_records)} of {len(records)} benchmark trials. Failed trials retain N/A error values.")

st.markdown("---")


# Section C: Visual Correspondences
st.markdown("### C. Visual Feature Correspondences")
st.write(
    "Inlier matches establish visual correspondence between the query image and reference image. "
    "Image correspondence alone does not establish geographic localization without validated sensor scale and orientation."
)

if plots_path.is_file():
    st.image(str(plots_path), caption="Benchmark Performance Summary: Inlier Counts & Steady-State Latencies", use_container_width=True)
else:
    st.info("Benchmark summary plot not found. Run `scripts/run_benchmarks.py` to regenerate.")

st.markdown("---")


# Section D & E: Error Analysis and Performance Analysis
col_d, col_e = st.columns(2)

with col_d:
    st.markdown("### D. Geometric Error Analysis")
    st.write("Independent 25-point grid Root Mean Square Error (RMSE in pixels):")

    successful_trials = [r for r in records if r.pixel_reprojection_rmse is not None]
    if successful_trials:
        err_df = pd.DataFrame([
            {"Trial": r.pair_id.replace("pair_", ""), "RMSE (pixels)": r.pixel_reprojection_rmse}
            for r in successful_trials
        ])
        st.bar_chart(err_df.set_index("Trial"), color="#58a6ff")
        st.caption("Pixel RMSE across successful degradation scenarios. Note significant error growth under high glare.")
    else:
        st.write("No successful trials available for error analysis.")

with col_e:
    st.markdown("### E. Processing Latency Analysis")
    st.write("Steady-state latency measured across 5 repetitions per trial:")

    time_df = pd.DataFrame([
        {"Trial": r.pair_id.replace("pair_", ""), "Median Latency (ms)": r.steady_state_latency_median_ms}
        for r in records
    ])
    st.bar_chart(time_df.set_index("Trial"), color="#238636")
    st.caption("Offline benchmark CPU execution latency. Throughput represents batch execution, not demonstrated live camera FPS.")

st.markdown("---")


# Section F: Research Limitations
st.markdown("### F. Research Limitations & Future Work")

st.markdown("""
<div class="limitation-box">
    <ul>
        <li><strong>Controlled Synthetic Data Only:</strong> Benchmark imagery is synthetically generated; real-world aerial imagery contains non-planar topography, seasonal foliage changes, shadow shifts, and dynamic objects.</li>
        <li><strong>Sample Size Constraints:</strong> The benchmark currently evaluates 7 controlled test pairs. The 71.4% success rate and zero false-positive observation apply strictly to this sample set and cannot be generalized to unconstrained operational domains.</li>
        <li><strong>No Real-World Geodetic Validation:</strong> Synthetic grid-scaled metre values are linear scale demonstrations (GSD=0.5m/px) and do not represent validated GNSS-denied field positioning.</li>
        <li><strong>No Operational Flight Readiness:</strong> This prototype is an offline research tool. It has not been tested on flight hardware, autopilots (PX4/ArduPilot), or in electronic warfare (EW) environments.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
