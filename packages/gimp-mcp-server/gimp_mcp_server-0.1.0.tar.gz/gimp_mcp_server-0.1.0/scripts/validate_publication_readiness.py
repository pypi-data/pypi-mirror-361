#!/usr/bin/env python3
"""
Publication Readiness Validation Script

This script performs comprehensive validation to ensure the GIMP MCP Server project
is ready for GitHub repository creation and PyPI publication.

Usage:
    python scripts/validate_publication_readiness.py [--fix] [--verbose]

Requirements:
    - All publication preparation files and scripts
    - Development dependencies installed
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import json


class PublicationValidator:
    """Validates project readiness for publication."""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        """
        Initialize publication validator.
        
        Args:
            project_root: Path to project root directory
            verbose: Enable verbose output
        """
        self.project_root = project_root
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.passed_checks = []
        
    def log_pass(self, message: str):
        """Log a passed check."""
        self.passed_checks.append(message)
        if self.verbose:
            print(f"✅ {message}")
            
    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        print(f"⚠️  {message}")
        
    def log_error(self, message: str):
        """Log an error."""
        self.errors.append(message)
        print(f"❌ {message}")
        
    def check_required_files(self) -> bool:
        """Check that all required files exist."""
        print("🔍 Checking required files...")
        
        required_files = [
            # Core project files
            "pyproject.toml",
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            "MANIFEST.in",
            
            # GitHub configuration
            ".github/workflows/ci.yml",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/documentation.yml",
            ".github/PULL_REQUEST_TEMPLATE.md",
            
            # Publication scripts
            "scripts/create_github_repo.py",
            "scripts/prepare_pypi_package.py",
            "scripts/publish_to_pypi.py",
            "scripts/requirements.txt",
            "PUBLICATION_GUIDE.md",
            
            # Source code structure
            "src/gimp_mcp/__init__.py",
            "src/gimp_mcp/server.py",
            
            # Test structure
            "tests/__init__.py",
            "pytest.ini",
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log_pass(f"Required file exists: {file_path}")
            else:
                self.log_error(f"Missing required file: {file_path}")
                all_exist = False
                
        return all_exist
        
    def validate_pyproject_toml(self) -> bool:
        """Validate pyproject.toml configuration."""
        print("\n🔍 Validating pyproject.toml...")
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                self.log_error("tomllib/tomli not available for TOML parsing")
                return False
        
        pyproject_path = self.project_root / "pyproject.toml"
        
        if not pyproject_path.exists():
            self.log_error("pyproject.toml not found")
            return False
            
        try:
            with open(pyproject_path, "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            self.log_error(f"Failed to parse pyproject.toml: {e}")
            return False
            
        # Check required sections
        required_sections = ["build-system", "project", "tool"]
        for section in required_sections:
            if section in config:
                self.log_pass(f"Section exists: [{section}]")
            else:
                self.log_error(f"Missing section: [{section}]")
                return False
                
        # Check project metadata
        project = config.get("project", {})
        required_fields = [
            "name", "version", "description", "readme", "requires-python",
            "license", "authors", "keywords", "classifiers", "dependencies"
        ]
        
        for field in required_fields:
            if field in project:
                self.log_pass(f"Project field exists: {field}")
            else:
                self.log_error(f"Missing project field: {field}")
                return False
                
        # Validate version format
        version = project.get("version", "")
        if re.match(r'^\d+\.\d+\.\d+', version):
            self.log_pass(f"Valid version format: {version}")
        else:
            self.log_error(f"Invalid version format: {version}")
            return False
            
        # Check for required URLs
        urls = project.get("urls", {})
        required_urls = ["Homepage", "Repository", "Bug Tracker"]
        for url_type in required_urls:
            if url_type in urls:
                self.log_pass(f"URL configured: {url_type}")
            else:
                self.log_warning(f"Missing URL: {url_type}")
                
        return True
        
    def validate_readme(self) -> bool:
        """Validate README.md content."""
        print("\n🔍 Validating README.md...")
        
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            self.log_error("README.md not found")
            return False
            
        try:
            content = readme_path.read_text(encoding="utf-8")
        except Exception as e:
            self.log_error(f"Failed to read README.md: {e}")
            return False
            
        # Check required sections
        required_sections = [
            "# GIMP MCP Server",
            "## Features",
            "## Requirements", 
            "## Installation",
            "## Quick Start",
            "## Documentation",
            "## Contributing",
            "## License"
        ]
        
        for section in required_sections:
            if section in content:
                self.log_pass(f"README section found: {section}")
            else:
                self.log_warning(f"README section missing: {section}")
                
        # Check for badges
        if "![" in content and "https://img.shields.io" in content:
            self.log_pass("README contains badges")
        else:
            self.log_warning("README missing badges/shields")
            
        # Check for installation instructions
        if "pip install" in content:
            self.log_pass("README contains pip installation instructions")
        else:
            self.log_warning("README missing pip installation instructions")
            
        return True
        
    def validate_license(self) -> bool:
        """Validate LICENSE file."""
        print("\n🔍 Validating LICENSE...")
        
        license_path = self.project_root / "LICENSE"
        if not license_path.exists():
            self.log_error("LICENSE file not found")
            return False
            
        try:
            content = license_path.read_text(encoding="utf-8")
        except Exception as e:
            self.log_error(f"Failed to read LICENSE: {e}")
            return False
            
        # Check for MIT license content
        if "MIT License" in content and "Permission is hereby granted" in content:
            self.log_pass("Valid MIT License content")
        else:
            self.log_warning("LICENSE content may not be valid MIT license")
            
        # Check for current year
        import datetime
        current_year = datetime.datetime.now().year
        if str(current_year) in content:
            self.log_pass(f"LICENSE contains current year ({current_year})")
        else:
            self.log_warning(f"LICENSE may need year update ({current_year})")
            
        return True
        
    def validate_changelog(self) -> bool:
        """Validate CHANGELOG.md."""
        print("\n🔍 Validating CHANGELOG.md...")
        
        changelog_path = self.project_root / "CHANGELOG.md"
        if not changelog_path.exists():
            self.log_error("CHANGELOG.md not found")
            return False
            
        try:
            content = changelog_path.read_text(encoding="utf-8")
        except Exception as e:
            self.log_error(f"Failed to read CHANGELOG.md: {e}")
            return False
            
        # Check format
        if "# Changelog" in content and "## [0.1.0]" in content:
            self.log_pass("CHANGELOG.md has proper format")
        else:
            self.log_warning("CHANGELOG.md format may need improvement")
            
        # Check for version entries
        if "### Added" in content and "### Changed" in content:
            self.log_pass("CHANGELOG.md contains change categories")
        else:
            self.log_warning("CHANGELOG.md missing change categories")
            
        return True
        
    def validate_github_config(self) -> bool:
        """Validate GitHub configuration files."""
        print("\n🔍 Validating GitHub configuration...")
        
        # Check workflow file
        workflow_path = self.project_root / ".github" / "workflows" / "ci.yml"
        if workflow_path.exists():
            self.log_pass("GitHub Actions CI workflow exists")
            
            try:
                content = workflow_path.read_text(encoding="utf-8")
                
                # Check for required jobs
                required_jobs = ["lint", "security", "test", "build"]
                for job in required_jobs:
                    if f"{job}:" in content:
                        self.log_pass(f"CI job configured: {job}")
                    else:
                        self.log_warning(f"CI job missing: {job}")
                        
            except Exception as e:
                self.log_error(f"Failed to read CI workflow: {e}")
                return False
        else:
            self.log_error("GitHub Actions CI workflow not found")
            return False
            
        # Check issue templates
        issue_templates = [
            "bug_report.yml",
            "feature_request.yml", 
            "documentation.yml"
        ]
        
        for template in issue_templates:
            template_path = self.project_root / ".github" / "ISSUE_TEMPLATE" / template
            if template_path.exists():
                self.log_pass(f"Issue template exists: {template}")
            else:
                self.log_error(f"Issue template missing: {template}")
                return False
                
        # Check PR template
        pr_template_path = self.project_root / ".github" / "PULL_REQUEST_TEMPLATE.md"
        if pr_template_path.exists():
            self.log_pass("Pull request template exists")
        else:
            self.log_error("Pull request template missing")
            return False
            
        return True
        
    def validate_scripts(self) -> bool:
        """Validate publication scripts."""
        print("\n🔍 Validating publication scripts...")
        
        scripts = [
            "create_github_repo.py",
            "prepare_pypi_package.py",
            "publish_to_pypi.py"
        ]
        
        for script in scripts:
            script_path = self.project_root / "scripts" / script
            if script_path.exists():
                self.log_pass(f"Publication script exists: {script}")
                
                # Check if script is executable
                try:
                    with open(script_path, 'r') as f:
                        first_line = f.readline()
                        if first_line.startswith("#!"):
                            self.log_pass(f"Script has shebang: {script}")
                        else:
                            self.log_warning(f"Script missing shebang: {script}")
                except Exception:
                    self.log_warning(f"Could not check shebang: {script}")
                    
            else:
                self.log_error(f"Publication script missing: {script}")
                return False
                
        return True
        
    def validate_manifest(self) -> bool:
        """Validate MANIFEST.in."""
        print("\n🔍 Validating MANIFEST.in...")
        
        manifest_path = self.project_root / "MANIFEST.in"
        if not manifest_path.exists():
            self.log_error("MANIFEST.in not found")
            return False
            
        try:
            content = manifest_path.read_text(encoding="utf-8")
        except Exception as e:
            self.log_error(f"Failed to read MANIFEST.in: {e}")
            return False
            
        # Check for required includes
        required_includes = [
            "README.md",
            "LICENSE", 
            "CHANGELOG.md",
            "recursive-include docs",
            "recursive-include tests",
            "recursive-include src"
        ]
        
        for include in required_includes:
            if include in content:
                self.log_pass(f"MANIFEST.in includes: {include}")
            else:
                self.log_warning(f"MANIFEST.in missing: {include}")
                
        return True
        
    def check_code_quality(self) -> bool:
        """Check code quality tools."""
        print("\n🔍 Checking code quality...")
        
        quality_tools = ["black", "flake8", "isort", "mypy"]
        all_passed = True
        
        for tool in quality_tools:
            try:
                if tool == "black":
                    cmd = [sys.executable, "-m", "black", "--check", "src/", "tests/"]
                elif tool == "flake8":
                    cmd = [sys.executable, "-m", "flake8", "src/", "tests/"]
                elif tool == "isort":
                    cmd = [sys.executable, "-m", "isort", "--check-only", "src/", "tests/"]
                elif tool == "mypy":
                    cmd = [sys.executable, "-m", "mypy", "src/"]
                else:
                    continue
                    
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    self.log_pass(f"Code quality check passed: {tool}")
                else:
                    self.log_warning(f"Code quality check failed: {tool}")
                    if self.verbose:
                        print(f"  Output: {result.stdout}")
                        print(f"  Error: {result.stderr}")
                    all_passed = False
                    
            except FileNotFoundError:
                self.log_warning(f"Code quality tool not found: {tool}")
                all_passed = False
            except Exception as e:
                self.log_warning(f"Error running {tool}: {e}")
                all_passed = False
                
        return all_passed
        
    def check_test_suite(self) -> bool:
        """Check test suite."""
        print("\n🔍 Checking test suite...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_pass("pytest is available")
            else:
                self.log_warning("pytest not available")
                return False
                
        except Exception as e:
            self.log_warning(f"Error checking pytest: {e}")
            return False
            
        # Check for test files
        test_files = list((self.project_root / "tests").glob("**/test_*.py"))
        if test_files:
            self.log_pass(f"Found {len(test_files)} test files")
        else:
            self.log_warning("No test files found")
            
        return True
        
    def validate_documentation_links(self) -> bool:
        """Validate documentation links."""
        print("\n🔍 Validating documentation links...")
        
        # Check internal links in README
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8")
            
            # Find markdown links
            import re
            links = re.findall(r'\[.*?\]\((.*?)\)', content)
            
            for link in links:
                if link.startswith('http'):
                    # External link - skip for now
                    continue
                elif link.startswith('#'):
                    # Anchor link - skip for now
                    continue
                else:
                    # Internal file link
                    link_path = self.project_root / link
                    if link_path.exists():
                        self.log_pass(f"Internal link valid: {link}")
                    else:
                        self.log_warning(f"Internal link broken: {link}")
                        
        return True
        
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate validation summary report."""
        total_checks = len(self.passed_checks) + len(self.warnings) + len(self.errors)
        
        summary = {
            "total_checks": total_checks,
            "passed": len(self.passed_checks),
            "warnings": len(self.warnings),
            "errors": len(self.errors),
            "ready_for_publication": len(self.errors) == 0,
            "details": {
                "passed_checks": self.passed_checks,
                "warnings": self.warnings,
                "errors": self.errors
            }
        }
        
        print("\n" + "="*60)
        print("📊 PUBLICATION READINESS SUMMARY")
        print("="*60)
        
        print(f"📋 Total Checks: {total_checks}")
        print(f"✅ Passed: {len(self.passed_checks)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if len(self.errors) == 0:
            print("\n🎉 PROJECT IS READY FOR PUBLICATION!")
            print("✅ All critical checks passed")
            if len(self.warnings) > 0:
                print(f"⚠️  {len(self.warnings)} warnings should be addressed for best practices")
        else:
            print("\n❌ PROJECT IS NOT READY FOR PUBLICATION")
            print(f"💡 Fix {len(self.errors)} errors before proceeding")
            
        if len(self.warnings) > 0:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
                
        if len(self.errors) > 0:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"   • {error}")
                
        return summary
        
    def run_validation(self) -> bool:
        """Run all validation checks."""
        print("🔍 Publication Readiness Validation")
        print("====================================")
        
        validation_steps = [
            ("Required Files", self.check_required_files),
            ("pyproject.toml", self.validate_pyproject_toml),
            ("README.md", self.validate_readme),
            ("LICENSE", self.validate_license),
            ("CHANGELOG.md", self.validate_changelog),
            ("GitHub Config", self.validate_github_config),
            ("Publication Scripts", self.validate_scripts),
            ("MANIFEST.in", self.validate_manifest),
            ("Code Quality", self.check_code_quality),
            ("Test Suite", self.check_test_suite),
            ("Documentation Links", self.validate_documentation_links),
        ]
        
        for step_name, step_func in validation_steps:
            try:
                step_func()
            except Exception as e:
                self.log_error(f"Validation step '{step_name}' failed: {e}")
                
        # Generate summary
        summary = self.generate_summary_report()
        
        return summary["ready_for_publication"]


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Validate GIMP MCP Server publication readiness"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output",
        help="Save validation report to JSON file"
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    project_root = Path.cwd()
    validator = PublicationValidator(project_root, args.verbose)
    
    # Run validation
    ready = validator.run_validation()
    
    # Save report if requested
    if args.output:
        summary = validator.generate_summary_report()
        with open(args.output, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n📄 Validation report saved to: {args.output}")
    
    # Exit with appropriate code
    if ready:
        print("\n🎉 Validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Validation completed with issues")
        sys.exit(1)


if __name__ == "__main__":
    main()