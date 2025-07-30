"""
Drawing Tools for GIMP MCP Server

This module provides MCP tools for basic drawing operations including
brush strokes, shapes, and fill operations.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple

from ..utils.errors import safe_operation, GimpValidationError
from ..utils.image_utils import (
    validate_color, parse_color, validate_coordinates, validate_dimensions,
    validate_brush_size, normalize_path_points
)

logger = logging.getLogger(__name__)


class DrawingTools:
    """Basic drawing operations for GIMP MCP server."""
    
    def __init__(self, gimp_api):
        """
        Initialize drawing tools.
        
        Args:
            gimp_api: GIMP API instance
        """
        self.gimp_api = gimp_api
    
    @safe_operation("apply_brush_stroke")
    async def apply_brush_stroke(
        self,
        points: List[Tuple[float, float]],
        brush_name: str = "2. Hardness 050",
        size: float = 10.0,
        opacity: float = 100.0,
        color: Optional[str] = None,
        layer_id: Optional[int] = None,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Apply a brush stroke to the active layer.
        
        Args:
            points: List of (x, y) coordinate points for the stroke
            brush_name: Name of the brush to use
            size: Brush size in pixels
            opacity: Brush opacity (0-100)
            color: Brush color (uses foreground if None)
            layer_id: Target layer ID (uses active if None)
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing stroke result
        """
        try:
            # Validate parameters
            normalized_points = normalize_path_points(points)
            validate_brush_size(size)
            
            if opacity < 0 or opacity > 100:
                raise GimpValidationError(f"Opacity must be between 0 and 100, got {opacity}")
            
            if color and not validate_color(color):
                raise GimpValidationError(f"Invalid color format: {color}")
            
            # TODO: Implement actual GIMP brush stroke
            return {
                "success": True,
                "operation": "apply_brush_stroke",
                "points_count": len(normalized_points),
                "brush_name": brush_name,
                "size": size,
                "opacity": opacity,
                "color": color,
                "layer_id": layer_id,
                "document_id": document_id,
                "message": "Brush stroke applied successfully (stub implementation)",
            }
            
        except Exception as e:
            logger.error(f"Failed to apply brush stroke: {e}")
            raise
    
    @safe_operation("draw_rectangle")
    async def draw_rectangle(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill_color: Optional[str] = None,
        stroke_color: Optional[str] = None,
        stroke_width: float = 1.0,
        layer_id: Optional[int] = None,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Draw a rectangle shape.
        
        Args:
            x: X coordinate of rectangle
            y: Y coordinate of rectangle
            width: Rectangle width
            height: Rectangle height
            fill_color: Fill color (no fill if None)
            stroke_color: Stroke color (no stroke if None)
            stroke_width: Stroke width in pixels
            layer_id: Target layer ID (uses active if None)
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing draw result
        """
        try:
            # Validate parameters
            validate_coordinates(x, y)
            validate_dimensions(width, height)
            
            if stroke_width < 0:
                raise GimpValidationError("Stroke width cannot be negative")
            
            if fill_color and not validate_color(fill_color):
                raise GimpValidationError(f"Invalid fill color: {fill_color}")
            
            if stroke_color and not validate_color(stroke_color):
                raise GimpValidationError(f"Invalid stroke color: {stroke_color}")
            
            # TODO: Implement actual GIMP rectangle drawing
            return {
                "success": True,
                "operation": "draw_rectangle",
                "bounds": {"x": x, "y": y, "width": width, "height": height},
                "fill_color": fill_color,
                "stroke_color": stroke_color,
                "stroke_width": stroke_width,
                "layer_id": layer_id,
                "document_id": document_id,
                "message": "Rectangle drawn successfully (stub implementation)",
            }
            
        except Exception as e:
            logger.error(f"Failed to draw rectangle: {e}")
            raise
    
    @safe_operation("draw_ellipse")
    async def draw_ellipse(
        self,
        center_x: float,
        center_y: float,
        radius_x: float,
        radius_y: float,
        fill_color: Optional[str] = None,
        stroke_color: Optional[str] = None,
        stroke_width: float = 1.0,
        layer_id: Optional[int] = None,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Draw an ellipse shape.
        
        Args:
            center_x: X coordinate of ellipse center
            center_y: Y coordinate of ellipse center
            radius_x: Horizontal radius
            radius_y: Vertical radius
            fill_color: Fill color (no fill if None)
            stroke_color: Stroke color (no stroke if None)
            stroke_width: Stroke width in pixels
            layer_id: Target layer ID (uses active if None)
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing draw result
        """
        try:
            # Validate parameters
            validate_coordinates(center_x, center_y)
            
            if radius_x <= 0 or radius_y <= 0:
                raise GimpValidationError("Radii must be positive values")
            
            if stroke_width < 0:
                raise GimpValidationError("Stroke width cannot be negative")
            
            if fill_color and not validate_color(fill_color):
                raise GimpValidationError(f"Invalid fill color: {fill_color}")
            
            if stroke_color and not validate_color(stroke_color):
                raise GimpValidationError(f"Invalid stroke color: {stroke_color}")
            
            # TODO: Implement actual GIMP ellipse drawing
            return {
                "success": True,
                "operation": "draw_ellipse",
                "center": {"x": center_x, "y": center_y},
                "radii": {"x": radius_x, "y": radius_y},
                "fill_color": fill_color,
                "stroke_color": stroke_color,
                "stroke_width": stroke_width,
                "layer_id": layer_id,
                "document_id": document_id,
                "message": "Ellipse drawn successfully (stub implementation)",
            }
            
        except Exception as e:
            logger.error(f"Failed to draw ellipse: {e}")
            raise
    
    @safe_operation("bucket_fill")
    async def bucket_fill(
        self,
        x: float,
        y: float,
        color: str,
        threshold: float = 10.0,
        sample_merged: bool = False,
        layer_id: Optional[int] = None,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform bucket fill operation.
        
        Args:
            x: X coordinate to fill from
            y: Y coordinate to fill from
            color: Fill color
            threshold: Fill threshold (0-100)
            sample_merged: Whether to sample from merged layers
            layer_id: Target layer ID (uses active if None)
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing fill result
        """
        try:
            # Validate parameters
            validate_coordinates(x, y)
            
            if not validate_color(color):
                raise GimpValidationError(f"Invalid color: {color}")
            
            if not (0 <= threshold <= 100):
                raise GimpValidationError(f"Threshold must be between 0 and 100, got {threshold}")
            
            # TODO: Implement actual GIMP bucket fill
            return {
                "success": True,
                "operation": "bucket_fill",
                "fill_point": {"x": x, "y": y},
                "color": color,
                "threshold": threshold,
                "sample_merged": sample_merged,
                "layer_id": layer_id,
                "document_id": document_id,
                "message": "Bucket fill completed successfully (stub implementation)",
            }
            
        except Exception as e:
            logger.error(f"Failed to perform bucket fill: {e}")
            raise