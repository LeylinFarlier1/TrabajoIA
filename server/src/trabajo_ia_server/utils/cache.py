"""Caching utilities for Trabajo IA server.

Provides a namespaced cache manager with pluggable backends and
lightweight in-memory storage. Designed to support TTL-based caching for
FRED API responses and other expensive operations.
"""

from __future__ import annotations

import pickle
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional, Tuple

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.logger import setup_logger
from trabajo_ia_server.utils.metrics import metrics

logger = setup_logger(__name__)

try:  # pragma: no cover - optional dependency
    import diskcache  # type: ignore
except ImportError:  # pragma: no cover - optional dependency not installed
    diskcache = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import redis  # type: ignore
except ImportError:  # pragma: no cover - optional dependency not installed
    redis = None  # type: ignore


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


class DiskCacheBackend(CacheBackend):
    """Persistent on-disk cache backend using diskcache."""

    def __init__(self, directory: str, default_ttl: Optional[int] = None) -> None:
        if diskcache is None:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "diskcache backend requested but the 'diskcache' package is not installed"
            )

        self.default_ttl = default_ttl
        cache_dir = Path(directory)
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache = diskcache.Cache(str(cache_dir))

    def get(self, key: str, default: Any = None) -> Any:
        return self._cache.get(key, default)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expire = ttl if ttl is not None and ttl > 0 else None
        self._cache.set(key, value, expire=expire)

    def delete(self, key: str) -> None:
        self._cache.delete(key)

    def clear(self, prefix: Optional[str] = None) -> None:
        if prefix is None:
            self._cache.clear()
            return
        for key in list(self._cache.iterkeys(prefix=prefix)):
            self._cache.delete(key)


class RedisCacheBackend(CacheBackend):
    """Redis-backed cache suitable for multi-instance deployments."""

    def __init__(
        self,
        *,
        url: str,
        prefix: str,
        default_ttl: Optional[int] = None,
    ) -> None:
        if redis is None:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "redis backend requested but the 'redis' package is not installed"
            )

        self.default_ttl = default_ttl
        self._client = redis.Redis.from_url(url)  # type: ignore[attr-defined]
        self._prefix = prefix.rstrip(":")

    def _namespaced(self, key: str) -> str:
        if self._prefix:
            return f"{self._prefix}:{key}"
        return key

    def get(self, key: str, default: Any = None) -> Any:
        namespaced = self._namespaced(key)
        value = self._client.get(namespaced)
        if value is None:
            return default
        try:
            return pickle.loads(value)
        except Exception:  # pragma: no cover - corrupted payload fallback
            logger.warning("Failed to deserialize redis cache entry for %s", namespaced)
            self._client.delete(namespaced)
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        namespaced = self._namespaced(key)
        payload = pickle.dumps(value)
        if ttl is not None and ttl > 0:
            self._client.set(namespaced, payload, ex=ttl)
        else:
            self._client.set(namespaced, payload)

    def delete(self, key: str) -> None:
        self._client.delete(self._namespaced(key))

    def clear(self, prefix: Optional[str] = None) -> None:
        if prefix is None:
            for key in self._client.scan_iter(f"{self._prefix}:*"):
                self._client.delete(key)
            return
        full_prefix = f"{self._prefix}:{prefix}" if self._prefix else prefix
        for key in self._client.scan_iter(f"{full_prefix}*"):
            self._client.delete(key)


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
            namespace_metrics = self._metrics.setdefault(
                normalized, {"hits": 0, "misses": 0, "stores": 0}
            )
            if hit is True:
                namespace_metrics["hits"] += 1
            elif hit is False:
                namespace_metrics["misses"] += 1
            if stored:
                namespace_metrics["stores"] += 1

        if hit is True:
            metrics.increment("cache_hits_total", labels={"namespace": normalized})
        elif hit is False:
            metrics.increment("cache_misses_total", labels={"namespace": normalized})
        if stored:
            metrics.increment("cache_stores_total", labels={"namespace": normalized})

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
        metrics.increment("cache_invalidations_total", labels={"namespace": normalized})

    def get_metrics(self) -> Dict[str, Dict[str, int]]:
        with self._lock:
            return {namespace: metrics.copy() for namespace, metrics in self._metrics.items()}

    def describe(self) -> Dict[str, Any]:
        """Return a snapshot of cache configuration and runtime metrics."""

        with self._lock:
            namespaces = {
                namespace: {
                    "ttl": ttl,
                    "metrics": self._metrics.get(namespace, {}).copy(),
                }
                for namespace, ttl in self._namespace_ttls.items()
            }

        return {
            "enabled": self.enabled,
            "backend": type(self.backend).__name__,
            "default_ttl": self.default_ttl,
            "namespaces": namespaces,
        }


def _build_cache_manager() -> CacheManager:
    """Factory that creates the global cache manager using configuration."""

    default_ttl = config.CACHE_DEFAULT_TTL_SECONDS
    backend: CacheBackend
    backend_name = (config.CACHE_BACKEND or "").strip().lower()
    ttl_value = default_ttl if default_ttl > 0 else None

    backend: CacheBackend
    if not config.CACHE_ENABLED:
        backend = NullCache()
    elif backend_name in {"memory", "inmemory", "local"}:
        backend = InMemoryCache(default_ttl=ttl_value)
    elif backend_name == "diskcache":
        if diskcache is None:
            logger.warning(
                "diskcache backend requested but package not installed; falling back to in-memory"
            )
            backend = InMemoryCache(default_ttl=ttl_value)
        else:
            backend = DiskCacheBackend(
                config.CACHE_DISKCACHE_DIRECTORY, default_ttl=ttl_value
            )
    elif backend_name == "redis":
        if redis is None:
            logger.warning(
                "redis backend requested but package not installed; caching disabled"
            )
            backend = NullCache()
        else:
            backend = RedisCacheBackend(
                url=config.CACHE_REDIS_URL,
                prefix=config.CACHE_REDIS_PREFIX,
                default_ttl=ttl_value,
            )
    else:
        logger.warning("Unknown cache backend '%s'; caching disabled", backend_name)
        backend = NullCache()

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
    "DiskCacheBackend",
    "RedisCacheBackend",
    "NullCache",
    "CacheManager",
    "cache_manager",
]

