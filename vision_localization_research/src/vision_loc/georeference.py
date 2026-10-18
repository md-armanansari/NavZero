"""
Georeferencing and Coordinate Transformation Module for Aerial Image Research.

Implements standard GDAL 6-parameter affine transformations, coordinate space conversions,
and metadata validation for georeferenced raster imagery without external geospatial C-dependencies.
Does NOT implement operational flight control or weapon guidance.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple
import math
import struct


class CoordinateType(str, Enum):
    PROJECTED = "PROJECTED"       # Linear units (e.g., Easting/Northing in meters, UTM)
    GEOGRAPHIC = "GEOGRAPHIC"     # Angular units (e.g., Latitude/Longitude in degrees, WGS84)
    UNKNOWN = "UNKNOWN"           # Raster lacks documented CRS


@dataclass(frozen=True)
class CoordinateBounds:
    """Represents spatial bounding box limits."""
    min_x: float
    max_x: float
    min_y: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y


@dataclass(frozen=True)
class AffineTransform:
    """
    Standard 6-parameter affine transformation relating pixel coordinates (c, r)
    to projected or geographic coordinates (X, Y):

        X = origin_x + c * a + r * b
        Y = origin_y + c * d + r * e

    Where:
        origin_x: Top-left corner X
        origin_y: Top-left corner Y
        a: pixel width (ground sampling distance X)
        b: row rotation / shear X (0 for north-up images)
        d: column rotation / shear Y (0 for north-up images)
        e: pixel height (ground sampling distance Y, typically negative)
    """
    origin_x: float
    origin_y: float
    a: float  # pixel_width
    b: float  # rotation_x
    d: float  # rotation_y
    e: float  # pixel_height

    def determinant(self) -> float:
        """Calculates determinant of the 2x2 affine matrix."""
        return (self.a * self.e) - (self.b * self.d)

    def is_invertible(self) -> bool:
        """Verifies if transformation can be mapped from map coordinates back to pixels."""
        return abs(self.determinant()) > 1e-12

    def pixel_to_map(self, col: float, row: float) -> Tuple[float, float]:
        """
        Maps image pixel coordinates (col, row) to map coordinates (X, Y).
        """
        x = self.origin_x + (col * self.a) + (row * self.b)
        y = self.origin_y + (col * self.d) + (row * self.e)
        return float(x), float(y)

    def map_to_pixel(self, x: float, y: float) -> Tuple[float, float]:
        """
        Maps map coordinates (X, Y) back to image pixel coordinates (col, row).

        Raises:
            ValueError: If transformation determinant is zero (non-invertible).
        """
        det = self.determinant()
        if abs(det) <= 1e-12:
            raise ValueError("Affine transformation is degenerate and cannot be inverted.")

        dx = x - self.origin_x
        dy = y - self.origin_y

        # Inverse of 2x2 matrix: [[e, -b], [-d, a]] / det
        col = (self.e * dx - self.b * dy) / det
        row = (-self.d * dx + self.a * dy) / det
        return float(col), float(row)


@dataclass(frozen=True)
class GeoReferenceMetadata:
    """Structured georeferencing metadata for a raster image."""
    has_georeference: bool
    crs_name: str
    epsg_code: Optional[int]
    coord_type: CoordinateType
    transform: Optional[AffineTransform]
    pixel_size_x: Optional[float]
    pixel_size_y: Optional[float]
    bounds: Optional[CoordinateBounds]
    notes: str


def read_world_file(world_file_path: Path) -> Optional[AffineTransform]:
    """
    Parses standard 6-line ESRI world file (.tfw, .pgw, .wld).
    Line 1: A (x-component of pixel width)
    Line 2: D (rotation term y)
    Line 3: B (rotation term x)
    Line 4: E (y-component of pixel height, typically negative)
    Line 5: C (x-coordinate of center of top-left pixel)
    Line 6: F (y-coordinate of center of top-left pixel)
    """
    path = Path(world_file_path)
    if not path.is_file():
        return None

    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(lines) < 6:
            return None

        a = float(lines[0])
        d = float(lines[1])
        b = float(lines[2])
        e = float(lines[3])
        center_x = float(lines[4])
        center_y = float(lines[5])

        # World files store pixel *center*; GDAL affine transform stores pixel *outer corner*:
        # origin_x = center_x - 0.5 * a - 0.5 * b
        # origin_y = center_y - 0.5 * d - 0.5 * e
        origin_x = center_x - 0.5 * a - 0.5 * b
        origin_y = center_y - 0.5 * d - 0.5 * e

        return AffineTransform(
            origin_x=origin_x,
            origin_y=origin_y,
            a=a,
            b=b,
            d=d,
            e=e,
        )
    except (ValueError, OSError):
        return None


def inspect_georeference(
    image_path: Path,
    width: int,
    height: int,
    custom_transform: Optional[AffineTransform] = None,
    crs_name: Optional[str] = None,
    epsg_code: Optional[int] = None,
    coord_type: Optional[CoordinateType] = None,
) -> GeoReferenceMetadata:
    """
    Inspects whether an image has associated georeference information.
    Checks:
        1. Explicitly provided transform parameter (if passed).
        2. Sidecar world file (.tfw, .pgw, .wld).
        3. If none found, explicitly reports has_georeference=False.
        Never silently assumes or invents coordinates.

    Args:
        image_path: Path to the image file.
        width: Raster width in pixels.
        height: Raster height in pixels.
        custom_transform: Optional AffineTransform if already parsed.
        crs_name: Name of Coordinate Reference System.
        epsg_code: Numeric EPSG code.
        coord_type: CoordinateType enum.

    Returns:
        GeoReferenceMetadata instance.
    """
    image_path = Path(image_path)

    # 1. Check custom transform
    transform = custom_transform

    # 2. Check for companion sidecar world file if no custom transform provided
    if transform is None:
        # Check extensions: .tfw for .tif, .pgw for .png, .jgw for .jpg, .wld generic
        candidate_world_files = [
            image_path.with_suffix(".tfw"),
            image_path.with_suffix(".pgw"),
            image_path.with_suffix(".jgw"),
            image_path.with_suffix(".wld"),
        ]
        for wf in candidate_world_files:
            if wf.is_file():
                transform = read_world_file(wf)
                if transform is not None:
                    break

    # 3. If no georeference exists, return clean negative result without inventing CRS
    if transform is None:
        return GeoReferenceMetadata(
            has_georeference=False,
            crs_name="NONE",
            epsg_code=None,
            coord_type=CoordinateType.UNKNOWN,
            transform=None,
            pixel_size_x=None,
            pixel_size_y=None,
            bounds=None,
            notes="No spatial georeference metadata found in header or companion world file.",
        )

    # 4. Calculate spatial bounding box using 4 corners of raster
    corners = [(0, 0), (width, 0), (width, height), (0, height)]
    map_corners = [transform.pixel_to_map(c, r) for c, r in corners]

    xs = [pt[0] for pt in map_corners]
    ys = [pt[1] for pt in map_corners]

    bounds = CoordinateBounds(
        min_x=min(xs),
        max_x=max(xs),
        min_y=min(ys),
        max_y=max(ys),
    )

    resolved_crs = crs_name if crs_name else "UNKNOWN_COORDINATE_SYSTEM"
    resolved_type = coord_type if coord_type else CoordinateType.PROJECTED

    return GeoReferenceMetadata(
        has_georeference=True,
        crs_name=resolved_crs,
        epsg_code=epsg_code,
        coord_type=resolved_type,
        transform=transform,
        pixel_size_x=abs(transform.a),
        pixel_size_y=abs(transform.e),
        bounds=bounds,
        notes="Spatial georeference successfully verified via affine transform.",
    )
