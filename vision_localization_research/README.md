# Vision-Based Aerial Localization in GPS-Denied Environments (Research Prototype)

An offline computer vision research prototype investigating geographic coordinate estimation for aerial imagery by visual correspondence against georeferenced reference imagery.

## Research Objectives
- Visual feature detection and descriptor correspondence on aerial terrain.
- Image correspondence under scale, rotation, illumination, and quality variations.
- Pixel-to-coordinate georeferencing relationships.
- Error analysis, matching confidence, and false-positive / failed-match detection.
- Latency and CPU computational requirements on standard consumer hardware.

## Project Structure
```
vision_localization_research/
├── README.md               # Research documentation
├── PROGRESS.md             # Milestone tracking checklist
├── requirements.txt        # Pinned dependencies
├── data/                   # Licensed sample aerial and reference imagery
│   ├── reference/          # Georeferenced aerial orthoimagery
│   └── query/              # Target query aerial frames
├── src/
│   └── vision_loc/         # Core research algorithms
│       └── __init__.py
└── tests/                  # Unit and integration test suite
    └── test_foundation.py
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



