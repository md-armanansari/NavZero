"""
vision_loc: Vision-Based Aerial Localization Research Package.
"""

from vision_loc.image_inspector import (
    ImageMetadata,
    inspect_image_metadata,
    load_image,
    visualize_image_pair,
)
from vision_loc.feature_matcher import (
    MatchMetrics,
    VisualFeatureMatcher,
)
from vision_loc.georeference import (
    AffineTransform,
    CoordinateBounds,
    CoordinateType,
    GeoReferenceMetadata,
    inspect_georeference,
    read_world_file,
)
from vision_loc.evaluation import (
    BenchmarkSummary,
    TrialResult,
    compute_summary_statistics,
    create_base_synthetic_landscape,
    evaluate_trial,
    export_results_to_csv,
    generate_benchmark_pairs,
)

__version__ = "0.5.0"

__all__ = [
    "ImageMetadata",
    "inspect_image_metadata",
    "load_image",
    "visualize_image_pair",
    "MatchMetrics",
    "VisualFeatureMatcher",
    "AffineTransform",
    "CoordinateBounds",
    "CoordinateType",
    "GeoReferenceMetadata",
    "inspect_georeference",
    "read_world_file",
    "BenchmarkSummary",
    "TrialResult",
    "compute_summary_statistics",
    "create_base_synthetic_landscape",
    "evaluate_trial",
    "export_results_to_csv",
    "generate_benchmark_pairs",
]
