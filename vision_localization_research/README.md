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

