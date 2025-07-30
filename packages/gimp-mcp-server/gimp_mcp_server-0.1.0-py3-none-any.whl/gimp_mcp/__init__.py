"""
GIMP MCP Server - AI Assistant for Image Editing

A Model Context Protocol (MCP) server implementation for GIMP 3.0+,
enabling AI assistants to perform sophisticated image editing operations
through GIMP's GObject Introspection bindings.
"""

__version__ = "0.1.0"
__author__ = "GIMP MCP Server Team"
__email__ = "support@gimp-mcp.com"
__license__ = "MIT"

from .server import create_server, main
from .gimp_api import GimpAPI
from .mode_manager import GimpModeManager

__all__ = [
    "create_server",
    "main",
    "GimpAPI",
    "GimpModeManager",
    "__version__",
]