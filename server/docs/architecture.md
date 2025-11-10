# Trabajo IA MCP Server - Architecture

## Overview

This document describes the architecture and design decisions for the Trabajo IA MCP Server, a clean, modular implementation of a Model Context Protocol server for FRED economic data.

## Architecture Principles

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- `server.py` - MCP protocol handling and tool registration
- `config.py` - Configuration management
- `tools/` - Tool implementations
- `utils/` - Shared utilities
- `models/` - Data structures

### 2. **Dependency Injection**
Configuration is centralized and injected where needed, avoiding global state pollution.

### 3. **Type Safety**
Full type hints throughout the codebase for better IDE support and early error detection.

### 4. **Error Handling**
Comprehensive error handling with proper logging and user-friendly error messages.

## Directory Structure

```
server/
├── src/                           # Source code (src-layout)
│   ├── __main__.py               # Entry point for -m flag
│   └── trabajo_ia_server/        # Main package
│       ├── __init__.py           # Package exports
│       ├── server.py             # MCP server implementation
│       ├── config.py             # Configuration singleton
│       │
│       ├── tools/                # Tool implementations (12 MCP tools)
│       │   ├── fred/             # FRED-specific tools (11 tools)
│       │   │   ├── search_series.py              # Search with filters
│       │   │   ├── observations.py               # Historical data
│       │   │   ├── get_tags.py                   # Tag discovery
│       │   │   ├── related_tags.py               # Related tags
│       │   │   ├── series_by_tags.py             # Tag-based search
│       │   │   ├── search_series_tags.py         # Series search tags
│       │   │   ├── search_series_related_tags.py # Related tags in searches
│       │   │   ├── get_series_tags.py            # Series-specific tags
│       │   │   ├── category.py                   # Category info
│       │   │   ├── category_children.py          # Sub-categories
│       │   │   ├── category_series.py            # Category series
│       │   │   └── __init__.py
│       │   │
│       │   ├── system/           # Internal utilities (not exposed as MCP tools)
│       │   │   ├── health.py     # Internal health diagnostics
│       │   │   └── __init__.py
│       │   │
│       │   └── workflows/        # Workflow registration (1 tool)
│       │       └── __init__.py   # Workflows registered in server.py
│       │
│       ├── workflows/            # Complex analysis workflows
│       │   ├── analyze_gdp.py    # Main GDP analysis orchestrator
│       │   │
│       │   ├── layers/           # 3-layer architecture
│       │   │   ├── fetch_data.py      # Layer 1: FRED data retrieval
│       │   │   ├── analyze_data.py    # Layer 2: Economic analysis
│       │   │   └── format_output.py   # Layer 3: Output formatting
│       │   │
│       │   └── utils/            # Workflow utilities
│       │       ├── gdp_mappings.py    # 238 country series IDs
│       │       └── gdp_validators.py  # Input validation & presets
│       │
│       ├── models/               # Data models (future expansion)
│       │   └── __init__.py
│       │
│       └── utils/                # Shared utilities
│           ├── cache.py          # Multi-backend caching (Memory/Disk/Redis)
│           ├── rate_limiter.py   # Token bucket rate limiting
│           ├── metrics.py        # Prometheus-style telemetry
│           ├── logger.py         # Structured JSON logging
│           ├── validators.py     # Input validation helpers
│           ├── fred_client.py    # Unified FRED API client
│           └── __init__.py
│
├── tests/                        # Test suite (pytest)
│   ├── unit/                     # Unit tests
│   │   ├── tools/                # Tool tests
│   │   ├── workflows/            # Workflow tests
│   │   └── utils/                # Utility tests
│   ├── integration/              # Integration tests
│   │   └── test_fred_api.py      # Live FRED API tests
│   └── fixtures/                 # Test data
│       └── mock_responses/       # Mock API responses
│
├── config/                       # Configuration templates
│   └── .env.example              # Environment variable template
│
├── docs/                         # Documentation
│   ├── README.md                 # Documentation index (this lives here)
│   ├── architecture.md           # Architecture guide (this file)
│   │
│   ├── api/                      # FRED API reference docs (11 files)
│   │   ├── search_series.md
│   │   ├── observations.md
│   │   ├── tags.md
│   │   └── ...
│   │
│   ├── workflows/                # Workflow documentation
│   │   └── ANALYZE_GDP_CROSS_COUNTRY_REFERENCE.md
│   │
│   ├── guides/                   # Development guides
│   │   ├── VERSION_UPDATE_GUIDE.md
│   │   ├── MCP_PROJECT_TESTING_GUIDE.md
│   │   └── IMPLEMENTACION_NUEVA_TOOL_GUIA.md
│   │
│   ├── Release_notes/            # Version releases
│   │   └── RELEASE_NOTES_v0.1.9.md
│   │
│   ├── Changelog/                # Change history
│   │   └── CHANGELOG.md
│   │
│   └── planning/                 # Future planning docs
│       └── v0.2.0_expansion_plan.md
│
├── .env                          # Environment variables (gitignored)
├── pyproject.toml                # Project metadata + dependencies
├── uv.lock                       # Dependency lock file
└── README.md                     # Main documentation
```

## Module Responsibilities

### `server.py` - MCP Server
**Purpose**: FastMCP server initialization and tool registration

**Responsibilities**:
- Initialize FastMCP instance
- Register MCP tools with decorators
- Validate configuration on startup
- Handle server lifecycle (start, stop, errors)
- Provide main entry point

**Dependencies**:
- `mcp.server.fastmcp.FastMCP`
- `trabajo_ia_server.config`
- `trabajo_ia_server.tools.*`

### `config.py` - Configuration Management
**Purpose**: Centralized configuration with validation

**Responsibilities**:
- Load environment variables from `.env`
- Provide typed access to config values
- Validate required configuration on access
- Expose configuration singleton

**Pattern**: Singleton class with class methods

**Environment Variables**:
- `FRED_API_KEY` (required) - FRED API authentication
- `LOG_LEVEL` (optional) - Logging verbosity (default: INFO)

### `tools/fred/fetch_series.py` - FRED Data Tool
**Purpose**: Fetch time-series data from FRED API

**Responsibilities**:
- Validate input parameters (series ID, dates)
- Call FRED API via `fredapi` library
- Process data with pandas
- Format response as JSON
- Handle and log errors

**Input Validation**:
- Series ID format check
- Date format validation (YYYY-MM-DD)
- API key presence

**Output Format**:
```json
{
  "tool": "fetch_series_observations",
  "series_id": "GDP",
  "data": [
    {"date": "2020-01-01T00:00:00", "value": 21734.843},
    ...
  ],
  "metadata": {
    "fetch_date": "2024-11-01T...",
    "observation_start": "2020-01-01",
    "observation_end": "latest",
    "total_count": 16,
    "date_range": {
      "start": "2020-01-01T00:00:00",
      "end": "2023-10-01T00:00:00"
    }
  }
}
```

### `utils/logger.py` - Logging Utilities
**Purpose**: Centralized logging configuration

**Responsibilities**:
- Create configured logger instances
- Standardize log format across application
- Support different log levels
- Output to stdout for MCP compatibility

**Usage**:
```python
from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Message")
```

### `utils/validators.py` - Input Validators
**Purpose**: Validate user inputs before processing

**Responsibilities**:
- Validate date format (YYYY-MM-DD)
- Validate FRED series ID format
- Provide reusable validation functions

**Functions**:
- `validate_date_format(date_str) -> bool`
- `validate_series_id(series_id) -> bool`

### `utils/cache.py` - Multi-Backend Caching
**Purpose**: Intelligent caching system for FRED API responses

**Architecture**: Strategy pattern with pluggable backends

**Supported Backends**:
1. **MemoryCache** (default)
   - In-memory dictionary storage
   - Fast access (<1ms)
   - Configurable TTL (default: 300s)
   - Best for: Development, single-process deployments

2. **DiskCache**
   - Persistent file-based storage
   - Survives restarts
   - Automatic cleanup
   - Best for: Local development, persistent cache

3. **RedisCache**
   - Distributed caching
   - Shared across processes
   - Production-ready
   - Best for: Multi-instance deployments

**Key Methods**:
```python
cache.get(key: str) -> Optional[Any]
cache.set(key: str, value: Any, ttl: Optional[int] = None)
cache.delete(key: str)
cache.clear()
cache.stats() -> dict  # Hit rate, size, etc.
```

**Usage**:
```python
from trabajo_ia_server.utils.cache import cache

# Automatic cache key generation from function args
@cache.memoize(ttl=300)
def fetch_series(series_id: str, start_date: str):
    return fred_api.get_series(series_id, start_date)
```

**Performance Impact**:
- Cache hit: <400ms response time
- Cache miss: 1500-3000ms (FRED API call)
- 70-90% cache hit rate typical

### `utils/rate_limiter.py` - Token Bucket Rate Limiting
**Purpose**: Enforce FRED API rate limits (120 requests/minute)

**Algorithm**: Token Bucket
- Tokens replenish at fixed rate (120/min = 2/sec)
- Burst capacity: 120 tokens
- Requests consume 1 token each
- Blocks when empty (returns False)

**Key Methods**:
```python
rate_limiter.acquire() -> bool      # Try to consume token
rate_limiter.wait_time() -> float   # Seconds until next token
rate_limiter.stats() -> dict        # Tokens, rate, requests
```

**Integration**:
```python
from trabajo_ia_server.utils.rate_limiter import rate_limiter

if not rate_limiter.acquire():
    raise Exception(f"Rate limited. Retry in {rate_limiter.wait_time()}s")
```

**Configuration**:
- Default: 120 requests/minute
- Configurable via environment: `FRED_RATE_LIMIT=120`
- Thread-safe implementation

### `utils/metrics.py` - Telemetry & Metrics
**Purpose**: Prometheus-style metrics for observability

**Architecture**: Counter + Gauge + Histogram metrics

**Tracked Metrics**:
- **Counters**:
  - `fred_api_requests_total` (by tool, status)
  - `cache_hits_total`, `cache_misses_total`
  - `rate_limit_blocks_total`

- **Gauges**:
  - `cache_size_bytes`
  - `rate_limiter_tokens_available`

- **Histograms**:
  - `fred_api_duration_seconds` (request latency)
  - `cache_operation_duration_seconds`

**Key Methods**:
```python
from trabajo_ia_server.utils.metrics import metrics

# Increment counter
metrics.increment("fred_api_requests_total",
                  labels={"tool": "search_series", "status": "success"})

# Set gauge value
metrics.gauge("cache_size_bytes", cache.size())

# Record timing
with metrics.timer("fred_api_duration_seconds"):
    result = fred_api.call()

# Get snapshot
stats = metrics.get_stats()  # Returns all metrics
```

**Output Format**: JSON (compatible with log aggregators)

**Internal Usage** (not exposed as MCP tool):
```python
# Used internally for diagnostics
{
  "cache": cache.stats(),
  "rate_limiter": rate_limiter.stats(),
  "metrics": metrics.get_stats(),
  "server_uptime": uptime_seconds
}
```

### `utils/fred_client.py` - Unified FRED API Client
**Purpose**: Centralized FRED API interaction with retry logic

**Responsibilities**:
- Manage `fredapi` library integration
- Implement automatic retry (3 attempts, exponential backoff)
- Integrate cache, rate limiter, metrics
- Standardize error handling

**Architecture**:
```python
fred_client.get_series(series_id)
  → check cache
  → rate limit check
  → API call (with retry)
  → record metrics
  → update cache
```

**Retry Policy**:
- Max 3 attempts
- Exponential backoff: 1s, 2s, 4s
- Retries on: Connection errors, timeouts, 5xx errors
- No retry on: 4xx errors, invalid API key

## Data Flow

### Standard Tool Request Flow

```
1. MCP Client Request
   ↓
2. FastMCP Server (server.py)
   ↓
3. Tool Decorator (@mcp.tool)
   ↓
4. Tool Implementation (e.g., tools/fred/observations.py)
   ↓
5. Input Validation (utils/validators.py)
   ↓
6. Cache Check (utils/cache.py)
   ├─→ Cache HIT → Return cached data (skip to step 12)
   └─→ Cache MISS → Continue
   ↓
7. Rate Limit Check (utils/rate_limiter.py)
   ├─→ Token available → Continue
   └─→ Rate limited → Wait or return error
   ↓
8. FRED API Client (utils/fred_client.py)
   ↓
9. FRED API Call (with retry logic)
   ↓
10. Record Metrics (utils/metrics.py)
   ↓
11. Update Cache (utils/cache.py)
   ↓
12. Data Processing (pandas)
   ↓
13. JSON Response
   ↓
14. MCP Client Response
```

### GDP Workflow Request Flow

```
1. MCP Client Request (analyze_gdp_cross_country)
   ↓
2. FastMCP Server → Tool Wrapper (tools/workflows/analyze_gdp_tool.py)
   ↓
3. Main Orchestrator (workflows/analyze_gdp.py)
   ↓
4. Input Validation & Preset Expansion (workflows/utils/gdp_validators.py)
   ↓
5. LAYER 1: Data Fetching (workflows/layers/fetch_data.py)
   ├─→ Country → Series ID mapping (workflows/utils/gdp_mappings.py)
   ├─→ Parallel FRED API calls (ThreadPoolExecutor)
   ├─→ Each call goes through standard cache/rate limiter flow
   └─→ Data alignment & missing value handling
   ↓
6. LAYER 2: Analysis (workflows/layers/analyze_data.py)
   ├─→ Growth metrics (CAGR, volatility, stability)
   ├─→ Structural breaks detection (rolling variance)
   ├─→ Convergence analysis (sigma/beta)
   └─→ Rankings & cross-country statistics
   ↓
7. LAYER 3: Formatting (workflows/layers/format_output.py)
   ├─→ Analysis format (compact JSON for AI)
   ├─→ Dataset format (tidy DataFrame)
   ├─→ Summary format (markdown)
   └─→ Both format (combined)
   ↓
8. JSON Response
   ↓
9. MCP Client Response
```

## Design Patterns

### 1. **Singleton Pattern**
Used in `config.py` for centralized configuration access.
```python
class Config:
    _api_key: Optional[str] = None

    @classmethod
    def get_api_key(cls) -> str:
        if cls._api_key is None:
            cls._api_key = os.getenv("FRED_API_KEY")
        return cls._api_key
```

### 2. **Strategy Pattern**
Cache backend selection (Memory/Disk/Redis):
```python
cache = CacheFactory.create(backend="memory")  # or "disk", "redis"
```

### 3. **Decorator Pattern**
- MCP tool registration: `@mcp.tool()`
- Cache memoization: `@cache.memoize(ttl=300)`
- Metrics timing: `@metrics.timed()`

### 4. **Factory Pattern**
- Logger creation: `setup_logger(__name__)`
- Cache backend creation: `CacheFactory.create(backend)`

### 5. **Dependency Injection**
Configuration and utilities injected into tools via imports.

### 6. **Layered Architecture**
GDP workflow uses 3-layer separation:
- Layer 1: Data fetching (I/O)
- Layer 2: Business logic (analysis)
- Layer 3: Presentation (formatting)

### 7. **Repository Pattern**
`fred_client.py` abstracts FRED API access, acting as data repository.

## Error Handling Strategy

### Validation Errors
- Caught early in validators
- Return JSON error response
- Log at ERROR level

### API Errors
- Caught in tool implementation
- FRED API errors wrapped with context
- Return structured error JSON

### Configuration Errors
- Caught at server startup
- Fail fast with clear message
- Exit with status code 1

### Runtime Errors
- Logged with full traceback
- Return error JSON to client
- Server continues running

## Extension Points

### Adding New Tools

1. **Create tool module**:
   ```python
   # src/trabajo_ia_server/tools/fred/search_series.py
   def search_series(query: str) -> str:
       # Implementation
       pass
   ```

2. **Register in server.py**:
   ```python
   @mcp.tool("search_fred_series")
   def search_fred_series(query: str) -> str:
       return search_series(query)
   ```

3. **Add tests**:
   ```python
   # tests/unit/tools/fred/test_search_series.py
   def test_search_series():
       # Test implementation
       pass
   ```

### Adding New Data Sources

1. Create new package: `tools/new_source/`
2. Implement tool functions
3. Register tools in `server.py`
4. Update configuration if needed
5. Add documentation

## Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies (FRED API, config)
- Located in `tests/unit/`

### Integration Tests
- Test complete tool workflows
- Use real FRED API (with test key)
- Located in `tests/integration/`

### Fixtures
- Shared test data
- Mock responses
- Located in `tests/fixtures/`

## Dependencies

### Core Dependencies
- `mcp[cli]` - Model Context Protocol framework
- `fredapi` - FRED API Python client
- `pandas` - Data manipulation
- `python-dotenv` - Environment variable loading
- `httpx` - HTTP client (transitive from MCP)

### Development Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `mypy` - Type checking
- `ruff` - Linting and formatting

## Configuration Management

### Environment Variables
Stored in `.env` file (not committed to git):
```bash
FRED_API_KEY=your_api_key_here
LOG_LEVEL=INFO
```

### Configuration Template
Stored in `config/.env.example`:
```bash
# FRED API Configuration
FRED_API_KEY=

# Logging Configuration
LOG_LEVEL=INFO
```

## Security Considerations

1. **API Key Protection**
   - Stored in `.env` (gitignored)
   - Never logged or exposed in responses
   - Validated before use

2. **Input Validation**
   - All user inputs validated
   - Date format checked
   - Series ID sanitized

3. **Error Messages**
   - No sensitive information leaked
   - Structured error responses
   - Full errors only in logs

## Performance Considerations

1. **Lazy Loading**
   - Configuration loaded once on startup
   - Logger instances cached

2. **Data Processing**
   - Pandas used for efficient data manipulation
   - NaN values removed to reduce payload size

3. **API Efficiency**
   - Date ranges specified to limit data transfer
   - Single API call per request

## Workflows Architecture

### GDP Cross-Country Analysis Workflow

**Location**: `src/trabajo_ia_server/workflows/`

**Pattern**: 3-Layer Architecture for complex multi-step analysis

#### Layer 1: Data Fetching (`layers/fetch_data.py`)
- Parallel FRED API calls using ThreadPoolExecutor
- Series ID mapping for 238 countries
- Automatic variant computation (growth rates, per capita)
- Data alignment and missing value handling
- Integrates with cache and rate limiter

#### Layer 2: Analysis (`layers/analyze_data.py`)
- **Growth Metrics**: CAGR, volatility, stability index
- **Structural Breaks Detection**:
  ```python
  def _detect_structural_breaks(series, threshold=0.05):
      # Rolling variance method (5-year window)
      # Detects when variance ratio > 1.5 or < 2/3
      # Identifies crisis periods and stabilization
  ```
- **Convergence Analysis**: Sigma and beta convergence tests
- **Rankings**: By GDP level and growth rate
- **Cross-country statistics**: Correlations, dispersions

#### Layer 3: Formatting (`layers/format_output.py`)
- **Analysis format**: AI-optimized compact JSON
- **Dataset format**: Tidy DataFrame for further processing
- **Summary format**: Markdown executive summary
- **Both format**: Combined analysis + dataset

#### Supporting Utilities
- **gdp_mappings.py**: 238 country codes → FRED series IDs
- **gdp_validators.py**: Input validation and preset expansion

### Structural Breaks Detection Method

Implemented using **rolling variance analysis**:

```python
# 5-year rolling window on year-over-year growth rates
window = 5
rolling_var = []

for i in range(len(growth_rates) - window + 1):
    window_data = growth_rates[i:i+window]
    rolling_var.append(np.var(window_data, ddof=1))

# Detect significant variance changes
for i in range(1, len(rolling_var)):
    ratio = rolling_var[i] / rolling_var[i-1]

    if ratio > 1.5:  # 50%+ increase
        # Volatility increase detected
        year_idx = i + window - 1  # Assign to last year of window

    elif ratio < 2/3:  # 33%+ decrease
        # Volatility decrease detected
        year_idx = i + window - 1
```

**Applications**:
- Economic crisis detection (1990-1991, 2008-2009)
- Structural reform impact analysis
- Policy regime changes
- Economic cycle analysis

## Completed Enhancements (v0.1.9)

✅ **Caching** - Multi-backend cache (in-memory, DiskCache, Redis)
✅ **Observability** - JSON logging with metrics and telemetry
✅ **Additional Tools** - 16+ FRED tools + GDP workflow
✅ **Data Models** - Type-safe configurations and responses

## Future Enhancements

1. **Additional Workflows**
   - Inflation analysis across regions
   - Labor market comparative analysis
   - Trade balance tracking
   - Monetary policy analysis

2. **Enhanced Structural Breaks**
   - Chow test implementation (requires statsmodels)
   - Bai-Perron multiple breakpoint detection
   - Confidence intervals for break dates

3. **Testing**
   - Increase test coverage to 90%+
   - Add property-based testing
   - Performance benchmarks for workflows

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [FRED API Docs](https://fred.stlouisfed.org/docs/api/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Python Packaging Guide](https://packaging.python.org/)

---

**Last Updated**: 2025-11-10 (v0.1.9)
**Architecture Version**: 3.0
