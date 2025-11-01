"""
Trabajo IA MCP Server.

A Model Context Protocol (MCP) server for accessing FRED economic data.
"""
__version__ = "0.1.8"
__author__ = "Trabajo IA Team"

from trabajo_ia_server.server import mcp, main

__all__ = ["mcp", "main", "__version__"]
