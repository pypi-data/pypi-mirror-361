"""
Comprehensive test runner for GIMP MCP Server.

This script provides a unified interface for running all types of tests
including unit tests, integration tests, performance tests, and validation.
"""

import os
import sys
import asyncio
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "tests"))

from tests.validation.mcp_protocol_validator import run_mcp_validation, format_validation_report


class TestRunner:
    """Comprehensive test runner with multiple execution modes."""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def run_unit_tests(self, verbose: bool = False, coverage: bool = False) -> Dict[str, Any]:
        """Run unit tests using pytest."""
        print("🧪 Running unit tests...")
        
        cmd = ["python", "-m", "pytest", "tests/unit/"]
        
        if verbose:
            cmd.append("-v")
        if coverage:
            cmd.extend(["--cov=gimp_mcp", "--cov-report=term-missing", "--cov-report=html"])
            
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "--strict-config",
            "-x"  # Stop on first failure for faster feedback
        ])
        
        result = self._run_subprocess(cmd)
        
        return {
            "name": "Unit Tests",
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "duration": getattr(result, 'duration', 0)
        }
        
    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run integration tests using pytest."""
        print("🔗 Running integration tests...")
        
        cmd = ["python", "-m", "pytest", "tests/integration/"]
        
        if verbose:
            cmd.append("-v")
            
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "-x"
        ])
        
        result = self._run_subprocess(cmd)
        
        return {
            "name": "Integration Tests",
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "duration": getattr(result, 'duration', 0)
        }
        
    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance tests using pytest."""
        print("⚡ Running performance tests...")
        
        cmd = ["python", "-m", "pytest", "-m", "performance"]
        
        if verbose:
            cmd.append("-v")
            
        cmd.extend([
            "--tb=short",
            "--benchmark-only",
            "--benchmark-sort=mean"
        ])
        
        result = self._run_subprocess(cmd)
        
        return {
            "name": "Performance Tests",
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "duration": getattr(result, 'duration', 0)
        }
        
    async def run_mcp_validation(self, server_url: str = "localhost:3001") -> Dict[str, Any]:
        """Run MCP protocol validation."""
        print("🔍 Running MCP protocol validation...")
        
        try:
            start_time = time.time()
            validation_report = await run_mcp_validation(server_url)
            end_time = time.time()
            
            # Format report
            report_text = format_validation_report(validation_report)
            
            return {
                "name": "MCP Protocol Validation",
                "success": validation_report.get_pass_rate() >= 0.8,
                "output": report_text,
                "error": "",
                "duration": end_time - start_time,
                "pass_rate": validation_report.get_pass_rate(),
                "summary": validation_report.get_summary_stats()
            }
            
        except Exception as e:
            return {
                "name": "MCP Protocol Validation",
                "success": False,
                "output": "",
                "error": str(e),
                "duration": 0
            }
            
    def run_linting(self, verbose: bool = False) -> Dict[str, Any]:
        """Run code linting checks."""
        print("📝 Running linting checks...")
        
        results = []
        
        # Run black check
        black_result = self._run_subprocess([
            "python", "-m", "black", "--check", "--diff", "src/", "tests/"
        ])
        results.append(("Black", black_result.returncode == 0, black_result.stdout))
        
        # Run flake8
        flake8_result = self._run_subprocess([
            "python", "-m", "flake8", "src/", "tests/"
        ])
        results.append(("Flake8", flake8_result.returncode == 0, flake8_result.stdout))
        
        # Run isort check
        isort_result = self._run_subprocess([
            "python", "-m", "isort", "--check-only", "--diff", "src/", "tests/"
        ])
        results.append(("isort", isort_result.returncode == 0, isort_result.stdout))
        
        # Combine results
        all_passed = all(result[1] for result in results)
        combined_output = "\n".join([f"{name}: {'✓' if passed else '✗'}\n{output}" 
                                   for name, passed, output in results])
        
        return {
            "name": "Linting",
            "success": all_passed,
            "output": combined_output,
            "error": "",
            "duration": 0
        }
        
    def run_type_checking(self, verbose: bool = False) -> Dict[str, Any]:
        """Run type checking with mypy."""
        print("🔍 Running type checking...")
        
        cmd = ["python", "-m", "mypy", "src/"]
        
        if verbose:
            cmd.append("--verbose")
            
        result = self._run_subprocess(cmd)
        
        return {
            "name": "Type Checking",
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "duration": getattr(result, 'duration', 0)
        }
        
    def run_dependency_check(self) -> Dict[str, Any]:
        """Check for dependency issues."""
        print("📦 Checking dependencies...")
        
        try:
            # Check if requirements can be installed
            result = self._run_subprocess([
                "python", "-m", "pip", "check"
            ])
            
            # Check for security vulnerabilities
            safety_result = self._run_subprocess([
                "python", "-m", "safety", "check", "--json"
            ])
            
            success = result.returncode == 0 and safety_result.returncode == 0
            output = f"Pip check: {'✓' if result.returncode == 0 else '✗'}\n"
            output += f"Safety check: {'✓' if safety_result.returncode == 0 else '✗'}\n"
            output += result.stdout + "\n" + safety_result.stdout
            
            return {
                "name": "Dependency Check",
                "success": success,
                "output": output,
                "error": result.stderr + safety_result.stderr,
                "duration": 0
            }
            
        except Exception as e:
            return {
                "name": "Dependency Check",
                "success": False,
                "output": "",
                "error": str(e),
                "duration": 0
            }
            
    def run_all_tests(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Run all test categories."""
        print("🚀 Running comprehensive test suite...")
        self.start_time = time.time()
        
        results = {}
        
        # Run each test category
        if not args.skip_unit:
            results["unit"] = self.run_unit_tests(args.verbose, args.coverage)
            
        if not args.skip_integration:
            results["integration"] = self.run_integration_tests(args.verbose)
            
        if not args.skip_performance:
            results["performance"] = self.run_performance_tests(args.verbose)
            
        if not args.skip_validation:
            validation_result = asyncio.run(self.run_mcp_validation(args.server_url))
            results["validation"] = validation_result
            
        if not args.skip_linting:
            results["linting"] = self.run_linting(args.verbose)
            
        if not args.skip_types:
            results["type_checking"] = self.run_type_checking(args.verbose)
            
        if not args.skip_deps:
            results["dependencies"] = self.run_dependency_check()
            
        self.end_time = time.time()
        self.test_results = results
        
        return results
        
    def generate_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Generate comprehensive test report."""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("GIMP MCP SERVER TEST REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        if self.start_time and self.end_time:
            report_lines.append(f"Total Duration: {self.end_time - self.start_time:.2f}s")
        report_lines.append("")
        
        # Summary
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result["success"])
        
        report_lines.append("SUMMARY:")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Test Categories: {total_tests}")
        report_lines.append(f"Passed: {passed_tests}")
        report_lines.append(f"Failed: {total_tests - passed_tests}")
        report_lines.append(f"Success Rate: {passed_tests/total_tests:.1%}" if total_tests > 0 else "Success Rate: N/A")
        report_lines.append("")
        
        # Detailed results
        for category, result in results.items():
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            report_lines.append(f"{result['name'].upper()}: {status}")
            report_lines.append("-" * 40)
            
            if result.get("duration", 0) > 0:
                report_lines.append(f"Duration: {result['duration']:.2f}s")
                
            if result.get("pass_rate") is not None:
                report_lines.append(f"Pass Rate: {result['pass_rate']:.1%}")
                
            if result.get("summary"):
                report_lines.append("Summary:")
                for key, value in result["summary"].items():
                    report_lines.append(f"  {key}: {value}")
                    
            if result["output"] and len(result["output"]) < 1000:  # Only include short outputs
                report_lines.append("Output:")
                report_lines.append(result["output"][:500] + "..." if len(result["output"]) > 500 else result["output"])
                
            if result["error"]:
                report_lines.append("Errors:")
                report_lines.append(result["error"][:500] + "..." if len(result["error"]) > 500 else result["error"])
                
            report_lines.append("")
            
        report_text = "\n".join(report_lines)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"📄 Report saved to: {output_file}")
            
        return report_text
        
    def generate_json_report(self, results: Dict[str, Any], output_file: str):
        """Generate JSON test report."""
        json_report = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": self.end_time - self.start_time if self.start_time and self.end_time else 0,
            "summary": {
                "total_categories": len(results),
                "passed": sum(1 for r in results.values() if r["success"]),
                "failed": sum(1 for r in results.values() if not r["success"]),
                "success_rate": sum(1 for r in results.values() if r["success"]) / len(results) if results else 0
            },
            "results": results
        }
        
        with open(output_file, 'w') as f:
            json.dump(json_report, f, indent=2)
            
        print(f"📊 JSON report saved to: {output_file}")
        
    def _run_subprocess(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run subprocess with timing."""
        start_time = time.time()
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        end_time = time.time()
        result.duration = end_time - start_time
        return result


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="GIMP MCP Server Test Runner")
    
    # Test categories
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--performance", action="store_true", help="Run only performance tests")
    parser.add_argument("--validation", action="store_true", help="Run only MCP validation")
    parser.add_argument("--linting", action="store_true", help="Run only linting checks")
    parser.add_argument("--types", action="store_true", help="Run only type checking")
    parser.add_argument("--deps", action="store_true", help="Run only dependency checks")
    
    # Skip options
    parser.add_argument("--skip-unit", action="store_true", help="Skip unit tests")
    parser.add_argument("--skip-integration", action="store_true", help="Skip integration tests")
    parser.add_argument("--skip-performance", action="store_true", help="Skip performance tests")
    parser.add_argument("--skip-validation", action="store_true", help="Skip MCP validation")
    parser.add_argument("--skip-linting", action="store_true", help="Skip linting checks")
    parser.add_argument("--skip-types", action="store_true", help="Skip type checking")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency checks")
    
    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--server-url", default="localhost:3001", help="MCP server URL for validation")
    parser.add_argument("--report", help="Save text report to file")
    parser.add_argument("--json-report", help="Save JSON report to file")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        # Determine which tests to run
        if any([args.unit, args.integration, args.performance, args.validation, 
                args.linting, args.types, args.deps]):
            # Run specific test categories
            results = {}
            
            if args.unit:
                results["unit"] = runner.run_unit_tests(args.verbose, args.coverage)
            if args.integration:
                results["integration"] = runner.run_integration_tests(args.verbose)
            if args.performance:
                results["performance"] = runner.run_performance_tests(args.verbose)
            if args.validation:
                validation_result = asyncio.run(runner.run_mcp_validation(args.server_url))
                results["validation"] = validation_result
            if args.linting:
                results["linting"] = runner.run_linting(args.verbose)
            if args.types:
                results["types"] = runner.run_type_checking(args.verbose)
            if args.deps:
                results["deps"] = runner.run_dependency_check()
        else:
            # Run all tests
            results = runner.run_all_tests(args)
            
        # Generate reports
        report_text = runner.generate_report(results, args.report)
        
        if args.json_report:
            runner.generate_json_report(results, args.json_report)
            
        # Print summary
        print("\n" + "=" * 80)
        print("TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result["success"])
        
        print(f"Categories Run: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        if total_tests > 0:
            success_rate = passed_tests / total_tests
            print(f"Success Rate: {success_rate:.1%}")
            
            if success_rate == 1.0:
                print("🎉 All tests passed!")
                exit_code = 0
            elif success_rate >= 0.8:
                print("⚠️  Most tests passed, but some failures detected")
                exit_code = 0 if not args.fail_fast else 1
            else:
                print("❌ Multiple test failures detected")
                exit_code = 1
        else:
            print("⚠️  No tests were run")
            exit_code = 1
            
        # Print individual results
        for category, result in results.items():
            status = "✓" if result["success"] else "✗"
            print(f"  {status} {result['name']}")
            
        return exit_code
        
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)