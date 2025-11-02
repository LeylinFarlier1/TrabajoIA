"""Trabajo IA MCP Server package exports."""

__version__ = "0.1.9"
__author__ = "Trabajo IA Team"

__all__ = ["mcp", "main", "__version__"]


def __getattr__(name: str):  # pragma: no cover - thin forwarding logic
    if name in {"mcp", "main"}:
        from trabajo_ia_server import server as _server

        return getattr(_server, name)
    raise AttributeError(f"module 'trabajo_ia_server' has no attribute '{name}'")
