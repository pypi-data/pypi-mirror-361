#!/usr/bin/env python3
"""
GIMP MCP Server - Layer Operations Demonstration

This script demonstrates advanced layer management operations using the GIMP MCP server.
It showcases layer-specific capabilities including:
- Creating multiple layers with different types
- Layer opacity and blend mode management
- Layer visibility and positioning
- Layer duplication and organization
- Complex multi-layer compositions

Perfect for understanding layer workflow patterns and best practices.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
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
    "demo_name": "layer-operations-demo",
    "image_size": (1920, 1080),
    "layer_configurations": [
        {
            "name": "Background",
            "type": "RGB",
            "opacity": 1.0,
            "blend_mode": "normal",
            "color": "#2C3E50"
        },
        {
            "name": "Base Shapes",
            "type": "RGB",
            "opacity": 0.8,
            "blend_mode": "normal",
            "color": "#3498DB"
        },
        {
            "name": "Overlay Effects",
            "type": "RGB",
            "opacity": 0.6,
            "blend_mode": "multiply",
            "color": "#E74C3C"
        },
        {
            "name": "Highlights",
            "type": "RGB",
            "opacity": 0.9,
            "blend_mode": "screen",
            "color": "#F39C12"
        },
        {
            "name": "Text Layer",
            "type": "RGB",
            "opacity": 1.0,
            "blend_mode": "normal",
            "color": "#ECF0F1"
        }
    ],
    "blend_modes": ["normal", "multiply", "screen", "overlay", "soft-light", "hard-light"]
}

class LayerOperationsDemo:
    """
    Demonstrates comprehensive layer management using GIMP MCP server.
    
    This demo creates a complex multi-layer composition showcasing
    various layer operations and management techniques.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = config["output_dir"]
        self.session = None
        self.document_id = None
        self.created_layers = []
        self.performance_metrics = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
    async def connect_to_server(self) -> bool:
        """Connect to the GIMP MCP server."""
        try:
            print("🔗 Connecting to GIMP MCP server...")
            
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "gimp_mcp.server"],
                env=None
            )
            
            self.session = await stdio_client(server_params)
            
            # Test connection
            response = await self.session.call_tool("list_documents", {})
            print(f"✅ Connected to GIMP MCP server successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to GIMP MCP server: {e}")
            return False
    
    async def create_document(self) -> bool:
        """Create a new document for layer operations."""
        try:
            print("\n📄 Creating new document...")
            start_time = time.time()
            
            response = await self.session.call_tool("create_document", {
                "width": self.config["image_size"][0],
                "height": self.config["image_size"][1],
                "name": f"{self.config['demo_name']}-document",
                "color_mode": "RGB",
                "fill_color": "#FFFFFF"
            })
            
            self.document_id = response["document_id"]
            creation_time = time.time() - start_time
            
            print(f"✅ Document created successfully")
            print(f"📄 Document ID: {self.document_id}")
            print(f"⏱️ Creation time: {creation_time:.2f}s")
            
            self.performance_metrics["document_creation"] = creation_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create document: {e}")
            return False
    
    async def create_layer_structure(self) -> bool:
        """Create a comprehensive layer structure."""
        try:
            print("\n🗂️ Creating layer structure...")
            start_time = time.time()
            
            for i, layer_config in enumerate(self.config["layer_configurations"]):
                print(f"  Creating layer: {layer_config['name']}")
                
                # Create layer
                layer_response = await self.session.call_tool("create_layer", {
                    "document_id": self.document_id,
                    "name": layer_config["name"],
                    "layer_type": layer_config["type"],
                    "opacity": layer_config["opacity"],
                    "blend_mode": layer_config["blend_mode"]
                })
                
                layer_id = layer_response["layer_id"]
                
                # Store layer info
                layer_info = {
                    "id": layer_id,
                    "config": layer_config,
                    "index": i
                }
                self.created_layers.append(layer_info)
                
                print(f"    ✅ Layer '{layer_config['name']}' created (ID: {layer_id})")
            
            creation_time = time.time() - start_time
            print(f"✅ Layer structure created successfully")
            print(f"📁 Created {len(self.created_layers)} layers")
            print(f"⏱️ Layer creation time: {creation_time:.2f}s")
            
            self.performance_metrics["layer_creation"] = creation_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create layer structure: {e}")
            return False
    
    async def populate_layers_with_content(self) -> bool:
        """Add content to each layer to demonstrate layer effects."""
        try:
            print("\n🎨 Populating layers with content...")
            start_time = time.time()
            
            for layer_info in self.created_layers:
                layer_id = layer_info["id"]
                layer_config = layer_info["config"]
                layer_name = layer_config["name"]
                
                print(f"  Adding content to: {layer_name}")
                
                if layer_name == "Background":
                    # Fill background with solid color
                    await self.session.call_tool("draw_rectangle", {
                        "document_id": self.document_id,
                        "layer_id": layer_id,
                        "x": 0,
                        "y": 0,
                        "width": self.config["image_size"][0],
                        "height": self.config["image_size"][1],
                        "fill_color": layer_config["color"],
                        "stroke_color": None,
                        "stroke_width": 0
                    })
                
                elif layer_name == "Base Shapes":
                    # Add large geometric shapes
                    await self.session.call_tool("draw_rectangle", {
                        "document_id": self.document_id,
                        "layer_id": layer_id,
                        "x": 200,
                        "y": 200,
                        "width": 600,
                        "height": 300,
                        "fill_color": layer_config["color"],
                        "stroke_color": "#34495E",
                        "stroke_width": 3
                    })
                    
                    await self.session.call_tool("draw_ellipse", {
                        "document_id": self.document_id,
                        "layer_id": layer_id,
                        "center_x": 1200,
                        "center_y": 400,
                        "radius_x": 200,
                        "radius_y": 150,
                        "fill_color": layer_config["color"],
                        "stroke_color": "#34495E",
                        "stroke_width": 3
                    })
                
                elif layer_name == "Overlay Effects":
                    # Add overlay shapes that will blend with base
                    await self.session.call_tool("draw_ellipse", {
                        "document_id": self.document_id,
                        "layer_id": layer_id,
                        "center_x": 500,
                        "center_y": 350,
                        "radius_x": 300,
                        "radius_y": 250,
                        "fill_color": layer_config["color"],
                        "stroke_color": None,
                        "stroke_width": 0
                    })
                    
                    await self.session.call_tool("draw_rectangle", {
                        "document_id": self.document_id,
                        "layer_id": layer_id,
                        "x": 900,
                        "y": 600,
                        "width": 400,
                        "height": 200,
                        "fill_color": layer_config["color"],
                        "stroke_color": None,
                        "stroke_width": 0
                    })
                
                elif layer_name == "Highlights":
                    # Add highlight elements
                    await self.session.call_tool("draw_ellipse", {
                        "document_id": self.document_id,
                        "layer_id": layer_id,
                        "center_x": 400,
                        "center_y": 250,
                        "radius_x": 80,
                        "radius_y": 80,
                        "fill_color": layer_config["color"],
                        "stroke_color": None,
                        "stroke_width": 0
                    })
                    
                    await self.session.call_tool("draw_ellipse", {
                        "document_id": self.document_id,
                        "layer_id": layer_id,
                        "center_x": 1300,
                        "center_y": 300,
                        "radius_x": 60,
                        "radius_y": 60,
                        "fill_color": layer_config["color"],
                        "stroke_color": None,
                        "stroke_width": 0
                    })
                
                elif layer_name == "Text Layer":
                    # Add text elements (represented as shapes for now)
                    await self.session.call_tool("draw_rectangle", {
                        "document_id": self.document_id,
                        "layer_id": layer_id,
                        "x": 100,
                        "y": 900,
                        "width": 1720,
                        "height": 100,
                        "fill_color": layer_config["color"],
                        "stroke_color": "#BDC3C7",
                        "stroke_width": 2
                    })
                
                print(f"    ✅ Content added to '{layer_name}'")
            
            population_time = time.time() - start_time
            print(f"✅ Layer content population completed")
            print(f"⏱️ Population time: {population_time:.2f}s")
            
            self.performance_metrics["layer_population"] = population_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to populate layers: {e}")
            return False
    
    async def demonstrate_layer_properties(self) -> bool:
        """Demonstrate various layer property modifications."""
        try:
            print("\n🔧 Demonstrating layer property modifications...")
            start_time = time.time()
            
            # Test opacity changes
            print("  Testing opacity changes...")
            for layer_info in self.created_layers[1:3]:  # Skip background, test middle layers
                layer_id = layer_info["id"]
                layer_name = layer_info["config"]["name"]
                
                # Set different opacity values
                new_opacity = 0.5 if layer_info["config"]["opacity"] > 0.5 else 0.8
                
                await self.session.call_tool("set_layer_opacity", {
                    "document_id": self.document_id,
                    "layer_id": layer_id,
                    "opacity": new_opacity
                })
                
                print(f"    ✅ Set opacity for '{layer_name}' to {new_opacity}")
            
            # Test blend mode changes
            print("  Testing blend mode changes...")
            for i, layer_info in enumerate(self.created_layers[2:4]):  # Test overlay layers
                layer_id = layer_info["id"]
                layer_name = layer_info["config"]["name"]
                
                # Cycle through different blend modes
                blend_mode = self.config["blend_modes"][i % len(self.config["blend_modes"])]
                
                await self.session.call_tool("set_layer_blend_mode", {
                    "document_id": self.document_id,
                    "layer_id": layer_id,
                    "blend_mode": blend_mode
                })
                
                print(f"    ✅ Set blend mode for '{layer_name}' to '{blend_mode}'")
            
            # Test visibility changes
            print("  Testing visibility changes...")
            if len(self.created_layers) > 3:
                layer_info = self.created_layers[3]
                layer_id = layer_info["id"]
                layer_name = layer_info["config"]["name"]
                
                # Toggle visibility
                await self.session.call_tool("set_layer_visibility", {
                    "document_id": self.document_id,
                    "layer_id": layer_id,
                    "visible": False
                })
                
                print(f"    ✅ Hidden layer '{layer_name}'")
                
                # Wait a moment then show again
                await asyncio.sleep(1)
                
                await self.session.call_tool("set_layer_visibility", {
                    "document_id": self.document_id,
                    "layer_id": layer_id,
                    "visible": True
                })
                
                print(f"    ✅ Restored visibility for layer '{layer_name}'")
            
            properties_time = time.time() - start_time
            print(f"✅ Layer property modifications completed")
            print(f"⏱️ Properties time: {properties_time:.2f}s")
            
            self.performance_metrics["layer_properties"] = properties_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to demonstrate layer properties: {e}")
            return False
    
    async def demonstrate_layer_management(self) -> bool:
        """Demonstrate layer duplication, movement, and organization."""
        try:
            print("\n📋 Demonstrating layer management operations...")
            start_time = time.time()
            
            # Duplicate a layer
            if len(self.created_layers) > 1:
                original_layer = self.created_layers[1]
                original_id = original_layer["id"]
                original_name = original_layer["config"]["name"]
                
                print(f"  Duplicating layer '{original_name}'...")
                
                duplicate_response = await self.session.call_tool("duplicate_layer", {
                    "document_id": self.document_id,
                    "layer_id": original_id,
                    "new_name": f"{original_name} Copy"
                })
                
                duplicate_id = duplicate_response["layer_id"]
                
                # Add duplicate to our tracking
                duplicate_info = {
                    "id": duplicate_id,
                    "config": {
                        "name": f"{original_name} Copy",
                        "type": original_layer["config"]["type"],
                        "opacity": 0.7,
                        "blend_mode": "overlay",
                        "color": "#9B59B6"
                    },
                    "index": len(self.created_layers)
                }
                self.created_layers.append(duplicate_info)
                
                print(f"    ✅ Duplicated layer '{original_name}' (New ID: {duplicate_id})")
                
                # Modify the duplicate to show it's different
                await self.session.call_tool("set_layer_opacity", {
                    "document_id": self.document_id,
                    "layer_id": duplicate_id,
                    "opacity": 0.4
                })
                
                await self.session.call_tool("set_layer_blend_mode", {
                    "document_id": self.document_id,
                    "layer_id": duplicate_id,
                    "blend_mode": "overlay"
                })
                
                print(f"    ✅ Modified duplicate layer properties")
            
            # Move layers (reorder)
            print("  Demonstrating layer reordering...")
            if len(self.created_layers) > 2:
                layer_to_move = self.created_layers[-1]  # Move the last layer
                layer_id = layer_to_move["id"]
                layer_name = layer_to_move["config"]["name"]
                
                await self.session.call_tool("move_layer", {
                    "document_id": self.document_id,
                    "layer_id": layer_id,
                    "new_position": 1  # Move to position 1 (near top)
                })
                
                print(f"    ✅ Moved layer '{layer_name}' to position 1")
            
            # Get layer information for verification
            print("  Retrieving layer information...")
            for layer_info in self.created_layers:
                layer_id = layer_info["id"]
                layer_name = layer_info["config"]["name"]
                
                info_response = await self.session.call_tool("get_layer_info", {
                    "document_id": self.document_id,
                    "layer_id": layer_id
                })
                
                print(f"    📄 Layer '{layer_name}': {info_response}")
            
            management_time = time.time() - start_time
            print(f"✅ Layer management operations completed")
            print(f"⏱️ Management time: {management_time:.2f}s")
            
            self.performance_metrics["layer_management"] = management_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to demonstrate layer management: {e}")
            return False
    
    async def save_layer_variations(self) -> bool:
        """Save different variations showing layer effects."""
        try:
            print("\n💾 Saving layer variations...")
            start_time = time.time()
            
            # Save original version
            original_path = self.output_dir / f"{self.config['demo_name']}-original.png"
            await self.session.call_tool("export_document", {
                "document_id": self.document_id,
                "file_path": str(original_path),
                "format": "PNG"
            })
            
            # Hide some layers and save variation
            layers_to_hide = self.created_layers[2:4]  # Hide middle layers
            for layer_info in layers_to_hide:
                await self.session.call_tool("set_layer_visibility", {
                    "document_id": self.document_id,
                    "layer_id": layer_info["id"],
                    "visible": False
                })
            
            variation1_path = self.output_dir / f"{self.config['demo_name']}-variation1.png"
            await self.session.call_tool("export_document", {
                "document_id": self.document_id,
                "file_path": str(variation1_path),
                "format": "PNG"
            })
            
            # Restore visibility and change blend modes
            for layer_info in layers_to_hide:
                await self.session.call_tool("set_layer_visibility", {
                    "document_id": self.document_id,
                    "layer_id": layer_info["id"],
                    "visible": True
                })
                
                await self.session.call_tool("set_layer_blend_mode", {
                    "document_id": self.document_id,
                    "layer_id": layer_info["id"],
                    "blend_mode": "screen"
                })
            
            variation2_path = self.output_dir / f"{self.config['demo_name']}-variation2.png"
            await self.session.call_tool("export_document", {
                "document_id": self.document_id,
                "file_path": str(variation2_path),
                "format": "PNG"
            })
            
            # Save the XCF file with all layers
            xcf_path = self.output_dir / f"{self.config['demo_name']}.xcf"
            await self.session.call_tool("save_document", {
                "document_id": self.document_id,
                "file_path": str(xcf_path)
            })
            
            save_time = time.time() - start_time
            print(f"✅ Layer variations saved successfully")
            print(f"🖼️ Original: {original_path}")
            print(f"🖼️ Variation 1: {variation1_path}")
            print(f"🖼️ Variation 2: {variation2_path}")
            print(f"📄 XCF file: {xcf_path}")
            print(f"⏱️ Save time: {save_time:.2f}s")
            
            self.performance_metrics["save_variations"] = save_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save layer variations: {e}")
            return False
    
    async def generate_layer_report(self) -> bool:
        """Generate a comprehensive layer operations report."""
        try:
            print("\n📊 Generating layer operations report...")
            
            total_time = sum(self.performance_metrics.values())
            
            report = {
                "demo_name": self.config["demo_name"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "document_info": {
                    "document_id": self.document_id,
                    "image_size": self.config["image_size"],
                    "layers_created": len(self.created_layers)
                },
                "layer_details": [
                    {
                        "name": layer["config"]["name"],
                        "id": layer["id"],
                        "type": layer["config"]["type"],
                        "opacity": layer["config"]["opacity"],
                        "blend_mode": layer["config"]["blend_mode"],
                        "color": layer["config"]["color"]
                    }
                    for layer in self.created_layers
                ],
                "performance_metrics": self.performance_metrics,
                "total_time": total_time,
                "operations_performed": [
                    "Document Creation",
                    "Layer Structure Creation",
                    "Layer Content Population",
                    "Layer Property Modifications",
                    "Layer Management Operations",
                    "Layer Variations Export"
                ],
                "files_generated": [
                    f"{self.config['demo_name']}-original.png",
                    f"{self.config['demo_name']}-variation1.png",
                    f"{self.config['demo_name']}-variation2.png",
                    f"{self.config['demo_name']}.xcf"
                ]
            }
            
            # Save report
            report_path = self.output_dir / f"{self.config['demo_name']}-report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            print(f"📊 Layer Operations Summary:")
            print(f"   Total execution time: {total_time:.2f}s")
            print(f"   Layers created: {len(self.created_layers)}")
            print(f"   Operations performed: {len(self.performance_metrics)}")
            print(f"   Files generated: {len(report['files_generated'])}")
            print(f"   Average operation time: {total_time / len(self.performance_metrics):.2f}s")
            
            print(f"📄 Layer operations report saved: {report_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate layer report: {e}")
            return False
    
    async def cleanup(self) -> bool:
        """Clean up resources and close connections."""
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
        """Run the complete layer operations demonstration."""
        try:
            print("🚀 Starting Layer Operations Demonstration")
            print("=" * 50)
            
            # Connect to server
            if not await self.connect_to_server():
                return False
            
            # Create document
            if not await self.create_document():
                return False
            
            # Create layer structure
            if not await self.create_layer_structure():
                return False
            
            # Populate layers with content
            if not await self.populate_layers_with_content():
                return False
            
            # Demonstrate layer properties
            if not await self.demonstrate_layer_properties():
                return False
            
            # Demonstrate layer management
            if not await self.demonstrate_layer_management():
                return False
            
            # Save variations
            if not await self.save_layer_variations():
                return False
            
            # Generate report
            if not await self.generate_layer_report():
                return False
            
            print("\n🎉 Layer Operations Demonstration completed successfully!")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return False
            
        finally:
            await self.cleanup()

async def main():
    """Main entry point for the layer operations demonstration."""
    print("GIMP MCP Server - Layer Operations Demonstration")
    print("=" * 60)
    
    # Create and run the demo
    demo = LayerOperationsDemo(DEMO_CONFIG)
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