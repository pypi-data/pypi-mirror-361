#!/usr/bin/env python3
"""
GIMP MCP Server - Basic MCP Client Integration

This script demonstrates how to integrate with the GIMP MCP server from
various MCP client applications. It showcases:
- Establishing MCP connections with proper configuration
- Tool discovery and usage patterns
- Resource provider integration and monitoring
- Error handling and connection recovery
- Best practices for MCP client development

Perfect for developers wanting to integrate GIMP automation into their applications.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import sys
import os
from dataclasses import dataclass
import logging

# Add the parent directory to the path to import gimp_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import Tool, Resource, TextContent, ImageContent
except ImportError:
    print("❌ MCP not installed. Please install with: pip install mcp")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MCPClientConfig:
    """Configuration for MCP client connection."""
    server_command: str
    server_args: List[str]
    connection_timeout: float = 30.0
    operation_timeout: float = 60.0
    retry_attempts: int = 3
    retry_delay: float = 1.0

# Demo configuration
DEMO_CONFIG = {
    "output_dir": Path(__file__).parent / "outputs",
    "demo_name": "basic-mcp-client",
    "client_config": MCPClientConfig(
        server_command="python",
        server_args=["-m", "gimp_mcp.server"],
        connection_timeout=30.0,
        operation_timeout=60.0,
        retry_attempts=3,
        retry_delay=1.0
    ),
    "demo_workflows": [
        {
            "name": "basic_image_creation",
            "description": "Create a basic image with shapes",
            "steps": [
                {"action": "create_document", "params": {"width": 800, "height": 600}},
                {"action": "create_layer", "params": {"name": "shapes"}},
                {"action": "draw_rectangle", "params": {"x": 100, "y": 100, "width": 200, "height": 150, "fill_color": "#3498DB"}},
                {"action": "draw_ellipse", "params": {"center_x": 500, "center_y": 300, "radius_x": 100, "radius_y": 80, "fill_color": "#E74C3C"}},
                {"action": "export_document", "params": {"format": "PNG"}}
            ]
        },
        {
            "name": "layer_manipulation",
            "description": "Demonstrate layer operations",
            "steps": [
                {"action": "create_document", "params": {"width": 1024, "height": 768}},
                {"action": "create_layer", "params": {"name": "background", "layer_type": "RGB"}},
                {"action": "create_layer", "params": {"name": "foreground", "layer_type": "RGB"}},
                {"action": "set_layer_opacity", "params": {"opacity": 0.7}},
                {"action": "set_layer_blend_mode", "params": {"blend_mode": "multiply"}},
                {"action": "duplicate_layer", "params": {"new_name": "copy"}},
                {"action": "export_document", "params": {"format": "PNG"}}
            ]
        },
        {
            "name": "filter_effects",
            "description": "Apply various filters and effects",
            "steps": [
                {"action": "create_document", "params": {"width": 1920, "height": 1080}},
                {"action": "create_layer", "params": {"name": "content"}},
                {"action": "draw_rectangle", "params": {"x": 200, "y": 200, "width": 800, "height": 600, "fill_color": "#F39C12"}},
                {"action": "apply_blur", "params": {"radius": 5.0, "method": "gaussian"}},
                {"action": "adjust_brightness_contrast", "params": {"brightness": 10, "contrast": 15}},
                {"action": "apply_sharpen", "params": {"amount": 0.8, "threshold": 0.1}},
                {"action": "export_document", "params": {"format": "PNG"}}
            ]
        }
    ]
}

class GimpMCPClient:
    """
    Advanced MCP client for GIMP server integration.
    
    This client demonstrates best practices for connecting to and
    interacting with the GIMP MCP server, including error handling,
    resource monitoring, and workflow automation.
    """
    
    def __init__(self, config: MCPClientConfig, output_dir: Path):
        self.config = config
        self.output_dir = output_dir
        self.session: Optional[ClientSession] = None
        self.available_tools: Dict[str, Tool] = {}
        self.available_resources: Dict[str, Resource] = {}
        self.current_document_id: Optional[int] = None
        self.current_layer_id: Optional[int] = None
        self.operation_history: List[Dict[str, Any]] = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
    
    async def connect(self) -> bool:
        """Establish connection to GIMP MCP server with retry logic."""
        for attempt in range(self.config.retry_attempts):
            try:
                logger.info(f"Attempting to connect to GIMP MCP server (attempt {attempt + 1}/{self.config.retry_attempts})")
                
                # Create server parameters
                server_params = StdioServerParameters(
                    command=self.config.server_command,
                    args=self.config.server_args,
                    env=None
                )
                
                # Establish connection
                self.session = await asyncio.wait_for(
                    stdio_client(server_params),
                    timeout=self.config.connection_timeout
                )
                
                # Verify connection by listing tools
                await self.discover_capabilities()
                
                logger.info("✅ Successfully connected to GIMP MCP server")
                return True
                
            except asyncio.TimeoutError:
                logger.error(f"❌ Connection timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"❌ Connection failed on attempt {attempt + 1}: {e}")
            
            if attempt < self.config.retry_attempts - 1:
                logger.info(f"⏳ Retrying in {self.config.retry_delay} seconds...")
                await asyncio.sleep(self.config.retry_delay)
        
        logger.error("❌ Failed to establish connection after all retry attempts")
        return False
    
    async def discover_capabilities(self) -> bool:
        """Discover available tools and resources from the server."""
        try:
            logger.info("🔍 Discovering server capabilities...")
            
            # List available tools
            tools_response = await self.session.list_tools()
            for tool in tools_response.tools:
                self.available_tools[tool.name] = tool
                logger.debug(f"  Found tool: {tool.name}")
            
            # List available resources
            try:
                resources_response = await self.session.list_resources()
                for resource in resources_response.resources:
                    self.available_resources[resource.uri] = resource
                    logger.debug(f"  Found resource: {resource.uri}")
            except Exception as e:
                logger.warning(f"⚠️ Could not list resources: {e}")
            
            logger.info(f"✅ Discovered {len(self.available_tools)} tools and {len(self.available_resources)} resources")
            
            # Print capabilities summary
            print(f"\n📋 Server Capabilities:")
            print(f"   Available Tools: {len(self.available_tools)}")
            for tool_name in sorted(self.available_tools.keys()):
                tool = self.available_tools[tool_name]
                print(f"     • {tool_name}: {tool.description}")
            
            print(f"   Available Resources: {len(self.available_resources)}")
            for resource_uri in sorted(self.available_resources.keys()):
                resource = self.available_resources[resource_uri]
                print(f"     • {resource_uri}: {resource.description}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to discover capabilities: {e}")
            return False
    
    async def call_tool_safe(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Safely call a tool with proper error handling and timeout."""
        try:
            # Check if tool is available
            if tool_name not in self.available_tools:
                logger.error(f"❌ Tool '{tool_name}' not available")
                return None
            
            # Log the operation
            start_time = time.time()
            logger.info(f"🔧 Calling tool: {tool_name}")
            logger.debug(f"   Arguments: {arguments}")
            
            # Call tool with timeout
            response = await asyncio.wait_for(
                self.session.call_tool(tool_name, arguments),
                timeout=self.config.operation_timeout
            )
            
            # Log the result
            duration = time.time() - start_time
            logger.info(f"✅ Tool '{tool_name}' completed in {duration:.2f}s")
            
            # Record operation in history
            self.operation_history.append({
                "tool_name": tool_name,
                "arguments": arguments,
                "duration": duration,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "success": True
            })
            
            return response.content
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Tool '{tool_name}' timed out after {self.config.operation_timeout}s")
            self.operation_history.append({
                "tool_name": tool_name,
                "arguments": arguments,
                "duration": self.config.operation_timeout,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "success": False,
                "error": "timeout"
            })
            return None
            
        except Exception as e:
            logger.error(f"❌ Tool '{tool_name}' failed: {e}")
            self.operation_history.append({
                "tool_name": tool_name,
                "arguments": arguments,
                "duration": time.time() - start_time if 'start_time' in locals() else 0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "success": False,
                "error": str(e)
            })
            return None
    
    async def get_resource_safe(self, resource_uri: str) -> Optional[Any]:
        """Safely get a resource with proper error handling."""
        try:
            if resource_uri not in self.available_resources:
                logger.error(f"❌ Resource '{resource_uri}' not available")
                return None
            
            logger.info(f"📡 Getting resource: {resource_uri}")
            
            response = await self.session.read_resource(resource_uri)
            
            logger.info(f"✅ Resource '{resource_uri}' retrieved successfully")
            return response.contents
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource '{resource_uri}': {e}")
            return None
    
    async def monitor_system_status(self) -> Dict[str, Any]:
        """Monitor server and system status using resource providers."""
        try:
            logger.info("📊 Monitoring system status...")
            
            status = {}
            
            # Get system status
            if "system://status" in self.available_resources:
                system_status = await self.get_resource_safe("system://status")
                if system_status:
                    status["system"] = system_status
            
            # Get current document status
            if "document://current" in self.available_resources:
                doc_status = await self.get_resource_safe("document://current")
                if doc_status:
                    status["current_document"] = doc_status
            
            # Get document list
            if "document://list" in self.available_resources:
                doc_list = await self.get_resource_safe("document://list")
                if doc_list:
                    status["document_list"] = doc_list
            
            # Get server health
            if "system://health" in self.available_resources:
                health = await self.get_resource_safe("system://health")
                if health:
                    status["health"] = health
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Failed to monitor system status: {e}")
            return {}
    
    async def execute_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Execute a complete workflow with multiple steps."""
        try:
            workflow_name = workflow["name"]
            workflow_description = workflow["description"]
            steps = workflow["steps"]
            
            logger.info(f"🚀 Executing workflow: {workflow_name}")
            logger.info(f"   Description: {workflow_description}")
            logger.info(f"   Steps: {len(steps)}")
            
            workflow_start_time = time.time()
            
            for i, step in enumerate(steps):
                action = step["action"]
                params = step.get("params", {})
                
                logger.info(f"   Step {i+1}/{len(steps)}: {action}")
                
                # Handle special actions that affect client state
                if action == "create_document":
                    response = await self.call_tool_safe("create_document", params)
                    if response and "document_id" in response:
                        self.current_document_id = response["document_id"]
                        logger.info(f"     📄 Document ID: {self.current_document_id}")
                
                elif action == "create_layer":
                    if self.current_document_id:
                        params["document_id"] = self.current_document_id
                    response = await self.call_tool_safe("create_layer", params)
                    if response and "layer_id" in response:
                        self.current_layer_id = response["layer_id"]
                        logger.info(f"     🗂️ Layer ID: {self.current_layer_id}")
                
                elif action in ["draw_rectangle", "draw_ellipse", "apply_brush_stroke", "bucket_fill"]:
                    if self.current_document_id:
                        params["document_id"] = self.current_document_id
                    if self.current_layer_id and "layer_id" not in params:
                        params["layer_id"] = self.current_layer_id
                    await self.call_tool_safe(action, params)
                
                elif action in ["set_layer_opacity", "set_layer_blend_mode", "duplicate_layer"]:
                    if self.current_document_id:
                        params["document_id"] = self.current_document_id
                    if self.current_layer_id and "layer_id" not in params:
                        params["layer_id"] = self.current_layer_id
                    response = await self.call_tool_safe(action, params)
                    # Update layer ID if duplicating
                    if action == "duplicate_layer" and response and "layer_id" in response:
                        self.current_layer_id = response["layer_id"]
                
                elif action in ["apply_blur", "apply_sharpen", "adjust_brightness_contrast"]:
                    if self.current_document_id:
                        params["document_id"] = self.current_document_id
                    await self.call_tool_safe(action, params)
                
                elif action == "export_document":
                    if self.current_document_id:
                        params["document_id"] = self.current_document_id
                    if "file_path" not in params:
                        export_format = params.get("format", "PNG").lower()
                        params["file_path"] = str(self.output_dir / f"{workflow_name}.{export_format}")
                    await self.call_tool_safe("export_document", params)
                
                else:
                    # Generic tool call
                    if self.current_document_id and "document_id" not in params:
                        params["document_id"] = self.current_document_id
                    await self.call_tool_safe(action, params)
                
                # Brief pause between steps
                await asyncio.sleep(0.1)
            
            workflow_duration = time.time() - workflow_start_time
            logger.info(f"✅ Workflow '{workflow_name}' completed in {workflow_duration:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow '{workflow_name}' failed: {e}")
            return False
    
    async def cleanup_document(self) -> bool:
        """Clean up current document."""
        try:
            if self.current_document_id:
                logger.info(f"🧹 Closing document: {self.current_document_id}")
                await self.call_tool_safe("close_document", {"document_id": self.current_document_id})
                self.current_document_id = None
                self.current_layer_id = None
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cleanup document: {e}")
            return False
    
    async def generate_integration_report(self) -> bool:
        """Generate a comprehensive integration report."""
        try:
            logger.info("📊 Generating integration report...")
            
            # Calculate statistics
            successful_ops = [op for op in self.operation_history if op["success"]]
            failed_ops = [op for op in self.operation_history if not op["success"]]
            
            total_duration = sum(op["duration"] for op in self.operation_history)
            avg_duration = total_duration / len(self.operation_history) if self.operation_history else 0
            
            # Group operations by tool
            tool_stats = {}
            for op in self.operation_history:
                tool_name = op["tool_name"]
                if tool_name not in tool_stats:
                    tool_stats[tool_name] = {"count": 0, "success": 0, "total_duration": 0}
                tool_stats[tool_name]["count"] += 1
                if op["success"]:
                    tool_stats[tool_name]["success"] += 1
                tool_stats[tool_name]["total_duration"] += op["duration"]
            
            # Create comprehensive report
            report = {
                "integration_info": {
                    "demo_name": DEMO_CONFIG["demo_name"],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "client_config": {
                        "server_command": self.config.server_command,
                        "server_args": self.config.server_args,
                        "connection_timeout": self.config.connection_timeout,
                        "operation_timeout": self.config.operation_timeout,
                        "retry_attempts": self.config.retry_attempts
                    }
                },
                "server_capabilities": {
                    "available_tools": len(self.available_tools),
                    "available_resources": len(self.available_resources),
                    "tool_list": list(self.available_tools.keys()),
                    "resource_list": list(self.available_resources.keys())
                },
                "operation_statistics": {
                    "total_operations": len(self.operation_history),
                    "successful_operations": len(successful_ops),
                    "failed_operations": len(failed_ops),
                    "success_rate": (len(successful_ops) / len(self.operation_history) * 100) if self.operation_history else 0,
                    "total_duration": total_duration,
                    "average_duration": avg_duration
                },
                "tool_performance": {
                    tool: {
                        "calls": stats["count"],
                        "success_rate": (stats["success"] / stats["count"] * 100) if stats["count"] > 0 else 0,
                        "avg_duration": stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0
                    }
                    for tool, stats in tool_stats.items()
                },
                "operation_history": self.operation_history,
                "integration_insights": {
                    "most_used_tool": max(tool_stats.keys(), key=lambda x: tool_stats[x]["count"]) if tool_stats else None,
                    "fastest_tool": min(tool_stats.keys(), key=lambda x: tool_stats[x]["total_duration"] / tool_stats[x]["count"]) if tool_stats else None,
                    "slowest_tool": max(tool_stats.keys(), key=lambda x: tool_stats[x]["total_duration"] / tool_stats[x]["count"]) if tool_stats else None,
                    "most_reliable_tool": max(tool_stats.keys(), key=lambda x: tool_stats[x]["success"] / tool_stats[x]["count"]) if tool_stats else None
                }
            }
            
            # Save report
            report_path = self.output_dir / f"{DEMO_CONFIG['demo_name']}-integration-report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Create summary
            summary_path = self.output_dir / f"{DEMO_CONFIG['demo_name']}-summary.txt"
            with open(summary_path, 'w') as f:
                f.write("GIMP MCP Client Integration Summary\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Integration Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Server Capabilities: {len(self.available_tools)} tools, {len(self.available_resources)} resources\n")
                f.write(f"Operations Performed: {len(self.operation_history)}\n")
                f.write(f"Success Rate: {(len(successful_ops) / len(self.operation_history) * 100):.1f}%\n")
                f.write(f"Total Duration: {total_duration:.2f}s\n")
                f.write(f"Average Operation Time: {avg_duration:.3f}s\n\n")
                
                f.write("Tool Performance:\n")
                for tool, stats in tool_stats.items():
                    success_rate = (stats["success"] / stats["count"] * 100) if stats["count"] > 0 else 0
                    avg_duration = stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0
                    f.write(f"  {tool}: {stats['count']} calls, {success_rate:.1f}% success, {avg_duration:.3f}s avg\n")
                
                f.write(f"\nIntegration Insights:\n")
                for key, value in report["integration_insights"].items():
                    if value:
                        f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
            
            # Print summary
            print(f"\n📊 MCP Integration Summary:")
            print(f"   Server capabilities: {len(self.available_tools)} tools, {len(self.available_resources)} resources")
            print(f"   Operations performed: {len(self.operation_history)}")
            print(f"   Success rate: {(len(successful_ops) / len(self.operation_history) * 100):.1f}%")
            print(f"   Total integration time: {total_duration:.2f}s")
            print(f"   Average operation time: {avg_duration:.3f}s")
            
            logger.info(f"📄 Integration report saved: {report_path}")
            logger.info(f"📄 Summary saved: {summary_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate integration report: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Properly disconnect from the server."""
        try:
            logger.info("🔌 Disconnecting from server...")
            
            # Clean up any open documents
            await self.cleanup_document()
            
            # Close session
            if self.session:
                await self.session.close()
                self.session = None
            
            logger.info("✅ Disconnected successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to disconnect properly: {e}")
            return False

async def demonstrate_mcp_integration():
    """Demonstrate comprehensive MCP client integration."""
    try:
        print("🚀 Starting GIMP MCP Client Integration Demonstration")
        print("=" * 60)
        
        # Initialize client
        client = GimpMCPClient(
            config=DEMO_CONFIG["client_config"],
            output_dir=DEMO_CONFIG["output_dir"]
        )
        
        # Connect to server
        if not await client.connect():
            return False
        
        # Monitor initial system status
        print("\n📊 Initial system status:")
        status = await client.monitor_system_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Execute demo workflows
        print(f"\n🔄 Executing {len(DEMO_CONFIG['demo_workflows'])} demo workflows...")
        
        for i, workflow in enumerate(DEMO_CONFIG["demo_workflows"]):
            print(f"\n--- Workflow {i+1}: {workflow['name']} ---")
            success = await client.execute_workflow(workflow)
            
            if success:
                print(f"✅ Workflow '{workflow['name']}' completed successfully")
            else:
                print(f"❌ Workflow '{workflow['name']}' failed")
            
            # Clean up between workflows
            await client.cleanup_document()
            
            # Brief pause between workflows
            await asyncio.sleep(1)
        
        # Monitor final system status
        print("\n📊 Final system status:")
        final_status = await client.monitor_system_status()
        for key, value in final_status.items():
            print(f"   {key}: {value}")
        
        # Generate integration report
        await client.generate_integration_report()
        
        # Disconnect
        await client.disconnect()
        
        print("\n🎉 MCP Client Integration Demonstration completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration demonstration failed: {e}")
        return False

async def main():
    """Main entry point for the MCP client integration demonstration."""
    print("GIMP MCP Server - MCP Client Integration Demonstration")
    print("=" * 70)
    
    success = await demonstrate_mcp_integration()
    
    if success:
        print("\n✅ Demonstration completed successfully!")
        print(f"📁 Output files available in: {DEMO_CONFIG['output_dir']}")
        print("\n🔗 MCP Integration capabilities demonstrated:")
        print("   • Server connection and capability discovery")
        print("   • Tool usage with proper error handling")
        print("   • Resource provider monitoring")
        print("   • Workflow automation and state management")
        print("   • Performance tracking and reporting")
        print("   • Graceful connection management")
        sys.exit(0)
    else:
        print("\n❌ Demonstration failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())