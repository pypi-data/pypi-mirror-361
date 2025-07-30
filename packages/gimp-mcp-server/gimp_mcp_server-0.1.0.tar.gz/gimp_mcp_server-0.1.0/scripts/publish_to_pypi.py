#!/usr/bin/env python3
"""
PyPI Publication Script

This script handles the publication of the GIMP MCP Server package to PyPI.
It supports both TestPyPI and production PyPI with safety checks.

Usage:
    python scripts/publish_to_pypi.py [--test] [--prod] [--token TOKEN]

Requirements:
    - twine: pip install twine
    - Package must be built first using prepare_pypi_package.py
"""

import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import requests


class PyPIPublisher:
    """Handles PyPI package publication."""
    
    def __init__(self, project_root: Path):
        """
        Initialize PyPI publisher.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        
        # PyPI endpoints
        self.pypi_urls = {
            "test": {
                "upload": "https://test.pypi.org/legacy/",
                "api": "https://test.pypi.org/pypi/",
                "web": "https://test.pypi.org/project/"
            },
            "prod": {
                "upload": "https://upload.pypi.org/legacy/",
                "api": "https://pypi.org/pypi/",
                "web": "https://pypi.org/project/"
            }
        }
        
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are met for publication."""
        print("🔍 Checking prerequisites...")
        
        # Check if twine is installed
        try:
            subprocess.run([sys.executable, "-m", "twine", "--version"], 
                         capture_output=True, check=True)
            print("✅ Twine is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Twine not found. Install with: pip install twine")
            return False
            
        # Check if dist directory exists
        if not self.dist_dir.exists():
            print("❌ No dist directory found. Run prepare_pypi_package.py first")
            return False
            
        # Check for distribution files
        dist_files = list(self.dist_dir.glob("*"))
        if not dist_files:
            print("❌ No distribution files found in dist/")
            return False
            
        # Check for both wheel and source distribution
        has_wheel = bool(list(self.dist_dir.glob("*.whl")))
        has_source = bool(list(self.dist_dir.glob("*.tar.gz")))
        
        if not has_wheel:
            print("❌ No wheel distribution found")
            return False
            
        if not has_source:
            print("❌ No source distribution found") 
            return False
            
        print(f"✅ Found {len(dist_files)} distribution files")
        return True
        
    def get_package_info(self) -> Dict[str, Any]:
        """Get package information from pyproject.toml."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                print("❌ tomllib/tomli not available")
                return {}
        
        pyproject_path = self.project_root / "pyproject.toml"
        
        try:
            with open(pyproject_path, "rb") as f:
                config = tomllib.load(f)
                
            project = config.get("project", {})
            return {
                "name": project.get("name", "unknown"),
                "version": project.get("version", "unknown"),
                "description": project.get("description", ""),
            }
        except Exception as e:
            print(f"❌ Failed to read package info: {e}")
            return {}
            
    def check_existing_version(self, package_name: str, version: str, 
                             target: str = "prod") -> bool:
        """
        Check if version already exists on PyPI.
        
        Args:
            package_name: Package name
            version: Version to check
            target: 'test' or 'prod'
            
        Returns:
            True if version exists, False otherwise
        """
        api_url = self.pypi_urls[target]["api"]
        
        try:
            response = requests.get(f"{api_url}{package_name}/json", timeout=10)
            if response.status_code == 404:
                # Package doesn't exist yet
                return False
            elif response.status_code == 200:
                data = response.json()
                releases = data.get("releases", {})
                return version in releases
            else:
                print(f"⚠️  Could not check existing versions: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️  Could not check existing versions: {e}")
            return False
            
    def validate_distributions(self) -> bool:
        """Validate distributions before upload."""
        print("🔍 Validating distributions...")
        
        dist_files = list(self.dist_dir.glob("*"))
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "twine", "check"] + [str(f) for f in dist_files],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ All distributions are valid")
                return True
            else:
                print("❌ Distribution validation failed:")
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
            
    def get_credentials(self, target: str) -> Dict[str, str]:
        """
        Get PyPI credentials.
        
        Args:
            target: 'test' or 'prod'
            
        Returns:
            Dictionary with username and password/token
        """
        print(f"🔐 Getting credentials for {'TestPyPI' if target == 'test' else 'PyPI'}...")
        
        # Check for API token in environment
        token_env_var = "PYPI_API_TOKEN" if target == "prod" else "TEST_PYPI_API_TOKEN"
        token = os.getenv(token_env_var)
        
        if token:
            print("✅ Using API token from environment")
            return {"username": "__token__", "password": token}
            
        # Check for token in .pypirc
        pypirc_path = Path.home() / ".pypirc"
        if pypirc_path.exists():
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(pypirc_path)
                
                section = "testpypi" if target == "test" else "pypi"
                if section in config:
                    username = config[section].get("username", "__token__")
                    password = config[section].get("password")
                    if password:
                        print("✅ Using credentials from .pypirc")
                        return {"username": username, "password": password}
            except Exception:
                pass
                
        # Prompt for credentials
        print("📝 Please enter your PyPI credentials:")
        username = input("Username (or '__token__' for API token): ").strip()
        password = getpass.getpass("Password/Token: ")
        
        return {"username": username, "password": password}
        
    def upload_to_pypi(self, target: str, token: Optional[str] = None) -> bool:
        """
        Upload package to PyPI.
        
        Args:
            target: 'test' or 'prod'
            token: Optional API token
            
        Returns:
            True if upload succeeded, False otherwise
        """
        repository_url = self.pypi_urls[target]["upload"]
        dist_files = list(self.dist_dir.glob("*"))
        
        print(f"📤 Uploading to {'TestPyPI' if target == 'test' else 'PyPI'}...")
        
        # Prepare upload command
        cmd = [
            sys.executable, "-m", "twine", "upload",
            "--repository-url", repository_url,
            "--verbose"
        ]
        
        # Add credentials
        if token:
            cmd.extend(["--username", "__token__", "--password", token])
        else:
            credentials = self.get_credentials(target)
            cmd.extend(["--username", credentials["username"]])
            cmd.extend(["--password", credentials["password"]])
            
        # Add distribution files
        cmd.extend([str(f) for f in dist_files])
        
        try:
            # Run upload (don't capture output so user can see progress)
            result = subprocess.run(cmd, cwd=self.project_root)
            
            if result.returncode == 0:
                print(f"✅ Successfully uploaded to {'TestPyPI' if target == 'test' else 'PyPI'}")
                return True
            else:
                print(f"❌ Upload to {'TestPyPI' if target == 'test' else 'PyPI'} failed")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
            
    def verify_upload(self, package_name: str, version: str, target: str) -> bool:
        """
        Verify that the package was uploaded successfully.
        
        Args:
            package_name: Package name
            version: Package version
            target: 'test' or 'prod'
            
        Returns:
            True if package is available, False otherwise
        """
        print(f"🔍 Verifying upload to {'TestPyPI' if target == 'test' else 'PyPI'}...")
        
        api_url = self.pypi_urls[target]["api"]
        
        try:
            # Wait a moment for indexing
            import time
            time.sleep(5)
            
            response = requests.get(f"{api_url}{package_name}/{version}/json", timeout=30)
            
            if response.status_code == 200:
                print("✅ Package is available and accessible")
                return True
            else:
                print(f"❌ Package not found: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️  Could not verify upload: {e}")
            return False
            
    def test_installation(self, package_name: str, version: str, target: str) -> bool:
        """
        Test package installation from PyPI.
        
        Args:
            package_name: Package name
            version: Package version
            target: 'test' or 'prod'
            
        Returns:
            True if installation succeeded, False otherwise
        """
        print(f"🧪 Testing installation from {'TestPyPI' if target == 'test' else 'PyPI'}...")
        
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_venv = Path(temp_dir) / "test_env"
            
            try:
                # Create virtual environment
                subprocess.run(
                    [sys.executable, "-m", "venv", str(temp_venv)],
                    check=True,
                    capture_output=True
                )
                
                # Get python executable in venv
                if sys.platform == "win32":
                    python_exe = temp_venv / "Scripts" / "python.exe"
                else:
                    python_exe = temp_venv / "bin" / "python"
                
                # Install from PyPI
                install_cmd = [str(python_exe), "-m", "pip", "install"]
                
                if target == "test":
                    install_cmd.extend([
                        "--index-url", "https://test.pypi.org/simple/",
                        "--extra-index-url", "https://pypi.org/simple/"
                    ])
                    
                install_cmd.append(f"{package_name}=={version}")
                
                result = subprocess.run(install_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Package installed successfully")
                    
                    # Test import
                    import_result = subprocess.run(
                        [str(python_exe), "-c", f"import {package_name.replace('-', '_')}; print('Import successful')"],
                        capture_output=True,
                        text=True
                    )
                    
                    if import_result.returncode == 0:
                        print("✅ Package imports successfully")
                        return True
                    else:
                        print("❌ Package import failed:")
                        print(import_result.stderr)
                        return False
                else:
                    print("❌ Package installation failed:")
                    print(result.stderr)
                    return False
                    
            except Exception as e:
                print(f"❌ Installation test failed: {e}")
                return False
                
    def print_success_message(self, package_name: str, version: str, target: str):
        """Print success message with next steps."""
        web_url = self.pypi_urls[target]["web"]
        
        print("\n" + "="*60)
        print("🎉 PUBLICATION SUCCESSFUL!")
        print("="*60)
        
        print(f"📦 Package: {package_name}")
        print(f"🏷️  Version: {version}")
        print(f"🌐 Repository: {'TestPyPI' if target == 'test' else 'PyPI'}")
        print(f"🔗 URL: {web_url}{package_name}/")
        
        print("\n📋 NEXT STEPS:")
        
        if target == "test":
            print("1. Verify the package on TestPyPI:")
            print(f"   {web_url}{package_name}/")
            print("\n2. Test installation:")
            print(f"   pip install --index-url https://test.pypi.org/simple/ {package_name}")
            print("\n3. If everything looks good, publish to production PyPI:")
            print("   python scripts/publish_to_pypi.py --prod")
        else:
            print("1. Verify the package on PyPI:")
            print(f"   {web_url}{package_name}/")
            print("\n2. Test installation:")
            print(f"   pip install {package_name}")
            print("\n3. Update documentation with installation instructions")
            print("\n4. Announce the release:")
            print("   - GitHub release notes")
            print("   - Community announcements")
            print("   - Update project documentation")
            
        print("\n5. Monitor for issues and user feedback")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Publish GIMP MCP Server package to PyPI"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Upload to TestPyPI"
    )
    parser.add_argument(
        "--prod",
        action="store_true", 
        help="Upload to production PyPI"
    )
    parser.add_argument(
        "--token",
        help="API token for authentication"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip safety checks (not recommended)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without uploading"
    )
    
    args = parser.parse_args()
    
    # Default to test if neither specified
    if not args.test and not args.prod:
        args.test = True
        
    target = "prod" if args.prod else "test"
    
    print("📤 PyPI Publication Script")
    print("==========================")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No uploads will be performed")
        
    print(f"🎯 Target: {'Production PyPI' if target == 'prod' else 'TestPyPI'}")
    
    # Initialize publisher
    project_root = Path.cwd()
    publisher = PyPIPublisher(project_root)
    
    # Check prerequisites
    if not publisher.check_prerequisites():
        sys.exit(1)
        
    # Get package info
    package_info = publisher.get_package_info()
    if not package_info:
        sys.exit(1)
        
    package_name = package_info["name"]
    version = package_info["version"]
    
    print(f"📦 Package: {package_name} v{version}")
    
    # Safety checks
    if not args.skip_checks:
        # Check if version already exists
        if publisher.check_existing_version(package_name, version, target):
            print(f"❌ Version {version} already exists on {'PyPI' if target == 'prod' else 'TestPyPI'}")
            print("   Consider updating the version number")
            sys.exit(1)
            
        # Validate distributions
        if not publisher.validate_distributions():
            sys.exit(1)
            
        # Confirmation for production
        if target == "prod":
            response = input(f"\n⚠️  You are about to publish {package_name} v{version} to PRODUCTION PyPI.\n"
                           "This action cannot be undone. Continue? (yes/no): ")
            if response.lower() != "yes":
                print("❌ Publication cancelled")
                sys.exit(1)
                
    if args.dry_run:
        print("\n📋 DRY RUN SUMMARY:")
        print(f"   Would upload {package_name} v{version}")
        print(f"   Target: {'Production PyPI' if target == 'prod' else 'TestPyPI'}")
        distributions = list(publisher.dist_dir.glob("*"))
        print(f"   Distributions: {', '.join(d.name for d in distributions)}")
        return
        
    # Upload to PyPI
    if not publisher.upload_to_pypi(target, args.token):
        sys.exit(1)
        
    # Verify upload
    if publisher.verify_upload(package_name, version, target):
        # Test installation
        publisher.test_installation(package_name, version, target)
        
    # Print success message
    publisher.print_success_message(package_name, version, target)


if __name__ == "__main__":
    main()