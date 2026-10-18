"""
Unit Tests for Image Inspection Module.
"""
from pathlib import Path
import pytest
import numpy as np
import cv2

from vision_loc.image_inspector import (
    inspect_image_metadata,
    load_image,
    visualize_image_pair,
    ImageMetadata,
)


@pytest.fixture
def test_image_dir(tmp_path: Path) -> Path:
    """Creates a temporary directory with various synthetic test image fixtures."""
    img_dir = tmp_path / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    # 1. Valid Color PNG (120x80)
    color_img = np.zeros((80, 120, 3), dtype=np.uint8)
    color_img[:, :60] = [255, 0, 0]  # Red half in RGB
    color_img[:, 60:] = [0, 255, 0]  # Green half in RGB
    # Save using OpenCV BGR ordering
    cv2.imwrite(str(img_dir / "valid_color.png"), cv2.cvtColor(color_img, cv2.COLOR_RGB2BGR))

    # 2. Valid Grayscale JPEG (100x100)
    gray_img = np.linspace(0, 255, 10000, dtype=np.uint8).reshape((100, 100))
    cv2.imwrite(str(img_dir / "valid_gray.jpg"), gray_img)

    # 3. Valid Uncompressed TIFF (64x64)
    tiff_img = np.ones((64, 64, 3), dtype=np.uint8) * 128
    cv2.imwrite(str(img_dir / "valid.tiff"), tiff_img)

    # 4. Zero-byte empty file
    empty_file = img_dir / "empty.png"
    empty_file.write_bytes(b"")

    # 5. Corrupt file with valid image extension but invalid header bytes
    corrupt_file = img_dir / "corrupt.png"
    corrupt_file.write_bytes(b"NOT_AN_IMAGE_HEADER_DATA_12345")

    # 6. Unsupported extension
    unsupported_file = img_dir / "notes.txt"
    unsupported_file.write_text("plain text")

    return img_dir


def test_inspect_valid_color_png(test_image_dir: Path):
    """Test metadata extraction from a valid color PNG."""
    png_path = test_image_dir / "valid_color.png"
    meta = inspect_image_metadata(png_path)

    assert isinstance(meta, ImageMetadata)
    assert meta.file_exists is True
    assert meta.width == 120
    assert meta.height == 80
    assert meta.channels == 3
    assert meta.dtype == "uint8"
    assert meta.file_size_bytes > 0
    # Expected memory usage: 120 * 80 * 3 * 1 byte = 28,800 bytes
    assert meta.memory_usage_bytes == 120 * 80 * 3 * 1
    assert meta.aspect_ratio == round(120 / 80, 4)


def test_inspect_valid_grayscale_jpeg(test_image_dir: Path):
    """Test metadata extraction from a valid grayscale JPEG."""
    jpg_path = test_image_dir / "valid_gray.jpg"
    meta = inspect_image_metadata(jpg_path)

    assert meta.width == 100
    assert meta.height == 100
    assert meta.channels == 1
    assert meta.dtype == "uint8"
    assert meta.memory_usage_bytes == 100 * 100 * 1 * 1


def test_inspect_valid_tiff(test_image_dir: Path):
    """Test metadata extraction from a valid TIFF image."""
    tiff_path = test_image_dir / "valid.tiff"
    meta = inspect_image_metadata(tiff_path)

    assert meta.width == 64
    assert meta.height == 64
    assert meta.channels == 3


def test_load_image_preserves_rgb(test_image_dir: Path):
    """Test that load_image correctly converts OpenCV BGR to RGB by default."""
    png_path = test_image_dir / "valid_color.png"
    img, meta = load_image(png_path, to_rgb=True)

    assert img.shape == (80, 120, 3)
    # Left half was created as Red [255, 0, 0] in RGB
    assert img[40, 30, 0] == 255  # Red channel
    assert img[40, 30, 1] == 0    # Green channel
    assert img[40, 30, 2] == 0    # Blue channel


def test_missing_file_raises_filenotfound(test_image_dir: Path):
    """Test that querying a non-existent file raises FileNotFoundError."""
    non_existent = test_image_dir / "does_not_exist.png"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        inspect_image_metadata(non_existent)


def test_empty_file_raises_valueerror(test_image_dir: Path):
    """Test that an empty 0-byte file raises ValueError."""
    empty_path = test_image_dir / "empty.png"
    with pytest.raises(ValueError, match="empty \\(0 bytes\\)"):
        inspect_image_metadata(empty_path)


def test_corrupt_file_raises_valueerror(test_image_dir: Path):
    """Test that corrupt image bytes raise ValueError."""
    corrupt_path = test_image_dir / "corrupt.png"
    with pytest.raises(ValueError, match="Corrupt, truncated, or unreadable"):
        inspect_image_metadata(corrupt_path)


def test_unsupported_format_raises_valueerror(test_image_dir: Path):
    """Test that unsupported extensions raise ValueError."""
    unsupported_path = test_image_dir / "notes.txt"
    with pytest.raises(ValueError, match="Unsupported format"):
        inspect_image_metadata(unsupported_path)


def test_visualize_image_pair_does_not_mutate_data(tmp_path: Path):
    """Test side-by-side visualization without mutating original image arrays."""
    img_a = np.ones((1000, 1200, 3), dtype=np.uint8) * 50
    img_b = np.ones((800, 800), dtype=np.uint8) * 100

    orig_shape_a = img_a.shape
    orig_shape_b = img_b.shape

    out_file = tmp_path / "pair_visualization.png"
    fig = visualize_image_pair(
        img_a=img_a,
        label_a="Large Image A",
        img_b=img_b,
        label_b="Grayscale Image B",
        save_path=out_file,
        display_max_dim=400,  # Scaled down for rendering only
    )

    # Assert original arrays were NOT mutated in place
    assert img_a.shape == orig_shape_a
    assert img_b.shape == orig_shape_b
    assert out_file.exists()
    assert out_file.stat().st_size > 0
