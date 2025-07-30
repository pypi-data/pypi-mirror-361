"""
GIMP MCP Server - Main FastMCP Server Implementation

This module provides the main FastMCP server implementation for GIMP integration.
It handles tool registration, resource providers, and connection management.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from .gimp_api import GimpAPI
from .mode_manager import GimpModeManager
from .utils.logging import setup_logging
from .utils.errors import GimpError, GimpConnectionError

# Import tool modules
from .tools.document_tools import DocumentTools
from .tools.layer_tools import LayerTools
from .tools.drawing_tools import DrawingTools
from .tools.selection_tools import SelectionTools
from .tools.color_tools import ColorTools
from .tools.filter_tools import FilterTools

# Import resource providers
from .resources.providers import ResourceProviders

logger = logging.getLogger(__name__)


class ServerConfig(BaseModel):
    """Configuration for the GIMP MCP Server."""
    
    host: str = "localhost"
    port: int = 3000
    debug: bool = False
    mode: Optional[str] = None  # "gui", "headless", or None for auto-detect
    log_level: str = "INFO"


class GimpMCPServer:
    """Main GIMP MCP Server class."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.app = FastMCP("GIMP MCP Server")
        self.gimp_api: Optional[GimpAPI] = None
        self.mode_manager: Optional[GimpModeManager] = None
        self.is_running = False
        
        # Initialize logging
        setup_logging(
            level=getattr(logging, config.log_level.upper()),
            debug=config.debug
        )
        
        # Initialize components
        self._initialize_components()
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
        
        # Setup server event handlers
        self._setup_event_handlers()
    
    def _initialize_components(self):
        """Initialize core components."""
        try:
            # Initialize mode manager
            self.mode_manager = GimpModeManager(force_mode=self.config.mode)
            logger.info(f"Mode manager initialized - GUI mode: {self.mode_manager.gui_mode}")
            
            # Initialize GIMP API
            self.gimp_api = GimpAPI(mode_manager=self.mode_manager)
            logger.info("GIMP API initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise GimpConnectionError(f"Component initialization failed: {e}")
    
    def _register_tools(self):
        """Register all MCP tools."""
        try:
            # Initialize tool classes
            document_tools = DocumentTools(self.gimp_api)
            layer_tools = LayerTools(self.gimp_api)
            drawing_tools = DrawingTools(self.gimp_api)
            selection_tools = SelectionTools(self.gimp_api)
            color_tools = ColorTools(self.gimp_api)
            filter_tools = FilterTools(self.gimp_api)
            
            # Register tools with the FastMCP app
            # Document tools
            self.app.add_tool(document_tools.get_document_info)
            self.app.add_tool(document_tools.list_documents)
            self.app.add_tool(document_tools.create_document)
            self.app.add_tool(document_tools.open_document)
            self.app.add_tool(document_tools.save_document)
            self.app.add_tool(document_tools.export_document)
            self.app.add_tool(document_tools.close_document)
            
            # Layer tools
            self.app.add_tool(layer_tools.get_layer_info)
            self.app.add_tool(layer_tools.create_layer)
            self.app.add_tool(layer_tools.set_layer_opacity)
            self.app.add_tool(layer_tools.set_layer_blend_mode)
            self.app.add_tool(layer_tools.set_layer_visibility)
            self.app.add_tool(layer_tools.duplicate_layer)
            self.app.add_tool(layer_tools.delete_layer)
            self.app.add_tool(layer_tools.move_layer)
            
            # Drawing tools
            self.app.add_tool(drawing_tools.apply_brush_stroke)
            self.app.add_tool(drawing_tools.draw_rectangle)
            self.app.add_tool(drawing_tools.draw_ellipse)
            self.app.add_tool(drawing_tools.bucket_fill)
            
            # Selection tools
            self.app.add_tool(selection_tools.create_rectangular_selection)
            self.app.add_tool(selection_tools.create_elliptical_selection)
            self.app.add_tool(selection_tools.modify_selection)
            self.app.add_tool(selection_tools.clear_selection)
            
            # Color tools
            self.app.add_tool(color_tools.set_foreground_color)
            self.app.add_tool(color_tools.set_background_color)
            self.app.add_tool(color_tools.sample_color)
            self.app.add_tool(color_tools.get_active_palette)
            
            # Filter tools
            self.app.add_tool(filter_tools.apply_blur)
            self.app.add_tool(filter_tools.apply_sharpen)
            self.app.add_tool(filter_tools.adjust_brightness_contrast)
            
            logger.info("All tools registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register tools: {e}")
            raise GimpError(f"Tool registration failed: {e}")
    
    def _register_resources(self):
        """Register all MCP resources."""
        try:
            # Initialize resource providers
            resource_providers = ResourceProviders(self.gimp_api)
            
            # Register resources with the FastMCP app
            self.app.add_resource(resource_providers.get_current_document)
            self.app.add_resource(resource_providers.get_document_list)
            self.app.add_resource(resource_providers.get_document_metadata)
            self.app.add_resource(resource_providers.get_system_status)
            self.app.add_resource(resource_providers.get_system_capabilities)
            self.app.add_resource(resource_providers.get_system_health)
            self.app.add_resource(resource_providers.get_active_palette)
            self.app.add_resource(resource_providers.get_brush_list)
            self.app.add_resource(resource_providers.get_current_tool)
            
            logger.info("All resources registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register resources: {e}")
            raise GimpError(f"Resource registration failed: {e}")
    
    def _setup_event_handlers(self):
        """Setup server event handlers."""
        
        @self.app.on_startup
        async def on_startup():
            """Handle server startup."""
            logger.info("GIMP MCP Server starting up...")
            self.is_running = True
            
            # Perform initial GIMP connection check
            try:
                await self._check_gimp_connection()
                logger.info("GIMP connection verified")
            except Exception as e:
                logger.warning(f"GIMP connection check failed: {e}")
        
        @self.app.on_shutdown
        async def on_shutdown():
            """Handle server shutdown."""
            logger.info("GIMP MCP Server shutting down...")
            self.is_running = False
            
            # Cleanup resources
            if self.gimp_api:
                await self.gimp_api.cleanup()
    
    async def _check_gimp_connection(self):
        """Check GIMP connection status."""
        if not self.gimp_api:
            raise GimpConnectionError("GIMP API not initialized")
        
        # Test basic connection
        try:
            result = await self.gimp_api.test_connection()
            if not result.get("success", False):
                raise GimpConnectionError("GIMP connection test failed")
        except Exception as e:
            raise GimpConnectionError(f"GIMP connection failed: {e}")
    
    async def run(self):
        """Run the server."""
        try:
            logger.info(f"Starting GIMP MCP Server on {self.config.host}:{self.config.port}")
            await self.app.run(host=self.config.host, port=self.config.port)
        except Exception as e:
            logger.error(f"Server run failed: {e}")
            raise


def create_server(config: Optional[ServerConfig] = None) -> GimpMCPServer:
    """Create and configure the GIMP MCP Server."""
    if config is None:
        config = ServerConfig()
    
    return GimpMCPServer(config)


def main():
    """Main entry point for the GIMP MCP Server."""
    # Load configuration from environment
    config = ServerConfig(
        host=os.getenv("GIMP_MCP_HOST", "localhost"),
        port=int(os.getenv("GIMP_MCP_PORT", "3000")),
        debug=os.getenv("GIMP_MCP_DEBUG", "").lower() in ("1", "true", "yes"),
        mode=os.getenv("GIMP_MCP_MODE"),
        log_level=os.getenv("GIMP_MCP_LOG_LEVEL", "INFO"),
    )
    
    # Create and run server
    server = create_server(config)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise


if __name__ == "__main__":
    main()