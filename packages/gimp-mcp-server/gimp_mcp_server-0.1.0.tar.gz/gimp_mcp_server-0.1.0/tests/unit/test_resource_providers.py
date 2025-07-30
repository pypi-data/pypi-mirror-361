"""
Unit tests for resource providers implementation.

This module tests the ResourceProviders class which provides
MCP resources for real-time state monitoring and information access.
"""

import pytest
import time
from unittest.mock import Mock, AsyncMock

from gimp_mcp.resources.providers import ResourceProviders
from gimp_mcp.utils.errors import GimpError, GimpConnectionError


class TestResourceProvidersInitialization:
    """Test ResourceProviders initialization."""
    
    def test_init_with_gimp_api(self, mock_gimp_api):
        """Test initialization with GIMP API."""
        providers = ResourceProviders(mock_gimp_api)
        
        assert providers.gimp_api is mock_gimp_api
        
    def test_init_without_gimp_api(self):
        """Test initialization without GIMP API raises error."""
        with pytest.raises(ValueError, match="GimpAPI instance is required"):
            ResourceProviders(None)


class TestCurrentDocumentResource:
    """Test current document resource provider."""
    
    @pytest.mark.asyncio
    async def test_get_current_document_success(self, mock_gimp_api):
        """Test successful current document retrieval."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_active_image = AsyncMock(return_value={
            "id": 1,
            "name": "Current Document",
            "width": 800,
            "height": 600,
            "mode": "RGB"
        })
        
        result = await providers.get_current_document()
        
        assert result["success"] is True
        assert result["document"]["id"] == 1
        assert result["document"]["name"] == "Current Document"
        assert result["document"]["active"] is True
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    async def test_get_current_document_none_active(self, mock_gimp_api):
        """Test current document retrieval when no document is active."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_active_image = AsyncMock(return_value=None)
        
        result = await providers.get_current_document()
        
        assert result["success"] is True
        assert result["document"] is None
        assert result["message"] == "No active document"
        
    @pytest.mark.asyncio
    async def test_get_current_document_error(self, mock_gimp_api):
        """Test current document retrieval with error."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_active_image = AsyncMock(
            side_effect=GimpConnectionError("Connection failed")
        )
        
        result = await providers.get_current_document()
        
        assert result["success"] is False
        assert "Connection failed" in result["error"]


class TestDocumentListResource:
    """Test document list resource provider."""
    
    @pytest.mark.asyncio
    async def test_get_document_list_success(self, mock_gimp_api):
        """Test successful document list retrieval."""
        providers = ResourceProviders(mock_gimp_api)
        
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
        
        result = await providers.get_document_list()
        
        assert result["success"] is True
        assert len(result["documents"]) == 2
        assert result["count"] == 2
        assert result["documents"][0]["name"] == "Document 1"
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    async def test_get_document_list_empty(self, mock_gimp_api):
        """Test document list retrieval when no documents are open."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.list_open_images = AsyncMock(return_value=[])
        
        result = await providers.get_document_list()
        
        assert result["success"] is True
        assert len(result["documents"]) == 0
        assert result["count"] == 0
        
    @pytest.mark.asyncio
    async def test_get_document_list_with_filtering(self, mock_gimp_api):
        """Test document list retrieval with filtering."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.list_open_images = AsyncMock(return_value=[
            {
                "id": 1,
                "name": "RGB Document",
                "width": 800,
                "height": 600,
                "mode": "RGB"
            },
            {
                "id": 2,
                "name": "Grayscale Document",
                "width": 1024,
                "height": 768,
                "mode": "GRAYSCALE"
            }
        ])
        
        result = await providers.get_document_list(filter_mode="RGB")
        
        assert result["success"] is True
        assert len(result["documents"]) == 1
        assert result["documents"][0]["mode"] == "RGB"


class TestDocumentMetadataResource:
    """Test document metadata resource provider."""
    
    @pytest.mark.asyncio
    async def test_get_document_metadata_success(self, mock_gimp_api):
        """Test successful document metadata retrieval."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_image_info = AsyncMock(return_value={
            "success": True,
            "image_info": {
                "id": 1,
                "name": "Test Document",
                "width": 800,
                "height": 600,
                "mode": "RGB",
                "resolution": 300.0,
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
        
        # Mock additional metadata
        mock_gimp_api.get_document_metadata = AsyncMock(return_value={
            "file_size": 1024000,
            "created_date": "2023-01-01T00:00:00Z",
            "modified_date": "2023-01-02T00:00:00Z",
            "color_profile": "sRGB",
            "has_alpha": False
        })
        
        result = await providers.get_document_metadata(document_id=1)
        
        assert result["success"] is True
        assert result["metadata"]["basic_info"]["name"] == "Test Document"
        assert result["metadata"]["basic_info"]["layer_count"] == 1
        assert "technical_info" in result["metadata"]
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    async def test_get_document_metadata_not_found(self, mock_gimp_api):
        """Test document metadata retrieval for non-existent document."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_image_info = AsyncMock(return_value={
            "success": False,
            "error": "Image not found: 999"
        })
        
        result = await providers.get_document_metadata(document_id=999)
        
        assert result["success"] is False
        assert "Image not found" in result["error"]


class TestSystemStatusResource:
    """Test system status resource provider."""
    
    @pytest.mark.asyncio
    async def test_get_system_status_success(self, mock_gimp_api):
        """Test successful system status retrieval."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_system_info = AsyncMock(return_value={
            "mode": "headless",
            "connection_active": True,
            "api_version": "3.0",
            "server_version": "0.1.0",
            "capabilities": {
                "document_management": True,
                "layer_operations": True,
                "drawing_tools": True
            }
        })
        
        mock_gimp_api.test_connection = AsyncMock(return_value={
            "success": True,
            "mode": "headless",
            "connection_verified": True
        })
        
        result = await providers.get_system_status()
        
        assert result["success"] is True
        assert result["status"]["connection"]["active"] is True
        assert result["status"]["mode"]["current"] == "headless"
        assert result["status"]["performance"]["uptime"] > 0
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    async def test_get_system_status_connection_failed(self, connection_error_api):
        """Test system status with connection failure."""
        providers = ResourceProviders(connection_error_api)
        
        result = await providers.get_system_status()
        
        assert result["success"] is True  # Status should still return info
        assert result["status"]["connection"]["active"] is False
        assert "error" in result["status"]["connection"]


class TestSystemCapabilitiesResource:
    """Test system capabilities resource provider."""
    
    @pytest.mark.asyncio
    async def test_get_system_capabilities_success(self, mock_gimp_api):
        """Test successful system capabilities retrieval."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_system_info = AsyncMock(return_value={
            "capabilities": {
                "document_management": True,
                "layer_operations": True,
                "drawing_tools": True,
                "selection_tools": True,
                "color_management": True,
                "filter_operations": True
            },
            "mode": "headless"
        })
        
        result = await providers.get_system_capabilities()
        
        assert result["success"] is True
        assert result["capabilities"]["core"]["document_management"] is True
        assert result["capabilities"]["core"]["layer_operations"] is True
        assert result["capabilities"]["mode"]["current"] == "headless"
        assert "supported_formats" in result["capabilities"]
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    async def test_get_system_capabilities_with_mode_info(self, mock_gimp_api, mock_mode_manager):
        """Test system capabilities with mode information."""
        providers = ResourceProviders(mock_gimp_api)
        mock_gimp_api.mode_manager = mock_mode_manager
        
        mock_mode_manager.get_mode_info = Mock(return_value={
            "current_mode": "headless",
            "capabilities": {
                "gui_available": False,
                "headless_available": True,
                "can_switch_modes": True
            }
        })
        
        result = await providers.get_system_capabilities()
        
        assert result["success"] is True
        assert result["capabilities"]["mode"]["can_switch"] is True


class TestSystemHealthResource:
    """Test system health resource provider."""
    
    @pytest.mark.asyncio
    async def test_get_system_health_healthy(self, mock_gimp_api):
        """Test system health when everything is healthy."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.test_connection = AsyncMock(return_value={
            "success": True,
            "mode": "headless",
            "connection_verified": True
        })
        
        mock_gimp_api.get_system_info = AsyncMock(return_value={
            "connection_active": True,
            "mode": "headless"
        })
        
        result = await providers.get_system_health()
        
        assert result["success"] is True
        assert result["health"]["overall_status"] == "healthy"
        assert result["health"]["connection"]["status"] == "connected"
        assert result["health"]["connection"]["healthy"] is True
        assert "checks_performed" in result["health"]
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    async def test_get_system_health_unhealthy(self, connection_error_api):
        """Test system health when connection is unhealthy."""
        providers = ResourceProviders(connection_error_api)
        
        result = await providers.get_system_health()
        
        assert result["success"] is True
        assert result["health"]["overall_status"] in ["unhealthy", "degraded"]
        assert result["health"]["connection"]["healthy"] is False
        
    @pytest.mark.asyncio
    async def test_get_system_health_with_performance_metrics(self, mock_gimp_api):
        """Test system health with performance metrics."""
        providers = ResourceProviders(mock_gimp_api)
        
        # Mock performance measurement
        providers._measure_response_time = AsyncMock(return_value=0.05)  # 50ms
        
        result = await providers.get_system_health()
        
        assert result["success"] is True
        assert "performance" in result["health"]
        assert result["health"]["performance"]["response_time"] < 1.0


class TestActivePaletteResource:
    """Test active palette resource provider."""
    
    @pytest.mark.asyncio
    async def test_get_active_palette_success(self, mock_gimp_api):
        """Test successful active palette retrieval."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_active_palette = AsyncMock(return_value={
            "success": True,
            "palette": {
                "name": "Default Palette",
                "colors": [
                    {"name": "Black", "color": "#000000"},
                    {"name": "White", "color": "#FFFFFF"},
                    {"name": "Red", "color": "#FF0000"}
                ]
            }
        })
        
        result = await providers.get_active_palette()
        
        assert result["success"] is True
        assert result["palette"]["name"] == "Default Palette"
        assert len(result["palette"]["colors"]) == 3
        assert "timestamp" in result
        
    @pytest.mark.asyncio
    async def test_get_active_palette_none(self, mock_gimp_api):
        """Test active palette retrieval when no palette is active."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_active_palette = AsyncMock(return_value={
            "success": True,
            "palette": None
        })
        
        result = await providers.get_active_palette()
        
        assert result["success"] is True
        assert result["palette"] is None
        assert result["message"] == "No active palette"


class TestBrushListResource:
    """Test brush list resource provider."""
    
    @pytest.mark.asyncio
    async def test_get_brush_list_success(self, mock_gimp_api):
        """Test successful brush list retrieval."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_brush_list = AsyncMock(return_value={
            "success": True,
            "brushes": [
                {
                    "name": "2. Hardness 050",
                    "size": 10.0,
                    "hardness": 0.5,
                    "spacing": 10
                },
                {
                    "name": "3. Hardness 075",
                    "size": 15.0,
                    "hardness": 0.75,
                    "spacing": 15
                }
            ]
        })
        
        result = await providers.get_brush_list()
        
        assert result["success"] is True
        assert len(result["brushes"]) == 2
        assert result["brushes"][0]["name"] == "2. Hardness 050"
        assert "timestamp" in result


class TestCurrentToolResource:
    """Test current tool resource provider."""
    
    @pytest.mark.asyncio
    async def test_get_current_tool_success(self, mock_gimp_api):
        """Test successful current tool retrieval."""
        providers = ResourceProviders(mock_gimp_api)
        
        mock_gimp_api.get_active_tool = AsyncMock(return_value={
            "success": True,
            "tool": {
                "name": "paintbrush",
                "display_name": "Paintbrush",
                "options": {
                    "brush": "2. Hardness 050",
                    "size": 10.0,
                    "opacity": 100.0,
                    "mode": "normal"
                }
            }
        })
        
        result = await providers.get_current_tool()
        
        assert result["success"] is True
        assert result["tool"]["name"] == "paintbrush"
        assert result["tool"]["options"]["size"] == 10.0
        assert "timestamp" in result


class TestResourceProvidersPerformance:
    """Test resource providers performance."""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_current_document_performance(self, mock_gimp_api, performance_helper):
        """Test current document resource performance."""
        providers = ResourceProviders(mock_gimp_api)
        
        result, duration = await performance_helper.measure_execution_time(
            providers.get_current_document
        )
        
        assert result["success"] is True
        assert duration < 0.5  # Should complete within 500ms
        
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_system_status_performance(self, mock_gimp_api, performance_helper):
        """Test system status resource performance."""
        providers = ResourceProviders(mock_gimp_api)
        
        result, duration = await performance_helper.measure_execution_time(
            providers.get_system_status
        )
        
        assert result["success"] is True
        assert duration < 1.0  # Should complete within 1 second
        
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_multiple_resources_performance(self, mock_gimp_api, performance_helper):
        """Test performance of accessing multiple resources."""
        providers = ResourceProviders(mock_gimp_api)
        
        async def access_multiple_resources():
            results = await asyncio.gather(
                providers.get_current_document(),
                providers.get_document_list(),
                providers.get_system_status(),
                providers.get_system_health()
            )
            return results
        
        results, duration = await performance_helper.measure_execution_time(
            access_multiple_resources
        )
        
        assert len(results) == 4
        assert all(r["success"] for r in results)
        assert duration < 2.0  # All resources should complete within 2 seconds


class TestResourceProvidersErrorHandling:
    """Test resource providers error handling."""
    
    @pytest.mark.asyncio
    async def test_handle_connection_error(self, connection_error_api):
        """Test handling of connection errors."""
        providers = ResourceProviders(connection_error_api)
        
        result = await providers.get_current_document()
        
        assert result["success"] is False
        assert "error" in result
        
    @pytest.mark.asyncio
    async def test_handle_operation_error(self, operation_error_api):
        """Test handling of operation errors."""
        providers = ResourceProviders(operation_error_api)
        
        result = await providers.get_document_list()
        
        assert result["success"] is False
        assert "error" in result
        
    @pytest.mark.asyncio
    async def test_handle_timeout_error(self, timeout_error_api):
        """Test handling of timeout errors."""
        providers = ResourceProviders(timeout_error_api)
        
        result = await providers.get_system_status()
        
        # Should handle timeout gracefully
        assert "success" in result
        
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, mock_gimp_api):
        """Test graceful degradation when some operations fail."""
        providers = ResourceProviders(mock_gimp_api)
        
        # Mock partial failure
        mock_gimp_api.get_active_image = AsyncMock(return_value=None)
        mock_gimp_api.test_connection = AsyncMock(return_value={
            "success": True,
            "mode": "headless"
        })
        
        result = await providers.get_system_health()
        
        assert result["success"] is True
        # Should still provide partial health information


class TestResourceProvidersRealTimeMonitoring:
    """Test resource providers real-time monitoring capabilities."""
    
    @pytest.mark.asyncio
    async def test_real_time_document_changes(self, mock_gimp_api):
        """Test real-time monitoring of document changes."""
        providers = ResourceProviders(mock_gimp_api)
        
        # Simulate document change
        initial_docs = []
        updated_docs = [{"id": 1, "name": "New Document"}]
        
        mock_gimp_api.list_open_images = AsyncMock(side_effect=[initial_docs, updated_docs])
        
        # First call - no documents
        result1 = await providers.get_document_list()
        assert len(result1["documents"]) == 0
        
        # Second call - new document appeared
        result2 = await providers.get_document_list()
        assert len(result2["documents"]) == 1
        
    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, mock_gimp_api):
        """Test system health monitoring over time."""
        providers = ResourceProviders(mock_gimp_api)
        
        # Simulate connection state changes
        connection_states = [
            {"success": True, "connection_verified": True},
            {"success": False, "connection_verified": False},
            {"success": True, "connection_verified": True}
        ]
        
        mock_gimp_api.test_connection = AsyncMock(side_effect=connection_states)
        
        # Monitor health changes
        health_results = []
        for _ in range(3):
            result = await providers.get_system_health()
            health_results.append(result["health"]["connection"]["healthy"])
            
        assert health_results == [True, False, True]


@pytest.fixture
def resource_providers(mock_gimp_api):
    """Create ResourceProviders instance for testing."""
    return ResourceProviders(mock_gimp_api)


@pytest.mark.asyncio
async def test_resource_providers_integration(resource_providers, mock_gimp_api):
    """Test resource providers integration scenario."""
    # Test accessing all main resources
    current_doc = await resource_providers.get_current_document()
    doc_list = await resource_providers.get_document_list()
    status = await resource_providers.get_system_status()
    health = await resource_providers.get_system_health()
    capabilities = await resource_providers.get_system_capabilities()
    
    # All should succeed with mocked data
    assert current_doc["success"] is True or "No active document" in current_doc.get("message", "")
    assert doc_list["success"] is True
    assert status["success"] is True
    assert health["success"] is True
    assert capabilities["success"] is True