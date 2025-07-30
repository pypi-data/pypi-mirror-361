"""
Document Management Tools for GIMP MCP Server

This module provides MCP tools for document operations including
creation, opening, saving, and document information retrieval.
"""

import logging
from typing import Dict, Any, Optional

from ..utils.errors import safe_operation, GimpValidationError
from ..utils.image_utils import validate_dimensions, validate_resolution, create_image_info

logger = logging.getLogger(__name__)


class DocumentTools:
    """Document management operations for GIMP MCP server."""
    
    def __init__(self, gimp_api):
        """
        Initialize document tools.
        
        Args:
            gimp_api: GIMP API instance
        """
        self.gimp_api = gimp_api
    
    @safe_operation("get_document_info")
    async def get_document_info(self, document_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get detailed information about a GIMP document.
        
        Args:
            document_id: Document ID (uses active document if None)
            
        Returns:
            Dictionary containing document information
        """
        try:
            if document_id is None:
                # Get active document
                active_doc = await self.gimp_api.get_active_image()
                if not active_doc:
                    return {
                        "success": False,
                        "operation": "get_document_info",
                        "error": "No active document found",
                        "timestamp": __import__('time').time(),
                    }
                document_id = active_doc.get("id", 0)
            
            # Get detailed document information
            result = await self.gimp_api.get_image_info(document_id)
            
            if result.get("success"):
                return {
                    "success": True,
                    "operation": "get_document_info",
                    "document_id": document_id,
                    "info": result.get("image_info", {}),
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "success": False,
                    "operation": "get_document_info",
                    "document_id": document_id,
                    "error": result.get("error", "Unknown error"),
                    "timestamp": result.get("timestamp"),
                }
                
        except Exception as e:
            logger.error(f"Failed to get document info: {e}")
            return {
                "success": False,
                "operation": "get_document_info",
                "error": str(e),
                "timestamp": __import__('time').time(),
            }
    
    @safe_operation("list_documents")
    async def list_documents(self) -> Dict[str, Any]:
        """
        List all open documents in GIMP.
        
        Returns:
            Dictionary containing list of open documents
        """
        try:
            # Get all open images from GIMP
            images = await self.gimp_api.list_open_images()
            
            return {
                "success": True,
                "operation": "list_documents",
                "documents": images,
                "count": len(images),
                "timestamp": __import__('time').time(),
            }
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return {
                "success": False,
                "operation": "list_documents",
                "error": str(e),
                "timestamp": __import__('time').time(),
            }
    
    @safe_operation("create_document")
    async def create_document(
        self,
        width: int = 1920,
        height: int = 1080,
        resolution: float = 300.0,
        color_mode: str = "RGB",
        fill_type: str = "transparent"
    ) -> Dict[str, Any]:
        """
        Create a new GIMP document.
        
        Args:
            width: Document width in pixels
            height: Document height in pixels
            resolution: Document resolution in DPI
            color_mode: Color mode (RGB, GRAYSCALE, INDEXED)
            fill_type: Fill type (transparent, white, black, foreground, background)
            
        Returns:
            Dictionary containing document creation result
        """
        try:
            # Validate input parameters
            validate_dimensions(width, height)
            validate_resolution(resolution)
            
            valid_modes = ["RGB", "GRAYSCALE", "INDEXED"]
            if color_mode.upper() not in valid_modes:
                raise GimpValidationError(f"Invalid color mode: {color_mode}")
            
            valid_fills = ["transparent", "white", "black", "foreground", "background"]
            if fill_type.lower() not in valid_fills:
                raise GimpValidationError(f"Invalid fill type: {fill_type}")
            
            # Create document using GIMP API
            result = await self.gimp_api.create_image(
                width=width,
                height=height,
                image_type=color_mode,
                fill_type=fill_type,
                resolution=resolution
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "operation": "create_document",
                    "document_id": result.get("image_id"),
                    "document_info": {
                        "width": width,
                        "height": height,
                        "mode": color_mode,
                        "resolution": resolution,
                        "fill_type": fill_type,
                    },
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "success": False,
                    "operation": "create_document",
                    "error": result.get("error", "Document creation failed"),
                    "timestamp": result.get("timestamp"),
                }
            
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise
    
    @safe_operation("open_document")
    async def open_document(self, file_path: str) -> Dict[str, Any]:
        """
        Open an existing document from file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing document open result
        """
        if not file_path or not isinstance(file_path, str):
            raise GimpValidationError("File path is required and must be a string")
        
        try:
            # Open document using GIMP API
            result = await self.gimp_api.open_image(file_path)
            
            if result.get("success"):
                return {
                    "success": True,
                    "operation": "open_document",
                    "file_path": file_path,
                    "document_id": result.get("image_id"),
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "success": False,
                    "operation": "open_document",
                    "file_path": file_path,
                    "error": result.get("error", "Document opening failed"),
                    "timestamp": result.get("timestamp"),
                }
                
        except Exception as e:
            logger.error(f"Failed to open document: {e}")
            return {
                "success": False,
                "operation": "open_document",
                "file_path": file_path,
                "error": str(e),
                "timestamp": __import__('time').time(),
            }
    
    @safe_operation("save_document")
    async def save_document(
        self,
        document_id: Optional[int] = None,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save a document to file.
        
        Args:
            document_id: Document ID (uses active document if None)
            file_path: File path (uses current path if None)
            
        Returns:
            Dictionary containing save result
        """
        try:
            # Get active document if not specified
            if document_id is None:
                active_doc = await self.gimp_api.get_active_image()
                if not active_doc:
                    return {
                        "success": False,
                        "operation": "save_document",
                        "error": "No active document found",
                        "timestamp": __import__('time').time(),
                    }
                document_id = active_doc.get("id", 0)
            
            # Use default file path if not specified
            if file_path is None:
                file_path = f"document_{document_id}.xcf"
            
            # Save document using GIMP API
            result = await self.gimp_api.save_image(document_id, file_path)
            
            if result.get("success"):
                return {
                    "success": True,
                    "operation": "save_document",
                    "document_id": document_id,
                    "file_path": file_path,
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "success": False,
                    "operation": "save_document",
                    "document_id": document_id,
                    "file_path": file_path,
                    "error": result.get("error", "Document save failed"),
                    "timestamp": result.get("timestamp"),
                }
                
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            return {
                "success": False,
                "operation": "save_document",
                "error": str(e),
                "timestamp": __import__('time').time(),
            }
    
    @safe_operation("export_document")
    async def export_document(
        self,
        document_id: Optional[int] = None,
        file_path: str = "",
        export_format: str = "PNG",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export document to various formats.
        
        Args:
            document_id: Document ID (uses active document if None)
            file_path: Export file path
            export_format: Export format (PNG, JPEG, etc.)
            options: Format-specific export options
            
        Returns:
            Dictionary containing export result
        """
        if not file_path:
            raise GimpValidationError("Export file path is required")
        
        try:
            # Get active document if not specified
            if document_id is None:
                active_doc = await self.gimp_api.get_active_image()
                if not active_doc:
                    return {
                        "success": False,
                        "operation": "export_document",
                        "error": "No active document found",
                        "timestamp": __import__('time').time(),
                    }
                document_id = active_doc.get("id", 0)
            
            # Export document using GIMP API
            result = await self.gimp_api.save_image(document_id, file_path, export_format)
            
            if result.get("success"):
                return {
                    "success": True,
                    "operation": "export_document",
                    "document_id": document_id,
                    "file_path": file_path,
                    "format": export_format,
                    "options": options or {},
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "success": False,
                    "operation": "export_document",
                    "document_id": document_id,
                    "file_path": file_path,
                    "format": export_format,
                    "error": result.get("error", "Document export failed"),
                    "timestamp": result.get("timestamp"),
                }
                
        except Exception as e:
            logger.error(f"Failed to export document: {e}")
            return {
                "success": False,
                "operation": "export_document",
                "error": str(e),
                "timestamp": __import__('time').time(),
            }
    
    @safe_operation("close_document")
    async def close_document(
        self,
        document_id: Optional[int] = None,
        save_before_close: bool = True
    ) -> Dict[str, Any]:
        """
        Close a document safely.
        
        Args:
            document_id: Document ID (uses active document if None)
            save_before_close: Whether to save before closing
            
        Returns:
            Dictionary containing close result
        """
        try:
            # Get active document if not specified
            if document_id is None:
                active_doc = await self.gimp_api.get_active_image()
                if not active_doc:
                    return {
                        "success": False,
                        "operation": "close_document",
                        "error": "No active document found",
                        "timestamp": __import__('time').time(),
                    }
                document_id = active_doc.get("id", 0)
            
            # Save before closing if requested
            if save_before_close:
                save_result = await self.save_document(document_id)
                if not save_result.get("success"):
                    return {
                        "success": False,
                        "operation": "close_document",
                        "document_id": document_id,
                        "error": f"Failed to save before closing: {save_result.get('error')}",
                        "timestamp": __import__('time').time(),
                    }
            
            # Close document using GIMP API
            result = await self.gimp_api.close_image(document_id)
            
            if result.get("success"):
                return {
                    "success": True,
                    "operation": "close_document",
                    "document_id": document_id,
                    "saved_before_close": save_before_close,
                    "timestamp": result.get("timestamp"),
                }
            else:
                return {
                    "success": False,
                    "operation": "close_document",
                    "document_id": document_id,
                    "error": result.get("error", "Document close failed"),
                    "timestamp": result.get("timestamp"),
                }
                
        except Exception as e:
            logger.error(f"Failed to close document: {e}")
            return {
                "success": False,
                "operation": "close_document",
                "error": str(e),
                "timestamp": __import__('time').time(),
            }