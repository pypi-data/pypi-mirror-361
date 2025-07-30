"""
Error handling utilities for GIMP MCP Server

This module provides a comprehensive error hierarchy and safe operation
decorators for handling GIMP-related errors gracefully.
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class GimpError(Exception):
    """Base exception for all GIMP MCP server errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class GimpConnectionError(GimpError):
    """Raised when GIMP connection issues occur."""
    pass


class GimpOperationError(GimpError):
    """Raised when GIMP operations fail."""
    pass


class GimpResourceError(GimpError):
    """Raised when resource access fails."""
    pass


class GimpValidationError(GimpError):
    """Raised when parameter validation fails."""
    pass


class GimpModeError(GimpError):
    """Raised when mode-specific operations fail."""
    pass


class GimpImageError(GimpError):
    """Raised when image-related operations fail."""
    pass


class GimpLayerError(GimpError):
    """Raised when layer-related operations fail."""
    pass


class GimpDrawingError(GimpError):
    """Raised when drawing operations fail."""
    pass


class GimpFileError(GimpError):
    """Raised when file operations fail."""
    pass


class GimpBrushError(GimpError):
    """Raised when brush operations fail."""
    pass


class GimpColorError(GimpError):
    """Raised when color operations fail."""
    pass


def safe_operation(operation_name: str, return_on_error: Optional[Dict[str, Any]] = None):
    """
    Decorator for safe GIMP operations with comprehensive error handling.
    
    Args:
        operation_name: Name of the operation for logging
        return_on_error: Default return value on error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                logger.info(f"Starting operation: {operation_name}")
                result = await func(*args, **kwargs)
                logger.info(f"Completed operation: {operation_name}")
                return result
            except GimpError as e:
                logger.error(f"GIMP error in {operation_name}: {e.message}", extra=e.details)
                return return_on_error or {
                    "success": False,
                    "error": e.message,
                    "error_type": e.__class__.__name__,
                    "operation": operation_name,
                    "details": e.details,
                }
            except Exception as e:
                logger.error(f"Unexpected error in {operation_name}: {str(e)}", exc_info=True)
                return return_on_error or {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_type": "UnexpectedError",
                    "operation": operation_name,
                }
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                logger.info(f"Starting operation: {operation_name}")
                result = func(*args, **kwargs)
                logger.info(f"Completed operation: {operation_name}")
                return result
            except GimpError as e:
                logger.error(f"GIMP error in {operation_name}: {e.message}", extra=e.details)
                return return_on_error or {
                    "success": False,
                    "error": e.message,
                    "error_type": e.__class__.__name__,
                    "operation": operation_name,
                    "details": e.details,
                }
            except Exception as e:
                logger.error(f"Unexpected error in {operation_name}: {str(e)}", exc_info=True)
                return return_on_error or {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_type": "UnexpectedError",
                    "operation": operation_name,
                }
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_required_params(required_params: list, provided_params: dict) -> None:
    """
    Validate that all required parameters are provided.
    
    Args:
        required_params: List of required parameter names
        provided_params: Dictionary of provided parameters
        
    Raises:
        GimpValidationError: If required parameters are missing
    """
    missing_params = [param for param in required_params if param not in provided_params]
    
    if missing_params:
        raise GimpValidationError(
            f"Missing required parameters: {', '.join(missing_params)}",
            details={"missing_params": missing_params, "provided_params": list(provided_params.keys())}
        )


def validate_param_type(param_name: str, param_value: Any, expected_type: type) -> None:
    """
    Validate parameter type.
    
    Args:
        param_name: Name of the parameter
        param_value: Value to validate
        expected_type: Expected type
        
    Raises:
        GimpValidationError: If parameter type is incorrect
    """
    if not isinstance(param_value, expected_type):
        raise GimpValidationError(
            f"Parameter '{param_name}' must be of type {expected_type.__name__}, got {type(param_value).__name__}",
            details={
                "param_name": param_name,
                "expected_type": expected_type.__name__,
                "actual_type": type(param_value).__name__,
                "value": str(param_value),
            }
        )


def validate_param_range(param_name: str, param_value: float, min_val: float, max_val: float) -> None:
    """
    Validate parameter is within specified range.
    
    Args:
        param_name: Name of the parameter
        param_value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Raises:
        GimpValidationError: If parameter is out of range
    """
    if not (min_val <= param_value <= max_val):
        raise GimpValidationError(
            f"Parameter '{param_name}' must be between {min_val} and {max_val}, got {param_value}",
            details={
                "param_name": param_name,
                "value": param_value,
                "min_val": min_val,
                "max_val": max_val,
            }
        )


def validate_param_choices(param_name: str, param_value: Any, choices: list) -> None:
    """
    Validate parameter is one of allowed choices.
    
    Args:
        param_name: Name of the parameter
        param_value: Value to validate
        choices: List of allowed choices
        
    Raises:
        GimpValidationError: If parameter is not in choices
    """
    if param_value not in choices:
        raise GimpValidationError(
            f"Parameter '{param_name}' must be one of {choices}, got {param_value}",
            details={
                "param_name": param_name,
                "value": param_value,
                "choices": choices,
            }
        )


def handle_gimp_exception(operation: str, exception: Exception) -> Dict[str, Any]:
    """
    Handle GIMP exceptions and convert to standardized error response.
    
    Args:
        operation: Name of the operation that failed
        exception: The exception that occurred
        
    Returns:
        Standardized error response dictionary
    """
    if isinstance(exception, GimpError):
        return {
            "success": False,
            "error": exception.message,
            "error_type": exception.__class__.__name__,
            "operation": operation,
            "details": exception.details,
        }
    else:
        return {
            "success": False,
            "error": str(exception),
            "error_type": "UnexpectedError",
            "operation": operation,
        }


def validate_image_id(image_id: int) -> None:
    """
    Validate image ID parameter.
    
    Args:
        image_id: Image ID to validate
        
    Raises:
        GimpValidationError: If image ID is invalid
    """
    if not isinstance(image_id, int):
        raise GimpValidationError(
            f"Image ID must be an integer, got {type(image_id).__name__}",
            details={"image_id": image_id, "expected_type": "int"}
        )
    
    if image_id < 0:
        raise GimpValidationError(
            f"Image ID must be non-negative, got {image_id}",
            details={"image_id": image_id}
        )


def validate_layer_id(layer_id: int) -> None:
    """
    Validate layer ID parameter.
    
    Args:
        layer_id: Layer ID to validate
        
    Raises:
        GimpValidationError: If layer ID is invalid
    """
    if not isinstance(layer_id, int):
        raise GimpValidationError(
            f"Layer ID must be an integer, got {type(layer_id).__name__}",
            details={"layer_id": layer_id, "expected_type": "int"}
        )
    
    if layer_id < 0:
        raise GimpValidationError(
            f"Layer ID must be non-negative, got {layer_id}",
            details={"layer_id": layer_id}
        )


def validate_file_path(file_path: str, must_exist: bool = False) -> None:
    """
    Validate file path parameter.
    
    Args:
        file_path: File path to validate
        must_exist: Whether the file must already exist
        
    Raises:
        GimpValidationError: If file path is invalid
    """
    if not isinstance(file_path, str):
        raise GimpValidationError(
            f"File path must be a string, got {type(file_path).__name__}",
            details={"file_path": file_path, "expected_type": "str"}
        )
    
    if not file_path.strip():
        raise GimpValidationError(
            "File path cannot be empty",
            details={"file_path": file_path}
        )
    
    if must_exist:
        import os
        if not os.path.exists(file_path):
            raise GimpValidationError(
                f"File does not exist: {file_path}",
                details={"file_path": file_path, "exists": False}
            )


def validate_color_string(color: str) -> None:
    """
    Validate color string parameter.
    
    Args:
        color: Color string to validate
        
    Raises:
        GimpValidationError: If color string is invalid
    """
    if not isinstance(color, str):
        raise GimpValidationError(
            f"Color must be a string, got {type(color).__name__}",
            details={"color": color, "expected_type": "str"}
        )
    
    # Import here to avoid circular imports
    from .image_utils import validate_color
    
    if not validate_color(color):
        raise GimpValidationError(
            f"Invalid color format: {color}",
            details={"color": color, "valid_formats": ["#RGB", "#RRGGBB", "#RRGGBBAA", "rgb(r,g,b)", "rgba(r,g,b,a)", "named colors"]}
        )


def validate_blend_mode(blend_mode: str) -> None:
    """
    Validate blend mode parameter.
    
    Args:
        blend_mode: Blend mode to validate
        
    Raises:
        GimpValidationError: If blend mode is invalid
    """
    if not isinstance(blend_mode, str):
        raise GimpValidationError(
            f"Blend mode must be a string, got {type(blend_mode).__name__}",
            details={"blend_mode": blend_mode, "expected_type": "str"}
        )
    
    valid_blend_modes = [
        'normal', 'multiply', 'screen', 'overlay', 'soft_light', 'hard_light',
        'color_dodge', 'color_burn', 'darken_only', 'lighten_only',
        'difference', 'exclusion', 'hue', 'saturation', 'color', 'value'
    ]
    
    if blend_mode.lower() not in valid_blend_modes:
        raise GimpValidationError(
            f"Invalid blend mode: {blend_mode}",
            details={
                "blend_mode": blend_mode,
                "valid_modes": valid_blend_modes
            }
        )


def create_error_context(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Create standardized error context for operations.
    
    Args:
        operation: Name of the operation
        **kwargs: Additional context parameters
        
    Returns:
        Error context dictionary
    """
    import time
    
    context = {
        "operation": operation,
        "timestamp": time.time(),
        "context": kwargs
    }
    
    return context


def log_error_with_context(logger_instance, error: Exception, context: Dict[str, Any]) -> None:
    """
    Log error with detailed context information.
    
    Args:
        logger_instance: Logger instance to use
        error: Exception that occurred
        context: Error context information
    """
    error_details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "operation": context.get("operation", "unknown"),
        "timestamp": context.get("timestamp"),
        "context": context.get("context", {})
    }
    
    logger_instance.error(f"Operation failed: {error_details['operation']}", extra=error_details)


def wrap_gimp_operation(operation_name: str):
    """
    Decorator to wrap GIMP operations with comprehensive error handling.
    
    Args:
        operation_name: Name of the GIMP operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = create_error_context(operation_name, args=args, kwargs=kwargs)
            
            try:
                logger.info(f"Starting GIMP operation: {operation_name}")
                result = await func(*args, **kwargs)
                logger.info(f"Completed GIMP operation: {operation_name}")
                return result
                
            except (GimpImageError, GimpLayerError, GimpDrawingError, GimpFileError,
                    GimpBrushError, GimpColorError) as e:
                log_error_with_context(logger, e, context)
                return {
                    "success": False,
                    "error": e.message,
                    "error_type": e.__class__.__name__,
                    "operation": operation_name,
                    "details": e.details,
                    "context": context
                }
                
            except GimpError as e:
                log_error_with_context(logger, e, context)
                return {
                    "success": False,
                    "error": e.message,
                    "error_type": e.__class__.__name__,
                    "operation": operation_name,
                    "details": e.details,
                    "context": context
                }
                
            except Exception as e:
                log_error_with_context(logger, e, context)
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_type": "UnexpectedError",
                    "operation": operation_name,
                    "context": context
                }
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            context = create_error_context(operation_name, args=args, kwargs=kwargs)
            
            try:
                logger.info(f"Starting GIMP operation: {operation_name}")
                result = func(*args, **kwargs)
                logger.info(f"Completed GIMP operation: {operation_name}")
                return result
                
            except (GimpImageError, GimpLayerError, GimpDrawingError, GimpFileError,
                    GimpBrushError, GimpColorError) as e:
                log_error_with_context(logger, e, context)
                return {
                    "success": False,
                    "error": e.message,
                    "error_type": e.__class__.__name__,
                    "operation": operation_name,
                    "details": e.details,
                    "context": context
                }
                
            except GimpError as e:
                log_error_with_context(logger, e, context)
                return {
                    "success": False,
                    "error": e.message,
                    "error_type": e.__class__.__name__,
                    "operation": operation_name,
                    "details": e.details,
                    "context": context
                }
                
            except Exception as e:
                log_error_with_context(logger, e, context)
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_type": "UnexpectedError",
                    "operation": operation_name,
                    "context": context
                }
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def format_error_for_mcp(error: Exception, operation: str = "unknown") -> Dict[str, Any]:
    """
    Format error for MCP server response.
    
    Args:
        error: Exception that occurred
        operation: Name of the operation that failed
        
    Returns:
        Formatted error dictionary
    """
    import time
    
    if isinstance(error, GimpError):
        return {
            "success": False,
            "error": {
                "type": error.__class__.__name__,
                "message": error.message,
                "details": error.details,
                "operation": operation,
                "timestamp": time.time()
            }
        }
    else:
        return {
            "success": False,
            "error": {
                "type": "UnexpectedError",
                "message": str(error),
                "operation": operation,
                "timestamp": time.time()
            }
        }


# Import asyncio at the end to avoid circular imports
import asyncio