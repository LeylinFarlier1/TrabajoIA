# Release Notes - Trabajo IA MCP Server v0.1.9

**Release Date:** 2025-11-02
**Type:** Performance & Observability Upgrade
**Focus:** Cache acceleration, coordinated rate limiting, and operational telemetry

---

## Overview

Version 0.1.9 delivers the infrastructure needed to keep FRED workloads fast and reliable as usage scales. A unified caching
layer reduces redundant API traffic, a coordinated rate limiter keeps the server inside FRED's global budget, and brand-new
telemetry surfaces real-time insights into latency, retries, and capacity. Together with the new `system_health` MCP tool, these
features let operators monitor deployments and react before downstream clients notice problems.

The release also standardizes HTTP handling by routing every tool through a shared `FredClient`. That consolidation ensures
consistent headers, retries, and cache lookups across the suite of FRED tools while simplifying future enhancements such as
async execution.

### Key Achievement

**Cache + Telemetry Foundation:** Trabajo IA Server now ships with a production-ready caching layer, rate limiter, and metrics
registry that keep popular workflows under 400 ms while exposing actionable observability for operators and automation systems.

---

## What's New

### 1. Unified Cache Infrastructure

A configurable cache manager wraps every outbound FRED request, providing both in-memory and persistent backends with minimal
configuration.

**Core Functionality:**
```python
from trabajo_ia_server.utils.cache import CacheManager

cache = CacheManager.from_settings(
    backend="redis",  # or "memory" / "diskcache"
    ttl_overrides={
        "fred:search": 300,   # warm frequently searched keywords for 5 minutes
        "fred:metadata": 3600 # keep static metadata around for an hour
    },
)
```

**Highlights:**
- Namespace-specific TTLs keep hot searches responsive without serving stale data for longer-lived metadata.
- Transparent serialization handles pandas and JSON payloads so tool authors operate on native Python objects.
- Cache-hit metadata is surfaced to callers, allowing observability dashboards to track reuse percentages by workflow.

### 2. Coordinated Rate Limiter

A global rate limiter protects the shared FRED API quota by coordinating penalties and retry windows across all tools.

**Core Functionality:**
```python
from trabajo_ia_server.utils.rate_limiter import RateLimiter

limiter = RateLimiter(max_requests_per_minute=120)
with limiter.claim("fred:search") as ticket:
    response = fred_client.get("/fred/series/search", params)
    ticket.observe(response.status_code)
```

**Highlights:**
- Adaptive backoff applies exponential penalties when the API responds with HTTP 429 or gateway timeouts.
- Namespace tagging lets you track which workflows are consuming the quota.
- Rate limiter state is exported through the `system_health` tool alongside cache statistics.

### 3. Structured Logging & Metrics

The logging subsystem now supports JSON output with contextual request IDs, and an in-process metrics registry provides
Prometheus-ready counters and histograms.

**Core Functionality:**
```python
from trabajo_ia_server.utils.logger import get_logger
from trabajo_ia_server.utils.metrics import metrics

logger = get_logger(__name__, json=True)
logger.info("search", extra={"request_id": "req-123", "namespace": "fred:search"})

latency_histogram = metrics.histogram("fred_client_latency_ms", buckets=[50, 100, 250, 500, 1000])
with latency_histogram.time():
    fred_client.get_series("UNRATE")
```

**Highlights:**
- JSON mode is activated via `LOG_FORMAT=json`, enabling seamless ingestion into ELK, CloudWatch, or other aggregators.
- Built-in metrics include cache hits/misses, retry counts, rate limiter penalties, and tool execution times.
- Telemetry snapshots are compiled by `system_health`, offering a single MCP call to diagnose latency spikes or quota pressure.

### 4. New Tool: `system_health`

A dedicated MCP tool reports deployment status so that automation hooks and dashboards can verify readiness without custom code.

**Invocation:**
```python
from trabajo_ia_server.tools.system.health import system_health

result = system_health()
print(result)
```

**Response Format:**
```json
{
  "tool": "system_health",
  "data": {
    "cache": {
      "backend": "redis",
      "hit_rate": 0.82,
      "namespaces": {
        "fred:search": {"ttl": 300, "hits": 1842, "misses": 402},
        "fred:metadata": {"ttl": 3600, "hits": 120, "misses": 12}
      }
    },
    "rate_limiter": {
      "window_seconds": 60,
      "max_requests": 120,
      "active_penalty_ms": 0,
      "last_http_429": null
    },
    "metrics": {
      "fred_client": {
        "latency_ms_p50": 210,
        "latency_ms_p95": 420,
        "retry_rate": 0.04
      }
    }
  }
}
```

**Highlights:**
- Offers a quick readiness probe for CI/CD pipelines before exposing the server to traffic.
- Bundles cache, limiter, and metrics insights in one place to accelerate incident response.
- Designed for extensibility—future telemetry sources can plug into the health snapshot without breaking clients.

---

## Use Cases

### 1. Lightning-Fast Prompt Chains

**Scenario:** An LLM-powered assistant executes multiple `search_fred_series` calls in sequence while building dashboards.

**Solution:** The shared cache and rate limiter prevent repeated API calls from hitting FRED, while retries are coordinated behind
the scenes.

**Benefits:**
- Keeps average latency under 400 ms for warmed queries.
- Eliminates "thundering herd" effects when multiple prompts explore similar economic indicators.

### 2. Operations Monitoring & Alerting

**Scenario:** Platform engineers need to confirm the MCP server is healthy before rolling out a new workspace configuration.

**Solution:** Automate a `system_health` call that checks cache availability, limiter penalties, and telemetry freshness.

**Benefits:**
- Detects missing Redis connections or stale metrics instantly.
- Enables alert thresholds on retry rates or cache hit ratios.

### 3. Rate Limit Budgeting

**Scenario:** Analysts schedule nightly bulk exports of FRED data.

**Solution:** Tag limiter claims per workflow and observe the penalty counters via metrics dashboards.

**Benefits:**
- Prevents bulk jobs from starving interactive users.
- Supplies historical data for refining quotas and schedules.

---

## Parameters & Configuration Highlights

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CACHE_BACKEND` | `memory` | Selects cache backend (`memory`, `diskcache`, `redis`). |
| `CACHE_REDIS_URL` | `redis://localhost:6379/0` | Redis connection string when backend is redis. |
| `CACHE_DEFAULT_TTL` | `300` | Default TTL (seconds) applied when a namespace override is absent. |
| `RATE_LIMIT_MAX_REQUESTS` | `120` | Allowed requests per rolling window. |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Duration of limiter window in seconds. |
| `LOG_FORMAT` | `plain` | Set to `json` for structured logging. |
| `LOG_JSON_INDENT` | `null` | Optional indentation for human-readable JSON logs. |

### Configuration APIs

```python
from trabajo_ia_server.utils.cache import CacheManager
from trabajo_ia_server.utils.metrics import metrics
from trabajo_ia_server.utils.rate_limiter import RateLimiter

cache = CacheManager.from_env()
limiter = RateLimiter.from_env()
metrics.reset()  # clears counters/histograms during tests
```

---

## Performance

- **Warm `search_fred_series` Latency:** ~0.35–0.40 s (p50) with cache hits enabled.
- **Cold `search_fred_series` Latency:** ~0.55 s (p50) while awaiting upstream API responses.
- **Retry Rate:** <5% under nominal conditions thanks to coordinated backoff.
- **Cache Hit Ratio:** 70–90% for repeated analytic prompts depending on TTL configuration.

---

## Examples

### Example 1: Cached Search Flow

```python
from trabajo_ia_server.tools.fred.search_series import search_fred_series

first = search_fred_series("inflation expectations", limit=10)
second = search_fred_series("inflation expectations", limit=10)
```

**Outcome:** The second call is served from cache, returning in ~0.35 s and including metadata indicating the hit.

### Example 2: Observing Rate Limiter Penalties

```python
from trabajo_ia_server.utils.rate_limiter import RateLimiter

limiter = RateLimiter.from_env()
with limiter.claim("batch:export") as ticket:
    response = fred_client.get("/fred/series/observations", params)
    ticket.observe(response.status_code)

penalties = limiter.snapshot().penalties
```

**Outcome:** `penalties` reports active cooldowns if FRED signaled throttling, allowing scheduling systems to pause or slow
throughput.

### Example 3: Health Probe

```python
from trabajo_ia_server.tools.system.health import system_health

health = system_health()
print(health["data"]["cache"]["backend"])  # -> "memory"
```

**Outcome:** Provides immediate verification that the server is wired to the intended cache backend before production rollouts.

---

## Breaking Changes

- **None.** Existing tool signatures remain unchanged; enhancements are additive and fully backward compatible.

---

## Compatibility

### Backwards Compatibility

- Tools continue to return the same payload shape, with additional `metadata.cache` details appended for observability.
- JSON logging is opt-in; deployments not enabling `LOG_FORMAT=json` retain previous plaintext output.

### Dependencies

- `python-dotenv` remains optional; a built-in parser now loads `.env` files when the dependency is absent.
- Optional cache backends (`diskcache`, `redis`) are detected dynamically—install the packages only when needed.

---

## Installation & Upgrade

### New Installation

```bash
cd server
uv sync
cp config/.env.example .env
```

### Upgrade from v0.1.8

```bash
cd server
uv sync  # picks up new optional extras for diskcache/redis
cp config/.env.example .env  # review new CACHE_* and RATE_LIMIT_* settings
```

### Verify Installation

```python
from trabajo_ia_server import __version__
print(__version__)  # Should print: 0.1.9
```

---

## Verification & Testing Checklist

1. **Run Unit Tests**
   ```bash
   PYTHONPATH=server/src pytest --override-ini addopts="" \
     server/tests/unit/utils/test_cache.py \
     server/tests/unit/utils/test_rate_limiter.py \
     server/tests/unit/utils/test_metrics.py \
     server/tests/unit/utils/test_fred_client.py \
     server/tests/unit/tools/test_fred_search.py \
     server/tests/unit/tools/test_system_health.py
   ```
2. **Smoke Test `system_health`** from your MCP client and confirm cache + limiter data is present.
3. **Check Logs** with `LOG_FORMAT=json` to ensure request IDs appear as expected.
4. **Validate Cache Backend** by toggling between in-memory and Redis backends and observing hit rates.

---

## Known Issues

- Redis connectivity problems manifest as cache misses; telemetry in `system_health` now highlights backend availability, but
  deployments should still monitor Redis directly.
- Long-tail FRED endpoints may exceed default timeout windows; configure namespace-specific TTLs and retry budgets if necessary.

---

## Future Enhancements

Planned for v0.2.0 and beyond:

- **Async HTTP Pipeline:** Adopt `httpx.AsyncClient` with shared connection pools for lower tail latency.
- **Batch Operations Tool:** Execute multiple series fetches in a single MCP call to amortize round-trips.
- **Distributed Metrics Export:** Expose `/metrics` endpoint or StatsD integration for fleet-wide dashboards.
- **Circuit Breaker Support:** Automatically short-circuit repeated upstream failures while surfacing alerts to operators.

---

## Appendix: Files Updated in v0.1.9

- `src/trabajo_ia_server/utils/cache.py`
- `src/trabajo_ia_server/utils/fred_client.py`
- `src/trabajo_ia_server/utils/rate_limiter.py`
- `src/trabajo_ia_server/utils/logger.py`
- `src/trabajo_ia_server/utils/metrics.py`
- `src/trabajo_ia_server/tools/system/health.py`
- `src/trabajo_ia_server/config.py`
- `src/trabajo_ia_server/__init__.py`
- `pyproject.toml`
- `docs/Release_notes/RELEASE_NOTES_v0.1.9.md`

