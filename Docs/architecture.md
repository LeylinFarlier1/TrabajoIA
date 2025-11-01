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
│       ├── tools/                # Tool implementations
│       │   ├── __init__.py
│       │   └── fred/             # FRED-specific tools
│       │       ├── __init__.py
│       │       └── fetch_series.py
│       │
│       ├── models/               # Data models (future)
│       │   └── __init__.py
│       │
│       └── utils/                # Utilities
│           ├── __init__.py
│           ├── logger.py         # Logging setup
│           └── validators.py     # Input validation
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
│
├── scripts/                      # Development scripts
├── config/                       # Configuration templates
├── docs/                         # Documentation
│   ├── api/                      # API docs
│   ├── guides/                   # User guides
│   └── architecture.md           # This file
│
├── .env                          # Environment variables (gitignored)
├── .gitignore                    # Git exclusions
├── .python-version               # Python version
├── pyproject.toml                # Project metadata
├── uv.lock                       # Dependency lock
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

## Data Flow

```
1. MCP Client Request
   ↓
2. FastMCP Server (server.py)
   ↓
3. Tool Decorator (@mcp.tool)
   ↓
4. Tool Implementation (tools/fred/fetch_series.py)
   ↓
5. Input Validation (utils/validators.py)
   ↓
6. Configuration Access (config.py)
   ↓
7. FRED API Call (fredapi library)
   ↓
8. Data Processing (pandas)
   ↓
9. JSON Response
   ↓
10. MCP Client Response
```

## Design Patterns

### 1. **Singleton Pattern**
Used in `config.py` for centralized configuration access.

### 2. **Factory Pattern**
Logger creation through `setup_logger()` function.

### 3. **Decorator Pattern**
MCP tool registration using `@mcp.tool()`.

### 4. **Dependency Injection**
Configuration and logger instances injected into tools.

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

## Future Enhancements

1. **Caching**
   - Add Redis/SQLite cache for FRED data
   - Reduce API calls
   - Improve response time

2. **Data Models**
   - Add Pydantic models for request/response validation
   - Improve type safety
   - Better error messages

3. **Additional Tools**
   - `search_fred_series` - Search for series by keywords
   - `get_series_info` - Get metadata about a series
   - `get_categories` - Browse FRED categories

4. **Observability**
   - Add structured logging (JSON)
   - Metrics collection
   - Tracing support

5. **Testing**
   - Increase test coverage
   - Add property-based testing
   - Performance benchmarks

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [FRED API Docs](https://fred.stlouisfed.org/docs/api/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Python Packaging Guide](https://packaging.python.org/)
