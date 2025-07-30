"""
Utility modules for GIMP MCP Server

This package contains utility functions and classes used throughout
the GIMP MCP Server implementation.
"""

from .errors import (
    GimpError,
    GimpConnectionError,
    GimpOperationError,
    GimpResourceError,
    GimpValidationError,
    GimpModeError,
    safe_operation,
)
from .logging import setup_logging, get_logger
from .gi_helpers import safe_gi_import, check_gi_availability
from .image_utils import (
    validate_color,
    parse_color,
    validate_coordinates,
    validate_dimensions,
)

__all__ = [
    # Error handling
    "GimpError",
    "GimpConnectionError",
    "GimpOperationError",
    "GimpResourceError",
    "GimpValidationError",
    "GimpModeError",
    "safe_operation",
    # Logging
    "setup_logging",
    "get_logger",
    # GI helpers
    "safe_gi_import",
    "check_gi_availability",
    # Image utilities
    "validate_color",
    "parse_color",
    "validate_coordinates",
    "validate_dimensions",
]