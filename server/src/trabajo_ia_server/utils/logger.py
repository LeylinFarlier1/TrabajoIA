"""
Logging utilities for Trabajo IA Server.

Provides centralized logging configuration.
"""
import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup and configure a logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Create formatter
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


# Default logger for the application
default_logger = setup_logger("trabajo_ia_server")
