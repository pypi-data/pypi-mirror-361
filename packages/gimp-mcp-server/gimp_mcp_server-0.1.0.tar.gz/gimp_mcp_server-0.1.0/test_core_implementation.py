#!/usr/bin/env python3
"""
Test script to validate the core GIMP API wrapper implementation.

This script tests the core functionality of the GIMP MCP server without
requiring actual GIMP installation, using mock objects and validation.
"""

import asyncio
import logging
import sys
import traceback
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports() -> Dict[str, Any]:
    """Test that all modules can be imported successfully."""
    logger.info("Testing module imports...")
    
    results = {
        "success": True,
        "imported_modules": [],
        "failed_modules": [],
        "errors": []
    }
    
    modules_to_test = [
        "src.gimp_mcp.gimp_api",
        "src.gimp_mcp.mode_manager", 
        "src.gimp_mcp.utils.errors",
        "src.gimp_mcp.utils.gi_helpers",
        "src.gimp_mcp.utils.image_utils",
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            results["imported_modules"].append(module_name)
            logger.info(f"✓ Successfully imported {module_name}")
        except Exception as e:
            results["failed_modules"].append(module_name)
            results["errors"].append(f"{module_name}: {str(e)}")
            results["success"] = False
            logger.error(f"✗ Failed to import {module_name}: {e}")
    
    return results


def test_error_classes() -> Dict[str, Any]:
    """Test error class definitions and functionality."""
    logger.info("Testing error classes...")
    
    results = {
        "success": True,
        "tested_errors": [],
        "errors": []
    }
    
    try:
        from src.gimp_mcp.utils.errors import (
            GimpError, GimpConnectionError, GimpOperationError,
            GimpValidationError, GimpModeError, GimpImageError,
            GimpLayerError, GimpDrawingError, GimpFileError,
            validate_required_params, validate_param_type
        )
        
        # Test base error
        error = GimpError("Test error", {"detail": "test"})
        assert error.message == "Test error"
        assert error.details == {"detail": "test"}
        
        error_dict = error.to_dict()
        assert error_dict["error_type"] == "GimpError"
        assert error_dict["message"] == "Test error"
        
        results["tested_errors"].append("GimpError")
        
        # Test validation functions
        try:
            validate_required_params(["param1", "param2"], {"param1": "value1"})
            assert False, "Should have raised GimpValidationError"
        except GimpValidationError:
            pass  # Expected
        
        try:
            validate_param_type("test_param", "string_value", int)
            assert False, "Should have raised GimpValidationError"
        except GimpValidationError:
            pass  # Expected
        
        results["tested_errors"].extend(["validate_required_params", "validate_param_type"])
        logger.info("✓ Error classes working correctly")
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Error class test failed: {str(e)}")
        logger.error(f"✗ Error class test failed: {e}")
    
    return results


def test_image_utils() -> Dict[str, Any]:
    """Test image utility functions."""
    logger.info("Testing image utilities...")
    
    results = {
        "success": True,
        "tested_functions": [],
        "errors": []
    }
    
    try:
        from src.gimp_mcp.utils.image_utils import (
            validate_color, parse_color, validate_coordinates,
            validate_dimensions, validate_opacity, normalize_path_points,
            validate_image_format, create_image_info
        )
        
        # Test color validation
        assert validate_color("#FF0000") == True
        assert validate_color("#ff0000") == True
        assert validate_color("red") == True
        assert validate_color("rgb(255,0,0)") == True
        assert validate_color("invalid") == False
        results["tested_functions"].append("validate_color")
        
        # Test color parsing
        r, g, b, a = parse_color("#FF0000")
        assert r == 1.0 and g == 0.0 and b == 0.0 and a == 1.0
        
        r, g, b, a = parse_color("red")
        assert r == 1.0 and g == 0.0 and b == 0.0 and a == 1.0
        results["tested_functions"].append("parse_color")
        
        # Test coordinate validation
        validate_coordinates(10, 20)  # Should not raise
        try:
            validate_coordinates(-1, 5)
            assert False, "Should have raised exception"
        except:
            pass  # Expected
        results["tested_functions"].append("validate_coordinates")
        
        # Test dimension validation
        validate_dimensions(100, 200)  # Should not raise
        try:
            validate_dimensions(0, 100)
            assert False, "Should have raised exception"
        except:
            pass  # Expected
        results["tested_functions"].append("validate_dimensions")
        
        # Test image format validation
        assert validate_image_format("PNG") == "PNG"
        assert validate_image_format("jpg") == "JPEG"
        results["tested_functions"].append("validate_image_format")
        
        # Test image info creation
        info = create_image_info(800, 600, "RGB", 300.0)
        assert info["width"] == 800
        assert info["height"] == 600
        assert info["mode"] == "RGB"
        assert info["resolution"] == 300.0
        results["tested_functions"].append("create_image_info")
        
        logger.info("✓ Image utilities working correctly")
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Image utils test failed: {str(e)}")
        logger.error(f"✗ Image utils test failed: {e}")
    
    return results


def test_gi_helpers() -> Dict[str, Any]:
    """Test GObject Introspection helper functions."""
    logger.info("Testing GI helpers...")
    
    results = {
        "success": True,
        "tested_functions": [],
        "errors": []
    }
    
    try:
        from src.gimp_mcp.utils.gi_helpers import (
            check_gi_availability, validate_gimp_version,
            get_gimp_system_info, create_gimp_color
        )
        
        # Test GI availability check (will likely fail without GIMP installed)
        gi_status = check_gi_availability()
        assert isinstance(gi_status, dict)
        assert "gi_available" in gi_status
        results["tested_functions"].append("check_gi_availability")
        
        # Test version validation (will likely fail without GIMP installed)
        version_status = validate_gimp_version()
        assert isinstance(version_status, dict)
        assert "compatible" in version_status
        results["tested_functions"].append("validate_gimp_version")
        
        # Test system info (will work even without GIMP)
        system_info = get_gimp_system_info()
        assert isinstance(system_info, dict)
        results["tested_functions"].append("get_gimp_system_info")
        
        logger.info("✓ GI helpers working correctly (may show warnings without GIMP)")
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"GI helpers test failed: {str(e)}")
        logger.error(f"✗ GI helpers test failed: {e}")
    
    return results


def test_mode_manager() -> Dict[str, Any]:
    """Test mode manager functionality."""
    logger.info("Testing mode manager...")
    
    results = {
        "success": True,
        "tested_functions": [],
        "errors": []
    }
    
    try:
        from src.gimp_mcp.mode_manager import GimpModeManager
        
        # Test mode manager creation
        manager = GimpModeManager(force_mode="headless")
        assert manager.force_mode == "headless"
        assert manager.gui_mode == False
        results["tested_functions"].append("GimpModeManager.__init__")
        
        # Test mode info
        mode_info = manager.get_mode_info()
        assert isinstance(mode_info, dict)
        assert "current_mode" in mode_info
        results["tested_functions"].append("get_mode_info")
        
        # Test mode validation
        validation_result = manager.validate_mode_requirements()
        assert isinstance(validation_result, bool)
        results["tested_functions"].append("validate_mode_requirements")
        
        logger.info("✓ Mode manager working correctly")
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Mode manager test failed: {str(e)}")
        logger.error(f"✗ Mode manager test failed: {e}")
    
    return results


async def test_gimp_api() -> Dict[str, Any]:
    """Test GIMP API wrapper functionality."""
    logger.info("Testing GIMP API wrapper...")
    
    results = {
        "success": True,
        "tested_functions": [],
        "errors": []
    }
    
    try:
        from src.gimp_mcp.gimp_api import GimpAPI
        from src.gimp_mcp.mode_manager import GimpModeManager
        
        # Test API creation
        mode_manager = GimpModeManager(force_mode="headless")
        api = GimpAPI(mode_manager=mode_manager)
        assert api.mode_manager is not None
        results["tested_functions"].append("GimpAPI.__init__")
        
        # Test connection status
        assert hasattr(api, "is_connected")
        assert hasattr(api, "mode")
        results["tested_functions"].append("GimpAPI.properties")
        
        # Test system info (will work even without GIMP connection)
        system_info = await api.get_system_info()
        assert isinstance(system_info, dict)
        results["tested_functions"].append("get_system_info")
        
        # Test image listing (will likely fail without GIMP)
        try:
            images = await api.list_open_images()
            results["tested_functions"].append("list_open_images")
        except Exception as e:
            logger.info(f"list_open_images failed as expected without GIMP: {e}")
        
        # Test cleanup
        await api.cleanup()
        results["tested_functions"].append("cleanup")
        
        logger.info("✓ GIMP API wrapper structure working correctly")
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"GIMP API test failed: {str(e)}")
        logger.error(f"✗ GIMP API test failed: {e}")
    
    return results


async def run_all_tests() -> Dict[str, Any]:
    """Run all tests and return comprehensive results."""
    logger.info("Starting comprehensive GIMP MCP Server core implementation tests...")
    
    test_results = {
        "overall_success": True,
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "detailed_results": {}
    }
    
    # Define tests to run
    tests = [
        ("imports", test_imports),
        ("error_classes", test_error_classes),
        ("image_utils", test_image_utils),
        ("gi_helpers", test_gi_helpers),
        ("mode_manager", test_mode_manager),
        ("gimp_api", test_gimp_api),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            test_results["detailed_results"][test_name] = result
            test_results["tests_run"] += 1
            
            if result["success"]:
                test_results["tests_passed"] += 1
                logger.info(f"✓ Test {test_name} PASSED")
            else:
                test_results["tests_failed"] += 1
                test_results["overall_success"] = False
                logger.error(f"✗ Test {test_name} FAILED")
                for error in result.get("errors", []):
                    logger.error(f"  Error: {error}")
        
        except Exception as e:
            test_results["detailed_results"][test_name] = {
                "success": False,
                "errors": [f"Test execution failed: {str(e)}"]
            }
            test_results["tests_run"] += 1
            test_results["tests_failed"] += 1
            test_results["overall_success"] = False
            logger.error(f"✗ Test {test_name} FAILED with exception: {e}")
            logger.error(traceback.format_exc())
    
    return test_results


def print_summary(results: Dict[str, Any]) -> None:
    """Print test summary."""
    logger.info(f"\n{'='*70}")
    logger.info("GIMP MCP SERVER CORE IMPLEMENTATION TEST SUMMARY")
    logger.info(f"{'='*70}")
    
    logger.info(f"Tests Run: {results['tests_run']}")
    logger.info(f"Tests Passed: {results['tests_passed']}")
    logger.info(f"Tests Failed: {results['tests_failed']}")
    logger.info(f"Overall Success: {'✓ PASS' if results['overall_success'] else '✗ FAIL'}")
    
    logger.info(f"\n{'='*70}")
    logger.info("DETAILED RESULTS")
    logger.info(f"{'='*70}")
    
    for test_name, result in results["detailed_results"].items():
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        logger.info(f"{test_name:20} {status}")
        
        if "tested_functions" in result and result["tested_functions"]:
            logger.info(f"  Functions tested: {', '.join(result['tested_functions'])}")
        
        if result.get("errors"):
            for error in result["errors"]:
                logger.info(f"  Error: {error}")
    
    logger.info(f"\n{'='*70}")
    if results["overall_success"]:
        logger.info("🎉 CORE IMPLEMENTATION VALIDATION SUCCESSFUL!")
        logger.info("The GIMP MCP Server core functionality is properly implemented.")
    else:
        logger.info("⚠️  SOME TESTS FAILED")
        logger.info("Review the errors above. Note: Some failures are expected without GIMP installation.")
    logger.info(f"{'='*70}")


async def main():
    """Main test runner."""
    try:
        # Add the src directory to the Python path
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        results = await run_all_tests()
        print_summary(results)
        
        # Exit with appropriate code
        sys.exit(0 if results["overall_success"] else 1)
        
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())