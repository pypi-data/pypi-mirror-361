"""
Pytest configuration and fixtures for GIMP MCP Server tests.

This module provides comprehensive test fixtures and configuration
for the entire test suite including mocks, test data, and helpers.
"""

import pytest
import asyncio
import tempfile
import os
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

from gimp_mcp.gimp_api import GimpAPI
from gimp_mcp.mode_manager import GimpModeManager
from gimp_mcp.server import GimpMCPServer, ServerConfig

# Import mock implementations
from .mocks.mock_gimp import create_mock_gimp_modules, MockGimpAPI, MockGimpImage, MockGimpLayer
from .mocks.mock_mcp_client import MockMCPClient, MockMCPServer
from .mocks.test_fixtures import (
    TestImageFactory, TestDataProvider, TestEnvironmentManager,
    AsyncTestHelper, MCPTestHelper, PerformanceTestHelper, ErrorTestHelper
)


# ============================================================================
# Core Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def test_env():
    """Create and manage test environment."""
    env = TestEnvironmentManager()
    yield env
    env.cleanup()


@pytest.fixture
def mock_gi_modules():
    """Mock GObject Introspection modules."""
    modules = create_mock_gimp_modules()
    
    # Patch gi imports
    with patch.dict('sys.modules', {
        'gi': Mock(),
        'gi.repository': Mock(),
        'gi.repository.Gimp': modules['Gimp'],
        'gi.repository.Gtk': Mock(),
        'gi.repository.GObject': Mock(),
        'gi.repository.Gio': Mock(),
    }):
        yield modules


# ============================================================================
# GIMP API Fixtures
# ============================================================================

@pytest.fixture
def mock_gimp_api(mock_gi_modules):
    """Create a comprehensive mock GIMP API instance."""
    api = Mock(spec=GimpAPI)
    
    # Connection and health methods
    api.test_connection = AsyncMock(return_value={
        "success": True,
        "mode": "headless",
        "connection_verified": True,
        "timestamp": 1234567890.0
    })
    
    api.get_system_info = AsyncMock(return_value={
        "mode": "headless",
        "connection_active": True,
        "api_version": "3.0",
        "server_version": "0.1.0",
        "capabilities": {
            "document_management": True,
            "layer_operations": True,
            "drawing_tools": True,
            "selection_tools": True,
            "color_management": True,
            "filter_operations": True,
        },
        "timestamp": 1234567890.0
    })
    
    # Document methods
    api.list_open_images = AsyncMock(return_value=[])
    api.get_active_image = AsyncMock(return_value=None)
    api.get_image_info = AsyncMock(return_value={
        "success": True,
        "image_info": {
            "id": 1,
            "name": "Test Image",
            "width": 800,
            "height": 600,
            "layers": []
        }
    })
    
    # Document lifecycle methods
    api.create_image = AsyncMock(return_value={
        "success": True,
        "image_id": 1,
        "width": 800,
        "height": 600
    })
    api.open_image = AsyncMock(return_value={
        "success": True,
        "image_id": 2,
        "file_path": "/test/path.png"
    })
    api.save_image = AsyncMock(return_value={
        "success": True,
        "image_id": 1,
        "file_path": "/test/output.png"
    })
    api.close_image = AsyncMock(return_value={
        "success": True,
        "image_id": 1
    })
    
    # Layer methods
    api.create_layer = AsyncMock(return_value={
        "success": True,
        "layer_id": 2,
        "layer_name": "New Layer"
    })
    api.delete_layer = AsyncMock(return_value={
        "success": True,
        "layer_id": 2
    })
    api.set_layer_opacity = AsyncMock(return_value={
        "success": True,
        "layer_id": 1,
        "opacity": 50.0
    })
    api.set_layer_blend_mode = AsyncMock(return_value={
        "success": True,
        "layer_id": 1,
        "blend_mode": "multiply"
    })
    
    # Drawing methods
    api.fill_layer = AsyncMock(return_value={
        "success": True,
        "layer_id": 1,
        "color": "#FF0000"
    })
    api.draw_rectangle = AsyncMock(return_value={
        "success": True,
        "layer_id": 1,
        "x": 10, "y": 10, "width": 100, "height": 80
    })
    api.draw_ellipse = AsyncMock(return_value={
        "success": True,
        "layer_id": 1,
        "x": 50, "y": 50, "width": 120, "height": 100
    })
    api.draw_brush_stroke = AsyncMock(return_value={
        "success": True,
        "layer_id": 1,
        "points_count": 4
    })
    
    # Generic operation execution
    api.execute_operation = AsyncMock(return_value={
        "success": True,
        "operation": "test_operation"
    })
    
    # Cleanup and properties
    api.cleanup = AsyncMock()
    api.is_connected = True
    api.mode = "headless"
    
    # Add mock GIMP instance
    api._gimp = mock_gi_modules['gimp_api']
    api.mode_manager = Mock()
    api.mode_manager.gui_mode = False
    
    return api


@pytest.fixture
def mock_mode_manager():
    """Create a comprehensive mock mode manager."""
    manager = Mock(spec=GimpModeManager)
    manager.gui_mode = False
    manager.get_gimp_instance = Mock(return_value=Mock())
    manager.get_mode_info = Mock(return_value={
        "current_mode": "headless",
        "forced_mode": None,
        "connection_verified": True,
        "capabilities": {
            "gui_available": False,
            "headless_available": True,
            "can_switch_modes": True,
        }
    })
    manager.switch_to_gui_mode = Mock(return_value=True)
    manager.switch_to_headless_mode = Mock(return_value=True)
    manager.verify_mode_capabilities = Mock(return_value=True)
    
    return manager


# ============================================================================
# Server and Configuration Fixtures
# ============================================================================

@pytest.fixture
def server_config():
    """Create a test server configuration."""
    return ServerConfig(
        host="localhost",
        port=3001,  # Different port for tests
        debug=True,
        mode="headless",
        log_level="DEBUG"
    )


@pytest.fixture
def alternative_server_configs():
    """Create alternative server configurations for testing."""
    return [
        ServerConfig(host="localhost", port=3002, mode="gui"),
        ServerConfig(host="0.0.0.0", port=3003, mode="headless", debug=False),
        ServerConfig(host="localhost", port=3004, mode=None),  # Auto-detect
    ]


@pytest.fixture
async def mock_gimp_server(mock_gimp_api, mock_mode_manager, server_config):
    """Create a mock GIMP MCP server instance."""
    server = Mock(spec=GimpMCPServer)
    server.config = server_config
    server.gimp_api = mock_gimp_api
    server.mode_manager = mock_mode_manager
    server.is_running = False
    
    # Mock server methods
    server.run = AsyncMock()
    server._check_gimp_connection = AsyncMock()
    server._initialize_components = Mock()
    server._register_tools = Mock()
    server._register_resources = Mock()
    
    # Mock FastMCP app
    server.app = Mock()
    server.app.add_tool = Mock()
    server.app.add_resource = Mock()
    server.app.run = AsyncMock()
    
    return server


# ============================================================================
# MCP Client and Protocol Fixtures
# ============================================================================

@pytest.fixture
def mock_mcp_client():
    """Create a mock MCP client for testing."""
    return MockMCPClient()


@pytest.fixture
def mock_mcp_server():
    """Create a mock MCP server for testing."""
    return MockMCPServer()


@pytest.fixture
def mcp_test_helper():
    """Create MCP test helper."""
    return MCPTestHelper()


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
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
                "width": 800,
                "height": 600,
                "opacity": 100.0,
                "visible": True,
                "blend_mode": "normal",
            }
        ]
    }


@pytest.fixture
def sample_layer_data():
    """Sample layer data for testing."""
    return {
        "id": 1,
        "name": "Test Layer",
        "width": 800,
        "height": 600,
        "opacity": 100.0,
        "visible": True,
        "blend_mode": "normal",
        "layer_type": "RGB",
    }


@pytest.fixture
def sample_color_data():
    """Sample color data for testing."""
    return {
        "hex": "#FF5733",
        "rgb": "rgb(255, 87, 51)",
        "rgba": (1.0, 0.34, 0.2, 1.0),
    }


@pytest.fixture
def sample_brush_stroke_data():
    """Sample brush stroke data for testing."""
    return {
        "points": [(10, 10), (50, 50), (100, 30)],
        "brush_name": "2. Hardness 050",
        "size": 10.0,
        "opacity": 100.0,
        "color": "#000000",
    }


@pytest.fixture
def test_data_provider():
    """Provide comprehensive test data."""
    return TestDataProvider()


@pytest.fixture
def document_test_data(test_data_provider):
    """Get document test data."""
    return test_data_provider.get_document_test_data()


@pytest.fixture
def layer_test_data(test_data_provider):
    """Get layer test data."""
    return test_data_provider.get_layer_test_data()


@pytest.fixture
def drawing_test_data(test_data_provider):
    """Get drawing test data."""
    return test_data_provider.get_drawing_test_data()


@pytest.fixture
def color_test_data(test_data_provider):
    """Get color test data."""
    return test_data_provider.get_color_test_data()


# ============================================================================
# Image and Layer Factory Fixtures
# ============================================================================

@pytest.fixture
def image_factory():
    """Create test image factory."""
    return TestImageFactory()


@pytest.fixture
def simple_test_image(image_factory):
    """Create a simple test image."""
    return image_factory.create_simple_image()


@pytest.fixture
def multilayer_test_image(image_factory):
    """Create a multi-layer test image."""
    return image_factory.create_multilayer_image()


@pytest.fixture
def complex_test_image(image_factory):
    """Create a complex test image."""
    return image_factory.create_complex_image()


# ============================================================================
# Helper Fixtures
# ============================================================================

@pytest.fixture
def async_helper():
    """Create async test helper."""
    return AsyncTestHelper()


@pytest.fixture
def performance_helper():
    """Create performance test helper."""
    return PerformanceTestHelper()


@pytest.fixture
def error_helper():
    """Create error test helper."""
    return ErrorTestHelper()


# ============================================================================
# File and Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_directory(test_env):
    """Create a temporary directory for testing."""
    return test_env.create_temp_directory()


@pytest.fixture
def temp_image_file(test_env):
    """Create a temporary image file for testing."""
    return test_env.create_temp_file(suffix=".png")


@pytest.fixture
def temp_project_file(test_env):
    """Create a temporary project file for testing."""
    return test_env.create_temp_file(
        content='{"name": "Test Project", "version": "1.0"}',
        suffix=".json"
    )


# ============================================================================
# Error and Edge Case Fixtures
# ============================================================================

@pytest.fixture
def connection_error_api(mock_gimp_api, error_helper):
    """Create a GIMP API that simulates connection errors."""
    mock_gimp_api.test_connection = AsyncMock(
        side_effect=error_helper.create_connection_error()
    )
    mock_gimp_api.is_connected = False
    return mock_gimp_api


@pytest.fixture
def operation_error_api(mock_gimp_api, error_helper):
    """Create a GIMP API that simulates operation errors."""
    mock_gimp_api.create_image = AsyncMock(
        side_effect=error_helper.create_operation_error("create_image")
    )
    return mock_gimp_api


@pytest.fixture
def timeout_error_api(mock_gimp_api, error_helper):
    """Create a GIMP API that simulates timeout errors."""
    mock_gimp_api.execute_operation = AsyncMock(
        side_effect=error_helper.create_timeout_error("execute_operation")
    )
    return mock_gimp_api


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def performance_benchmarks():
    """Create performance benchmarks for testing."""
    return [
        {
            "operation": "create_document",
            "max_duration": 0.5,
            "parameters": {"width": 800, "height": 600}
        },
        {
            "operation": "create_layer",
            "max_duration": 0.3,
            "parameters": {"name": "Test Layer"}
        },
        {
            "operation": "apply_brush_stroke",
            "max_duration": 1.0,
            "parameters": {"points": [(0, 0), (100, 100)]}
        }
    ]


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may take longer to run)"
    )
    config.addinivalue_line(
        "markers", "gimp: marks tests that require GIMP connection"
    )
    config.addinivalue_line(
        "markers", "mcp: marks tests for MCP protocol compliance"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests for performance benchmarking"
    )
    config.addinivalue_line(
        "markers", "error: marks tests for error handling"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "error" in str(item.fspath):
            item.add_marker(pytest.mark.error)
        
        # Add slow marker for tests that might take longer
        if any(keyword in item.name.lower() for keyword in ["timeout", "large", "complex", "stress"]):
            item.add_marker(pytest.mark.slow)


# ============================================================================
# Legacy Compatibility
# ============================================================================

# Keep existing fixtures for backward compatibility
class MockGimpModule:
    """Mock GIMP module for testing without actual GIMP."""
    
    class BlendMode:
        NORMAL = 0
        MULTIPLY = 1
        SCREEN = 2
        OVERLAY = 3
    
    class ImageBaseType:
        RGB = 0
        GRAY = 1
        INDEXED = 2
    
    class FillType:
        FOREGROUND = 0
        BACKGROUND = 1
        WHITE = 2
        TRANSPARENT = 3
        PATTERN = 4
    
    @staticmethod
    def list_images():
        return []
    
    @staticmethod
    def get_active_image():
        return None