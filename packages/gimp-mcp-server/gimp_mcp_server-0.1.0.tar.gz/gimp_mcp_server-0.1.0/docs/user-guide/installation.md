# Installation Guide

This guide will walk you through installing the GIMP MCP Server on your system.

## 📋 Prerequisites

Before installing the GIMP MCP Server, ensure you have the following prerequisites:

### Required Software

1. **GIMP 3.0+** with Python support enabled
2. **Python 3.9+** with pip package manager
3. **GTK4 development libraries** (for GUI mode)
4. **GObject Introspection libraries**

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+), Windows 10+, macOS 11+
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space for installation
- **Graphics**: OpenGL-compatible graphics card

## 🐧 Linux Installation

### Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install GIMP 3.0 and dependencies
sudo apt install gimp-3.0 python3-dev python3-pip

# Install GTK4 and GObject development libraries
sudo apt install libgtk-4-dev libgirepository1.0-dev

# Install PyGObject
pip3 install PyGObject

# Install GIMP MCP Server
pip3 install gimp-mcp-server
```

### Fedora/RHEL

```bash
# Install GIMP 3.0 and dependencies
sudo dnf install gimp python3-devel python3-pip

# Install GTK4 and GObject development libraries
sudo dnf install gtk4-devel gobject-introspection-devel

# Install PyGObject
pip3 install PyGObject

# Install GIMP MCP Server
pip3 install gimp-mcp-server
```

### Arch Linux

```bash
# Install GIMP 3.0 and dependencies
sudo pacman -S gimp python python-pip

# Install GTK4 and GObject development libraries
sudo pacman -S gtk4 gobject-introspection

# Install PyGObject
pip install PyGObject

# Install GIMP MCP Server
pip install gimp-mcp-server
```

## 🪟 Windows Installation

### Option 1: Using Windows Subsystem for Linux (WSL)

1. **Install WSL2** following [Microsoft's guide](https://docs.microsoft.com/en-us/windows/wsl/install)
2. **Install Ubuntu** from Microsoft Store
3. **Follow Linux installation steps** above in your WSL environment

### Option 2: Native Windows Installation

1. **Install GIMP 3.0**
   - Download from [GIMP official website](https://www.gimp.org/downloads/)
   - Ensure Python support is enabled during installation

2. **Install Python 3.9+**
   - Download from [Python.org](https://www.python.org/downloads/)
   - Add Python to PATH during installation

3. **Install GTK4 for Windows**
   ```cmd
   # Using MSYS2 (recommended)
   pacman -S mingw-w64-x86_64-gtk4
   pacman -S mingw-w64-x86_64-gobject-introspection
   ```

4. **Install PyGObject**
   ```cmd
   pip install PyGObject
   ```

5. **Install GIMP MCP Server**
   ```cmd
   pip install gimp-mcp-server
   ```

## 🍎 macOS Installation

### Using Homebrew (Recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install GIMP 3.0
brew install --cask gimp

# Install Python 3.9+
brew install python@3.9

# Install GTK4 and GObject libraries
brew install gtk4 gobject-introspection

# Install PyGObject
pip3 install PyGObject

# Install GIMP MCP Server
pip3 install gimp-mcp-server
```

### Using MacPorts

```bash
# Install GIMP 3.0
sudo port install gimp3

# Install Python 3.9+
sudo port install python39

# Install GTK4 and GObject libraries
sudo port install gtk4 gobject-introspection

# Install PyGObject
pip3 install PyGObject

# Install GIMP MCP Server
pip3 install gimp-mcp-server
```

## 🔧 Development Installation

For development or to install from source:

```bash
# Clone the repository
git clone https://github.com/gimp-mcp/gimp-mcp-server.git
cd gimp-mcp-server

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install development dependencies
pip install -e ".[dev,test]"
```

## ✅ Verification

After installation, verify everything is working:

```bash
# Check GIMP MCP Server installation
gimp-mcp-server --version

# Test GIMP connection
gimp-mcp-server --test-connection

# Start the server (should start without errors)
gimp-mcp-server --debug
```

## 🐳 Docker Installation

For containerized deployment:

```bash
# Pull the official image
docker pull gimp-mcp/server:latest

# Run the container
docker run -d \
  --name gimp-mcp-server \
  -p 3000:3000 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  gimp-mcp/server:latest
```

## 🔄 Updating

To update to the latest version:

```bash
# Update via pip
pip install --upgrade gimp-mcp-server

# Or if installed from source
cd gimp-mcp-server
git pull origin main
pip install -e .
```

## 🚨 Troubleshooting Installation

### Common Issues

1. **"ModuleNotFoundError: No module named 'gi'"**
   - Install PyGObject: `pip install PyGObject`
   - Ensure GObject Introspection is installed

2. **"GIMP not found" error**
   - Verify GIMP 3.0+ is installed
   - Check GIMP is in your PATH
   - Enable Python support in GIMP preferences

3. **"Permission denied" errors**
   - Use `sudo` for system-wide installation
   - Or use virtual environments for user installation

4. **GTK4 related errors**
   - Install GTK4 development libraries
   - Set `GI_TYPELIB_PATH` environment variable if needed

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](../troubleshooting/README.md)
2. Review [Common Issues](../troubleshooting/common-issues.md)
3. Search the [Issue Tracker](https://github.com/gimp-mcp/gimp-mcp-server/issues)
4. Ask in [Discussions](https://github.com/gimp-mcp/gimp-mcp-server/discussions)

## 📚 Next Steps

After successful installation:

1. **Configure the server**: See [Configuration Guide](configuration.md)
2. **Start using the server**: Check [Getting Started](getting-started.md)
3. **Integrate with clients**: Review [Client Integration](client-integration.md)
4. **Explore examples**: Try the [Tutorials](../tutorials/README.md)