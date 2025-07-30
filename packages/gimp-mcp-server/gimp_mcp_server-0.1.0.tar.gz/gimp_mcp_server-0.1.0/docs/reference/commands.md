# Command Reference

Quick reference for all GIMP MCP Server tools and their parameters.

## 📋 Quick Navigation

- [Document Tools](#document-tools)
- [Layer Tools](#layer-tools)
- [Drawing Tools](#drawing-tools)
- [Selection Tools](#selection-tools)
- [Color Tools](#color-tools)
- [Filter Tools](#filter-tools)
- [Resource URIs](#resource-uris)

## 📄 Document Tools

### get_document_info
Get detailed information about a document.
```javascript
await mcp.callTool("get_document_info", {
  document_id?: number  // Optional: specific document ID
});
```

### list_documents
List all open documents.
```javascript
await mcp.callTool("list_documents");
```

### create_document
Create a new document.
```javascript
await mcp.callTool("create_document", {
  width?: number,           // Default: 1920
  height?: number,          // Default: 1080
  resolution?: number,      // Default: 300
  color_mode?: string,      // "RGB", "GRAYSCALE", "INDEXED". Default: "RGB"
  precision?: string,       // "8-bit", "16-bit", "32-bit". Default: "8-bit"
  fill_type?: string,       // "transparent", "white", "black", "foreground", "background"
  name?: string            // Default: "Untitled"
});
```

### open_document
Open an existing document from file.
```javascript
await mcp.callTool("open_document", {
  file_path: string        // Required: path to document file
});
```

### save_document
Save a document to file.
```javascript
await mcp.callTool("save_document", {
  document_id?: number,    // Optional: specific document
  file_path?: string,      // Optional: save path
  overwrite?: boolean      // Default: false
});
```

### export_document
Export document to various formats.
```javascript
await mcp.callTool("export_document", {
  document_id?: number,    // Optional: specific document
  file_path: string,       // Required: export path
  format?: string,         // Optional: format override
  options?: {
    quality?: number,      // JPEG quality (1-100)
    compression?: number,  // PNG compression (0-9)
    progressive?: boolean, // Progressive JPEG
    optimize?: boolean,    // Optimize file size
    metadata?: boolean,    // Include metadata
    color_profile?: boolean // Include color profile
  }
});
```

## 🗂️ Layer Tools

### get_layer_info
Get detailed information about a layer.
```javascript
await mcp.callTool("get_layer_info", {
  layer_id: number,        // Required: layer ID
  document_id?: number     // Optional: specific document
});
```

### create_layer
Create a new layer.
```javascript
await mcp.callTool("create_layer", {
  document_id?: number,    // Optional: specific document
  name?: string,           // Default: "New Layer"
  layer_type?: string,     // "RGB", "RGBA", "GRAYSCALE", etc. Default: "RGB"
  opacity?: number,        // 0-100. Default: 100
  blend_mode?: string      // Default: "normal"
});
```

### set_layer_opacity
Set layer opacity.
```javascript
await mcp.callTool("set_layer_opacity", {
  layer_id: number,        // Required: layer ID
  opacity: number,         // Required: 0-100
  document_id?: number     // Optional: specific document
});
```

### set_layer_blend_mode
Set layer blend mode.
```javascript
await mcp.callTool("set_layer_blend_mode", {
  layer_id: number,        // Required: layer ID
  blend_mode: string,      // Required: blend mode name
  document_id?: number     // Optional: specific document
});
```

**Common Blend Modes**: `normal`, `multiply`, `screen`, `overlay`, `soft-light`, `hard-light`, `color-dodge`, `color-burn`, `darken`, `lighten`, `difference`, `exclusion`

### set_layer_visibility
Toggle layer visibility.
```javascript
await mcp.callTool("set_layer_visibility", {
  layer_id: number,        // Required: layer ID
  visible: boolean,        // Required: visibility state
  document_id?: number     // Optional: specific document
});
```

### duplicate_layer
Duplicate an existing layer.
```javascript
await mcp.callTool("duplicate_layer", {
  layer_id: number,        // Required: source layer ID
  new_name?: string,       // Optional: name for duplicate
  document_id?: number     // Optional: specific document
});
```

### delete_layer
Delete a layer.
```javascript
await mcp.callTool("delete_layer", {
  layer_id: number,        // Required: layer ID to delete
  document_id?: number     // Optional: specific document
});
```

### move_layer
Move a layer in the layer stack.
```javascript
await mcp.callTool("move_layer", {
  layer_id: number,        // Required: layer ID to move
  new_parent_id?: number,  // Optional: new parent layer
  new_position?: number,   // Optional: position in stack
  document_id?: number     // Optional: specific document
});
```

## 🎨 Drawing Tools

### apply_brush_stroke
Apply a brush stroke to a layer.
```javascript
await mcp.callTool("apply_brush_stroke", {
  points: Array<[number, number]>, // Required: stroke path coordinates
  brush_name?: string,             // Default: "2. Hardness 050"
  size?: number,                   // Default: 10.0
  opacity?: number,                // Default: 100.0
  color?: string,                  // Optional: hex color
  layer_id?: number,               // Optional: target layer
  document_id?: number             // Optional: specific document
});
```

**Common Brushes**: `"2. Hardness 050"`, `"2. Hardness 075"`, `"2. Hardness 100"`, `"Airbrush Soft"`, `"Pencil"`

### draw_rectangle
Draw a rectangle shape.
```javascript
await mcp.callTool("draw_rectangle", {
  x: number,               // Required: top-left X coordinate
  y: number,               // Required: top-left Y coordinate
  width: number,           // Required: rectangle width
  height: number,          // Required: rectangle height
  fill_color?: string,     // Optional: fill color (hex)
  stroke_color?: string,   // Optional: stroke color (hex)
  stroke_width?: number,   // Default: 1.0
  layer_id?: number,       // Optional: target layer
  document_id?: number     // Optional: specific document
});
```

### draw_ellipse
Draw an ellipse shape.
```javascript
await mcp.callTool("draw_ellipse", {
  center_x: number,        // Required: center X coordinate
  center_y: number,        // Required: center Y coordinate
  radius_x: number,        // Required: horizontal radius
  radius_y: number,        // Required: vertical radius
  fill_color?: string,     // Optional: fill color (hex)
  stroke_color?: string,   // Optional: stroke color (hex)
  stroke_width?: number,   // Default: 1.0
  layer_id?: number,       // Optional: target layer
  document_id?: number     // Optional: specific document
});
```

### bucket_fill
Fill an area with color.
```javascript
await mcp.callTool("bucket_fill", {
  x: number,               // Required: click X coordinate
  y: number,               // Required: click Y coordinate
  color: string,           // Required: fill color (hex)
  threshold?: number,      // Default: 10.0 (0-100)
  sample_merged?: boolean, // Default: false
  layer_id?: number,       // Optional: target layer
  document_id?: number     // Optional: specific document
});
```

## 🔲 Selection Tools

### create_rectangular_selection
Create a rectangular selection.
```javascript
await mcp.callTool("create_rectangular_selection", {
  x: number,               // Required: top-left X coordinate
  y: number,               // Required: top-left Y coordinate
  width: number,           // Required: selection width
  height: number,          // Required: selection height
  operation?: string,      // "replace", "add", "subtract", "intersect". Default: "replace"
  feather?: number,        // Default: 0.0
  document_id?: number     // Optional: specific document
});
```

### create_elliptical_selection
Create an elliptical selection.
```javascript
await mcp.callTool("create_elliptical_selection", {
  center_x: number,        // Required: center X coordinate
  center_y: number,        // Required: center Y coordinate
  radius_x: number,        // Required: horizontal radius
  radius_y: number,        // Required: vertical radius
  operation?: string,      // "replace", "add", "subtract", "intersect". Default: "replace"
  feather?: number,        // Default: 0.0
  document_id?: number     // Optional: specific document
});
```

### modify_selection
Modify existing selection.
```javascript
await mcp.callTool("modify_selection", {
  operation: string,       // Required: "grow", "shrink", "border", "feather"
  value: number,           // Required: operation amount
  document_id?: number     // Optional: specific document
});
```

### clear_selection
Clear the current selection.
```javascript
await mcp.callTool("clear_selection", {
  document_id?: number     // Optional: specific document
});
```

## 🎨 Color Tools

### set_foreground_color
Set the foreground color.
```javascript
await mcp.callTool("set_foreground_color", {
  color: string            // Required: hex color (e.g., "#FF0000")
});
```

### set_background_color
Set the background color.
```javascript
await mcp.callTool("set_background_color", {
  color: string            // Required: hex color (e.g., "#FFFFFF")
});
```

### sample_color
Sample color from image.
```javascript
await mcp.callTool("sample_color", {
  x: number,               // Required: sample X coordinate
  y: number,               // Required: sample Y coordinate
  sample_merged?: boolean, // Default: false
  layer_id?: number,       // Optional: specific layer
  document_id?: number     // Optional: specific document
});
```

### get_active_palette
Get the currently active color palette.
```javascript
await mcp.callTool("get_active_palette");
```

## 🎭 Filter Tools

### apply_blur
Apply blur filter to layer.
```javascript
await mcp.callTool("apply_blur", {
  radius: number,          // Required: blur radius
  method?: string,         // "gaussian", "motion", "radial". Default: "gaussian"
  layer_id?: number,       // Optional: target layer
  document_id?: number     // Optional: specific document
});
```

### apply_sharpen
Apply sharpen filter to layer.
```javascript
await mcp.callTool("apply_sharpen", {
  amount: number,          // Required: sharpen amount (0-100)
  threshold?: number,      // Default: 0.0
  layer_id?: number,       // Optional: target layer
  document_id?: number     // Optional: specific document
});
```

### adjust_brightness_contrast
Adjust brightness and contrast.
```javascript
await mcp.callTool("adjust_brightness_contrast", {
  brightness?: number,     // -100 to 100. Default: 0
  contrast?: number,       // -100 to 100. Default: 0
  layer_id?: number,       // Optional: target layer
  document_id?: number     // Optional: specific document
});
```

## 📡 Resource URIs

### Document Resources
```javascript
// Current active document state
await mcp.getResource("document://current");

// List of all open documents
await mcp.getResource("document://list");

// Metadata about current document
await mcp.getResource("document://metadata");
```

### System Resources
```javascript
// System and server status
await mcp.getResource("system://status");

// Server capabilities and features
await mcp.getResource("system://capabilities");

// System health information
await mcp.getResource("system://health");
```

### Palette and Tool Resources
```javascript
// Active color palette
await mcp.getResource("palettes://active");

// Available brush presets
await mcp.getResource("brushes://list");

// Current tool state
await mcp.getResource("tools://current");
```

## 🎨 Color Format Reference

### Supported Color Formats
- **Hex**: `"#FF0000"`, `"#ff0000"` (red)
- **Hex with alpha**: `"#FF0000FF"` (red, fully opaque)
- **RGB**: `"rgb(255, 0, 0)"` (red)
- **RGBA**: `"rgba(255, 0, 0, 1.0)"` (red, fully opaque)
- **Named colors**: `"red"`, `"blue"`, `"green"`, `"black"`, `"white"`

### Common Colors
```javascript
const colors = {
  red: "#FF0000",
  green: "#00FF00",
  blue: "#0000FF",
  yellow: "#FFFF00",
  cyan: "#00FFFF",
  magenta: "#FF00FF",
  black: "#000000",
  white: "#FFFFFF",
  gray: "#808080",
  transparent: "#00000000"
};
```

## 📐 Coordinate System

- **Origin**: Top-left corner (0, 0)
- **X-axis**: Increases from left to right
- **Y-axis**: Increases from top to bottom
- **Units**: Pixels (integer coordinates preferred)

## 🔢 Common Parameter Ranges

| Parameter | Range | Notes |
|-----------|--------|--------|
| `opacity` | 0-100 | 0 = transparent, 100 = opaque |
| `quality` | 1-100 | JPEG quality setting |
| `compression` | 0-9 | PNG compression level |
| `threshold` | 0-100 | Selection/fill threshold |
| `feather` | 0+ | Feather radius in pixels |
| `brightness` | -100 to 100 | Brightness adjustment |
| `contrast` | -100 to 100 | Contrast adjustment |

## ⚡ Performance Tips

1. **Batch operations**: Group related tool calls together
2. **Use appropriate image sizes**: Larger images = slower processing
3. **Monitor memory usage**: Close unused documents
4. **Cache colors**: Reuse color values when possible
5. **Optimize brush strokes**: Use fewer points for simple shapes

## 🚨 Error Handling

All tools return a standardized response:
```javascript
{
  success: boolean,        // Operation success status
  data?: object,          // Result data (if successful)
  error?: string,         // Error message (if failed)
  operation: string,      // Tool name
  timestamp: number       // Unix timestamp
}
```

Check `success` field before using `data`:
```javascript
const result = await mcp.callTool("create_document", {width: 800, height: 600});
if (result.success) {
  const docId = result.data.document_id;
  // Use document ID
} else {
  console.error("Failed:", result.error);
}
```

## 📚 See Also

- [API Reference](../api-reference/README.md) - Detailed documentation
- [Tutorials](../tutorials/README.md) - Step-by-step examples
- [Tool Parameters](tool-parameters.md) - Complete parameter reference
- [Error Codes](error-codes.md) - Error code reference