"""Logging utilities for Trabajo IA Server with structured output support."""

from __future__ import annotations

import contextlib
import contextvars
import json
import logging
import os
import sys
from contextlib import contextmanager
from typing import Any, Dict, Optional

_REQUEST_ID: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trabajo_ia_request_id", default=None
)

RESERVED_RECORD_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "asctime",
}


def get_request_id() -> Optional[str]:
    """Return the current request identifier if one has been bound."""

    return _REQUEST_ID.get()


def bind_request_id(request_id: Optional[str]) -> contextvars.Token[Optional[str]]:
    """Bind a request identifier to the current context."""

    return _REQUEST_ID.set(request_id)


def reset_request_id(token: contextvars.Token[Optional[str]]) -> None:
    """Reset the request identifier to a previous context token."""

    _REQUEST_ID.reset(token)


@contextmanager
def request_context(request_id: Optional[str]):
    """Context manager that binds a request identifier for log correlation."""

    token: Optional[contextvars.Token[Optional[str]]] = None
    if request_id is not None:
        token = bind_request_id(request_id)
    try:
        yield
    finally:
        if token is not None:
            reset_request_id(token)


class RequestContextFilter(logging.Filter):
    """Inject the current request id into log records when available."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        if getattr(record, "request_id", None) is None:
            request_id = get_request_id()
            if request_id is not None:
                record.request_id = request_id
        return True


class JsonFormatter(logging.Formatter):
    """Serialize log records as JSON for ingestion into observability stacks."""

    def __init__(self, *, indent: Optional[int] = None) -> None:
        super().__init__(datefmt="%Y-%m-%dT%H:%M:%S.%fZ")
        self._indent = indent

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - formatting
        base: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "request_id", None)
        if request_id is not None:
            base["request_id"] = request_id

        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            base["stack"] = record.stack_info

        # Capture any custom attributes added to the record (excluding internal keys)
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in RESERVED_RECORD_ATTRS and not key.startswith("_")
        }
        if extras:
            base["extras"] = extras

        return json.dumps(base, indent=self._indent, default=str, separators=(",", ":"))


def _resolve_log_configuration(level: Optional[str]) -> tuple[str, str, Optional[int]]:
    """Derive the effective log level, format, and indent settings."""

    resolved_level = level
    log_format = None
    indent: Optional[int] = None

    if resolved_level is not None:
        resolved_level = resolved_level.upper()

    try:  # Prefer central configuration when available
        import trabajo_ia_server.config as config_module  # type: ignore

        config_level = getattr(config_module.Config, "LOG_LEVEL", "INFO")
        config_format = getattr(config_module.Config, "LOG_FORMAT", "plain")
        config_indent = getattr(config_module.Config, "LOG_JSON_INDENT", None)

        resolved_level = resolved_level or str(config_level).upper()
        log_format = str(config_format)
        indent = config_indent if isinstance(config_indent, int) else None
    except Exception:  # pragma: no cover - defensive fallback
        resolved_level = resolved_level or os.getenv("LOG_LEVEL", "INFO").upper()
        log_format = os.getenv("LOG_FORMAT", "plain")
        indent_value = os.getenv("LOG_JSON_INDENT")
        if indent_value is not None:
            with contextlib.suppress(ValueError):
                indent = max(0, int(indent_value))

    log_format = log_format or "plain"
    return resolved_level, log_format.lower(), indent


def setup_logger(
    name: str,
    level: Optional[str] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """Setup and configure a logger instance."""

    logger = logging.getLogger(name)
    resolved_level, log_format, indent = _resolve_log_configuration(level)
    numeric_level = getattr(logging, resolved_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    stream_handler: Optional[logging.Handler] = None
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            stream_handler = handler
            break

    if stream_handler is None:
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)

    stream_handler.setLevel(numeric_level)

    if log_format == "json":
        formatter = JsonFormatter(indent=indent)
    else:
        if format_string is None:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format_string)
    stream_handler.setFormatter(formatter)

    if not any(isinstance(f, RequestContextFilter) for f in logger.filters):
        logger.addFilter(RequestContextFilter())
    if not any(isinstance(f, RequestContextFilter) for f in stream_handler.filters):
        stream_handler.addFilter(RequestContextFilter())

    return logger


# Default logger for the application
default_logger = setup_logger("trabajo_ia_server")

__all__ = [
    "setup_logger",
    "default_logger",
    "request_context",
    "bind_request_id",
    "reset_request_id",
    "get_request_id",
]
