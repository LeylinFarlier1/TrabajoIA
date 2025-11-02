"""System health check tool providing operational diagnostics."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

from trabajo_ia_server import __version__
from trabajo_ia_server.config import config
from trabajo_ia_server.utils.cache import cache_manager
from trabajo_ia_server.utils.logger import setup_logger
from trabajo_ia_server.utils.metrics import metrics
from trabajo_ia_server.utils.rate_limiter import rate_limiter

logger = setup_logger(__name__)


def _config_snapshot() -> Dict[str, Any]:
    return {
        "log_level": config.LOG_LEVEL,
        "log_format": getattr(config, "LOG_FORMAT", "plain"),
        "cache_backend": getattr(config, "CACHE_BACKEND", "memory"),
        "metrics_enabled": config.METRICS_ENABLED,
    }


def system_health() -> str:
    """Return a compact JSON payload summarising runtime health."""

    logger.debug("Generating system health snapshot")

    cache_info = cache_manager.describe()
    limiter_info = (
        rate_limiter.snapshot() if hasattr(rate_limiter, "snapshot") else {"enabled": False}
    )
    if metrics.enabled:
        metrics_info: Dict[str, Any] = metrics.export()
        metrics_info["enabled"] = True
        metrics_info["names"] = metrics.list_metrics()
    else:
        metrics_info = {"enabled": False}

    payload: Dict[str, Any] = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": __version__,
        "config": _config_snapshot(),
        "cache": cache_info,
        "rate_limiter": limiter_info,
        "metrics": metrics_info,
    }

    return json.dumps(payload, separators=(",", ":"))


__all__ = ["system_health"]
