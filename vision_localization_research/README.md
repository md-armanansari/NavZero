# Vision-Based Aerial Localization in GPS-Denied Environments (Research Prototype)

An offline computer vision research prototype investigating geographic coordinate estimation for aerial imagery by visual correspondence against georeferenced reference imagery.

## Research Objectives
- Visual feature detection and descriptor correspondence on aerial terrain.
- Image correspondence under scale, rotation, illumination, and quality variations.
- Pixel-to-coordinate georeferencing relationships.
- Error analysis, matching confidence, and false-positive / failed-match detection.
- Latency and CPU computational requirements on standard consumer hardware.

## Project Documentation
- [Research Report (Full Technical Specification)](docs/RESEARCH_REPORT.md)
- [Milestone Progress Tracker](PROGRESS.md)
- [Benchmark Results Table (CSV)](experiments/benchmark_results.csv)
- [Benchmark Summary Report](experiments/benchmark_report.md)

## Project Structure
```
vision_localization_research/
├── docs/
│   └── RESEARCH_REPORT.md  # Milestone 7 comprehensive research report
├── README.md               # Quickstart guide
├── PROGRESS.md             # Milestone tracking checklist
├── requirements.txt        # Pinned dependencies
├── pyproject.toml          # Build and test configuration
├── run_dashboard.bat       # One-click Windows dashboard launcher
├── run_benchmarks.bat      # One-click Windows benchmark runner
├── experiments/            # Benchmark CSV, plots, and markdown summaries
├── scripts/
│   └── run_benchmarks.py   # Automated reproducible benchmark runner
├── src/
│   └── vision_loc/         # Core research algorithms
│       ├── __init__.py
│       ├── image_inspector.py
│       ├── feature_matcher.py
│       ├── georeference.py
│       ├── evaluation.py
│       ├── dashboard_data.py
│       └── dashboard_app.py
└── tests/                  # 34 automated unit & integration tests
```

## Setup Instructions (Windows PowerShell)
```powershell
cd vision_localization_research
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -v
```

## Module Documentation

### Image Inspection (`vision_loc.image_inspector`)
Provides memory-safe inspection, format validation, and side-by-side visualization:
- `inspect_image_metadata(path)`: Returns `ImageMetadata` with file size, dimensions, channels, data type, and uncompressed memory footprint.
- `load_image(path, to_rgb=True)`: Loads array and converts BGR to RGB.
- `visualize_image_pair(img_a, label_a, img_b, label_b, save_path)`: Plots two images side-by-side without mutating source arrays.

### Visual Feature Matching (`vision_loc.feature_matcher`)
Provides CPU-efficient visual correspondence and outlier rejection:
- `VisualFeatureMatcher(max_features, ratio_threshold, ransac_reproj_threshold)`:
  - Extracts 256-bit binary ORB features.
  - Matches descriptors using bitwise Hamming distance.
  - Filters ambiguous matches using Lowe's ratio test ($d_1 < \text{ratio} \times d_2$).
  - Rejects geometric outliers using RANSAC homography.
  - Returns `MatchMetrics` (keypoint counts, tentative matches, inlier counts, inlier ratio, and detection/matching latency).
- `VisualFeatureMatcher.draw_matches_visualization(...)`: Renders visual correspondence lines between matching points.

### Georeferencing & Spatial Transformation (`vision_loc.georeference`)
Provides mathematical mapping between discrete image pixel indices and spatial coordinate grids:
- `AffineTransform(origin_x, origin_y, a, b, d, e)`:
  - Standard 6-parameter affine matrix relating $(c, r)$ to $(X, Y)$.
  - `pixel_to_map(col, row)`: Maps pixel indices to planar coordinates.
  - `map_to_pixel(x, y)`: Inverts planar coordinates back to pixel space with determinant checks.
- `inspect_georeference(image_path, width, height)`:
  - Validates companion world files (`.tfw`, `.pgw`, `.wld`).
  - Reports bounding box, resolution, and coordinate system type (`PROJECTED` vs `GEOGRAPHIC`).
  - Returns `has_georeference=False` if metadata is missing; never silently guesses a CRS.

### Research Evaluation & Benchmarking (`vision_loc.evaluation`)
Provides automated, reproducible experimental evaluation:
- Run benchmark suite via PowerShell:
  ```powershell
  .\.venv\Scripts\python.exe scripts\run_benchmarks.py
  ```
- Evaluates degradation categories: baseline translation, illumination (low-light, glare), rotation (20°), sensor noise, and hard negatives (uncorrelated noise, blank canvas).
- Methodology & Validation:
  - **Latency:** Uses 1 unrecorded warmup run followed by 5 steady-state timed repetitions per trial, reporting median and standard deviation.
  - **Geometric Accuracy:** Measured as Root Mean Square Error (RMSE in pixels) over an independent $5 \times 5$ grid of 25 checkpoints across the image (never reusing inlier points as ground truth).
  - **Geographic Scale:** Multiplies pixel RMSE by synthetic GSD (0.5m/px) strictly as a digital grid demonstration without claiming operational geodetic GPS-denied accuracy.
- Outputs:
  - `experiments/benchmark_results.csv`: Per-trial metrics, inliers, latency, and reprojection errors.
  - `experiments/benchmark_report.md`: Summary markdown report with scientific disclaimers.
  - `experiments/plots/evaluation_metrics_plot.png`: Diagnostic bar charts with latency error bars.

### Interactive Evaluation Dashboard (`vision_loc.dashboard_app`)
Local Streamlit research interface:
- Launch via PowerShell:
  ```powershell
  .\.venv\Scripts\streamlit.exe run src\vision_loc\dashboard_app.py --server.port 8502
  ```
  Or double-click `run_dashboard.bat`.
- Opens at: `http://localhost:8502`
- Sections:
  - **A. Research Overview:** Overall trials, pass/fail counts, median steady-state latency, median pixel RMSE.
  - **B. Experiment Results Table:** Filterable by category/status, preserving N/A values for failed trials.
  - **C. Visual Correspondences:** Explains inliers vs localization.
  - **D. Geometric Error Analysis:** Bar chart of independent pixel RMSE.
  - **E. Performance Analysis:** Steady-state latency per scenario.
  - **F. Research Limitations:** Documents synthetic boundaries and lack of operational testing.






