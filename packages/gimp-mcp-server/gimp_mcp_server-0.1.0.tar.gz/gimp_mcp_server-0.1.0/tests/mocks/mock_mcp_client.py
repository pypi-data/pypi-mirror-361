"""
Mock MCP client implementation for testing MCP protocol compliance.

This module provides a mock MCP client that can be used to test
the GIMP MCP server's protocol compliance and tool functionality.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from unittest.mock import Mock, AsyncMock


class MockMCPMessage:
    """Mock MCP message for testing."""
    
    def __init__(self, message_type: str, data: Dict[str, Any], message_id: Optional[str] = None):
        self.type = message_type
        self.data = data
        self.id = message_id or f"msg_{id(self)}"
        self.timestamp = asyncio.get_event_loop().time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "type": self.type,
            "data": self.data,
            "id": self.id,
            "timestamp": self.timestamp,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MockMCPMessage':
        """Create message from dictionary."""
        return cls(
            message_type=data["type"],
            data=data["data"],
            message_id=data.get("id")
        )


class MockMCPClient:
    """Mock MCP client for testing protocol compliance."""
    
    def __init__(self):
        self.connected = False
        self.server_info = None
        self.available_tools = {}
        self.available_resources = {}
        self.message_handlers = {}
        self.sent_messages = []
        self.received_messages = []
        
    async def connect(self, server_url: str) -> bool:
        """Connect to MCP server."""
        try:
            # Mock connection process
            self.connected = True
            
            # Mock server info exchange
            self.server_info = {
                "name": "GIMP MCP Server",
                "version": "0.1.0",
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "notifications": True,
                }
            }
            
            return True
            
        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Failed to connect to MCP server: {e}")
            
    async def disconnect(self):
        """Disconnect from MCP server."""
        self.connected = False
        self.server_info = None
        self.available_tools.clear()
        self.available_resources.clear()
        
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from server."""
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
            
        # Mock tool listing
        tools = [
            {
                "name": "get_document_info",
                "description": "Get detailed information about a document",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "integer", "description": "Document ID"}
                    },
                    "required": ["document_id"]
                }
            },
            {
                "name": "list_documents",
                "description": "List all open documents",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "create_document",
                "description": "Create a new document",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "width": {"type": "integer", "description": "Document width"},
                        "height": {"type": "integer", "description": "Document height"},
                        "name": {"type": "string", "description": "Document name"}
                    },
                    "required": ["width", "height"]
                }
            },
            {
                "name": "create_layer",
                "description": "Create a new layer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "integer", "description": "Document ID"},
                        "name": {"type": "string", "description": "Layer name"},
                        "layer_type": {"type": "string", "description": "Layer type"}
                    },
                    "required": ["document_id", "name"]
                }
            },
            {
                "name": "apply_brush_stroke",
                "description": "Apply a brush stroke to a layer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "integer", "description": "Document ID"},
                        "layer_id": {"type": "integer", "description": "Layer ID"},
                        "points": {"type": "array", "description": "Stroke points"},
                        "brush_size": {"type": "number", "description": "Brush size"}
                    },
                    "required": ["document_id", "layer_id", "points"]
                }
            }
        ]
        
        # Store available tools
        for tool in tools:
            self.available_tools[tool["name"]] = tool
            
        return tools
        
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from server."""
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
            
        # Mock resource listing
        resources = [
            {
                "uri": "document://current",
                "name": "Current Document",
                "description": "Information about the currently active document",
                "mimeType": "application/json"
            },
            {
                "uri": "document://list",
                "name": "Document List",
                "description": "List of all open documents",
                "mimeType": "application/json"
            },
            {
                "uri": "system://status",
                "name": "System Status",
                "description": "Current system status and health",
                "mimeType": "application/json"
            },
            {
                "uri": "system://capabilities",
                "name": "System Capabilities",
                "description": "Available system capabilities",
                "mimeType": "application/json"
            }
        ]
        
        # Store available resources
        for resource in resources:
            self.available_resources[resource["uri"]] = resource
            
        return resources
        
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server."""
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
            
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available")
            
        # Create mock message
        message = MockMCPMessage("tool_call", {
            "tool_name": tool_name,
            "parameters": parameters
        })
        
        self.sent_messages.append(message)
        
        # Mock tool responses based on tool name
        if tool_name == "list_documents":
            result = {
                "success": True,
                "documents": [
                    {
                        "id": 1,
                        "name": "Test Document",
                        "width": 800,
                        "height": 600,
                        "layers": 2
                    }
                ]
            }
        elif tool_name == "get_document_info":
            doc_id = parameters.get("document_id", 1)
            result = {
                "success": True,
                "document": {
                    "id": doc_id,
                    "name": "Test Document",
                    "width": 800,
                    "height": 600,
                    "mode": "RGB",
                    "layers": [
                        {
                            "id": 1,
                            "name": "Background",
                            "opacity": 100,
                            "visible": True
                        }
                    ]
                }
            }
        elif tool_name == "create_document":
            result = {
                "success": True,
                "document_id": 2,
                "width": parameters.get("width", 800),
                "height": parameters.get("height", 600),
                "name": parameters.get("name", "New Document")
            }
        elif tool_name == "create_layer":
            result = {
                "success": True,
                "layer_id": 3,
                "document_id": parameters.get("document_id", 1),
                "name": parameters.get("name", "New Layer")
            }
        elif tool_name == "apply_brush_stroke":
            result = {
                "success": True,
                "document_id": parameters.get("document_id", 1),
                "layer_id": parameters.get("layer_id", 1),
                "points_applied": len(parameters.get("points", []))
            }
        else:
            result = {
                "success": True,
                "message": f"Mock response for {tool_name}"
            }
            
        # Create response message
        response = MockMCPMessage("tool_response", result, message.id)
        self.received_messages.append(response)
        
        return result
        
    async def get_resource(self, uri: str) -> Dict[str, Any]:
        """Get a resource from the server."""
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
            
        if uri not in self.available_resources:
            raise ValueError(f"Resource '{uri}' not available")
            
        # Create mock message
        message = MockMCPMessage("resource_get", {"uri": uri})
        self.sent_messages.append(message)
        
        # Mock resource responses based on URI
        if uri == "document://current":
            result = {
                "success": True,
                "document": {
                    "id": 1,
                    "name": "Current Document",
                    "width": 800,
                    "height": 600,
                    "active": True
                }
            }
        elif uri == "document://list":
            result = {
                "success": True,
                "documents": [
                    {
                        "id": 1,
                        "name": "Test Document 1",
                        "width": 800,
                        "height": 600
                    },
                    {
                        "id": 2,
                        "name": "Test Document 2",
                        "width": 1024,
                        "height": 768
                    }
                ]
            }
        elif uri == "system://status":
            result = {
                "success": True,
                "status": {
                    "connected": True,
                    "mode": "headless",
                    "version": "0.1.0",
                    "uptime": 3600
                }
            }
        elif uri == "system://capabilities":
            result = {
                "success": True,
                "capabilities": {
                    "document_management": True,
                    "layer_operations": True,
                    "drawing_tools": True,
                    "selection_tools": True,
                    "color_management": True,
                    "filter_operations": True
                }
            }
        else:
            result = {
                "success": True,
                "message": f"Mock response for resource {uri}"
            }
            
        # Create response message
        response = MockMCPMessage("resource_response", result, message.id)
        self.received_messages.append(response)
        
        return result
        
    def add_message_handler(self, message_type: str, handler: Callable):
        """Add a message handler for specific message types."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        
    async def send_notification(self, notification_type: str, data: Dict[str, Any]):
        """Send a notification to the server."""
        if not self.connected:
            raise ConnectionError("Not connected to MCP server")
            
        message = MockMCPMessage("notification", {
            "type": notification_type,
            "data": data
        })
        
        self.sent_messages.append(message)
        
    def get_message_history(self) -> List[MockMCPMessage]:
        """Get complete message history."""
        return self.sent_messages + self.received_messages
        
    def clear_message_history(self):
        """Clear message history."""
        self.sent_messages.clear()
        self.received_messages.clear()
        
    def get_protocol_compliance_stats(self) -> Dict[str, Any]:
        """Get protocol compliance statistics."""
        return {
            "total_messages": len(self.sent_messages) + len(self.received_messages),
            "sent_messages": len(self.sent_messages),
            "received_messages": len(self.received_messages),
            "tools_available": len(self.available_tools),
            "resources_available": len(self.available_resources),
            "connection_status": "connected" if self.connected else "disconnected",
            "server_info": self.server_info,
        }


class MockMCPServer:
    """Mock MCP server for testing client interactions."""
    
    def __init__(self):
        self.running = False
        self.clients = []
        self.tools = {}
        self.resources = {}
        self.message_log = []
        
    async def start(self, host: str = "localhost", port: int = 3000):
        """Start the mock MCP server."""
        self.running = True
        
        # Register default tools and resources
        self._register_default_tools()
        self._register_default_resources()
        
    async def stop(self):
        """Stop the mock MCP server."""
        self.running = False
        self.clients.clear()
        
    def _register_default_tools(self):
        """Register default tools for testing."""
        self.tools = {
            "test_tool": {
                "name": "test_tool",
                "description": "Test tool for MCP protocol testing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"},
                        "param2": {"type": "integer"}
                    }
                }
            }
        }
        
    def _register_default_resources(self):
        """Register default resources for testing."""
        self.resources = {
            "test://resource": {
                "uri": "test://resource",
                "name": "Test Resource",
                "description": "Test resource for MCP protocol testing",
                "mimeType": "application/json"
            }
        }
        
    async def handle_client_connection(self, client: MockMCPClient):
        """Handle a client connection."""
        if client not in self.clients:
            self.clients.append(client)
            
    async def handle_client_disconnection(self, client: MockMCPClient):
        """Handle a client disconnection."""
        if client in self.clients:
            self.clients.remove(client)
            
    def log_message(self, message: MockMCPMessage):
        """Log a message for testing purposes."""
        self.message_log.append(message)
        
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            "running": self.running,
            "connected_clients": len(self.clients),
            "registered_tools": len(self.tools),
            "registered_resources": len(self.resources),
            "message_count": len(self.message_log),
        }


def create_mock_mcp_client() -> MockMCPClient:
    """Create a mock MCP client for testing."""
    return MockMCPClient()


def create_mock_mcp_server() -> MockMCPServer:
    """Create a mock MCP server for testing."""
    return MockMCPServer()