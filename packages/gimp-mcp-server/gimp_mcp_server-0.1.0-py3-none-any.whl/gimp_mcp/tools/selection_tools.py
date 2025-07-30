"""
Selection Tools for GIMP MCP Server

This module provides MCP tools for selection operations including
rectangular, elliptical selections and selection modifications.
"""

import logging
from typing import Dict, Any, Optional

from ..utils.errors import safe_operation, GimpValidationError
from ..utils.image_utils import validate_coordinates, validate_dimensions

logger = logging.getLogger(__name__)


class SelectionTools:
    """Selection management operations for GIMP MCP server."""
    
    def __init__(self, gimp_api):
        """
        Initialize selection tools.
        
        Args:
            gimp_api: GIMP API instance
        """
        self.gimp_api = gimp_api
    
    @safe_operation("create_rectangular_selection")
    async def create_rectangular_selection(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        operation: str = "replace",
        feather: float = 0.0,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a rectangular selection.
        
        Args:
            x: X coordinate of selection
            y: Y coordinate of selection
            width: Selection width
            height: Selection height
            operation: Selection operation (replace, add, subtract, intersect)
            feather: Feather amount in pixels
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing selection result
        """
        try:
            validate_coordinates(x, y)
            validate_dimensions(width, height)
            
            valid_operations = ["replace", "add", "subtract", "intersect"]
            if operation.lower() not in valid_operations:
                raise GimpValidationError(f"Invalid operation: {operation}")
            
            if feather < 0:
                raise GimpValidationError("Feather amount cannot be negative")
            
            # TODO: Implement actual GIMP rectangular selection
            return {
                "success": True,
                "operation": "create_rectangular_selection",
                "bounds": {"x": x, "y": y, "width": width, "height": height},
                "selection_operation": operation,
                "feather": feather,
                "document_id": document_id,
                "message": "Rectangular selection created (stub implementation)",
            }
            
        except Exception as e:
            logger.error(f"Failed to create rectangular selection: {e}")
            raise
    
    @safe_operation("create_elliptical_selection")
    async def create_elliptical_selection(
        self,
        center_x: float,
        center_y: float,
        radius_x: float,
        radius_y: float,
        operation: str = "replace",
        feather: float = 0.0,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create an elliptical selection.
        
        Args:
            center_x: X coordinate of ellipse center
            center_y: Y coordinate of ellipse center
            radius_x: Horizontal radius
            radius_y: Vertical radius
            operation: Selection operation (replace, add, subtract, intersect)
            feather: Feather amount in pixels
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing selection result
        """
        try:
            validate_coordinates(center_x, center_y)
            
            if radius_x <= 0 or radius_y <= 0:
                raise GimpValidationError("Radii must be positive values")
            
            valid_operations = ["replace", "add", "subtract", "intersect"]
            if operation.lower() not in valid_operations:
                raise GimpValidationError(f"Invalid operation: {operation}")
            
            if feather < 0:
                raise GimpValidationError("Feather amount cannot be negative")
            
            # TODO: Implement actual GIMP elliptical selection
            return {
                "success": True,
                "operation": "create_elliptical_selection",
                "center": {"x": center_x, "y": center_y},
                "radii": {"x": radius_x, "y": radius_y},
                "selection_operation": operation,
                "feather": feather,
                "document_id": document_id,
                "message": "Elliptical selection created (stub implementation)",
            }
            
        except Exception as e:
            logger.error(f"Failed to create elliptical selection: {e}")
            raise
    
    @safe_operation("modify_selection")
    async def modify_selection(
        self,
        operation: str,
        value: float,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Modify existing selection (grow, shrink, border, feather).
        
        Args:
            operation: Modification operation (grow, shrink, border, feather)
            value: Modification value in pixels
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing modification result
        """
        try:
            valid_operations = ["grow", "shrink", "border", "feather"]
            if operation.lower() not in valid_operations:
                raise GimpValidationError(f"Invalid operation: {operation}")
            
            if value < 0:
                raise GimpValidationError("Modification value cannot be negative")
            
            # TODO: Implement actual GIMP selection modification
            return {
                "success": True,
                "operation": "modify_selection",
                "modification": operation,
                "value": value,
                "document_id": document_id,
                "message": f"Selection {operation} applied (stub implementation)",
            }
            
        except Exception as e:
            logger.error(f"Failed to modify selection: {e}")
            raise
    
    @safe_operation("clear_selection")
    async def clear_selection(self, document_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Clear the current selection.
        
        Args:
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing clear result
        """
        # TODO: Implement actual GIMP selection clearing
        return {
            "success": True,
            "operation": "clear_selection",
            "document_id": document_id,
            "message": "Selection cleared (stub implementation)",
        }