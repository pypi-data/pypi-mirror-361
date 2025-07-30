#!/usr/bin/env python3
"""
GIMP MCP Server - Simple Graphics Demonstration

This script demonstrates basic image creation and simple graphics operations
using the GIMP MCP server. It showcases fundamental capabilities including:
- Document creation with various parameters
- Basic drawing operations (rectangles, ellipses)
- Color management and layer operations
- Document saving and exporting

Perfect for getting started with the GIMP MCP server and understanding
basic workflows.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import sys
import os

# Add the parent directory to the path to import gimp_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ MCP not installed. Please install with: pip install mcp")
    sys.exit(1)

# Demo configuration
DEMO_CONFIG = {
    "output_dir": Path(__file__).parent / "outputs",
    "demo_name": "simple-graphics-demo",
    "image_size": (1920, 1080),
    "colors": {
        "primary": "#3498DB",      # Blue
        "secondary": "#E74C3C",    # Red
        "accent": "#F39C12",       # Orange
        "background": "#2C3E50",   # Dark blue-gray
        "text": "#ECF0F1"          # Light gray
    }
}

class SimpleGraphicsDemo:
    """
    Demonstrates basic graphics operations using GIMP MCP server.
    
    This demo creates a simple composition with geometric shapes,
    demonstrating fundamental GIMP MCP operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = config["output_dir"]
        self.session = None
        self.document_id = None
        self.performance_metrics = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
    async def connect_to_server(self) -> bool:
        """
        Connect to the GIMP MCP server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print("🔗 Connecting to GIMP MCP server...")
            
            # Connect to the server using stdio
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "gimp_mcp.server"],
                env=None
            )
            
            self.session = await stdio_client(server_params)
            
            # Test connection
            response = await self.session.call_tool("list_documents", {})
            print(f"✅ Connected to GIMP MCP server successfully")
            print(f"📊 Server response: {response}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to GIMP MCP server: {e}")
            return False
    
    async def create_canvas(self) -> bool:
        """
        Create a new document/canvas for the demonstration.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n🎨 Creating new canvas...")
            start_time = time.time()
            
            # Create a new document
            response = await self.session.call_tool("create_document", {
                "width": self.config["image_size"][0],
                "height": self.config["image_size"][1],
                "name": f"{self.config['demo_name']}-canvas",
                "color_mode": "RGB",
                "fill_color": self.config["colors"]["background"]
            })
            
            self.document_id = response["document_id"]
            creation_time = time.time() - start_time
            
            print(f"✅ Canvas created successfully")
            print(f"📄 Document ID: {self.document_id}")
            print(f"⏱️ Creation time: {creation_time:.2f}s")
            
            self.performance_metrics["canvas_creation"] = creation_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create canvas: {e}")
            return False
    
    async def draw_geometric_shapes(self) -> bool:
        """
        Draw various geometric shapes to demonstrate drawing tools.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n🔷 Drawing geometric shapes...")
            start_time = time.time()
            
            # Create a layer for shapes
            layer_response = await self.session.call_tool("create_layer", {
                "document_id": self.document_id,
                "name": "Geometric Shapes",
                "layer_type": "RGB"
            })
            
            shapes_layer_id = layer_response["layer_id"]
            print(f"📁 Created shapes layer: {shapes_layer_id}")
            
            # Draw a large rectangle (background element)
            await self.session.call_tool("draw_rectangle", {
                "document_id": self.document_id,
                "layer_id": shapes_layer_id,
                "x": 100,
                "y": 100,
                "width": 600,
                "height": 400,
                "fill_color": self.config["colors"]["primary"],
                "stroke_color": self.config["colors"]["text"],
                "stroke_width": 3
            })
            
            # Draw a circle
            await self.session.call_tool("draw_ellipse", {
                "document_id": self.document_id,
                "layer_id": shapes_layer_id,
                "center_x": 1200,
                "center_y": 300,
                "radius_x": 150,
                "radius_y": 150,
                "fill_color": self.config["colors"]["secondary"],
                "stroke_color": self.config["colors"]["text"],
                "stroke_width": 3
            })
            
            # Draw a smaller rectangle
            await self.session.call_tool("draw_rectangle", {
                "document_id": self.document_id,
                "layer_id": shapes_layer_id,
                "x": 800,
                "y": 600,
                "width": 300,
                "height": 200,
                "fill_color": self.config["colors"]["accent"],
                "stroke_color": self.config["colors"]["text"],
                "stroke_width": 2
            })
            
            # Draw an ellipse
            await self.session.call_tool("draw_ellipse", {
                "document_id": self.document_id,
                "layer_id": shapes_layer_id,
                "center_x": 400,
                "center_y": 700,
                "radius_x": 200,
                "radius_y": 100,
                "fill_color": self.config["colors"]["primary"],
                "stroke_color": self.config["colors"]["secondary"],
                "stroke_width": 4
            })
            
            drawing_time = time.time() - start_time
            print(f"✅ Geometric shapes drawn successfully")
            print(f"⏱️ Drawing time: {drawing_time:.2f}s")
            
            self.performance_metrics["shape_drawing"] = drawing_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to draw shapes: {e}")
            return False
    
    async def demonstrate_layer_operations(self) -> bool:
        """
        Demonstrate layer management operations.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n🗂️ Demonstrating layer operations...")
            start_time = time.time()
            
            # Create additional layers
            text_layer = await self.session.call_tool("create_layer", {
                "document_id": self.document_id,
                "name": "Text Layer",
                "layer_type": "RGB"
            })
            
            effects_layer = await self.session.call_tool("create_layer", {
                "document_id": self.document_id,
                "name": "Effects Layer",
                "layer_type": "RGB"
            })
            
            # Demonstrate layer opacity changes
            await self.session.call_tool("set_layer_opacity", {
                "document_id": self.document_id,
                "layer_id": effects_layer["layer_id"],
                "opacity": 0.7
            })
            
            # Demonstrate layer blend modes
            await self.session.call_tool("set_layer_blend_mode", {
                "document_id": self.document_id,
                "layer_id": effects_layer["layer_id"],
                "blend_mode": "multiply"
            })
            
            # Add some content to the effects layer
            await self.session.call_tool("draw_ellipse", {
                "document_id": self.document_id,
                "layer_id": effects_layer["layer_id"],
                "center_x": 960,
                "center_y": 540,
                "radius_x": 400,
                "radius_y": 300,
                "fill_color": self.config["colors"]["accent"],
                "stroke_color": None,
                "stroke_width": 0
            })
            
            layer_time = time.time() - start_time
            print(f"✅ Layer operations completed successfully")
            print(f"⏱️ Layer operations time: {layer_time:.2f}s")
            
            self.performance_metrics["layer_operations"] = layer_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to perform layer operations: {e}")
            return False
    
    async def demonstrate_color_operations(self) -> bool:
        """
        Demonstrate color management operations.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n🎨 Demonstrating color operations...")
            start_time = time.time()
            
            # Set foreground and background colors
            await self.session.call_tool("set_foreground_color", {
                "color": self.config["colors"]["primary"]
            })
            
            await self.session.call_tool("set_background_color", {
                "color": self.config["colors"]["background"]
            })
            
            # Sample color from the image
            color_sample = await self.session.call_tool("sample_color", {
                "document_id": self.document_id,
                "x": 400,
                "y": 300,
                "sample_merged": True
            })
            
            print(f"🎨 Sampled color: {color_sample}")
            
            # Get active palette
            palette = await self.session.call_tool("get_active_palette", {})
            print(f"🎨 Active palette: {palette}")
            
            color_time = time.time() - start_time
            print(f"✅ Color operations completed successfully")
            print(f"⏱️ Color operations time: {color_time:.2f}s")
            
            self.performance_metrics["color_operations"] = color_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to perform color operations: {e}")
            return False
    
    async def save_and_export_document(self) -> bool:
        """
        Save the document and export in multiple formats.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n💾 Saving and exporting document...")
            start_time = time.time()
            
            # Save as native GIMP format
            xcf_path = self.output_dir / f"{self.config['demo_name']}.xcf"
            await self.session.call_tool("save_document", {
                "document_id": self.document_id,
                "file_path": str(xcf_path)
            })
            
            # Export as PNG
            png_path = self.output_dir / f"{self.config['demo_name']}.png"
            await self.session.call_tool("export_document", {
                "document_id": self.document_id,
                "file_path": str(png_path),
                "format": "PNG",
                "options": {
                    "compression": 6,
                    "optimize": True
                }
            })
            
            # Export as JPEG
            jpg_path = self.output_dir / f"{self.config['demo_name']}.jpg"
            await self.session.call_tool("export_document", {
                "document_id": self.document_id,
                "file_path": str(jpg_path),
                "format": "JPEG",
                "options": {
                    "quality": 90,
                    "optimize": True
                }
            })
            
            save_time = time.time() - start_time
            print(f"✅ Document saved and exported successfully")
            print(f"📄 XCF file: {xcf_path}")
            print(f"🖼️ PNG file: {png_path}")
            print(f"🖼️ JPEG file: {jpg_path}")
            print(f"⏱️ Save/export time: {save_time:.2f}s")
            
            self.performance_metrics["save_export"] = save_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save/export document: {e}")
            return False
    
    async def generate_performance_report(self) -> bool:
        """
        Generate a performance report from the collected metrics.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n📊 Generating performance report...")
            
            total_time = sum(self.performance_metrics.values())
            
            report = {
                "demo_name": self.config["demo_name"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "image_size": self.config["image_size"],
                "performance_metrics": self.performance_metrics,
                "total_time": total_time,
                "operations_count": len(self.performance_metrics),
                "average_operation_time": total_time / len(self.performance_metrics)
            }
            
            # Save performance report
            report_path = self.output_dir / f"{self.config['demo_name']}-performance.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Print performance summary
            print(f"📊 Performance Summary:")
            print(f"   Total execution time: {total_time:.2f}s")
            print(f"   Operations performed: {len(self.performance_metrics)}")
            print(f"   Average operation time: {total_time / len(self.performance_metrics):.2f}s")
            print(f"   Performance breakdown:")
            
            for operation, duration in self.performance_metrics.items():
                percentage = (duration / total_time) * 100
                print(f"     {operation}: {duration:.2f}s ({percentage:.1f}%)")
            
            print(f"📄 Performance report saved: {report_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate performance report: {e}")
            return False
    
    async def cleanup(self) -> bool:
        """
        Clean up resources and close connections.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n🧹 Cleaning up...")
            
            if self.document_id:
                await self.session.call_tool("close_document", {
                    "document_id": self.document_id
                })
            
            if self.session:
                await self.session.close()
            
            print("✅ Cleanup completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to cleanup: {e}")
            return False
    
    async def run_demo(self) -> bool:
        """
        Run the complete simple graphics demonstration.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("🚀 Starting Simple Graphics Demonstration")
            print("=" * 50)
            
            # Connect to server
            if not await self.connect_to_server():
                return False
            
            # Create canvas
            if not await self.create_canvas():
                return False
            
            # Draw geometric shapes
            if not await self.draw_geometric_shapes():
                return False
            
            # Demonstrate layer operations
            if not await self.demonstrate_layer_operations():
                return False
            
            # Demonstrate color operations
            if not await self.demonstrate_color_operations():
                return False
            
            # Save and export
            if not await self.save_and_export_document():
                return False
            
            # Generate performance report
            if not await self.generate_performance_report():
                return False
            
            print("\n🎉 Simple Graphics Demonstration completed successfully!")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return False
            
        finally:
            await self.cleanup()

async def main():
    """
    Main entry point for the simple graphics demonstration.
    """
    print("GIMP MCP Server - Simple Graphics Demonstration")
    print("=" * 60)
    
    # Create and run the demo
    demo = SimpleGraphicsDemo(DEMO_CONFIG)
    success = await demo.run_demo()
    
    if success:
        print("\n✅ Demonstration completed successfully!")
        print(f"📁 Output files available in: {DEMO_CONFIG['output_dir']}")
        sys.exit(0)
    else:
        print("\n❌ Demonstration failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())