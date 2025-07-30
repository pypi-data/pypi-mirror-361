"""
Mock GIMP implementation for testing.

This module provides comprehensive mock implementations of GIMP
classes and functions for testing without requiring actual GIMP.
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from unittest.mock import Mock, MagicMock


class MockGimpImage:
    """Mock GIMP Image class."""
    
    def __init__(self, image_id: int, name: str = "Test Image", 
                 width: int = 800, height: int = 600, base_type: int = 0):
        self._id = image_id
        self._name = name
        self._width = width
        self._height = height
        self._base_type = base_type
        self._layers = []
        self._resolution = (300.0, 300.0)
        self._dirty = False
        
    def get_id(self) -> int:
        return self._id
        
    def get_name(self) -> str:
        return self._name
        
    def set_name(self, name: str):
        self._name = name
        
    def get_width(self) -> int:
        return self._width
        
    def get_height(self) -> int:
        return self._height
        
    def get_base_type(self) -> int:
        return self._base_type
        
    def get_layers(self) -> List['MockGimpLayer']:
        return self._layers.copy()
        
    def get_resolution(self) -> Tuple[float, float]:
        return self._resolution
        
    def set_resolution(self, x_res: float, y_res: float):
        self._resolution = (x_res, y_res)
        
    def insert_layer(self, layer: 'MockGimpLayer', parent: Optional['MockGimpLayer'] = None, position: int = 0):
        """Insert a layer into the image."""
        if layer not in self._layers:
            self._layers.insert(position, layer)
            layer._parent_image = self
            self._dirty = True
            
    def remove_layer(self, layer: 'MockGimpLayer'):
        """Remove a layer from the image."""
        if layer in self._layers:
            self._layers.remove(layer)
            layer._parent_image = None
            self._dirty = True
            
    def delete(self):
        """Delete the image (mock implementation)."""
        self._layers.clear()
        
    def flatten(self) -> 'MockGimpLayer':
        """Flatten image to single layer."""
        if not self._layers:
            return None
            
        # Create flattened layer
        flattened = MockGimpLayer(1, "Flattened", self._width, self._height, 0)
        flattened._parent_image = self
        
        # Clear existing layers and add flattened
        self._layers.clear()
        self._layers.append(flattened)
        
        return flattened
        
    def is_dirty(self) -> bool:
        """Check if image has unsaved changes."""
        return self._dirty
        
    def clean_all(self):
        """Mark image as clean (saved)."""
        self._dirty = False


class MockGimpLayer:
    """Mock GIMP Layer class."""
    
    def __init__(self, layer_id: int, name: str, width: int, height: int, 
                 layer_type: int = 0, opacity: float = 100.0, mode: int = 0):
        self._id = layer_id
        self._name = name
        self._width = width
        self._height = height
        self._type = layer_type
        self._opacity = opacity
        self._mode = mode
        self._visible = True
        self._parent_image = None
        self._offset = (0, 0)
        
    def get_id(self) -> int:
        return self._id
        
    def get_name(self) -> str:
        return self._name
        
    def set_name(self, name: str):
        self._name = name
        
    def get_width(self) -> int:
        return self._width
        
    def get_height(self) -> int:
        return self._height
        
    def get_opacity(self) -> float:
        return self._opacity
        
    def set_opacity(self, opacity: float):
        self._opacity = max(0.0, min(100.0, opacity))
        
    def get_mode(self) -> int:
        return self._mode
        
    def set_mode(self, mode: int):
        self._mode = mode
        
    def get_visible(self) -> bool:
        return self._visible
        
    def set_visible(self, visible: bool):
        self._visible = visible
        
    def get_offsets(self) -> Tuple[int, int]:
        return self._offset
        
    def set_offsets(self, x: int, y: int):
        self._offset = (x, y)
        
    def fill(self, fill_type: int):
        """Fill layer with specified fill type."""
        # Mock implementation - just mark as filled
        pass
        
    def resize(self, width: int, height: int, offset_x: int = 0, offset_y: int = 0):
        """Resize the layer."""
        self._width = width
        self._height = height
        self._offset = (offset_x, offset_y)


class MockGimpDrawable:
    """Mock GIMP Drawable class."""
    
    def __init__(self, drawable_id: int):
        self._id = drawable_id
        
    def get_id(self) -> int:
        return self._id


class MockGimpColor:
    """Mock GIMP Color class."""
    
    def __init__(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        
    def set_rgb(self, r: float, g: float, b: float):
        self.r = r
        self.g = g
        self.b = b
        
    def set_rgba(self, r: float, g: float, b: float, a: float):
        self.r = r
        self.g = g
        self.b = b
        self.a = a


class MockGimpContext:
    """Mock GIMP Context class."""
    
    def __init__(self):
        self.foreground = MockGimpColor()
        self.background = MockGimpColor(1.0, 1.0, 1.0)
        self.brush_size = 10.0
        self.brush_name = "2. Hardness 050"
        
    def get_foreground(self) -> MockGimpColor:
        return self.foreground
        
    def set_foreground(self, color: MockGimpColor):
        self.foreground = color
        
    def get_background(self) -> MockGimpColor:
        return self.background
        
    def set_background(self, color: MockGimpColor):
        self.background = color
        
    def get_brush_size(self) -> float:
        return self.brush_size
        
    def set_brush_size(self, size: float):
        self.brush_size = size
        
    def get_brush(self) -> str:
        return self.brush_name
        
    def set_brush(self, name: str):
        self.brush_name = name


class MockGimpAPI:
    """Mock GIMP API class providing all core functionality."""
    
    def __init__(self):
        self._images = {}
        self._next_image_id = 1
        self._next_layer_id = 1
        self._active_image = None
        self._context = MockGimpContext()
        
        # Mock version info
        self._version = "2.10.32"
        
        # Create some sample images for testing
        self._create_sample_images()
        
    def _create_sample_images(self):
        """Create sample images for testing."""
        # Create test image
        image = MockGimpImage(self._next_image_id, "Test Image", 800, 600)
        self._images[self._next_image_id] = image
        self._next_image_id += 1
        
        # Add background layer
        layer = MockGimpLayer(self._next_layer_id, "Background", 800, 600)
        image.insert_layer(layer)
        self._next_layer_id += 1
        
        self._active_image = image
        
    def version(self) -> str:
        """Get GIMP version."""
        return self._version
        
    def list_images(self) -> List[MockGimpImage]:
        """List all open images."""
        return list(self._images.values())
        
    def get_active_image(self) -> Optional[MockGimpImage]:
        """Get currently active image."""
        return self._active_image
        
    def set_active_image(self, image: MockGimpImage):
        """Set active image."""
        if image.get_id() in self._images:
            self._active_image = image
            
    def file_load(self, filename: str) -> MockGimpImage:
        """Load image from file."""
        import os
        
        # Mock file loading
        image_id = self._next_image_id
        self._next_image_id += 1
        
        # Create mock image based on filename
        basename = os.path.basename(filename)
        image = MockGimpImage(image_id, basename, 1024, 768)
        
        # Add background layer
        layer = MockGimpLayer(self._next_layer_id, "Background", 1024, 768)
        image.insert_layer(layer)
        self._next_layer_id += 1
        
        self._images[image_id] = image
        self._active_image = image
        
        return image
        
    def file_save(self, image: MockGimpImage, filename: str):
        """Save image to file."""
        # Mock file saving
        image.clean_all()
        
    def context_get_foreground(self) -> MockGimpColor:
        """Get foreground color."""
        return self._context.get_foreground()
        
    def context_set_foreground(self, color: MockGimpColor):
        """Set foreground color."""
        self._context.set_foreground(color)
        
    def context_get_background(self) -> MockGimpColor:
        """Get background color."""
        return self._context.get_background()
        
    def context_set_background(self, color: MockGimpColor):
        """Set background color."""
        self._context.set_background(color)
        
    def context_get_brush_size(self) -> float:
        """Get brush size."""
        return self._context.get_brush_size()
        
    def context_set_brush_size(self, size: float):
        """Set brush size."""
        self._context.set_brush_size(size)
        
    def image_select_rectangle(self, image: MockGimpImage, operation: int, 
                              x: float, y: float, width: float, height: float):
        """Create rectangular selection."""
        # Mock selection operation
        pass
        
    def image_select_ellipse(self, image: MockGimpImage, operation: int,
                           x: float, y: float, width: float, height: float):
        """Create elliptical selection."""
        # Mock selection operation
        pass
        
    def selection_none(self, image: MockGimpImage):
        """Clear selection."""
        # Mock selection clearing
        pass
        
    def edit_fill(self, drawable: MockGimpDrawable, fill_type: int):
        """Fill drawable with specified fill type."""
        # Mock fill operation
        pass
        
    def edit_stroke(self, drawable: MockGimpDrawable):
        """Stroke current selection."""
        # Mock stroke operation
        pass
        
    def paintbrush_default(self, drawable: MockGimpDrawable, num_strokes: int, strokes: List[float]):
        """Apply brush stroke."""
        # Mock brush stroke
        pass
        
    def create_image(self, width: int, height: int, image_type: int) -> MockGimpImage:
        """Create new image."""
        image_id = self._next_image_id
        self._next_image_id += 1
        
        image = MockGimpImage(image_id, "Untitled", width, height, image_type)
        self._images[image_id] = image
        self._active_image = image
        
        return image
        
    def create_layer(self, image: MockGimpImage, name: str, width: int, height: int,
                    layer_type: int, opacity: float = 100.0, mode: int = 0) -> MockGimpLayer:
        """Create new layer."""
        layer_id = self._next_layer_id
        self._next_layer_id += 1
        
        layer = MockGimpLayer(layer_id, name, width, height, layer_type, opacity, mode)
        return layer


class MockGimpEnums:
    """Mock GIMP enums and constants."""
    
    class ImageBaseType:
        RGB = 0
        GRAY = 1
        INDEXED = 2
        
    class ImageType:
        RGB_IMAGE = 0
        RGBA_IMAGE = 1
        GRAY_IMAGE = 2
        GRAYA_IMAGE = 3
        INDEXED_IMAGE = 4
        INDEXEDA_IMAGE = 5
        
    class LayerMode:
        NORMAL = 0
        MULTIPLY = 1
        SCREEN = 2
        OVERLAY = 3
        DIFFERENCE = 4
        ADDITION = 5
        SUBTRACT = 6
        DARKEN_ONLY = 7
        LIGHTEN_ONLY = 8
        
    class FillType:
        FOREGROUND = 0
        BACKGROUND = 1
        WHITE = 2
        TRANSPARENT = 3
        PATTERN = 4
        
    class SelectionOp:
        REPLACE = 0
        ADD = 1
        SUBTRACT = 2
        INTERSECT = 3


def create_mock_gimp_modules() -> Dict[str, Any]:
    """Create mock GIMP modules for testing."""
    
    # Create mock GIMP API instance
    gimp_api = MockGimpAPI()
    
    # Create mock Gimp module
    gimp_module = Mock()
    gimp_module.version = Mock(return_value=gimp_api.version())
    gimp_module.list_images = Mock(return_value=gimp_api.list_images())
    gimp_module.get_active_image = Mock(return_value=gimp_api.get_active_image())
    gimp_module.set_active_image = Mock(side_effect=gimp_api.set_active_image)
    gimp_module.file_load = Mock(side_effect=gimp_api.file_load)
    gimp_module.file_save = Mock(side_effect=gimp_api.file_save)
    gimp_module.context_get_foreground = Mock(return_value=gimp_api.context_get_foreground())
    gimp_module.context_set_foreground = Mock(side_effect=gimp_api.context_set_foreground)
    gimp_module.context_get_background = Mock(return_value=gimp_api.context_get_background())
    gimp_module.context_set_background = Mock(side_effect=gimp_api.context_set_background)
    gimp_module.context_get_brush_size = Mock(return_value=gimp_api.context_get_brush_size())
    gimp_module.context_set_brush_size = Mock(side_effect=gimp_api.context_set_brush_size)
    gimp_module.image_select_rectangle = Mock(side_effect=gimp_api.image_select_rectangle)
    gimp_module.image_select_ellipse = Mock(side_effect=gimp_api.image_select_ellipse)
    gimp_module.selection_none = Mock(side_effect=gimp_api.selection_none)
    gimp_module.edit_fill = Mock(side_effect=gimp_api.edit_fill)
    gimp_module.edit_stroke = Mock(side_effect=gimp_api.edit_stroke)
    gimp_module.paintbrush_default = Mock(side_effect=gimp_api.paintbrush_default)
    
    # Add class constructors
    gimp_module.Image = Mock()
    gimp_module.Image.new = Mock(side_effect=gimp_api.create_image)
    
    gimp_module.Layer = Mock()
    gimp_module.Layer.new = Mock(side_effect=gimp_api.create_layer)
    
    gimp_module.Color = MockGimpColor
    
    # Add enums
    for enum_name in dir(MockGimpEnums):
        if not enum_name.startswith('_'):
            setattr(gimp_module, enum_name, getattr(MockGimpEnums, enum_name))
    
    return {
        'Gimp': gimp_module,
        'gimp_api': gimp_api,
        'enums': MockGimpEnums,
    }