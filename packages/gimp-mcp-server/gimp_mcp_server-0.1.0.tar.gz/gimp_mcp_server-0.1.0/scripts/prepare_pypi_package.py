#!/usr/bin/env python3
"""
PyPI Package Preparation Script

This script prepares the GIMP MCP Server package for PyPI publication.
It validates the package, builds distributions, and performs pre-publication checks.

Usage:
    python scripts/prepare_pypi_package.py [--build] [--validate] [--clean]

Requirements:
    - build: pip install build
    - twine: pip install twine
    - check-manifest: pip install check-manifest
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import tempfile
import zipfile
import tarfile


class PyPIPackagePreparator:
    """Handles PyPI package preparation and validation."""
    
    def __init__(self, project_root: Path):
        """
        Initialize package preparator.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"
        
    def check_dependencies(self) -> bool:
        """Check if required tools are installed."""
        required_tools = ["build", "twine", "check-manifest"]
        missing_tools = []
        
        for tool in required_tools:
            try:
                subprocess.run([sys.executable, "-m", tool, "--help"], 
                             capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"❌ Missing required tools: {', '.join(missing_tools)}")
            print("Install with:")
            for tool in missing_tools:
                print(f"  pip install {tool}")
            return False
            
        print("✅ All required tools are installed")
        return True
        
    def validate_project_structure(self) -> bool:
        """Validate project structure for PyPI publication."""
        print("🔍 Validating project structure...")
        
        required_files = [
            "pyproject.toml",
            "README.md", 
            "LICENSE",
            "CHANGELOG.md",
            "src/gimp_mcp/__init__.py",
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
            
        print("✅ Project structure is valid")
        return True
        
    def validate_pyproject_toml(self) -> bool:
        """Validate pyproject.toml configuration."""
        print("🔍 Validating pyproject.toml...")
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                print("❌ tomllib/tomli not available")
                return False
        
        pyproject_path = self.project_root / "pyproject.toml"
        
        try:
            with open(pyproject_path, "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            print(f"❌ Failed to parse pyproject.toml: {e}")
            return False
            
        # Check required fields
        project = config.get("project", {})
        required_fields = ["name", "version", "description", "authors", "license"]
        
        missing_fields = []
        for field in required_fields:
            if field not in project:
                missing_fields.append(field)
                
        if missing_fields:
            print(f"❌ Missing required fields in [project]: {', '.join(missing_fields)}")
            return False
            
        # Validate version format
        version = project["version"]
        import re
        if not re.match(r'^\d+\.\d+\.\d+', version):
            print(f"❌ Invalid version format: {version}")
            print("   Expected format: X.Y.Z (semantic versioning)")
            return False
            
        print(f"✅ pyproject.toml is valid (version: {version})")
        return True
        
    def check_manifest(self) -> bool:
        """Check MANIFEST.in completeness."""
        print("🔍 Checking MANIFEST.in...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "check_manifest"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ MANIFEST.in is complete")
                return True
            else:
                print("❌ MANIFEST.in issues found:")
                print(result.stdout)
                return False
                
        except Exception as e:
            print(f"❌ Failed to check manifest: {e}")
            return False
            
    def clean_build_artifacts(self):
        """Clean existing build artifacts."""
        print("🧹 Cleaning build artifacts...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  ✅ Cleaned {dir_path}")
                
        # Clean egg-info directories
        for egg_info in self.project_root.glob("**/*.egg-info"):
            if egg_info.is_dir():
                shutil.rmtree(egg_info)
                print(f"  ✅ Cleaned {egg_info}")
                
    def build_package(self) -> bool:
        """Build source and wheel distributions."""
        print("🔨 Building package distributions...")
        
        try:
            # Build both source and wheel distributions
            result = subprocess.run(
                [sys.executable, "-m", "build"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Package built successfully")
                
                # List built files
                if self.dist_dir.exists():
                    built_files = list(self.dist_dir.glob("*"))
                    print("📦 Built distributions:")
                    for file_path in built_files:
                        print(f"  - {file_path.name}")
                        
                return True
            else:
                print("❌ Package build failed:")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
            
    def validate_distributions(self) -> bool:
        """Validate built distributions."""
        print("🔍 Validating distributions...")
        
        if not self.dist_dir.exists():
            print("❌ No dist directory found")
            return False
            
        dist_files = list(self.dist_dir.glob("*"))
        if not dist_files:
            print("❌ No distribution files found")
            return False
            
        # Check with twine
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
            
    def test_install(self) -> bool:
        """Test package installation in temporary environment."""
        print("🧪 Testing package installation...")
        
        if not self.dist_dir.exists():
            print("❌ No distributions to test")
            return False
            
        # Find wheel file
        wheel_files = list(self.dist_dir.glob("*.whl"))
        if not wheel_files:
            print("❌ No wheel file found for testing")
            return False
            
        wheel_file = wheel_files[0]
        
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
                
                # Install wheel
                subprocess.run(
                    [str(python_exe), "-m", "pip", "install", str(wheel_file)],
                    check=True,
                    capture_output=True
                )
                
                # Test import
                result = subprocess.run(
                    [str(python_exe), "-c", "import gimp_mcp; print('Import successful')"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print("✅ Package installs and imports successfully")
                    return True
                else:
                    print("❌ Package import failed:")
                    print(result.stderr)
                    return False
                    
            except subprocess.CalledProcessError as e:
                print(f"❌ Installation test failed: {e}")
                return False
                
    def analyze_package_contents(self):
        """Analyze and display package contents."""
        print("📋 Analyzing package contents...")
        
        if not self.dist_dir.exists():
            print("❌ No distributions to analyze")
            return
            
        for dist_file in self.dist_dir.glob("*"):
            print(f"\n📦 {dist_file.name}:")
            
            if dist_file.suffix == ".whl":
                self._analyze_wheel(dist_file)
            elif dist_file.suffix == ".gz":
                self._analyze_tarball(dist_file)
                
    def _analyze_wheel(self, wheel_path: Path):
        """Analyze wheel file contents."""
        try:
            with zipfile.ZipFile(wheel_path, 'r') as zf:
                files = zf.namelist()
                print(f"  📁 Contains {len(files)} files")
                
                # Show directory structure
                dirs = set()
                for file_path in files:
                    parts = file_path.split('/')
                    if len(parts) > 1:
                        dirs.add(parts[0])
                        
                print(f"  📂 Top-level directories: {', '.join(sorted(dirs))}")
                
        except Exception as e:
            print(f"  ❌ Error analyzing wheel: {e}")
            
    def _analyze_tarball(self, tar_path: Path):
        """Analyze source tarball contents."""
        try:
            with tarfile.open(tar_path, 'r:gz') as tf:
                files = tf.getnames()
                print(f"  📁 Contains {len(files)} files")
                
                # Show directory structure
                dirs = set()
                for file_path in files:
                    parts = file_path.split('/')
                    if len(parts) > 1:
                        dirs.add(parts[1] if len(parts) > 1 else parts[0])
                        
                print(f"  📂 Top-level directories: {', '.join(sorted(dirs))}")
                
        except Exception as e:
            print(f"  ❌ Error analyzing tarball: {e}")
            
    def generate_summary_report(self) -> dict:
        """Generate package preparation summary."""
        print("\n" + "="*60)
        print("📊 PACKAGE PREPARATION SUMMARY")
        print("="*60)
        
        summary = {
            "project_root": str(self.project_root),
            "distributions": [],
            "ready_for_publication": False
        }
        
        if self.dist_dir.exists():
            dist_files = list(self.dist_dir.glob("*"))
            summary["distributions"] = [f.name for f in dist_files]
            
            print(f"📦 Built distributions ({len(dist_files)}):")
            for dist_file in dist_files:
                size_mb = dist_file.stat().st_size / (1024 * 1024)
                print(f"  - {dist_file.name} ({size_mb:.2f} MB)")
                
        # Check if ready for publication
        required_files = ["*.whl", "*.tar.gz"]
        has_wheel = bool(list(self.dist_dir.glob("*.whl")))
        has_source = bool(list(self.dist_dir.glob("*.tar.gz")))
        
        if has_wheel and has_source:
            summary["ready_for_publication"] = True
            print("\n✅ READY FOR PUBLICATION!")
            print("📋 Next steps:")
            print("   1. Review distributions in ./dist/")
            print("   2. Test upload to TestPyPI first")
            print("   3. Upload to PyPI using publish script")
        else:
            print("\n❌ NOT READY FOR PUBLICATION")
            if not has_wheel:
                print("   - Missing wheel distribution")
            if not has_source:
                print("   - Missing source distribution")
                
        return summary


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Prepare GIMP MCP Server package for PyPI publication"
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build package distributions"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate package without building"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building"
    )
    parser.add_argument(
        "--test-install",
        action="store_true",
        help="Test package installation"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze package contents"
    )
    
    args = parser.parse_args()
    
    # Default to build if no specific action specified
    if not any([args.validate, args.clean, args.test_install, args.analyze]):
        args.build = True
        
    print("📦 PyPI Package Preparation Script")
    print("==================================")
    
    # Initialize preparator
    project_root = Path.cwd()
    preparator = PyPIPackagePreparator(project_root)
    
    # Check dependencies
    if not preparator.check_dependencies():
        sys.exit(1)
        
    # Validate project structure
    if not preparator.validate_project_structure():
        sys.exit(1)
        
    # Validate pyproject.toml
    if not preparator.validate_pyproject_toml():
        sys.exit(1)
        
    # Check manifest
    if not preparator.check_manifest():
        print("⚠️  MANIFEST.in issues found, but continuing...")
        
    # Clean if requested
    if args.clean:
        preparator.clean_build_artifacts()
        
    # Build package
    if args.build:
        if args.clean:
            preparator.clean_build_artifacts()
            
        if not preparator.build_package():
            sys.exit(1)
            
        if not preparator.validate_distributions():
            sys.exit(1)
            
    # Test installation
    if args.test_install:
        if not preparator.test_install():
            sys.exit(1)
            
    # Analyze package contents
    if args.analyze:
        preparator.analyze_package_contents()
        
    # Generate summary
    summary = preparator.generate_summary_report()
    
    # Exit with appropriate code
    if summary["ready_for_publication"]:
        print("\n🎉 Package preparation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Package preparation completed with issues")
        sys.exit(1)


if __name__ == "__main__":
    main()