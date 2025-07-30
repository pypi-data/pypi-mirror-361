# Creating Simple Graphics

Learn to create basic graphics and shapes using the GIMP MCP Server. This tutorial covers fundamental operations for creating logos, icons, and simple illustrations.

## 🎯 What You'll Learn

- Creating documents with custom dimensions
- Working with basic shapes and colors
- Layer management fundamentals
- Text and typography basics
- Exporting for different uses

## 📋 Prerequisites

- GIMP MCP Server installed and running
- Basic understanding of MCP tool calls
- An MCP client (Claude Desktop, custom client, etc.)

## 🚀 Step-by-Step Walkthrough

### Step 1: Create a New Document

Let's start by creating a square canvas suitable for a logo or icon:

```javascript
// Create a 512x512 pixel document at 300 DPI
const document = await mcp.callTool("create_document", {
  width: 512,
  height: 512,
  resolution: 300,
  color_mode: "RGB",
  fill_type: "transparent",
  name: "Simple Logo"
});

console.log(`Created document with ID: ${document.data.document_id}`);
```

**Result**: You now have a transparent 512x512 canvas ready for graphics.

### Step 2: Set Up Colors

Define a color palette for your graphic:

```javascript
// Set up a modern color scheme
const primaryColor = "#2C3E50";   // Dark blue-gray
const accentColor = "#3498DB";    // Bright blue
const highlightColor = "#E74C3C"; // Red

// Set the foreground color for drawing
await mcp.callTool("set_foreground_color", {
  color: primaryColor
});

// Set background color (even though we're using transparent)
await mcp.callTool("set_background_color", {
  color: "#FFFFFF"
});
```

### Step 3: Create a Background Layer

Add a subtle background to make our graphic stand out:

```javascript
// Create a background layer
const bgLayer = await mcp.callTool("create_layer", {
  name: "Background",
  layer_type: "RGB",
  opacity: 100.0,
  blend_mode: "normal"
});

// Create a subtle gradient background using a large ellipse
await mcp.callTool("draw_ellipse", {
  layer_id: bgLayer.data.layer_id,
  center_x: 256,
  center_y: 256,
  radius_x: 400,
  radius_y: 400,
  fill_color: "#ECF0F1", // Very light gray
  stroke_color: null
});

// Reduce opacity for subtlety
await mcp.callTool("set_layer_opacity", {
  layer_id: bgLayer.data.layer_id,
  opacity: 30.0
});
```

### Step 4: Create the Main Shape

Now let's create the primary graphic element:

```javascript
// Create a shapes layer
const shapesLayer = await mcp.callTool("create_layer", {
  name: "Main Shape",
  layer_type: "RGB",
  opacity: 100.0
});

// Draw a rounded rectangle (approximated with overlapping shapes)
// Main rectangle body
await mcp.callTool("draw_rectangle", {
  layer_id: shapesLayer.data.layer_id,
  x: 156,
  y: 156,
  width: 200,
  height: 200,
  fill_color: primaryColor,
  stroke_color: null
});

// Add corner circles for rounded effect
const cornerRadius = 20;
const corners = [
  {x: 156 + cornerRadius, y: 156 + cornerRadius}, // Top-left
  {x: 356 - cornerRadius, y: 156 + cornerRadius}, // Top-right
  {x: 156 + cornerRadius, y: 356 - cornerRadius}, // Bottom-left
  {x: 356 - cornerRadius, y: 356 - cornerRadius}  // Bottom-right
];

for (const corner of corners) {
  await mcp.callTool("draw_ellipse", {
    layer_id: shapesLayer.data.layer_id,
    center_x: corner.x,
    center_y: corner.y,
    radius_x: cornerRadius,
    radius_y: cornerRadius,
    fill_color: primaryColor,
    stroke_color: null
  });
}
```

### Step 5: Add Accent Elements

Create visual interest with accent shapes:

```javascript
// Create an accents layer
const accentsLayer = await mcp.callTool("create_layer", {
  name: "Accents",
  layer_type: "RGB",
  opacity: 100.0
});

// Add a smaller accent circle
await mcp.callTool("draw_ellipse", {
  layer_id: accentsLayer.data.layer_id,
  center_x: 256,
  center_y: 220,
  radius_x: 40,
  radius_y: 40,
  fill_color: accentColor,
  stroke_color: null
});

// Add accent lines using brush strokes
const linePoints1 = [[200, 280], [312, 280]];
const linePoints2 = [[200, 300], [290, 300]];

await mcp.callTool("set_foreground_color", {
  color: accentColor
});

await mcp.callTool("apply_brush_stroke", {
  layer_id: accentsLayer.data.layer_id,
  points: linePoints1,
  brush_name: "2. Hardness 100",
  size: 8,
  opacity: 100,
  color: accentColor
});

await mcp.callTool("apply_brush_stroke", {
  layer_id: accentsLayer.data.layer_id,
  points: linePoints2,
  brush_name: "2. Hardness 100",
  size: 6,
  opacity: 100,
  color: accentColor
});
```

### Step 6: Add Highlight Details

Create depth with highlights:

```javascript
// Create highlights layer
const highlightsLayer = await mcp.callTool("create_layer", {
  name: "Highlights",
  layer_type: "RGB",
  opacity: 100.0,
  blend_mode: "overlay" // Blend mode for subtle highlights
});

// Add a small highlight circle
await mcp.callTool("draw_ellipse", {
  layer_id: highlightsLayer.data.layer_id,
  center_x: 240,
  center_y: 190,
  radius_x: 15,
  radius_y: 15,
  fill_color: "#FFFFFF",
  stroke_color: null
});

// Reduce opacity for subtle effect
await mcp.callTool("set_layer_opacity", {
  layer_id: highlightsLayer.data.layer_id,
  opacity: 60.0
});
```

### Step 7: Add a Text Element (Optional)

If creating a logo, add text:

```javascript
// Create text layer
const textLayer = await mcp.callTool("create_layer", {
  name: "Text",
  layer_type: "RGB",
  opacity: 100.0
});

// Note: Text rendering requires more complex operations
// For now, we'll create a simple text-like element with shapes
const letterSpacing = 25;
const startX = 190;
const textY = 380;

// Simple "LOGO" representation with rectangles
const letters = [
  // L
  [[startX, textY], [startX, textY + 40], [startX + 15, textY + 40]],
  // O (approximated with rectangle)
  [[startX + letterSpacing, textY], [startX + letterSpacing + 15, textY + 40]],
  // G (approximated)
  [[startX + letterSpacing * 2, textY], [startX + letterSpacing * 2 + 15, textY + 40]],
  // O
  [[startX + letterSpacing * 3, textY], [startX + letterSpacing * 3 + 15, textY + 40]]
];

// Draw simple letter shapes
for (let i = 0; i < letters.length; i++) {
  await mcp.callTool("draw_rectangle", {
    layer_id: textLayer.data.layer_id,
    x: letters[i][0][0],
    y: letters[i][0][1],
    width: 15,
    height: 40,
    fill_color: primaryColor,
    stroke_color: null
  });
}
```

### Step 8: Final Adjustments

Fine-tune the composition:

```javascript
// Get current document info to verify our work
const docInfo = await mcp.callTool("get_document_info");
console.log(`Document has ${docInfo.data.layer_count} layers`);

// List all layers
for (const layer of docInfo.data.layers) {
  console.log(`Layer: ${layer.name}, Opacity: ${layer.opacity}%, Visible: ${layer.visible}`);
}

// Adjust overall composition if needed
// For example, make the accents layer slightly more transparent
await mcp.callTool("set_layer_opacity", {
  layer_id: accentsLayer.data.layer_id,
  opacity: 85.0
});
```

### Step 9: Export Your Graphic

Export in multiple formats for different uses:

```javascript
// Export as PNG for web use (preserves transparency)
await mcp.callTool("export_document", {
  file_path: "/path/to/simple-logo.png",
  options: {
    optimize: true,
    compression: 6
  }
});

// Export as JPEG for presentations (adds white background)
await mcp.callTool("export_document", {
  file_path: "/path/to/simple-logo.jpg",
  options: {
    quality: 95,
    progressive: true
  }
});

// Export smaller version for favicon
await mcp.callTool("export_document", {
  file_path: "/path/to/simple-logo-32x32.png",
  options: {
    width: 32,
    height: 32,
    optimize: true
  }
});

// Save the GIMP project file
await mcp.callTool("save_document", {
  file_path: "/path/to/simple-logo.xcf"
});
```

## 🎨 Variations and Experiments

Try these variations to explore different design approaches:

### Color Variations

```javascript
// Create a monochromatic version
const monoColors = {
  primary: "#2C3E50",
  light: "#7F8C8D",
  lighter: "#BDC3C7"
};

// Or try a vibrant palette
const vibrantColors = {
  primary: "#E74C3C",
  accent: "#F39C12",
  highlight: "#F1C40F"
};
```

### Shape Variations

```javascript
// Try different shapes for variety
// Hexagon instead of rounded rectangle
await mcp.callTool("draw_hexagon", {
  center_x: 256,
  center_y: 256,
  radius: 100,
  fill_color: primaryColor
});

// Or multiple smaller circles
const circlePositions = [
  {x: 200, y: 200}, {x: 312, y: 200},
  {x: 200, y: 312}, {x: 312, y: 312},
  {x: 256, y: 256}
];

for (const pos of circlePositions) {
  await mcp.callTool("draw_ellipse", {
    center_x: pos.x,
    center_y: pos.y,
    radius_x: 30,
    radius_y: 30,
    fill_color: accentColor
  });
}
```

## 💡 Tips and Best Practices

### 1. Layer Organization
- Use descriptive layer names
- Group related elements on the same layer
- Keep backgrounds on bottom layers
- Use separate layers for different colors

### 2. Color Management
- Define your color palette before starting
- Use consistent colors throughout
- Consider accessibility (contrast ratios)
- Test colors on different backgrounds

### 3. Composition Guidelines
- Follow the rule of thirds
- Create visual balance
- Use whitespace effectively
- Maintain consistent spacing

### 4. Export Optimization
- PNG for graphics with transparency
- JPEG for photographic content
- Consider file size vs. quality trade-offs
- Create multiple sizes for different uses

## 🚨 Troubleshooting

### Common Issues

**Colors don't match expectations**
```javascript
// Verify color values
const currentFG = await mcp.getResource("palettes://active");
console.log("Current foreground:", currentFG.content.foreground_color);
```

**Shapes aren't aligned properly**
```javascript
// Use consistent positioning
const centerX = 256; // Half of 512
const centerY = 256;
// Always calculate positions relative to center
```

**Layers appear in wrong order**
```javascript
// Check layer order
const docInfo = await mcp.callTool("get_document_info");
docInfo.data.layers.forEach((layer, index) => {
  console.log(`Layer ${index}: ${layer.name}`);
});
```

### Performance Tips

1. **Batch similar operations** - Group color changes together
2. **Use appropriate brush sizes** - Smaller brushes for details
3. **Monitor memory usage** - Check system resources periodically
4. **Save frequently** - Prevent work loss

## 📚 Next Steps

After completing this tutorial, try:

1. **[Layer Management](layer-management.md)** - Advanced layer techniques
2. **[Color and Brushes](color-and-brushes.md)** - Artistic techniques
3. **[Logo Design](../real-world-projects/logo-design.md)** - Professional logo creation
4. **[Web Graphics](../real-world-projects/web-graphics.md)** - Graphics for web use

## 🔍 Related Resources

- [Drawing Tools API](../../api-reference/tools/drawing-tools.md)
- [Layer Tools API](../../api-reference/tools/layer-tools.md)
- [Color Tools API](../../api-reference/tools/color-tools.md)
- [Export Best Practices](../../user-guide/advanced-features.md#export-optimization)