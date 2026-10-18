"""
vision_loc: Vision-Based Aerial Localization Research Package.
"""

from vision_loc.image_inspector import (
    ImageMetadata,
    inspect_image_metadata,
    load_image,
    visualize_image_pair,
)

__version__ = "0.2.0"

__all__ = [
    "ImageMetadata",
    "inspect_image_metadata",
    "load_image",
    "visualize_image_pair",
]
