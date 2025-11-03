# Workflows Documentation

## Overview

Workflows are **v0.2.0 end-to-end orchestration tools** that combine multiple v0.1.9 building blocks to deliver complete economic analysis with minimal user effort.

### Philosophy

- **One-Call Simplicity**: Complete analysis from data retrieval to insights
- **Best Practices Built-In**: Implements OECD/IMF/Eurostat methodology
- **Transparent Limitations**: Explicit about what is and isn't included
- **Production-Ready**: Error handling, logging, metrics, and documentation

## Available Workflows

### v0.2.0 (Current)

| Workflow | Status | Description | Documentation |
|----------|--------|-------------|---------------|
| `compare_inflation_across_regions` | ✅ Released | Compare inflation rates across countries with central bank target analysis, HICP/CPI harmonization, and comparability warnings | [Reference](./COMPARE_INFLATION_REFERENCE.md) |

### Future Planned Workflows

| Workflow | Status | Description |
|----------|--------|-------------|
| `analyze_labor_market` | 📋 Planned | Deep-dive unemployment and labor force participation analysis |
| `compare_gdp_growth` | 📋 Planned | GDP growth comparison with PPP adjustments |
| `download_for_analysis` | 📋 Planned | Export aligned cross-country data for external analysis |

## Quick Start

### Compare Inflation Across Regions

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to MCP server
server_params = StdioServerParameters(
    command="python",
    args=["-m", "trabajo_ia_server"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()

        # Compare inflation across G7
        result = await session.call_tool(
            "compare_inflation_across_regions",
            arguments={
                "regions": ["g7"]
            }
        )

        print(result)
```

## Design Philosophy: Focus over Breadth

**Previous Approach**: Try to handle inflation, unemployment, GDP, and interest rates in one generic tool.

**Current Approach**: One excellent inflation-focused tool that implements international best practices.

### Why Inflation-Only?

1. **Methodological Complexity**: Inflation comparison requires deep understanding of:
   - HICP (Harmonized Index) vs CPI differences
   - Owner-occupied housing treatment
   - Central bank targeting regimes
   - Base effects from policy changes
   - Quality adjustment methodologies

2. **Quality over Quantity**: "El que mucho abarca poco aprieta" - Better one excellent tool than four superficial ones

3. **Best Practices Implementation**: Follows OECD/IMF/Eurostat standards:
   - HICP prioritization for European countries (harmonized, excludes owner housing)
   - CPI for non-European countries (includes owner housing typically)
   - Year-over-year % change to eliminate seasonality
   - Central bank inflation target analysis
   - Comparability warnings for methodological differences
   - Base effects detection (VAT changes, subsidies unwinding)

## Architecture

### Workflow Structure

```
workflows/
├── __init__.py                      # Exports public workflows
├── compare_inflation.py             # Inflation-only comparison
└── utils/
    ├── __init__.py                  # Utility exports
    ├── inflation_mappings.py        # HICP/CPI series, targets, metadata
    └── calculations.py              # Statistical functions
```

### Design Patterns

**1. Orchestration Layer**
```python
def compare_inflation_across_regions(...):
    # STEP 1: Validate & Expand Parameters
    expanded_regions = expand_region_preset(regions)

    # STEP 2: Fetch Series IDs and Metadata
    series_metadata = {region: get_inflation_series(region) ...}

    # STEP 3: Parallel Data Fetch (ThreadPoolExecutor)
    with ThreadPoolExecutor() as executor:
        series_data = fetch_all_parallel(...)

    # STEP 4: Align Time Series (Inner Join)
    dates, aligned_data = align_time_series(series_data)

    # STEP 5: Statistical Analysis + Target Analysis
    ranking = rank_values(...)
    trends = calculate_trends(...)
    target_analysis = analyze_inflation_targets(...)

    # STEP 6: Generate Comparability Warnings
    warnings = get_comparability_warnings(regions)
    base_effects = detect_base_effects(aligned_data, dates)

    # STEP 7: Format Response
    return comprehensive_json_response(...)
```

**2. Separation of Concerns**
- **Workflows** (compare_inflation.py): Orchestration, error handling, response formatting
- **Mappings** (utils/inflation_mappings.py): Inflation-specific metadata, HICP/CPI selection, central bank targets
- **Calculations** (utils/calculations.py): Pure statistical functions
- **Tools** (v0.1.9): Granular FRED API wrappers

**3. Error Handling Philosophy**
```python
try:
    # Attempt workflow
    result = execute_workflow(...)
except Exception as e:
    # Return structured error, never crash
    return {
        "tool": "compare_inflation_across_regions",
        "error": str(e),
        "context": {...}
    }
```

## International Best Practices Implemented

### 1. HICP vs CPI Selection

**Europe**: Prioritize HICP (Harmonized Index of Consumer Prices)
- Excludes owner-occupied housing (~20-25% of basket)
- Harmonized methodology across EU countries
- Comparable across Euro Area

**Non-Europe**: CPI (Consumer Price Index)
- Includes owner-occupied housing (typically via OER or rental equivalence)
- National methodologies vary
- Less directly comparable internationally

### 2. Central Bank Inflation Targets

Automatically analyzes inflation relative to stated targets:

| Region | Target | Measure | Notes |
|--------|--------|---------|-------|
| USA | 2.0% | PCE (not CPI!) | Fed targets Personal Consumption Expenditures |
| Euro Area | 2.0% | HICP | ECB symmetric target since 2021 |
| UK | 2.0% | CPI | Bank of England explicit target |
| Australia | 2-3% | CPI | RBA range target |
| Canada | 2.0% | CPI | Bank of Canada midpoint |

### 3. Comparability Warnings

Automatically generated based on region combinations:

- **Mixed Index Types**: Warns when comparing HICP (Europe) vs CPI (non-Europe)
- **Owner Housing Treatment**: Highlights differences in housing coverage
- **Canada Mortgage Costs**: Flags Canada's unique inclusion of mortgage interest
- **Frequency Mismatches**: Identifies if some countries report quarterly vs monthly
- **Quality Adjustments**: Notes differences in hedonic adjustments (e.g., Sweden electronics)

### 4. Base Effects Detection

Detects temporary distortions in YoY inflation:

- Sharp drops followed by sharp rises (e.g., VAT rate changes)
- Policy subsidies unwinding
- Statistical anomalies from prior-year events

### 5. Sticky Inflation Analysis

Identifies persistent high inflation:
- Flags regions with >3% inflation for 6+ consecutive months
- Helps distinguish transitory vs persistent inflation

## Testing Strategy

### Test Coverage

- **Inflation Mappings Tests**: 54 tests covering series metadata, targets, warnings
- **Workflow Orchestration Tests**: 33 tests covering data fetching, target analysis, comparability warnings
- **Statistical Calculations Tests**: 40 tests (unchanged from generic version)
- **Total**: 127 passing tests

### Test Structure

```
tests/unit/workflows/
├── test_compare_inflation.py              # Workflow tests
└── utils/
    ├── test_inflation_mappings.py         # Inflation-specific mappings
    └── test_calculations.py               # Statistical functions
```

### Running Tests

```bash
# All workflow tests
pytest tests/unit/workflows/

# Specific test file
pytest tests/unit/workflows/test_compare_inflation.py -v

# All tests with coverage
pytest tests/unit/workflows/ --cov=trabajo_ia_server.workflows
```

## Performance Monitoring

### Key Metrics

```python
# Automatically logged via metrics system
metrics.record("workflow.compare_inflation.latency", duration_ms)
metrics.record("workflow.compare_inflation.regions_count", len(regions))
metrics.record("workflow.compare_inflation.data_points", len(dates))
metrics.record("workflow.compare_inflation.success", 1 if success else 0)
```

### Performance Targets (MVP v0.2.0)

| Metric | Target | Notes |
|--------|--------|-------|
| p50 latency | <1.5s | Typical 2-3 regions |
| p95 latency | <2.5s | Up to 5 regions |
| p99 latency | <5.0s | Worst case with cold cache |
| Success rate | >98% | Excluding invalid inputs |

## Workflow Design Principles

### 1. User Experience First

❌ **Bad**: Require multiple tool calls and manual harmonization
```python
# User has to know HICP vs CPI, manually align, analyze
series_usa = get_series_observations("CPIAUCSL", units="pc1")
series_euro = get_series_observations("CP0000EZ19M086NEST", units="pc1")
# ... manually check comparability, align dates, compare to targets
```

✅ **Good**: One call, complete analysis with best practices
```python
# Workflow handles HICP selection, target analysis, warnings
result = compare_inflation_across_regions(
    regions=["usa", "euro_area"]
)
```

### 2. Transparent Limitations

Every workflow response includes:

```json
{
  "comparison": {...},
  "metadata": {
    "series_used": [
      {
        "region": "usa",
        "index_type": "CPI",
        "includes_owner_housing": true,
        "methodological_notes": "CPI-U includes owner housing via OER..."
      }
    ]
  },
  "comparability_warnings": [
    "Mixed index types (CPI, HICP) - see methodological notes",
    "Owner-occupied housing: included in usa but excluded in euro_area"
  ],
  "limitations": [
    "No PPP adjustment - nominal comparison only",
    "CPI vs HICP methodological differences may affect comparability"
  ],
  "suggestions": [
    "Consider HICP-only comparison for Euro Area countries",
    "Review methodological notes for interpretation caveats"
  ]
}
```

### 3. Performance Optimization

- **Parallel Fetching**: ThreadPoolExecutor for concurrent API calls
- **Response Truncation**: Limit time series to 24 points for graphing
- **Early Validation**: Fail fast before expensive API calls
- **Caching**: Leverage v0.1.9 tool caching automatically

### 4. Statistical Rigor

- **Documented Methods**:
  - CV (Coefficient of Variation) for convergence analysis
  - Z-score for outlier detection
  - Linear regression for trend analysis
  - Distance from target for central bank adherence
- **Assumptions Explicit**:
  - "Assumes pc1 (YoY %) transformation eliminates seasonality"
  - "No PPP adjustment - compares nominal inflation rates"
- **Conservative Defaults**:
  - Inner join alignment (only common dates)
  - 2-sigma outlier threshold
  - Sticky inflation = >3% for 6+ months
- **Methodology References**: OECD/IMF/Eurostat best practices

## Contributing New Workflows

### Checklist

- [ ] Workflow implements single, well-defined use case
- [ ] Follows international best practices (OECD/IMF/Eurostat/etc.)
- [ ] Includes comprehensive metadata and methodological notes
- [ ] Generates comparability warnings for known limitations
- [ ] Has ≥90% test coverage
- [ ] Documented with reference guide + examples
- [ ] Performance tested (p95 < 2.5s)
- [ ] Registered in server.py with full docstring

## Roadmap

### v0.2.0 (Current)
- [x] compare_inflation_across_regions with HICP/CPI best practices
- [x] Central bank inflation target analysis
- [x] Comparability warnings generation
- [x] Base effects detection
- [ ] analyze_labor_market workflow
- [ ] download_for_analysis workflow

### v0.3.0 (Future)
- [ ] compare_gdp_growth with PPP adjustments
- [ ] Increase region limit to 10-15
- [ ] Structural break detection in inflation
- [ ] Correlation analysis across indicators

### v0.4.0 (Exploratory)
- [ ] Natural language query interface
- [ ] Automated insight generation
- [ ] Policy impact simulation

## FAQ

**Q: Why only inflation? What about unemployment/GDP?**

A: We prioritize depth over breadth. One excellent inflation tool with HICP/CPI harmonization, central bank target analysis, and comparability warnings is more valuable than four superficial generic tools. Future workflows will tackle other indicators with similar rigor.

**Q: When should I use this workflow vs v0.1.9 tools directly?**

A: Use workflow when:
- You want complete inflation analysis, not just data retrieval
- You're comparing countries and need HICP/CPI harmonization
- You value international best practices and comparability warnings

Use v0.1.9 tools when:
- You need fine-grained control
- You're building custom analysis pipelines
- You need indicators beyond inflation

**Q: What's the difference between HICP and CPI?**

A: Key differences:
- **Coverage**: HICP excludes owner-occupied housing (~20-25% of basket), CPI typically includes it
- **Harmonization**: HICP is harmonized across EU, CPI methodologies vary by country
- **Purpose**: HICP designed for cross-country comparison in EU, CPI for national inflation measurement
- **See**: Workflow automatically provides methodological notes per region

**Q: Why does the Fed target 2% but USA inflation is measured with CPI?**

A: The Federal Reserve targets 2% **PCE inflation** (Personal Consumption Expenditures), not CPI. PCE has broader coverage and lower weights for housing. The workflow flags this in target analysis: "Fed targets 2% PCE (not CPI)". CPI typically runs ~0.5pp higher than PCE.

**Q: Can I compare only HICP countries to avoid methodology issues?**

A: Yes! Compare Euro Area countries for maximum comparability:
```python
compare_inflation_across_regions(regions=["eurozone_core"])  # Germany, France, Netherlands
compare_inflation_across_regions(regions=["euro_area", "germany", "france", "italy", "spain"])
```

All will use HICP, exclude owner housing, and have minimal comparability warnings.

**Q: How do I export full time series data (not truncated to 24 points)?**

A: Use `download_for_analysis` workflow (v0.2.0 planned). It exports full aligned data in CSV/JSON format for offline analysis.

## Resources

- **API Reference**: [COMPARE_INFLATION_REFERENCE.md](./COMPARE_INFLATION_REFERENCE.md)
- **Methodology Documentation**: See OECD/IMF/Eurostat guidelines on international inflation comparison
- **Architecture Deep-Dive**: `docs/architecture.md`

## Changelog

### 2025-11-02 - v0.2.0 Inflation-Focused Refactoring
- **Breaking Change**: Removed generic `compare_across_regions` workflow
- **New**: `compare_inflation_across_regions` with HICP/CPI best practices
- **New**: Central bank inflation target analysis
- **New**: Comparability warnings for methodological differences
- **New**: Base effects detection (VAT changes, subsidies unwinding)
- **New**: Sticky inflation detection (>3% for 6+ months)
- **New**: Rich metadata per series (index type, housing treatment, sources)
- **Tests**: 127 passing tests (inflation mappings, workflow, calculations)
- **Documentation**: Complete rewrite focusing on inflation methodology

### 2025-11-01 - v0.2.0 Initial Release
- Initial workflows documentation structure
- compare_across_regions workflow (deprecated)
- 101 tests passing

---

**Maintained By:** TrabajoIA Server Team
**Last Updated:** 2025-11-02
**Version:** 2.0.0 (Inflation-Focused)
