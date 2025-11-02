from trabajo_ia_server.utils.metrics import MetricsRegistry


def test_metrics_registry_tracks_counters_and_histograms():
    registry = MetricsRegistry(enabled=True)

    registry.increment("requests_total", labels={"status": "200"})
    registry.increment("requests_total", labels={"status": "200"}, amount=2)
    registry.increment("requests_total", labels={"status": "500"})

    registry.set_gauge("inflight_requests", 3, labels={"queue": "fred"})
    registry.observe("latency_seconds", 0.5, labels={"tool": "search"})
    registry.observe("latency_seconds", 1.0, labels={"tool": "search"})

    snapshot = registry.export()

    assert snapshot["counters"]["requests_total"]["(('status', '200'),)"] == 3.0
    assert snapshot["counters"]["requests_total"]["(('status', '500'),)"] == 1.0
    assert snapshot["gauges"]["inflight_requests"]["(('queue', 'fred'),)"] == 3.0

    latency = snapshot["histograms"]["latency_seconds"]["(('tool', 'search'),)"]
    assert latency["count"] == 2.0
    assert latency["min"] == 0.5
    assert latency["max"] == 1.0
    assert latency["avg"] == 0.75

    registry.reset()
    cleared = registry.export()
    assert cleared["counters"] == {}
