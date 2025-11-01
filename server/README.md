# Trabajo IA MCP Server

A **Model Context Protocol (MCP)** server that provides access to Federal Reserve Economic Data (FRED) through a standardized interface.

## Features

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

### fetch_fred_series

Fetches historical observations for a FRED economic data series.

**Parameters:**
- `series_id` (string, required): FRED series identifier (e.g., GDP, UNRATE, CPIAUCSL)
- `observation_start` (string, optional): Start date in YYYY-MM-DD format
- `observation_end` (string, optional): End date in YYYY-MM-DD format

**Returns:**
JSON object containing data array and metadata

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
