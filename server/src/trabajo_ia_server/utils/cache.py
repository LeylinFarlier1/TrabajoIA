"""Caching utilities for Trabajo IA server.

Provides a namespaced cache manager with pluggable backends and
lightweight in-memory storage. Designed to support TTL-based caching for
FRED API responses and other expensive operations.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, MutableMapping, Optional, Tuple

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class CacheEntry:
    """Container for cached values and their expiration metadata."""

    value: Any
    expires_at: Optional[float]


class CacheBackend:
    """Base cache backend interface."""

    enabled: bool = True
    default_ttl: Optional[int] = None

    def get(self, key: str, default: Any = None) -> Any:  # pragma: no cover - interface
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:  # pragma: no cover
        raise NotImplementedError

    def delete(self, key: str) -> None:  # pragma: no cover
        raise NotImplementedError

    def clear(self, prefix: Optional[str] = None) -> None:  # pragma: no cover
        raise NotImplementedError


class NullCache(CacheBackend):
    """Disabled cache backend used when caching is turned off."""

    enabled = False

    def get(self, key: str, default: Any = None) -> Any:
        return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        return None

    def delete(self, key: str) -> None:
        return None

    def clear(self, prefix: Optional[str] = None) -> None:
        return None


class InMemoryCache(CacheBackend):
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self, default_ttl: Optional[int] = None) -> None:
        self.default_ttl = default_ttl
        self._store: MutableMapping[str, CacheEntry] = {}
        self._lock = threading.RLock()

    def _now(self) -> float:
        return time.monotonic()

    def _is_expired(self, entry: CacheEntry) -> bool:
        return entry.expires_at is not None and entry.expires_at <= self._now()

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return default
            if self._is_expired(entry):
                self._store.pop(key, None)
                return default
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        effective_ttl = self.default_ttl if ttl is None else ttl
        if effective_ttl is not None and effective_ttl <= 0:
            return
        expires_at = None
        if effective_ttl is not None:
            expires_at = self._now() + effective_ttl
        with self._lock:
            self._store[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self, prefix: Optional[str] = None) -> None:
        with self._lock:
            if prefix is None:
                self._store.clear()
                return
            keys_to_delete = [key for key in self._store if key.startswith(prefix)]
            for key in keys_to_delete:
                self._store.pop(key, None)


class CacheManager:
    """High level cache manager with namespace isolation and metrics."""

    _MISSING = object()

    def __init__(
        self,
        *,
        backend: Optional[CacheBackend] = None,
        enabled: bool = True,
        default_ttl: Optional[int] = None,
    ) -> None:
        if backend is None:
            backend = InMemoryCache(default_ttl=default_ttl)
        self.backend = backend
        self.enabled = enabled and backend.enabled
        self.default_ttl = default_ttl if default_ttl is not None else backend.default_ttl
        self._namespace_ttls: Dict[str, Optional[int]] = {}
        self._metrics: Dict[str, Dict[str, int]] = {}
        self._lock = threading.RLock()

    def configure_namespace(self, namespace: str, ttl: Optional[int]) -> None:
        normalized = namespace.strip().lower()
        with self._lock:
            self._namespace_ttls[normalized] = ttl

    def _namespaced_key(self, namespace: str, key: str) -> str:
        normalized = namespace.strip().lower()
        return f"{normalized}:{key}"

    def _effective_ttl(self, namespace: str, ttl_override: Optional[int]) -> Optional[int]:
        if not self.enabled:
            return None
        if ttl_override is not None:
            return ttl_override if ttl_override > 0 else None
        normalized = namespace.strip().lower()
        with self._lock:
            ttl = self._namespace_ttls.get(normalized, self.default_ttl)
        if ttl is None or ttl <= 0:
            return None
        return ttl

    def _update_metrics(self, namespace: str, *, hit: Optional[bool] = None, stored: bool = False) -> None:
        normalized = namespace.strip().lower()
        with self._lock:
            metrics = self._metrics.setdefault(normalized, {"hits": 0, "misses": 0, "stores": 0})
            if hit is True:
                metrics["hits"] += 1
            elif hit is False:
                metrics["misses"] += 1
            if stored:
                metrics["stores"] += 1

    def get(self, namespace: str, key: str) -> Tuple[Any, bool]:
        if not self.enabled:
            return None, False
        namespaced_key = self._namespaced_key(namespace, key)
        value = self.backend.get(namespaced_key, self._MISSING)
        hit = value is not self._MISSING
        self._update_metrics(namespace, hit=hit)
        if hit:
            return value, True
        return None, False

    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        if not self.enabled:
            return False
        effective_ttl = self._effective_ttl(namespace, ttl)
        if effective_ttl is None:
            logger.debug("Cache disabled for namespace '%s'", namespace)
            return False
        namespaced_key = self._namespaced_key(namespace, key)
        self.backend.set(namespaced_key, value, effective_ttl)
        self._update_metrics(namespace, stored=True)
        return True

    def delete(self, namespace: str, key: str) -> None:
        namespaced_key = self._namespaced_key(namespace, key)
        self.backend.delete(namespaced_key)

    def invalidate_namespace(self, namespace: str) -> None:
        normalized = namespace.strip().lower()
        prefix = f"{normalized}:"
        self.backend.clear(prefix)

    def get_metrics(self) -> Dict[str, Dict[str, int]]:
        with self._lock:
            return {namespace: metrics.copy() for namespace, metrics in self._metrics.items()}


def _build_cache_manager() -> CacheManager:
    """Factory that creates the global cache manager using configuration."""

    default_ttl = config.CACHE_DEFAULT_TTL_SECONDS
    backend: CacheBackend
    if not config.CACHE_ENABLED or config.CACHE_BACKEND.lower() not in {"memory", "inmemory"}:
        backend = NullCache()
    else:
        ttl_value = default_ttl if default_ttl > 0 else None
        backend = InMemoryCache(default_ttl=ttl_value)

    manager = CacheManager(backend=backend, enabled=config.CACHE_ENABLED, default_ttl=default_ttl)

    for namespace, fallback in config.CACHE_NAMESPACE_DEFAULTS.items():
        ttl = config.get_cache_ttl(namespace, fallback=fallback)
        manager.configure_namespace(namespace, ttl)

    if manager.enabled:
        logger.info("Cache manager initialized with %d namespaces", len(config.CACHE_NAMESPACE_DEFAULTS))
    else:
        logger.info("Cache manager initialized in disabled mode")

    return manager


cache_manager = _build_cache_manager()

__all__ = [
    "CacheEntry",
    "CacheBackend",
    "InMemoryCache",
    "NullCache",
    "CacheManager",
    "cache_manager",
]

