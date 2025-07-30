"""
Test fixtures and helpers for GIMP MCP server testing.

This module provides comprehensive test fixtures and helper functions
for testing the GIMP MCP server implementation.
"""

import asyncio
import tempfile
import os
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock, patch
from contextlib import asynccontextmanager

from .mock_gimp import create_mock_gimp_modules, MockGimpAPI, MockGimpImage, MockGimpLayer
from .mock_mcp_client import MockMCPClient, MockMCPServer


class TestImageFactory:
    """Factory for creating test images with various configurations."""
    
    @staticmethod
    def create_simple_image(width: int = 800, height: int = 600, name: str = "Test Image") -> MockGimpImage:
        """Create a simple test image with background layer."""
        image = MockGimpImage(1, name, width, height)
        layer = MockGimpLayer(1, "Background", width, height)
        image.insert_layer(layer)
        return image
        
    @staticmethod
    def create_multilayer_image(width: int = 800, height: int = 600, 
                               layer_count: int = 3, name: str = "Multi-layer Image") -> MockGimpImage:
        """Create a test image with multiple layers."""
        image = MockGimpImage(1, name, width, height)
        
        for i in range(layer_count):
            layer = MockGimpLayer(i + 1, f"Layer {i + 1}", width, height)
            image.insert_layer(layer)
            
        return image
        
    @staticmethod
    def create_complex_image(width: int = 1024, height: int = 768, 
                           name: str = "Complex Image") -> MockGimpImage:
        """Create a complex test image with various layer types and properties."""
        image = MockGimpImage(1, name, width, height)
        
        # Background layer
        bg_layer = MockGimpLayer(1, "Background", width, height, opacity=100.0)
        image.insert_layer(bg_layer)
        
        # Text layer (simulated)
        text_layer = MockGimpLayer(2, "Text Layer", width // 2, height // 4, opacity=80.0)
        image.insert_layer(text_layer)
        
        # Transparent layer
        transparent_layer = MockGimpLayer(3, "Transparent Layer", width, height, opacity=50.0)
        image.insert_layer(transparent_layer)
        
        # Hidden layer
        hidden_layer = MockGimpLayer(4, "Hidden Layer", width, height, opacity=100.0)
        hidden_layer.set_visible(False)
        image.insert_layer(hidden_layer)
        
        return image


class TestDataProvider:
    """Provider for various test data scenarios."""
    
    @staticmethod
    def get_document_test_data() -> List[Dict[str, Any]]:
        """Get test data for document operations."""
        return [
            {
                "name": "Small Document",
                "width": 400,
                "height": 300,
                "mode": "RGB",
                "resolution": 72.0,
            },
            {
                "name": "Standard Document",
                "width": 800,
                "height": 600,
                "mode": "RGB",
                "resolution": 300.0,
            },
            {
                "name": "Large Document",
                "width": 2048,
                "height": 1536,
                "mode": "RGB",
                "resolution": 300.0,
            },
            {
                "name": "Grayscale Document",
                "width": 800,
                "height": 600,
                "mode": "GRAYSCALE",
                "resolution": 300.0,
            },
        ]
        
    @staticmethod
    def get_layer_test_data() -> List[Dict[str, Any]]:
        """Get test data for layer operations."""
        return [
            {
                "name": "Background Layer",
                "width": 800,
                "height": 600,
                "opacity": 100.0,
                "blend_mode": "normal",
                "visible": True,
            },
            {
                "name": "Semi-transparent Layer",
                "width": 800,
                "height": 600,
                "opacity": 50.0,
                "blend_mode": "normal",
                "visible": True,
            },
            {
                "name": "Multiply Layer",
                "width": 800,
                "height": 600,
                "opacity": 75.0,
                "blend_mode": "multiply",
                "visible": True,
            },
            {
                "name": "Hidden Layer",
                "width": 800,
                "height": 600,
                "opacity": 100.0,
                "blend_mode": "normal",
                "visible": False,
            },
        ]
        
    @staticmethod
    def get_drawing_test_data() -> List[Dict[str, Any]]:
        """Get test data for drawing operations."""
        return [
            {
                "operation": "rectangle",
                "x": 10,
                "y": 10,
                "width": 100,
                "height": 80,
                "fill_color": "#FF0000",
                "stroke_color": "#000000",
                "stroke_width": 2.0,
            },
            {
                "operation": "ellipse",
                "x": 50,
                "y": 50,
                "width": 120,
                "height": 100,
                "fill_color": "#00FF00",
                "stroke_color": "#0000FF",
                "stroke_width": 3.0,
            },
            {
                "operation": "brush_stroke",
                "points": [(10, 10), (50, 30), (100, 20), (150, 40)],
                "brush_size": 15.0,
                "brush_color": "#FF00FF",
            },
        ]
        
    @staticmethod
    def get_color_test_data() -> List[Dict[str, Any]]:
        """Get test data for color operations."""
        return [
            {"hex": "#FF0000", "rgb": (255, 0, 0), "rgba": (1.0, 0.0, 0.0, 1.0)},
            {"hex": "#00FF00", "rgb": (0, 255, 0), "rgba": (0.0, 1.0, 0.0, 1.0)},
            {"hex": "#0000FF", "rgb": (0, 0, 255), "rgba": (0.0, 0.0, 1.0, 1.0)},
            {"hex": "#FFFFFF", "rgb": (255, 255, 255), "rgba": (1.0, 1.0, 1.0, 1.0)},
            {"hex": "#000000", "rgb": (0, 0, 0), "rgba": (0.0, 0.0, 0.0, 1.0)},
            {"hex": "#808080", "rgb": (128, 128, 128), "rgba": (0.5, 0.5, 0.5, 1.0)},
        ]


class TestEnvironmentManager:
    """Manager for test environment setup and cleanup."""
    
    def __init__(self):
        self.temp_dirs = []
        self.temp_files = []
        self.mock_patches = []
        
    def create_temp_directory(self) -> str:
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir
        
    def create_temp_file(self, content: str = "", suffix: str = ".txt") -> str:
        """Create a temporary file for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name
        
    def add_mock_patch(self, target: str, new: Any = None):
        """Add a mock patch to be managed."""
        patcher = patch(target, new=new)
        mock = patcher.start()
        self.mock_patches.append(patcher)
        return mock
        
    def cleanup(self):
        """Clean up test environment."""
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        # Clean up temporary files
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
        # Stop mock patches
        for patcher in self.mock_patches:
            patcher.stop()
            
        # Clear lists
        self.temp_dirs.clear()
        self.temp_files.clear()
        self.mock_patches.clear()


class AsyncTestHelper:
    """Helper for async testing operations."""
    
    @staticmethod
    def create_async_mock(return_value: Any = None, side_effect: Any = None) -> AsyncMock:
        """Create an async mock with specified return value or side effect."""
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        return mock
        
    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 1.0, interval: float = 0.1) -> bool:
        """Wait for a condition to become true."""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            if condition_func():
                return True
            await asyncio.sleep(interval)
            
        return False
        
    @staticmethod
    @asynccontextmanager
    async def timeout_context(timeout: float = 5.0):
        """Context manager for async operations with timeout."""
        try:
            async with asyncio.timeout(timeout):
                yield
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")


class MCPTestHelper:
    """Helper for MCP protocol testing."""
    
    @staticmethod
    def create_test_server_config() -> Dict[str, Any]:
        """Create a test server configuration."""
        return {
            "host": "localhost",
            "port": 3001,  # Different port for testing
            "debug": True,
            "mode": "headless",
            "log_level": "DEBUG",
        }
        
    @staticmethod
    def create_test_tool_call(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a test tool call message."""
        return {
            "type": "tool_call",
            "tool_name": tool_name,
            "parameters": parameters,
            "id": f"test_{tool_name}_{id(parameters)}",
        }
        
    @staticmethod
    def create_test_resource_request(uri: str) -> Dict[str, Any]:
        """Create a test resource request."""
        return {
            "type": "resource_request",
            "uri": uri,
            "id": f"test_{uri.replace('://', '_')}",
        }
        
    @staticmethod
    def validate_mcp_message(message: Dict[str, Any]) -> bool:
        """Validate MCP message structure."""
        required_fields = ["type", "id"]
        return all(field in message for field in required_fields)
        
    @staticmethod
    def validate_tool_definition(tool_def: Dict[str, Any]) -> bool:
        """Validate tool definition structure."""
        required_fields = ["name", "description", "parameters"]
        return all(field in tool_def for field in required_fields)
        
    @staticmethod
    def validate_resource_definition(resource_def: Dict[str, Any]) -> bool:
        """Validate resource definition structure."""
        required_fields = ["uri", "name", "description"]
        return all(field in resource_def for field in required_fields)


class PerformanceTestHelper:
    """Helper for performance testing."""
    
    @staticmethod
    async def measure_execution_time(async_func, *args, **kwargs) -> Tuple[Any, float]:
        """Measure execution time of an async function."""
        start_time = asyncio.get_event_loop().time()
        result = await async_func(*args, **kwargs)
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        return result, execution_time
        
    @staticmethod
    def create_performance_benchmark(operation_name: str, max_duration: float = 1.0) -> Dict[str, Any]:
        """Create a performance benchmark definition."""
        return {
            "operation": operation_name,
            "max_duration": max_duration,
            "measurements": [],
            "passed": None,
        }
        
    @staticmethod
    def analyze_performance_results(benchmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance benchmark results."""
        total_benchmarks = len(benchmarks)
        passed_benchmarks = sum(1 for b in benchmarks if b.get("passed", False))
        
        return {
            "total_benchmarks": total_benchmarks,
            "passed_benchmarks": passed_benchmarks,
            "failed_benchmarks": total_benchmarks - passed_benchmarks,
            "pass_rate": passed_benchmarks / total_benchmarks if total_benchmarks > 0 else 0.0,
            "benchmarks": benchmarks,
        }


class ErrorTestHelper:
    """Helper for error testing scenarios."""
    
    @staticmethod
    def create_connection_error() -> Exception:
        """Create a connection error for testing."""
        return ConnectionError("Mock connection failed")
        
    @staticmethod
    def create_operation_error(operation: str) -> Exception:
        """Create an operation error for testing."""
        return RuntimeError(f"Mock {operation} operation failed")
        
    @staticmethod
    def create_validation_error(field: str, value: Any) -> Exception:
        """Create a validation error for testing."""
        return ValueError(f"Invalid {field}: {value}")
        
    @staticmethod
    def create_timeout_error(operation: str) -> Exception:
        """Create a timeout error for testing."""
        return TimeoutError(f"Mock {operation} operation timed out")
        
    @staticmethod
    async def simulate_intermittent_failure(success_rate: float = 0.5) -> bool:
        """Simulate intermittent failures for testing."""
        import random
        return random.random() < success_rate


# Export commonly used fixtures
__all__ = [
    'TestImageFactory',
    'TestDataProvider',
    'TestEnvironmentManager',
    'AsyncTestHelper',
    'MCPTestHelper',
    'PerformanceTestHelper',
    'ErrorTestHelper',
]