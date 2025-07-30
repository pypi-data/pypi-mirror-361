"""
Unit tests for GIMP API wrapper.

This module contains comprehensive tests for the GimpAPI class,
covering all functionality including connection management, 
document operations, layer management, and drawing operations.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from gimp_mcp.gimp_api import GimpAPI
from gimp_mcp.mode_manager import GimpModeManager
from gimp_mcp.utils.errors import GimpError, GimpConnectionError, GimpOperationError


class TestGimpAPIInitialization:
    """Test GIMP API initialization and setup."""
    
    def test_init_with_mode_manager(self, mock_mode_manager, mock_gi_modules):
        """Test initialization with provided mode manager."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            api = GimpAPI(mode_manager=mock_mode_manager)
            
            assert api.mode_manager is mock_mode_manager
            assert api._connection_verified is False
            assert api._health_check_interval == 30
            
    def test_init_without_mode_manager(self, mock_gi_modules):
        """Test initialization without mode manager creates default."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.gimp_api.GimpModeManager') as mock_manager_class:
                api = GimpAPI()
                
                mock_manager_class.assert_called_once()
                assert api.mode_manager is not None
                
    def test_init_connection_failure(self, mock_mode_manager):
        """Test initialization handles connection failure gracefully."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=None):
            with pytest.raises(GimpConnectionError, match="Failed to import GObject Introspection"):
                GimpAPI(mode_manager=mock_mode_manager)
                
    def test_init_gimp_module_missing(self, mock_mode_manager):
        """Test initialization handles missing GIMP module."""
        mock_modules = {'gi': Mock()}  # Missing Gimp module
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_modules):
            with pytest.raises(GimpConnectionError, match="Failed to import GIMP module"):
                GimpAPI(mode_manager=mock_mode_manager)


class TestGimpAPIConnection:
    """Test GIMP API connection management."""
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, mock_gimp_api):
        """Test successful connection test."""
        result = await mock_gimp_api.test_connection()
        
        assert result["success"] is True
        assert result["mode"] == "headless"
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, connection_error_api):
        """Test connection test failure."""
        result = await connection_error_api.test_connection()
        
        assert result["success"] is False
        assert "error" in result
        assert result["connection_verified"] is False
        
    @pytest.mark.asyncio
    async def test_get_system_info_success(self, mock_gimp_api):
        """Test successful system info retrieval."""
        result = await mock_gimp_api.get_system_info()
        
        assert result["mode"] == "headless"
        assert result["connection_active"] is True
        assert result["api_version"] == "3.0"
        assert "capabilities" in result
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    async def test_get_system_info_failure(self, connection_error_api):
        """Test system info retrieval failure."""
        result = await connection_error_api.get_system_info()
        
        assert result["connection_active"] is False
        assert "error" in result
        
    def test_is_connected_property(self, mock_gimp_api):
        """Test is_connected property."""
        assert mock_gimp_api.is_connected is True
        
        mock_gimp_api.is_connected = False
        assert mock_gimp_api.is_connected is False
        
    def test_mode_property(self, mock_gimp_api):
        """Test mode property."""
        assert mock_gimp_api.mode == "headless"


class TestGimpAPIDocumentOperations:
    """Test GIMP API document lifecycle operations."""
    
    @pytest.mark.asyncio
    async def test_list_open_images_success(self, mock_gimp_api):
        """Test successful image listing."""
        # Configure mock to return sample images
        mock_gimp_api.list_open_images = AsyncMock(return_value=[
            {
                "id": 1,
                "name": "Test Image 1",
                "width": 800,
                "height": 600,
                "mode": "RGB"
            },
            {
                "id": 2,
                "name": "Test Image 2",
                "width": 1024,
                "height": 768,
                "mode": "RGB"
            }
        ])
        
        images = await mock_gimp_api.list_open_images()
        
        assert len(images) == 2
        assert images[0]["id"] == 1
        assert images[1]["name"] == "Test Image 2"
        
    @pytest.mark.asyncio
    async def test_list_open_images_empty(self, mock_gimp_api):
        """Test listing images when none are open."""
        images = await mock_gimp_api.list_open_images()
        
        assert isinstance(images, list)
        assert len(images) == 0
        
    @pytest.mark.asyncio
    async def test_get_active_image_exists(self, mock_gimp_api):
        """Test getting active image when one exists."""
        mock_gimp_api.get_active_image = AsyncMock(return_value={
            "id": 1,
            "name": "Active Image",
            "width": 800,
            "height": 600,
            "mode": "RGB"
        })
        
        image = await mock_gimp_api.get_active_image()
        
        assert image is not None
        assert image["id"] == 1
        assert image["name"] == "Active Image"
        
    @pytest.mark.asyncio
    async def test_get_active_image_none(self, mock_gimp_api):
        """Test getting active image when none exists."""
        image = await mock_gimp_api.get_active_image()
        
        assert image is None
        
    @pytest.mark.asyncio
    async def test_create_image_success(self, mock_gimp_api):
        """Test successful image creation."""
        result = await mock_gimp_api.create_image(800, 600, "RGB", "white", 300.0)
        
        assert result["success"] is True
        assert result["width"] == 800
        assert result["height"] == 600
        assert "image_id" in result
        
    @pytest.mark.asyncio
    async def test_create_image_with_defaults(self, mock_gimp_api):
        """Test image creation with default parameters."""
        mock_gimp_api.create_image = AsyncMock(return_value={
            "success": True,
            "image_id": 1,
            "width": 800,
            "height": 600,
            "image_type": "RGB",
            "resolution": 300.0
        })
        
        result = await mock_gimp_api.create_image(800, 600)
        
        assert result["success"] is True
        assert result["image_type"] == "RGB"
        assert result["resolution"] == 300.0
        
    @pytest.mark.asyncio
    async def test_open_image_success(self, mock_gimp_api, temp_image_file):
        """Test successful image opening."""
        result = await mock_gimp_api.open_image(temp_image_file)
        
        assert result["success"] is True
        assert result["file_path"] == temp_image_file
        assert "image_id" in result
        
    @pytest.mark.asyncio
    async def test_open_image_file_not_found(self, mock_gimp_api):
        """Test opening non-existent image file."""
        mock_gimp_api.open_image = AsyncMock(return_value={
            "success": False,
            "error": "File not found: /nonexistent/file.png",
            "file_path": "/nonexistent/file.png"
        })
        
        result = await mock_gimp_api.open_image("/nonexistent/file.png")
        
        assert result["success"] is False
        assert "File not found" in result["error"]
        
    @pytest.mark.asyncio
    async def test_save_image_success(self, mock_gimp_api, temp_directory):
        """Test successful image saving."""
        import os
        save_path = os.path.join(temp_directory, "test_output.png")
        
        result = await mock_gimp_api.save_image(1, save_path, "PNG")
        
        assert result["success"] is True
        assert result["image_id"] == 1
        assert result["file_path"] == save_path
        
    @pytest.mark.asyncio
    async def test_close_image_success(self, mock_gimp_api):
        """Test successful image closing."""
        result = await mock_gimp_api.close_image(1)
        
        assert result["success"] is True
        assert result["image_id"] == 1


class TestGimpAPILayerOperations:
    """Test GIMP API layer management operations."""
    
    @pytest.mark.asyncio
    async def test_create_layer_success(self, mock_gimp_api):
        """Test successful layer creation."""
        result = await mock_gimp_api.create_layer(
            image_id=1,
            layer_name="Test Layer",
            width=800,
            height=600,
            layer_type="RGB",
            opacity=100.0,
            blend_mode="normal"
        )
        
        assert result["success"] is True
        assert result["layer_name"] == "Test Layer"
        assert result["opacity"] == 100.0
        
    @pytest.mark.asyncio
    async def test_create_layer_with_defaults(self, mock_gimp_api):
        """Test layer creation with default parameters."""
        mock_gimp_api.create_layer = AsyncMock(return_value={
            "success": True,
            "layer_id": 2,
            "layer_name": "New Layer",
            "width": 800,
            "height": 600,
            "opacity": 100.0,
            "blend_mode": "normal"
        })
        
        result = await mock_gimp_api.create_layer(1, "New Layer")
        
        assert result["success"] is True
        assert result["opacity"] == 100.0
        assert result["blend_mode"] == "normal"
        
    @pytest.mark.asyncio
    async def test_delete_layer_success(self, mock_gimp_api):
        """Test successful layer deletion."""
        result = await mock_gimp_api.delete_layer(1, 2)
        
        assert result["success"] is True
        assert result["layer_id"] == 2
        
    @pytest.mark.asyncio
    async def test_set_layer_opacity_success(self, mock_gimp_api):
        """Test successful layer opacity setting."""
        result = await mock_gimp_api.set_layer_opacity(1, 2, 50.0)
        
        assert result["success"] is True
        assert result["layer_id"] == 2
        assert result["opacity"] == 50.0
        
    @pytest.mark.asyncio
    async def test_set_layer_blend_mode_success(self, mock_gimp_api):
        """Test successful layer blend mode setting."""
        result = await mock_gimp_api.set_layer_blend_mode(1, 2, "multiply")
        
        assert result["success"] is True
        assert result["layer_id"] == 2
        assert result["blend_mode"] == "multiply"


class TestGimpAPIDrawingOperations:
    """Test GIMP API drawing operations."""
    
    @pytest.mark.asyncio
    async def test_fill_layer_success(self, mock_gimp_api):
        """Test successful layer filling."""
        result = await mock_gimp_api.fill_layer(1, 2, "#FF0000")
        
        assert result["success"] is True
        assert result["layer_id"] == 2
        assert result["color"] == "#FF0000"
        
    @pytest.mark.asyncio
    async def test_draw_rectangle_success(self, mock_gimp_api):
        """Test successful rectangle drawing."""
        result = await mock_gimp_api.draw_rectangle(
            image_id=1,
            layer_id=2,
            x=10, y=10,
            width=100, height=80,
            stroke_color="#000000",
            fill_color="#FF0000",
            stroke_width=2.0
        )
        
        assert result["success"] is True
        assert result["x"] == 10
        assert result["y"] == 10
        assert result["width"] == 100
        assert result["height"] == 80
        
    @pytest.mark.asyncio
    async def test_draw_ellipse_success(self, mock_gimp_api):
        """Test successful ellipse drawing."""
        result = await mock_gimp_api.draw_ellipse(
            image_id=1,
            layer_id=2,
            x=50, y=50,
            width=120, height=100,
            stroke_color="#0000FF",
            fill_color="#00FF00",
            stroke_width=3.0
        )
        
        assert result["success"] is True
        assert result["x"] == 50
        assert result["y"] == 50
        assert result["width"] == 120
        assert result["height"] == 100
        
    @pytest.mark.asyncio
    async def test_draw_brush_stroke_success(self, mock_gimp_api):
        """Test successful brush stroke drawing."""
        points = [(10, 10), (50, 30), (100, 20), (150, 40)]
        
        result = await mock_gimp_api.draw_brush_stroke(
            image_id=1,
            layer_id=2,
            points=points,
            brush_size=15.0,
            brush_color="#FF00FF"
        )
        
        assert result["success"] is True
        assert result["points_count"] == 4
        assert result["layer_id"] == 2


class TestGimpAPIImageInfo:
    """Test GIMP API image information retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_image_info_success(self, mock_gimp_api):
        """Test successful image info retrieval."""
        result = await mock_gimp_api.get_image_info(1)
        
        assert result["success"] is True
        assert "image_info" in result
        image_info = result["image_info"]
        assert image_info["id"] == 1
        assert "layers" in image_info
        
    @pytest.mark.asyncio
    async def test_get_image_info_not_found(self, mock_gimp_api):
        """Test image info retrieval for non-existent image."""
        mock_gimp_api.get_image_info = AsyncMock(return_value={
            "success": False,
            "error": "Image not found: 999",
            "image_id": 999
        })
        
        result = await mock_gimp_api.get_image_info(999)
        
        assert result["success"] is False
        assert "Image not found" in result["error"]


class TestGimpAPIExecuteOperation:
    """Test GIMP API generic operation execution."""
    
    @pytest.mark.asyncio
    async def test_execute_operation_known_operation(self, mock_gimp_api):
        """Test execution of known operation."""
        result = await mock_gimp_api.execute_operation("create_image", 800, 600)
        
        assert result["success"] is True
        assert "operation" in result
        
    @pytest.mark.asyncio
    async def test_execute_operation_unknown_operation(self, mock_gimp_api):
        """Test execution of unknown operation."""
        mock_gimp_api.execute_operation = AsyncMock(return_value={
            "success": True,
            "operation": "unknown_operation",
            "args": ("arg1", "arg2"),
            "kwargs": {"param": "value"}
        })
        
        result = await mock_gimp_api.execute_operation(
            "unknown_operation", "arg1", "arg2", param="value"
        )
        
        assert result["success"] is True
        assert result["operation"] == "unknown_operation"
        
    @pytest.mark.asyncio
    async def test_execute_operation_failure(self, operation_error_api):
        """Test operation execution failure."""
        result = await operation_error_api.execute_operation("create_image", 800, 600)
        
        assert result["success"] is False
        assert "error" in result


class TestGimpAPICleanup:
    """Test GIMP API cleanup and resource management."""
    
    @pytest.mark.asyncio
    async def test_cleanup_success(self, mock_gimp_api):
        """Test successful cleanup."""
        await mock_gimp_api.cleanup()
        
        # Verify cleanup was called
        mock_gimp_api.cleanup.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_cleanup_with_error(self, mock_gimp_api):
        """Test cleanup with error handling."""
        # Configure cleanup to raise an error
        mock_gimp_api.cleanup = AsyncMock(side_effect=Exception("Cleanup error"))
        
        # Should not raise exception
        await mock_gimp_api.cleanup()


class TestGimpAPIEdgeCases:
    """Test GIMP API edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_invalid_image_dimensions(self, mock_gimp_api):
        """Test creation with invalid dimensions."""
        mock_gimp_api.create_image = AsyncMock(return_value={
            "success": False,
            "error": "Invalid dimensions: width and height must be positive"
        })
        
        result = await mock_gimp_api.create_image(-1, 600)
        
        assert result["success"] is False
        assert "Invalid dimensions" in result["error"]
        
    @pytest.mark.asyncio
    async def test_invalid_opacity_value(self, mock_gimp_api):
        """Test setting invalid opacity value."""
        mock_gimp_api.set_layer_opacity = AsyncMock(return_value={
            "success": False,
            "error": "Invalid opacity: must be between 0.0 and 100.0"
        })
        
        result = await mock_gimp_api.set_layer_opacity(1, 2, 150.0)
        
        assert result["success"] is False
        assert "Invalid opacity" in result["error"]
        
    @pytest.mark.asyncio
    async def test_invalid_color_format(self, mock_gimp_api):
        """Test using invalid color format."""
        mock_gimp_api.fill_layer = AsyncMock(return_value={
            "success": False,
            "error": "Invalid color format: invalid_color"
        })
        
        result = await mock_gimp_api.fill_layer(1, 2, "invalid_color")
        
        assert result["success"] is False
        assert "Invalid color format" in result["error"]
        
    @pytest.mark.asyncio
    async def test_empty_brush_stroke_points(self, mock_gimp_api):
        """Test brush stroke with empty points."""
        mock_gimp_api.draw_brush_stroke = AsyncMock(return_value={
            "success": False,
            "error": "Invalid brush stroke: no points provided"
        })
        
        result = await mock_gimp_api.draw_brush_stroke(1, 2, [])
        
        assert result["success"] is False
        assert "no points provided" in result["error"]


class TestGimpAPIPerformance:
    """Test GIMP API performance characteristics."""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_connection_test_performance(self, mock_gimp_api, performance_helper):
        """Test connection test performance."""
        result, duration = await performance_helper.measure_execution_time(
            mock_gimp_api.test_connection
        )
        
        assert result["success"] is True
        assert duration < 1.0  # Should complete within 1 second
        
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_image_creation_performance(self, mock_gimp_api, performance_helper):
        """Test image creation performance."""
        result, duration = await performance_helper.measure_execution_time(
            mock_gimp_api.create_image, 800, 600
        )
        
        assert result["success"] is True
        assert duration < 2.0  # Should complete within 2 seconds
        
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_multiple_operations_performance(self, mock_gimp_api, performance_helper):
        """Test performance of multiple operations."""
        operations = [
            (mock_gimp_api.create_image, (800, 600)),
            (mock_gimp_api.create_layer, (1, "Test Layer")),
            (mock_gimp_api.fill_layer, (1, 2, "#FF0000")),
            (mock_gimp_api.save_image, (1, "/test/path.png"))
        ]
        
        total_duration = 0
        for operation, args in operations:
            result, duration = await performance_helper.measure_execution_time(
                operation, *args
            )
            total_duration += duration
            assert result["success"] is True
            
        # All operations should complete within 5 seconds total
        assert total_duration < 5.0


@pytest.mark.asyncio
async def test_gimp_api_context_manager_success(mock_mode_manager, mock_gi_modules):
    """Test GIMP API context manager success case."""
    with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
        api = GimpAPI(mode_manager=mock_mode_manager)
        
        # Mock the _verify_connection method
        api._verify_connection = AsyncMock(return_value=True)
        api._gimp = Mock()
        
        async with api.ensure_connection() as gimp:
            assert gimp is api._gimp


@pytest.mark.asyncio
async def test_gimp_api_context_manager_connection_failure(mock_mode_manager, mock_gi_modules):
    """Test GIMP API context manager connection failure."""
    with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
        api = GimpAPI(mode_manager=mock_mode_manager)
        
        # Mock connection failure
        api._verify_connection = AsyncMock(return_value=False)
        
        with pytest.raises(GimpConnectionError, match="Cannot establish GIMP connection"):
            async with api.ensure_connection():
                pass