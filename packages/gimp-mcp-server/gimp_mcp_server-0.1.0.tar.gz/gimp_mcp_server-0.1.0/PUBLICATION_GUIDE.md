# GIMP MCP Server Publication Guide

This comprehensive guide provides step-by-step instructions for publishing the GIMP MCP Server to GitHub and PyPI, making it publicly available for the community.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Pre-Publication Checklist](#pre-publication-checklist)
- [GitHub Repository Setup](#github-repository-setup)
- [PyPI Publication Process](#pypi-publication-process)
- [Post-Publication Tasks](#post-publication-tasks)
- [Troubleshooting](#troubleshooting)
- [Maintenance and Updates](#maintenance-and-updates)

## 🛠️ Prerequisites

### Required Accounts
- **GitHub Account**: With repository creation permissions
- **PyPI Account**: For package distribution
- **TestPyPI Account**: For testing package uploads (recommended)

### Required Tools
```bash
# Install publication tools
pip install build twine check-manifest PyGithub requests

# Development tools (if not already installed)
pip install -e ".[dev]"
```

### Required Tokens and Credentials
1. **GitHub Personal Access Token**
   - Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - Create token with `repo`, `workflow`, and `admin:org` permissions

2. **PyPI API Token**
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
   - Create API token for project uploads

3. **TestPyPI API Token** (recommended)
   - Go to [TestPyPI Account Settings](https://test.pypi.org/manage/account/token/)
   - Create API token for testing uploads

### Environment Variables
```bash
# Set up environment variables (optional but recommended)
export GITHUB_TOKEN="your_github_token_here"
export PYPI_API_TOKEN="your_pypi_token_here"
export TEST_PYPI_API_TOKEN="your_test_pypi_token_here"
```

## ✅ Pre-Publication Checklist

### 1. Project Readiness
- [ ] All core functionality implemented and tested
- [ ] Comprehensive test suite with good coverage
- [ ] Documentation complete and up-to-date
- [ ] Code quality tools passing (black, flake8, mypy)
- [ ] All demo projects working correctly

### 2. Version and Metadata
- [ ] Version number updated in `pyproject.toml`
- [ ] `CHANGELOG.md` updated with release notes
- [ ] README.md reflects current features and installation
- [ ] All links in documentation are working
- [ ] License information is correct

### 3. Publication Files
- [ ] `LICENSE` file present (MIT license)
- [ ] `CONTRIBUTING.md` with contribution guidelines
- [ ] `CODE_OF_CONDUCT.md` for community standards
- [ ] `SECURITY.md` for security reporting
- [ ] `MANIFEST.in` for package distribution
- [ ] GitHub Actions workflow configured
- [ ] Issue templates created
- [ ] Pull request template created

### 4. Package Structure
```
gimp-mcp-server/
├── src/gimp_mcp/           # Source code
├── tests/                  # Test suite
├── docs/                   # Documentation
├── demos/                  # Example projects
├── scripts/                # Publication scripts
├── .github/                # GitHub configuration
├── pyproject.toml          # Package configuration
├── README.md               # Project documentation
├── LICENSE                 # License file
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # Contribution guide
├── CODE_OF_CONDUCT.md      # Community standards
├── SECURITY.md             # Security policy
└── MANIFEST.in             # Package manifest
```

## 🐙 GitHub Repository Setup

### Step 1: Create Repository Using Script

```bash
# Navigate to project root
cd gimp-mcp-server

# Create GitHub repository
python scripts/create_github_repo.py --token $GITHUB_TOKEN --org gimp-mcp

# Or for personal repository
python scripts/create_github_repo.py --token $GITHUB_TOKEN
```

### Step 2: Push Code to Repository

```bash
# Add remote (replace with your repository URL)
git remote add origin https://github.com/gimp-mcp/gimp-mcp-server.git

# Ensure main branch
git branch -M main

# Push all content
git push -u origin main

# Push tags if any
git push --tags
```

### Step 3: Configure Repository Settings

1. **Branch Protection**
   - Go to repository Settings > Branches
   - Add protection rule for `main` branch
   - Require status checks (CI tests)
   - Require pull request reviews

2. **Repository Secrets**
   - Go to Settings > Secrets and variables > Actions
   - Add secrets:
     - `PYPI_API_TOKEN`: For PyPI publishing
     - `CODECOV_TOKEN`: For code coverage (optional)

3. **Repository Features**
   - Enable Issues
   - Enable Discussions (recommended)
   - Enable GitHub Pages (for documentation)
   - Configure topics/tags for discoverability

### Step 4: Verify GitHub Actions

```bash
# Check that CI/CD workflow runs successfully
# Monitor at: https://github.com/your-org/gimp-mcp-server/actions

# Ensure all checks pass:
# - Code quality (lint)
# - Security scanning
# - Unit tests
# - Integration tests
# - Package building
```

## 📦 PyPI Publication Process

### Step 1: Prepare Package

```bash
# Clean and prepare package
python scripts/prepare_pypi_package.py --clean --build

# Verify package is ready
python scripts/prepare_pypi_package.py --validate --test-install
```

### Step 2: Test Upload to TestPyPI

```bash
# Upload to TestPyPI first (recommended)
python scripts/publish_to_pypi.py --test --token $TEST_PYPI_API_TOKEN

# Or without token (will prompt for credentials)
python scripts/publish_to_pypi.py --test
```

### Step 3: Verify TestPyPI Upload

```bash
# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ gimp-mcp-server

# Verify package works
gimp-mcp-server --version
python -c "import gimp_mcp; print('Import successful')"
```

### Step 4: Upload to Production PyPI

```bash
# Upload to production PyPI
python scripts/publish_to_pypi.py --prod --token $PYPI_API_TOKEN

# Or without token (will prompt for credentials)
python scripts/publish_to_pypi.py --prod
```

### Step 5: Verify Production Upload

```bash
# Test installation from PyPI
pip install gimp-mcp-server

# Verify package works
gimp-mcp-server --version
```

## 📊 Publication Verification

### Automated Verification Script

```bash
# Create verification script
cat > verify_publication.py << 'EOF'
#!/usr/bin/env python3
"""Verify publication success."""

import requests
import subprocess
import sys

def check_github_repo():
    """Check GitHub repository accessibility."""
    url = "https://github.com/gimp-mcp/gimp-mcp-server"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ GitHub repository is accessible")
            return True
        else:
            print(f"❌ GitHub repository not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking GitHub: {e}")
        return False

def check_pypi_package():
    """Check PyPI package availability."""
    try:
        response = requests.get("https://pypi.org/pypi/gimp-mcp-server/json")
        if response.status_code == 200:
            data = response.json()
            version = data["info"]["version"]
            print(f"✅ PyPI package available (version: {version})")
            return True
        else:
            print(f"❌ PyPI package not found: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking PyPI: {e}")
        return False

def test_installation():
    """Test package installation."""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--dry-run", "gimp-mcp-server"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Package installation test passed")
            return True
        else:
            print("❌ Package installation test failed")
            return False
    except Exception as e:
        print(f"❌ Installation test error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verifying Publication Success")
    print("=" * 40)
    
    checks = [
        check_github_repo(),
        check_pypi_package(),
        test_installation()
    ]
    
    if all(checks):
        print("\n🎉 All publication checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Some publication checks failed")
        sys.exit(1)
EOF

# Run verification
python verify_publication.py
```

## 🚀 Post-Publication Tasks

### 1. Create GitHub Release

```bash
# Tag the release
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Create release on GitHub UI or via API
# Include changelog content in release notes
```

### 2. Update Documentation

- [ ] Update installation instructions in README.md
- [ ] Add PyPI installation badges
- [ ] Update documentation links
- [ ] Create user guides and tutorials

### 3. Community Announcements

- [ ] Announce on relevant forums and communities
- [ ] Share on social media
- [ ] Submit to package indexes and directories
- [ ] Contact potential users and contributors

### 4. Monitoring Setup

```bash
# Set up monitoring for:
# - Package download statistics
# - GitHub repository activity
# - Issue reports and feature requests
# - Security vulnerabilities
```

### 5. Documentation Site (Optional)

```bash
# Set up GitHub Pages for documentation
# Navigate to repository Settings > Pages
# Source: GitHub Actions
# The CI workflow will automatically deploy docs
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. GitHub Repository Creation Failed

**Error**: Authentication failed or repository already exists

**Solutions**:
```bash
# Check token permissions
# Ensure token has 'repo' and 'workflow' permissions

# If repository exists, delete it first or use a different name
python scripts/create_github_repo.py --repo-name gimp-mcp-server-new
```

#### 2. PyPI Upload Failed

**Error**: Package already exists or authentication failed

**Solutions**:
```bash
# Check if version already exists
python -c "import requests; print(requests.get('https://pypi.org/pypi/gimp-mcp-server/json').status_code)"

# Update version in pyproject.toml if needed
# Verify credentials are correct

# Test with TestPyPI first
python scripts/publish_to_pypi.py --test
```

#### 3. Package Import Failed

**Error**: Module not found after installation

**Solutions**:
```bash
# Check package structure
python scripts/prepare_pypi_package.py --analyze

# Verify MANIFEST.in includes all necessary files
check-manifest

# Test in clean environment
python scripts/prepare_pypi_package.py --test-install
```

#### 4. CI/CD Pipeline Failed

**Error**: GitHub Actions workflow failing

**Solutions**:
```bash
# Check workflow logs at:
# https://github.com/your-org/gimp-mcp-server/actions

# Common fixes:
# - Update dependencies in pyproject.toml
# - Fix code quality issues
# - Add missing test data
# - Update workflow permissions
```

### Getting Help

If you encounter issues not covered here:

1. Check the [project issues](https://github.com/gimp-mcp/gimp-mcp-server/issues)
2. Search [PyPI documentation](https://packaging.python.org/)
3. Consult [GitHub documentation](https://docs.github.com/)
4. Ask for help in [GitHub Discussions](https://github.com/gimp-mcp/gimp-mcp-server/discussions)

## 🔄 Maintenance and Updates

### Regular Tasks

#### 1. Dependency Updates
```bash
# Monthly: Update dependencies
pip-audit  # Check for security vulnerabilities
pip list --outdated  # Check for updates

# Update pyproject.toml with new versions
# Test thoroughly before publishing
```

#### 2. Security Monitoring
```bash
# Set up GitHub security alerts
# Monitor CVE databases for dependencies
# Review and respond to security reports
```

#### 3. Version Management
```bash
# Follow semantic versioning (MAJOR.MINOR.PATCH)
# Update CHANGELOG.md with each release
# Tag releases consistently
```

### Release Process

1. **Prepare Release**
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   # Run full test suite
   ```

2. **Create Release**
   ```bash
   # Build and test package
   python scripts/prepare_pypi_package.py --clean --build --test-install
   
   # Upload to TestPyPI first
   python scripts/publish_to_pypi.py --test
   
   # If tests pass, upload to PyPI
   python scripts/publish_to_pypi.py --prod
   ```

3. **Post-Release**
   ```bash
   # Create GitHub release
   # Update documentation
   # Announce to community
   ```

## 📈 Success Metrics

Track these metrics to measure publication success:

- **Downloads**: PyPI download statistics
- **Stars**: GitHub repository stars
- **Issues**: Number and resolution time of issues
- **Contributors**: Number of active contributors
- **Usage**: Community adoption and feedback

## 🎯 Next Steps

After successful publication:

1. **Community Building**
   - Engage with users and contributors
   - Respond to issues and questions
   - Build documentation and tutorials

2. **Feature Development**
   - Roadmap planning
   - Priority-based development
   - User feedback integration

3. **Ecosystem Integration**
   - Integration with other tools
   - Plugin development
   - Third-party compatibility

---

**Congratulations!** You've successfully published the GIMP MCP Server to GitHub and PyPI. The project is now available for the global community to use, contribute to, and benefit from.

For ongoing support and updates, refer to the project documentation and community resources.