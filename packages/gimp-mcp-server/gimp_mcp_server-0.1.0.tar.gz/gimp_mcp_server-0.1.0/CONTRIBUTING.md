# Contributing to GIMP MCP Server

Thank you for your interest in contributing to the GIMP MCP Server! This document provides guidelines and information for contributors.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Release Process](#release-process)

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- GIMP 3.0+ installed with Python support
- Git for version control
- Basic knowledge of Python and image processing concepts

### Areas for Contribution

We welcome contributions in these areas:

1. **Core Features**: New tools, filters, or operations
2. **Documentation**: User guides, API documentation, tutorials
3. **Testing**: Unit tests, integration tests, benchmarks
4. **Bug Fixes**: Resolving issues and improving stability
5. **Performance**: Optimization and efficiency improvements
6. **Platform Support**: Windows, macOS, Linux compatibility
7. **Examples**: Demos and real-world use cases

## 🔧 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/gimp-mcp-server.git
cd gimp-mcp-server

# Add upstream remote
git remote add upstream https://github.com/gimp-mcp/gimp-mcp-server.git
```

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install gimp-3.0 python3-dev python3-pip
sudo apt install libgtk-4-dev libgirepository1.0-dev
```

#### macOS
```bash
brew install gimp python@3.9 gtk4 gobject-introspection
```

#### Windows
See [Windows Installation Guide](docs/user-guide/installation.md#windows-installation)

### 4. Verify Setup

```bash
# Run tests to ensure everything works
pytest

# Test server startup
gimp-mcp-server --test-connection

# Check code formatting
black --check src/
flake8 src/
mypy src/
```

## 🔄 Contributing Process

### 1. Choose an Issue

- Check [Issues](https://github.com/gimp-mcp/gimp-mcp-server/issues) for open tasks
- Look for `good first issue` or `help wanted` labels
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Changes

- Follow our [Code Standards](#code-standards)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new drawing tool for custom shapes

- Implement custom shape drawing functionality
- Add comprehensive tests for shape validation
- Update documentation with usage examples
- Resolves #123"
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## 📝 Code Standards

### Python Code Style

We follow PEP 8 with some modifications:

```python
# Line length: 88 characters (Black default)
# Use Black for formatting
black src/

# Use isort for imports
isort src/

# Type hints required for public functions
def create_document(
    width: int,
    height: int,
    name: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new GIMP document.
    
    Args:
        width: Document width in pixels
        height: Document height in pixels  
        name: Optional document name
        
    Returns:
        Dictionary containing document information
        
    Raises:
        GimpApiError: If document creation fails
    """
```

### Code Quality Tools

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Variables**: `snake_case`

### Error Handling

```python
from gimp_mcp.utils.errors import GimpApiError

def risky_operation():
    try:
        # GIMP operation
        result = gimp.some_operation()
    except Exception as e:
        raise GimpApiError(f"Operation failed: {e}") from e
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_tools.py
│   └── test_api.py
├── integration/          # Integration tests
│   └── test_server.py
├── mocks/               # Mock objects
│   └── mock_gimp.py
└── conftest.py          # Test configuration
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from gimp_mcp.tools.document_tools import create_document

def test_create_document_success():
    """Test successful document creation."""
    with patch('gimp_mcp.gimp_api.gimp') as mock_gimp:
        mock_gimp.Image.new.return_value = Mock(get_id=lambda: 1)
        
        result = create_document(width=800, height=600)
        
        assert result["success"] is True
        assert result["document_id"] == 1
        mock_gimp.Image.new.assert_called_once_with(800, 600, 0)

def test_create_document_invalid_size():
    """Test document creation with invalid size."""
    with pytest.raises(ValueError, match="Width must be positive"):
        create_document(width=-1, height=600)
```

### Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration  
def test_integration_feature():
    pass

@pytest.mark.slow
def test_performance_benchmark():
    pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run with coverage
pytest --cov=gimp_mcp --cov-report=html

# Run tests in parallel
pytest -n auto
```

## 📚 Documentation

### Documentation Types

1. **Code Documentation**: Docstrings for all public functions
2. **User Documentation**: User guides and tutorials
3. **API Documentation**: Complete reference documentation
4. **Development Documentation**: Architecture and development guides

### Docstring Format

```python
def apply_filter(image_id: int, filter_type: str, **kwargs) -> Dict[str, Any]:
    """Apply a filter to an image.

    Args:
        image_id: ID of the target image
        filter_type: Type of filter to apply (blur, sharpen, etc.)
        **kwargs: Filter-specific parameters

    Returns:
        Dictionary containing:
            - success: Boolean indicating success
            - message: Status message
            - filter_applied: Name of applied filter

    Raises:
        GimpApiError: If filter application fails
        ValueError: If filter_type is not supported

    Example:
        >>> result = apply_filter(1, "blur", radius=2.0)
        >>> print(result["success"])
        True
    """
```

### Documentation Updates

- Update relevant documentation when adding features
- Add examples for new tools or functions
- Update API reference documentation
- Add troubleshooting entries for common issues

## 🐛 Issue Guidelines

### Creating Issues

Use our issue templates:

- **Bug Report**: For reporting bugs
- **Feature Request**: For suggesting new features
- **Documentation**: For documentation improvements
- **Performance**: For performance-related issues

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `priority:high`: High priority issues
- `platform:windows`: Windows-specific issues
- `platform:macos`: macOS-specific issues
- `platform:linux`: Linux-specific issues

### Bug Reports

Include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, GIMP version)
- Error messages and stack traces
- Minimal code example if applicable

## 📤 Pull Request Guidelines

### PR Requirements

- [ ] Code follows style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] PR description explains changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

### Review Process

1. **Automated Checks**: GitHub Actions run tests and linting
2. **Code Review**: Maintainers review code quality and design
3. **Testing**: Reviewers test functionality
4. **Documentation**: Check documentation completeness
5. **Approval**: Maintainer approval required for merge

## 📦 Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### Release Preparation

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Create release PR
4. Tag release after merge
5. Publish to PyPI

### Changelog Format

```markdown
## [1.2.0] - 2025-01-15

### Added
- New custom shape drawing tool
- Batch processing improvements
- Windows installation guide

### Changed
- Updated GIMP API wrapper for better performance
- Improved error handling in layer operations

### Fixed
- Fixed memory leak in large image processing
- Resolved Windows path handling issues

### Deprecated
- Old color sampling method (use sample_color instead)
```

## 🆘 Getting Help

### Resources

- **Documentation**: [docs/](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/gimp-mcp/gimp-mcp-server/discussions)
- **Issues**: [GitHub Issues](https://github.com/gimp-mcp/gimp-mcp-server/issues)

### Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and experiences
- Follow our Code of Conduct

### Development Questions

- Use GitHub Discussions for general questions
- Create issues for specific bugs or feature requests
- Join our community chat for real-time discussions

## 🎯 Maintainer Guidelines

### For Project Maintainers

- Review PRs promptly
- Provide constructive feedback
- Help contributors improve their contributions
- Maintain project quality standards
- Keep documentation up to date

### Code Review Checklist

- [ ] Code quality and style
- [ ] Test coverage and quality
- [ ] Documentation completeness
- [ ] Performance considerations
- [ ] Security implications
- [ ] Breaking change impact

Thank you for contributing to GIMP MCP Server! Your contributions help make image editing more accessible and powerful for everyone.