"""
Layer Management Tools for GIMP MCP Server

This module provides MCP tools for layer operations including
creation, modification, and layer hierarchy management.
"""

import logging
from typing import Dict, Any, Optional

from ..utils.errors import safe_operation, GimpValidationError
from ..utils.image_utils import validate_opacity, validate_layer_name

logger = logging.getLogger(__name__)


class LayerTools:
    """Layer management operations for GIMP MCP server."""
    
    def __init__(self, gimp_api):
        """
        Initialize layer tools.
        
        Args:
            gimp_api: GIMP API instance
        """
        self.gimp_api = gimp_api
    
    @safe_operation("get_layer_info")
    async def get_layer_info(
        self,
        layer_id: int,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a layer.
        
        Args:
            layer_id: ID of the layer
            document_id: ID of the document (uses active if None)
            
        Returns:
            Dictionary containing layer information
        """
        if not isinstance(layer_id, int):
            raise GimpValidationError("Layer ID must be an integer")
        
        try:
            # Get active document if not specified
            if document_id is None:
                active_doc = await self.gimp_api.get_active_image()
                if not active_doc:
                    return {
                        "success": False,
                        "operation": "get_layer_info",
                        "error": "No active document found",
                        "timestamp": __import__('time').time(),
                    }
                document_id = active_doc.get("id", 0)
            
            # Get layer information from GIMP API
            # Note: Layer info is typically included in document info
            doc_result = await self.gimp_api.get_image_info(document_id)
            
            if doc_result.get("success"):
                layers = doc_result.get("image_info", {}).get("layers", [])
                layer_info = None
                
                for layer in layers:
                    if layer.get("id") == layer_id:
                        layer_info = layer
                        break
                
                if layer_info:
                    return {
                        "success": True,
                        "operation": "get_layer_info",
                        "layer_id": layer_id,
                        "document_id": document_id,
                        "layer_info": layer_info,
                        "timestamp": doc_result.get("timestamp"),
                    }
                else:
                    return {
                        "success": False,
                        "operation": "get_layer_info",
                        "layer_id": layer_id,
                        "document_id": document_id,
                        "error": f"Layer {layer_id} not found",
                        "timestamp": __import__('time').time(),
                    }
            else:
                return {
                    "success": False,
                    "operation": "get_layer_info",
                    "error": doc_result.get("error", "Failed to get document info"),
                    "timestamp": doc_result.get("timestamp"),
                }
                
        except Exception as e:
            logger.error(f"Failed to get layer info: {e}")
            return {
                "success": False,
                "operation": "get_layer_info",
                "error": str(e),
                "timestamp": __import__('time').time(),
            }
    
    @safe_operation("create_layer")
    async def create_layer(
        self,
        document_id: Optional[int] = None,
        name: str = "New Layer",
        layer_type: str = "RGB",
        opacity: float = 100.0,
        blend_mode: str = "normal"
    ) -> Dict[str, Any]:
        """
        Create a new layer in the document.
        
        Args:
            document_id: Document ID (uses active if None)
            name: Layer name
            layer_type: Layer type (RGB, GRAYSCALE, etc.)
            opacity: Layer opacity (0-100)
            blend_mode: Layer blend mode
            
        Returns:
            Dictionary containing layer creation result
        """
        try:
            # Validate parameters
            name = validate_layer_name(name)
            validate_opacity(opacity)
            
            valid_types = ["RGB", "GRAYSCALE", "INDEXED"]
            if layer_type.upper() not in valid_types:
                raise GimpValidationError(f"Invalid layer type: {layer_type}")
            
            # Get active document if not specified
            if document_id is None:
                active_doc = await self.gimp_api.get_active_image()
                if not active_doc:
                    return {
                        "success": False,
                        "operation": "create_layer",
                        "error": "No active document found",
                        "timestamp": __import__('time').time(),
                    }
                document_id = active_doc.get("id", 0)
            
            # Create layer using GIMP API
            result = await self.gimp_api.create_layer(
                image_id=document_id,
                layer_name=name,
                layer_type=layer_type,
                opacity=opacity,
                blend_mode=blend_mode
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "operation": "create_layer",
                    "document_id": document_id,
                    "layer_id": result.get("layer_id"),
                    "layer_info": {
                        "name": name,
                        "type": layer_type,
                        "opacity": opacity,
                        "blend_mode": blend_mode,
                        "visible": True,
                        "width": result.get("width"),
                        "height": result.get("height"),
                    },
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "success": False,
                    "operation": "create_layer",
                    "document_id": document_id,
                    "error": result.get("error", "Layer creation failed"),
                    "timestamp": result.get("timestamp"),
                }
            
        except Exception as e:
            logger.error(f"Failed to create layer: {e}")
            raise
    
    @safe_operation("set_layer_opacity")
    async def set_layer_opacity(
        self,
        layer_id: int,
        opacity: float,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Set layer opacity (0-100).
        
        Args:
            layer_id: ID of the layer
            opacity: Opacity value (0-100)
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing operation result
        """
        if not isinstance(layer_id, int):
            raise GimpValidationError("Layer ID must be an integer")
        
        validate_opacity(opacity)
        
        try:
            # Get active document if not specified
            if document_id is None:
                active_doc = await self.gimp_api.get_active_image()
                if not active_doc:
                    return {
                        "success": False,
                        "operation": "set_layer_opacity",
                        "error": "No active document found",
                        "timestamp": __import__('time').time(),
                    }
                document_id = active_doc.get("id", 0)
            
            # Set layer opacity using GIMP API
            result = await self.gimp_api.set_layer_opacity(document_id, layer_id, opacity)
            
            if result.get("success"):
                return {
                    "success": True,
                    "operation": "set_layer_opacity",
                    "layer_id": layer_id,
                    "document_id": document_id,
                    "opacity": opacity,
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "success": False,
                    "operation": "set_layer_opacity",
                    "layer_id": layer_id,
                    "document_id": document_id,
                    "error": result.get("error", "Failed to set layer opacity"),
                    "timestamp": result.get("timestamp"),
                }
                
        except Exception as e:
            logger.error(f"Failed to set layer opacity: {e}")
            return {
                "success": False,
                "operation": "set_layer_opacity",
                "error": str(e),
                "timestamp": __import__('time').time(),
            }
    
    @safe_operation("set_layer_blend_mode")
    async def set_layer_blend_mode(
        self,
        layer_id: int,
        blend_mode: str,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Set layer blend mode.
        
        Args:
            layer_id: ID of the layer
            blend_mode: Blend mode name
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing operation result
        """
        if not isinstance(layer_id, int):
            raise GimpValidationError("Layer ID must be an integer")
        
        valid_blend_modes = [
            "normal", "multiply", "screen", "overlay", "soft_light", "hard_light",
            "color_dodge", "color_burn", "darken_only", "lighten_only",
            "difference", "exclusion", "hue", "saturation", "color", "luminosity"
        ]
        
        if blend_mode.lower() not in valid_blend_modes:
            raise GimpValidationError(f"Invalid blend mode: {blend_mode}")
        
        try:
            # Get active document if not specified
            if document_id is None:
                active_doc = await self.gimp_api.get_active_image()
                if not active_doc:
                    return {
                        "success": False,
                        "operation": "set_layer_blend_mode",
                        "error": "No active document found",
                        "timestamp": __import__('time').time(),
                    }
                document_id = active_doc.get("id", 0)
            
            # Set layer blend mode using GIMP API
            result = await self.gimp_api.set_layer_blend_mode(document_id, layer_id, blend_mode)
            
            if result.get("success"):
                return {
                    "success": True,
                    "operation": "set_layer_blend_mode",
                    "layer_id": layer_id,
                    "document_id": document_id,
                    "blend_mode": blend_mode,
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "success": False,
                    "operation": "set_layer_blend_mode",
                    "layer_id": layer_id,
                    "document_id": document_id,
                    "error": result.get("error", "Failed to set layer blend mode"),
                    "timestamp": result.get("timestamp"),
                }
                
        except Exception as e:
            logger.error(f"Failed to set layer blend mode: {e}")
            return {
                "success": False,
                "operation": "set_layer_blend_mode",
                "error": str(e),
                "timestamp": __import__('time').time(),
            }
    
    @safe_operation("set_layer_visibility")
    async def set_layer_visibility(
        self,
        layer_id: int,
        visible: bool,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Set layer visibility.
        
        Args:
            layer_id: ID of the layer
            visible: Visibility state
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing operation result
        """
        if not isinstance(layer_id, int):
            raise GimpValidationError("Layer ID must be an integer")
        
        if not isinstance(visible, bool):
            raise GimpValidationError("Visible must be a boolean value")
        
        # TODO: Implement actual GIMP layer visibility setting
        return {
            "success": True,
            "operation": "set_layer_visibility",
            "layer_id": layer_id,
            "document_id": document_id,
            "visible": visible,
            "message": "Layer visibility set successfully (stub implementation)",
        }
    
    @safe_operation("duplicate_layer")
    async def duplicate_layer(
        self,
        layer_id: int,
        new_name: Optional[str] = None,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Duplicate an existing layer.
        
        Args:
            layer_id: ID of the layer to duplicate
            new_name: Name for the duplicated layer
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing duplication result
        """
        if not isinstance(layer_id, int):
            raise GimpValidationError("Layer ID must be an integer")
        
        if new_name:
            new_name = validate_layer_name(new_name)
        
        # TODO: Implement actual GIMP layer duplication
        return {
            "success": True,
            "operation": "duplicate_layer",
            "original_layer_id": layer_id,
            "new_layer_id": 102,  # Stub ID
            "document_id": document_id,
            "new_name": new_name or f"Copy of Layer {layer_id}",
            "message": "Layer duplicated successfully (stub implementation)",
        }
    
    @safe_operation("delete_layer")
    async def delete_layer(
        self,
        layer_id: int,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Delete a layer safely.
        
        Args:
            layer_id: ID of the layer to delete
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing deletion result
        """
        if not isinstance(layer_id, int):
            raise GimpValidationError("Layer ID must be an integer")
        
        # TODO: Implement actual GIMP layer deletion
        return {
            "success": True,
            "operation": "delete_layer",
            "layer_id": layer_id,
            "document_id": document_id,
            "message": "Layer deleted successfully (stub implementation)",
        }
    
    @safe_operation("move_layer")
    async def move_layer(
        self,
        layer_id: int,
        new_parent_id: Optional[int] = None,
        new_position: Optional[int] = None,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Move a layer to a new position in the layer hierarchy.
        
        Args:
            layer_id: ID of the layer to move
            new_parent_id: New parent layer ID (for layer groups)
            new_position: New position in layer stack
            document_id: Document ID (uses active if None)
            
        Returns:
            Dictionary containing move result
        """
        if not isinstance(layer_id, int):
            raise GimpValidationError("Layer ID must be an integer")
        
        if new_parent_id is not None and not isinstance(new_parent_id, int):
            raise GimpValidationError("New parent ID must be an integer")
        
        if new_position is not None and not isinstance(new_position, int):
            raise GimpValidationError("New position must be an integer")
        
        # TODO: Implement actual GIMP layer moving
        return {
            "success": True,
            "operation": "move_layer",
            "layer_id": layer_id,
            "new_parent_id": new_parent_id,
            "new_position": new_position,
            "document_id": document_id,
            "message": "Layer moved successfully (stub implementation)",
        }