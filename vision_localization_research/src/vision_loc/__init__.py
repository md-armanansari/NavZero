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

__version__ = "0.4.0"

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
]
