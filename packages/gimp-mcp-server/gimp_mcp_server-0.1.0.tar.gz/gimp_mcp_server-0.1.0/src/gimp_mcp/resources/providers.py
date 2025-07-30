"""
Resource Providers for GIMP MCP Server

This module provides all MCP resource implementations for real-time
GIMP state and system information access.
"""

import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ResourceProviders:
    """Consolidated resource providers for GIMP MCP server."""
    
    def __init__(self, gimp_api):
        """
        Initialize resource providers.
        
        Args:
            gimp_api: GIMP API instance
        """
        self.gimp_api = gimp_api
    
    # Document Resources
    
    async def get_current_document(self) -> Dict[str, Any]:
        """
        Get current active document state.
        
        Returns:
            Dictionary containing current document information
        """
        try:
            # Get active document from GIMP API
            active_doc = await self.gimp_api.get_active_image()
            
            if active_doc:
                # Get detailed document information
                doc_info_result = await self.gimp_api.get_image_info(active_doc.get("id", 0))
                
                if doc_info_result.get("success"):
                    doc_info = doc_info_result.get("image_info", {})
                    return {
                        "uri": "document://current",
                        "name": "Current Document",
                        "mimeType": "application/json",
                        "content": {
                            "document_id": active_doc.get("id", 0),
                            "name": doc_info.get("name", "Untitled Document"),
                            "width": doc_info.get("width", 0),
                            "height": doc_info.get("height", 0),
                            "mode": doc_info.get("base_type", "RGB"),
                            "layer_count": len(doc_info.get("layers", [])),
                            "layers": doc_info.get("layers", []),
                            "timestamp": time.time(),
                        },
                    }
            
            # No active document
            return {
                "uri": "document://current",
                "name": "Current Document",
                "mimeType": "application/json",
                "content": {
                    "document_id": None,
                    "name": "No active document",
                    "message": "No document is currently active",
                    "timestamp": time.time(),
                },
            }
            
        except Exception as e:
            logger.error(f"Failed to get current document: {e}")
            return {
                "uri": "document://current",
                "name": "Current Document",
                "mimeType": "application/json",
                "content": {"error": str(e), "timestamp": time.time()},
            }
    
    async def get_document_list(self) -> Dict[str, Any]:
        """
        Get list of all open documents.
        
        Returns:
            Dictionary containing list of open documents
        """
        try:
            # Get all open images from GIMP API
            images = await self.gimp_api.list_open_images()
            
            # Get active document for comparison
            active_doc = await self.gimp_api.get_active_image()
            active_id = active_doc.get("id", 0) if active_doc else None
            
            # Mark active document
            for image in images:
                image["is_active"] = image.get("id") == active_id
            
            return {
                "uri": "document://list",
                "name": "Document List",
                "mimeType": "application/json",
                "content": {
                    "documents": images,
                    "count": len(images),
                    "active_document_id": active_id,
                    "timestamp": time.time(),
                },
            }
            
        except Exception as e:
            logger.error(f"Failed to get document list: {e}")
            return {
                "uri": "document://list",
                "name": "Document List",
                "mimeType": "application/json",
                "content": {"error": str(e), "timestamp": time.time()},
            }
    
    async def get_document_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the current document.
        
        Returns:
            Dictionary containing document metadata
        """
        try:
            # TODO: Implement actual GIMP document metadata retrieval
            return {
                "uri": "document://metadata",
                "name": "Document Metadata",
                "mimeType": "application/json",
                "content": {
                    "creation_time": time.time() - 3600,  # 1 hour ago
                    "modification_time": time.time() - 300,  # 5 minutes ago
                    "file_path": None,
                    "file_size": 0,
                    "color_profile": "sRGB",
                    "precision": "8-bit",
                    "has_alpha": True,
                    "undo_steps": 5,
                    "redo_steps": 0,
                    "timestamp": time.time(),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get document metadata: {e}")
            return {
                "uri": "document://metadata",
                "name": "Document Metadata",
                "mimeType": "application/json",
                "content": {"error": str(e), "timestamp": time.time()},
            }
    
    # System Resources
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get system and server status.
        
        Returns:
            Dictionary containing system status information
        """
        try:
            system_info = await self.gimp_api.get_system_info()
            
            return {
                "uri": "system://status",
                "name": "System Status",
                "mimeType": "application/json",
                "content": {
                    "server_status": "running",
                    "gimp_connection": system_info.get("connection_active", False),
                    "mode": system_info.get("mode", "unknown"),
                    "api_version": system_info.get("api_version", "unknown"),
                    "server_version": system_info.get("server_version", "0.1.0"),
                    "uptime": time.time(),  # Simplified uptime
                    "timestamp": time.time(),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "uri": "system://status",
                "name": "System Status",
                "mimeType": "application/json",
                "content": {
                    "server_status": "error",
                    "error": str(e),
                    "timestamp": time.time(),
                },
            }
    
    async def get_system_capabilities(self) -> Dict[str, Any]:
        """
        Get server capabilities and available features.
        
        Returns:
            Dictionary containing capability information
        """
        try:
            system_info = await self.gimp_api.get_system_info()
            
            return {
                "uri": "system://capabilities",
                "name": "System Capabilities",
                "mimeType": "application/json",
                "content": {
                    "capabilities": system_info.get("capabilities", {}),
                    "supported_formats": ["PNG", "JPEG", "GIF", "TIFF", "BMP", "WEBP", "XCF"],
                    "available_tools": [
                        "document_management",
                        "layer_operations", 
                        "drawing_tools",
                        "selection_tools",
                        "color_management",
                        "filter_operations",
                    ],
                    "features": {
                        "real_time_resources": True,
                        "batch_operations": True,
                        "undo_support": True,
                        "plugin_integration": False,  # Future feature
                    },
                    "timestamp": time.time(),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get system capabilities: {e}")
            return {
                "uri": "system://capabilities",
                "name": "System Capabilities",
                "mimeType": "application/json",
                "content": {"error": str(e), "timestamp": time.time()},
            }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health information.
        
        Returns:
            Dictionary containing health information
        """
        try:
            health_check = await self.gimp_api.test_connection()
            
            return {
                "uri": "system://health",
                "name": "System Health",
                "mimeType": "application/json",
                "content": {
                    "overall_status": "healthy" if health_check.get("success") else "unhealthy",
                    "gimp_connection": health_check.get("success", False),
                    "connection_mode": health_check.get("mode", "unknown"),
                    "last_check": health_check.get("timestamp", time.time()),
                    "components": {
                        "mcp_server": "healthy",
                        "gimp_api": "healthy" if health_check.get("success") else "unhealthy",
                        "resource_providers": "healthy",
                    },
                    "timestamp": time.time(),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "uri": "system://health",
                "name": "System Health",
                "mimeType": "application/json",
                "content": {
                    "overall_status": "unhealthy",
                    "error": str(e),
                    "timestamp": time.time(),
                },
            }
    
    # Palette and Tool Resources
    
    async def get_active_palette(self) -> Dict[str, Any]:
        """
        Get current color palette.
        
        Returns:
            Dictionary containing color palette data
        """
        try:
            # TODO: Implement actual GIMP palette retrieval
            return {
                "uri": "palettes://active",
                "name": "Active Palette",
                "mimeType": "application/json",
                "content": {
                    "palette_name": "Default",
                    "colors": [
                        {"name": "Black", "hex": "#000000"},
                        {"name": "White", "hex": "#FFFFFF"},
                        {"name": "Red", "hex": "#FF0000"},
                        {"name": "Green", "hex": "#00FF00"},
                        {"name": "Blue", "hex": "#0000FF"},
                    ],
                    "foreground_color": "#000000",
                    "background_color": "#FFFFFF",
                    "timestamp": time.time(),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get active palette: {e}")
            return {
                "uri": "palettes://active",
                "name": "Active Palette",
                "mimeType": "application/json",
                "content": {"error": str(e), "timestamp": time.time()},
            }
    
    async def get_brush_list(self) -> Dict[str, Any]:
        """
        Get available brush presets.
        
        Returns:
            Dictionary containing available brush presets
        """
        try:
            # TODO: Implement actual GIMP brush list retrieval
            return {
                "uri": "brushes://list",
                "name": "Brush List",
                "mimeType": "application/json",
                "content": {
                    "brushes": [
                        {"name": "2. Hardness 050", "type": "basic", "size": 10},
                        {"name": "2. Hardness 075", "type": "basic", "size": 10},
                        {"name": "2. Hardness 100", "type": "basic", "size": 10},
                        {"name": "Airbrush Soft", "type": "airbrush", "size": 20},
                        {"name": "Pencil", "type": "pencil", "size": 5},
                    ],
                    "active_brush": "2. Hardness 050",
                    "brush_size": 10.0,
                    "timestamp": time.time(),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get brush list: {e}")
            return {
                "uri": "brushes://list",
                "name": "Brush List",
                "mimeType": "application/json",
                "content": {"error": str(e), "timestamp": time.time()},
            }
    
    async def get_current_tool(self) -> Dict[str, Any]:
        """
        Get current tool state.
        
        Returns:
            Dictionary containing current tool information
        """
        try:
            # TODO: Implement actual GIMP tool state retrieval
            return {
                "uri": "tools://current",
                "name": "Current Tool",
                "mimeType": "application/json",
                "content": {
                    "active_tool": "paintbrush",
                    "tool_options": {
                        "brush": "2. Hardness 050",
                        "size": 10.0,
                        "opacity": 100.0,
                        "mode": "normal",
                    },
                    "timestamp": time.time(),
                },
            }
        except Exception as e:
            logger.error(f"Failed to get current tool: {e}")
            return {
                "uri": "tools://current",
                "name": "Current Tool", 
                "mimeType": "application/json",
                "content": {"error": str(e), "timestamp": time.time()},
            }