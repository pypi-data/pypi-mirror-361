"""
Integration tests for GIMP MCP Server.

This module contains comprehensive integration tests for the GIMP MCP server,
covering server startup/shutdown, tool registration, and MCP protocol compliance.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from gimp_mcp.server import GimpMCPServer, ServerConfig, create_server
from gimp_mcp.utils.errors import GimpError, GimpConnectionError


class TestServerStartupShutdown:
    """Test MCP server startup and shutdown procedures."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_creation_success(self, server_config, mock_gi_modules):
        """Test successful server creation."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                server = create_server(server_config)
                
                assert server is not None
                assert server.config == server_config
                assert server.is_running is False
                
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_creation_with_default_config(self, mock_gi_modules):
        """Test server creation with default configuration."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                server = create_server()
                
                assert server is not None
                assert server.config.host == "localhost"
                assert server.config.port == 3000
                
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_initialization_components(self, server_config, mock_gi_modules):
        """Test server component initialization."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager') as mock_mode_manager:
                with patch('gimp_mcp.gimp_api.GimpAPI') as mock_gimp_api:
                    server = GimpMCPServer(server_config)
                    
                    # Verify components were initialized
                    mock_mode_manager.assert_called_once()
                    mock_gimp_api.assert_called_once()
                    assert server.app is not None
                    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_startup_event_handlers(self, mock_gimp_server):
        """Test server startup event handlers."""
        # Mock FastMCP app startup
        startup_handlers = []
        
        def mock_on_startup(handler):
            startup_handlers.append(handler)
            return handler
            
        mock_gimp_server.app.on_startup = mock_on_startup
        
        # Reinitialize to register handlers
        mock_gimp_server._setup_event_handlers()
        
        # Verify startup handler was registered
        assert len(startup_handlers) == 1
        
        # Execute startup handler
        await startup_handlers[0]()
        
        # Verify startup actions
        mock_gimp_server._check_gimp_connection.assert_called_once()
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_shutdown_event_handlers(self, mock_gimp_server):
        """Test server shutdown event handlers."""
        # Mock FastMCP app shutdown
        shutdown_handlers = []
        
        def mock_on_shutdown(handler):
            shutdown_handlers.append(handler)
            return handler
            
        mock_gimp_server.app.on_shutdown = mock_on_shutdown
        
        # Reinitialize to register handlers
        mock_gimp_server._setup_event_handlers()
        
        # Verify shutdown handler was registered
        assert len(shutdown_handlers) == 1
        
        # Execute shutdown handler
        await shutdown_handlers[0]()
        
        # Verify cleanup was called
        mock_gimp_server.gimp_api.cleanup.assert_called_once()
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_connection_check_success(self, mock_gimp_server):
        """Test successful GIMP connection check during startup."""
        mock_gimp_server.gimp_api.test_connection = AsyncMock(return_value={
            "success": True,
            "mode": "headless"
        })
        
        # Should not raise exception
        await mock_gimp_server._check_gimp_connection()
        
        mock_gimp_server.gimp_api.test_connection.assert_called_once()
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_connection_check_failure(self, mock_gimp_server):
        """Test GIMP connection check failure during startup."""
        mock_gimp_server.gimp_api.test_connection = AsyncMock(return_value={
            "success": False,
            "error": "Connection failed"
        })
        
        with pytest.raises(GimpConnectionError, match="GIMP connection test failed"):
            await mock_gimp_server._check_gimp_connection()


class TestToolRegistration:
    """Test MCP tool registration and discovery."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tool_registration_success(self, server_config, mock_gi_modules):
        """Test successful tool registration."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI'):
                    server = GimpMCPServer(server_config)
                    
                    # Verify tools were registered with FastMCP app
                    assert server.app.add_tool.call_count > 0
                    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_document_tools_registration(self, server_config, mock_gi_modules):
        """Test document tools registration."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI'):
                    server = GimpMCPServer(server_config)
                    
                    # Check that document tools were registered
                    tool_calls = [call.args[0] for call in server.app.add_tool.call_args_list]
                    tool_names = [getattr(tool, '__name__', str(tool)) for tool in tool_calls]
                    
                    expected_tools = [
                        'get_document_info', 'list_documents', 'create_document',
                        'open_document', 'save_document', 'export_document', 'close_document'
                    ]
                    
                    # Verify at least some expected tools are registered
                    for expected_tool in expected_tools[:3]:  # Check first few
                        assert any(expected_tool in name for name in tool_names)
                        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_layer_tools_registration(self, server_config, mock_gi_modules):
        """Test layer tools registration."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI'):
                    server = GimpMCPServer(server_config)
                    
                    # Check that layer tools were registered
                    tool_calls = [call.args[0] for call in server.app.add_tool.call_args_list]
                    tool_names = [getattr(tool, '__name__', str(tool)) for tool in tool_calls]
                    
                    expected_tools = [
                        'get_layer_info', 'create_layer', 'set_layer_opacity',
                        'set_layer_blend_mode', 'set_layer_visibility'
                    ]
                    
                    # Verify at least some expected tools are registered
                    for expected_tool in expected_tools[:2]:  # Check first few
                        assert any(expected_tool in name for name in tool_names)
                        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_drawing_tools_registration(self, server_config, mock_gi_modules):
        """Test drawing tools registration."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI'):
                    server = GimpMCPServer(server_config)
                    
                    # Check that drawing tools were registered
                    tool_calls = [call.args[0] for call in server.app.add_tool.call_args_list]
                    tool_names = [getattr(tool, '__name__', str(tool)) for tool in tool_calls]
                    
                    expected_tools = [
                        'apply_brush_stroke', 'draw_rectangle', 'draw_ellipse', 'bucket_fill'
                    ]
                    
                    # Verify at least some expected tools are registered
                    for expected_tool in expected_tools[:2]:  # Check first few
                        assert any(expected_tool in name for name in tool_names)


class TestResourceRegistration:
    """Test MCP resource registration and discovery."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_resource_registration_success(self, server_config, mock_gi_modules):
        """Test successful resource registration."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI'):
                    server = GimpMCPServer(server_config)
                    
                    # Verify resources were registered with FastMCP app
                    assert server.app.add_resource.call_count > 0
                    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_system_resources_registration(self, server_config, mock_gi_modules):
        """Test system resources registration."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI'):
                    server = GimpMCPServer(server_config)
                    
                    # Check that system resources were registered
                    resource_calls = [call.args[0] for call in server.app.add_resource.call_args_list]
                    resource_names = [getattr(resource, '__name__', str(resource)) for resource in resource_calls]
                    
                    expected_resources = [
                        'get_system_status', 'get_system_capabilities', 'get_system_health'
                    ]
                    
                    # Verify at least some expected resources are registered
                    for expected_resource in expected_resources:
                        assert any(expected_resource in name for name in resource_names)
                        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_document_resources_registration(self, server_config, mock_gi_modules):
        """Test document resources registration."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI'):
                    server = GimpMCPServer(server_config)
                    
                    # Check that document resources were registered
                    resource_calls = [call.args[0] for call in server.app.add_resource.call_args_list]
                    resource_names = [getattr(resource, '__name__', str(resource)) for resource in resource_calls]
                    
                    expected_resources = [
                        'get_current_document', 'get_document_list', 'get_document_metadata'
                    ]
                    
                    # Verify at least some expected resources are registered
                    for expected_resource in expected_resources:
                        assert any(expected_resource in name for name in resource_names)


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_mcp_client_connection(self, mock_mcp_client):
        """Test MCP client connection to server."""
        # Test connection
        connected = await mock_mcp_client.connect("localhost:3001")
        
        assert connected is True
        assert mock_mcp_client.connected is True
        assert mock_mcp_client.server_info is not None
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_mcp_tool_discovery(self, mock_mcp_client):
        """Test MCP tool discovery via client."""
        await mock_mcp_client.connect("localhost:3001")
        
        tools = await mock_mcp_client.list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Verify tool structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_mcp_resource_discovery(self, mock_mcp_client):
        """Test MCP resource discovery via client."""
        await mock_mcp_client.connect("localhost:3001")
        
        resources = await mock_mcp_client.list_resources()
        
        assert isinstance(resources, list)
        assert len(resources) > 0
        
        # Verify resource structure
        for resource in resources:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_mcp_tool_invocation(self, mock_mcp_client):
        """Test MCP tool invocation via client."""
        await mock_mcp_client.connect("localhost:3001")
        
        # Test calling a tool
        result = await mock_mcp_client.call_tool("list_documents", {})
        
        assert isinstance(result, dict)
        assert "success" in result
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_mcp_resource_access(self, mock_mcp_client):
        """Test MCP resource access via client."""
        await mock_mcp_client.connect("localhost:3001")
        
        # Test accessing a resource
        result = await mock_mcp_client.get_resource("system://status")
        
        assert isinstance(result, dict)
        assert "success" in result
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_mcp_message_format_compliance(self, mock_mcp_client, mcp_test_helper):
        """Test MCP message format compliance."""
        await mock_mcp_client.connect("localhost:3001")
        
        # Call a tool and check message format
        await mock_mcp_client.call_tool("list_documents", {})
        
        messages = mock_mcp_client.get_message_history()
        
        # Verify message format compliance
        for message in messages:
            assert mcp_test_helper.validate_mcp_message(message.to_dict())
            
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_mcp_tool_parameter_validation(self, mock_mcp_client):
        """Test MCP tool parameter validation."""
        await mock_mcp_client.connect("localhost:3001")
        
        # Test tool with valid parameters
        result = await mock_mcp_client.call_tool("get_document_info", {
            "document_id": 1
        })
        assert result["success"] is True
        
        # Test tool with invalid parameters (should handle gracefully)
        result = await mock_mcp_client.call_tool("get_document_info", {
            "document_id": -1
        })
        assert result["success"] is False
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.mcp
    async def test_mcp_error_handling(self, mock_mcp_client):
        """Test MCP error handling compliance."""
        await mock_mcp_client.connect("localhost:3001")
        
        # Test calling non-existent tool
        try:
            await mock_mcp_client.call_tool("non_existent_tool", {})
        except Exception as e:
            # Should handle gracefully, not crash
            assert "not available" in str(e).lower()
            
        # Test accessing non-existent resource
        try:
            await mock_mcp_client.get_resource("invalid://resource")
        except Exception as e:
            # Should handle gracefully, not crash
            assert "not available" in str(e).lower()


class TestServerErrorHandling:
    """Test server error handling during integration scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_startup_with_gimp_connection_failure(self, server_config, mock_gi_modules):
        """Test server startup when GIMP connection fails."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI') as mock_api:
                    # Configure API to fail connection
                    mock_api.return_value.test_connection = AsyncMock(return_value={
                        "success": False,
                        "error": "GIMP not running"
                    })
                    
                    server = GimpMCPServer(server_config)
                    
                    # Server should still be created, but connection check will warn
                    assert server is not None
                    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_tool_registration_failure(self, server_config, mock_gi_modules):
        """Test server behavior when tool registration fails."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI'):
                    with patch('gimp_mcp.tools.document_tools.DocumentTools', side_effect=Exception("Tool init failed")):
                        with pytest.raises(GimpError, match="Tool registration failed"):
                            GimpMCPServer(server_config)
                            
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_resource_registration_failure(self, server_config, mock_gi_modules):
        """Test server behavior when resource registration fails."""
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                with patch('gimp_mcp.gimp_api.GimpAPI'):
                    with patch('gimp_mcp.resources.providers.ResourceProviders', side_effect=Exception("Resource init failed")):
                        with pytest.raises(GimpError, match="Resource registration failed"):
                            GimpMCPServer(server_config)


class TestServerConfigurationVariations:
    """Test server with different configuration variations."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_headless_mode_configuration(self, mock_gi_modules):
        """Test server configuration in headless mode."""
        config = ServerConfig(mode="headless", debug=True)
        
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager') as mock_mode_manager:
                mock_mode_manager.return_value.gui_mode = False
                
                server = create_server(config)
                
                assert server.config.mode == "headless"
                
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_gui_mode_configuration(self, mock_gi_modules):
        """Test server configuration in GUI mode."""
        config = ServerConfig(mode="gui", debug=True)
        
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager') as mock_mode_manager:
                mock_mode_manager.return_value.gui_mode = True
                
                server = create_server(config)
                
                assert server.config.mode == "gui"
                
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_auto_mode_configuration(self, mock_gi_modules):
        """Test server configuration with auto mode detection."""
        config = ServerConfig(mode=None)  # Auto-detect
        
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                server = create_server(config)
                
                assert server.config.mode is None
                
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_debug_configuration(self, mock_gi_modules):
        """Test server configuration with debug enabled."""
        config = ServerConfig(debug=True, log_level="DEBUG")
        
        with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
            with patch('gimp_mcp.mode_manager.GimpModeManager'):
                server = create_server(config)
                
                assert server.config.debug is True
                assert server.config.log_level == "DEBUG"


class TestServerRuntimeBehavior:
    """Test server runtime behavior and lifecycle."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_server_run_lifecycle(self, mock_gimp_server):
        """Test complete server run lifecycle."""
        # Mock FastMCP app run
        mock_gimp_server.app.run = AsyncMock()
        
        # Test server run
        await mock_gimp_server.run()
        
        # Verify FastMCP app was started
        mock_gimp_server.app.run.assert_called_once_with(
            host=mock_gimp_server.config.host,
            port=mock_gimp_server.config.port
        )
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_server_graceful_shutdown(self, mock_gimp_server):
        """Test server graceful shutdown."""
        # Simulate running state
        mock_gimp_server.is_running = True
        
        # Mock shutdown process
        shutdown_handlers = []
        
        def mock_on_shutdown(handler):
            shutdown_handlers.append(handler)
            
        mock_gimp_server.app.on_shutdown = mock_on_shutdown
        mock_gimp_server._setup_event_handlers()
        
        # Execute shutdown
        for handler in shutdown_handlers:
            await handler()
            
        # Verify cleanup was performed
        mock_gimp_server.gimp_api.cleanup.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_server_integration_scenario(server_config, mock_gi_modules, mock_mcp_client):
    """Test complete server integration scenario."""
    with patch('gimp_mcp.gimp_api.safe_gi_import', return_value=mock_gi_modules):
        with patch('gimp_mcp.mode_manager.GimpModeManager'):
            with patch('gimp_mcp.gimp_api.GimpAPI'):
                # Create and configure server
                server = create_server(server_config)
                assert server is not None
                
                # Simulate client connection
                await mock_mcp_client.connect("localhost:3001")
                assert mock_mcp_client.connected is True
                
                # Test tool discovery
                tools = await mock_mcp_client.list_tools()
                assert len(tools) > 0
                
                # Test resource discovery
                resources = await mock_mcp_client.list_resources()
                assert len(resources) > 0
                
                # Test tool invocation
                result = await mock_mcp_client.call_tool("list_documents", {})
                assert result["success"] is True
                
                # Test resource access
                result = await mock_mcp_client.get_resource("system://status")
                assert result["success"] is True
                
                # Test cleanup
                await mock_mcp_client.disconnect()
                assert mock_mcp_client.connected is False