# Development Guide

Comprehensive guide for developers working on or extending the GIMP MCP Server.

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Contribution Workflow](#contribution-workflow)
- [Debugging and Profiling](#debugging-and-profiling)
- [Release Process](#release-process)
- [Community Guidelines](#community-guidelines)

## 🛠️ Development Setup

### Prerequisites

1. **System Requirements**:
   - Python 3.9+
   - GIMP 3.0+ with Python support
   - Git
   - PyGObject development libraries

2. **Development Tools**:
   - Code editor/IDE (VS Code recommended)
   - Python virtual environment manager
   - Docker (optional, for containerized development)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/gimp-mcp/gimp-mcp-server.git
cd gimp-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Verify installation
pytest --version
black --version
mypy --version
```

### IDE Configuration

#### VS Code Setup

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "python.sortImports.args": ["--profile", "black"],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests",
    "--verbose"
  ],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    ".mypy_cache": true
  }
}
```

#### PyCharm Setup

1. Open project in PyCharm
2. Configure Python interpreter: `File → Settings → Project → Python Interpreter`
3. Select the virtual environment interpreter
4. Enable code style: `File → Settings → Editor → Code Style → Python`
5. Set line length to 88
6. Configure pytest as test runner

## 📁 Project Structure

### Directory Layout

```
gimp-mcp-server/
├── src/gimp_mcp/           # Main package
│   ├── __init__.py
│   ├── server.py           # FastMCP server implementation
│   ├── gimp_api.py         # GIMP API wrapper
│   ├── mode_manager.py     # GUI/headless mode management
│   ├── tools/              # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── document_tools.py
│   │   ├── layer_tools.py
│   │   ├── drawing_tools.py
│   │   ├── selection_tools.py
│   │   ├── color_tools.py
│   │   └── filter_tools.py
│   ├── resources/          # MCP resource providers
│   │   ├── __init__.py
│   │   └── providers.py
│   └── utils/              # Utility modules
│       ├── __init__.py
│       ├── errors.py
│       ├── gi_helpers.py
│       ├── image_utils.py
│       └── logging.py
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── requirements.txt
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── mocks/              # Mock implementations
│   └── validation/         # Protocol validation
├── docs/                   # Documentation
├── scripts/                # Development scripts
├── pyproject.toml          # Project configuration
├── requirements.txt        # Runtime dependencies
├── pytest.ini             # Test configuration
└── .pre-commit-config.yaml # Pre-commit hooks
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `server.py` | FastMCP server setup and configuration |
| `gimp_api.py` | Low-level GIMP API wrapper and connection management |
| `mode_manager.py` | GUI/headless mode detection and management |
| `tools/` | MCP tool implementations for different categories |
| `resources/` | MCP resource providers for real-time state |
| `utils/` | Shared utilities, helpers, and error handling |

## 📝 Code Standards

### Python Code Style

We follow [PEP 8](https://peps.python.org/pep-0008/) with these specific guidelines:

```python
# Line length: 88 characters (Black default)
# String quotes: Double quotes preferred
# Import order: isort with black profile

# Good example
async def create_document(
    self,
    width: int = 1920,
    height: int = 1080,
    resolution: float = 300.0,
    color_mode: str = "RGB",
    fill_type: str = "transparent"
) -> Dict[str, Any]:
    """
    Create a new GIMP document.
    
    Args:
        width: Document width in pixels
        height: Document height in pixels
        resolution: Resolution in DPI
        color_mode: Color mode ("RGB", "GRAYSCALE", "INDEXED")
        fill_type: Initial fill type
        
    Returns:
        Dictionary containing document creation result
        
    Raises:
        GimpConnectionError: If GIMP is not accessible
        GimpOperationError: If document creation fails
    """
    try:
        with self.gimp_api.ensure_connection() as gimp:
            # Implementation here
            pass
    except Exception as e:
        logger.error("Document creation failed", error=str(e))
        raise GimpOperationError(f"Failed to create document: {e}")
```

### Documentation Standards

All public functions and classes must have docstrings:

```python
class DocumentTools:
    """
    Document management operations for GIMP MCP server.
    
    This class provides MCP tools for creating, opening, saving, and
    exporting GIMP documents. All operations are performed through
    the GIMP API wrapper with proper error handling.
    
    Attributes:
        gimp_api: Instance of GimpAPI for GIMP operations
        
    Example:
        >>> tools = DocumentTools(gimp_api)
        >>> result = await tools.create_document(width=800, height=600)
    """
    
    @safe_operation("create_document")
    async def create_document(self, **kwargs) -> Dict[str, Any]:
        """
        Create a new GIMP document.
        
        Creates a new document with the specified dimensions and properties.
        The document becomes the active document in GIMP.
        
        Args:
            width: Document width in pixels (default: 1920)
            height: Document height in pixels (default: 1080)
            resolution: Resolution in DPI (default: 300.0)
            color_mode: Color mode - "RGB", "GRAYSCALE", or "INDEXED" (default: "RGB")
            fill_type: Initial fill - "transparent", "white", "black", 
                      "foreground", or "background" (default: "transparent")
            name: Document name (default: "Untitled")
            
        Returns:
            Dict containing:
                - success (bool): Operation success status
                - data (dict): Document information if successful
                    - document_id (int): GIMP document ID
                    - name (str): Document name
                    - width (int): Document width
                    - height (int): Document height
                    - resolution (float): Document resolution
                    - mode (str): Color mode
                    - layer_id (int): ID of initial layer
                - error (str): Error message if failed
                - operation (str): Operation name
                - timestamp (float): Operation timestamp
                
        Raises:
            GimpConnectionError: If GIMP is not accessible
            GimpOperationError: If document creation fails
            GimpValidationError: If parameters are invalid
            
        Example:
            >>> result = await tools.create_document(
            ...     width=1024, 
            ...     height=768,
            ...     name="My Project"
            ... )
            >>> if result["success"]:
            ...     doc_id = result["data"]["document_id"]
        """
```

### Type Hints

Use comprehensive type hints:

```python
from typing import Dict, List, Optional, Union, Tuple, Any, AsyncGenerator

# Function signatures
async def apply_brush_stroke(
    self,
    points: List[Tuple[float, float]],
    brush_name: str = "2. Hardness 050",
    size: float = 10.0,
    opacity: float = 100.0,
    color: Optional[str] = None,
    layer_id: Optional[int] = None,
    document_id: Optional[int] = None
) -> Dict[str, Any]:

# Class attributes
class GimpAPI:
    mode_manager: GimpModeManager
    _gimp: Optional[Any]
    _last_health_check: float
    _connection_verified: bool
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_gimp_api.py
│   ├── test_document_tools.py
│   ├── test_layer_tools.py
│   └── test_resource_providers.py
├── integration/             # Integration tests
│   ├── test_server_integration.py
│   └── test_gimp_integration.py
├── mocks/                   # Mock implementations
│   ├── mock_gimp.py
│   ├── mock_mcp_client.py
│   └── test_fixtures.py
└── validation/              # Protocol validation
    └── mcp_protocol_validator.py
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from gimp_mcp.tools.document_tools import DocumentTools
from gimp_mcp.utils.errors import GimpConnectionError

class TestDocumentTools:
    """Test suite for DocumentTools class."""
    
    @pytest.fixture
    def mock_gimp_api(self):
        """Create a mock GIMP API instance."""
        api = Mock()
        api.ensure_connection = Mock()
        api.create_image = AsyncMock()
        return api
    
    @pytest.fixture
    def document_tools(self, mock_gimp_api):
        """Create DocumentTools instance with mocked API."""
        return DocumentTools(mock_gimp_api)
    
    @pytest.mark.asyncio
    async def test_create_document_success(self, document_tools, mock_gimp_api):
        """Test successful document creation."""
        # Arrange
        expected_doc_id = 42
        mock_gimp_api.create_image.return_value = {
            "id": expected_doc_id,
            "width": 800,
            "height": 600
        }
        
        # Act
        result = await document_tools.create_document(width=800, height=600)
        
        # Assert
        assert result["success"] is True
        assert result["data"]["document_id"] == expected_doc_id
        assert result["data"]["width"] == 800
        assert result["data"]["height"] == 600
        
        # Verify API calls
        mock_gimp_api.create_image.assert_called_once_with(
            width=800,
            height=600,
            resolution=300.0,
            color_mode="RGB",
            fill_type="transparent"
        )
    
    @pytest.mark.asyncio
    async def test_create_document_connection_error(self, document_tools, mock_gimp_api):
        """Test document creation with connection error."""
        # Arrange
        mock_gimp_api.create_image.side_effect = GimpConnectionError("GIMP not found")
        
        # Act
        result = await document_tools.create_document()
        
        # Assert
        assert result["success"] is False
        assert "GIMP not found" in result["error"]
        assert result["operation"] == "create_document"
    
    @pytest.mark.parametrize("width,height,expected_error", [
        (0, 100, "width must be positive"),
        (100, 0, "height must be positive"),
        (-1, 100, "width must be positive"),
        (100, -1, "height must be positive"),
    ])
    @pytest.mark.asyncio
    async def test_create_document_invalid_parameters(
        self, 
        document_tools, 
        width, 
        height, 
        expected_error
    ):
        """Test document creation with invalid parameters."""
        result = await document_tools.create_document(width=width, height=height)
        
        assert result["success"] is False
        assert expected_error in result["error"].lower()
```

#### Integration Tests

```python
import pytest
import asyncio
from gimp_mcp.server import create_server
from mcp_client import MCPClient

@pytest.mark.integration
class TestServerIntegration:
    """Integration tests for the MCP server."""
    
    @pytest.fixture
    async def server(self):
        """Start a test server instance."""
        server = await create_server(port=3001, debug=True)
        yield server
        await server.close()
    
    @pytest.fixture
    async def client(self, server):
        """Create an MCP client connected to test server."""
        client = MCPClient()
        await client.connect("http://localhost:3001")
        yield client
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, client):
        """Test a complete image editing workflow."""
        # Create document
        doc_result = await client.call_tool("create_document", {
            "width": 512,
            "height": 512,
            "name": "Test Document"
        })
        assert doc_result["success"] is True
        doc_id = doc_result["data"]["document_id"]
        
        # Create layer
        layer_result = await client.call_tool("create_layer", {
            "document_id": doc_id,
            "name": "Test Layer"
        })
        assert layer_result["success"] is True
        layer_id = layer_result["data"]["layer_id"]
        
        # Draw rectangle
        draw_result = await client.call_tool("draw_rectangle", {
            "document_id": doc_id,
            "layer_id": layer_id,
            "x": 100,
            "y": 100,
            "width": 200,
            "height": 150,
            "fill_color": "#FF0000"
        })
        assert draw_result["success"] is True
        
        # Verify document state
        doc_state = await client.get_resource("document://current")
        assert doc_state["content"]["document_id"] == doc_id
        assert doc_state["content"]["layer_count"] >= 2  # Background + test layer
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run with coverage
pytest --cov=gimp_mcp --cov-report=html

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_document_tools.py

# Run specific test
pytest tests/unit/test_document_tools.py::TestDocumentTools::test_create_document_success

# Run tests in parallel
pytest -n auto  # Requires pytest-xdist
```

### Mock Guidelines

Create comprehensive mocks for external dependencies:

```python
# tests/mocks/mock_gimp.py
class MockGimpImage:
    """Mock GIMP image object."""
    
    def __init__(self, width=1920, height=1080, image_id=1):
        self.width = width
        self.height = height
        self.id = image_id
        self.layers = []
        self.name = f"Untitled-{image_id}"
    
    def add_layer(self, layer):
        self.layers.append(layer)
        return layer
    
    def get_layer_by_id(self, layer_id):
        return next((l for l in self.layers if l.id == layer_id), None)

class MockGimpAPI:
    """Mock GIMP API for testing."""
    
    def __init__(self):
        self.images = {}
        self.next_image_id = 1
        self.next_layer_id = 1
        self.active_image_id = None
    
    async def create_image(self, width, height, **kwargs):
        image_id = self.next_image_id
        self.next_image_id += 1
        
        image = MockGimpImage(width, height, image_id)
        self.images[image_id] = image
        self.active_image_id = image_id
        
        return {
            "id": image_id,
            "width": width,
            "height": height,
            "name": image.name
        }
    
    async def get_active_image(self):
        if self.active_image_id:
            return {"id": self.active_image_id}
        return None
```

## 🔄 Contribution Workflow

### Git Workflow

We use GitHub Flow with these guidelines:

1. **Create feature branch**:
   ```bash
   git checkout -b feature/add-filter-tools
   ```

2. **Make changes with clear commits**:
   ```bash
   git add .
   git commit -m "feat: add blur and sharpen filter tools
   
   - Add blur tool with radius and method options
   - Add sharpen tool with amount and threshold
   - Include comprehensive tests for both tools
   - Update API documentation"
   ```

3. **Keep branch updated**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Run tests and checks**:
   ```bash
   pre-commit run --all-files
   pytest
   ```

5. **Create pull request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots for UI changes
   - Test results

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(tools): add batch processing support

fix(gimp-api): handle connection timeout errors

docs(api): update drawing tools documentation

test(integration): add end-to-end workflow tests

refactor(utils): simplify error handling logic
```

### Code Review Process

1. **Self-review checklist**:
   - [ ] Code follows style guidelines
   - [ ] Tests are included and passing
   - [ ] Documentation is updated
   - [ ] No debug code or comments
   - [ ] Error handling is comprehensive

2. **Reviewer guidelines**:
   - Focus on logic, design, and maintainability
   - Check for proper error handling
   - Verify test coverage
   - Ensure documentation accuracy
   - Consider performance implications

3. **Required approvals**:
   - At least one core maintainer approval
   - All CI checks must pass
   - No merge conflicts

## 🐛 Debugging and Profiling

### Debug Mode

Enable comprehensive debugging:

```bash
# Environment variables
export GIMP_MCP_DEBUG=1
export GIMP_MCP_LOG_LEVEL=DEBUG
export GIMP_MCP_TRACE_TOOLS=1

# Start server with debugging
gimp-mcp-server --debug --verbose
```

### Logging Configuration

```python
# Development logging setup
import logging
import structlog

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Structured logging
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Usage in code
logger.info("Tool execution started", tool="create_document", params=params)
```

### Performance Profiling

```python
# Profile tool execution
import cProfile
import pstats
from functools import wraps

def profile_tool(func):
    """Decorator to profile tool execution."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            pr.disable()
            stats = pstats.Stats(pr)
            stats.sort_stats('cumulative')
            stats.print_stats(10)  # Top 10 functions
    
    return wrapper

# Memory profiling
from memory_profiler import profile

@profile
async def memory_intensive_operation():
    # Your code here
    pass
```

### Testing with GIMP

```bash
# Test GIMP integration manually
python -c "
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
print('GIMP API accessible:', hasattr(Gimp, 'Image'))
"

# Test server startup
gimp-mcp-server --test-mode --exit-after-test
```

## 📦 Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking API changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

### Release Checklist

1. **Pre-release**:
   - [ ] Update version in `pyproject.toml`
   - [ ] Update `CHANGELOG.md`
   - [ ] Run full test suite
   - [ ] Update documentation
   - [ ] Test installation from source

2. **Release**:
   - [ ] Create release branch
   - [ ] Tag version: `git tag v1.0.0`
   - [ ] Build distribution: `python -m build`
   - [ ] Test package: `twine check dist/*`
   - [ ] Upload to PyPI: `twine upload dist/*`

3. **Post-release**:
   - [ ] Create GitHub release
   - [ ] Update documentation site
   - [ ] Announce on community channels

### Automated Release

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

## 🤝 Community Guidelines

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Discord/Slack**: Real-time development chat
- **Weekly meetings**: Core contributor sync

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/):

1. **Be respectful** and inclusive
2. **Be constructive** in feedback
3. **Be patient** with new contributors
4. **Be collaborative** in problem-solving

### Mentoring

- New contributors are paired with experienced mentors
- Regular code review sessions for learning
- Documentation contributions are encouraged
- "Good first issue" labels for newcomers

## 📚 Additional Resources

- [Architecture Guide](../architecture/README.md) - Technical deep-dive
- [API Reference](../api-reference/README.md) - Complete API documentation
- [Extension Guide](../extension/README.md) - Adding new features
- [Testing Guide](testing.md) - Detailed testing procedures

## 🔗 External References

- [FastMCP Documentation](https://fastmcp.readthedocs.io/)
- [GIMP Python Documentation](https://www.gimp.org/docs/python/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/docs)
- [PyGObject Documentation](https://pygobject.readthedocs.io/)