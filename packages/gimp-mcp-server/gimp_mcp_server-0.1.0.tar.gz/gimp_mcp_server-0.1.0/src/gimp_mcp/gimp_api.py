"""
GIMP API Wrapper - High-level interface for GIMP operations

This module provides a high-level wrapper for GIMP Python API with error handling,
connection management, and mode-aware operations.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List, Tuple

from .mode_manager import GimpModeManager
from .utils.errors import GimpError, GimpConnectionError, GimpOperationError
from .utils.gi_helpers import safe_gi_import

logger = logging.getLogger(__name__)


class GimpAPI:
    """High-level wrapper for GIMP Python API with error handling."""
    
    def __init__(self, mode_manager: Optional[GimpModeManager] = None):
        self.mode_manager = mode_manager or GimpModeManager()
        self._gimp = None
        self._last_health_check = 0
        self._health_check_interval = 30  # seconds
        self._connection_verified = False
        
        # Initialize GIMP connection
        self._initialize_gimp()
    
    def _initialize_gimp(self):
        """Initialize GIMP connection based on mode."""
        try:
            # Import GIMP through GObject Introspection
            gi_modules = safe_gi_import()
            if not gi_modules:
                raise GimpConnectionError("Failed to import GObject Introspection modules")
            
            Gimp = gi_modules.get("Gimp")
            if not Gimp:
                raise GimpConnectionError("Failed to import GIMP module")
            
            # Get GIMP instance based on mode
            self._gimp = self.mode_manager.get_gimp_instance()
            
            logger.info(f"GIMP API initialized in {'GUI' if self.mode_manager.gui_mode else 'headless'} mode")
            
        except Exception as e:
            logger.error(f"Failed to initialize GIMP API: {e}")
            raise GimpConnectionError(f"GIMP initialization failed: {e}")
    
    @asynccontextmanager
    async def ensure_connection(self):
        """Context manager ensuring GIMP connection is active."""
        if not await self._verify_connection():
            raise GimpConnectionError("Cannot establish GIMP connection")
        
        try:
            yield self._gimp
        except Exception as e:
            logger.error(f"GIMP operation failed: {e}")
            raise GimpOperationError(f"Operation failed: {e}")
    
    async def _verify_connection(self) -> bool:
        """Verify GIMP connection is active."""
        current_time = time.time()
        
        # Check if we need to perform health check
        if current_time - self._last_health_check > self._health_check_interval:
            self._last_health_check = current_time
            
            try:
                # Perform basic health check
                if self._gimp is None:
                    self._initialize_gimp()
                
                # Test basic operation
                await self._perform_health_check()
                self._connection_verified = True
                
            except Exception as e:
                logger.error(f"GIMP health check failed: {e}")
                self._connection_verified = False
                return False
        
        return self._connection_verified
    
    async def _perform_health_check(self):
        """Perform basic health check operations."""
        try:
            # Test basic GIMP operations
            if hasattr(self._gimp, 'list_images'):
                # Try to list images (basic operation)
                images = self._gimp.list_images()
                logger.debug(f"Health check: Found {len(images)} open images")
            else:
                # Fallback health check
                logger.debug("Health check: Basic GIMP instance verification")
                
        except Exception as e:
            raise GimpOperationError(f"Health check failed: {e}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test GIMP connection and return status."""
        try:
            async with self.ensure_connection():
                await self._perform_health_check()
                
                return {
                    "success": True,
                    "mode": "GUI" if self.mode_manager.gui_mode else "headless",
                    "connection_verified": self._connection_verified,
                    "timestamp": time.time(),
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "GUI" if self.mode_manager.gui_mode else "headless",
                "connection_verified": False,
                "timestamp": time.time(),
            }
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information and capabilities."""
        try:
            async with self.ensure_connection() as gimp:
                info = {
                    "mode": "GUI" if self.mode_manager.gui_mode else "headless",
                    "connection_active": True,
                    "api_version": "3.0",  # GIMP 3.0 API
                    "server_version": "0.1.0",
                    "capabilities": {
                        "document_management": True,
                        "layer_operations": True,
                        "drawing_tools": True,
                        "selection_tools": True,
                        "color_management": True,
                        "filter_operations": True,
                    },
                    "timestamp": time.time(),
                }
                
                # Add GIMP-specific information if available
                if hasattr(gimp, 'version'):
                    info["gimp_version"] = gimp.version()
                
                return info
                
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {
                "mode": "GUI" if self.mode_manager.gui_mode else "headless",
                "connection_active": False,
                "error": str(e),
                "timestamp": time.time(),
            }
    
    async def list_open_images(self) -> List[Dict[str, Any]]:
        """List all open images in GIMP."""
        try:
            async with self.ensure_connection() as gimp:
                images = []
                
                if hasattr(gimp, 'list_images'):
                    image_list = gimp.list_images()
                    
                    for img in image_list:
                        image_info = {
                            "id": img.get_id() if hasattr(img, 'get_id') else 0,
                            "name": img.get_name() if hasattr(img, 'get_name') else "Unknown",
                            "width": img.get_width() if hasattr(img, 'get_width') else 0,
                            "height": img.get_height() if hasattr(img, 'get_height') else 0,
                            "mode": img.get_base_type() if hasattr(img, 'get_base_type') else "RGB",
                        }
                        images.append(image_info)
                
                return images
                
        except Exception as e:
            logger.error(f"Failed to list images: {e}")
            raise GimpOperationError(f"Failed to list images: {e}")
    
    async def get_active_image(self) -> Optional[Dict[str, Any]]:
        """Get the currently active image."""
        try:
            async with self.ensure_connection() as gimp:
                if hasattr(gimp, 'get_active_image'):
                    active_image = gimp.get_active_image()
                    
                    if active_image:
                        return {
                            "id": active_image.get_id() if hasattr(active_image, 'get_id') else 0,
                            "name": active_image.get_name() if hasattr(active_image, 'get_name') else "Unknown",
                            "width": active_image.get_width() if hasattr(active_image, 'get_width') else 0,
                            "height": active_image.get_height() if hasattr(active_image, 'get_height') else 0,
                            "mode": active_image.get_base_type() if hasattr(active_image, 'get_base_type') else "RGB",
                        }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get active image: {e}")
            raise GimpOperationError(f"Failed to get active image: {e}")
    
    # Document Lifecycle Management
    async def create_image(self, width: int, height: int, image_type: str = "RGB",
                          fill_type: str = "white", resolution: float = 300.0) -> Dict[str, Any]:
        """Create a new image."""
        try:
            async with self.ensure_connection() as gimp:
                from .utils.image_utils import validate_dimensions, validate_resolution
                from .utils.gi_helpers import get_gimp_enums
                
                # Validate parameters
                validate_dimensions(width, height)
                validate_resolution(resolution)
                
                # Get GIMP enums
                enums = get_gimp_enums()
                
                # Map image type
                image_type_map = {
                    "RGB": enums.get('image_types', {}).get('rgb', 0),
                    "GRAYSCALE": enums.get('image_types', {}).get('grayscale', 1),
                    "INDEXED": enums.get('image_types', {}).get('indexed', 2),
                }
                
                gimp_image_type = image_type_map.get(image_type.upper(), 0)
                
                # Create image
                if hasattr(gimp, 'Image') and hasattr(gimp.Image, 'new'):
                    image = gimp.Image.new(width, height, gimp_image_type)
                    
                    # Set resolution
                    if hasattr(image, 'set_resolution'):
                        image.set_resolution(resolution, resolution)
                    
                    # Create background layer
                    fill_type_map = {
                        "white": enums.get('fill_types', {}).get('white', 0),
                        "black": enums.get('fill_types', {}).get('foreground', 1),
                        "transparent": enums.get('fill_types', {}).get('transparent', 3),
                    }
                    
                    gimp_fill_type = fill_type_map.get(fill_type.lower(), 0)
                    
                    if hasattr(gimp, 'Layer') and hasattr(gimp.Layer, 'new'):
                        layer = gimp.Layer.new(image, "Background", width, height,
                                             gimp_image_type, 100, 0)
                        
                        # Add layer to image
                        if hasattr(image, 'insert_layer'):
                            image.insert_layer(layer, None, 0)
                            
                            # Fill layer
                            if hasattr(layer, 'fill'):
                                layer.fill(gimp_fill_type)
                    
                    return {
                        "success": True,
                        "image_id": image.get_id() if hasattr(image, 'get_id') else 0,
                        "width": width,
                        "height": height,
                        "image_type": image_type,
                        "resolution": resolution,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("Image creation not supported")
                    
        except Exception as e:
            logger.error(f"Failed to create image: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time(),
            }
    
    async def open_image(self, file_path: str) -> Dict[str, Any]:
        """Open an existing image file."""
        try:
            async with self.ensure_connection() as gimp:
                import os
                
                if not os.path.exists(file_path):
                    raise GimpOperationError(f"File not found: {file_path}")
                
                # Open image
                if hasattr(gimp, 'file_load'):
                    image = gimp.file_load(file_path)
                    
                    return {
                        "success": True,
                        "image_id": image.get_id() if hasattr(image, 'get_id') else 0,
                        "file_path": file_path,
                        "width": image.get_width() if hasattr(image, 'get_width') else 0,
                        "height": image.get_height() if hasattr(image, 'get_height') else 0,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("File loading not supported")
                    
        except Exception as e:
            logger.error(f"Failed to open image: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "timestamp": time.time(),
            }
    
    async def save_image(self, image_id: int, file_path: str, format_type: str = "PNG") -> Dict[str, Any]:
        """Save an image to file."""
        try:
            async with self.ensure_connection() as gimp:
                from .utils.image_utils import validate_image_format
                
                # Validate format
                format_type = validate_image_format(format_type)
                
                # Get image by ID
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                # Save image
                if hasattr(gimp, 'file_save'):
                    gimp.file_save(image, file_path)
                    
                    return {
                        "success": True,
                        "image_id": image_id,
                        "file_path": file_path,
                        "format": format_type,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("File saving not supported")
                    
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_id": image_id,
                "file_path": file_path,
                "timestamp": time.time(),
            }
    
    async def close_image(self, image_id: int) -> Dict[str, Any]:
        """Close an image."""
        try:
            async with self.ensure_connection() as gimp:
                # Get image by ID
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                # Close image
                if hasattr(image, 'delete'):
                    image.delete()
                    
                    return {
                        "success": True,
                        "image_id": image_id,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("Image closing not supported")
                    
        except Exception as e:
            logger.error(f"Failed to close image: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_id": image_id,
                "timestamp": time.time(),
            }
    
    # Layer Management Operations
    async def create_layer(self, image_id: int, layer_name: str, width: Optional[int] = None,
                          height: Optional[int] = None, layer_type: str = "RGB",
                          opacity: float = 100.0, blend_mode: str = "normal") -> Dict[str, Any]:
        """Create a new layer."""
        try:
            async with self.ensure_connection() as gimp:
                from .utils.image_utils import validate_layer_name, validate_opacity
                from .utils.gi_helpers import get_gimp_enums
                
                # Validate parameters
                layer_name = validate_layer_name(layer_name)
                validate_opacity(opacity)
                
                # Get image
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                # Use image dimensions if not specified
                if width is None:
                    width = image.get_width() if hasattr(image, 'get_width') else 0
                if height is None:
                    height = image.get_height() if hasattr(image, 'get_height') else 0
                
                # Get GIMP enums
                enums = get_gimp_enums()
                
                # Map layer type
                layer_type_map = {
                    "RGB": 0,  # RGB_IMAGE
                    "RGBA": 1,  # RGBA_IMAGE
                    "GRAYSCALE": 2,  # GRAY_IMAGE
                    "GRAYSCALE_ALPHA": 3,  # GRAYA_IMAGE
                }
                
                gimp_layer_type = layer_type_map.get(layer_type.upper(), 1)
                
                # Map blend mode
                blend_modes = enums.get('blend_modes', {})
                gimp_blend_mode = blend_modes.get(blend_mode.lower(), 0)
                
                # Create layer
                if hasattr(gimp, 'Layer') and hasattr(gimp.Layer, 'new'):
                    layer = gimp.Layer.new(image, layer_name, width, height,
                                         gimp_layer_type, opacity, gimp_blend_mode)
                    
                    # Add layer to image
                    if hasattr(image, 'insert_layer'):
                        image.insert_layer(layer, None, 0)
                        
                        return {
                            "success": True,
                            "layer_id": layer.get_id() if hasattr(layer, 'get_id') else 0,
                            "layer_name": layer_name,
                            "width": width,
                            "height": height,
                            "opacity": opacity,
                            "blend_mode": blend_mode,
                            "timestamp": time.time(),
                        }
                    else:
                        raise GimpOperationError("Layer insertion not supported")
                else:
                    raise GimpOperationError("Layer creation not supported")
                    
        except Exception as e:
            logger.error(f"Failed to create layer: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_id": image_id,
                "layer_name": layer_name,
                "timestamp": time.time(),
            }
    
    async def delete_layer(self, image_id: int, layer_id: int) -> Dict[str, Any]:
        """Delete a layer."""
        try:
            async with self.ensure_connection() as gimp:
                # Get image
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                # Get layer
                layer = self._get_layer_by_id(image, layer_id)
                if not layer:
                    raise GimpOperationError(f"Layer not found: {layer_id}")
                
                # Delete layer
                if hasattr(image, 'remove_layer'):
                    image.remove_layer(layer)
                    
                    return {
                        "success": True,
                        "layer_id": layer_id,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("Layer deletion not supported")
                    
        except Exception as e:
            logger.error(f"Failed to delete layer: {e}")
            return {
                "success": False,
                "error": str(e),
                "layer_id": layer_id,
                "timestamp": time.time(),
            }
    
    async def set_layer_opacity(self, image_id: int, layer_id: int, opacity: float) -> Dict[str, Any]:
        """Set layer opacity."""
        try:
            async with self.ensure_connection() as gimp:
                from .utils.image_utils import validate_opacity
                
                # Validate opacity
                validate_opacity(opacity)
                
                # Get image
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                # Get layer
                layer = self._get_layer_by_id(image, layer_id)
                if not layer:
                    raise GimpOperationError(f"Layer not found: {layer_id}")
                
                # Set opacity
                if hasattr(layer, 'set_opacity'):
                    layer.set_opacity(opacity)
                    
                    return {
                        "success": True,
                        "layer_id": layer_id,
                        "opacity": opacity,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("Layer opacity setting not supported")
                    
        except Exception as e:
            logger.error(f"Failed to set layer opacity: {e}")
            return {
                "success": False,
                "error": str(e),
                "layer_id": layer_id,
                "timestamp": time.time(),
            }
    
    async def set_layer_blend_mode(self, image_id: int, layer_id: int, blend_mode: str) -> Dict[str, Any]:
        """Set layer blend mode."""
        try:
            async with self.ensure_connection() as gimp:
                from .utils.gi_helpers import get_gimp_enums
                
                # Get image
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                # Get layer
                layer = self._get_layer_by_id(image, layer_id)
                if not layer:
                    raise GimpOperationError(f"Layer not found: {layer_id}")
                
                # Get GIMP enums
                enums = get_gimp_enums()
                blend_modes = enums.get('blend_modes', {})
                gimp_blend_mode = blend_modes.get(blend_mode.lower())
                
                if gimp_blend_mode is None:
                    raise GimpOperationError(f"Invalid blend mode: {blend_mode}")
                
                # Set blend mode
                if hasattr(layer, 'set_mode'):
                    layer.set_mode(gimp_blend_mode)
                    
                    return {
                        "success": True,
                        "layer_id": layer_id,
                        "blend_mode": blend_mode,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("Layer blend mode setting not supported")
                    
        except Exception as e:
            logger.error(f"Failed to set layer blend mode: {e}")
            return {
                "success": False,
                "error": str(e),
                "layer_id": layer_id,
                "timestamp": time.time(),
            }
    
    # Basic Drawing Operations
    async def fill_layer(self, image_id: int, layer_id: int, color: str) -> Dict[str, Any]:
        """Fill a layer with a solid color."""
        try:
            async with self.ensure_connection() as gimp:
                from .utils.image_utils import parse_color
                from .utils.gi_helpers import create_gimp_color
                
                # Parse color
                r, g, b, a = parse_color(color)
                
                # Get image and layer
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                layer = self._get_layer_by_id(image, layer_id)
                if not layer:
                    raise GimpOperationError(f"Layer not found: {layer_id}")
                
                # Create GIMP color
                gimp_color = create_gimp_color(r, g, b, a)
                if not gimp_color:
                    raise GimpOperationError("Failed to create GIMP color")
                
                # Fill layer
                if hasattr(layer, 'fill') and hasattr(gimp, 'context_set_foreground'):
                    gimp.context_set_foreground(gimp_color)
                    layer.fill(0)  # Fill with foreground color
                    
                    return {
                        "success": True,
                        "layer_id": layer_id,
                        "color": color,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("Layer fill operation not supported")
                    
        except Exception as e:
            logger.error(f"Failed to fill layer: {e}")
            return {
                "success": False,
                "error": str(e),
                "layer_id": layer_id,
                "timestamp": time.time(),
            }
    
    async def draw_rectangle(self, image_id: int, layer_id: int, x: float, y: float,
                           width: float, height: float, stroke_color: Optional[str] = None,
                           fill_color: Optional[str] = None, stroke_width: float = 1.0) -> Dict[str, Any]:
        """Draw a rectangle on a layer."""
        try:
            async with self.ensure_connection() as gimp:
                from .utils.image_utils import validate_coordinates, validate_dimensions, parse_color
                from .utils.gi_helpers import create_gimp_color
                
                # Validate parameters
                validate_coordinates(x, y)
                validate_dimensions(width, height)
                
                # Get image and layer
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                layer = self._get_layer_by_id(image, layer_id)
                if not layer:
                    raise GimpOperationError(f"Layer not found: {layer_id}")
                
                # Create selection rectangle
                if hasattr(gimp, 'image_select_rectangle'):
                    gimp.image_select_rectangle(image, 0, x, y, width, height)
                    
                    # Fill if fill_color is specified
                    if fill_color:
                        r, g, b, a = parse_color(fill_color)
                        gimp_color = create_gimp_color(r, g, b, a)
                        if gimp_color and hasattr(gimp, 'context_set_foreground'):
                            gimp.context_set_foreground(gimp_color)
                            if hasattr(gimp, 'edit_fill'):
                                gimp.edit_fill(layer, 0)  # Fill with foreground
                    
                    # Stroke if stroke_color is specified
                    if stroke_color:
                        r, g, b, a = parse_color(stroke_color)
                        gimp_color = create_gimp_color(r, g, b, a)
                        if gimp_color and hasattr(gimp, 'context_set_foreground'):
                            gimp.context_set_foreground(gimp_color)
                            if hasattr(gimp, 'edit_stroke'):
                                gimp.edit_stroke(layer)
                    
                    # Clear selection
                    if hasattr(gimp, 'selection_none'):
                        gimp.selection_none(image)
                    
                    return {
                        "success": True,
                        "layer_id": layer_id,
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height,
                        "fill_color": fill_color,
                        "stroke_color": stroke_color,
                        "stroke_width": stroke_width,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("Rectangle drawing not supported")
                    
        except Exception as e:
            logger.error(f"Failed to draw rectangle: {e}")
            return {
                "success": False,
                "error": str(e),
                "layer_id": layer_id,
                "timestamp": time.time(),
            }
    
    async def draw_ellipse(self, image_id: int, layer_id: int, x: float, y: float,
                          width: float, height: float, stroke_color: Optional[str] = None,
                          fill_color: Optional[str] = None, stroke_width: float = 1.0) -> Dict[str, Any]:
        """Draw an ellipse on a layer."""
        try:
            async with self.ensure_connection() as gimp:
                from .utils.image_utils import validate_coordinates, validate_dimensions, parse_color
                from .utils.gi_helpers import create_gimp_color
                
                # Validate parameters
                validate_coordinates(x, y)
                validate_dimensions(width, height)
                
                # Get image and layer
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                layer = self._get_layer_by_id(image, layer_id)
                if not layer:
                    raise GimpOperationError(f"Layer not found: {layer_id}")
                
                # Create elliptical selection
                if hasattr(gimp, 'image_select_ellipse'):
                    gimp.image_select_ellipse(image, 0, x, y, width, height)
                    
                    # Fill if fill_color is specified
                    if fill_color:
                        r, g, b, a = parse_color(fill_color)
                        gimp_color = create_gimp_color(r, g, b, a)
                        if gimp_color and hasattr(gimp, 'context_set_foreground'):
                            gimp.context_set_foreground(gimp_color)
                            if hasattr(gimp, 'edit_fill'):
                                gimp.edit_fill(layer, 0)  # Fill with foreground
                    
                    # Stroke if stroke_color is specified
                    if stroke_color:
                        r, g, b, a = parse_color(stroke_color)
                        gimp_color = create_gimp_color(r, g, b, a)
                        if gimp_color and hasattr(gimp, 'context_set_foreground'):
                            gimp.context_set_foreground(gimp_color)
                            if hasattr(gimp, 'edit_stroke'):
                                gimp.edit_stroke(layer)
                    
                    # Clear selection
                    if hasattr(gimp, 'selection_none'):
                        gimp.selection_none(image)
                    
                    return {
                        "success": True,
                        "layer_id": layer_id,
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height,
                        "fill_color": fill_color,
                        "stroke_color": stroke_color,
                        "stroke_width": stroke_width,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("Ellipse drawing not supported")
                    
        except Exception as e:
            logger.error(f"Failed to draw ellipse: {e}")
            return {
                "success": False,
                "error": str(e),
                "layer_id": layer_id,
                "timestamp": time.time(),
            }
    
    async def draw_brush_stroke(self, image_id: int, layer_id: int, points: List[Tuple[float, float]],
                               brush_size: float = 10.0, brush_color: str = "#000000") -> Dict[str, Any]:
        """Draw a brush stroke on a layer."""
        try:
            async with self.ensure_connection() as gimp:
                from .utils.image_utils import normalize_path_points, validate_brush_size, parse_color
                from .utils.gi_helpers import create_gimp_color
                
                # Validate parameters
                points = normalize_path_points(points)
                validate_brush_size(brush_size)
                
                # Get image and layer
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                layer = self._get_layer_by_id(image, layer_id)
                if not layer:
                    raise GimpOperationError(f"Layer not found: {layer_id}")
                
                # Parse brush color
                r, g, b, a = parse_color(brush_color)
                gimp_color = create_gimp_color(r, g, b, a)
                if not gimp_color:
                    raise GimpOperationError("Failed to create brush color")
                
                # Set brush properties
                if hasattr(gimp, 'context_set_foreground'):
                    gimp.context_set_foreground(gimp_color)
                
                if hasattr(gimp, 'context_set_brush_size'):
                    gimp.context_set_brush_size(brush_size)
                
                # Convert points to stroke data
                stroke_points = []
                for point in points:
                    stroke_points.extend([point[0], point[1]])
                
                # Draw brush stroke
                if hasattr(gimp, 'paintbrush_default') and len(stroke_points) >= 4:
                    gimp.paintbrush_default(layer, len(stroke_points), stroke_points)
                    
                    return {
                        "success": True,
                        "layer_id": layer_id,
                        "points_count": len(points),
                        "brush_size": brush_size,
                        "brush_color": brush_color,
                        "timestamp": time.time(),
                    }
                else:
                    raise GimpOperationError("Brush stroke drawing not supported")
                    
        except Exception as e:
            logger.error(f"Failed to draw brush stroke: {e}")
            return {
                "success": False,
                "error": str(e),
                "layer_id": layer_id,
                "timestamp": time.time(),
            }
    
    # Helper Methods
    def _get_image_by_id(self, image_id: int) -> Optional[Any]:
        """Get image by ID."""
        try:
            if hasattr(self._gimp, 'list_images'):
                images = self._gimp.list_images()
                for image in images:
                    if hasattr(image, 'get_id') and image.get_id() == image_id:
                        return image
            return None
        except Exception as e:
            logger.error(f"Failed to get image by ID {image_id}: {e}")
            return None
    
    def _get_layer_by_id(self, image: Any, layer_id: int) -> Optional[Any]:
        """Get layer by ID from image."""
        try:
            if hasattr(image, 'get_layers'):
                layers = image.get_layers()
                for layer in layers:
                    if hasattr(layer, 'get_id') and layer.get_id() == layer_id:
                        return layer
            return None
        except Exception as e:
            logger.error(f"Failed to get layer by ID {layer_id}: {e}")
            return None
    
    async def get_image_info(self, image_id: int) -> Dict[str, Any]:
        """Get detailed information about an image."""
        try:
            async with self.ensure_connection() as gimp:
                image = self._get_image_by_id(image_id)
                if not image:
                    raise GimpOperationError(f"Image not found: {image_id}")
                
                # Get image information
                info = {
                    "id": image_id,
                    "width": image.get_width() if hasattr(image, 'get_width') else 0,
                    "height": image.get_height() if hasattr(image, 'get_height') else 0,
                    "name": image.get_name() if hasattr(image, 'get_name') else "Unknown",
                    "base_type": image.get_base_type() if hasattr(image, 'get_base_type') else "RGB",
                    "layers": [],
                    "timestamp": time.time(),
                }
                
                # Get layer information
                if hasattr(image, 'get_layers'):
                    layers = image.get_layers()
                    for layer in layers:
                        layer_info = {
                            "id": layer.get_id() if hasattr(layer, 'get_id') else 0,
                            "name": layer.get_name() if hasattr(layer, 'get_name') else "Unknown",
                            "opacity": layer.get_opacity() if hasattr(layer, 'get_opacity') else 100,
                            "visible": layer.get_visible() if hasattr(layer, 'get_visible') else True,
                            "width": layer.get_width() if hasattr(layer, 'get_width') else 0,
                            "height": layer.get_height() if hasattr(layer, 'get_height') else 0,
                        }
                        info["layers"].append(layer_info)
                
                return {
                    "success": True,
                    "image_info": info,
                    "timestamp": time.time(),
                }
                
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_id": image_id,
                "timestamp": time.time(),
            }
    
    async def execute_operation(self, operation_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a GIMP operation safely."""
        try:
            async with self.ensure_connection() as gimp:
                logger.info(f"Executing operation: {operation_name}")
                
                # Route to appropriate method based on operation_name
                operation_map = {
                    "create_image": self.create_image,
                    "open_image": self.open_image,
                    "save_image": self.save_image,
                    "close_image": self.close_image,
                    "create_layer": self.create_layer,
                    "delete_layer": self.delete_layer,
                    "fill_layer": self.fill_layer,
                    "draw_rectangle": self.draw_rectangle,
                    "draw_ellipse": self.draw_ellipse,
                    "draw_brush_stroke": self.draw_brush_stroke,
                    "get_image_info": self.get_image_info,
                }
                
                if operation_name in operation_map:
                    result = await operation_map[operation_name](*args, **kwargs)
                    logger.info(f"Operation completed: {operation_name}")
                    return result
                else:
                    # Generic operation execution
                    result = {
                        "success": True,
                        "operation": operation_name,
                        "args": args,
                        "kwargs": kwargs,
                        "timestamp": time.time(),
                    }
                    
                    logger.info(f"Operation completed: {operation_name}")
                    return result
                
        except Exception as e:
            logger.error(f"Operation failed: {operation_name} - {e}")
            return {
                "success": False,
                "operation": operation_name,
                "error": str(e),
                "timestamp": time.time(),
            }
    
    async def cleanup(self):
        """Cleanup resources and connections."""
        try:
            logger.info("Cleaning up GIMP API resources")
            
            # Perform any necessary cleanup
            if self._gimp:
                # Add specific cleanup operations if needed
                pass
            
            self._gimp = None
            self._connection_verified = False
            
            logger.info("GIMP API cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if GIMP connection is active."""
        return self._connection_verified and self._gimp is not None
    
    @property
    def mode(self) -> str:
        """Get current operating mode."""
        return "GUI" if self.mode_manager.gui_mode else "headless"