# Document Tools

Document management operations for creating, opening, saving, and exporting GIMP documents.

## 📋 Available Tools

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| [get_document_info](#get_document_info) | Get document information | `document_id?` | Document details |
| [list_documents](#list_documents) | List all open documents | None | Document list |
| [create_document](#create_document) | Create new document | `width`, `height`, `resolution`, etc. | Document ID |
| [open_document](#open_document) | Open existing document | `file_path` | Document ID |
| [save_document](#save_document) | Save document | `document_id?`, `file_path?` | Save result |
| [export_document](#export_document) | Export document | `document_id?`, `file_path`, `format` | Export result |

## 🔧 Tool Details

### get_document_info

Get detailed information about a GIMP document.

#### Parameters

```typescript
interface GetDocumentInfoParams {
  document_id?: number;  // Optional document ID (uses active if not provided)
}
```

#### Returns

```typescript
interface DocumentInfo {
  success: boolean;
  data?: {
    document_id: number;
    name: string;
    width: number;
    height: number;
    resolution: number;
    mode: string;          // "RGB", "GRAYSCALE", "INDEXED"
    precision: string;     // "8-bit", "16-bit", "32-bit"
    layer_count: number;
    layers: Array<{
      id: number;
      name: string;
      visible: boolean;
      opacity: number;
      blend_mode: string;
    }>;
    has_unsaved_changes: boolean;
    file_path?: string;
    file_size?: number;
    creation_time?: number;
    modification_time?: number;
  };
  error?: string;
  operation: "get_document_info";
  timestamp: number;
}
```

#### Example

```javascript
// Get info for active document
const info = await mcp.callTool("get_document_info");

// Get info for specific document
const info = await mcp.callTool("get_document_info", {
  document_id: 42
});
```

### list_documents

List all open documents in GIMP.

#### Parameters

None

#### Returns

```typescript
interface DocumentList {
  success: boolean;
  data?: {
    documents: Array<{
      id: number;
      name: string;
      width: number;
      height: number;
      mode: string;
      is_active: boolean;
      has_unsaved_changes: boolean;
      file_path?: string;
    }>;
    count: number;
    active_document_id?: number;
  };
  error?: string;
  operation: "list_documents";
  timestamp: number;
}
```

#### Example

```javascript
const documents = await mcp.callTool("list_documents");
console.log(`Found ${documents.data.count} open documents`);
```

### create_document

Create a new GIMP document.

#### Parameters

```typescript
interface CreateDocumentParams {
  width?: number;        // Width in pixels (default: 1920)
  height?: number;       // Height in pixels (default: 1080)
  resolution?: number;   // Resolution in PPI (default: 300)
  color_mode?: string;   // "RGB", "GRAYSCALE", "INDEXED" (default: "RGB")
  precision?: string;    // "8-bit", "16-bit", "32-bit" (default: "8-bit")
  fill_type?: string;    // "transparent", "white", "black", "foreground", "background" (default: "transparent")
  name?: string;         // Document name (default: "Untitled")
}
```

#### Returns

```typescript
interface CreateDocumentResult {
  success: boolean;
  data?: {
    document_id: number;
    name: string;
    width: number;
    height: number;
    resolution: number;
    mode: string;
    precision: string;
    layer_id: number;      // ID of the initial layer
  };
  error?: string;
  operation: "create_document";
  timestamp: number;
}
```

#### Example

```javascript
// Create a standard document
const doc = await mcp.callTool("create_document", {
  width: 1920,
  height: 1080,
  resolution: 300,
  color_mode: "RGB",
  fill_type: "white",
  name: "My New Document"
});

// Create a high-resolution document
const hires = await mcp.callTool("create_document", {
  width: 4096,
  height: 4096,
  resolution: 600,
  precision: "16-bit",
  fill_type: "transparent"
});
```

### open_document

Open an existing document from file.

#### Parameters

```typescript
interface OpenDocumentParams {
  file_path: string;     // Path to the document file
}
```

#### Returns

```typescript
interface OpenDocumentResult {
  success: boolean;
  data?: {
    document_id: number;
    name: string;
    width: number;
    height: number;
    mode: string;
    layer_count: number;
    file_path: string;
    file_size: number;
  };
  error?: string;
  operation: "open_document";
  timestamp: number;
}
```

#### Example

```javascript
// Open a document
const doc = await mcp.callTool("open_document", {
  file_path: "/path/to/image.xcf"
});

// Open various formats
const jpg = await mcp.callTool("open_document", {
  file_path: "/path/to/photo.jpg"
});

const png = await mcp.callTool("open_document", {
  file_path: "/path/to/graphic.png"
});
```

### save_document

Save a document to file.

#### Parameters

```typescript
interface SaveDocumentParams {
  document_id?: number;   // Optional document ID (uses active if not provided)
  file_path?: string;     // Optional file path (uses current path if not provided)
  overwrite?: boolean;    // Whether to overwrite existing file (default: false)
}
```

#### Returns

```typescript
interface SaveDocumentResult {
  success: boolean;
  data?: {
    document_id: number;
    file_path: string;
    file_size: number;
    format: string;        // "XCF", "PSD", etc.
  };
  error?: string;
  operation: "save_document";
  timestamp: number;
}
```

#### Example

```javascript
// Save active document
const result = await mcp.callTool("save_document");

// Save to specific path
const result = await mcp.callTool("save_document", {
  file_path: "/path/to/save/document.xcf",
  overwrite: true
});

// Save specific document
const result = await mcp.callTool("save_document", {
  document_id: 42,
  file_path: "/path/to/save/document.xcf"
});
```

### export_document

Export document to various formats.

#### Parameters

```typescript
interface ExportDocumentParams {
  document_id?: number;   // Optional document ID (uses active if not provided)
  file_path: string;      // Export file path
  format?: string;        // Export format (default: inferred from file extension)
  options?: {
    quality?: number;     // JPEG quality (1-100)
    compression?: number; // PNG compression (0-9)
    progressive?: boolean;// Progressive JPEG
    optimize?: boolean;   // Optimize file size
    metadata?: boolean;   // Include metadata
    color_profile?: boolean; // Include color profile
  };
}
```

#### Returns

```typescript
interface ExportDocumentResult {
  success: boolean;
  data?: {
    document_id: number;
    file_path: string;
    file_size: number;
    format: string;
    options_used: object;
  };
  error?: string;
  operation: "export_document";
  timestamp: number;
}
```

#### Example

```javascript
// Export as PNG
const png = await mcp.callTool("export_document", {
  file_path: "/path/to/export.png",
  options: {
    compression: 6,
    optimize: true
  }
});

// Export as JPEG with quality
const jpg = await mcp.callTool("export_document", {
  file_path: "/path/to/export.jpg",
  options: {
    quality: 95,
    progressive: true,
    optimize: true
  }
});

// Export as TIFF
const tiff = await mcp.callTool("export_document", {
  file_path: "/path/to/export.tiff",
  options: {
    compression: 1,
    color_profile: true
  }
});
```

## 🎯 Common Workflows

### Basic Document Creation

```javascript
// Create a new document
const doc = await mcp.callTool("create_document", {
  width: 1920,
  height: 1080,
  name: "My Project"
});

// Work with the document...
// ... add layers, draw, etc ...

// Save the document
await mcp.callTool("save_document", {
  document_id: doc.data.document_id,
  file_path: "/path/to/project.xcf"
});

// Export for web
await mcp.callTool("export_document", {
  document_id: doc.data.document_id,
  file_path: "/path/to/web-version.png",
  options: {
    optimize: true
  }
});
```

### Batch Processing

```javascript
// Process multiple files
const files = [
  "/path/to/image1.jpg",
  "/path/to/image2.jpg",
  "/path/to/image3.jpg"
];

for (const file of files) {
  // Open document
  const doc = await mcp.callTool("open_document", {
    file_path: file
  });
  
  // Process document (resize, filter, etc.)
  // ... processing operations ...
  
  // Export processed version
  const outputPath = file.replace(".jpg", "_processed.png");
  await mcp.callTool("export_document", {
    document_id: doc.data.document_id,
    file_path: outputPath
  });
}
```

## 🚨 Error Handling

Common errors and their handling:

```javascript
try {
  const doc = await mcp.callTool("create_document", {
    width: 10000,
    height: 10000
  });
} catch (error) {
  if (error.message.includes("memory")) {
    console.log("Document too large, reducing size");
    // Retry with smaller dimensions
  }
}
```

## 📊 Supported Formats

### Import Formats
- **XCF** - GIMP native format
- **PSD** - Adobe Photoshop
- **PNG** - Portable Network Graphics
- **JPEG** - Joint Photographic Experts Group
- **TIFF** - Tagged Image File Format
- **GIF** - Graphics Interchange Format
- **BMP** - Bitmap
- **WEBP** - WebP format
- **SVG** - Scalable Vector Graphics (imported as raster)

### Export Formats
- **XCF** - GIMP native format (save)
- **PNG** - Best for graphics with transparency
- **JPEG** - Best for photographs
- **TIFF** - Best for print and archival
- **GIF** - Best for animations
- **BMP** - Windows bitmap
- **WEBP** - Modern web format
- **PDF** - Portable Document Format

## 🔧 Performance Tips

1. **Use appropriate resolution**: Higher resolution = larger file size and slower processing
2. **Choose the right format**: Use PNG for graphics, JPEG for photos
3. **Optimize exports**: Use compression options to reduce file size
4. **Monitor memory usage**: Large documents consume significant RAM
5. **Close unused documents**: Free up memory by closing documents when done

## 📚 See Also

- [Layer Tools](layer-tools.md) - Layer management operations
- [Drawing Tools](drawing-tools.md) - Drawing and painting
- [Color Tools](color-tools.md) - Color management
- [System Resources](../resources/system-resources.md) - System status monitoring