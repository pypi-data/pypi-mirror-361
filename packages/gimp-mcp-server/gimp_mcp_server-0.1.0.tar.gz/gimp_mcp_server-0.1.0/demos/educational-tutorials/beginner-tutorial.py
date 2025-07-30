#!/usr/bin/env python3
"""
GIMP MCP Server - Beginner Tutorial

This tutorial provides a gentle introduction to the GIMP MCP server for beginners.
It covers fundamental concepts and basic operations in a step-by-step format:
- Understanding MCP connections and server capabilities
- Basic document creation and management
- Simple drawing operations and color management
- Layer basics and export functionality
- Error handling and troubleshooting

Perfect for users new to GIMP automation and MCP integration.
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

# Tutorial configuration
TUTORIAL_CONFIG = {
    "output_dir": Path(__file__).parent / "outputs",
    "tutorial_name": "beginner-tutorial",
    "lessons": [
        {
            "id": 1,
            "title": "Getting Started - Server Connection",
            "description": "Learn how to connect to the GIMP MCP server and discover its capabilities",
            "objectives": [
                "Establish connection to GIMP MCP server",
                "Discover available tools and resources",
                "Understand basic MCP concepts"
            ]
        },
        {
            "id": 2,
            "title": "Your First Document",
            "description": "Create your first GIMP document and understand document management",
            "objectives": [
                "Create a new document",
                "Understand document properties",
                "Learn about coordinate systems"
            ]
        },
        {
            "id": 3,
            "title": "Basic Drawing Operations",
            "description": "Learn to draw simple shapes and understand drawing tools",
            "objectives": [
                "Draw rectangles and ellipses",
                "Understand color specification",
                "Learn about fill and stroke properties"
            ]
        },
        {
            "id": 4,
            "title": "Working with Layers",
            "description": "Introduction to layers - the foundation of GIMP editing",
            "objectives": [
                "Create and manage layers",
                "Understand layer properties",
                "Learn layer visibility and opacity"
            ]
        },
        {
            "id": 5,
            "title": "Colors and Painting",
            "description": "Learn about color management and basic painting operations",
            "objectives": [
                "Set foreground and background colors",
                "Sample colors from images",
                "Create simple brush strokes"
            ]
        },
        {
            "id": 6,
            "title": "Saving and Exporting",
            "description": "Learn how to save your work and export in different formats",
            "objectives": [
                "Save documents in GIMP format",
                "Export to common image formats",
                "Understand format options"
            ]
        }
    ]
}

class BeginnerTutorial:
    """
    Interactive beginner tutorial for GIMP MCP server.
    
    This class provides step-by-step lessons with detailed explanations,
    practical exercises, and verification of learning objectives.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = config["output_dir"]
        self.session = None
        self.current_document_id = None
        self.current_layer_id = None
        self.lesson_progress = {}
        self.tutorial_log = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
    def log_step(self, lesson_id: int, step: str, success: bool, details: str = ""):
        """Log tutorial progress for review."""
        entry = {
            "lesson_id": lesson_id,
            "step": step,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.tutorial_log.append(entry)
        
        # Print immediate feedback
        status = "✅" if success else "❌"
        print(f"   {status} {step}")
        if details and not success:
            print(f"      💡 {details}")
    
    def print_lesson_header(self, lesson: Dict[str, Any]):
        """Print formatted lesson header."""
        print(f"\n{'='*60}")
        print(f"📚 LESSON {lesson['id']}: {lesson['title']}")
        print(f"{'='*60}")
        print(f"📖 {lesson['description']}")
        print(f"\n🎯 Learning Objectives:")
        for objective in lesson['objectives']:
            print(f"   • {objective}")
        print(f"\n▶️ Let's begin!\n")
    
    def wait_for_user(self, message: str = "Press Enter to continue..."):
        """Pause for user interaction."""
        input(f"\n⏸️  {message}")
    
    async def lesson_1_server_connection(self) -> bool:
        """Lesson 1: Getting Started - Server Connection."""
        lesson = self.config["lessons"][0]
        self.print_lesson_header(lesson)
        
        print("🔗 In this lesson, we'll learn how to connect to the GIMP MCP server.")
        print("The MCP (Model Context Protocol) allows AI assistants to control GIMP.")
        
        self.wait_for_user()
        
        try:
            # Step 1: Establish connection
            print("\n📡 Step 1: Connecting to GIMP MCP Server")
            print("We'll create a connection using the MCP client library...")
            
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "gimp_mcp.server"],
                env=None
            )
            
            self.session = await stdio_client(server_params)
            self.log_step(1, "Server connection established", True)
            
            self.wait_for_user("Great! We're connected. Let's explore what the server can do.")
            
            # Step 2: Discover tools
            print("\n🔧 Step 2: Discovering Available Tools")
            print("The server provides 'tools' - these are operations we can perform...")
            
            tools_response = await self.session.list_tools()
            tool_count = len(tools_response.tools)
            
            print(f"\n📋 Found {tool_count} available tools:")
            for i, tool in enumerate(tools_response.tools[:5]):  # Show first 5
                print(f"   {i+1}. {tool.name}: {tool.description}")
            
            if tool_count > 5:
                print(f"   ... and {tool_count - 5} more tools!")
            
            self.log_step(1, f"Discovered {tool_count} tools", True)
            
            self.wait_for_user("Excellent! Now let's check the resources.")
            
            # Step 3: Discover resources
            print("\n📊 Step 3: Discovering Available Resources")
            print("Resources provide real-time information about GIMP's state...")
            
            try:
                resources_response = await self.session.list_resources()
                resource_count = len(resources_response.resources)
                
                print(f"\n📋 Found {resource_count} available resources:")
                for resource in resources_response.resources[:3]:  # Show first 3
                    print(f"   • {resource.uri}: {resource.description}")
                
                self.log_step(1, f"Discovered {resource_count} resources", True)
                
            except Exception as e:
                print(f"⚠️ Could not list resources: {e}")
                print("This is normal - some servers may not support all features.")
                self.log_step(1, "Resource discovery (optional)", True, "Some features not available")
            
            self.wait_for_user("Perfect! You've completed your first lesson.")
            
            # Step 4: Test basic operation
            print("\n🧪 Step 4: Testing Basic Operation")
            print("Let's test our connection with a simple operation...")
            
            response = await self.session.call_tool("list_documents", {})
            print(f"✅ Server responded: {response}")
            
            self.log_step(1, "Basic operation test", True)
            
            print(f"\n🎉 Lesson 1 Complete!")
            print(f"You've successfully:")
            print(f"   ✅ Connected to the GIMP MCP server")
            print(f"   ✅ Discovered {tool_count} tools")
            print(f"   ✅ Tested basic operations")
            print(f"   ✅ Learned about MCP concepts")
            
            return True
            
        except Exception as e:
            self.log_step(1, "Connection failed", False, str(e))
            print(f"\n❌ Connection failed: {e}")
            print(f"\n💡 Troubleshooting Tips:")
            print(f"   • Make sure GIMP is installed")
            print(f"   • Check that Python can find the gimp_mcp module")
            print(f"   • Verify GIMP supports Python scripting")
            return False
    
    async def lesson_2_first_document(self) -> bool:
        """Lesson 2: Your First Document."""
        lesson = self.config["lessons"][1]
        self.print_lesson_header(lesson)
        
        print("📄 In this lesson, we'll create our first GIMP document.")
        print("A document is like a canvas where we create our artwork.")
        
        self.wait_for_user()
        
        try:
            # Step 1: Create document
            print("\n🎨 Step 1: Creating a New Document")
            print("We'll create a document that's 800x600 pixels - perfect for learning!")
            
            create_response = await self.session.call_tool("create_document", {
                "width": 800,
                "height": 600,
                "name": "My First Document",
                "color_mode": "RGB"
            })
            
            self.current_document_id = create_response["document_id"]
            print(f"✅ Document created with ID: {self.current_document_id}")
            
            self.log_step(2, "Document creation", True)
            
            self.wait_for_user("Great! Your document is ready. Let's learn about its properties.")
            
            # Step 2: Understand document properties
            print("\n📏 Step 2: Understanding Document Properties")
            print("Let's examine what we just created...")
            
            doc_info = await self.session.call_tool("get_document_info", {
                "document_id": self.current_document_id
            })
            
            print(f"\n📋 Document Information:")
            print(f"   • Width: {doc_info.get('width', 'unknown')} pixels")
            print(f"   • Height: {doc_info.get('height', 'unknown')} pixels")
            print(f"   • Color Mode: {doc_info.get('color_mode', 'unknown')}")
            print(f"   • Layers: {doc_info.get('layers', 'unknown')}")
            
            self.log_step(2, "Document properties examined", True)
            
            self.wait_for_user("Excellent! Now you understand document basics.")
            
            # Step 3: Coordinate system explanation
            print("\n🗺️ Step 3: Understanding the Coordinate System")
            print("GIMP uses a coordinate system where:")
            print("   • (0, 0) is the top-left corner")
            print("   • X increases going right")
            print("   • Y increases going down")
            print("   • Our 800x600 document goes from (0,0) to (800,600)")
            
            print(f"\n🎯 Key Points:")
            print(f"   • Top-left: (0, 0)")
            print(f"   • Top-right: (800, 0)")
            print(f"   • Bottom-left: (0, 600)")
            print(f"   • Bottom-right: (800, 600)")
            print(f"   • Center: (400, 300)")
            
            self.log_step(2, "Coordinate system explained", True)
            
            print(f"\n🎉 Lesson 2 Complete!")
            print(f"You've successfully:")
            print(f"   ✅ Created your first GIMP document")
            print(f"   ✅ Learned about document properties")
            print(f"   ✅ Understood the coordinate system")
            
            return True
            
        except Exception as e:
            self.log_step(2, "Document creation failed", False, str(e))
            print(f"\n❌ Document creation failed: {e}")
            return False
    
    async def lesson_3_basic_drawing(self) -> bool:
        """Lesson 3: Basic Drawing Operations."""
        lesson = self.config["lessons"][2]
        self.print_lesson_header(lesson)
        
        print("🎨 In this lesson, we'll learn to draw basic shapes.")
        print("We'll create rectangles and circles with different colors!")
        
        if not self.current_document_id:
            print("⚠️ We need a document first. Let me create one...")
            await self.lesson_2_first_document()
        
        self.wait_for_user()
        
        try:
            # Step 1: Create a drawing layer
            print("\n🗂️ Step 1: Creating a Layer for Drawing")
            print("Layers are like transparent sheets where we draw things...")
            
            layer_response = await self.session.call_tool("create_layer", {
                "document_id": self.current_document_id,
                "name": "Drawing Layer",
                "layer_type": "RGB"
            })
            
            self.current_layer_id = layer_response["layer_id"]
            print(f"✅ Drawing layer created with ID: {self.current_layer_id}")
            
            self.log_step(3, "Drawing layer created", True)
            
            self.wait_for_user("Perfect! Now let's draw our first shape.")
            
            # Step 2: Draw a rectangle
            print("\n⬛ Step 2: Drawing a Rectangle")
            print("We'll draw a blue rectangle in the upper-left area...")
            
            await self.session.call_tool("draw_rectangle", {
                "document_id": self.current_document_id,
                "layer_id": self.current_layer_id,
                "x": 50,              # 50 pixels from left
                "y": 50,              # 50 pixels from top
                "width": 200,         # 200 pixels wide
                "height": 150,        # 150 pixels tall
                "fill_color": "#3498DB",  # Nice blue color
                "stroke_color": "#2980B9",  # Darker blue border
                "stroke_width": 3
            })
            
            print(f"✅ Blue rectangle drawn at position (50, 50)")
            print(f"   • Size: 200x150 pixels")
            print(f"   • Color: #3498DB (blue)")
            print(f"   • Border: 3 pixels thick")
            
            self.log_step(3, "Rectangle drawn", True)
            
            self.wait_for_user("Great! Now let's add a circle.")
            
            # Step 3: Draw a circle
            print("\n⭕ Step 3: Drawing a Circle")
            print("We'll draw a red circle in the upper-right area...")
            
            await self.session.call_tool("draw_ellipse", {
                "document_id": self.current_document_id,
                "layer_id": self.current_layer_id,
                "center_x": 600,      # Center X position
                "center_y": 150,      # Center Y position
                "radius_x": 80,       # Width radius
                "radius_y": 80,       # Height radius (same = perfect circle)
                "fill_color": "#E74C3C",  # Nice red color
                "stroke_color": "#C0392B",  # Darker red border
                "stroke_width": 2
            })
            
            print(f"✅ Red circle drawn at center (600, 150)")
            print(f"   • Radius: 80 pixels (diameter: 160)")
            print(f"   • Color: #E74C3C (red)")
            print(f"   • Border: 2 pixels thick")
            
            self.log_step(3, "Circle drawn", True)
            
            self.wait_for_user("Awesome! Let's understand color codes.")
            
            # Step 4: Understanding colors
            print("\n🌈 Step 4: Understanding Color Codes")
            print("We use hex color codes to specify colors:")
            print("   • #FF0000 = Pure Red")
            print("   • #00FF00 = Pure Green") 
            print("   • #0000FF = Pure Blue")
            print("   • #FFFFFF = White")
            print("   • #000000 = Black")
            print("   • #3498DB = Nice Blue (what we used)")
            print("   • #E74C3C = Nice Red (what we used)")
            
            # Draw a few more shapes with different colors
            print("\nLet's draw a few more shapes to practice colors...")
            
            # Green ellipse
            await self.session.call_tool("draw_ellipse", {
                "document_id": self.current_document_id,
                "layer_id": self.current_layer_id,
                "center_x": 200,
                "center_y": 400,
                "radius_x": 100,
                "radius_y": 60,
                "fill_color": "#2ECC71",  # Green
                "stroke_color": None,
                "stroke_width": 0
            })
            
            # Orange rectangle
            await self.session.call_tool("draw_rectangle", {
                "document_id": self.current_document_id,
                "layer_id": self.current_layer_id,
                "x": 400,
                "y": 350,
                "width": 150,
                "height": 100,
                "fill_color": "#F39C12",  # Orange
                "stroke_color": "#E67E22",  # Darker orange
                "stroke_width": 2
            })
            
            print(f"✅ Added green ellipse and orange rectangle")
            
            self.log_step(3, "Multiple shapes with colors", True)
            
            print(f"\n🎉 Lesson 3 Complete!")
            print(f"You've successfully:")
            print(f"   ✅ Created a drawing layer")
            print(f"   ✅ Drew rectangles and circles")
            print(f"   ✅ Used different colors and borders")
            print(f"   ✅ Learned about hex color codes")
            
            return True
            
        except Exception as e:
            self.log_step(3, "Drawing failed", False, str(e))
            print(f"\n❌ Drawing failed: {e}")
            return False
    
    async def lesson_4_working_with_layers(self) -> bool:
        """Lesson 4: Working with Layers."""
        lesson = self.config["lessons"][3]
        self.print_lesson_header(lesson)
        
        print("🗂️ In this lesson, we'll explore layers - the foundation of GIMP editing.")
        print("Think of layers like transparent sheets of paper stacked on top of each other!")
        
        self.wait_for_user()
        
        try:
            # Step 1: Create multiple layers
            print("\n📚 Step 1: Creating Multiple Layers")
            print("Let's create a few layers to understand how they work...")
            
            # Background layer
            bg_layer = await self.session.call_tool("create_layer", {
                "document_id": self.current_document_id,
                "name": "Background",
                "layer_type": "RGB"
            })
            bg_layer_id = bg_layer["layer_id"]
            
            # Fill background with light color
            await self.session.call_tool("draw_rectangle", {
                "document_id": self.current_document_id,
                "layer_id": bg_layer_id,
                "x": 0,
                "y": 0,
                "width": 800,
                "height": 600,
                "fill_color": "#ECF0F1",  # Light gray
                "stroke_color": None,
                "stroke_width": 0
            })
            
            # Middle layer
            mid_layer = await self.session.call_tool("create_layer", {
                "document_id": self.current_document_id,
                "name": "Middle Layer",
                "layer_type": "RGB"
            })
            mid_layer_id = mid_layer["layer_id"]
            
            # Foreground layer
            fg_layer = await self.session.call_tool("create_layer", {
                "document_id": self.current_document_id,
                "name": "Foreground",
                "layer_type": "RGB"
            })
            fg_layer_id = fg_layer["layer_id"]
            
            print(f"✅ Created 3 layers:")
            print(f"   • Background (filled with light gray)")
            print(f"   • Middle Layer (empty)")
            print(f"   • Foreground (empty)")
            
            self.log_step(4, "Multiple layers created", True)
            
            self.wait_for_user("Great! Now let's add content to each layer.")
            
            # Step 2: Add content to layers
            print("\n🎨 Step 2: Adding Content to Each Layer")
            
            # Add to middle layer
            await self.session.call_tool("draw_ellipse", {
                "document_id": self.current_document_id,
                "layer_id": mid_layer_id,
                "center_x": 400,
                "center_y": 300,
                "radius_x": 250,
                "radius_y": 200,
                "fill_color": "#3498DB",  # Blue
                "stroke_color": None,
                "stroke_width": 0
            })
            
            # Add to foreground layer
            await self.session.call_tool("draw_rectangle", {
                "document_id": self.current_document_id,
                "layer_id": fg_layer_id,
                "x": 300,
                "y": 200,
                "width": 200,
                "height": 200,
                "fill_color": "#E74C3C",  # Red
                "stroke_color": "#FFFFFF",  # White border
                "stroke_width": 5
            })
            
            print(f"✅ Added content:")
            print(f"   • Blue ellipse on middle layer")
            print(f"   • Red square on foreground layer")
            
            self.log_step(4, "Content added to layers", True)
            
            self.wait_for_user("Perfect! Now let's explore layer properties.")
            
            # Step 3: Modify layer opacity
            print("\n👻 Step 3: Playing with Layer Opacity")
            print("Opacity controls how transparent a layer is...")
            print("1.0 = completely opaque, 0.0 = completely transparent")
            
            # Make foreground layer semi-transparent
            await self.session.call_tool("set_layer_opacity", {
                "document_id": self.current_document_id,
                "layer_id": fg_layer_id,
                "opacity": 0.7  # 70% opaque
            })
            
            print(f"✅ Set foreground layer opacity to 70%")
            print(f"   Notice how it becomes semi-transparent!")
            
            self.log_step(4, "Layer opacity modified", True)
            
            self.wait_for_user("Cool effect! Let's try layer visibility.")
            
            # Step 4: Layer visibility
            print("\n👁️ Step 4: Controlling Layer Visibility")
            print("We can hide and show layers...")
            
            # Hide middle layer
            await self.session.call_tool("set_layer_visibility", {
                "document_id": self.current_document_id,
                "layer_id": mid_layer_id,
                "visible": False
            })
            
            print(f"✅ Hidden the middle layer (blue ellipse)")
            print(f"   The blue ellipse should disappear!")
            
            self.wait_for_user("The blue ellipse is hidden! Let's bring it back.")
            
            # Show middle layer again
            await self.session.call_tool("set_layer_visibility", {
                "document_id": self.current_document_id,
                "layer_id": mid_layer_id,
                "visible": True
            })
            
            print(f"✅ Made the middle layer visible again")
            
            self.log_step(4, "Layer visibility controlled", True)
            
            # Step 5: Layer information
            print("\n📋 Step 5: Getting Layer Information")
            print("Let's examine one of our layers...")
            
            layer_info = await self.session.call_tool("get_layer_info", {
                "document_id": self.current_document_id,
                "layer_id": fg_layer_id
            })
            
            print(f"📋 Foreground Layer Info:")
            print(f"   • Name: {layer_info.get('name', 'unknown')}")
            print(f"   • Opacity: {layer_info.get('opacity', 'unknown')}")
            print(f"   • Visible: {layer_info.get('visible', 'unknown')}")
            print(f"   • Blend Mode: {layer_info.get('blend_mode', 'unknown')}")
            
            self.log_step(4, "Layer information retrieved", True)
            
            print(f"\n🎉 Lesson 4 Complete!")
            print(f"You've successfully:")
            print(f"   ✅ Created multiple layers")
            print(f"   ✅ Added content to different layers")
            print(f"   ✅ Controlled layer opacity")
            print(f"   ✅ Managed layer visibility")
            print(f"   ✅ Retrieved layer information")
            
            return True
            
        except Exception as e:
            self.log_step(4, "Layer operations failed", False, str(e))
            print(f"\n❌ Layer operations failed: {e}")
            return False
    
    async def lesson_5_colors_and_painting(self) -> bool:
        """Lesson 5: Colors and Painting."""
        lesson = self.config["lessons"][4]
        self.print_lesson_header(lesson)
        
        print("🎨 In this lesson, we'll explore color management and painting.")
        print("We'll learn about foreground/background colors and create brush strokes!")
        
        self.wait_for_user()
        
        try:
            # Step 1: Setting colors
            print("\n🌈 Step 1: Setting Foreground and Background Colors")
            print("GIMP has two active colors: foreground (for drawing) and background (for erasing)")
            
            # Set foreground color
            await self.session.call_tool("set_foreground_color", {
                "color": "#9B59B6"  # Purple
            })
            
            # Set background color
            await self.session.call_tool("set_background_color", {
                "color": "#F1C40F"  # Yellow
            })
            
            print(f"✅ Set colors:")
            print(f"   • Foreground: #9B59B6 (purple)")
            print(f"   • Background: #F1C40F (yellow)")
            
            self.log_step(5, "Colors set", True)
            
            self.wait_for_user("Colors are set! Now let's create some brush strokes.")
            
            # Step 2: Create painting layer
            print("\n🖌️ Step 2: Creating a Painting Layer")
            
            paint_layer = await self.session.call_tool("create_layer", {
                "document_id": self.current_document_id,
                "name": "Painting",
                "layer_type": "RGB"
            })
            paint_layer_id = paint_layer["layer_id"]
            
            print(f"✅ Created painting layer")
            
            self.log_step(5, "Painting layer created", True)
            
            # Step 3: Create brush strokes
            print("\n🖌️ Step 3: Creating Brush Strokes")
            print("Let's paint some curved lines...")
            
            # Curved brush stroke
            curve_points = [
                (100, 500), (150, 450), (200, 400), (250, 380),
                (300, 390), (350, 420), (400, 450), (450, 460)
            ]
            
            await self.session.call_tool("apply_brush_stroke", {
                "document_id": self.current_document_id,
                "layer_id": paint_layer_id,
                "points": curve_points,
                "brush_name": "basic",
                "size": 15,
                "color": "#9B59B6"  # Use our foreground color
            })
            
            print(f"✅ Created curved brush stroke with {len(curve_points)} points")
            
            # Straight brush stroke
            straight_points = [(500, 500), (700, 400)]
            
            await self.session.call_tool("apply_brush_stroke", {
                "document_id": self.current_document_id,
                "layer_id": paint_layer_id,
                "points": straight_points,
                "brush_name": "basic",
                "size": 20,
                "color": "#E67E22"  # Orange
            })
            
            print(f"✅ Created straight brush stroke")
            
            self.log_step(5, "Brush strokes created", True)
            
            self.wait_for_user("Beautiful strokes! Let's learn about color sampling.")
            
            # Step 4: Color sampling
            print("\n🎯 Step 4: Sampling Colors from the Image")
            print("We can pick colors from existing parts of our image...")
            
            # Sample color from one of our shapes
            sampled_color = await self.session.call_tool("sample_color", {
                "document_id": self.current_document_id,
                "x": 400,  # Center of our blue ellipse
                "y": 300,
                "sample_merged": True  # Sample from all visible layers
            })
            
            print(f"✅ Sampled color from position (400, 300):")
            print(f"   • Color: {sampled_color}")
            
            self.log_step(5, "Color sampled", True)
            
            # Step 5: Get color palette info
            print("\n🎨 Step 5: Working with Color Palettes")
            print("GIMP can work with color palettes for consistent color schemes...")
            
            try:
                palette_info = await self.session.call_tool("get_active_palette", {})
                print(f"✅ Active palette information:")
                print(f"   • Palette: {palette_info}")
            except Exception as e:
                print(f"⚠️ Palette info not available: {e}")
                print("This is normal - palette features may vary by system.")
            
            self.log_step(5, "Palette information retrieved", True)
            
            print(f"\n🎉 Lesson 5 Complete!")
            print(f"You've successfully:")
            print(f"   ✅ Set foreground and background colors")
            print(f"   ✅ Created brush strokes with different sizes")
            print(f"   ✅ Learned about point-based drawing")
            print(f"   ✅ Sampled colors from existing artwork")
            print(f"   ✅ Explored color palette concepts")
            
            return True
            
        except Exception as e:
            self.log_step(5, "Color operations failed", False, str(e))
            print(f"\n❌ Color operations failed: {e}")
            return False
    
    async def lesson_6_saving_and_exporting(self) -> bool:
        """Lesson 6: Saving and Exporting."""
        lesson = self.config["lessons"][5]
        self.print_lesson_header(lesson)
        
        print("💾 In this lesson, we'll learn how to save our work and export images.")
        print("This is crucial for preserving your artwork and sharing it with others!")
        
        self.wait_for_user()
        
        try:
            # Step 1: Save in GIMP format
            print("\n💾 Step 1: Saving in GIMP Format (.xcf)")
            print("The .xcf format preserves all layers, transparency, and editing capability...")
            
            xcf_path = self.output_dir / f"{self.config['tutorial_name']}-artwork.xcf"
            
            await self.session.call_tool("save_document", {
                "document_id": self.current_document_id,
                "file_path": str(xcf_path)
            })
            
            print(f"✅ Saved as GIMP file: {xcf_path}")
            print(f"   • Preserves all layers and properties")
            print(f"   • Can be reopened for further editing")
            print(f"   • Best for work-in-progress files")
            
            self.log_step(6, "GIMP format save", True)
            
            self.wait_for_user("Excellent! Now let's export to common image formats.")
            
            # Step 2: Export as PNG
            print("\n🖼️ Step 2: Exporting as PNG")
            print("PNG is great for images with transparency and sharp edges...")
            
            png_path = self.output_dir / f"{self.config['tutorial_name']}-final.png"
            
            await self.session.call_tool("export_document", {
                "document_id": self.current_document_id,
                "file_path": str(png_path),
                "format": "PNG",
                "options": {
                    "optimize": True,
                    "compression": 6
                }
            })
            
            print(f"✅ Exported as PNG: {png_path}")
            print(f"   • Supports transparency")
            print(f"   • Lossless compression")
            print(f"   • Great for web graphics")
            
            self.log_step(6, "PNG export", True)
            
            self.wait_for_user("Perfect! Let's try JPEG format too.")
            
            # Step 3: Export as JPEG
            print("\n📷 Step 3: Exporting as JPEG")
            print("JPEG is ideal for photos and images with many colors...")
            
            jpg_path = self.output_dir / f"{self.config['tutorial_name']}-photo.jpg"
            
            await self.session.call_tool("export_document", {
                "document_id": self.current_document_id,
                "file_path": str(jpg_path),
                "format": "JPEG",
                "options": {
                    "quality": 90,
                    "optimize": True
                }
            })
            
            print(f"✅ Exported as JPEG: {jpg_path}")
            print(f"   • Smaller file sizes")
            print(f"   • Good for photos")
            print(f"   • No transparency support")
            
            self.log_step(6, "JPEG export", True)
            
            # Step 4: Understanding format differences
            print("\n📊 Step 4: Understanding Format Differences")
            print("Here's when to use each format:")
            print("")
            print("📄 XCF (GIMP Native):")
            print("   • Preserves layers, transparency, and all editing data")
            print("   • Use for: Work in progress, files you'll edit again")
            print("   • File size: Largest")
            print("")
            print("🖼️ PNG:")
            print("   • Supports transparency")
            print("   • Lossless compression")
            print("   • Use for: Graphics, logos, images with text")
            print("   • File size: Medium")
            print("")
            print("📷 JPEG:")
            print("   • Lossy compression (some quality loss)")
            print("   • No transparency")
            print("   • Use for: Photos, images with many colors")
            print("   • File size: Smallest")
            
            self.log_step(6, "Format education", True)
            
            # Step 5: Clean up
            print("\n🧹 Step 5: Cleaning Up")
            print("Let's close our document properly...")
            
            await self.session.call_tool("close_document", {
                "document_id": self.current_document_id
            })
            
            print(f"✅ Document closed properly")
            print(f"   • Frees up memory")
            print(f"   • Good practice for resource management")
            
            self.log_step(6, "Document cleanup", True)
            
            print(f"\n🎉 Lesson 6 Complete!")
            print(f"You've successfully:")
            print(f"   ✅ Saved work in GIMP format (.xcf)")
            print(f"   ✅ Exported as PNG with transparency support")
            print(f"   ✅ Exported as JPEG for photo use")
            print(f"   ✅ Learned when to use each format")
            print(f"   ✅ Properly closed the document")
            
            return True
            
        except Exception as e:
            self.log_step(6, "Save/export failed", False, str(e))
            print(f"\n❌ Save/export failed: {e}")
            return False
    
    async def generate_tutorial_completion_report(self) -> bool:
        """Generate a completion report for the tutorial."""
        try:
            print("\n📊 Generating Tutorial Completion Report...")
            
            # Calculate completion statistics
            total_steps = len(self.tutorial_log)
            successful_steps = len([log for log in self.tutorial_log if log["success"]])
            completion_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
            
            # Group by lesson
            lesson_progress = {}
            for log in self.tutorial_log:
                lesson_id = log["lesson_id"]
                if lesson_id not in lesson_progress:
                    lesson_progress[lesson_id] = {"total": 0, "success": 0}
                lesson_progress[lesson_id]["total"] += 1
                if log["success"]:
                    lesson_progress[lesson_id]["success"] += 1
            
            # Create report
            report = {
                "tutorial_info": {
                    "name": self.config["tutorial_name"],
                    "completion_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_lessons": len(self.config["lessons"]),
                    "total_steps": total_steps,
                    "successful_steps": successful_steps,
                    "completion_rate": completion_rate
                },
                "lesson_progress": {
                    f"lesson_{lesson_id}": {
                        "title": self.config["lessons"][lesson_id-1]["title"],
                        "completion_rate": (progress["success"] / progress["total"] * 100) if progress["total"] > 0 else 0,
                        "steps_completed": f"{progress['success']}/{progress['total']}"
                    }
                    for lesson_id, progress in lesson_progress.items()
                },
                "skills_learned": [
                    "MCP server connection and communication",
                    "Document creation and management",
                    "Basic drawing operations (rectangles, ellipses)",
                    "Layer creation and manipulation",
                    "Color management and brush painting",
                    "File saving and format export"
                ],
                "files_created": [
                    f"{self.config['tutorial_name']}-artwork.xcf",
                    f"{self.config['tutorial_name']}-final.png",
                    f"{self.config['tutorial_name']}-photo.jpg"
                ],
                "next_steps": [
                    "Try the intermediate tutorial for advanced techniques",
                    "Experiment with filters and effects",
                    "Explore batch processing capabilities",
                    "Learn about MCP client development"
                ],
                "tutorial_log": self.tutorial_log
            }
            
            # Save report
            report_path = self.output_dir / f"{self.config['tutorial_name']}-completion-report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Create certificate
            certificate_path = self.output_dir / f"{self.config['tutorial_name']}-certificate.txt"
            with open(certificate_path, 'w') as f:
                f.write("🎓 GIMP MCP SERVER BEGINNER TUTORIAL\n")
                f.write("=" * 50 + "\n")
                f.write("CERTIFICATE OF COMPLETION\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Completion Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Tutorial: {self.config['tutorial_name']}\n")
                f.write(f"Completion Rate: {completion_rate:.1f}%\n\n")
                f.write("SKILLS MASTERED:\n")
                for skill in report["skills_learned"]:
                    f.write(f"✅ {skill}\n")
                f.write(f"\nFILES CREATED:\n")
                for file in report["files_created"]:
                    f.write(f"📄 {file}\n")
                f.write(f"\nCongratulations on completing the beginner tutorial!\n")
                f.write(f"You're ready to explore more advanced GIMP MCP features.\n")
            
            print(f"📄 Tutorial report saved: {report_path}")
            print(f"🎓 Certificate saved: {certificate_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate completion report: {e}")
            return False
    
    async def cleanup(self) -> bool:
        """Clean up resources and close connections."""
        try:
            if self.current_document_id:
                try:
                    await self.session.call_tool("close_document", {
                        "document_id": self.current_document_id
                    })
                except:
                    pass  # Document might already be closed
            
            if self.session:
                await self.session.close()
            
            return True
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
            return False
    
    async def run_tutorial(self) -> bool:
        """Run the complete beginner tutorial."""
        try:
            print("🎓 Welcome to the GIMP MCP Server Beginner Tutorial!")
            print("=" * 60)
            print("This tutorial will teach you the basics of GIMP automation")
            print("using the Model Context Protocol (MCP) server.")
            print("=" * 60)
            
            # Introduction
            print("\n📚 What You'll Learn:")
            for lesson in self.config["lessons"]:
                print(f"   {lesson['id']}. {lesson['title']}")
                print(f"      {lesson['description']}")
            
            print(f"\n⏱️ Estimated Time: 20-30 minutes")
            print(f"📁 Output Directory: {self.output_dir}")
            
            self.wait_for_user("Ready to start your learning journey?")
            
            # Run lessons
            lessons = [
                self.lesson_1_server_connection,
                self.lesson_2_first_document,
                self.lesson_3_basic_drawing,
                self.lesson_4_working_with_layers,
                self.lesson_5_colors_and_painting,
                self.lesson_6_saving_and_exporting
            ]
            
            successful_lessons = 0
            
            for i, lesson_func in enumerate(lessons):
                try:
                    success = await lesson_func()
                    if success:
                        successful_lessons += 1
                        print(f"\n✅ Lesson {i+1} completed successfully!")
                    else:
                        print(f"\n❌ Lesson {i+1} had some issues.")
                        
                        should_continue = input("Would you like to continue with the next lesson? (y/n): ")
                        if should_continue.lower() != 'y':
                            break
                            
                except Exception as e:
                    print(f"\n❌ Lesson {i+1} failed: {e}")
                    should_continue = input("Would you like to continue with the next lesson? (y/n): ")
                    if should_continue.lower() != 'y':
                        break
            
            # Generate completion report
            await self.generate_tutorial_completion_report()
            
            # Final summary
            completion_rate = (successful_lessons / len(lessons)) * 100
            
            print(f"\n" + "="*60)
            print(f"🎉 TUTORIAL COMPLETE!")
            print(f"="*60)
            print(f"📊 Lessons completed: {successful_lessons}/{len(lessons)}")
            print(f"📈 Success rate: {completion_rate:.1f}%")
            print(f"📁 Files created in: {self.output_dir}")
            
            if completion_rate >= 80:
                print(f"\n🎓 Congratulations! You've mastered the basics of GIMP MCP!")
                print(f"🚀 You're ready to explore intermediate and advanced features.")
            elif completion_rate >= 60:
                print(f"\n👍 Good job! You've learned the core concepts.")
                print(f"💡 Consider reviewing any lessons that had issues.")
            else:
                print(f"\n💪 You've made a good start!")
                print(f"🔄 Consider running the tutorial again to reinforce learning.")
            
            print(f"\n📚 Next Steps:")
            print(f"   • Try the intermediate tutorial")
            print(f"   • Explore the advanced automation examples")
            print(f"   • Check out the real-world scenario demos")
            print(f"   • Read the comprehensive documentation")
            
            return completion_rate >= 60  # Consider 60%+ a success
            
        except Exception as e:
            print(f"❌ Tutorial failed: {e}")
            return False
            
        finally:
            await self.cleanup()

async def main():
    """Main entry point for the beginner tutorial."""
    print("GIMP MCP Server - Beginner Tutorial")
    print("=" * 50)
    
    # Create and run tutorial
    tutorial = BeginnerTutorial(TUTORIAL_CONFIG)
    success = await tutorial.run_tutorial()
    
    if success:
        print("\n🎉 Tutorial completed successfully!")
        print(f"📁 Check your outputs in: {TUTORIAL_CONFIG['output_dir']}")
        sys.exit(0)
    else:
        print("\n📚 Tutorial session ended.")
        print("Remember: Learning is a process - you can always try again!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())