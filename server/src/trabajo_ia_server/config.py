"""Configuration module for Trabajo IA Server."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Tuple


def _load_env_file(dotenv_path: Path) -> None:
    """Best-effort loader for ``.env`` files when ``python-dotenv`` is missing.

    The production dependency list still includes ``python-dotenv``.  However,
    our test environment stubs optional dependencies to keep unit tests
    lightweight.  Importing :mod:`python-dotenv` in that context would raise an
    :class:`ImportError`, so we provide this tiny fallback that mirrors the
    subset of functionality we rely on (simple ``KEY=VALUE`` assignments).
    """

    if not dotenv_path.exists():
        return

    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")

        os.environ.setdefault(key, value)


env_path = Path(__file__).parent.parent.parent / ".env"

try:  # pragma: no cover - executed only when dependency is available
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=env_path)
except Exception:  # pragma: no cover - executed in lightweight test envs
    _load_env_file(env_path)


def _str_to_bool(value: Optional[str], default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "off", "no"}


def _safe_int(value: Optional[str], default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class Config:
    """Central configuration class for the MCP server."""

    # FRED API Configuration
    FRED_API_KEY: Optional[str] = os.getenv("FRED_API_KEY")

    # Server Configuration
    SERVER_NAME: str = "trabajo-ia-server"
    SERVER_VERSION: str = "0.1.9"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "plain")
    LOG_JSON_INDENT: Optional[int] = None
    try:
        _indent_value = os.getenv("LOG_JSON_INDENT")
        if _indent_value is not None:
            LOG_JSON_INDENT = max(0, int(_indent_value))
    except (TypeError, ValueError):
        LOG_JSON_INDENT = None

    # Cache configuration
    CACHE_ENABLED: bool = _str_to_bool(os.getenv("CACHE_ENABLED"), default=True)
    CACHE_BACKEND: str = os.getenv("CACHE_BACKEND", "memory")
    CACHE_DEFAULT_TTL_SECONDS: int = max(
        0, _safe_int(os.getenv("CACHE_DEFAULT_TTL_SECONDS"), 300)
    )
    CACHE_DISKCACHE_DIRECTORY: str = os.getenv(
        "CACHE_DISKCACHE_DIRECTORY",
        str(Path(__file__).parent.parent.parent / ".cache" / "trabajo_ia"),
    )
    CACHE_REDIS_URL: str = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")
    CACHE_REDIS_PREFIX: str = os.getenv("CACHE_REDIS_PREFIX", "trabajo-ia")
    CACHE_NAMESPACE_DEFAULTS: Dict[str, Optional[int]] = {
        "search_series": 300,
        "search_series_tags": 300,
        "search_series_related_tags": 300,
        "series_by_tags": 300,
        "get_series_tags": 900,
        "get_fred_tags": 1800,
        "search_fred_related_tags": 1800,
        "related_tags": 1800,
        "category": 3600,
        "category_children": 3600,
        "category_related": 3600,
        "category_series": 900,
        "category_tags": 1800,
        "category_related_tags": 1800,
        "observations": 900,
    }

    # Coordinated FRED rate limit configuration
    FRED_RATE_LIMIT_ENABLED: bool = _str_to_bool(
        os.getenv("FRED_RATE_LIMIT_ENABLED"), default=True
    )
    FRED_RATE_LIMIT_PER_SECOND: int = max(
        0, _safe_int(os.getenv("FRED_RATE_LIMIT_PER_SECOND"), 10)
    )
    FRED_RATE_LIMIT_PER_MINUTE: int = max(
        0, _safe_int(os.getenv("FRED_RATE_LIMIT_PER_MINUTE"), 120)
    )
    FRED_RATE_LIMIT_DEFAULT_RETRY_SECONDS: int = max(
        1, _safe_int(os.getenv("FRED_RATE_LIMIT_DEFAULT_RETRY_SECONDS"), 5)
    )

    # Metrics configuration
    METRICS_ENABLED: bool = _str_to_bool(os.getenv("METRICS_ENABLED"), default=True)
    METRICS_EXPORT_FORMAT: str = os.getenv("METRICS_EXPORT_FORMAT", "json")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration values."""
        if not cls.FRED_API_KEY:
            raise ValueError(
                "FRED_API_KEY environment variable is required. "
                "Please set it in your .env file."
            )

    @classmethod
    def get_fred_api_key(cls) -> str:
        """Get FRED API key with validation."""
        if not cls.FRED_API_KEY:
            raise ValueError("FRED_API_KEY not configured")
        return cls.FRED_API_KEY

    @classmethod
    def get_cache_ttl(cls, namespace: str, fallback: Optional[int] = None) -> Optional[int]:
        """Resolve TTL for a cache namespace with environment overrides."""

        if not cls.CACHE_ENABLED:
            return None

        normalized = namespace.strip().lower()
        env_key = f"CACHE_TTL_{normalized.upper()}"
        env_value = os.getenv(env_key)

        if env_value is not None:
            try:
                ttl = int(env_value)
            except ValueError:
                raise ValueError(
                    f"Invalid TTL value '{env_value}' for environment variable {env_key}"
                ) from None
            return ttl if ttl > 0 else None

        if fallback is not None:
            return fallback if fallback > 0 else None

        default = cls.CACHE_NAMESPACE_DEFAULTS.get(normalized, cls.CACHE_DEFAULT_TTL_SECONDS)
        if default is None or default <= 0:
            return None
        return default

    @classmethod
    def get_rate_limits(cls) -> Tuple[Optional[int], Optional[int]]:
        """Return the configured per-second and per-minute FRED request limits."""

        if not cls.FRED_RATE_LIMIT_ENABLED:
            return None, None

        per_second = cls.FRED_RATE_LIMIT_PER_SECOND or None
        per_minute = cls.FRED_RATE_LIMIT_PER_MINUTE or None
        return per_second, per_minute

    @classmethod
    def get_rate_limit_penalty(cls, fallback: Optional[float] = None) -> float:
        """Return the default backoff seconds when FRED rate limits are triggered."""

        if fallback is not None and fallback > 0:
            return fallback
        return float(max(1, cls.FRED_RATE_LIMIT_DEFAULT_RETRY_SECONDS))


# Singleton instance
config = Config()
