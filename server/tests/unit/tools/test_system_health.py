import json

from trabajo_ia_server.tools.system.health import system_health
from trabajo_ia_server.utils.cache import cache_manager
from trabajo_ia_server.utils.metrics import metrics


def test_system_health_payload_contains_core_sections():
    metrics.reset()
    cache_manager.configure_namespace("health_test", 60)

    output = system_health()
    payload = json.loads(output)

    assert payload["status"] == "ok"
    assert "timestamp" in payload
    assert "version" in payload

    cache_section = payload["cache"]
    assert cache_section["enabled"] in {True, False}
    assert "namespaces" in cache_section

    rate_section = payload["rate_limiter"]
    assert "enabled" in rate_section

    metrics_section = payload["metrics"]
    assert metrics_section["enabled"] in {True, False}

    if metrics_section["enabled"]:
        assert "counters" in metrics_section
        assert "names" in metrics_section
