"""OpenMemory MCP Bridge Package"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development mode

__author__ = "Ankit Patel"
__email__ = "ankitpasi1@gmail.com"

from .main import OpenMemoryMCPBridge

__all__ = ["OpenMemoryMCPBridge"] 