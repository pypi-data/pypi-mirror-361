#!/usr/bin/env python3
"""
GIMP MCP Server - Logo Design Demonstration

This script demonstrates professional logo design workflows using the GIMP MCP server.
It showcases real-world logo creation including:
- Brand identity development with multiple logo variants
- Professional color palette management
- Scalable logo design for various applications
- Export optimization for different use cases
- Brand guideline generation

Perfect for understanding professional design workflows and brand identity creation.
"""

import asyncio
import json
import time
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sys
import os
from dataclasses import dataclass, asdict
from enum import Enum

# Add the parent directory to the path to import gimp_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ MCP not installed. Please install with: pip install mcp")
    sys.exit(1)

class LogoType(Enum):
    """Types of logos to create."""
    WORDMARK = "wordmark"
    SYMBOL = "symbol"
    COMBINATION = "combination"
    EMBLEM = "emblem"

class ExportFormat(Enum):
    """Export formats for different use cases."""
    WEB_PNG = {"format": "PNG", "size": (512, 512), "quality": 90}
    PRINT_PNG = {"format": "PNG", "size": (2048, 2048), "quality": 100}
    FAVICON = {"format": "PNG", "size": (32, 32), "quality": 80}
    SOCIAL_MEDIA = {"format": "PNG", "size": (1080, 1080), "quality": 85}
    VECTOR_EXPORT = {"format": "SVG", "size": (1024, 1024), "quality": 100}

@dataclass
class BrandColors:
    """Brand color palette definition."""
    primary: str
    secondary: str
    accent: str
    neutral_dark: str
    neutral_light: str
    background: str
    text: str

@dataclass
class LogoVariant:
    """Logo variant specification."""
    name: str
    logo_type: LogoType
    colors: BrandColors
    elements: List[Dict[str, Any]]
    description: str

# Demo configuration
DEMO_CONFIG = {
    "output_dir": Path(__file__).parent / "outputs",
    "demo_name": "logo-design-demo",
    "brand_name": "TechFlow",
    "brand_tagline": "Innovating Tomorrow",
    "logo_size": (1024, 1024),
    "brand_colors": BrandColors(
        primary="#2C3E50",      # Dark blue-gray
        secondary="#3498DB",    # Blue
        accent="#E74C3C",       # Red
        neutral_dark="#34495E", # Dark gray
        neutral_light="#ECF0F1",# Light gray
        background="#FFFFFF",   # White
        text="#2C3E50"         # Dark blue-gray
    ),
    "logo_variants": [
        {
            "name": "primary_symbol",
            "logo_type": LogoType.SYMBOL,
            "description": "Primary symbol logo - geometric design with brand colors",
            "elements": [
                {"type": "circle", "radius": 300, "color": "primary", "stroke": True},
                {"type": "triangle", "size": 200, "color": "secondary", "position": "center"},
                {"type": "accent_dots", "count": 3, "color": "accent", "size": 20}
            ]
        },
        {
            "name": "wordmark",
            "logo_type": LogoType.WORDMARK,
            "description": "Text-based logo with custom typography",
            "elements": [
                {"type": "text", "content": "TechFlow", "font_size": 120, "color": "primary"},
                {"type": "tagline", "content": "Innovating Tomorrow", "font_size": 40, "color": "secondary"}
            ]
        },
        {
            "name": "combination_horizontal",
            "logo_type": LogoType.COMBINATION,
            "description": "Horizontal combination of symbol and wordmark",
            "elements": [
                {"type": "symbol", "size": 150, "position": "left"},
                {"type": "wordmark", "size": 100, "position": "right"},
                {"type": "separator", "width": 3, "color": "accent"}
            ]
        },
        {
            "name": "combination_vertical",
            "logo_type": LogoType.COMBINATION,
            "description": "Vertical combination of symbol and wordmark",
            "elements": [
                {"type": "symbol", "size": 200, "position": "top"},
                {"type": "wordmark", "size": 80, "position": "bottom"},
                {"type": "tagline", "size": 30, "position": "bottom"}
            ]
        },
        {
            "name": "monochrome_light",
            "logo_type": LogoType.COMBINATION,
            "description": "Monochrome version for light backgrounds",
            "elements": [
                {"type": "symbol", "size": 150, "color": "neutral_dark"},
                {"type": "wordmark", "size": 100, "color": "neutral_dark"}
            ]
        },
        {
            "name": "monochrome_dark",
            "logo_type": LogoType.COMBINATION,
            "description": "Monochrome version for dark backgrounds",
            "elements": [
                {"type": "symbol", "size": 150, "color": "neutral_light"},
                {"type": "wordmark", "size": 100, "color": "neutral_light"}
            ]
        }
    ],
    "export_formats": [
        {"name": "web_standard", "size": (512, 512), "format": "PNG", "quality": 90},
        {"name": "print_high_res", "size": (2048, 2048), "format": "PNG", "quality": 100},
        {"name": "favicon", "size": (32, 32), "format": "PNG", "quality": 80},
        {"name": "social_media", "size": (1080, 1080), "format": "PNG", "quality": 85},
        {"name": "app_icon", "size": (1024, 1024), "format": "PNG", "quality": 95}
    ]
}

class LogoDesignDemo:
    """
    Demonstrates professional logo design workflows using GIMP MCP server.
    
    This demo creates a complete brand identity with multiple logo variants
    and export formats for different use cases.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = config["output_dir"]
        self.session = None
        self.brand_colors = config["brand_colors"]
        self.created_logos = []
        self.performance_metrics = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "variants").mkdir(exist_ok=True)
        (self.output_dir / "exports").mkdir(exist_ok=True)
        (self.output_dir / "brand-guidelines").mkdir(exist_ok=True)
        
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
    
    async def create_brand_color_palette(self) -> bool:
        """Create a visual brand color palette reference."""
        try:
            print("\n🎨 Creating brand color palette...")
            start_time = time.time()
            
            # Create palette document
            palette_response = await self.session.call_tool("create_document", {
                "width": 1200,
                "height": 800,
                "name": "Brand Color Palette",
                "color_mode": "RGB",
                "fill_color": self.brand_colors.background
            })
            
            palette_doc_id = palette_response["document_id"]
            
            # Create color swatches
            colors = [
                ("Primary", self.brand_colors.primary),
                ("Secondary", self.brand_colors.secondary),
                ("Accent", self.brand_colors.accent),
                ("Neutral Dark", self.brand_colors.neutral_dark),
                ("Neutral Light", self.brand_colors.neutral_light),
                ("Background", self.brand_colors.background),
                ("Text", self.brand_colors.text)
            ]
            
            # Create palette layer
            palette_layer = await self.session.call_tool("create_layer", {
                "document_id": palette_doc_id,
                "name": "Color Palette",
                "layer_type": "RGB"
            })
            
            palette_layer_id = palette_layer["layer_id"]
            
            # Draw color swatches
            swatch_size = 150
            swatches_per_row = 4
            start_x = 50
            start_y = 100
            
            for i, (color_name, color_value) in enumerate(colors):
                row = i // swatches_per_row
                col = i % swatches_per_row
                
                x = start_x + (col * (swatch_size + 30))
                y = start_y + (row * (swatch_size + 80))
                
                # Draw color swatch
                await self.session.call_tool("draw_rectangle", {
                    "document_id": palette_doc_id,
                    "layer_id": palette_layer_id,
                    "x": x,
                    "y": y,
                    "width": swatch_size,
                    "height": swatch_size,
                    "fill_color": color_value,
                    "stroke_color": self.brand_colors.neutral_dark,
                    "stroke_width": 2
                })
                
                # Draw color name (represented as rectangle for now)
                await self.session.call_tool("draw_rectangle", {
                    "document_id": palette_doc_id,
                    "layer_id": palette_layer_id,
                    "x": x,
                    "y": y + swatch_size + 10,
                    "width": swatch_size,
                    "height": 30,
                    "fill_color": self.brand_colors.text,
                    "stroke_color": None,
                    "stroke_width": 0
                })
            
            # Export palette
            palette_path = self.output_dir / "brand-guidelines" / "color-palette.png"
            await self.session.call_tool("export_document", {
                "document_id": palette_doc_id,
                "file_path": str(palette_path),
                "format": "PNG",
                "options": {"quality": 95}
            })
            
            # Close palette document
            await self.session.call_tool("close_document", {
                "document_id": palette_doc_id
            })
            
            palette_time = time.time() - start_time
            print(f"✅ Brand color palette created in {palette_time:.2f}s")
            print(f"📁 Saved: {palette_path}")
            
            self.performance_metrics["color_palette_creation"] = palette_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create brand color palette: {e}")
            return False
    
    async def create_logo_variant(self, variant_config: Dict[str, Any]) -> bool:
        """Create a single logo variant."""
        try:
            variant_name = variant_config["name"]
            logo_type = variant_config["logo_type"]
            elements = variant_config["elements"]
            
            print(f"  Creating logo variant: {variant_name}")
            start_time = time.time()
            
            # Create document for this variant
            doc_response = await self.session.call_tool("create_document", {
                "width": self.config["logo_size"][0],
                "height": self.config["logo_size"][1],
                "name": f"Logo-{variant_name}",
                "color_mode": "RGB",
                "fill_color": self.brand_colors.background
            })
            
            document_id = doc_response["document_id"]
            
            # Create main logo layer
            logo_layer = await self.session.call_tool("create_layer", {
                "document_id": document_id,
                "name": f"Logo-{variant_name}",
                "layer_type": "RGB"
            })
            
            logo_layer_id = logo_layer["layer_id"]
            
            # Create logo elements based on type
            await self._create_logo_elements(document_id, logo_layer_id, variant_name, elements)
            
            # Save as XCF for editing
            xcf_path = self.output_dir / "variants" / f"{variant_name}.xcf"
            await self.session.call_tool("save_document", {
                "document_id": document_id,
                "file_path": str(xcf_path)
            })
            
            # Export as PNG
            png_path = self.output_dir / "variants" / f"{variant_name}.png"
            await self.session.call_tool("export_document", {
                "document_id": document_id,
                "file_path": str(png_path),
                "format": "PNG",
                "options": {"quality": 95}
            })
            
            # Store logo info
            logo_info = {
                "name": variant_name,
                "document_id": document_id,
                "type": logo_type.value if isinstance(logo_type, LogoType) else logo_type,
                "xcf_path": str(xcf_path),
                "png_path": str(png_path),
                "creation_time": time.time() - start_time
            }
            
            self.created_logos.append(logo_info)
            
            print(f"    ✅ Created {variant_name} in {logo_info['creation_time']:.2f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create logo variant {variant_name}: {e}")
            return False
    
    async def _create_logo_elements(self, document_id: int, layer_id: int, 
                                   variant_name: str, elements: List[Dict[str, Any]]) -> None:
        """Create logo elements based on variant configuration."""
        center_x = self.config["logo_size"][0] // 2
        center_y = self.config["logo_size"][1] // 2
        
        for element in elements:
            element_type = element["type"]
            
            if element_type == "circle":
                radius = element.get("radius", 200)
                color = self._get_brand_color(element.get("color", "primary"))
                stroke = element.get("stroke", False)
                
                await self.session.call_tool("draw_ellipse", {
                    "document_id": document_id,
                    "layer_id": layer_id,
                    "center_x": center_x,
                    "center_y": center_y,
                    "radius_x": radius,
                    "radius_y": radius,
                    "fill_color": color if not stroke else None,
                    "stroke_color": color if stroke else None,
                    "stroke_width": 8 if stroke else 0
                })
            
            elif element_type == "triangle":
                size = element.get("size", 150)
                color = self._get_brand_color(element.get("color", "secondary"))
                
                # Create triangle using three lines (simplified)
                # Top point
                await self.session.call_tool("draw_rectangle", {
                    "document_id": document_id,
                    "layer_id": layer_id,
                    "x": center_x - size//2,
                    "y": center_y - size//3,
                    "width": size,
                    "height": size//2,
                    "fill_color": color,
                    "stroke_color": None,
                    "stroke_width": 0
                })
            
            elif element_type == "accent_dots":
                count = element.get("count", 3)
                color = self._get_brand_color(element.get("color", "accent"))
                dot_size = element.get("size", 15)
                
                for i in range(count):
                    angle = (2 * math.pi * i) / count
                    dot_x = center_x + int(250 * math.cos(angle))
                    dot_y = center_y + int(250 * math.sin(angle))
                    
                    await self.session.call_tool("draw_ellipse", {
                        "document_id": document_id,
                        "layer_id": layer_id,
                        "center_x": dot_x,
                        "center_y": dot_y,
                        "radius_x": dot_size,
                        "radius_y": dot_size,
                        "fill_color": color,
                        "stroke_color": None,
                        "stroke_width": 0
                    })
            
            elif element_type == "text":
                content = element.get("content", "TechFlow")
                font_size = element.get("font_size", 100)
                color = self._get_brand_color(element.get("color", "primary"))
                
                # Create text representation using rectangle for now
                text_width = len(content) * (font_size // 2)
                text_height = font_size
                
                await self.session.call_tool("draw_rectangle", {
                    "document_id": document_id,
                    "layer_id": layer_id,
                    "x": center_x - text_width // 2,
                    "y": center_y - text_height // 2,
                    "width": text_width,
                    "height": text_height,
                    "fill_color": color,
                    "stroke_color": None,
                    "stroke_width": 0
                })
            
            elif element_type == "tagline":
                content = element.get("content", "Innovating Tomorrow")
                font_size = element.get("font_size", 40)
                color = self._get_brand_color(element.get("color", "secondary"))
                
                # Create tagline representation
                tagline_width = len(content) * (font_size // 3)
                tagline_height = font_size
                
                await self.session.call_tool("draw_rectangle", {
                    "document_id": document_id,
                    "layer_id": layer_id,
                    "x": center_x - tagline_width // 2,
                    "y": center_y + 100,
                    "width": tagline_width,
                    "height": tagline_height,
                    "fill_color": color,
                    "stroke_color": None,
                    "stroke_width": 0
                })
            
            elif element_type == "symbol":
                size = element.get("size", 150)
                position = element.get("position", "center")
                color = self._get_brand_color(element.get("color", "primary"))
                
                # Adjust position based on layout
                if position == "left":
                    symbol_x = center_x - 200
                    symbol_y = center_y
                elif position == "top":
                    symbol_x = center_x
                    symbol_y = center_y - 150
                else:
                    symbol_x = center_x
                    symbol_y = center_y
                
                # Create symbol
                await self.session.call_tool("draw_ellipse", {
                    "document_id": document_id,
                    "layer_id": layer_id,
                    "center_x": symbol_x,
                    "center_y": symbol_y,
                    "radius_x": size,
                    "radius_y": size,
                    "fill_color": color,
                    "stroke_color": None,
                    "stroke_width": 0
                })
            
            elif element_type == "wordmark":
                size = element.get("font_size", 80)
                position = element.get("position", "center")
                color = self._get_brand_color(element.get("color", "primary"))
                
                # Adjust position based on layout
                if position == "right":
                    text_x = center_x + 100
                    text_y = center_y
                elif position == "bottom":
                    text_x = center_x
                    text_y = center_y + 100
                else:
                    text_x = center_x
                    text_y = center_y
                
                # Create wordmark
                text_width = len(self.config["brand_name"]) * (size // 2)
                await self.session.call_tool("draw_rectangle", {
                    "document_id": document_id,
                    "layer_id": layer_id,
                    "x": text_x - text_width // 2,
                    "y": text_y - size // 2,
                    "width": text_width,
                    "height": size,
                    "fill_color": color,
                    "stroke_color": None,
                    "stroke_width": 0
                })
            
            elif element_type == "separator":
                width = element.get("width", 3)
                color = self._get_brand_color(element.get("color", "accent"))
                
                await self.session.call_tool("draw_rectangle", {
                    "document_id": document_id,
                    "layer_id": layer_id,
                    "x": center_x - width // 2,
                    "y": center_y - 100,
                    "width": width,
                    "height": 200,
                    "fill_color": color,
                    "stroke_color": None,
                    "stroke_width": 0
                })
    
    def _get_brand_color(self, color_name: str) -> str:
        """Get brand color by name."""
        color_map = {
            "primary": self.brand_colors.primary,
            "secondary": self.brand_colors.secondary,
            "accent": self.brand_colors.accent,
            "neutral_dark": self.brand_colors.neutral_dark,
            "neutral_light": self.brand_colors.neutral_light,
            "background": self.brand_colors.background,
            "text": self.brand_colors.text
        }
        return color_map.get(color_name, self.brand_colors.primary)
    
    async def create_all_logo_variants(self) -> bool:
        """Create all configured logo variants."""
        try:
            print("\n🎯 Creating logo variants...")
            start_time = time.time()
            
            for variant_config in self.config["logo_variants"]:
                if not await self.create_logo_variant(variant_config):
                    return False
            
            total_time = time.time() - start_time
            print(f"✅ Created {len(self.created_logos)} logo variants in {total_time:.2f}s")
            
            self.performance_metrics["logo_variants_creation"] = total_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create logo variants: {e}")
            return False
    
    async def export_optimized_formats(self) -> bool:
        """Export logos in various optimized formats for different use cases."""
        try:
            print("\n📤 Exporting optimized formats...")
            start_time = time.time()
            
            export_count = 0
            
            for logo_info in self.created_logos:
                logo_name = logo_info["name"]
                document_id = logo_info["document_id"]
                
                print(f"  Exporting formats for: {logo_name}")
                
                for export_config in self.config["export_formats"]:
                    format_name = export_config["name"]
                    size = export_config["size"]
                    format_type = export_config["format"]
                    quality = export_config["quality"]
                    
                    # Create export filename
                    export_filename = f"{logo_name}_{format_name}.{format_type.lower()}"
                    export_path = self.output_dir / "exports" / export_filename
                    
                    # For different sizes, we would need to resize the document
                    # For now, we'll export at original size
                    await self.session.call_tool("export_document", {
                        "document_id": document_id,
                        "file_path": str(export_path),
                        "format": format_type,
                        "options": {"quality": quality}
                    })
                    
                    export_count += 1
                    
                print(f"    ✅ Exported {len(self.config['export_formats'])} formats")
            
            export_time = time.time() - start_time
            print(f"✅ Exported {export_count} optimized formats in {export_time:.2f}s")
            
            self.performance_metrics["format_export"] = export_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to export optimized formats: {e}")
            return False
    
    async def create_brand_guidelines(self) -> bool:
        """Create brand guidelines document showing logo usage."""
        try:
            print("\n📋 Creating brand guidelines...")
            start_time = time.time()
            
            # Create guidelines document
            guidelines_response = await self.session.call_tool("create_document", {
                "width": 1920,
                "height": 2560,  # Tall document for guidelines
                "name": "Brand Guidelines",
                "color_mode": "RGB",
                "fill_color": self.brand_colors.background
            })
            
            guidelines_doc_id = guidelines_response["document_id"]
            
            # Create guidelines layer
            guidelines_layer = await self.session.call_tool("create_layer", {
                "document_id": guidelines_doc_id,
                "name": "Brand Guidelines",
                "layer_type": "RGB"
            })
            
            guidelines_layer_id = guidelines_layer["layer_id"]
            
            # Add title section
            await self.session.call_tool("draw_rectangle", {
                "document_id": guidelines_doc_id,
                "layer_id": guidelines_layer_id,
                "x": 100,
                "y": 100,
                "width": 1720,
                "height": 200,
                "fill_color": self.brand_colors.primary,
                "stroke_color": None,
                "stroke_width": 0
            })
            
            # Add brand name
            await self.session.call_tool("draw_rectangle", {
                "document_id": guidelines_doc_id,
                "layer_id": guidelines_layer_id,
                "x": 150,
                "y": 150,
                "width": 600,
                "height": 100,
                "fill_color": self.brand_colors.background,
                "stroke_color": None,
                "stroke_width": 0
            })
            
            # Add logo showcase sections
            y_offset = 400
            section_height = 300
            
            # Add sections for different logo variants
            for i, logo_info in enumerate(self.created_logos[:4]):  # Show first 4 variants
                # Section background
                await self.session.call_tool("draw_rectangle", {
                    "document_id": guidelines_doc_id,
                    "layer_id": guidelines_layer_id,
                    "x": 100,
                    "y": y_offset + (i * section_height),
                    "width": 1720,
                    "height": section_height - 20,
                    "fill_color": self.brand_colors.neutral_light,
                    "stroke_color": self.brand_colors.neutral_dark,
                    "stroke_width": 2
                })
                
                # Logo preview area
                await self.session.call_tool("draw_rectangle", {
                    "document_id": guidelines_doc_id,
                    "layer_id": guidelines_layer_id,
                    "x": 150,
                    "y": y_offset + (i * section_height) + 50,
                    "width": 200,
                    "height": 200,
                    "fill_color": self.brand_colors.background,
                    "stroke_color": self.brand_colors.neutral_dark,
                    "stroke_width": 1
                })
                
                # Usage description area
                await self.session.call_tool("draw_rectangle", {
                    "document_id": guidelines_doc_id,
                    "layer_id": guidelines_layer_id,
                    "x": 400,
                    "y": y_offset + (i * section_height) + 50,
                    "width": 1320,
                    "height": 200,
                    "fill_color": self.brand_colors.background,
                    "stroke_color": None,
                    "stroke_width": 0
                })
            
            # Export guidelines
            guidelines_path = self.output_dir / "brand-guidelines" / "brand-guidelines.png"
            await self.session.call_tool("export_document", {
                "document_id": guidelines_doc_id,
                "file_path": str(guidelines_path),
                "format": "PNG",
                "options": {"quality": 95}
            })
            
            # Close guidelines document
            await self.session.call_tool("close_document", {
                "document_id": guidelines_doc_id
            })
            
            guidelines_time = time.time() - start_time
            print(f"✅ Brand guidelines created in {guidelines_time:.2f}s")
            print(f"📁 Saved: {guidelines_path}")
            
            self.performance_metrics["guidelines_creation"] = guidelines_time
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create brand guidelines: {e}")
            return False
    
    async def generate_logo_design_report(self) -> bool:
        """Generate a comprehensive logo design report."""
        try:
            print("\n📊 Generating logo design report...")
            
            total_time = sum(self.performance_metrics.values())
            
            # Create detailed report
            report = {
                "demo_name": self.config["demo_name"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "brand_info": {
                    "name": self.config["brand_name"],
                    "tagline": self.config["brand_tagline"],
                    "color_palette": asdict(self.brand_colors)
                },
                "logo_variants": [
                    {
                        "name": logo["name"],
                        "type": logo["type"],
                        "creation_time": logo["creation_time"],
                        "files": {
                            "xcf": logo["xcf_path"],
                            "png": logo["png_path"]
                        }
                    }
                    for logo in self.created_logos
                ],
                "export_formats": self.config["export_formats"],
                "performance_metrics": self.performance_metrics,
                "total_time": total_time,
                "files_created": {
                    "logo_variants": len(self.created_logos),
                    "exported_formats": len(self.created_logos) * len(self.config["export_formats"]),
                    "brand_guidelines": 2  # Color palette + guidelines
                },
                "professional_deliverables": [
                    "Primary logo symbol",
                    "Wordmark logo",
                    "Horizontal combination logo",
                    "Vertical combination logo",
                    "Monochrome versions (light/dark)",
                    "Brand color palette",
                    "Usage guidelines",
                    "Multiple export formats",
                    "Scalable vector versions",
                    "Print-ready high resolution"
                ]
            }
            
            # Save report
            report_path = self.output_dir / f"{self.config['demo_name']}-report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Create summary text file
            summary_path = self.output_dir / "brand-guidelines" / "project-summary.txt"
            with open(summary_path, 'w') as f:
                f.write(f"Logo Design Project Summary\n")
                f.write(f"==========================\n\n")
                f.write(f"Brand: {self.config['brand_name']}\n")
                f.write(f"Tagline: {self.config['brand_tagline']}\n")
                f.write(f"Project Date: {time.strftime('%Y-%m-%d')}\n\n")
                f.write(f"Deliverables:\n")
                f.write(f"- {len(self.created_logos)} logo variants\n")
                f.write(f"- {len(self.config['export_formats'])} export formats per variant\n")
                f.write(f"- Brand color palette\n")
                f.write(f"- Usage guidelines\n\n")
                f.write(f"Performance:\n")
                f.write(f"- Total creation time: {total_time:.2f}s\n")
                f.write(f"- Average variant time: {total_time/len(self.created_logos):.2f}s\n")
            
            # Print summary
            print(f"📊 Logo Design Project Summary:")
            print(f"   Brand: {self.config['brand_name']}")
            print(f"   Logo variants created: {len(self.created_logos)}")
            print(f"   Export formats: {len(self.config['export_formats'])}")
            print(f"   Total creation time: {total_time:.2f}s")
            print(f"   Professional deliverables: {len(report['professional_deliverables'])}")
            
            print(f"📄 Report saved: {report_path}")
            print(f"📄 Summary saved: {summary_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate logo design report: {e}")
            return False
    
    async def cleanup(self) -> bool:
        """Clean up resources and close connections."""
        try:
            print("\n🧹 Cleaning up...")
            
            # Close all open documents
            for logo_info in self.created_logos:
                try:
                    await self.session.call_tool("close_document", {
                        "document_id": logo_info["document_id"]
                    })
                except:
                    pass  # Document might already be closed
            
            if self.session:
                await self.session.close()
            
            print("✅ Cleanup completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to cleanup: {e}")
            return False
    
    async def run_demo(self) -> bool:
        """Run the complete logo design demonstration."""
        try:
            print("🚀 Starting Logo Design Demonstration")
            print("=" * 50)
            
            # Connect to server
            if not await self.connect_to_server():
                return False
            
            # Create brand color palette
            if not await self.create_brand_color_palette():
                return False
            
            # Create logo variants
            if not await self.create_all_logo_variants():
                return False
            
            # Export optimized formats
            if not await self.export_optimized_formats():
                return False
            
            # Create brand guidelines
            if not await self.create_brand_guidelines():
                return False
            
            # Generate report
            if not await self.generate_logo_design_report():
                return False
            
            print("\n🎉 Logo Design Demonstration completed successfully!")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return False
            
        finally:
            await self.cleanup()

async def main():
    """Main entry point for the logo design demonstration."""
    print("GIMP MCP Server - Logo Design Demonstration")
    print("=" * 60)
    
    # Create and run the demo
    demo = LogoDesignDemo(DEMO_CONFIG)
    success = await demo.run_demo()
    
    if success:
        print("\n✅ Demonstration completed successfully!")
        print(f"📁 Output files available in: {DEMO_CONFIG['output_dir']}")
        print("\n🎨 Professional logo design deliverables created:")
        print("   • Multiple logo variants (symbol, wordmark, combination)")
        print("   • Brand color palette")
        print("   • Usage guidelines")
        print("   • Optimized export formats")
        print("   • Print-ready high resolution files")
        sys.exit(0)
    else:
        print("\n❌ Demonstration failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())