"""
Unit tests for document tools implementation.

This module tests the DocumentTools class which provides
MCP tools for document lifecycle management.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from gimp_mcp.tools.document_tools import DocumentTools
from gimp_mcp.utils.errors import GimpError, GimpOperationError


class TestDocumentToolsInitialization:
    """Test DocumentTools initialization."""
    
    def test_init_with_gimp_api(self, mock_gimp_api):
        """Test initialization with GIMP API."""
        tools = DocumentTools(mock_gimp_api)
        
        assert tools.gimp_api is mock_gimp_api
        
    def test_init_without_gimp_api(self):
        """Test initialization without GIMP API raises error."""
        with pytest.raises(ValueError, match="GimpAPI instance is required"):
            DocumentTools(None)


class TestDocumentToolsGetDocumentInfo:
    """Test get_document_info tool."""
    
    @pytest.mark.asyncio
    async def test_get_document_info_success(self, mock_gimp_api):
        """Test successful document info retrieval."""
        tools = DocumentTools(mock_gimp_api)
        
        # Configure mock response
        mock_gimp_api.get_image_info = AsyncMock(return_value={
            "success": True,
            "image_info": {
                "id": 1,
                "name": "Test Document",
                "width": 800,
                "height": 600,
                "mode": "RGB",
                "layers": [
                    {
                        "id": 1,
                        "name": "Background",
                        "opacity": 100.0,
                        "visible": True
                    }
                ]
            }
        })
        
        result = await tools.get_document_info(document_id=1)
        
        assert result["success"] is True
        assert result["document"]["id"] == 1
        assert result["document"]["name"] == "Test Document"
        assert len(result["document"]["layers"]) == 1
        
        mock_gimp_api.get_image_info.assert_called_once_with(1)
        
    @pytest.mark.asyncio
    async def test_get_document_info_not_found(self, mock_gimp_api):
        """Test document info retrieval for non-existent document."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.get_image_info = AsyncMock(return_value={
            "success": False,
            "error": "Image not found: 999"
        })
        
        result = await tools.get_document_info(document_id=999)
        
        assert result["success"] is False
        assert "Image not found" in result["error"]
        
    @pytest.mark.asyncio
    async def test_get_document_info_invalid_id(self, mock_gimp_api):
        """Test document info retrieval with invalid ID."""
        tools = DocumentTools(mock_gimp_api)
        
        result = await tools.get_document_info(document_id=-1)
        
        assert result["success"] is False
        assert "Invalid document ID" in result["error"]


class TestDocumentToolsListDocuments:
    """Test list_documents tool."""
    
    @pytest.mark.asyncio
    async def test_list_documents_success(self, mock_gimp_api):
        """Test successful document listing."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.list_open_images = AsyncMock(return_value=[
            {
                "id": 1,
                "name": "Document 1",
                "width": 800,
                "height": 600,
                "mode": "RGB"
            },
            {
                "id": 2,
                "name": "Document 2",
                "width": 1024,
                "height": 768,
                "mode": "GRAYSCALE"
            }
        ])
        
        result = await tools.list_documents()
        
        assert result["success"] is True
        assert len(result["documents"]) == 2
        assert result["documents"][0]["name"] == "Document 1"
        assert result["documents"][1]["mode"] == "GRAYSCALE"
        
    @pytest.mark.asyncio
    async def test_list_documents_empty(self, mock_gimp_api):
        """Test listing documents when none are open."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.list_open_images = AsyncMock(return_value=[])
        
        result = await tools.list_documents()
        
        assert result["success"] is True
        assert len(result["documents"]) == 0
        
    @pytest.mark.asyncio
    async def test_list_documents_error(self, mock_gimp_api):
        """Test document listing with error."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.list_open_images = AsyncMock(
            side_effect=GimpOperationError("Failed to list images")
        )
        
        result = await tools.list_documents()
        
        assert result["success"] is False
        assert "Failed to list images" in result["error"]


class TestDocumentToolsCreateDocument:
    """Test create_document tool."""
    
    @pytest.mark.asyncio
    async def test_create_document_success(self, mock_gimp_api):
        """Test successful document creation."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.create_image = AsyncMock(return_value={
            "success": True,
            "image_id": 1,
            "width": 800,
            "height": 600,
            "image_type": "RGB",
            "resolution": 300.0
        })
        
        result = await tools.create_document(
            width=800,
            height=600,
            name="New Document",
            image_type="RGB",
            fill_type="white",
            resolution=300.0
        )
        
        assert result["success"] is True
        assert result["document_id"] == 1
        assert result["width"] == 800
        assert result["height"] == 600
        assert result["name"] == "New Document"
        
        mock_gimp_api.create_image.assert_called_once_with(
            800, 600, "RGB", "white", 300.0
        )
        
    @pytest.mark.asyncio
    async def test_create_document_with_defaults(self, mock_gimp_api):
        """Test document creation with default parameters."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.create_image = AsyncMock(return_value={
            "success": True,
            "image_id": 2,
            "width": 1024,
            "height": 768,
            "image_type": "RGB",
            "resolution": 300.0
        })
        
        result = await tools.create_document(width=1024, height=768)
        
        assert result["success"] is True
        assert result["document_id"] == 2
        
    @pytest.mark.asyncio
    async def test_create_document_invalid_dimensions(self, mock_gimp_api):
        """Test document creation with invalid dimensions."""
        tools = DocumentTools(mock_gimp_api)
        
        result = await tools.create_document(width=-1, height=600)
        
        assert result["success"] is False
        assert "Invalid dimensions" in result["error"]
        
        result = await tools.create_document(width=800, height=0)
        
        assert result["success"] is False
        assert "Invalid dimensions" in result["error"]


class TestDocumentToolsOpenDocument:
    """Test open_document tool."""
    
    @pytest.mark.asyncio
    async def test_open_document_success(self, mock_gimp_api, temp_image_file):
        """Test successful document opening."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.open_image = AsyncMock(return_value={
            "success": True,
            "image_id": 3,
            "file_path": temp_image_file,
            "width": 1024,
            "height": 768
        })
        
        result = await tools.open_document(file_path=temp_image_file)
        
        assert result["success"] is True
        assert result["document_id"] == 3
        assert result["file_path"] == temp_image_file
        
        mock_gimp_api.open_image.assert_called_once_with(temp_image_file)
        
    @pytest.mark.asyncio
    async def test_open_document_file_not_found(self, mock_gimp_api):
        """Test opening non-existent document."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.open_image = AsyncMock(return_value={
            "success": False,
            "error": "File not found: /nonexistent/file.png"
        })
        
        result = await tools.open_document(file_path="/nonexistent/file.png")
        
        assert result["success"] is False
        assert "File not found" in result["error"]
        
    @pytest.mark.asyncio
    async def test_open_document_empty_path(self, mock_gimp_api):
        """Test opening document with empty path."""
        tools = DocumentTools(mock_gimp_api)
        
        result = await tools.open_document(file_path="")
        
        assert result["success"] is False
        assert "File path cannot be empty" in result["error"]


class TestDocumentToolsSaveDocument:
    """Test save_document tool."""
    
    @pytest.mark.asyncio
    async def test_save_document_success(self, mock_gimp_api, temp_directory):
        """Test successful document saving."""
        import os
        tools = DocumentTools(mock_gimp_api)
        save_path = os.path.join(temp_directory, "test_save.png")
        
        mock_gimp_api.save_image = AsyncMock(return_value={
            "success": True,
            "image_id": 1,
            "file_path": save_path,
            "format": "PNG"
        })
        
        result = await tools.save_document(
            document_id=1,
            file_path=save_path,
            format_type="PNG"
        )
        
        assert result["success"] is True
        assert result["document_id"] == 1
        assert result["file_path"] == save_path
        
        mock_gimp_api.save_image.assert_called_once_with(1, save_path, "PNG")
        
    @pytest.mark.asyncio
    async def test_save_document_invalid_format(self, mock_gimp_api):
        """Test saving document with invalid format."""
        tools = DocumentTools(mock_gimp_api)
        
        result = await tools.save_document(
            document_id=1,
            file_path="/test/path.xyz",
            format_type="INVALID"
        )
        
        assert result["success"] is False
        assert "Invalid format" in result["error"]


class TestDocumentToolsExportDocument:
    """Test export_document tool."""
    
    @pytest.mark.asyncio
    async def test_export_document_success(self, mock_gimp_api, temp_directory):
        """Test successful document export."""
        import os
        tools = DocumentTools(mock_gimp_api)
        export_path = os.path.join(temp_directory, "test_export.jpg")
        
        # Mock export functionality
        mock_gimp_api.export_image = AsyncMock(return_value={
            "success": True,
            "image_id": 1,
            "file_path": export_path,
            "format": "JPEG",
            "quality": 90
        })
        
        result = await tools.export_document(
            document_id=1,
            file_path=export_path,
            format_type="JPEG",
            quality=90
        )
        
        assert result["success"] is True
        assert result["document_id"] == 1
        assert result["file_path"] == export_path
        
    @pytest.mark.asyncio
    async def test_export_document_with_options(self, mock_gimp_api, temp_directory):
        """Test document export with format-specific options."""
        import os
        tools = DocumentTools(mock_gimp_api)
        export_path = os.path.join(temp_directory, "test_export.png")
        
        mock_gimp_api.export_image = AsyncMock(return_value={
            "success": True,
            "image_id": 1,
            "file_path": export_path,
            "format": "PNG",
            "compression": 9
        })
        
        result = await tools.export_document(
            document_id=1,
            file_path=export_path,
            format_type="PNG",
            compression=9
        )
        
        assert result["success"] is True


class TestDocumentToolsCloseDocument:
    """Test close_document tool."""
    
    @pytest.mark.asyncio
    async def test_close_document_success(self, mock_gimp_api):
        """Test successful document closing."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.close_image = AsyncMock(return_value={
            "success": True,
            "image_id": 1
        })
        
        result = await tools.close_document(document_id=1, save_changes=False)
        
        assert result["success"] is True
        assert result["document_id"] == 1
        
        mock_gimp_api.close_image.assert_called_once_with(1)
        
    @pytest.mark.asyncio
    async def test_close_document_with_save(self, mock_gimp_api):
        """Test closing document with save."""
        tools = DocumentTools(mock_gimp_api)
        
        # Mock getting image info for save path
        mock_gimp_api.get_image_info = AsyncMock(return_value={
            "success": True,
            "image_info": {
                "id": 1,
                "name": "Test Document.png",
                "file_path": "/test/path.png"
            }
        })
        
        mock_gimp_api.save_image = AsyncMock(return_value={
            "success": True,
            "image_id": 1
        })
        
        mock_gimp_api.close_image = AsyncMock(return_value={
            "success": True,
            "image_id": 1
        })
        
        result = await tools.close_document(document_id=1, save_changes=True)
        
        assert result["success"] is True
        
    @pytest.mark.asyncio
    async def test_close_document_not_found(self, mock_gimp_api):
        """Test closing non-existent document."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.close_image = AsyncMock(return_value={
            "success": False,
            "error": "Image not found: 999"
        })
        
        result = await tools.close_document(document_id=999)
        
        assert result["success"] is False
        assert "Image not found" in result["error"]


class TestDocumentToolsValidation:
    """Test document tools parameter validation."""
    
    @pytest.mark.asyncio
    async def test_validate_document_dimensions(self, mock_gimp_api):
        """Test document dimension validation."""
        tools = DocumentTools(mock_gimp_api)
        
        # Test valid dimensions
        assert tools._validate_dimensions(800, 600) is True
        assert tools._validate_dimensions(1, 1) is True
        assert tools._validate_dimensions(32768, 32768) is True
        
        # Test invalid dimensions
        assert tools._validate_dimensions(0, 600) is False
        assert tools._validate_dimensions(800, -1) is False
        assert tools._validate_dimensions(-1, -1) is False
        
    @pytest.mark.asyncio
    async def test_validate_file_path(self, mock_gimp_api):
        """Test file path validation."""
        tools = DocumentTools(mock_gimp_api)
        
        # Test valid paths
        assert tools._validate_file_path("/valid/path.png") is True
        assert tools._validate_file_path("relative/path.jpg") is True
        
        # Test invalid paths
        assert tools._validate_file_path("") is False
        assert tools._validate_file_path(None) is False
        
    @pytest.mark.asyncio
    async def test_validate_image_format(self, mock_gimp_api):
        """Test image format validation."""
        tools = DocumentTools(mock_gimp_api)
        
        # Test valid formats
        valid_formats = ["PNG", "JPEG", "JPG", "GIF", "BMP", "TIFF"]
        for fmt in valid_formats:
            assert tools._validate_format(fmt) is True
            assert tools._validate_format(fmt.lower()) is True
            
        # Test invalid formats
        assert tools._validate_format("INVALID") is False
        assert tools._validate_format("") is False
        assert tools._validate_format(None) is False


class TestDocumentToolsErrorHandling:
    """Test document tools error handling."""
    
    @pytest.mark.asyncio
    async def test_handle_gimp_api_error(self, mock_gimp_api):
        """Test handling of GIMP API errors."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.get_image_info = AsyncMock(
            side_effect=GimpOperationError("GIMP operation failed")
        )
        
        result = await tools.get_document_info(document_id=1)
        
        assert result["success"] is False
        assert "GIMP operation failed" in result["error"]
        
    @pytest.mark.asyncio
    async def test_handle_unexpected_error(self, mock_gimp_api):
        """Test handling of unexpected errors."""
        tools = DocumentTools(mock_gimp_api)
        
        mock_gimp_api.create_image = AsyncMock(
            side_effect=Exception("Unexpected error")
        )
        
        result = await tools.create_document(width=800, height=600)
        
        assert result["success"] is False
        assert "Unexpected error" in result["error"]
        
    @pytest.mark.asyncio
    async def test_handle_connection_error(self, connection_error_api):
        """Test handling of connection errors."""
        tools = DocumentTools(connection_error_api)
        
        result = await tools.list_documents()
        
        assert result["success"] is False
        assert "connection" in result["error"].lower()


@pytest.fixture
def document_tools(mock_gimp_api):
    """Create DocumentTools instance for testing."""
    return DocumentTools(mock_gimp_api)


@pytest.mark.asyncio
async def test_document_tools_integration(document_tools, mock_gimp_api):
    """Test document tools integration scenario."""
    # Create a document
    mock_gimp_api.create_image = AsyncMock(return_value={
        "success": True,
        "image_id": 1,
        "width": 800,
        "height": 600
    })
    
    create_result = await document_tools.create_document(width=800, height=600)
    assert create_result["success"] is True
    
    # Get document info
    mock_gimp_api.get_image_info = AsyncMock(return_value={
        "success": True,
        "image_info": {
            "id": 1,
            "name": "Untitled",
            "width": 800,
            "height": 600,
            "layers": []
        }
    })
    
    info_result = await document_tools.get_document_info(document_id=1)
    assert info_result["success"] is True
    
    # Close document
    mock_gimp_api.close_image = AsyncMock(return_value={
        "success": True,
        "image_id": 1
    })
    
    close_result = await document_tools.close_document(document_id=1)
    assert close_result["success"] is True