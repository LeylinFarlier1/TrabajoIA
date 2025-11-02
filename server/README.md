# Trabajo IA MCP Server

A **Model Context Protocol (MCP)** server that provides comprehensive access to Federal Reserve Economic Data (FRED) through a standardized interface.

## Features

### v0.1.9 - Observability, Cache & Resilience (Latest)
- **Shared Cache Layer**: Multi-backend cache (in-memory, DiskCache, Redis) with per-tool TTL tuning to keep hot queries under 400 ms.
- **Coordinated Rate Limiting**: Centralized backoff with penalty tracking to stay within FRED's 120 req/min budget while preserving throughput.
- **Structured Telemetry**: JSON logging with request context IDs plus in-process Prometheus-ready metrics for cache hits, retries, and latency.
- **Health Monitoring**: `system_health` MCP tool surfaces cache and rate-limiter status alongside metrics snapshots for automation hooks.
- **User-Agent Consistency**: Unified configuration-driven headers across all tools for easier observability on the FRED side.

### Core Features
- **FRED Data Access**: Fetch historical economic time-series data from FRED API
- **MCP Compliant**: Fully compatible with Model Context Protocol specification
- **Clean Architecture**: Modular, maintainable, and extensible codebase
- **Type Safety**: Full type hints for better IDE support
- **Comprehensive Logging**: Built-in logging for debugging and monitoring
- **Input Validation**: Validates dates and series IDs before API calls

## Installation

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip
- FRED API Key (get one free at https://fred.stlouisfed.org/docs/api/api_key.html)

### Setup

1. **Navigate to the project directory**:
   ```bash
   cd server
   ```

2. **Install dependencies**:
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

3. **Configure environment variables**:
   ```bash
   # Copy the example file
   cp config/.env.example .env

   # Edit .env and add your FRED API key
   # FRED_API_KEY=your_api_key_here
   ```

## Running the Server

### Using Python module:
```bash
python -m trabajo_ia_server
```

### Using UV:
```bash
uv run python -m trabajo_ia_server
```

The server will start and listen for MCP protocol messages via stdio.

## Available Tools

### 1. search_fred_series (v0.1.9 - Cached & Optimized)

Lightning-fast, cache-aware search for FRED economic data series with advanced filters.

**Performance:**
- Response time: ~0.4 seconds on warm cache (~0.5s cold)
- Optimized for AI/LLM consumption
- Compact JSON output (saves ~25% tokens)
- Integrates with shared cache and rate limiter to smooth bursts of queries

**Parameters:**
- `search_text` (string, required): Search query (e.g., "unemployment", "GDP")
- `limit` (int, optional): Max results (1-1000, default: **20** - optimal for AI)
- `offset` (int, optional): Starting offset for pagination (default: 0)
- `search_type` (string, optional): "full_text" or "series_id" (default: "full_text")
- `filter_variable` (string, optional): Filter by metadata (e.g., "frequency", "units")
- `filter_value` (string, optional): Value for filter (e.g., "Monthly", "Percent")
- `tag_names` (string, optional): Include tags, **semicolon-delimited** (e.g., "usa;nsa")
- `exclude_tag_names` (string, optional): Exclude tags, semicolon-delimited
- `order_by` (string, optional): Sort field (default: "popularity")
  - Options: "popularity", "search_rank", "title", "units", "last_updated"
- `sort_order` (string, optional): "asc" or "desc" (default: "desc")

**Returns:**
Compact JSON with list of matching series and comprehensive metadata

**Examples:**
```python
# Basic search - returns top 20 most relevant
search_fred_series("unemployment rate")

# Filtered search
search_fred_series("GDP", filter_variable="frequency", filter_value="Quarterly", limit=15)

# With tags (note: semicolon-delimited)
search_fred_series("inflation", tag_names="usa;nsa", order_by="last_updated")

# Get more results if needed
search_fred_series("interest rate", limit=50)
```

### 2. fetch_fred_series

Fetch historical observations for a FRED economic data series.

**Parameters:**
- `series_id` (string, required): FRED series identifier (e.g., GDP, UNRATE, CPIAUCSL)
- `observation_start` (string, optional): Start date in YYYY-MM-DD format
- `observation_end` (string, optional): End date in YYYY-MM-DD format

**Returns:**
JSON object containing data array and metadata

**Example:**
```python
fetch_fred_series("GDP", "2020-01-01", "2023-12-31")
```

### 3. system_health

Expose operational status, cache and rate-limiter telemetry, and key metrics for automation or dashboards.

**Returns:**
- Cache backend, hit/miss counters, and namespace TTLs
- Rate limiter windows, penalties, and last 429 timestamps
- Recent latency and retry metrics gathered by the in-process registry

## Project Structure

```
server/
├── src/                          # Source code
│   └── trabajo_ia_server/        # Main package
│       ├── server.py             # MCP server implementation
│       ├── config.py             # Configuration management
│       ├── tools/                # MCP tools
│       ├── models/               # Data models
│       └── utils/                # Utilities
├── tests/                        # Test suite
├── scripts/                      # Helper scripts
├── config/                       # Configuration files
├── docs/                         # Documentation
└── pyproject.toml                # Project metadata
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trabajo_ia_server
```

## Documentation

- Architecture Guide - See docs/architecture.md
- API Reference - See docs/api/
- Development Guide - See docs/guides/

## Common FRED Series IDs

- `GDP` - Gross Domestic Product
- `UNRATE` - Unemployment Rate
- `CPIAUCSL` - Consumer Price Index
- `DFF` - Federal Funds Rate
- `DEXUSEU` - USD/EUR Exchange Rate
- `SP500` - S&P 500 Index

Search for more series at https://fred.stlouisfed.org/

## Resources

- FRED API Documentation: https://fred.stlouisfed.org/docs/api/
- Model Context Protocol: https://modelcontextprotocol.io/
- FastMCP: https://github.com/jlowin/fastmcp
