"""
Logging utilities for GIMP MCP Server

This module provides structured logging configuration and utilities
for the GIMP MCP Server implementation.
"""

import logging
import sys
from typing import Optional, Dict, Any

import structlog


def setup_logging(level: int = logging.INFO, debug: bool = False) -> None:
    """
    Setup structured logging for the GIMP MCP Server.
    
    Args:
        level: Logging level (default: INFO)
        debug: Enable debug mode with more verbose logging
    """
    # Configure stdlib logging
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if not debug else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set specific logger levels
    if debug:
        logging.getLogger("gimp_mcp").setLevel(logging.DEBUG)
    else:
        logging.getLogger("gimp_mcp").setLevel(level)
    
    # Quiet some noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structured logger
    """
    return structlog.get_logger(name)


class GimpLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds GIMP-specific context to log messages.
    """
    
    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process log message with additional context."""
        # Add GIMP-specific context
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        # Merge adapter extra with message extra
        kwargs["extra"].update(self.extra)
        
        return msg, kwargs


def create_operation_logger(operation_name: str, **context) -> GimpLoggerAdapter:
    """
    Create a logger for a specific GIMP operation.
    
    Args:
        operation_name: Name of the operation
        **context: Additional context to include in logs
        
    Returns:
        Configured logger adapter
    """
    logger = logging.getLogger(f"gimp_mcp.operations.{operation_name}")
    
    extra = {
        "operation": operation_name,
        **context,
    }
    
    return GimpLoggerAdapter(logger, extra)


def log_operation_start(logger: logging.Logger, operation: str, **kwargs) -> None:
    """
    Log the start of a GIMP operation.
    
    Args:
        logger: Logger instance
        operation: Operation name
        **kwargs: Operation parameters
    """
    logger.info(
        f"Starting operation: {operation}",
        extra={
            "operation": operation,
            "stage": "start",
            "parameters": kwargs,
        }
    )


def log_operation_success(logger: logging.Logger, operation: str, result: Any = None, **kwargs) -> None:
    """
    Log successful completion of a GIMP operation.
    
    Args:
        logger: Logger instance
        operation: Operation name
        result: Operation result
        **kwargs: Additional context
    """
    logger.info(
        f"Operation completed successfully: {operation}",
        extra={
            "operation": operation,
            "stage": "success",
            "result_type": type(result).__name__ if result is not None else None,
            **kwargs,
        }
    )


def log_operation_error(logger: logging.Logger, operation: str, error: Exception, **kwargs) -> None:
    """
    Log error in a GIMP operation.
    
    Args:
        logger: Logger instance
        operation: Operation name
        error: Exception that occurred
        **kwargs: Additional context
    """
    logger.error(
        f"Operation failed: {operation}",
        extra={
            "operation": operation,
            "stage": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            **kwargs,
        },
        exc_info=True,
    )


def log_performance_metric(logger: logging.Logger, operation: str, duration: float, **kwargs) -> None:
    """
    Log performance metrics for a GIMP operation.
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration: Operation duration in seconds
        **kwargs: Additional metrics
    """
    logger.info(
        f"Performance metric for {operation}",
        extra={
            "operation": operation,
            "metric_type": "performance",
            "duration_seconds": duration,
            **kwargs,
        }
    )


def log_resource_usage(logger: logging.Logger, operation: str, **metrics) -> None:
    """
    Log resource usage metrics for a GIMP operation.
    
    Args:
        logger: Logger instance
        operation: Operation name
        **metrics: Resource usage metrics
    """
    logger.info(
        f"Resource usage for {operation}",
        extra={
            "operation": operation,
            "metric_type": "resource_usage",
            **metrics,
        }
    )


def log_gimp_connection_event(logger: logging.Logger, event: str, **context) -> None:
    """
    Log GIMP connection events.
    
    Args:
        logger: Logger instance
        event: Event name (connected, disconnected, error, etc.)
        **context: Additional context
    """
    logger.info(
        f"GIMP connection event: {event}",
        extra={
            "event_type": "gimp_connection",
            "event": event,
            **context,
        }
    )


def log_mcp_event(logger: logging.Logger, event: str, **context) -> None:
    """
    Log MCP protocol events.
    
    Args:
        logger: Logger instance
        event: Event name
        **context: Additional context
    """
    logger.info(
        f"MCP event: {event}",
        extra={
            "event_type": "mcp_protocol",
            "event": event,
            **context,
        }
    )


class PerformanceTimer:
    """Context manager for measuring operation performance."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        log_operation_start(self.logger, self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type is None:
            log_operation_success(self.logger, self.operation)
            log_performance_metric(self.logger, self.operation, duration)
        else:
            log_operation_error(self.logger, self.operation, exc_val)
        
        return False  # Don't suppress exceptions


def performance_timer(logger: logging.Logger, operation: str) -> PerformanceTimer:
    """
    Create a performance timer for an operation.
    
    Args:
        logger: Logger instance
        operation: Operation name
        
    Returns:
        Performance timer context manager
    """
    return PerformanceTimer(logger, operation)