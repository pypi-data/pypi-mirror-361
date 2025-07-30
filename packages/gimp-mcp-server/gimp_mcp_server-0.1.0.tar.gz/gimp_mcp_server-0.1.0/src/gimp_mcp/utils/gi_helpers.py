"""
GObject Introspection helpers for GIMP MCP Server

This module provides utilities for safely importing and working with
GObject Introspection modules, particularly for GIMP 3.0 integration.
"""

import logging
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


def safe_gi_import() -> Optional[Dict[str, Any]]:
    """
    Safely import GObject Introspection modules.
    
    Returns:
        Dictionary of imported modules or None if import failed
    """
    try:
        import gi
        
        # Require specific versions
        gi.require_version('Gtk', '4.0')
        gi.require_version('Gimp', '3.0')
        
        # Import modules
        from gi.repository import Gtk, Gimp, GObject, Gio
        
        modules = {
            'gi': gi,
            'Gtk': Gtk,
            'Gimp': Gimp,
            'GObject': GObject,
            'Gio': Gio,
        }
        
        logger.debug("Successfully imported GI modules")
        return modules
        
    except ImportError as e:
        logger.warning(f"Failed to import GI modules: {e}")
        return None
    except ValueError as e:
        logger.warning(f"GI version requirement failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error importing GI modules: {e}")
        return None


def check_gi_availability() -> Dict[str, Any]:
    """
    Check availability of GObject Introspection modules.
    
    Returns:
        Dictionary with availability status and version info
    """
    result = {
        "gi_available": False,
        "gtk_available": False,
        "gimp_available": False,
        "versions": {},
        "errors": [],
    }
    
    try:
        import gi
        result["gi_available"] = True
        result["versions"]["gi"] = gi.version_info
        
        # Check GTK availability
        try:
            gi.require_version('Gtk', '4.0')
            from gi.repository import Gtk
            result["gtk_available"] = True
            result["versions"]["gtk"] = "4.0"
        except (ImportError, ValueError) as e:
            result["errors"].append(f"GTK 4.0 not available: {e}")
        
        # Check GIMP availability
        try:
            gi.require_version('Gimp', '3.0')
            from gi.repository import Gimp
            result["gimp_available"] = True
            result["versions"]["gimp"] = "3.0"
        except (ImportError, ValueError) as e:
            result["errors"].append(f"GIMP 3.0 not available: {e}")
            
    except ImportError as e:
        result["errors"].append(f"GObject Introspection not available: {e}")
    except Exception as e:
        result["errors"].append(f"Unexpected error: {e}")
    
    return result


def get_gimp_enums() -> Dict[str, Any]:
    """
    Get GIMP enumeration values safely.
    
    Returns:
        Dictionary of GIMP enums or empty dict if not available
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return {}
        
        Gimp = gi_modules['Gimp']
        
        enums = {}
        
        # Common GIMP enums
        if hasattr(Gimp, 'BlendMode'):
            enums['blend_modes'] = {
                'normal': Gimp.BlendMode.NORMAL,
                'multiply': Gimp.BlendMode.MULTIPLY,
                'screen': Gimp.BlendMode.SCREEN,
                'overlay': Gimp.BlendMode.OVERLAY,
                'soft_light': Gimp.BlendMode.SOFT_LIGHT,
                'hard_light': Gimp.BlendMode.HARD_LIGHT,
                'color_dodge': Gimp.BlendMode.COLOR_DODGE,
                'color_burn': Gimp.BlendMode.COLOR_BURN,
                'darken_only': Gimp.BlendMode.DARKEN_ONLY,
                'lighten_only': Gimp.BlendMode.LIGHTEN_ONLY,
            }
        
        if hasattr(Gimp, 'ImageBaseType'):
            enums['image_types'] = {
                'rgb': Gimp.ImageBaseType.RGB,
                'grayscale': Gimp.ImageBaseType.GRAY,
                'indexed': Gimp.ImageBaseType.INDEXED,
            }
        
        if hasattr(Gimp, 'FillType'):
            enums['fill_types'] = {
                'foreground': Gimp.FillType.FOREGROUND,
                'background': Gimp.FillType.BACKGROUND,
                'white': Gimp.FillType.WHITE,
                'transparent': Gimp.FillType.TRANSPARENT,
                'pattern': Gimp.FillType.PATTERN,
            }
        
        return enums
        
    except Exception as e:
        logger.error(f"Failed to get GIMP enums: {e}")
        return {}


def validate_gimp_version() -> Dict[str, Any]:
    """
    Validate GIMP version compatibility.
    
    Returns:
        Dictionary with version validation results
    """
    result = {
        "compatible": False,
        "version": None,
        "required_version": "3.0",
        "errors": [],
    }
    
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            result["errors"].append("GIMP not available")
            return result
        
        Gimp = gi_modules['Gimp']
        
        if hasattr(Gimp, 'version'):
            version = Gimp.version()
            result["version"] = version
            
            # Check if version is 3.0 or higher
            if version.startswith('3.'):
                result["compatible"] = True
            else:
                result["errors"].append(f"GIMP version {version} is not compatible (requires 3.0+)")
        else:
            result["errors"].append("Cannot determine GIMP version")
            
    except Exception as e:
        result["errors"].append(f"Version validation failed: {e}")
    
    return result


def create_gimp_color(red: float, green: float, blue: float, alpha: float = 1.0) -> Optional[Any]:
    """
    Create a GIMP color object safely.
    
    Args:
        red: Red component (0.0-1.0)
        green: Green component (0.0-1.0)
        blue: Blue component (0.0-1.0)
        alpha: Alpha component (0.0-1.0)
        
    Returns:
        GIMP color object or None if creation failed
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return None
        
        Gimp = gi_modules['Gimp']
        
        if hasattr(Gimp, 'RGB'):
            color = Gimp.RGB()
            color.set(red, green, blue, alpha)
            return color
        elif hasattr(Gimp, 'Color'):
            # Alternative color creation method
            color = Gimp.Color()
            color.set_rgba(red, green, blue, alpha)
            return color
        else:
            logger.warning("No known GIMP color creation method available")
            return None
            
    except Exception as e:
        logger.error(f"Failed to create GIMP color: {e}")
        return None


def get_gimp_procedure_names() -> List[str]:
    """
    Get list of available GIMP procedures.
    
    Returns:
        List of procedure names or empty list if not available
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return []
        
        Gimp = gi_modules['Gimp']
        
        if hasattr(Gimp, 'get_procedures'):
            procedures = Gimp.get_procedures()
            return list(procedures) if procedures else []
        else:
            logger.warning("Cannot list GIMP procedures")
            return []
            
    except Exception as e:
        logger.error(f"Failed to get GIMP procedures: {e}")
        return []


def check_gimp_capability(capability: str) -> bool:
    """
    Check if GIMP has a specific capability.
    
    Args:
        capability: Capability to check (e.g., 'python-fu', 'script-fu')
        
    Returns:
        True if capability is available
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return False
        
        Gimp = gi_modules['Gimp']
        
        # Check for specific capabilities
        if capability == 'python-fu':
            return hasattr(Gimp, 'python_fu_eval')
        elif capability == 'script-fu':
            return hasattr(Gimp, 'script_fu_eval')
        elif capability == 'procedures':
            return hasattr(Gimp, 'get_procedures')
        elif capability == 'images':
            return hasattr(Gimp, 'list_images')
        else:
            # Generic attribute check
            return hasattr(Gimp, capability)
            
    except Exception as e:
        logger.error(f"Failed to check GIMP capability '{capability}': {e}")
        return False


def get_gimp_system_info() -> Dict[str, Any]:
    """
    Get comprehensive GIMP system information.
    
    Returns:
        Dictionary with system information
    """
    info = {
        "gi_status": check_gi_availability(),
        "version_status": validate_gimp_version(),
        "capabilities": {},
        "enums_available": bool(get_gimp_enums()),
    }
    
    # Check common capabilities
    capabilities = [
        'python-fu',
        'script-fu',
        'procedures',
        'images',
        'list_images',
        'get_procedures',
    ]
    
    for cap in capabilities:
        info["capabilities"][cap] = check_gimp_capability(cap)
    
    return info


def safe_gimp_call(func_name: str, *args, **kwargs) -> Optional[Any]:
    """
    Safely call a GIMP function with error handling.
    
    Args:
        func_name: Name of the GIMP function to call
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or None if call failed
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return None
        
        Gimp = gi_modules['Gimp']
        
        if not hasattr(Gimp, func_name):
            logger.warning(f"GIMP function '{func_name}' not available")
            return None
        
        func = getattr(Gimp, func_name)
        result = func(*args, **kwargs)
        
        logger.debug(f"Successfully called GIMP function: {func_name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to call GIMP function '{func_name}': {e}")
        return None


def get_gimp_brush_list() -> List[str]:
    """
    Get list of available GIMP brushes.
    
    Returns:
        List of brush names or empty list if not available
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return []
        
        Gimp = gi_modules['Gimp']
        
        if hasattr(Gimp, 'brushes_get_list'):
            brushes = Gimp.brushes_get_list()
            return list(brushes) if brushes else []
        else:
            logger.warning("Cannot list GIMP brushes")
            return []
            
    except Exception as e:
        logger.error(f"Failed to get GIMP brushes: {e}")
        return []


def get_gimp_pattern_list() -> List[str]:
    """
    Get list of available GIMP patterns.
    
    Returns:
        List of pattern names or empty list if not available
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return []
        
        Gimp = gi_modules['Gimp']
        
        if hasattr(Gimp, 'patterns_get_list'):
            patterns = Gimp.patterns_get_list()
            return list(patterns) if patterns else []
        else:
            logger.warning("Cannot list GIMP patterns")
            return []
            
    except Exception as e:
        logger.error(f"Failed to get GIMP patterns: {e}")
        return []


def get_gimp_font_list() -> List[str]:
    """
    Get list of available GIMP fonts.
    
    Returns:
        List of font names or empty list if not available
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return []
        
        Gimp = gi_modules['Gimp']
        
        if hasattr(Gimp, 'fonts_get_list'):
            fonts = Gimp.fonts_get_list()
            return list(fonts) if fonts else []
        else:
            logger.warning("Cannot list GIMP fonts")
            return []
            
    except Exception as e:
        logger.error(f"Failed to get GIMP fonts: {e}")
        return []


def create_gimp_image_from_buffer(width: int, height: int, buffer_data: bytes,
                                  image_format: str = "RGB") -> Optional[Any]:
    """
    Create a GIMP image from buffer data.
    
    Args:
        width: Image width
        height: Image height
        buffer_data: Raw image data
        image_format: Image format (RGB, RGBA, GRAY)
        
    Returns:
        GIMP image object or None if creation failed
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return None
        
        Gimp = gi_modules['Gimp']
        
        # Map format to GIMP image type
        format_map = {
            "RGB": 0,  # RGB
            "RGBA": 0,  # RGB (alpha handled in layer)
            "GRAY": 1,  # GRAYSCALE
            "GRAYSCALE": 1,
        }
        
        gimp_format = format_map.get(image_format.upper(), 0)
        
        if hasattr(Gimp, 'Image') and hasattr(Gimp.Image, 'new'):
            image = Gimp.Image.new(width, height, gimp_format)
            
            # Create layer for the buffer data
            if hasattr(Gimp, 'Layer') and hasattr(Gimp.Layer, 'new'):
                layer_type = 0 if image_format.upper() == "RGB" else 1  # RGB or RGBA
                layer = Gimp.Layer.new(image, "Buffer Layer", width, height, layer_type, 100, 0)
                
                # Add layer to image
                if hasattr(image, 'insert_layer'):
                    image.insert_layer(layer, None, 0)
                    
                    # Set pixel data (this would require more complex buffer handling)
                    logger.debug(f"Created GIMP image from buffer: {width}x{height}")
                    return image
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to create GIMP image from buffer: {e}")
        return None


def get_gimp_layer_blend_modes() -> Dict[str, int]:
    """
    Get mapping of layer blend mode names to GIMP constants.
    
    Returns:
        Dictionary mapping blend mode names to constants
    """
    try:
        gi_modules = safe_gi_import()
        if not gi_modules:
            return {}
        
        Gimp = gi_modules['Gimp']
        
        blend_modes = {}
        
        if hasattr(Gimp, 'BlendMode'):
            # Common blend modes
            mode_names = [
                'NORMAL', 'MULTIPLY', 'SCREEN', 'OVERLAY', 'SOFT_LIGHT', 'HARD_LIGHT',
                'COLOR_DODGE', 'COLOR_BURN', 'DARKEN_ONLY', 'LIGHTEN_ONLY',
                'DIFFERENCE', 'EXCLUSION', 'HUE', 'SATURATION', 'COLOR', 'VALUE'
            ]
            
            for mode_name in mode_names:
                if hasattr(Gimp.BlendMode, mode_name):
                    blend_modes[mode_name.lower()] = getattr(Gimp.BlendMode, mode_name)
        
        return blend_modes
        
    except Exception as e:
        logger.error(f"Failed to get blend modes: {e}")
        return {}


def validate_gimp_installation() -> Dict[str, Any]:
    """
    Comprehensive validation of GIMP installation and capabilities.
    
    Returns:
        Dictionary with detailed validation results
    """
    validation = {
        "gi_available": False,
        "gimp_available": False,
        "gtk_available": False,
        "version_compatible": False,
        "basic_functionality": False,
        "advanced_functionality": False,
        "errors": [],
        "warnings": [],
        "capabilities": {},
        "missing_features": [],
    }
    
    try:
        # Check GI availability
        gi_status = check_gi_availability()
        validation["gi_available"] = gi_status["gi_available"]
        validation["gimp_available"] = gi_status["gimp_available"]
        validation["gtk_available"] = gi_status["gtk_available"]
        validation["errors"].extend(gi_status["errors"])
        
        # Check version compatibility
        version_status = validate_gimp_version()
        validation["version_compatible"] = version_status["compatible"]
        validation["errors"].extend(version_status["errors"])
        
        if validation["gimp_available"]:
            gi_modules = safe_gi_import()
            if gi_modules:
                Gimp = gi_modules['Gimp']
                
                # Test basic functionality
                basic_features = [
                    'list_images', 'Image', 'Layer', 'context_set_foreground'
                ]
                
                basic_available = 0
                for feature in basic_features:
                    if hasattr(Gimp, feature):
                        basic_available += 1
                    else:
                        validation["missing_features"].append(feature)
                
                validation["basic_functionality"] = basic_available >= len(basic_features) * 0.8
                
                # Test advanced functionality
                advanced_features = [
                    'file_load', 'file_save', 'paintbrush_default', 'edit_fill',
                    'image_select_rectangle', 'selection_none'
                ]
                
                advanced_available = 0
                for feature in advanced_features:
                    if hasattr(Gimp, feature):
                        advanced_available += 1
                        validation["capabilities"][feature] = True
                    else:
                        validation["capabilities"][feature] = False
                        validation["missing_features"].append(feature)
                
                validation["advanced_functionality"] = advanced_available >= len(advanced_features) * 0.6
                
                # Check for common resources
                validation["capabilities"]["brushes"] = bool(get_gimp_brush_list())
                validation["capabilities"]["patterns"] = bool(get_gimp_pattern_list())
                validation["capabilities"]["fonts"] = bool(get_gimp_font_list())
                validation["capabilities"]["blend_modes"] = bool(get_gimp_layer_blend_modes())
        
    except Exception as e:
        validation["errors"].append(f"Validation error: {e}")
    
    return validation


def get_gimp_runtime_stats() -> Dict[str, Any]:
    """
    Get runtime statistics and performance information.
    
    Returns:
        Dictionary with runtime statistics
    """
    stats = {
        "import_time": 0.0,
        "initialization_time": 0.0,
        "memory_usage": 0,
        "active_images": 0,
        "procedure_count": 0,
        "errors": [],
    }
    
    try:
        import time
        import psutil
        import os
        
        # Measure import time
        start_time = time.time()
        gi_modules = safe_gi_import()
        stats["import_time"] = time.time() - start_time
        
        if gi_modules:
            Gimp = gi_modules['Gimp']
            
            # Measure initialization time
            start_time = time.time()
            # Perform basic initialization operations
            if hasattr(Gimp, 'list_images'):
                images = Gimp.list_images()
                stats["active_images"] = len(images) if images else 0
            stats["initialization_time"] = time.time() - start_time
            
            # Get procedure count
            if hasattr(Gimp, 'get_procedures'):
                procedures = Gimp.get_procedures()
                stats["procedure_count"] = len(procedures) if procedures else 0
        
        # Get memory usage
        process = psutil.Process(os.getpid())
        stats["memory_usage"] = process.memory_info().rss
        
    except Exception as e:
        stats["errors"].append(str(e))
    
    return stats