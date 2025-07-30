"""
GIMP MCP Server Resource Providers

This package contains all MCP resource provider implementations
for real-time GIMP state and system information.
"""

from .providers import ResourceProviders

__all__ = [
    "ResourceProviders",
]