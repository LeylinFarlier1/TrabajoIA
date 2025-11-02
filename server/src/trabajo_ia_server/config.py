"""
Configuration module for Trabajo IA Server.

Manages environment variables and server configuration.
"""
import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


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
    SERVER_VERSION: str = "0.1.9-alpha"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Cache configuration
    CACHE_ENABLED: bool = _str_to_bool(os.getenv("CACHE_ENABLED"), default=True)
    CACHE_BACKEND: str = os.getenv("CACHE_BACKEND", "memory")
    CACHE_DEFAULT_TTL_SECONDS: int = max(0, _safe_int(os.getenv("CACHE_DEFAULT_TTL_SECONDS"), 300))
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


# Singleton instance
config = Config()
