"""
Image Inspection Module for Vision-Based Aerial Localization Research.

Provides safe loading, metadata extraction, validation, and side-by-side
visualization for aerial imagery without assuming or fabricating geographic coordinates.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


@dataclass(frozen=True)
class ImageMetadata:
    """Stores technical image properties without geographic assumptions."""
    file_path: Path
    file_exists: bool
    file_size_bytes: int
    width: int
    height: int
    channels: int
    dtype: str
    memory_usage_bytes: int
    aspect_ratio: float


def inspect_image_metadata(path: Path) -> ImageMetadata:
    """
    Safely inspects image file metadata and memory requirements.

    Args:
        path: Path to the image file.

    Returns:
        ImageMetadata dataclass instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If file is zero bytes, unsupported format, or unreadable.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Image file does not exist: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format '{ext}'. Supported formats: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    file_size = path.stat().st_size
    if file_size == 0:
        raise ValueError(f"Image file is empty (0 bytes): {path}")

    # Use cv2.imread to load and validate image integrity
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Corrupt, truncated, or unreadable image file: {path}")

    if img.ndim == 2:
        height, width = img.shape
        channels = 1
    elif img.ndim == 3:
        height, width, channels = img.shape
    else:
        raise ValueError(f"Unexpected image array dimension: {img.ndim}")

    if width == 0 or height == 0:
        raise ValueError(f"Invalid image dimensions: {width}x{height}")

    dtype_str = str(img.dtype)
    item_size = img.dtype.itemsize
    memory_usage = width * height * channels * item_size
    aspect_ratio = float(width) / float(height)

    return ImageMetadata(
        file_path=path,
        file_exists=True,
        file_size_bytes=file_size,
        width=width,
        height=height,
        channels=channels,
        dtype=dtype_str,
        memory_usage_bytes=memory_usage,
        aspect_ratio=round(aspect_ratio, 4),
    )


def load_image(path: Path, to_rgb: bool = True) -> Tuple[np.ndarray, ImageMetadata]:
    """
    Loads an image array and extracts its metadata safely.

    Args:
        path: Path to the image file.
        to_rgb: If True, converts standard OpenCV BGR images to RGB.

    Returns:
        Tuple of (numpy image array, ImageMetadata).
    """
    metadata = inspect_image_metadata(path)
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

    if img is None:
        raise ValueError(f"Failed to read image content from {path}")

    # Convert BGR to RGB for standard 3-channel images if requested
    if to_rgb and img.ndim == 3 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img, metadata


def visualize_image_pair(
    img_a: np.ndarray,
    label_a: str,
    img_b: np.ndarray,
    label_b: str,
    save_path: Optional[Path] = None,
    display_max_dim: Optional[int] = 800,
) -> plt.Figure:
    """
    Renders two images side-by-side using Matplotlib.

    Optional display_max_dim allows downscaling *only* for figure rendering
    to conserve memory without mutating the input data arrays.

    Args:
        img_a: First image array.
        label_a: Label for first image.
        img_b: Second image array.
        label_b: Label for second image.
        save_path: Optional path to save figure.
        display_max_dim: Max dimension for display figure rendering.

    Returns:
        Matplotlib Figure object.
    """
    def _prepare_for_display(img: np.ndarray) -> np.ndarray:
        if display_max_dim is None:
            return img
        h, w = img.shape[:2]
        max_dim = max(h, w)
        if max_dim <= display_max_dim:
            return img
        scale = display_max_dim / float(max_dim)
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    disp_a = _prepare_for_display(img_a)
    disp_b = _prepare_for_display(img_b)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    cmap_a = "gray" if disp_a.ndim == 2 else None
    cmap_b = "gray" if disp_b.ndim == 2 else None

    axes[0].imshow(disp_a, cmap=cmap_a)
    axes[0].set_title(f"{label_a}\n({img_a.shape[1]}x{img_a.shape[0]}, {disp_a.dtype})")
    axes[0].axis("on")

    axes[1].imshow(disp_b, cmap=cmap_b)
    axes[1].set_title(f"{label_b}\n({img_b.shape[1]}x{img_b.shape[0]}, {disp_b.dtype})")
    axes[1].axis("on")

    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(save_path), dpi=150, bbox_inches="tight")

    return fig
