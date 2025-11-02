"""Unit tests for cache manager and in-memory backend."""

import time

from trabajo_ia_server.utils.cache import CacheManager, InMemoryCache


def test_cache_manager_records_hits_and_metrics():
    backend = InMemoryCache(default_ttl=60)
    manager = CacheManager(backend=backend, enabled=True, default_ttl=60)
    manager.configure_namespace("search", 30)

    value, hit = manager.get("search", "key")
    assert not hit
    assert value is None

    stored = manager.set("search", "key", "value")
    assert stored is True

    value, hit = manager.get("search", "key")
    assert hit is True
    assert value == "value"

    metrics = manager.get_metrics()["search"]
    assert metrics["hits"] == 1
    assert metrics["misses"] == 1
    assert metrics["stores"] == 1


def test_cache_manager_ttl_expiration():
    backend = InMemoryCache(default_ttl=1)
    manager = CacheManager(backend=backend, enabled=True, default_ttl=1)
    manager.configure_namespace("short", 1)

    manager.set("short", "temp", "value", ttl=1)
    value, hit = manager.get("short", "temp")
    assert hit is True
    assert value == "value"

    time.sleep(1.1)

    value, hit = manager.get("short", "temp")
    assert hit is False
    assert value is None


def test_cache_manager_disabled_namespace():
    backend = InMemoryCache(default_ttl=10)
    manager = CacheManager(backend=backend, enabled=True, default_ttl=10)
    manager.configure_namespace("disabled", 0)

    stored = manager.set("disabled", "key", "value")
    assert stored is False

    value, hit = manager.get("disabled", "key")
    assert hit is False
    assert value is None
