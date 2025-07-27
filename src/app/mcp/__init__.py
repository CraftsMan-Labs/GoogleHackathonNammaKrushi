"""
NammaKrushi Model Context Protocol (MCP) Server

Provides agricultural AI services through the standardized MCP interface
while maintaining zero data retention for farmer privacy.

This package includes:
- MCP server implementation
- Agricultural tools (disease analysis, weather, soil, search)
- Agricultural resources (crop calendar, disease database)
- Agricultural prompts (diagnosis, planning, advisory)
- Zero-retention security layer
"""

from .server import get_mcp_server, NammaKrushiMCPServer
from .config.mcp_settings import get_mcp_config, get_zero_retention_config
from .security.zero_retention import get_zero_retention_proxy

__version__ = "1.0.0"
__author__ = "NammaKrushi Team"
__description__ = "Agricultural AI services via Model Context Protocol"

__all__ = [
    "get_mcp_server",
    "NammaKrushiMCPServer",
    "get_mcp_config",
    "get_zero_retention_config",
    "get_zero_retention_proxy",
]
