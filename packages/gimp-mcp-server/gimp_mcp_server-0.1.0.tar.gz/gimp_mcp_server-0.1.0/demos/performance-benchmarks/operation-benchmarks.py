#!/usr/bin/env python3
"""
GIMP MCP Server - Operation Benchmarks

This script provides comprehensive performance benchmarking for the GIMP MCP server.
It measures and analyzes the performance of individual operations including:
- Document creation and management operations
- Layer operations (create, modify, delete)
- Drawing operations (shapes, strokes, fills)
- Filter and effect operations
- Export and save operations
- Memory usage and resource consumption

Perfect for performance analysis, optimization, and capacity planning.
"""

import asyncio
import json
import time
import psutil
import statistics
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sys
import os
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import gc
import traceback

# Add the parent directory to the path to import gimp_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please install with: pip install mcp matplotlib numpy psutil")
    sys.exit(1)

@dataclass
class BenchmarkResult:
    """Individual benchmark operation result."""
    operation_name: str
    duration: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None
    additional_metrics: Optional[Dict[str, Any]] = None

@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results."""
    suite_name: str
    total_time: float
    operations: List[BenchmarkResult]
    summary_stats: Dict[str, Any]
    system_info: Dict[str, Any]

# Benchmark configuration
BENCHMARK_CONFIG = {
    "output_dir": Path(__file__).parent / "outputs",
    "demo_name": "operation-benchmarks",
    "iterations": {
        "quick": 5,
        "standard": 10,
        "thorough": 25
    },
    "test_sizes": [
        {"name": "small", "width": 512, "height": 512},
        {"name": "medium", "width": 1920, "height": 1080},
        {"name": "large", "width": 3840, "height": 2160},
        {"name": "extra_large", "width": 7680, "height": 4320}
    ],
    "benchmark_suites": [
        {
            "name": "document_operations",
            "description": "Document creation, opening, saving, and closing",
            "operations": [
                "create_document_small",
                "create_document_medium", 
                "create_document_large",
                "save_document",
                "export_document_png",
                "export_document_jpeg",
                "close_document"
            ]
        },
        {
            "name": "layer_operations",
            "description": "Layer creation, modification, and management",
            "operations": [
                "create_layer",
                "set_layer_opacity",
                "set_layer_blend_mode",
                "duplicate_layer",
                "delete_layer",
                "move_layer"
            ]
        },
        {
            "name": "drawing_operations",
            "description": "Basic drawing and shape operations",
            "operations": [
                "draw_rectangle_small",
                "draw_rectangle_large",
                "draw_ellipse_small",
                "draw_ellipse_large",
                "apply_brush_stroke_short",
                "apply_brush_stroke_long",
                "bucket_fill"
            ]
        },
        {
            "name": "filter_operations",
            "description": "Image filters and effects",
            "operations": [
                "apply_blur_light",
                "apply_blur_heavy",
                "apply_sharpen",
                "adjust_brightness_contrast"
            ]
        },
        {
            "name": "selection_operations",
            "description": "Selection creation and modification",
            "operations": [
                "create_rectangular_selection",
                "create_elliptical_selection",
                "modify_selection",
                "clear_selection"
            ]
        },
        {
            "name": "color_operations",
            "description": "Color management operations",
            "operations": [
                "set_foreground_color",
                "set_background_color",
                "sample_color",
                "get_active_palette"
            ]
        }
    ]
}

class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking for GIMP MCP server operations.
    
    This class provides detailed performance analysis including timing,
    memory usage, CPU utilization, and statistical analysis.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = config["output_dir"]
        self.session = None
        self.current_document_id = None
        self.benchmark_results = []
        self.system_info = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup monitoring
        self.process = psutil.Process()
        
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
    
    def collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for benchmark context."""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:\\').total,
                "platform": sys.platform,
                "python_version": sys.version,
                "process_id": os.getpid()
            }
        except Exception as e:
            return {"error": str(e)}
    
    @asynccontextmanager
    async def benchmark_operation(self, operation_name: str):
        """Context manager for benchmarking individual operations."""
        # Collect baseline metrics
        gc.collect()  # Force garbage collection
        memory_before = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_before = self.process.cpu_percent()
        
        start_time = time.perf_counter()
        memory_peak = memory_before
        error = None
        success = True
        
        try:
            yield
            
        except Exception as e:
            error = str(e)
            success = False
            print(f"❌ Operation {operation_name} failed: {e}")
            
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            # Collect final metrics
            memory_after = self.process.memory_info().rss / 1024 / 1024  # MB
            memory_peak = max(memory_peak, memory_after)
            cpu_after = self.process.cpu_percent()
            
            # Create benchmark result
            result = BenchmarkResult(
                operation_name=operation_name,
                duration=duration,
                memory_before=memory_before,
                memory_after=memory_after,
                memory_peak=memory_peak,
                cpu_percent=(cpu_before + cpu_after) / 2,
                success=success,
                error=error
            )
            
            self.benchmark_results.append(result)
            
            # Print immediate feedback
            status = "✅" if success else "❌"
            print(f"  {status} {operation_name}: {duration:.3f}s")
    
    async def benchmark_document_operations(self, iterations: int) -> List[BenchmarkResult]:
        """Benchmark document-related operations."""
        print("\n📄 Benchmarking document operations...")
        results = []
        
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")
            
            # Create documents of different sizes
            for size_config in self.config["test_sizes"][:3]:  # Skip extra_large for speed
                size_name = size_config["name"]
                width = size_config["width"]
                height = size_config["height"]
                
                # Create document
                async with self.benchmark_operation(f"create_document_{size_name}"):
                    response = await self.session.call_tool("create_document", {
                        "width": width,
                        "height": height,
                        "name": f"benchmark_{size_name}_{i}",
                        "color_mode": "RGB"
                    })
                    self.current_document_id = response["document_id"]
                
                # Save document
                async with self.benchmark_operation("save_document"):
                    save_path = self.output_dir / f"benchmark_{size_name}_{i}.xcf"
                    await self.session.call_tool("save_document", {
                        "document_id": self.current_document_id,
                        "file_path": str(save_path)
                    })
                
                # Export PNG
                async with self.benchmark_operation("export_document_png"):
                    png_path = self.output_dir / f"benchmark_{size_name}_{i}.png"
                    await self.session.call_tool("export_document", {
                        "document_id": self.current_document_id,
                        "file_path": str(png_path),
                        "format": "PNG"
                    })
                
                # Export JPEG
                async with self.benchmark_operation("export_document_jpeg"):
                    jpg_path = self.output_dir / f"benchmark_{size_name}_{i}.jpg"
                    await self.session.call_tool("export_document", {
                        "document_id": self.current_document_id,
                        "file_path": str(jpg_path),
                        "format": "JPEG"
                    })
                
                # Close document
                async with self.benchmark_operation("close_document"):
                    await self.session.call_tool("close_document", {
                        "document_id": self.current_document_id
                    })
                
                self.current_document_id = None
        
        return [r for r in self.benchmark_results if r.operation_name.startswith(("create_document", "save_document", "export_document", "close_document"))]
    
    async def benchmark_layer_operations(self, iterations: int) -> List[BenchmarkResult]:
        """Benchmark layer-related operations."""
        print("\n🗂️ Benchmarking layer operations...")
        
        # Create a test document
        doc_response = await self.session.call_tool("create_document", {
            "width": 1920,
            "height": 1080,
            "name": "layer_benchmark",
            "color_mode": "RGB"
        })
        self.current_document_id = doc_response["document_id"]
        
        layer_ids = []
        
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")
            
            # Create layer
            async with self.benchmark_operation("create_layer"):
                layer_response = await self.session.call_tool("create_layer", {
                    "document_id": self.current_document_id,
                    "name": f"benchmark_layer_{i}",
                    "layer_type": "RGB"
                })
                layer_ids.append(layer_response["layer_id"])
            
            if layer_ids:
                current_layer = layer_ids[-1]
                
                # Set layer opacity
                async with self.benchmark_operation("set_layer_opacity"):
                    await self.session.call_tool("set_layer_opacity", {
                        "document_id": self.current_document_id,
                        "layer_id": current_layer,
                        "opacity": 0.8
                    })
                
                # Set blend mode
                async with self.benchmark_operation("set_layer_blend_mode"):
                    await self.session.call_tool("set_layer_blend_mode", {
                        "document_id": self.current_document_id,
                        "layer_id": current_layer,
                        "blend_mode": "multiply"
                    })
                
                # Duplicate layer (if we have at least one layer)
                if len(layer_ids) >= 1:
                    async with self.benchmark_operation("duplicate_layer"):
                        dup_response = await self.session.call_tool("duplicate_layer", {
                            "document_id": self.current_document_id,
                            "layer_id": current_layer,
                            "new_name": f"duplicate_layer_{i}"
                        })
                        layer_ids.append(dup_response["layer_id"])
                
                # Move layer (if we have multiple layers)
                if len(layer_ids) >= 2:
                    async with self.benchmark_operation("move_layer"):
                        await self.session.call_tool("move_layer", {
                            "document_id": self.current_document_id,
                            "layer_id": layer_ids[-1],
                            "new_position": 0
                        })
                
                # Delete a layer (keep some for next iteration)
                if len(layer_ids) > 3:
                    async with self.benchmark_operation("delete_layer"):
                        await self.session.call_tool("delete_layer", {
                            "document_id": self.current_document_id,
                            "layer_id": layer_ids.pop(0)
                        })
        
        # Clean up
        await self.session.call_tool("close_document", {
            "document_id": self.current_document_id
        })
        
        return [r for r in self.benchmark_results if r.operation_name.startswith(("create_layer", "set_layer", "duplicate_layer", "move_layer", "delete_layer"))]
    
    async def benchmark_drawing_operations(self, iterations: int) -> List[BenchmarkResult]:
        """Benchmark drawing operations."""
        print("\n🎨 Benchmarking drawing operations...")
        
        # Create test document
        doc_response = await self.session.call_tool("create_document", {
            "width": 1920,
            "height": 1080,
            "name": "drawing_benchmark",
            "color_mode": "RGB"
        })
        self.current_document_id = doc_response["document_id"]
        
        # Create drawing layer
        layer_response = await self.session.call_tool("create_layer", {
            "document_id": self.current_document_id,
            "name": "drawing_layer",
            "layer_type": "RGB"
        })
        layer_id = layer_response["layer_id"]
        
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")
            
            # Small rectangle
            async with self.benchmark_operation("draw_rectangle_small"):
                await self.session.call_tool("draw_rectangle", {
                    "document_id": self.current_document_id,
                    "layer_id": layer_id,
                    "x": 100 + (i * 10),
                    "y": 100 + (i * 10),
                    "width": 100,
                    "height": 100,
                    "fill_color": "#3498DB"
                })
            
            # Large rectangle
            async with self.benchmark_operation("draw_rectangle_large"):
                await self.session.call_tool("draw_rectangle", {
                    "document_id": self.current_document_id,
                    "layer_id": layer_id,
                    "x": 300 + (i * 10),
                    "y": 300 + (i * 10),
                    "width": 500,
                    "height": 300,
                    "fill_color": "#E74C3C"
                })
            
            # Small ellipse
            async with self.benchmark_operation("draw_ellipse_small"):
                await self.session.call_tool("draw_ellipse", {
                    "document_id": self.current_document_id,
                    "layer_id": layer_id,
                    "center_x": 1200 + (i * 10),
                    "center_y": 200 + (i * 10),
                    "radius_x": 50,
                    "radius_y": 50,
                    "fill_color": "#F39C12"
                })
            
            # Large ellipse
            async with self.benchmark_operation("draw_ellipse_large"):
                await self.session.call_tool("draw_ellipse", {
                    "document_id": self.current_document_id,
                    "layer_id": layer_id,
                    "center_x": 1200 + (i * 10),
                    "center_y": 600 + (i * 10),
                    "radius_x": 200,
                    "radius_y": 150,
                    "fill_color": "#9B59B6"
                })
            
            # Short brush stroke
            async with self.benchmark_operation("apply_brush_stroke_short"):
                points = [(100 + i * 5, 800), (200 + i * 5, 850), (300 + i * 5, 800)]
                await self.session.call_tool("apply_brush_stroke", {
                    "document_id": self.current_document_id,
                    "layer_id": layer_id,
                    "points": points,
                    "brush_name": "basic",
                    "size": 10,
                    "color": "#2ECC71"
                })
            
            # Long brush stroke
            async with self.benchmark_operation("apply_brush_stroke_long"):
                points = [(j, 900 + (i * 2)) for j in range(500 + i * 10, 1000 + i * 10, 20)]
                await self.session.call_tool("apply_brush_stroke", {
                    "document_id": self.current_document_id,
                    "layer_id": layer_id,
                    "points": points,
                    "brush_name": "basic",
                    "size": 5,
                    "color": "#E67E22"
                })
            
            # Bucket fill
            async with self.benchmark_operation("bucket_fill"):
                await self.session.call_tool("bucket_fill", {
                    "document_id": self.current_document_id,
                    "layer_id": layer_id,
                    "x": 50 + (i * 20),
                    "y": 50 + (i * 20),
                    "color": "#1ABC9C",
                    "threshold": 15.0
                })
        
        # Clean up
        await self.session.call_tool("close_document", {
            "document_id": self.current_document_id
        })
        
        return [r for r in self.benchmark_results if r.operation_name.startswith(("draw_", "apply_brush", "bucket_fill"))]
    
    async def benchmark_filter_operations(self, iterations: int) -> List[BenchmarkResult]:
        """Benchmark filter and effect operations."""
        print("\n🎭 Benchmarking filter operations...")
        
        # Create test document with content
        doc_response = await self.session.call_tool("create_document", {
            "width": 1920,
            "height": 1080,
            "name": "filter_benchmark",
            "color_mode": "RGB"
        })
        self.current_document_id = doc_response["document_id"]
        
        # Create content layer
        layer_response = await self.session.call_tool("create_layer", {
            "document_id": self.current_document_id,
            "name": "content_layer",
            "layer_type": "RGB"
        })
        layer_id = layer_response["layer_id"]
        
        # Add some content to filter
        await self.session.call_tool("draw_rectangle", {
            "document_id": self.current_document_id,
            "layer_id": layer_id,
            "x": 200,
            "y": 200,
            "width": 800,
            "height": 600,
            "fill_color": "#3498DB"
        })
        
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")
            
            # Light blur
            async with self.benchmark_operation("apply_blur_light"):
                await self.session.call_tool("apply_blur", {
                    "document_id": self.current_document_id,
                    "radius": 2.0,
                    "method": "gaussian"
                })
            
            # Heavy blur
            async with self.benchmark_operation("apply_blur_heavy"):
                await self.session.call_tool("apply_blur", {
                    "document_id": self.current_document_id,
                    "radius": 10.0,
                    "method": "gaussian"
                })
            
            # Sharpen
            async with self.benchmark_operation("apply_sharpen"):
                await self.session.call_tool("apply_sharpen", {
                    "document_id": self.current_document_id,
                    "amount": 1.0,
                    "threshold": 0.1
                })
            
            # Brightness/Contrast
            async with self.benchmark_operation("adjust_brightness_contrast"):
                await self.session.call_tool("adjust_brightness_contrast", {
                    "document_id": self.current_document_id,
                    "brightness": 10,
                    "contrast": 5
                })
        
        # Clean up
        await self.session.call_tool("close_document", {
            "document_id": self.current_document_id
        })
        
        return [r for r in self.benchmark_results if r.operation_name.startswith(("apply_", "adjust_"))]
    
    async def run_benchmark_suite(self, suite_name: str, iterations: int = 10) -> BenchmarkSuite:
        """Run a complete benchmark suite."""
        print(f"\n🚀 Running benchmark suite: {suite_name}")
        start_time = time.perf_counter()
        
        # Clear previous results
        initial_results_count = len(self.benchmark_results)
        
        # Run appropriate benchmark based on suite name
        if suite_name == "document_operations":
            await self.benchmark_document_operations(iterations)
        elif suite_name == "layer_operations":
            await self.benchmark_layer_operations(iterations)
        elif suite_name == "drawing_operations":
            await self.benchmark_drawing_operations(iterations)
        elif suite_name == "filter_operations":
            await self.benchmark_filter_operations(iterations)
        else:
            print(f"❌ Unknown benchmark suite: {suite_name}")
            return None
        
        total_time = time.perf_counter() - start_time
        
        # Get results from this suite
        suite_results = self.benchmark_results[initial_results_count:]
        
        # Calculate summary statistics
        if suite_results:
            durations = [r.duration for r in suite_results if r.success]
            memory_usage = [r.memory_after - r.memory_before for r in suite_results if r.success]
            
            summary_stats = {
                "total_operations": len(suite_results),
                "successful_operations": len(durations),
                "failed_operations": len(suite_results) - len(durations),
                "avg_duration": statistics.mean(durations) if durations else 0,
                "median_duration": statistics.median(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
                "std_duration": statistics.stdev(durations) if len(durations) > 1 else 0,
                "avg_memory_delta": statistics.mean(memory_usage) if memory_usage else 0,
                "total_memory_delta": sum(memory_usage) if memory_usage else 0,
                "throughput_ops_per_sec": len(durations) / total_time if durations and total_time > 0 else 0
            }
        else:
            summary_stats = {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "avg_duration": 0,
                "median_duration": 0,
                "min_duration": 0,
                "max_duration": 0,
                "std_duration": 0,
                "avg_memory_delta": 0,
                "total_memory_delta": 0,
                "throughput_ops_per_sec": 0
            }
        
        # Create benchmark suite result
        suite_result = BenchmarkSuite(
            suite_name=suite_name,
            total_time=total_time,
            operations=suite_results,
            summary_stats=summary_stats,
            system_info=self.system_info
        )
        
        print(f"✅ Completed {suite_name} in {total_time:.2f}s")
        print(f"   Operations: {summary_stats['successful_operations']}/{summary_stats['total_operations']} successful")
        print(f"   Avg duration: {summary_stats['avg_duration']:.3f}s")
        print(f"   Throughput: {summary_stats['throughput_ops_per_sec']:.1f} ops/sec")
        
        return suite_result
    
    async def generate_performance_charts(self, benchmark_suites: List[BenchmarkSuite]) -> bool:
        """Generate performance visualization charts."""
        try:
            print("\n📊 Generating performance charts...")
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('GIMP MCP Server Performance Benchmarks', fontsize=16)
            
            # Chart 1: Average operation duration by suite
            suite_names = [suite.suite_name for suite in benchmark_suites]
            avg_durations = [suite.summary_stats['avg_duration'] for suite in benchmark_suites]
            
            axes[0, 0].bar(suite_names, avg_durations, color='skyblue')
            axes[0, 0].set_title('Average Operation Duration by Suite')
            axes[0, 0].set_ylabel('Duration (seconds)')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Chart 2: Throughput comparison
            throughputs = [suite.summary_stats['throughput_ops_per_sec'] for suite in benchmark_suites]
            
            axes[0, 1].bar(suite_names, throughputs, color='lightgreen')
            axes[0, 1].set_title('Throughput by Suite')
            axes[0, 1].set_ylabel('Operations per Second')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Chart 3: Memory usage patterns
            if benchmark_suites:
                memory_deltas = [suite.summary_stats['avg_memory_delta'] for suite in benchmark_suites]
                
                axes[1, 0].bar(suite_names, memory_deltas, color='orange')
                axes[1, 0].set_title('Average Memory Delta by Suite')
                axes[1, 0].set_ylabel('Memory Change (MB)')
                axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Chart 4: Success rate
            success_rates = []
            for suite in benchmark_suites:
                total = suite.summary_stats['total_operations']
                successful = suite.summary_stats['successful_operations']
                success_rate = (successful / total * 100) if total > 0 else 0
                success_rates.append(success_rate)
            
            axes[1, 1].bar(suite_names, success_rates, color='lightcoral')
            axes[1, 1].set_title('Success Rate by Suite')
            axes[1, 1].set_ylabel('Success Rate (%)')
            axes[1, 1].set_ylim(0, 100)
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            chart_path = self.output_dir / f"{self.config['demo_name']}-performance-charts.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"📊 Performance charts saved: {chart_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate performance charts: {e}")
            return False
    
    async def generate_benchmark_report(self, benchmark_suites: List[BenchmarkSuite]) -> bool:
        """Generate comprehensive benchmark report."""
        try:
            print("\n📊 Generating benchmark report...")
            
            # Calculate overall statistics
            all_operations = []
            for suite in benchmark_suites:
                all_operations.extend(suite.operations)
            
            successful_ops = [op for op in all_operations if op.success]
            total_duration = sum(suite.total_time for suite in benchmark_suites)
            
            if successful_ops:
                overall_stats = {
                    "total_operations": len(all_operations),
                    "successful_operations": len(successful_ops),
                    "overall_success_rate": (len(successful_ops) / len(all_operations)) * 100,
                    "total_benchmark_time": total_duration,
                    "avg_operation_time": statistics.mean([op.duration for op in successful_ops]),
                    "median_operation_time": statistics.median([op.duration for op in successful_ops]),
                    "fastest_operation": min(successful_ops, key=lambda x: x.duration),
                    "slowest_operation": max(successful_ops, key=lambda x: x.duration),
                    "total_memory_impact": sum([op.memory_after - op.memory_before for op in successful_ops])
                }
            else:
                overall_stats = {
                    "total_operations": len(all_operations),
                    "successful_operations": 0,
                    "overall_success_rate": 0,
                    "total_benchmark_time": total_duration,
                    "avg_operation_time": 0,
                    "median_operation_time": 0,
                    "fastest_operation": None,
                    "slowest_operation": None,
                    "total_memory_impact": 0
                }
            
            # Create comprehensive report
            report = {
                "benchmark_info": {
                    "demo_name": self.config["demo_name"],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_suites": len(benchmark_suites),
                    "system_info": self.system_info
                },
                "overall_statistics": overall_stats,
                "suite_results": [
                    {
                        "suite_name": suite.suite_name,
                        "total_time": suite.total_time,
                        "summary_stats": suite.summary_stats,
                        "operation_details": [
                            {
                                "operation": op.operation_name,
                                "duration": op.duration,
                                "memory_delta": op.memory_after - op.memory_before,
                                "success": op.success,
                                "error": op.error
                            }
                            for op in suite.operations
                        ]
                    }
                    for suite in benchmark_suites
                ],
                "performance_insights": {
                    "fastest_suite": min(benchmark_suites, key=lambda x: x.summary_stats['avg_duration']).suite_name if benchmark_suites else None,
                    "slowest_suite": max(benchmark_suites, key=lambda x: x.summary_stats['avg_duration']).suite_name if benchmark_suites else None,
                    "most_efficient_suite": max(benchmark_suites, key=lambda x: x.summary_stats['throughput_ops_per_sec']).suite_name if benchmark_suites else None,
                    "memory_intensive_suite": max(benchmark_suites, key=lambda x: x.summary_stats['avg_memory_delta']).suite_name if benchmark_suites else None
                }
            }
            
            # Save detailed JSON report
            report_path = self.output_dir / f"{self.config['demo_name']}-detailed-report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            # Create summary report
            summary_path = self.output_dir / f"{self.config['demo_name']}-summary.txt"
            with open(summary_path, 'w') as f:
                f.write("GIMP MCP Server Performance Benchmark Summary\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Benchmark Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Benchmark Time: {total_duration:.2f} seconds\n")
                f.write(f"Total Operations: {overall_stats['total_operations']}\n")
                f.write(f"Successful Operations: {overall_stats['successful_operations']}\n")
                f.write(f"Success Rate: {overall_stats['overall_success_rate']:.1f}%\n\n")
                
                f.write("Performance Highlights:\n")
                f.write(f"  Average Operation Time: {overall_stats['avg_operation_time']:.3f}s\n")
                f.write(f"  Median Operation Time: {overall_stats['median_operation_time']:.3f}s\n")
                if overall_stats['fastest_operation']:
                    f.write(f"  Fastest Operation: {overall_stats['fastest_operation'].operation_name} ({overall_stats['fastest_operation'].duration:.3f}s)\n")
                if overall_stats['slowest_operation']:
                    f.write(f"  Slowest Operation: {overall_stats['slowest_operation'].operation_name} ({overall_stats['slowest_operation'].duration:.3f}s)\n")
                f.write(f"  Total Memory Impact: {overall_stats['total_memory_impact']:.2f} MB\n\n")
                
                f.write("Suite Performance Summary:\n")
                for suite in benchmark_suites:
                    f.write(f"  {suite.suite_name}:\n")
                    f.write(f"    Average Duration: {suite.summary_stats['avg_duration']:.3f}s\n")
                    f.write(f"    Throughput: {suite.summary_stats['throughput_ops_per_sec']:.1f} ops/sec\n")
                    f.write(f"    Success Rate: {(suite.summary_stats['successful_operations']/suite.summary_stats['total_operations']*100):.1f}%\n")
                    f.write(f"    Memory Delta: {suite.summary_stats['avg_memory_delta']:.2f} MB\n\n")
            
            # Print summary
            print(f"📊 Benchmark Results Summary:")
            print(f"   Total operations: {overall_stats['total_operations']}")
            print(f"   Success rate: {overall_stats['overall_success_rate']:.1f}%")
            print(f"   Average operation time: {overall_stats['avg_operation_time']:.3f}s")
            print(f"   Total benchmark time: {total_duration:.2f}s")
            print(f"   Performance insights:")
            for key, value in report["performance_insights"].items():
                if value:
                    print(f"     {key.replace('_', ' ').title()}: {value}")
            
            print(f"📄 Detailed report: {report_path}")
            print(f"📄 Summary report: {summary_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate benchmark report: {e}")
            return False
    
    async def cleanup(self) -> bool:
        """Clean up resources and close connections."""
        try:
            print("\n🧹 Cleaning up...")
            
            if self.current_document_id:
                try:
                    await self.session.call_tool("close_document", {
                        "document_id": self.current_document_id
                    })
                except:
                    pass
            
            if self.session:
                await self.session.close()
            
            print("✅ Cleanup completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to cleanup: {e}")
            return False
    
    async def run_full_benchmark(self, mode: str = "standard") -> bool:
        """Run the complete performance benchmark suite."""
        try:
            print("🚀 Starting GIMP MCP Server Performance Benchmarks")
            print("=" * 60)
            
            # Collect system information
            self.system_info = self.collect_system_info()
            print(f"💻 System: {self.system_info.get('cpu_count', 'unknown')} CPUs, "
                  f"{self.system_info.get('memory_total', 0) / 1024 / 1024 / 1024:.1f}GB RAM")
            
            # Connect to server
            if not await self.connect_to_server():
                return False
            
            # Determine iteration count based on mode
            iterations = self.config["iterations"].get(mode, 10)
            print(f"🔢 Running {mode} benchmark mode with {iterations} iterations per operation")
            
            # Run benchmark suites
            benchmark_suites = []
            
            for suite_config in self.config["benchmark_suites"]:
                suite_name = suite_config["name"]
                suite_result = await self.run_benchmark_suite(suite_name, iterations)
                if suite_result:
                    benchmark_suites.append(suite_result)
            
            # Generate visualizations
            await self.generate_performance_charts(benchmark_suites)
            
            # Generate reports
            await self.generate_benchmark_report(benchmark_suites)
            
            print("\n🎉 Performance Benchmarks completed successfully!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
            traceback.print_exc()
            return False
            
        finally:
            await self.cleanup()

async def main():
    """Main entry point for the performance benchmarks."""
    print("GIMP MCP Server - Performance Benchmarks")
    print("=" * 60)
    
    # Determine benchmark mode
    mode = "standard"
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode not in ["quick", "standard", "thorough"]:
            print(f"❌ Invalid mode: {mode}. Use 'quick', 'standard', or 'thorough'")
            sys.exit(1)
    
    # Create and run benchmarks
    benchmark = PerformanceBenchmark(BENCHMARK_CONFIG)
    success = await benchmark.run_full_benchmark(mode)
    
    if success:
        print("\n✅ Benchmarks completed successfully!")
        print(f"📁 Results available in: {BENCHMARK_CONFIG['output_dir']}")
        sys.exit(0)
    else:
        print("\n❌ Benchmarks failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())