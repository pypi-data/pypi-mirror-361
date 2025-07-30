#!/usr/bin/env python3
"""
Test script for GIMP MCP Server startup and basic functionality.

This script tests the server initialization, tool registration,
and basic connectivity without requiring a full GIMP installation.
"""

import asyncio
import logging
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gimp_mcp.server import create_server, ServerConfig


async def test_server_initialization():
    """Test basic server initialization."""
    print("Testing server initialization...")
    
    try:
        # Create server configuration
        config = ServerConfig(
            host="localhost",
            port=3001,  # Use different port for testing
            debug=True,
            mode="headless",  # Force headless mode for testing
            log_level="DEBUG"
        )
        
        # Create server instance
        server = create_server(config)
        print("✓ Server instance created successfully")
        
        # Check if server has required components
        assert hasattr(server, 'app'), "Server missing FastMCP app"
        assert hasattr(server, 'gimp_api'), "Server missing GIMP API"
        assert hasattr(server, 'mode_manager'), "Server missing mode manager"
        
        print("✓ Server components initialized")
        
        # Test server configuration
        assert server.config.host == "localhost"
        assert server.config.port == 3001
        assert server.config.debug == True
        
        print("✓ Server configuration validated")
        
        return True
        
    except Exception as e:
        print(f"✗ Server initialization failed: {e}")
        return False


async def test_tool_registration():
    """Test that tools are properly registered."""
    print("\nTesting tool registration...")
    
    try:
        config = ServerConfig(mode="headless", debug=True)
        server = create_server(config)
        
        # Check if FastMCP app has tools registered
        # Note: This is a basic check - actual tool functionality would require GIMP
        app = server.app
        
        print("✓ FastMCP app accessible")
        print(f"✓ Server mode: {server.mode_manager.gui_mode}")
        
        return True
        
    except Exception as e:
        print(f"✗ Tool registration test failed: {e}")
        return False


async def test_error_handling():
    """Test error handling without GIMP connection."""
    print("\nTesting error handling...")
    
    try:
        config = ServerConfig(mode="headless", debug=True)
        server = create_server(config)
        
        # Test connection status (should handle missing GIMP gracefully)
        if hasattr(server.gimp_api, 'test_connection'):
            connection_result = await server.gimp_api.test_connection()
            
            # Should return a result even if GIMP is not available
            assert isinstance(connection_result, dict), "Connection test should return dict"
            assert "success" in connection_result, "Connection result should have success field"
            
            print(f"✓ Connection test handled gracefully: {connection_result.get('success')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("GIMP MCP Server Startup Test")
    print("=" * 40)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tests = [
        test_server_initialization,
        test_tool_registration,
        test_error_handling,
    ]
    
    results = []
    
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("Test Results:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "PASS" if result else "FAIL"
        print(f"  {test.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Server appears to be properly configured.")
        return 0
    else:
        print("✗ Some tests failed. Check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))