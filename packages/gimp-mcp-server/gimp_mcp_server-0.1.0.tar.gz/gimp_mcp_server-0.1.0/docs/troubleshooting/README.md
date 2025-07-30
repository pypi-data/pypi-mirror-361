# Troubleshooting Guide

Comprehensive troubleshooting guide for the GIMP MCP Server, covering common issues, error messages, and their solutions.

## 📋 Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Connection Problems](#connection-problems)
- [GIMP Integration Issues](#gimp-integration-issues)
- [Tool Execution Errors](#tool-execution-errors)
- [Performance Issues](#performance-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Advanced Debugging](#advanced-debugging)

## 🔍 Quick Diagnostics

Run these commands to quickly identify common issues:

```bash
# Check server installation
gimp-mcp-server --version

# Test GIMP connection
gimp-mcp-server --test-connection

# Verify system requirements
gimp-mcp-server --system-check

# Run in debug mode
gimp-mcp-server --debug
```

## 🚨 Common Error Messages

### "ModuleNotFoundError: No module named 'gi'"

**Cause**: PyGObject (GObject Introspection) not installed

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0

# Fedora
sudo dnf install python3-gobject python3-gobject-devel

# macOS
brew install pygobject3 gtk+3

# Windows (using MSYS2)
pacman -S mingw-w64-x86_64-python-gobject
```

### "GIMP connection failed"

**Cause**: GIMP not found or not properly configured

**Solutions**:
1. **Verify GIMP installation**:
   ```bash
   # Check if GIMP is in PATH
   which gimp
   gimp --version
   ```

2. **Check GIMP Python support**:
   - Open GIMP
   - Go to Edit → Preferences → Folders → Plug-ins
   - Verify Python plug-ins directory exists

3. **Manual GIMP path configuration**:
   ```bash
   export GIMP_PATH="/path/to/gimp"
   gimp-mcp-server
   ```

### "Permission denied" errors

**Cause**: Insufficient permissions for GIMP or file operations

**Solutions**:
1. **Linux/macOS**:
   ```bash
   # Add user to necessary groups
   sudo usermod -a -G video $USER
   
   # Fix file permissions
   chmod +x ~/.local/bin/gimp-mcp-server
   ```

2. **Windows**:
   - Run Command Prompt as Administrator
   - Check User Account Control settings

### "Display not found" errors

**Cause**: No GUI display available (headless environment)

**Solutions**:
1. **Enable headless mode**:
   ```bash
   export GIMP_MCP_MODE=headless
   gimp-mcp-server
   ```

2. **Set up virtual display (Linux)**:
   ```bash
   # Install Xvfb
   sudo apt install xvfb
   
   # Run with virtual display
   export DISPLAY=:99
   Xvfb :99 -screen 0 1024x768x24 &
   gimp-mcp-server
   ```

3. **Windows Subsystem for Linux**:
   ```bash
   # Install X server for Windows
   # Use VcXsrv or Xming
   export DISPLAY=:0
   ```

## 🔧 Installation Issues

### PyGObject Installation Fails

**Ubuntu/Debian**:
```bash
# Install build dependencies
sudo apt update
sudo apt install build-essential python3-dev pkg-config
sudo apt install libgirepository1.0-dev libcairo2-dev
pip3 install PyGObject
```

**CentOS/RHEL**:
```bash
# Enable EPEL repository
sudo yum install epel-release
sudo yum install python3-devel pkg-config cairo-devel
sudo yum install gobject-introspection-devel
pip3 install PyGObject
```

**macOS**:
```bash
# Using Homebrew
brew install pkg-config cairo gobject-introspection
pip3 install PyGObject

# If still failing, try:
export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig"
pip3 install PyGObject
```

### GIMP 3.0 Not Available

**Solution**: Install GIMP 3.0 from development sources:

```bash
# Ubuntu (using PPA)
sudo add-apt-repository ppa:otto-kesselgulasch/gimp-edge
sudo apt update
sudo apt install gimp-2.99

# Flatpak (any Linux distribution)
flatpak install flathub org.gimp.GIMP//beta

# macOS (using Homebrew)
brew install --cask gimp@beta

# Windows
# Download from GIMP development releases
```

## 🔌 Connection Problems

### Server Won't Start

**Diagnosis**:
```bash
# Check port availability
netstat -tlnp | grep 3000

# Check for conflicting processes
ps aux | grep gimp-mcp
```

**Solutions**:
1. **Port already in use**:
   ```bash
   # Use different port
   gimp-mcp-server --port 3001
   
   # Or kill conflicting process
   sudo kill $(lsof -t -i:3000)
   ```

2. **Multiple server instances**:
   ```bash
   # Kill all instances
   pkill -f gimp-mcp-server
   
   # Restart clean
   gimp-mcp-server
   ```

### Client Connection Fails

**Diagnosis**:
```bash
# Test server accessibility
curl http://localhost:3000/health

# Check firewall
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS
```

**Solutions**:
1. **Firewall blocking connection**:
   ```bash
   # Ubuntu
   sudo ufw allow 3000
   
   # CentOS
   sudo firewall-cmd --add-port=3000/tcp --permanent
   sudo firewall-cmd --reload
   ```

2. **Network configuration**:
   ```bash
   # Allow external connections
   gimp-mcp-server --host 0.0.0.0 --port 3000
   ```

## 🖼️ GIMP Integration Issues

### GIMP Crashes on Tool Execution

**Diagnosis**:
```bash
# Run GIMP with debugging
gimp --verbose --console-messages

# Check system logs
journalctl -f  # Linux
Console.app    # macOS
Event Viewer   # Windows
```

**Solutions**:
1. **Memory issues**:
   ```bash
   # Increase GIMP memory limits
   export GIMP_CACHE_SIZE=4096  # 4GB cache
   export GIMP_TILE_CACHE_SIZE=2048  # 2GB tiles
   ```

2. **Plugin conflicts**:
   - Disable third-party plugins
   - Reset GIMP preferences:
     ```bash
     # Backup and reset preferences
     mv ~/.config/GIMP ~/.config/GIMP.backup
     gimp  # This will create fresh preferences
     ```

### Operations Timeout

**Cause**: Large images or complex operations

**Solutions**:
1. **Increase timeout values**:
   ```python
   # In client code
   mcp_client.timeout = 300  # 5 minutes
   ```

2. **Optimize image size**:
   ```javascript
   // Reduce image dimensions for testing
   const doc = await mcp.callTool("create_document", {
     width: 1024,   // Instead of 4096
     height: 1024,  // Instead of 4096
     resolution: 150 // Instead of 300
   });
   ```

## ⚡ Performance Issues

### Slow Tool Execution

**Diagnosis**:
```bash
# Monitor system resources
htop        # Linux/macOS
taskmgr     # Windows

# Check GIMP memory usage
ps aux | grep gimp
```

**Solutions**:
1. **Optimize GIMP settings**:
   ```bash
   # Set environment variables
   export GIMP_NUM_PROCESSORS=4  # Use 4 CPU cores
   export GIMP_USE_OPENCL=yes     # Enable GPU acceleration
   ```

2. **Batch operations efficiently**:
   ```javascript
   // Bad: Many individual calls
   for (let i = 0; i < 100; i++) {
     await mcp.callTool("set_layer_opacity", {opacity: i});
   }
   
   // Good: Batch related operations
   const operations = [];
   for (let i = 0; i < 100; i++) {
     operations.push({tool: "set_layer_opacity", params: {opacity: i}});
   }
   await batchExecute(operations);
   ```

### Memory Leaks

**Symptoms**: Increasing memory usage over time

**Solutions**:
1. **Close unused documents**:
   ```javascript
   // Close document when done
   await mcp.callTool("close_document", {
     document_id: doc.data.document_id
   });
   ```

2. **Restart server periodically**:
   ```bash
   # For long-running processes
   pkill -f gimp-mcp-server
   sleep 5
   gimp-mcp-server &
   ```

## 🖥️ Platform-Specific Issues

### Linux (Ubuntu/Debian)

**GTK4 not found**:
```bash
sudo apt install libgtk-4-dev libgtk-4-1
export PKG_CONFIG_PATH="/usr/lib/x86_64-linux-gnu/pkgconfig"
```

**Wayland compatibility**:
```bash
# Force X11 if Wayland causes issues
export GDK_BACKEND=x11
gimp-mcp-server
```

### Windows

**DLL loading errors**:
```cmd
# Add GIMP bin directory to PATH
set PATH=%PATH%;C:\Program Files\GIMP 3\bin
gimp-mcp-server
```

**MSYS2 environment**:
```bash
# Ensure proper environment
source /etc/profile
export PATH="/mingw64/bin:$PATH"
```

### macOS

**SIP (System Integrity Protection) issues**:
```bash
# Use Homebrew installation
brew install gimp --cask
export PATH="/Applications/GIMP.app/Contents/MacOS:$PATH"
```

**Permission errors**:
```bash
# Grant terminal permissions in Security & Privacy
# System Preferences → Security & Privacy → Privacy → Developer Tools
```

## 🔬 Advanced Debugging

### Enable Verbose Logging

```bash
# Maximum verbosity
export GIMP_MCP_DEBUG=1
export GIMP_MCP_LOG_LEVEL=DEBUG
gimp-mcp-server --verbose
```

### Debug Tool Execution

```python
# Add to client code
import logging
logging.basicConfig(level=logging.DEBUG)

# Trace MCP calls
async def debug_tool_call(tool_name, params):
    print(f"Calling tool: {tool_name}")
    print(f"Parameters: {params}")
    
    result = await mcp.callTool(tool_name, params)
    
    print(f"Result: {result}")
    return result
```

### Memory and Performance Profiling

```bash
# Monitor server process
# Get PID of gimp-mcp-server
ps aux | grep gimp-mcp-server

# Monitor memory usage
watch -n 1 'ps -p <PID> -o pid,ppid,cmd,%mem,%cpu --no-headers'

# Generate core dump if crashed
ulimit -c unlimited
export GIMP_MCP_DEBUG_CORE=1
```

### Network Debugging

```bash
# Monitor network traffic
sudo tcpdump -i lo port 3000

# Test with curl
curl -X POST http://localhost:3000/api/tools/test \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## 📞 Getting Help

If you can't resolve the issue:

1. **Search existing issues**: [GitHub Issues](https://github.com/gimp-mcp/gimp-mcp-server/issues)

2. **Create a bug report** with:
   - Operating system and version
   - GIMP version
   - Python version
   - Full error messages
   - Steps to reproduce
   - Debug logs

3. **Join community discussions**: [GitHub Discussions](https://github.com/gimp-mcp/gimp-mcp-server/discussions)

4. **Check documentation**:
   - [User Guide](../user-guide/README.md)
   - [API Reference](../api-reference/README.md)
   - [Installation Guide](../user-guide/installation.md)

## 🔄 Recovery Procedures

### Reset Server State

```bash
# Clean shutdown
pkill -TERM gimp-mcp-server

# Remove temporary files
rm -rf /tmp/gimp-mcp-*

# Reset GIMP preferences (if needed)
mv ~/.config/GIMP ~/.config/GIMP.backup

# Fresh start
gimp-mcp-server --clean-start
```

### Backup and Restore

```bash
# Backup important files
cp ~/.config/gimp-mcp-server/config.json config-backup.json

# Restore from backup
cp config-backup.json ~/.config/gimp-mcp-server/config.json
```

### Emergency Debugging

```bash
# Emergency debug mode
export GIMP_MCP_EMERGENCY_DEBUG=1
export GIMP_MCP_SAFE_MODE=1
gimp-mcp-server --emergency