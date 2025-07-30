"""
Image processing utilities for GIMP MCP Server

This module provides utilities for image validation, color handling,
and coordinate/dimension validation for GIMP operations.
"""

import re
import logging
from typing import Tuple, Dict, Any, Optional, Union, List

from .errors import GimpValidationError

logger = logging.getLogger(__name__)


def validate_color(color: str) -> bool:
    """
    Validate color string format.
    
    Args:
        color: Color string (hex, rgb, rgba, or named color)
        
    Returns:
        True if color format is valid
    """
    if not isinstance(color, str):
        return False
    
    color = color.strip().lower()
    
    # Hex color validation
    if color.startswith('#'):
        hex_pattern = r'^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$'
        return bool(re.match(hex_pattern, color))
    
    # RGB/RGBA validation
    rgb_pattern = r'^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)$'
    rgb_match = re.match(rgb_pattern, color)
    if rgb_match:
        r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
        alpha = float(rgb_match.group(4)) if rgb_match.group(4) else 1.0
        return 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0 <= alpha <= 1
    
    # Named colors
    named_colors = {
        'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'black', 'white',
        'gray', 'grey', 'orange', 'purple', 'pink', 'brown', 'transparent'
    }
    return color in named_colors


def parse_color(color: str) -> Tuple[float, float, float, float]:
    """
    Parse color string to RGBA values.
    
    Args:
        color: Color string
        
    Returns:
        Tuple of (red, green, blue, alpha) values (0.0-1.0)
        
    Raises:
        GimpValidationError: If color format is invalid
    """
    if not validate_color(color):
        raise GimpValidationError(f"Invalid color format: {color}")
    
    color = color.strip().lower()
    
    # Hex color parsing
    if color.startswith('#'):
        hex_color = color[1:]
        
        if len(hex_color) == 3:
            # Short hex format: #RGB -> #RRGGBB
            hex_color = ''.join([c*2 for c in hex_color])
        
        if len(hex_color) == 6:
            # RGB format
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            a = 1.0
        elif len(hex_color) == 8:
            # RGBA format
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            a = int(hex_color[6:8], 16) / 255.0
        
        return (r, g, b, a)
    
    # RGB/RGBA parsing
    rgb_pattern = r'^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)$'
    rgb_match = re.match(rgb_pattern, color)
    if rgb_match:
        r = int(rgb_match.group(1)) / 255.0
        g = int(rgb_match.group(2)) / 255.0
        b = int(rgb_match.group(3)) / 255.0
        a = float(rgb_match.group(4)) if rgb_match.group(4) else 1.0
        return (r, g, b, a)
    
    # Named colors
    named_colors = {
        'red': (1.0, 0.0, 0.0, 1.0),
        'green': (0.0, 1.0, 0.0, 1.0),
        'blue': (0.0, 0.0, 1.0, 1.0),
        'yellow': (1.0, 1.0, 0.0, 1.0),
        'cyan': (0.0, 1.0, 1.0, 1.0),
        'magenta': (1.0, 0.0, 1.0, 1.0),
        'black': (0.0, 0.0, 0.0, 1.0),
        'white': (1.0, 1.0, 1.0, 1.0),
        'gray': (0.5, 0.5, 0.5, 1.0),
        'grey': (0.5, 0.5, 0.5, 1.0),
        'orange': (1.0, 0.65, 0.0, 1.0),
        'purple': (0.5, 0.0, 0.5, 1.0),
        'pink': (1.0, 0.75, 0.8, 1.0),
        'brown': (0.65, 0.16, 0.16, 1.0),
        'transparent': (0.0, 0.0, 0.0, 0.0),
    }
    
    return named_colors.get(color, (0.0, 0.0, 0.0, 1.0))


def validate_coordinates(x: float, y: float, min_x: float = 0, min_y: float = 0, 
                        max_x: Optional[float] = None, max_y: Optional[float] = None) -> None:
    """
    Validate coordinate values.
    
    Args:
        x: X coordinate
        y: Y coordinate
        min_x: Minimum X value (default: 0)
        min_y: Minimum Y value (default: 0)
        max_x: Maximum X value (optional)
        max_y: Maximum Y value (optional)
        
    Raises:
        GimpValidationError: If coordinates are invalid
    """
    if not isinstance(x, (int, float)):
        raise GimpValidationError(f"X coordinate must be numeric, got {type(x).__name__}")
    
    if not isinstance(y, (int, float)):
        raise GimpValidationError(f"Y coordinate must be numeric, got {type(y).__name__}")
    
    if x < min_x:
        raise GimpValidationError(f"X coordinate {x} is below minimum {min_x}")
    
    if y < min_y:
        raise GimpValidationError(f"Y coordinate {y} is below minimum {min_y}")
    
    if max_x is not None and x > max_x:
        raise GimpValidationError(f"X coordinate {x} exceeds maximum {max_x}")
    
    if max_y is not None and y > max_y:
        raise GimpValidationError(f"Y coordinate {y} exceeds maximum {max_y}")


def validate_dimensions(width: float, height: float, min_width: float = 1, min_height: float = 1,
                       max_width: Optional[float] = None, max_height: Optional[float] = None) -> None:
    """
    Validate dimension values.
    
    Args:
        width: Width value
        height: Height value
        min_width: Minimum width (default: 1)
        min_height: Minimum height (default: 1)
        max_width: Maximum width (optional)
        max_height: Maximum height (optional)
        
    Raises:
        GimpValidationError: If dimensions are invalid
    """
    if not isinstance(width, (int, float)):
        raise GimpValidationError(f"Width must be numeric, got {type(width).__name__}")
    
    if not isinstance(height, (int, float)):
        raise GimpValidationError(f"Height must be numeric, got {type(height).__name__}")
    
    if width < min_width:
        raise GimpValidationError(f"Width {width} is below minimum {min_width}")
    
    if height < min_height:
        raise GimpValidationError(f"Height {height} is below minimum {min_height}")
    
    if max_width is not None and width > max_width:
        raise GimpValidationError(f"Width {width} exceeds maximum {max_width}")
    
    if max_height is not None and height > max_height:
        raise GimpValidationError(f"Height {height} exceeds maximum {max_height}")


def validate_opacity(opacity: float) -> None:
    """
    Validate opacity value.
    
    Args:
        opacity: Opacity value (0.0-100.0)
        
    Raises:
        GimpValidationError: If opacity is invalid
    """
    if not isinstance(opacity, (int, float)):
        raise GimpValidationError(f"Opacity must be numeric, got {type(opacity).__name__}")
    
    if not (0.0 <= opacity <= 100.0):
        raise GimpValidationError(f"Opacity must be between 0.0 and 100.0, got {opacity}")


def validate_brush_size(size: float, min_size: float = 0.1, max_size: float = 1000.0) -> None:
    """
    Validate brush size value.
    
    Args:
        size: Brush size
        min_size: Minimum size (default: 0.1)
        max_size: Maximum size (default: 1000.0)
        
    Raises:
        GimpValidationError: If brush size is invalid
    """
    if not isinstance(size, (int, float)):
        raise GimpValidationError(f"Brush size must be numeric, got {type(size).__name__}")
    
    if not (min_size <= size <= max_size):
        raise GimpValidationError(f"Brush size must be between {min_size} and {max_size}, got {size}")


def validate_angle(angle: float) -> None:
    """
    Validate angle value.
    
    Args:
        angle: Angle in degrees
        
    Raises:
        GimpValidationError: If angle is invalid
    """
    if not isinstance(angle, (int, float)):
        raise GimpValidationError(f"Angle must be numeric, got {type(angle).__name__}")
    
    # Normalize angle to 0-360 range is optional, but validate it's reasonable
    if not (-360.0 <= angle <= 360.0):
        raise GimpValidationError(f"Angle should be between -360 and 360 degrees, got {angle}")


def normalize_path_points(points: list) -> list:
    """
    Normalize path points to ensure they're valid coordinate pairs.
    
    Args:
        points: List of points (can be tuples, lists, or dicts)
        
    Returns:
        List of (x, y) tuples
        
    Raises:
        GimpValidationError: If points format is invalid
    """
    if not isinstance(points, list):
        raise GimpValidationError("Points must be a list")
    
    if len(points) < 2:
        raise GimpValidationError("At least 2 points are required")
    
    normalized_points = []
    
    for i, point in enumerate(points):
        try:
            if isinstance(point, (tuple, list)) and len(point) >= 2:
                x, y = float(point[0]), float(point[1])
            elif isinstance(point, dict):
                x, y = float(point['x']), float(point['y'])
            else:
                raise ValueError(f"Invalid point format: {point}")
            
            validate_coordinates(x, y)
            normalized_points.append((x, y))
            
        except (ValueError, KeyError, TypeError) as e:
            raise GimpValidationError(f"Invalid point at index {i}: {e}")
    
    return normalized_points


def calculate_bounding_box(points: list) -> Dict[str, float]:
    """
    Calculate bounding box for a set of points.
    
    Args:
        points: List of (x, y) coordinate tuples
        
    Returns:
        Dictionary with min_x, min_y, max_x, max_y, width, height
    """
    if not points:
        return {"min_x": 0, "min_y": 0, "max_x": 0, "max_y": 0, "width": 0, "height": 0}
    
    x_coords = [point[0] for point in points]
    y_coords = [point[1] for point in points]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    return {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "width": max_x - min_x,
        "height": max_y - min_y,
    }


def validate_image_format(format_name: str) -> str:
    """
    Validate and normalize image format name.
    
    Args:
        format_name: Image format name
        
    Returns:
        Normalized format name
        
    Raises:
        GimpValidationError: If format is not supported
    """
    if not isinstance(format_name, str):
        raise GimpValidationError("Format name must be a string")
    
    format_name = format_name.upper().strip()
    
    supported_formats = {
        'PNG', 'JPEG', 'JPG', 'GIF', 'TIFF', 'TIF', 'BMP', 'WEBP', 'XCF'
    }
    
    # Normalize some common variations
    format_mapping = {
        'JPG': 'JPEG',
        'TIF': 'TIFF',
    }
    
    format_name = format_mapping.get(format_name, format_name)
    
    if format_name not in supported_formats:
        raise GimpValidationError(
            f"Unsupported image format: {format_name}. "
            f"Supported formats: {', '.join(sorted(supported_formats))}"
        )
    
    return format_name


def validate_resolution(resolution: float) -> None:
    """
    Validate image resolution (DPI).
    
    Args:
        resolution: Resolution in DPI
        
    Raises:
        GimpValidationError: If resolution is invalid
    """
    if not isinstance(resolution, (int, float)):
        raise GimpValidationError(f"Resolution must be numeric, got {type(resolution).__name__}")
    
    if not (1.0 <= resolution <= 3000.0):
        raise GimpValidationError(f"Resolution must be between 1 and 3000 DPI, got {resolution}")


def create_image_info(width: int, height: int, mode: str = "RGB", 
                     resolution: float = 300.0) -> Dict[str, Any]:
    """
    Create standardized image information dictionary.
    
    Args:
        width: Image width
        height: Image height
        mode: Color mode (RGB, GRAYSCALE, INDEXED)
        resolution: Resolution in DPI
        
    Returns:
        Dictionary with image information
    """
    validate_dimensions(width, height)
    validate_resolution(resolution)
    
    mode = mode.upper()
    valid_modes = {'RGB', 'GRAYSCALE', 'INDEXED'}
    if mode not in valid_modes:
        raise GimpValidationError(f"Invalid color mode: {mode}. Valid modes: {', '.join(valid_modes)}")
    
    return {
        "width": int(width),
        "height": int(height),
        "mode": mode,
        "resolution": float(resolution),
        "aspect_ratio": width / height if height > 0 else 1.0,
        "total_pixels": width * height,
    }


def validate_layer_name(name: str) -> str:
    """
    Validate and sanitize layer name.
    
    Args:
        name: Layer name
        
    Returns:
        Sanitized layer name
        
    Raises:
        GimpValidationError: If name is invalid
    """
    if not isinstance(name, str):
        raise GimpValidationError("Layer name must be a string")
    
    name = name.strip()
    
    if not name:
        raise GimpValidationError("Layer name cannot be empty")
    
    if len(name) > 255:
        raise GimpValidationError("Layer name cannot exceed 255 characters")
    
    # Remove or replace problematic characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    return name


def convert_coordinates_to_gimp(x: float, y: float, image_width: int, image_height: int,
                               coordinate_system: str = "top_left") -> Tuple[float, float]:
    """
    Convert coordinates between different coordinate systems and GIMP's system.
    
    Args:
        x: X coordinate
        y: Y coordinate
        image_width: Image width
        image_height: Image height
        coordinate_system: Source coordinate system ("top_left", "bottom_left", "center")
        
    Returns:
        Tuple of (gimp_x, gimp_y) coordinates
        
    Raises:
        GimpValidationError: If coordinate system is invalid
    """
    valid_systems = ["top_left", "bottom_left", "center"]
    if coordinate_system not in valid_systems:
        raise GimpValidationError(
            f"Invalid coordinate system: {coordinate_system}. Valid systems: {valid_systems}"
        )
    
    # GIMP uses top-left origin
    if coordinate_system == "top_left":
        return (x, y)
    elif coordinate_system == "bottom_left":
        return (x, image_height - y)
    elif coordinate_system == "center":
        return (x + image_width / 2, y + image_height / 2)
    
    return (x, y)


def calculate_aspect_ratio_dimensions(original_width: int, original_height: int,
                                    target_width: Optional[int] = None,
                                    target_height: Optional[int] = None) -> Tuple[int, int]:
    """
    Calculate dimensions maintaining aspect ratio.
    
    Args:
        original_width: Original image width
        original_height: Original image height
        target_width: Target width (optional)
        target_height: Target height (optional)
        
    Returns:
        Tuple of (width, height) maintaining aspect ratio
        
    Raises:
        GimpValidationError: If neither target dimension is provided
    """
    if target_width is None and target_height is None:
        raise GimpValidationError("Either target_width or target_height must be provided")
    
    original_ratio = original_width / original_height
    
    if target_width is not None and target_height is not None:
        # Both provided, choose the one that maintains ratio within bounds
        width_based_height = target_width / original_ratio
        height_based_width = target_height * original_ratio
        
        if width_based_height <= target_height:
            return (target_width, int(width_based_height))
        else:
            return (int(height_based_width), target_height)
    
    elif target_width is not None:
        # Width provided, calculate height
        new_height = target_width / original_ratio
        return (target_width, int(new_height))
    
    else:
        # Height provided, calculate width
        new_width = target_height * original_ratio
        return (int(new_width), target_height)


def validate_brush_parameters(brush_size: float, brush_hardness: float = 1.0,
                             brush_spacing: float = 0.1) -> None:
    """
    Validate brush parameters.
    
    Args:
        brush_size: Brush size
        brush_hardness: Brush hardness (0.0-1.0)
        brush_spacing: Brush spacing (0.0-1.0)
        
    Raises:
        GimpValidationError: If parameters are invalid
    """
    validate_brush_size(brush_size)
    
    if not isinstance(brush_hardness, (int, float)):
        raise GimpValidationError(f"Brush hardness must be numeric, got {type(brush_hardness).__name__}")
    
    if not (0.0 <= brush_hardness <= 1.0):
        raise GimpValidationError(f"Brush hardness must be between 0.0 and 1.0, got {brush_hardness}")
    
    if not isinstance(brush_spacing, (int, float)):
        raise GimpValidationError(f"Brush spacing must be numeric, got {type(brush_spacing).__name__}")
    
    if not (0.0 <= brush_spacing <= 1.0):
        raise GimpValidationError(f"Brush spacing must be between 0.0 and 1.0, got {brush_spacing}")


def create_gradient_points(start_x: float, start_y: float, end_x: float, end_y: float,
                          start_color: str, end_color: str) -> Dict[str, Any]:
    """
    Create gradient definition for GIMP operations.
    
    Args:
        start_x: Gradient start X coordinate
        start_y: Gradient start Y coordinate
        end_x: Gradient end X coordinate
        end_y: Gradient end Y coordinate
        start_color: Starting color
        end_color: Ending color
        
    Returns:
        Dictionary with gradient information
        
    Raises:
        GimpValidationError: If parameters are invalid
    """
    validate_coordinates(start_x, start_y)
    validate_coordinates(end_x, end_y)
    
    start_rgba = parse_color(start_color)
    end_rgba = parse_color(end_color)
    
    return {
        "start_point": (start_x, start_y),
        "end_point": (end_x, end_y),
        "start_color": {
            "r": start_rgba[0],
            "g": start_rgba[1],
            "b": start_rgba[2],
            "a": start_rgba[3]
        },
        "end_color": {
            "r": end_rgba[0],
            "g": end_rgba[1],
            "b": end_rgba[2],
            "a": end_rgba[3]
        },
        "length": ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5,
        "angle": math.atan2(end_y - start_y, end_x - start_x)
    }


def validate_selection_bounds(x: float, y: float, width: float, height: float,
                             image_width: int, image_height: int) -> None:
    """
    Validate selection bounds within image dimensions.
    
    Args:
        x: Selection X coordinate
        y: Selection Y coordinate
        width: Selection width
        height: Selection height
        image_width: Image width
        image_height: Image height
        
    Raises:
        GimpValidationError: If selection is out of bounds
    """
    validate_coordinates(x, y)
    validate_dimensions(width, height)
    
    if x + width > image_width:
        raise GimpValidationError(
            f"Selection extends beyond image width: {x + width} > {image_width}"
        )
    
    if y + height > image_height:
        raise GimpValidationError(
            f"Selection extends beyond image height: {y + height} > {image_height}"
        )


def calculate_canvas_size(current_width: int, current_height: int,
                         new_width: int, new_height: int,
                         anchor: str = "center") -> Dict[str, int]:
    """
    Calculate canvas resize parameters.
    
    Args:
        current_width: Current canvas width
        current_height: Current canvas height
        new_width: New canvas width
        new_height: New canvas height
        anchor: Anchor position ("center", "top_left", "top_right", "bottom_left", "bottom_right")
        
    Returns:
        Dictionary with offset and size information
        
    Raises:
        GimpValidationError: If anchor is invalid
    """
    valid_anchors = ["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    if anchor not in valid_anchors:
        raise GimpValidationError(f"Invalid anchor: {anchor}. Valid anchors: {valid_anchors}")
    
    validate_dimensions(new_width, new_height)
    
    # Calculate offsets based on anchor
    if anchor == "center":
        offset_x = (new_width - current_width) // 2
        offset_y = (new_height - current_height) // 2
    elif anchor == "top_left":
        offset_x = 0
        offset_y = 0
    elif anchor == "top_right":
        offset_x = new_width - current_width
        offset_y = 0
    elif anchor == "bottom_left":
        offset_x = 0
        offset_y = new_height - current_height
    elif anchor == "bottom_right":
        offset_x = new_width - current_width
        offset_y = new_height - current_height
    
    return {
        "new_width": new_width,
        "new_height": new_height,
        "offset_x": offset_x,
        "offset_y": offset_y,
        "anchor": anchor
    }


def create_transform_matrix(scale_x: float = 1.0, scale_y: float = 1.0,
                           rotation: float = 0.0, translate_x: float = 0.0,
                           translate_y: float = 0.0) -> List[float]:
    """
    Create 2D transformation matrix for GIMP operations.
    
    Args:
        scale_x: X scale factor
        scale_y: Y scale factor
        rotation: Rotation angle in degrees
        translate_x: X translation
        translate_y: Y translation
        
    Returns:
        2D transformation matrix as list
    """
    import math
    
    # Convert rotation to radians
    angle = math.radians(rotation)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Create transformation matrix
    # [a, b, c, d, e, f] represents:
    # [a c e]   [scale_x*cos  -scale_x*sin  translate_x]
    # [b d f] = [scale_y*sin   scale_y*cos  translate_y]
    # [0 0 1]   [0            0            1          ]
    
    matrix = [
        scale_x * cos_a,  # a
        scale_y * sin_a,  # b
        -scale_x * sin_a, # c
        scale_y * cos_a,  # d
        translate_x,      # e
        translate_y       # f
    ]
    
    return matrix


def validate_filter_parameters(filter_name: str, parameters: Dict[str, Any]) -> None:
    """
    Validate filter parameters for common GIMP filters.
    
    Args:
        filter_name: Name of the filter
        parameters: Filter parameters
        
    Raises:
        GimpValidationError: If parameters are invalid
    """
    filter_specs = {
        "gaussian_blur": {
            "required": ["radius"],
            "optional": ["horizontal", "vertical"],
            "ranges": {"radius": (0.1, 100.0)}
        },
        "unsharp_mask": {
            "required": ["radius", "amount"],
            "optional": ["threshold"],
            "ranges": {"radius": (0.1, 100.0), "amount": (0.0, 10.0), "threshold": (0, 255)}
        },
        "brightness_contrast": {
            "required": [],
            "optional": ["brightness", "contrast"],
            "ranges": {"brightness": (-100, 100), "contrast": (-100, 100)}
        }
    }
    
    if filter_name not in filter_specs:
        logger.warning(f"Unknown filter: {filter_name}, skipping validation")
        return
    
    spec = filter_specs[filter_name]
    
    # Check required parameters
    for param in spec["required"]:
        if param not in parameters:
            raise GimpValidationError(f"Missing required parameter for {filter_name}: {param}")
    
    # Validate parameter ranges
    for param, value in parameters.items():
        if param in spec.get("ranges", {}):
            min_val, max_val = spec["ranges"][param]
            if not (min_val <= value <= max_val):
                raise GimpValidationError(
                    f"Parameter '{param}' for {filter_name} must be between {min_val} and {max_val}, got {value}"
                )


# Import math at the top for transform matrix calculations
import math