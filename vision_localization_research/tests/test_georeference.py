"""
Unit Tests for Georeference and Coordinate Transformation Module.
"""
from pathlib import Path
import pytest
import math

from vision_loc.georeference import (
    AffineTransform,
    CoordinateBounds,
    CoordinateType,
    GeoReferenceMetadata,
    inspect_georeference,
    read_world_file,
)


def test_affine_transform_forward_and_inverse_roundtrip():
    """
    Test that mapping from pixel -> map -> pixel matches within numerical tolerance (1e-6).
    Using synthetic projected coordinates (e.g., UTM meters with 0.5m GSD).
    """
    transform = AffineTransform(
        origin_x=500000.0,
        origin_y=4000000.0,
        a=0.5,      # 0.5 meters per pixel Easting
        b=0.0,
        d=0.0,
        e=-0.5,     # -0.5 meters per pixel Northing (standard negative y-resolution)
    )

    assert transform.is_invertible() is True
    assert transform.determinant() == pytest.approx(-0.25)

    test_cols = [0.0, 100.5, 512.0, 1024.0]
    test_rows = [0.0, 80.25, 512.0, 1024.0]

    for col, row in zip(test_cols, test_rows):
        map_x, map_y = transform.pixel_to_map(col, row)
        recon_col, recon_row = transform.map_to_pixel(map_x, map_y)

        assert recon_col == pytest.approx(col, abs=1e-6)
        assert recon_row == pytest.approx(row, abs=1e-6)


def test_affine_transform_with_rotation_roundtrip():
    """Test round-trip consistency on an affine transform with grid rotation/skew terms."""
    # 30-degree rotation synthetic transform
    theta = math.radians(30)
    scale = 1.0
    a = scale * math.cos(theta)
    b = -scale * math.sin(theta)
    d = scale * math.sin(theta)
    e = scale * math.cos(theta)

    transform = AffineTransform(
        origin_x=10000.0,
        origin_y=20000.0,
        a=a,
        b=b,
        d=d,
        e=e,
    )

    assert transform.is_invertible() is True
    col, row = 250.0, 175.0
    x, y = transform.pixel_to_map(col, row)
    r_col, r_row = transform.map_to_pixel(x, y)

    assert r_col == pytest.approx(col, abs=1e-6)
    assert r_row == pytest.approx(row, abs=1e-6)


def test_degenerate_affine_transform_raises_error():
    """Test that a non-invertible transform (determinant 0) raises ValueError on inversion."""
    degenerate = AffineTransform(
        origin_x=0.0,
        origin_y=0.0,
        a=0.0,
        b=0.0,
        d=0.0,
        e=0.0,
    )
    assert degenerate.is_invertible() is False
    with pytest.raises(ValueError, match="cannot be inverted"):
        degenerate.map_to_pixel(100.0, 200.0)


def test_missing_georeference_handled_explicitly(tmp_path: Path):
    """Test that an image without georeference returns has_georeference=False and does not invent CRS."""
    dummy_img = tmp_path / "plain_photo.png"
    dummy_img.write_bytes(b"dummy")

    meta = inspect_georeference(dummy_img, width=800, height=600)

    assert isinstance(meta, GeoReferenceMetadata)
    assert meta.has_georeference is False
    assert meta.crs_name == "NONE"
    assert meta.coord_type == CoordinateType.UNKNOWN
    assert meta.transform is None
    assert meta.bounds is None


def test_world_file_parsing(tmp_path: Path):
    """Test parsing standard 6-line ESRI world file (.tfw / .pgw)."""
    img_file = tmp_path / "ortho.tif"
    img_file.write_bytes(b"dummy_tiff")

    world_file = tmp_path / "ortho.tfw"
    # Standard world file:
    # Line 1: x pixel resolution (e.g. 0.25)
    # Line 2: rotation y (0.0)
    # Line 3: rotation x (0.0)
    # Line 4: y pixel resolution (-0.25)
    # Line 5: center of top-left pixel X (500000.125)
    # Line 6: center of top-left pixel Y (4000000.125)
    world_content = "0.25\n0.0\n0.0\n-0.25\n500000.125\n4000000.125\n"
    world_file.write_text(world_content)

    meta = inspect_georeference(
        image_path=img_file,
        width=1000,
        height=1000,
        crs_name="UTM Zone 43N",
        epsg_code=32643,
        coord_type=CoordinateType.PROJECTED,
    )

    assert meta.has_georeference is True
    assert meta.epsg_code == 32643
    assert meta.coord_type == CoordinateType.PROJECTED
    assert meta.pixel_size_x == pytest.approx(0.25)
    assert meta.pixel_size_y == pytest.approx(0.25)

    # Check bounds
    assert meta.bounds is not None
    # 1000 pixels * 0.25m = 250m extent
    assert meta.bounds.width == pytest.approx(250.0)
    assert meta.bounds.height == pytest.approx(250.0)
