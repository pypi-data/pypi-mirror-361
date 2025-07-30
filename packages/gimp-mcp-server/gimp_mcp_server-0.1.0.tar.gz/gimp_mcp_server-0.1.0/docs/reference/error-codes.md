# Error Code Reference

Comprehensive reference for GIMP MCP Server error codes, their meanings, and resolution strategies.

## 📋 Error Code Categories

- [MCP Protocol Errors](#mcp-protocol-errors) (100-199)
- [GIMP Connection Errors](#gimp-connection-errors) (200-299)
- [Document Errors](#document-errors) (300-399)
- [Layer Errors](#layer-errors) (400-499)
- [Tool Execution Errors](#tool-execution-errors) (500-599)
- [Resource Errors](#resource-errors) (600-699)
- [Validation Errors](#validation-errors) (700-799)
- [System Errors](#system-errors) (800-899)

## 🔧 Error Response Format

All errors follow a standardized format:

```typescript
interface ErrorResponse {
  success: false;
  error: string;           // Human-readable error message
  error_code: number;      // Numeric error code
  error_type: string;      // Error category
  details?: object;        // Additional error details
  operation: string;       // Operation that failed
  timestamp: number;       // Unix timestamp
  suggestions?: string[];  // Resolution suggestions
}
```

**Example Error Response**:
```json
{
  "success": false,
  "error": "Document with ID 42 not found",
  "error_code": 301,
  "error_type": "DOCUMENT_NOT_FOUND",
  "details": {
    "document_id": 42,
    "available_documents": [1, 2, 3]
  },
  "operation": "get_document_info",
  "timestamp": 1641234567.890,
  "suggestions": [
    "Check available documents with list_documents",
    "Ensure document ID is correct",
    "Verify document hasn't been closed"
  ]
}
```

## 🔌 MCP Protocol Errors (100-199)

### 100 - INVALID_REQUEST
**Message**: "Invalid MCP request format"  
**Cause**: Malformed JSON-RPC request  
**Resolution**: 
- Verify JSON syntax
- Check request structure
- Ensure required fields are present

```javascript
// Bad request
await mcp.callTool("create_document");  // Missing parameters object

// Good request
await mcp.callTool("create_document", {});
```

### 101 - METHOD_NOT_FOUND
**Message**: "Tool '{tool_name}' not found"  
**Cause**: Requested tool doesn't exist  
**Resolution**:
- Check tool name spelling
- Verify tool is available in current server version
- Use `list_tools` to see available tools

### 102 - INVALID_PARAMETERS
**Message**: "Invalid parameters for tool '{tool_name}'"  
**Cause**: Parameters don't match tool schema  
**Resolution**:
- Check parameter names and types
- Review tool documentation
- Validate required vs optional parameters

### 103 - RESOURCE_NOT_FOUND
**Message**: "Resource '{uri}' not found"  
**Cause**: Requested resource URI doesn't exist  
**Resolution**:
- Check resource URI spelling
- Verify resource is available
- Use `list_resources` to see available resources

### 104 - INTERNAL_ERROR
**Message**: "Internal server error"  
**Cause**: Unexpected server-side error  
**Resolution**:
- Retry the operation
- Check server logs
- Report bug if persistent

## 🔗 GIMP Connection Errors (200-299)

### 200 - GIMP_NOT_FOUND
**Message**: "GIMP application not found or not accessible"  
**Cause**: GIMP not installed or not in PATH  
**Resolution**:
- Install GIMP 3.0+
- Add GIMP to system PATH
- Verify GIMP can be launched manually

```bash
# Check GIMP installation
which gimp
gimp --version

# Test GIMP accessibility
gimp --batch-interpreter=python-fu-eval --batch='import gi; gi.require_version("Gimp", "3.0")' --batch='quit()'
```

### 201 - GIMP_CONNECTION_FAILED
**Message**: "Failed to establish connection with GIMP"  
**Cause**: Cannot connect to GIMP API  
**Resolution**:
- Ensure GIMP Python support is enabled
- Check PyGObject installation
- Verify GObject Introspection bindings

### 202 - GIMP_API_ERROR
**Message**: "GIMP API call failed: {details}"  
**Cause**: Error in GIMP API operation  
**Resolution**:
- Check GIMP compatibility
- Verify operation parameters
- Restart GIMP if needed

### 203 - GIMP_TIMEOUT
**Message**: "GIMP operation timed out"  
**Cause**: Operation took too long to complete  
**Resolution**:
- Reduce image size or complexity
- Increase timeout settings
- Check system resources

### 204 - GIMP_PERMISSION_DENIED
**Message**: "Permission denied accessing GIMP"  
**Cause**: Insufficient permissions  
**Resolution**:
- Run with appropriate user permissions
- Check file system permissions
- Verify display access (GUI mode)

## 📄 Document Errors (300-399)

### 300 - NO_ACTIVE_DOCUMENT
**Message**: "No active document available"  
**Cause**: No document is currently active in GIMP  
**Resolution**:
- Create a new document
- Open an existing document
- Specify document_id parameter

```javascript
// Handle no active document
try {
  const result = await mcp.callTool("get_layer_info", {layer_id: 1});
} catch (error) {
  if (error.error_code === 300) {
    // Create document first
    await mcp.callTool("create_document", {width: 800, height: 600});
    // Retry operation
  }
}
```

### 301 - DOCUMENT_NOT_FOUND
**Message**: "Document with ID {id} not found"  
**Cause**: Specified document doesn't exist  
**Resolution**:
- Check document ID is correct
- Verify document hasn't been closed
- Use `list_documents` to see available documents

### 302 - DOCUMENT_CREATION_FAILED
**Message**: "Failed to create document: {reason}"  
**Cause**: Document creation failed  
**Resolution**:
- Check memory availability
- Verify dimension parameters
- Reduce document size if needed

### 303 - DOCUMENT_OPEN_FAILED
**Message**: "Failed to open document: {file_path}"  
**Cause**: Cannot open specified file  
**Resolution**:
- Check file exists and is readable
- Verify file format is supported
- Check file permissions

### 304 - DOCUMENT_SAVE_FAILED
**Message**: "Failed to save document: {reason}"  
**Cause**: Document save operation failed  
**Resolution**:
- Check write permissions
- Verify disk space
- Ensure file path is valid

### 305 - UNSUPPORTED_FORMAT
**Message**: "File format not supported: {format}"  
**Cause**: Requested format is not supported  
**Resolution**:
- Use supported formats (PNG, JPEG, TIFF, XCF, etc.)
- Check GIMP format plugins
- Convert to supported format

## 🗂️ Layer Errors (400-499)

### 400 - LAYER_NOT_FOUND
**Message**: "Layer with ID {id} not found"  
**Cause**: Specified layer doesn't exist  
**Resolution**:
- Check layer ID is correct
- Verify layer hasn't been deleted
- Use `get_document_info` to see available layers

### 401 - LAYER_CREATION_FAILED
**Message**: "Failed to create layer: {reason}"  
**Cause**: Layer creation failed  
**Resolution**:
- Check memory availability
- Verify layer parameters
- Ensure document has space for new layer

### 402 - INVALID_LAYER_TYPE
**Message**: "Invalid layer type: {type}"  
**Cause**: Unsupported layer type specified  
**Resolution**:
- Use valid layer types: "RGB", "RGBA", "GRAYSCALE", etc.
- Check GIMP documentation for supported types

### 403 - LAYER_OPERATION_FAILED
**Message**: "Layer operation failed: {operation}"  
**Cause**: Layer modification failed  
**Resolution**:
- Check layer is not locked
- Verify operation parameters
- Ensure layer supports the operation

### 404 - INVALID_BLEND_MODE
**Message**: "Invalid blend mode: {mode}"  
**Cause**: Unsupported blend mode specified  
**Resolution**:
- Use valid blend modes: "normal", "multiply", "screen", etc.
- Check blend mode compatibility with layer type

## 🎨 Tool Execution Errors (500-599)

### 500 - TOOL_EXECUTION_FAILED
**Message**: "Tool execution failed: {tool_name}"  
**Cause**: Tool operation failed to complete  
**Resolution**:
- Check tool parameters
- Verify prerequisites are met
- Retry with different parameters

### 501 - INVALID_COORDINATES
**Message**: "Invalid coordinates: outside image bounds"  
**Cause**: Coordinates are outside image dimensions  
**Resolution**:
- Check coordinate values
- Ensure coordinates are within image bounds
- Get image dimensions first

```javascript
// Check coordinates before drawing
const docInfo = await mcp.callTool("get_document_info");
const {width, height} = docInfo.data;

if (x >= 0 && x < width && y >= 0 && y < height) {
  // Coordinates are valid
  await mcp.callTool("draw_rectangle", {x, y, width: 100, height: 100});
}
```

### 502 - INVALID_COLOR
**Message**: "Invalid color format: {color}"  
**Cause**: Color value is not in a recognized format  
**Resolution**:
- Use valid hex colors: "#FF0000"
- Use RGB format: "rgb(255, 0, 0)"
- Check color value syntax

### 503 - BRUSH_NOT_FOUND
**Message**: "Brush '{name}' not found"  
**Cause**: Specified brush doesn't exist  
**Resolution**:
- Check brush name spelling
- Use `brushes://list` resource to see available brushes
- Install required brush if missing

### 504 - SELECTION_REQUIRED
**Message**: "Operation requires an active selection"  
**Cause**: Tool needs a selection but none exists  
**Resolution**:
- Create a selection first
- Use selection tools before operation
- Check if operation supports no selection

### 505 - INSUFFICIENT_MEMORY
**Message**: "Insufficient memory for operation"  
**Cause**: Not enough memory to complete operation  
**Resolution**:
- Close unused documents
- Reduce image size
- Increase system memory
- Use smaller brush sizes

## 📡 Resource Errors (600-699)

### 600 - RESOURCE_ACCESS_FAILED
**Message**: "Failed to access resource: {uri}"  
**Cause**: Cannot retrieve resource data  
**Resolution**:
- Check resource URI
- Verify resource is available
- Retry after brief delay

### 601 - RESOURCE_UPDATE_FAILED
**Message**: "Failed to update resource: {uri}"  
**Cause**: Cannot update resource data  
**Resolution**:
- Check write permissions
- Verify resource supports updates
- Ensure resource is not locked

### 602 - STALE_RESOURCE
**Message**: "Resource data is stale: {uri}"  
**Cause**: Resource data is outdated  
**Resolution**:
- Refresh resource data
- Check for document changes
- Clear resource cache

## ✅ Validation Errors (700-799)

### 700 - PARAMETER_REQUIRED
**Message**: "Required parameter missing: {parameter}"  
**Cause**: Required parameter not provided  
**Resolution**:
- Check tool documentation
- Provide required parameter
- Verify parameter spelling

### 701 - PARAMETER_TYPE_MISMATCH
**Message**: "Parameter type mismatch: {parameter}"  
**Cause**: Parameter type doesn't match expected type  
**Resolution**:
- Check parameter type requirements
- Convert value to correct type
- Verify numeric ranges

### 702 - PARAMETER_OUT_OF_RANGE
**Message**: "Parameter out of range: {parameter}"  
**Cause**: Parameter value outside valid range  
**Resolution**:
- Check valid value ranges
- Adjust parameter value
- Use default values if unsure

### 703 - INVALID_FILE_PATH
**Message**: "Invalid file path: {path}"  
**Cause**: File path is invalid or inaccessible  
**Resolution**:
- Check path syntax
- Verify file exists
- Check file permissions

## ⚙️ System Errors (800-899)

### 800 - SYSTEM_RESOURCE_EXHAUSTED
**Message**: "System resources exhausted"  
**Cause**: System running out of resources  
**Resolution**:
- Close other applications
- Increase system memory
- Reduce operation complexity

### 801 - FILESYSTEM_ERROR
**Message**: "Filesystem error: {details}"  
**Cause**: File system operation failed  
**Resolution**:
- Check disk space
- Verify permissions
- Check file system integrity

### 802 - NETWORK_ERROR
**Message**: "Network operation failed"  
**Cause**: Network-related operation failed  
**Resolution**:
- Check network connectivity
- Verify server accessibility
- Retry after network recovery

### 803 - CONFIGURATION_ERROR
**Message**: "Configuration error: {details}"  
**Cause**: Server configuration issue  
**Resolution**:
- Check configuration files
- Verify environment variables
- Reset to default configuration

## 🛠️ Error Handling Best Practices

### 1. Always Check Success Status

```javascript
const result = await mcp.callTool("create_document", params);
if (!result.success) {
  console.error(`Operation failed: ${result.error}`);
  console.error(`Error code: ${result.error_code}`);
  return;
}
// Use result.data safely
```

### 2. Handle Specific Error Codes

```javascript
async function robustDocumentCreation(params) {
  try {
    const result = await mcp.callTool("create_document", params);
    
    if (!result.success) {
      switch (result.error_code) {
        case 200: // GIMP_NOT_FOUND
          throw new Error("GIMP not installed or accessible");
        case 302: // DOCUMENT_CREATION_FAILED
          // Try with smaller dimensions
          return await mcp.callTool("create_document", {
            ...params,
            width: Math.min(params.width, 2048),
            height: Math.min(params.height, 2048)
          });
        case 505: // INSUFFICIENT_MEMORY
          // Try with lower resolution
          return await mcp.callTool("create_document", {
            ...params,
            resolution: 150
          });
        default:
          throw new Error(`Document creation failed: ${result.error}`);
      }
    }
    
    return result;
  } catch (error) {
    console.error("Document creation error:", error);
    throw error;
  }
}
```

### 3. Implement Retry Logic

```javascript
async function retryOperation(operation, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await operation();
      
      if (result.success) {
        return result;
      }
      
      // Check if error is retryable
      const retryableCodes = [203, 500, 600, 800]; // Timeout, execution failed, resource access, system resource
      if (!retryableCodes.includes(result.error_code)) {
        throw new Error(`Non-retryable error: ${result.error}`);
      }
      
      if (attempt < maxRetries) {
        const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, delay));
        console.log(`Retrying operation (attempt ${attempt + 1}/${maxRetries})...`);
      }
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
    }
  }
}
```

### 4. Provide User-Friendly Error Messages

```javascript
function getUserFriendlyError(errorCode, error) {
  const errorMessages = {
    200: "GIMP is not installed or cannot be found. Please install GIMP 3.0+.",
    300: "No document is open. Please create or open a document first.",
    301: "The specified document could not be found. It may have been closed.",
    400: "The specified layer could not be found. Please check the layer ID.",
    501: "The coordinates are outside the image boundaries.",
    502: "The color format is invalid. Please use hex format like '#FF0000'.",
    505: "Not enough memory to complete the operation. Try closing other applications."
  };
  
  return errorMessages[errorCode] || `An error occurred: ${error}`;
}
```

### 5. Log Errors for Debugging

```javascript
function logError(operation, error) {
  console.error(`Error in ${operation}:`, {
    message: error.error,
    code: error.error_code,
    type: error.error_type,
    details: error.details,
    timestamp: new Date(error.timestamp * 1000).toISOString(),
    suggestions: error.suggestions
  });
}
```

## 📚 See Also

- [Command Reference](commands.md) - Quick tool reference
- [Troubleshooting Guide](../troubleshooting/README.md) - Detailed troubleshooting
- [API Reference](../api-reference/README.md) - Complete API documentation
- [Integration Guide](../integration/README.md) - Client integration patterns