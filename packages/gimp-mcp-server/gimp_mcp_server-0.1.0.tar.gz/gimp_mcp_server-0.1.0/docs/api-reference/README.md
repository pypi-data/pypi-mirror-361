# API Reference

Complete reference documentation for all GIMP MCP Server tools and resources.

## 📋 Table of Contents

### MCP Tools
- [Document Tools](tools/document-tools.md) - Document management operations
- [Layer Tools](tools/layer-tools.md) - Layer operations and management
- [Drawing Tools](tools/drawing-tools.md) - Drawing and painting operations
- [Selection Tools](tools/selection-tools.md) - Selection management
- [Color Tools](tools/color-tools.md) - Color and palette management
- [Filter Tools](tools/filter-tools.md) - Image filter operations

### MCP Resources
- [Document Resources](resources/document-resources.md) - Real-time document state
- [System Resources](resources/system-resources.md) - System status and capabilities
- [Palette Resources](resources/palette-resources.md) - Color palettes and brushes
- [Tool Resources](resources/tool-resources.md) - Current tool state

### Reference Materials
- [Data Types](reference/data-types.md) - Common data structures
- [Error Handling](reference/error-handling.md) - Error codes and handling
- [Parameter Validation](reference/parameter-validation.md) - Input validation rules
- [Return Values](reference/return-values.md) - Standard return formats

## 🎯 API Overview

The GIMP MCP Server provides a comprehensive set of tools and resources for AI-powered image editing. The API is organized into logical categories:

### Tool Categories

| Category | Description | Tool Count |
|----------|-------------|------------|
| **Document** | Create, open, save, and export documents | 6 |
| **Layer** | Layer management and manipulation | 8 |
| **Drawing** | Drawing and painting operations | 4 |
| **Selection** | Selection creation and modification | 4 |
| **Color** | Color and palette management | 4 |
| **Filter** | Image filters and effects | 3 |

### Resource Categories

| Category | Description | Resource Count |
|----------|-------------|----------------|
| **Document** | Real-time document state | 3 |
| **System** | Server status and capabilities | 3 |
| **Palette** | Color palettes and brushes | 2 |
| **Tool** | Current tool state | 1 |

## 🔧 Common Patterns

### Tool Parameters

Most tools follow consistent parameter patterns:

```typescript
interface CommonParameters {
  document_id?: number;      // Optional document ID (uses active if not provided)
  layer_id?: number;         // Optional layer ID (uses active if not provided)
}
```

### Return Values

All tools return standardized response objects:

```typescript
interface ToolResponse {
  success: boolean;          // Operation success status
  message?: string;          // Human-readable message
  data?: any;               // Operation-specific data
  error?: string;           // Error message if success is false
  operation: string;        // Name of the operation performed
  timestamp: number;        // Unix timestamp of operation
}
```

### Error Handling

All tools include comprehensive error handling:

- **Parameter validation** before execution
- **Connection verification** to ensure GIMP is available
- **Operation-specific error handling** for GIMP API calls
- **Graceful degradation** when operations partially fail

## 🚀 Quick Start Examples

### Creating a Document

```javascript
// Create a new document
const result = await mcp.callTool("create_document", {
  width: 1920,
  height: 1080,
  resolution: 300,
  color_mode: "RGB",
  fill_type: "white"
});
```

### Working with Layers

```javascript
// Create a new layer
const layer = await mcp.callTool("create_layer", {
  name: "My Layer",
  layer_type: "RGB",
  opacity: 100.0,
  blend_mode: "normal"
});

// Set layer properties
await mcp.callTool("set_layer_opacity", {
  layer_id: layer.data.layer_id,
  opacity: 75.0
});
```

### Drawing Operations

```javascript
// Apply a brush stroke
await mcp.callTool("apply_brush_stroke", {
  points: [[100, 100], [200, 150], [300, 200]],
  brush_name: "2. Hardness 050",
  size: 20.0,
  opacity: 100.0,
  color: "#FF0000"
});

// Draw a rectangle
await mcp.callTool("draw_rectangle", {
  x: 50,
  y: 50,
  width: 200,
  height: 100,
  fill_color: "#00FF00",
  stroke_color: "#000000",
  stroke_width: 2.0
});
```

### Using Resources

```javascript
// Get current document state
const docState = await mcp.getResource("document://current");

// Get system capabilities
const capabilities = await mcp.getResource("system://capabilities");

// Get active color palette
const palette = await mcp.getResource("palettes://active");
```

## 📊 Tool Usage Statistics

Based on common workflows, here are the most frequently used tools:

1. **create_document** - Starting new projects
2. **create_layer** - Layer-based editing
3. **apply_brush_stroke** - Drawing operations
4. **set_layer_opacity** - Layer adjustments
5. **save_document** - Saving work
6. **draw_rectangle** - Shape creation
7. **set_foreground_color** - Color management
8. **create_rectangular_selection** - Selection operations

## 🔄 API Versioning

The GIMP MCP Server follows semantic versioning:

- **Major version** (1.x.x) - Breaking API changes
- **Minor version** (x.1.x) - New features, backward compatible
- **Patch version** (x.x.1) - Bug fixes, backward compatible

Current API version: **1.0.0**

## 🛠️ Development Integration

### Type Definitions

TypeScript definitions are available for all tools and resources:

```bash
npm install @gimp-mcp/types
```

### SDK Libraries

Official SDKs are available for:
- **JavaScript/TypeScript**: `@gimp-mcp/sdk-js`
- **Python**: `gimp-mcp-sdk`
- **Go**: `github.com/gimp-mcp/sdk-go`

### Testing

Use the test utilities to verify API behavior:

```bash
# Test all tools
gimp-mcp-server --test-tools

# Test specific tool
gimp-mcp-server --test-tool create_document

# Test resources
gimp-mcp-server --test-resources
```

## 📚 Further Reading

- [Architecture Guide](../architecture/README.md) - Technical deep-dive
- [Extension Guide](../extension/README.md) - Adding new tools
- [Performance Guide](../performance/README.md) - Optimization tips
- [Troubleshooting](../troubleshooting/README.md) - Common issues

## 🤝 Contributing

See the [Development Guide](../development/README.md) for information on:
- Adding new tools
- Extending existing functionality
- Testing and validation
- Contribution guidelines