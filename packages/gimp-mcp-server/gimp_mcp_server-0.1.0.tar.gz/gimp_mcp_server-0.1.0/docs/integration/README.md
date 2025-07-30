# Integration Guide

Comprehensive guide for integrating the GIMP MCP Server with various MCP clients and applications.

## 📋 Table of Contents

- [MCP Protocol Overview](#mcp-protocol-overview)
- [Client Configuration](#client-configuration)
- [Popular MCP Clients](#popular-mcp-clients)
- [Custom Client Development](#custom-client-development)
- [Authentication & Security](#authentication--security)
- [API Integration Patterns](#api-integration-patterns)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)

## 🔌 MCP Protocol Overview

The Model Context Protocol (MCP) enables seamless communication between AI assistants and external tools. The GIMP MCP Server implements:

- **Tools**: Executable functions for GIMP operations
- **Resources**: Real-time data about GIMP state
- **Prompts**: Structured inputs for complex operations
- **Transport**: Standard MCP communication protocol

### Protocol Features

```typescript
interface MCPCapabilities {
  tools: {
    listChanged?: boolean;    // Dynamic tool discovery
  };
  resources: {
    subscribe?: boolean;      // Resource subscriptions
    listChanged?: boolean;    // Dynamic resource discovery
  };
  prompts: {
    listChanged?: boolean;    // Dynamic prompt discovery
  };
  experimental?: {
    [key: string]: unknown;
  };
}
```

## ⚙️ Client Configuration

### Standard MCP Configuration

Most MCP clients use a configuration file to define server connections:

```json
{
  "mcpServers": {
    "gimp": {
      "command": "gimp-mcp-server",
      "args": [],
      "env": {
        "GIMP_MCP_DEBUG": "false",
        "GIMP_MCP_MODE": "hybrid"
      }
    }
  }
}
```

### Advanced Configuration

```json
{
  "mcpServers": {
    "gimp": {
      "command": "gimp-mcp-server",
      "args": [
        "--port", "3000",
        "--host", "localhost",
        "--timeout", "300"
      ],
      "env": {
        "GIMP_MCP_DEBUG": "true",
        "GIMP_MCP_LOG_LEVEL": "INFO",
        "GIMP_MCP_MODE": "gui",
        "GIMP_CACHE_SIZE": "4096"
      },
      "cwd": "/path/to/working/directory"
    }
  }
}
```

## 🤖 Popular MCP Clients

### Claude Desktop

**Configuration Location**:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

**Basic Setup**:
```json
{
  "mcpServers": {
    "gimp": {
      "command": "gimp-mcp-server",
      "args": []
    }
  }
}
```

**Example Usage in Claude**:
```
Create a 1920x1080 document and add a red circle in the center
```

Claude will automatically:
1. Call `create_document` with the specified dimensions
2. Call `draw_ellipse` to create the red circle
3. Handle any necessary color and layer operations

### Continue.dev

**Configuration** (`.continue/config.json`):
```json
{
  "mcpServers": {
    "gimp": {
      "command": "gimp-mcp-server",
      "args": ["--port", "3000"]
    }
  },
  "contextProviders": [
    {
      "name": "gimp-state",
      "params": {
        "serverName": "gimp",
        "resourceUri": "document://current"
      }
    }
  ]
}
```

### Cline (Claude in VS Code)

**Configuration** (VS Code settings):
```json
{
  "cline.mcpServers": {
    "gimp": {
      "command": "gimp-mcp-server",
      "args": [],
      "description": "GIMP image editing capabilities"
    }
  }
}
```

### Custom Jupyter Notebook Integration

```python
# Install MCP client library
# pip install mcp-client

import asyncio
from mcp_client import MCPClient

class GimpMCPClient:
    def __init__(self):
        self.client = None
    
    async def connect(self):
        self.client = MCPClient()
        await self.client.connect_to_server(
            command="gimp-mcp-server",
            args=[]
        )
    
    async def create_document(self, width=1920, height=1080):
        return await self.client.call_tool(
            "create_document",
            {"width": width, "height": height}
        )
    
    async def get_document_state(self):
        return await self.client.get_resource("document://current")

# Usage
async def main():
    gimp = GimpMCPClient()
    await gimp.connect()
    
    # Create a document
    doc = await gimp.create_document(800, 600)
    print(f"Created document: {doc}")
    
    # Get current state
    state = await gimp.get_document_state()
    print(f"Document state: {state}")

# Run in Jupyter
await main()
```

## 🛠️ Custom Client Development

### JavaScript/TypeScript Client

```typescript
import { MCPClient } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

class GimpMCPWrapper {
  private client: MCPClient;
  private transport: StdioClientTransport;

  async initialize() {
    // Create transport for stdio communication
    this.transport = new StdioClientTransport({
      command: 'gimp-mcp-server',
      args: []
    });

    // Create and connect client
    this.client = new MCPClient({
      name: "gimp-client",
      version: "1.0.0"
    }, {
      capabilities: {}
    });

    await this.client.connect(this.transport);
  }

  async createDocument(options: {
    width?: number;
    height?: number;
    resolution?: number;
    color_mode?: string;
    fill_type?: string;
    name?: string;
  }) {
    return await this.client.request({
      method: "tools/call",
      params: {
        name: "create_document",
        arguments: options
      }
    });
  }

  async drawShape(type: 'rectangle' | 'ellipse', options: any) {
    const toolName = type === 'rectangle' ? 'draw_rectangle' : 'draw_ellipse';
    return await this.client.request({
      method: "tools/call",
      params: {
        name: toolName,
        arguments: options
      }
    });
  }

  async getCurrentDocument() {
    return await this.client.request({
      method: "resources/read",
      params: {
        uri: "document://current"
      }
    });
  }
}

// Usage example
async function example() {
  const gimp = new GimpMCPWrapper();
  await gimp.initialize();

  // Create a new document
  const doc = await gimp.createDocument({
    width: 800,
    height: 600,
    name: "My Project"
  });

  // Draw a red rectangle
  await gimp.drawShape('rectangle', {
    x: 100,
    y: 100,
    width: 200,
    height: 150,
    fill_color: "#FF0000"
  });

  // Get document state
  const state = await gimp.getCurrentDocument();
  console.log('Current document:', state);
}
```

### Python Client

```python
import asyncio
import subprocess
import json
from typing import Dict, Any, Optional

class GimpMCPClient:
    def __init__(self):
        self.process = None
        self.request_id = 0

    async def start_server(self):
        """Start the GIMP MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            'gimp-mcp-server',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Send initialization
        await self._send_request({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "python-gimp-client",
                    "version": "1.0.0"
                }
            }
        })

        response = await self._read_response()
        print(f"Server initialized: {response}")

    async def _send_request(self, request: Dict[str, Any]):
        """Send a JSON-RPC request to the server."""
        message = json.dumps(request) + '\n'
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()

    async def _read_response(self) -> Dict[str, Any]:
        """Read a JSON-RPC response from the server."""
        line = await self.process.stdout.readline()
        return json.loads(line.decode().strip())

    def _next_id(self) -> int:
        """Generate next request ID."""
        self.request_id += 1
        return self.request_id

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a GIMP MCP tool."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }

        await self._send_request(request)
        return await self._read_response()

    async def get_resource(self, uri: str) -> Dict[str, Any]:
        """Get a resource from the server."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "resources/read",
            "params": {
                "uri": uri
            }
        }

        await self._send_request(request)
        return await self._read_response()

    async def close(self):
        """Close the server connection."""
        if self.process:
            self.process.terminate()
            await self.process.wait()

# Example workflow
async def image_editing_workflow():
    client = GimpMCPClient()
    
    try:
        await client.start_server()
        
        # Create a new document
        doc_result = await client.call_tool("create_document", {
            "width": 1024,
            "height": 768,
            "name": "Workflow Example"
        })
        print(f"Created document: {doc_result}")

        # Add a layer
        layer_result = await client.call_tool("create_layer", {
            "name": "Graphics Layer",
            "layer_type": "RGB"
        })
        print(f"Created layer: {layer_result}")

        # Draw shapes
        await client.call_tool("draw_rectangle", {
            "x": 100,
            "y": 100,
            "width": 300,
            "height": 200,
            "fill_color": "#3498DB",
            "layer_id": layer_result["result"]["layer_id"]
        })

        await client.call_tool("draw_ellipse", {
            "center_x": 250,
            "center_y": 200,
            "radius_x": 80,
            "radius_y": 80,
            "fill_color": "#E74C3C",
            "layer_id": layer_result["result"]["layer_id"]
        })

        # Get document state
        doc_state = await client.get_resource("document://current")
        print(f"Final document state: {doc_state}")

        # Save the document
        save_result = await client.call_tool("save_document", {
            "file_path": "/tmp/workflow_example.xcf"
        })
        print(f"Saved document: {save_result}")

    finally:
        await client.close()

# Run the workflow
if __name__ == "__main__":
    asyncio.run(image_editing_workflow())
```

## 🔐 Authentication & Security

### Basic Security Considerations

```json
{
  "mcpServers": {
    "gimp": {
      "command": "gimp-mcp-server",
      "args": [
        "--bind-host", "127.0.0.1",  // Localhost only
        "--require-auth", "true",     // Enable authentication
        "--max-clients", "1"          // Limit concurrent clients
      ],
      "env": {
        "GIMP_MCP_API_KEY": "your-secret-key"
      }
    }
  }
}
```

### File System Restrictions

```json
{
  "mcpServers": {
    "gimp": {
      "command": "gimp-mcp-server",
      "args": [
        "--allowed-paths", "/home/user/images,/tmp/gimp-work",
        "--deny-system-paths", "true"
      ]
    }
  }
}
```

## 🚀 API Integration Patterns

### Batch Processing Pattern

```javascript
class BatchProcessor {
  constructor(gimpClient) {
    this.client = gimpClient;
    this.queue = [];
  }

  addOperation(tool, params) {
    this.queue.push({ tool, params });
  }

  async executeBatch() {
    const results = [];
    
    for (const operation of this.queue) {
      try {
        const result = await this.client.call_tool(
          operation.tool, 
          operation.params
        );
        results.push({ success: true, result });
      } catch (error) {
        results.push({ success: false, error: error.message });
      }
      
      // Add small delay to prevent overwhelming GIMP
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    this.queue = []; // Clear queue
    return results;
  }
}

// Usage
const batch = new BatchProcessor(gimpClient);
batch.addOperation("create_layer", { name: "Layer 1" });
batch.addOperation("create_layer", { name: "Layer 2" });
batch.addOperation("create_layer", { name: "Layer 3" });

const results = await batch.executeBatch();
```

### Resource Monitoring Pattern

```javascript
class DocumentMonitor {
  constructor(gimpClient) {
    this.client = gimpClient;
    this.callbacks = {};
    this.polling = false;
  }

  onDocumentChange(callback) {
    this.callbacks.documentChange = callback;
  }

  onLayerChange(callback) {
    this.callbacks.layerChange = callback;
  }

  async startMonitoring(interval = 1000) {
    this.polling = true;
    let lastState = null;

    while (this.polling) {
      try {
        const currentState = await this.client.get_resource("document://current");
        
        if (this.hasChanged(lastState, currentState)) {
          this.notifyCallbacks(lastState, currentState);
          lastState = currentState;
        }
      } catch (error) {
        console.error("Monitoring error:", error);
      }

      await new Promise(resolve => setTimeout(resolve, interval));
    }
  }

  stopMonitoring() {
    this.polling = false;
  }

  hasChanged(oldState, newState) {
    if (!oldState) return !!newState;
    return JSON.stringify(oldState) !== JSON.stringify(newState);
  }

  notifyCallbacks(oldState, newState) {
    if (this.callbacks.documentChange) {
      this.callbacks.documentChange(oldState, newState);
    }
  }
}
```

### Error Recovery Pattern

```javascript
class ResilientGimpClient {
  constructor(baseClient) {
    this.client = baseClient;
    this.retryAttempts = 3;
    this.retryDelay = 1000;
  }

  async callToolWithRetry(toolName, params, attempts = this.retryAttempts) {
    for (let i = 0; i < attempts; i++) {
      try {
        return await this.client.call_tool(toolName, params);
      } catch (error) {
        console.warn(`Attempt ${i + 1} failed:`, error.message);
        
        if (i < attempts - 1) {
          // Check if GIMP is still responsive
          try {
            await this.client.get_resource("system://health");
          } catch (healthError) {
            console.error("GIMP appears unresponsive, attempting recovery");
            await this.attemptRecovery();
          }
          
          await new Promise(resolve => 
            setTimeout(resolve, this.retryDelay * (i + 1))
          );
        } else {
          throw error; // Final attempt failed
        }
      }
    }
  }

  async attemptRecovery() {
    // Implementation depends on your setup
    // Could restart server, reset connection, etc.
    console.log("Attempting to recover GIMP connection...");
  }
}
```

## 🐛 Error Handling

### Standard Error Responses

```typescript
interface MCPError {
  code: number;
  message: string;
  data?: any;
}

// Common error codes
const ERROR_CODES = {
  GIMP_NOT_FOUND: -32001,
  DOCUMENT_NOT_FOUND: -32002,
  LAYER_NOT_FOUND: -32003,
  INVALID_PARAMETERS: -32602,
  INTERNAL_ERROR: -32603
};
```

### Client Error Handling

```javascript
async function safeToolCall(client, toolName, params) {
  try {
    const result = await client.call_tool(toolName, params);
    
    if (!result.success) {
      throw new Error(`Tool execution failed: ${result.error}`);
    }
    
    return result.data;
  } catch (error) {
    console.error(`Error calling ${toolName}:`, error);
    
    // Handle specific error types
    if (error.code === ERROR_CODES.GIMP_NOT_FOUND) {
      throw new Error("GIMP is not running or not accessible");
    } else if (error.code === ERROR_CODES.DOCUMENT_NOT_FOUND) {
      throw new Error("No active document found");
    } else {
      throw error; // Re-throw unknown errors
    }
  }
}
```

## ⚡ Performance Optimization

### Connection Pooling

```javascript
class GimpConnectionPool {
  constructor(maxConnections = 3) {
    this.pool = [];
    this.maxConnections = maxConnections;
    this.activeConnections = 0;
  }

  async getConnection() {
    if (this.pool.length > 0) {
      return this.pool.pop();
    }

    if (this.activeConnections < this.maxConnections) {
      this.activeConnections++;
      return await this.createConnection();
    }

    // Wait for a connection to become available
    return new Promise((resolve) => {
      const checkForConnection = () => {
        if (this.pool.length > 0) {
          resolve(this.pool.pop());
        } else {
          setTimeout(checkForConnection, 100);
        }
      };
      checkForConnection();
    });
  }

  releaseConnection(connection) {
    this.pool.push(connection);
  }

  async createConnection() {
    // Create new GIMP MCP client connection
    const client = new GimpMCPClient();
    await client.connect();
    return client;
  }
}
```

### Caching Strategy

```javascript
class CachedGimpClient {
  constructor(baseClient) {
    this.client = baseClient;
    this.cache = new Map();
    this.cacheTimeout = 5000; // 5 seconds
  }

  async getResourceCached(uri) {
    const cacheKey = uri;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const data = await this.client.get_resource(uri);
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now()
    });

    return data;
  }

  clearCache() {
    this.cache.clear();
  }
}
```

## 📚 See Also

- [API Reference](../api-reference/README.md) - Complete tool documentation
- [Tutorials](../tutorials/README.md) - Step-by-step examples
- [User Guide](../user-guide/README.md) - Installation and setup
- [Troubleshooting](../troubleshooting/README.md) - Common issues

## 🤝 Contributing

Help improve integration support:

1. **Test new clients** - Try the server with different MCP clients
2. **Create examples** - Share integration patterns and examples
3. **Report issues** - Help identify compatibility problems
4. **Improve documentation** - Add missing integration details

Submit contributions via [GitHub](https://github.com/gimp-mcp/gimp-mcp-server/pulls).