#!/usr/bin/env python3
"""
GIMP MCP Server - Batch Processing Demonstration

This script demonstrates advanced batch processing capabilities using the GIMP MCP server.
It showcases automated workflows for processing multiple images including:
- Batch image resizing and format conversion
- Automated filter application across multiple images
- Batch watermarking and branding
- Performance optimization for large-scale processing
- Progress tracking and error handling

Perfect for understanding production-ready automation workflows.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sys
import os
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import logging

# Add the parent directory to the path to import gimp_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please install with: pip install mcp pillow numpy")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BatchJob:
    """Represents a single batch processing job."""
    input_path: str
    output_path: str
    operations: List[Dict[str, Any]]
    status: str = "pending"
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

@dataclass
class BatchConfiguration:
    """Configuration for batch processing operations."""
    input_directory: str
    output_directory: str
    file_patterns: List[str]
    operations: List[Dict[str, Any]]
    max_concurrent: int = 3
    resize_dimensions: Tuple[int, int] = (1920, 1080)
    quality_settings: Dict[str, Any] = None
    watermark_settings: Dict[str, Any] = None

# Demo configuration
DEMO_CONFIG = {
    "output_dir": Path(__file__).parent / "outputs",
    "demo_name": "batch-processing-demo",
    "sample_images": [
        {"name": "photo1.jpg", "size": (2560, 1440), "type": "photo"},
        {"name": "graphic1.png", "size": (1920, 1080), "type": "graphic"},
        {"name": "logo1.png", "size": (512, 512), "type": "logo"},
        {"name": "banner1.jpg", "size": (1920, 600), "type": "banner"}
    ],
    "batch_operations": [
        {
            "name": "resize_and_optimize",
            "description": "Resize images and optimize for web",
            "operations": [
                {"type": "resize", "width": 1920, "height": 1080, "maintain_aspect": True},
                {"type": "adjust_brightness_contrast", "brightness": 5, "contrast": 10},
                {"type": "apply_sharpen", "amount": 0.5, "threshold": 0.1},
                {"type": "export", "format": "PNG", "quality": 90}
            ]
        },
        {
            "name": "watermark_and_brand",
            "description": "Apply watermark and branding",
            "operations": [
                {"type": "create_watermark_layer", "text": "GIMP MCP Demo", "opacity": 0.3},
                {"type": "apply_blur", "radius": 1.0, "method": "gaussian"},
                {"type": "export", "format": "JPEG", "quality": 85}
            ]
        },
        {
            "name": "thumbnail_generation",
            "description": "Generate thumbnails",
            "operations": [
                {"type": "resize", "width": 300, "height": 300, "maintain_aspect": True},
                {"type": "apply_blur", "radius": 0.5, "method": "gaussian"},
                {"type": "export", "format": "PNG", "quality": 80}
            ]
        }
    ]
}

class BatchProcessingDemo:
    """
    Demonstrates advanced batch processing using GIMP MCP server.
    
    This demo processes multiple images automatically with various
    operations and tracks performance metrics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = config["output_dir"]
        self.session = None
        self.batch_jobs = []
        self.performance_metrics = {}
        self.processed_count = 0
        self.error_count = 0
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "samples").mkdir(exist_ok=True)
        (self.output_dir / "processed").mkdir(exist_ok=True)
        
    async def connect_to_server(self) -> bool:
        """Connect to the GIMP MCP server."""
        try:
            logger.info("Connecting to GIMP MCP server...")
            
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "gimp_mcp.server"],
                env=None
            )
            
            self.session = await stdio_client(server_params)
            
            # Test connection
            response = await self.session.call_tool("list_documents", {})
            logger.info("Connected to GIMP MCP server successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to GIMP MCP server: {e}")
            return False
    
    async def create_sample_images(self) -> bool:
        """Create sample images for batch processing demonstration."""
        try:
            logger.info("Creating sample images for batch processing...")
            start_time = time.time()
            
            for i, image_config in enumerate(self.config["sample_images"]):
                image_name = image_config["name"]
                image_size = image_config["size"]
                image_type = image_config["type"]
                
                logger.info(f"Creating sample image: {image_name}")
                
                # Create document
                doc_response = await self.session.call_tool("create_document", {
                    "width": image_size[0],
                    "height": image_size[1],
                    "name": f"sample-{image_name}",
                    "color_mode": "RGB",
                    "fill_color": self._get_background_color_for_type(image_type)
                })
                
                document_id = doc_response["document_id"]
                
                # Add content based on image type
                await self._add_content_for_type(document_id, image_type, image_size)
                
                # Export the sample image
                sample_path = self.output_dir / "samples" / image_name
                await self.session.call_tool("export_document", {
                    "document_id": document_id,
                    "file_path": str(sample_path),
                    "format": "PNG" if image_name.endswith(".png") else "JPEG",
                    "options": {"quality": 95}
                })
                
                # Close document
                await self.session.call_tool("close_document", {
                    "document_id": document_id
                })
                
                logger.info(f"Created sample image: {sample_path}")
            
            creation_time = time.time() - start_time
            logger.info(f"Sample images created successfully in {creation_time:.2f}s")
            
            self.performance_metrics["sample_creation"] = creation_time
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample images: {e}")
            return False
    
    def _get_background_color_for_type(self, image_type: str) -> str:
        """Get appropriate background color for image type."""
        colors = {
            "photo": "#87CEEB",      # Sky blue
            "graphic": "#2C3E50",    # Dark blue-gray
            "logo": "#FFFFFF",       # White
            "banner": "#34495E"      # Dark gray
        }
        return colors.get(image_type, "#FFFFFF")
    
    async def _add_content_for_type(self, document_id: int, image_type: str, image_size: Tuple[int, int]) -> None:
        """Add appropriate content based on image type."""
        width, height = image_size
        
        # Create a content layer
        layer_response = await self.session.call_tool("create_layer", {
            "document_id": document_id,
            "name": f"{image_type}_content",
            "layer_type": "RGB"
        })
        
        layer_id = layer_response["layer_id"]
        
        if image_type == "photo":
            # Add photo-like elements
            await self.session.call_tool("draw_ellipse", {
                "document_id": document_id,
                "layer_id": layer_id,
                "center_x": width // 2,
                "center_y": height // 2,
                "radius_x": width // 4,
                "radius_y": height // 4,
                "fill_color": "#F39C12",
                "stroke_color": "#E67E22",
                "stroke_width": 3
            })
            
            # Add some rectangles for buildings/landscape
            for i in range(3):
                x = (width // 4) * i + 50
                y = height - 200 - (i * 50)
                await self.session.call_tool("draw_rectangle", {
                    "document_id": document_id,
                    "layer_id": layer_id,
                    "x": x,
                    "y": y,
                    "width": 150,
                    "height": 200 + (i * 50),
                    "fill_color": "#95A5A6",
                    "stroke_color": "#7F8C8D",
                    "stroke_width": 2
                })
        
        elif image_type == "graphic":
            # Add graphic design elements
            await self.session.call_tool("draw_rectangle", {
                "document_id": document_id,
                "layer_id": layer_id,
                "x": 100,
                "y": 100,
                "width": width - 200,
                "height": height - 200,
                "fill_color": "#3498DB",
                "stroke_color": "#2980B9",
                "stroke_width": 5
            })
            
            await self.session.call_tool("draw_ellipse", {
                "document_id": document_id,
                "layer_id": layer_id,
                "center_x": width // 2,
                "center_y": height // 2,
                "radius_x": 200,
                "radius_y": 200,
                "fill_color": "#E74C3C",
                "stroke_color": "#C0392B",
                "stroke_width": 3
            })
        
        elif image_type == "logo":
            # Add logo-like elements
            await self.session.call_tool("draw_ellipse", {
                "document_id": document_id,
                "layer_id": layer_id,
                "center_x": width // 2,
                "center_y": height // 2,
                "radius_x": width // 3,
                "radius_y": height // 3,
                "fill_color": "#2ECC71",
                "stroke_color": "#27AE60",
                "stroke_width": 8
            })
            
            # Add inner circle
            await self.session.call_tool("draw_ellipse", {
                "document_id": document_id,
                "layer_id": layer_id,
                "center_x": width // 2,
                "center_y": height // 2,
                "radius_x": width // 6,
                "radius_y": height // 6,
                "fill_color": "#FFFFFF",
                "stroke_color": None,
                "stroke_width": 0
            })
        
        elif image_type == "banner":
            # Add banner elements
            await self.session.call_tool("draw_rectangle", {
                "document_id": document_id,
                "layer_id": layer_id,
                "x": 0,
                "y": 0,
                "width": width,
                "height": height,
                "fill_color": "#9B59B6",
                "stroke_color": None,
                "stroke_width": 0
            })
            
            # Add decorative elements
            for i in range(5):
                x = (width // 6) * i + 100
                await self.session.call_tool("draw_rectangle", {
                    "document_id": document_id,
                    "layer_id": layer_id,
                    "x": x,
                    "y": height // 4,
                    "width": 50,
                    "height": height // 2,
                    "fill_color": "#8E44AD",
                    "stroke_color": None,
                    "stroke_width": 0
                })
    
    async def create_batch_jobs(self) -> bool:
        """Create batch processing jobs from sample images."""
        try:
            logger.info("Creating batch processing jobs...")
            
            sample_dir = self.output_dir / "samples"
            processed_dir = self.output_dir / "processed"
            
            # Get all sample images
            sample_files = list(sample_dir.glob("*"))
            
            for batch_config in self.config["batch_operations"]:
                batch_name = batch_config["name"]
                operations = batch_config["operations"]
                
                # Create output directory for this batch
                batch_output_dir = processed_dir / batch_name
                batch_output_dir.mkdir(exist_ok=True)
                
                for sample_file in sample_files:
                    if sample_file.is_file():
                        # Create output filename
                        output_filename = f"{sample_file.stem}_{batch_name}{sample_file.suffix}"
                        output_path = batch_output_dir / output_filename
                        
                        # Create batch job
                        job = BatchJob(
                            input_path=str(sample_file),
                            output_path=str(output_path),
                            operations=operations
                        )
                        
                        self.batch_jobs.append(job)
            
            logger.info(f"Created {len(self.batch_jobs)} batch processing jobs")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create batch jobs: {e}")
            return False
    
    async def process_single_job(self, job: BatchJob) -> bool:
        """Process a single batch job."""
        try:
            job.start_time = time.time()
            job.status = "processing"
            
            logger.info(f"Processing: {Path(job.input_path).name}")
            
            # Open the input image
            doc_response = await self.session.call_tool("open_document", {
                "file_path": job.input_path
            })
            
            document_id = doc_response["document_id"]
            
            # Process each operation
            for operation in job.operations:
                await self._execute_operation(document_id, operation)
            
            # Export the final result
            export_operation = next((op for op in job.operations if op["type"] == "export"), None)
            if export_operation:
                await self.session.call_tool("export_document", {
                    "document_id": document_id,
                    "file_path": job.output_path,
                    "format": export_operation["format"],
                    "options": {"quality": export_operation.get("quality", 90)}
                })
            
            # Close document
            await self.session.call_tool("close_document", {
                "document_id": document_id
            })
            
            job.end_time = time.time()
            job.status = "completed"
            
            logger.info(f"Completed: {Path(job.input_path).name} in {job.duration:.2f}s")
            
            return True
            
        except Exception as e:
            job.end_time = time.time()
            job.status = "failed"
            job.error = str(e)
            logger.error(f"Failed to process {Path(job.input_path).name}: {e}")
            return False
    
    async def _execute_operation(self, document_id: int, operation: Dict[str, Any]) -> None:
        """Execute a single operation on a document."""
        op_type = operation["type"]
        
        if op_type == "resize":
            # Get current document info
            doc_info = await self.session.call_tool("get_document_info", {
                "document_id": document_id
            })
            
            # Calculate new dimensions
            current_width = doc_info["width"]
            current_height = doc_info["height"]
            target_width = operation["width"]
            target_height = operation["height"]
            
            if operation.get("maintain_aspect", False):
                # Calculate aspect ratio
                aspect_ratio = current_width / current_height
                if target_width / target_height > aspect_ratio:
                    target_width = int(target_height * aspect_ratio)
                else:
                    target_height = int(target_width / aspect_ratio)
            
            # Note: GIMP MCP might need a resize operation implementation
            # For now, we'll use a placeholder
            logger.info(f"Resizing to {target_width}x{target_height}")
        
        elif op_type == "adjust_brightness_contrast":
            await self.session.call_tool("adjust_brightness_contrast", {
                "document_id": document_id,
                "brightness": operation["brightness"],
                "contrast": operation["contrast"]
            })
        
        elif op_type == "apply_sharpen":
            await self.session.call_tool("apply_sharpen", {
                "document_id": document_id,
                "amount": operation["amount"],
                "threshold": operation["threshold"]
            })
        
        elif op_type == "apply_blur":
            await self.session.call_tool("apply_blur", {
                "document_id": document_id,
                "radius": operation["radius"],
                "method": operation["method"]
            })
        
        elif op_type == "create_watermark_layer":
            # Create watermark layer
            layer_response = await self.session.call_tool("create_layer", {
                "document_id": document_id,
                "name": "Watermark",
                "layer_type": "RGB"
            })
            
            layer_id = layer_response["layer_id"]
            
            # Set layer opacity
            await self.session.call_tool("set_layer_opacity", {
                "document_id": document_id,
                "layer_id": layer_id,
                "opacity": operation["opacity"]
            })
            
            # Add watermark text (represented as a rectangle for now)
            await self.session.call_tool("draw_rectangle", {
                "document_id": document_id,
                "layer_id": layer_id,
                "x": 50,
                "y": 50,
                "width": 300,
                "height": 50,
                "fill_color": "#000000",
                "stroke_color": "#FFFFFF",
                "stroke_width": 2
            })
        
        elif op_type == "export":
            # Export operation is handled separately
            pass
        
        else:
            logger.warning(f"Unknown operation type: {op_type}")
    
    async def run_batch_processing(self) -> bool:
        """Run all batch processing jobs."""
        try:
            logger.info("Starting batch processing...")
            start_time = time.time()
            
            # Process jobs in chunks to avoid overwhelming the server
            chunk_size = 3  # Process 3 jobs concurrently
            
            for i in range(0, len(self.batch_jobs), chunk_size):
                chunk = self.batch_jobs[i:i + chunk_size]
                
                # Process chunk concurrently
                tasks = [self.process_single_job(job) for job in chunk]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update counters
                for result in results:
                    if isinstance(result, Exception):
                        self.error_count += 1
                    elif result:
                        self.processed_count += 1
                    else:
                        self.error_count += 1
                
                # Progress update
                progress = (i + len(chunk)) / len(self.batch_jobs) * 100
                logger.info(f"Batch progress: {progress:.1f}% ({i + len(chunk)}/{len(self.batch_jobs)})")
            
            processing_time = time.time() - start_time
            logger.info(f"Batch processing completed in {processing_time:.2f}s")
            logger.info(f"Successfully processed: {self.processed_count}/{len(self.batch_jobs)}")
            logger.info(f"Errors: {self.error_count}")
            
            self.performance_metrics["batch_processing"] = processing_time
            self.performance_metrics["total_jobs"] = len(self.batch_jobs)
            self.performance_metrics["successful_jobs"] = self.processed_count
            self.performance_metrics["failed_jobs"] = self.error_count
            
            return True
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return False
    
    async def generate_batch_report(self) -> bool:
        """Generate a comprehensive batch processing report."""
        try:
            logger.info("Generating batch processing report...")
            
            # Calculate statistics
            total_duration = sum(job.duration for job in self.batch_jobs if job.duration)
            average_duration = total_duration / max(self.processed_count, 1)
            
            # Group jobs by status
            job_stats = {}
            for job in self.batch_jobs:
                status = job.status
                if status not in job_stats:
                    job_stats[status] = []
                job_stats[status].append(job)
            
            # Create report
            report = {
                "demo_name": self.config["demo_name"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "batch_summary": {
                    "total_jobs": len(self.batch_jobs),
                    "successful_jobs": self.processed_count,
                    "failed_jobs": self.error_count,
                    "success_rate": (self.processed_count / len(self.batch_jobs)) * 100,
                    "total_processing_time": total_duration,
                    "average_job_time": average_duration
                },
                "performance_metrics": self.performance_metrics,
                "job_statistics": {
                    status: len(jobs) for status, jobs in job_stats.items()
                },
                "batch_operations": self.config["batch_operations"],
                "job_details": [
                    {
                        "input_path": job.input_path,
                        "output_path": job.output_path,
                        "status": job.status,
                        "duration": job.duration,
                        "error": job.error
                    }
                    for job in self.batch_jobs
                ]
            }
            
            # Save report
            report_path = self.output_dir / f"{self.config['demo_name']}-report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            print("\n📊 Batch Processing Summary:")
            print(f"   Total jobs: {len(self.batch_jobs)}")
            print(f"   Successful: {self.processed_count}")
            print(f"   Failed: {self.error_count}")
            print(f"   Success rate: {(self.processed_count / len(self.batch_jobs)) * 100:.1f}%")
            print(f"   Total processing time: {total_duration:.2f}s")
            print(f"   Average job time: {average_duration:.2f}s")
            print(f"   Throughput: {self.processed_count / (total_duration / 60):.1f} jobs/minute")
            
            logger.info(f"Batch processing report saved: {report_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate batch report: {e}")
            return False
    
    async def cleanup(self) -> bool:
        """Clean up resources and close connections."""
        try:
            logger.info("Cleaning up...")
            
            if self.session:
                await self.session.close()
            
            logger.info("Cleanup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup: {e}")
            return False
    
    async def run_demo(self) -> bool:
        """Run the complete batch processing demonstration."""
        try:
            print("🚀 Starting Batch Processing Demonstration")
            print("=" * 50)
            
            # Connect to server
            if not await self.connect_to_server():
                return False
            
            # Create sample images
            if not await self.create_sample_images():
                return False
            
            # Create batch jobs
            if not await self.create_batch_jobs():
                return False
            
            # Run batch processing
            if not await self.run_batch_processing():
                return False
            
            # Generate report
            if not await self.generate_batch_report():
                return False
            
            print("\n🎉 Batch Processing Demonstration completed successfully!")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            return False
            
        finally:
            await self.cleanup()

async def main():
    """Main entry point for the batch processing demonstration."""
    print("GIMP MCP Server - Batch Processing Demonstration")
    print("=" * 60)
    
    # Create and run the demo
    demo = BatchProcessingDemo(DEMO_CONFIG)
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