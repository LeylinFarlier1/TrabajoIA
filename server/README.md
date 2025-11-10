# Trabajo IA MCP Server

A **Model Context Protocol (MCP)** server that provides comprehensive access to Federal Reserve Economic Data (FRED) through a standardized interface.

## Features

### v0.1.9 - Observability, Cache & Resilience (Latest)
- **Shared Cache Layer**: Multi-backend cache (in-memory, DiskCache, Redis) with per-tool TTL tuning to keep hot queries under 400 ms.
- **Coordinated Rate Limiting**: Centralized backoff with penalty tracking to stay within FRED's 120 req/min budget while preserving throughput.
- **Structured Telemetry**: JSON logging with request context IDs plus in-process Prometheus-ready metrics for cache hits, retries, and latency.
- **Internal Health Monitoring**: Internal diagnostics for cache and rate-limiter status with metrics snapshots (not exposed as MCP tool).
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

## Client Integration

This MCP server works with multiple clients. See the comprehensive integration guide:
📖 **[Quick Start Guide](../QUICKSTART.md)** - Step-by-step setup for:
- **Claude Desktop** - Native MCP support
- **VSCode** - Claude Dev / Cline extensions
- **Claude Code CLI** - Command-line interface

Quick setup:
1. Install dependencies: `uv pip install -e .`
2. Configure your FRED API key in `.env`
3. Add server to your client's MCP configuration
4. Restart your client
5. Start asking questions about economic data!

## Available Tools (12)

The server provides comprehensive FRED data access through categorized tools:

### Core FRED Search & Data Tools

#### `search_fred_series`
Fast, AI-optimized search (~0.4s with cache). Search by keywords with advanced filters.
- **Performance**: Compact JSON, 20 results default
- **Key params**: `search_text`, `limit`, `filter_variable`, `tag_names`, `order_by`
- **Example**: `search_fred_series("unemployment", tag_names="usa;nsa")`

#### `get_fred_series_observations`
Fetch historical time-series data with transformations.
- **Params**: `series_id`, `observation_start/end`, `units`, `frequency`
- **Units**: "lin", "chg", "pch" (percent change), "pc1" (YoY%), "log"
- **Example**: `get_fred_series_observations("GDP", "2020-01-01", units="pch")`

#### `get_fred_tags`
Discover available tags by group (frequency, geography, seasonal adjustment, source).
- **Tag groups**: "freq", "geo", "seas", "src", "gen"
- **Example**: `get_fred_tags(tag_group_id="freq")`

#### `search_fred_related_tags`
Find tags that frequently co-occur with specified tags.
- **Example**: `search_fred_related_tags("monetary aggregates")`

#### `get_fred_series_by_tags`
Find series matching ALL specified tags, excluding others.
- **Example**: `get_fred_series_by_tags("slovenia;food;oecd")`

#### `search_fred_series_tags`
Get tags associated with series matching a search.
- **Example**: `search_fred_series_tags("monetary service index")`

#### `search_fred_series_related_tags`
Related tags within search context.

#### `get_fred_series_tags`
Tags for a specific series ID.

### Category Navigation Tools

#### `get_fred_category`
Get metadata about a FRED category (ID, name, parent).

#### `get_fred_category_children`
Browse subcategories in the hierarchy tree.

#### `get_fred_category_series`
List all series within a category with filtering options.

### Advanced Economic Analysis Workflows

#### `analyze_gdp_cross_country` ⭐
**Comprehensive multi-country GDP analysis with econometric features.**

**Coverage:**
- **238 Countries/Territories** + **Preset Groups**:
  - `"g7"`, `"g20"`, `"brics"`, `"oecd"`, `"eu"`
  - `"latam"`, `"asia"`, `"africa"`, `"emerging"`, `"developed"`
- **6 GDP Variants**: nominal_usd, constant_2010, per_capita_constant, per_capita_ppp, growth_rate, ppp_adjusted

**Key Features:**

1. **Structural Break Detection** (Rolling Variance Method)
   ```python
   # 5-year rolling window on growth rates
   # Detects variance changes ≥50%
   if ratio > 1.5:      # Volatility increase (crisis)
   elif ratio < 2/3:    # Volatility decrease (stabilization)
   ```
   - Identifies economic crises: 1990-91 recession, 2008-09 financial crisis
   - Detects policy regime changes and structural reforms

2. **Convergence Analysis**
   - **Sigma convergence**: Dispersion trends over time (CV analysis)
   - **Beta convergence**: Catch-up effect testing (poor grow faster?)

3. **Growth Metrics**
   - CAGR (Compound Annual Growth Rate)
   - Volatility (growth rate std dev)
   - Stability index

4. **Rankings**
   - By final GDP level (2010, etc.)
   - By growth rate (CAGR)

5. **Output Formats**
   - `"analysis"`: AI-optimized JSON
   - `"dataset"`: Tidy DataFrame for further analysis
   - `"summary"`: Markdown executive summary
   - `"both"`: Combined analysis + dataset

**Example Usage:**
```python
# G7 analysis 1980-2010 with all features
analyze_gdp_cross_country(
    countries="g7",
    gdp_variants="per_capita_constant",
    start_date="1980-01-01",
    end_date="2010-12-31",
    detect_structural_breaks=True,
    include_convergence=True,
    include_rankings=True,
    output_format="both"
)

# Latin America comparison vs USA benchmark
analyze_gdp_cross_country(
    countries="latam",
    comparison_mode="indexed",
    base_year=2000,
    benchmark_against="usa"
)
```

**Documentation**: See [docs/workflows/ANALYZE_GDP_CROSS_COUNTRY_REFERENCE.md](docs/workflows/ANALYZE_GDP_CROSS_COUNTRY_REFERENCE.md)

## Project Structure

```
server/
├── src/trabajo_ia_server/              # Source code
│   ├── server.py                       # FastMCP server + tool registration
│   ├── config.py                       # Centralized configuration
│   │
│   ├── tools/                          # MCP Tools (12 exposed)
│   │   ├── fred/                       # FRED API tools (11 tools)
│   │   │   ├── search_series.py        # Advanced search
│   │   │   ├── observations.py         # Historical data
│   │   │   ├── get_tags.py             # Tag discovery
│   │   │   ├── related_tags.py         # Related tags
│   │   │   ├── series_by_tags.py       # Tag-based search
│   │   │   ├── search_series_tags.py   # Series search tags
│   │   │   ├── search_series_related_tags.py
│   │   │   ├── get_series_tags.py      # Series-specific tags
│   │   │   ├── category.py             # Category info
│   │   │   ├── category_children.py    # Subcategories
│   │   │   └── category_series.py      # Series in category
│   │   │
│   │   ├── system/                     # Internal utilities (not exposed)
│   │   │   └── health.py               # Internal health diagnostics
│   │   │
│   │   └── workflows/                  # Workflow tool wrappers (1 tool)
│   │
│   ├── workflows/                      # Complex analysis workflows
│   │   ├── analyze_gdp.py              # GDP analysis orchestrator
│   │   │
│   │   ├── layers/                     # 3-layer architecture
│   │   │   ├── fetch_data.py           # Layer 1: FRED data retrieval
│   │   │   ├── analyze_data.py         # Layer 2: Economic analysis
│   │   │   └── format_output.py        # Layer 3: Output formatting
│   │   │
│   │   └── utils/                      # Workflow utilities
│   │       ├── gdp_mappings.py         # 238 country series IDs
│   │       └── gdp_validators.py       # Input validation
│   │
│   ├── utils/                          # Shared utilities
│   │   ├── cache.py                    # Multi-backend caching
│   │   ├── rate_limiter.py             # FRED API rate limiting
│   │   ├── metrics.py                  # Prometheus-style telemetry
│   │   ├── fred_client.py              # Unified FRED client
│   │   ├── logger.py                   # Structured logging
│   │   └── validators.py               # Input validation
│   │
│   └── models/                         # Data models
│
├── tests/                              # Test suite (pytest)
│   ├── unit/                           # Unit tests
│   │   ├── tools/                      # Tool tests
│   │   ├── utils/                      # Utility tests
│   │   └── workflows/                  # Workflow tests
│   ├── integration/                    # Integration tests
│   └── fixtures/                       # Test data
│
├── docs/                               # Documentation
│   ├── api/                            # FRED API references (11 docs)
│   ├── workflows/                      # Workflow documentation
│   │   └── ANALYZE_GDP_CROSS_COUNTRY_REFERENCE.md
│   ├── guides/                         # Development guides
│   ├── Release_notes/                  # Version releases
│   └── architecture.md                 # System architecture
│
├── config/                             # Configuration templates
├── .env                                # Environment variables (gitignored)
└── pyproject.toml                      # Dependencies & metadata
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trabajo_ia_server
```

## Documentation

### Architecture & Technical Reference
- **[Architecture Guide](docs/architecture.md)** - Complete system architecture with 3-layer workflow design
- **[GDP Workflow Reference](docs/workflows/ANALYZE_GDP_CROSS_COUNTRY_REFERENCE.md)** - Comprehensive GDP analysis documentation
- **[Working Paper](docs/WORKING_PAPER_MCP_ARCHITECTURE.md)** - MCP architecture design paper

### API Reference (11 Documents)
- **[FRED Search](docs/api/FRED_SEARCH_REFERENCE.md)** - search_fred_series complete reference
- **[FRED Observations](docs/api/FRED_OBSERVATIONS_REFERENCE.MD)** - get_fred_series_observations
- **[FRED Tags](docs/api/FRED_TAGS_REFERENCE.MD)** - Tag system documentation
- **[FRED Categories](docs/api/FRED_CATEGORY_REFERENCE.MD)** - Category navigation
- **Additional API docs** - See [docs/api/](docs/api/) for all 11 references

### Development Guides
- **[Testing Guide](docs/guides/MCP_PROJECT_TESTING_GUIDE.md)** - How to write and run tests
- **[New Tool Guide](docs/guides/IMPLEMENTACION_NUEVA_TOOL_GUIA.md)** - Implementing new MCP tools
- **[Version Update Guide](docs/guides/VERSION_UPDATE_GUIDE.md)** - Updating versions

### Release Information
- **[Release Notes v0.1.9](docs/Release_notes/RELEASE_NOTES_v0.1.9.md)** - Cache, telemetry, resilience features
- **[CHANGELOG](docs/Changelog/CHANGELOG.md)** - Complete version history
- **[v0.2.0 Expansion Plan](docs/planning/v0.2.0_expansion_plan.md)** - Future roadmap

## Common FRED Series IDs

- `GDP` - Gross Domestic Product
- `UNRATE` - Unemployment Rate
- `CPIAUCSL` - Consumer Price Index
- `DFF` - Federal Funds Rate
- `DEXUSEU` - USD/EUR Exchange Rate
- `SP500` - S&P 500 Index

Search for more series at https://fred.stlouisfed.org/

## Resources

- **FRED API Documentation**: https://fred.stlouisfed.org/docs/api/
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **FastMCP**: https://github.com/jlowin/fastmcp

## Examples & Use Cases

See practical examples in the repository:
- **[prueba_workflow/](../prueba_workflow/)** - Complete G7 GDP analysis (1980-2010) with 7 visualizations
- **[prueba_modular/](../prueba_modular/)** - Step-by-step modular analysis approach
- **[correcion_workflow/](../correcion_workflow/)** - Structural breaks detection timeline

## Project Info

**Version**: 0.1.9
**Author**: Agustin Ernesto Mealla Cormenzana
**Last Updated**: November 10, 2025
**Status**: ✅ Production Ready

**License**: Open Source
**Python**: 3.10+
**Dependencies**: mcp, fredapi, pandas, httpx, tenacity
