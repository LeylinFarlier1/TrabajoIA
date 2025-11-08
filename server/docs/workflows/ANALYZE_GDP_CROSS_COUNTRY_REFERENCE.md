# GDP Cross-Country Analysis Tool – Comprehensive Reference
## Tool: analyze_gdp_cross_country

**MCP Tool Type:** Workflow (Multi-Layer Architecture)

**Description:** Advanced GDP analysis tool with comprehensive cross-country comparison, convergence testing, structural break detection, growth metrics, and flexible output formats. Built with 3-layer architecture for data fetching, analysis, and formatting.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Parameters](#parameters)
4. [Response Formats](#response-formats)
5. [Usage Examples](#usage-examples)
6. [Use Cases](#use-cases)
7. [Supported Countries & Presets](#supported-countries--presets)
8. [GDP Variants](#gdp-variants)
9. [Analysis Features](#analysis-features)
10. [Error Handling](#error-handling)
11. [Performance](#performance)
12. [Best Practices](#best-practices)
13. [Technical Implementation](#technical-implementation)
14. [Related Tools](#related-tools)

---

## Overview

The `analyze_gdp_cross_country` tool provides professional-grade GDP analysis for economic research, policy analysis, and international comparisons. It combines FRED data retrieval with sophisticated econometric analysis in a single MCP-compatible tool.

### Key Features

- **238 Countries/Territories**: Complete coverage of World Bank members
- **Preset Country Groups**: G7, G20, BRICS, OECD, regional groups
- **6 GDP Variants**: Nominal, constant prices, per capita, PPP-adjusted, growth rates
- **Automatic Computation**: Derives missing variants from available data
- **Convergence Analysis**: Sigma and beta convergence tests
- **Structural Break Detection**: Identifies regime changes and volatility shifts
- **Growth Metrics**: CAGR, volatility, stability index
- **Flexible Output**: 4 formats optimized for different use cases
- **AI-Optimized**: Compact JSON for LLM consumption

### Architecture Highlights

**3-Layer Design:**
1. **Fetch Layer**: Parallel FRED data retrieval with caching
2. **Analysis Layer**: Econometric computations and statistical tests
3. **Format Layer**: Output transformation for different consumers

**Infrastructure Integration:**
- Uses existing `fred_client` with rate limiting
- Redis caching with configurable TTL
- Concurrent fetching with ThreadPoolExecutor
- Comprehensive logging and error handling

---

## Architecture

### Workflow Diagram

```
User Request
    ↓
┌─────────────────────────────────────────┐
│  analyze_gdp_cross_country (Main)      │
│  - Input validation                     │
│  - FRED API key check                   │
│  - Error orchestration                  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  PHASE 1: Validation                    │
│  ├── validate_countries()               │
│  ├── validate_variants()                │
│  ├── validate_date_range()              │
│  └── validate_comparison_mode()         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  PHASE 2: Fetch Data Layer              │
│  ├── Determine series to fetch          │
│  ├── Parallel FRED requests (max 10)    │
│  ├── Convert to pandas Series           │
│  └── Compute derived variants           │
│      (growth_rate, per_capita_*)        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  PHASE 3: Analysis Layer                │
│  ├── Basic statistics (mean, std, min)  │
│  ├── Growth metrics (CAGR, volatility)  │
│  ├── Structural break detection         │
│  ├── Cross-country statistics           │
│  ├── Rankings (by level, by growth)     │
│  └── Convergence analysis (sigma/beta)  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  PHASE 4: Format Output Layer           │
│  ├── "analysis": AI-optimized JSON      │
│  ├── "dataset": Tidy DataFrame          │
│  ├── "summary": Markdown report         │
│  └── "both": Combined format            │
└─────────────────────────────────────────┘
    ↓
JSON String (MCP-compatible)
```

### File Structure

```
server/src/trabajo_ia_server/workflows/
├── analyze_gdp.py                    # Main orchestrator
├── layers/
│   ├── fetch_data.py                 # Layer 1: FRED data retrieval
│   ├── analyze_data.py               # Layer 2: Economic analysis
│   └── format_output.py              # Layer 3: Output formatting
└── utils/
    ├── gdp_mappings.py               # 238 country series IDs + presets
    └── gdp_validators.py             # Input validation logic
```

---

## Parameters

### Required Parameters

#### `countries` (string or list, REQUIRED)

Country code(s) or preset name.

**Format:** 
- Single country: `"usa"`
- Multiple countries (comma-separated string): `"usa,canada,mexico"`
- List: `["usa", "canada", "mexico"]`
- Preset: `"g7"`, `"latam"`, `"brics"`, etc.

**Examples:**
```python
countries="usa"                          # Single country
countries="usa,china,japan"              # Multiple countries (string)
countries=["usa", "china", "japan"]      # Multiple countries (list)
countries="g7"                           # Preset group
countries=["g7", "china", "india"]       # Mix preset + countries
```

**Available Presets:**
- `"g7"`, `"g20"`, `"brics"`, `"oecd"`
- `"latam"`, `"north_america"`, `"eurozone"`, `"asia_pacific"`
- `"emerging"`, `"developed"`
- See [Supported Countries & Presets](#supported-countries--presets)

---

### Optional Parameters - What to Analyze

#### `gdp_variants` (list of strings, optional)

GDP variants to analyze.

**Default:** `["per_capita_constant"]` (most commonly available)

**Valid Values:**
- `"nominal_usd"` - GDP in current USD
- `"constant_2010"` - GDP in constant 2010 USD (real growth)
- `"per_capita_constant"` - GDP per capita, constant prices (most used)
- `"per_capita_ppp"` - GDP per capita PPP-adjusted
- `"growth_rate"` - Annual growth rate (computed from constant_2010)
- `"ppp_adjusted"` - Total GDP PPP-adjusted

**Examples:**
```python
gdp_variants=["per_capita_constant"]                    # Default
gdp_variants=["per_capita_constant", "growth_rate"]     # Multiple
gdp_variants=["nominal_usd", "constant_2010", "ppp_adjusted"]
```

**Notes:**
- `growth_rate` is automatically computed from `constant_2010`
- `per_capita_*` variants are computed if source + population available
- Tool validates dependencies before fetching

#### `include_population` (boolean, optional)

Include population data in fetch.

**Default:** `True`

**Purpose:** Required for computing per capita variants

**When to set False:**
- Only analyzing total GDP (not per capita)
- Population data not needed

---

### Optional Parameters - Time Period

#### `start_date` (string, optional)

Start date for analysis period.

**Default:** `"1960-01-01"` (FRED/World Bank data start)

**Format:** `"YYYY-MM-DD"`

**Examples:**
```python
start_date="2000-01-01"     # 21st century only
start_date="1990-01-01"     # Post-Cold War
start_date="2010-01-01"     # Last decade
```

#### `end_date` (string, optional)

End date for analysis period.

**Default:** Latest available data

**Format:** `"YYYY-MM-DD"`

**Examples:**
```python
end_date="2023-12-31"       # End of 2023
end_date="2020-12-31"       # Pre-pandemic
end_date="2019-12-31"       # Exclude COVID period
```

#### `period_split` (string, optional)

Split analysis into sub-periods.

**Default:** `None` (single period analysis)

**Valid Values:**
- `"decade"` - Split by decades (1960-1969, 1970-1979, etc.)
- `"5y"` - 5-year periods
- `None` - No splitting

**Example:**
```python
period_split="decade"       # Analyze by decade
```

---

### Optional Parameters - Comparison Mode

#### `comparison_mode` (string, optional)

How to compare countries.

**Default:** `"absolute"`

**Valid Values:**
- `"absolute"` - Actual values in USD/units
- `"indexed"` - Normalize to 100 at base_year
- `"per_capita"` - Focus on per capita measures
- `"growth_rates"` - Focus on growth dynamics
- `"ppp"` - PPP-adjusted comparison
- `"relative_to_benchmark"` - Compare to benchmark country

**Examples:**
```python
comparison_mode="absolute"              # Default: actual values
comparison_mode="indexed"               # Normalize to base year
comparison_mode="growth_rates"          # Focus on growth
```

#### `base_year` (integer, optional)

Base year for indexed mode.

**Default:** `None` (uses start_date year if indexed mode)

**Required when:** `comparison_mode="indexed"`

**Examples:**
```python
base_year=2000                          # Y2K baseline
base_year=1990                          # Post-Cold War baseline
base_year=2010                          # Post-financial crisis
```

---

### Optional Parameters - Analysis Features

#### `include_rankings` (boolean, optional)

Compute country rankings.

**Default:** `True`

**Produces:**
- Rankings by latest level
- Rankings by growth rate (CAGR)
- Rankings by volatility/stability

#### `include_convergence` (boolean, optional)

Compute convergence analysis.

**Default:** `True`

**Produces:**
- **Sigma convergence:** Dispersion decreasing over time
- **Beta convergence:** Poor countries grow faster (catch-up effect)

**Requirements:** 3+ countries, 5+ overlapping observations

#### `include_growth_analysis` (boolean, optional)

Compute growth metrics.

**Default:** `True`

**Produces:**
- **CAGR:** Compound Annual Growth Rate
- **Volatility:** Standard deviation of growth
- **Stability Index:** 1 / (1 + volatility)
- **Total Growth %:** Overall period growth

#### `calculate_productivity` (boolean, optional)

Compute productivity metrics (GDP per hour worked).

**Default:** `False`

**Requirements:** Labor hours data (not yet implemented)

#### `detect_structural_breaks` (boolean, optional)

Detect structural breaks in time series.

**Default:** `True`

**Method:** Rolling variance detection (future: Chow test)

**Produces:**
- Break dates
- Break types (variance increase/decrease)
- Magnitude ratios

---

### Optional Parameters - Output

#### `output_format` (string, optional)

Output format type.

**Default:** `"analysis"`

**Valid Values:**

1. **`"analysis"`** (DEFAULT) - AI-optimized compact JSON
   - Minimal token usage
   - Hierarchical structure
   - Essential metrics only
   - Best for: LLM consumption, API responses

2. **`"dataset"`** - Tidy DataFrame format
   - Long format (one row per observation)
   - Columns: date, country, variant, value, unit
   - Best for: pandas, R, statistical software

3. **`"summary"`** - Human-readable markdown report
   - Executive summary
   - Key findings
   - Rankings
   - Best for: Reports, documentation

4. **`"both"`** - Combined analysis + dataset
   - Complete export
   - Both JSON analysis and tidy data
   - Best for: Comprehensive archives

**Examples:**
```python
output_format="analysis"        # Default: AI-optimized
output_format="dataset"         # For pandas/R
output_format="summary"         # Human-readable report
output_format="both"            # Complete export
```

#### `frequency` (string, optional)

Data frequency.

**Default:** `"annual"`

**Valid Values:**
- `"annual"` - Annual data (most common for GDP)
- `"quarterly"` - Quarterly data (limited availability)

---

### Optional Parameters - Technical

#### `fill_missing` (string, optional)

How to handle missing data.

**Default:** `"interpolate"`

**Valid Values:**
- `"interpolate"` - Linear interpolation between points
- `"forward"` - Forward fill (use last valid value)
- `"drop"` - Drop missing observations

#### `align_method` (string, optional)

Date alignment across countries.

**Default:** `"inner"`

**Valid Values:**
- `"inner"` - Use only dates common to all countries
- `"outer"` - Use all dates (may have gaps per country)

#### `benchmark_against` (string, optional)

Benchmark country for relative comparison.

**Default:** `None`

**Valid Values:**
- Country code (e.g., `"usa"`)
- `"world"` - World average (not yet implemented)
- `"oecd_avg"` - OECD average (not yet implemented)
- `None` - No benchmark

**Example:**
```python
benchmark_against="usa"         # Compare all to USA
```

#### `validate_variants` (boolean, optional)

Validate variant dependencies before fetching.

**Default:** `True`

**Purpose:** Check if source series exist for computed variants

**When to set False:**
- Skip validation for speed (not recommended)
- Trust input completely

---

## Response Formats

### Format 1: "analysis" (DEFAULT - AI-Optimized)

Compact JSON optimized for token efficiency and LLM consumption.

**Structure:**
```json
{
  "tool": "analyze_gdp_cross_country",
  "results": {
    "countries": {
      "usa": {
        "per_capita_constant": {
          "latest": {
            "date": "2023-01-01",
            "value": 63543.58,
            "unit": "USD per capita (2010)"
          },
          "growth": {
            "cagr_pct": 1.45,
            "volatility": 2.1,
            "stability_index": 0.323
          },
          "structural_breaks": [
            {
              "date": "2008-09-01",
              "type": "variance_increase",
              "ratio": 2.45
            }
          ],
          "stats": {
            "observations": 64,
            "first_date": "1960-01-01",
            "last_date": "2023-01-01",
            "mean": 45678.90,
            "min": 17432.11,
            "max": 63543.58
          }
        }
      }
    },
    "cross_country": {
      "per_capita_constant": {
        "statistics": {
          "mean": 35421.67,
          "median": 28934.12,
          "std": 15432.89,
          "cv": 0.436,
          "min": 5432.11,
          "max": 63543.58
        },
        "convergence": {
          "sigma": {
            "trend": "converging",
            "slope": -0.0023,
            "r_squared": 0.745,
            "p_value": 0.0001,
            "significant": true
          },
          "beta": {
            "coefficient": -0.0156,
            "r_squared": 0.523,
            "p_value": 0.0234,
            "significant": true,
            "interpretation": "catch-up growth"
          }
        }
      }
    },
    "rankings": {
      "per_capita_constant_level": [
        {"rank": 1, "country": "usa", "value": 63543.58},
        {"rank": 2, "country": "canada", "value": 48732.91}
      ],
      "per_capita_constant_growth": [
        {"rank": 1, "country": "china", "value": 8.23},
        {"rank": 2, "country": "india", "value": 5.67}
      ]
    }
  },
  "metadata": {
    "period": {
      "start": "1960-01-01",
      "end": "2023-12-31",
      "years": 63
    },
    "coverage": {
      "countries": ["usa", "canada", "china"],
      "variants": ["per_capita_constant"],
      "series_fetched": 6,
      "series_missing": 0
    },
    "computed_variants": ["growth_rate"],
    "limitations": [
      "Analysis period < 5 years - growth metrics may be unstable"
    ]
  },
  "interpretation": [
    "Sigma convergence: Countries are significantly converging (p=0.000)",
    "Beta convergence: catch-up growth detected (β=-0.016, p=0.023)"
  ]
}
```

**Token Efficiency:**
- 100 countries × 1 variant: ~15,000 tokens
- 10 countries × 2 variants: ~5,000 tokens
- 3 countries × 1 variant: ~1,500 tokens

---

### Format 2: "dataset" (Tidy Format)

Long-format DataFrame ready for statistical analysis.

**Structure:**
```json
{
  "tool": "analyze_gdp_cross_country",
  "dataset": [
    {
      "date": "1960-01-01",
      "country": "usa",
      "variant": "per_capita_constant",
      "value": 17432.11,
      "unit": "USD per capita (2010)"
    },
    {
      "date": "1960-01-01",
      "country": "canada",
      "variant": "per_capita_constant",
      "value": 15234.78,
      "unit": "USD per capita (2010)"
    }
  ],
  "metadata": {
    "format": "tidy",
    "rows": 192,
    "countries": 3,
    "variants": 1,
    "period": {
      "start": "1960-01-01",
      "end": "2023-01-01"
    }
  }
}
```

**Usage with pandas:**
```python
import json
import pandas as pd

result = analyze_gdp_cross_country("g7", output_format="dataset")
data = json.loads(result)
df = pd.DataFrame(data["dataset"])

# Pivot to wide format
df_wide = df.pivot_table(
    index="date", 
    columns="country", 
    values="value"
)
```

---

### Format 3: "summary" (Markdown Report)

Human-readable executive summary.

**Structure:**
```markdown
# GDP Cross-Country Analysis Summary

**Generated:** 2025-11-08 14:30 UTC
**Period:** 1960-01-01 to 2023-12-31
**Countries:** 7
**Variants:** per_capita_constant

## Rankings

### Top 5 by Growth Rate (CAGR)
1. **CHINA**: 8.23% per year
2. **INDIA**: 5.67% per year
3. **SOUTH_KOREA**: 5.12% per year

### Top 5 by Current Level
1. **USA**: 63543.58
2. **CANADA**: 48732.91
3. **GERMANY**: 46821.34

## Convergence Analysis

- **Sigma Convergence:** Countries are **converging** (significant) (slope: -0.0023, p=0.000)
- **Beta Convergence (Catch-up Growth):** **Yes** (β=-0.0156, p=0.023)

## Key Findings

- **Fastest growing:** CHINA (8.23% CAGR)
- **Slowest growing:** JAPAN (1.12% CAGR)
- **Average growth:** 3.45%
- **Variability (CV):** 0.436

## Limitations

- Some variants computed from other series (see metadata.computed_variants)
```

---

### Format 4: "both" (Combined)

Combines "analysis" + "dataset" in single JSON.

**Structure:**
```json
{
  "tool": "analyze_gdp_cross_country",
  "analysis": {
    /* Full analysis format results */
  },
  "dataset": [
    /* Full tidy dataset */
  ],
  "metadata": {
    /* Combined metadata */
    "dataset_rows": 192
  },
  "interpretation": [
    /* Interpretation hints */
  ]
}
```

---

## Usage Examples

### Example 1: Quick G7 Analysis

**Goal:** Compare G7 countries on per capita GDP.

```python
result = analyze_gdp_cross_country(
    countries="g7",
    gdp_variants=["per_capita_constant"],
    output_format="analysis"
)
```

**Result:**
- 7 countries analyzed
- Per capita constant prices (2010 USD)
- Full period (1960-2023)
- AI-optimized JSON

**Insight:** USA highest level, China highest growth (if included).

---

### Example 2: Latin America Convergence Study

**Goal:** Test convergence in Latin America since 2000.

```python
result = analyze_gdp_cross_country(
    countries="latam",
    gdp_variants=["per_capita_constant"],
    start_date="2000-01-01",
    include_convergence=True,
    detect_structural_breaks=True,
    output_format="summary"
)
```

**Result:**
- 11 Latin American countries
- 23 years of data (2000-2023)
- Sigma and beta convergence tests
- Structural break detection
- Markdown report format

**Insight:** Identifies if region is converging and detects crisis periods.

---

### Example 3: BRICS Growth Comparison

**Goal:** Compare BRICS growth trajectories with indexed values.

```python
result = analyze_gdp_cross_country(
    countries="brics",
    gdp_variants=["per_capita_constant"],
    comparison_mode="indexed",
    base_year=2000,
    start_date="2000-01-01",
    include_growth_analysis=True,
    output_format="analysis"
)
```

**Result:**
- 5 BRICS countries
- Indexed to 100 in year 2000
- Growth metrics (CAGR, volatility, stability)
- Rankings by growth rate

**Insight:** China and India show highest indexed growth from 2000 baseline.

---

### Example 4: USA vs China Historical Comparison

**Goal:** Long-run comparison with multiple variants.

```python
result = analyze_gdp_cross_country(
    countries=["usa", "china"],
    gdp_variants=[
        "per_capita_constant",
        "per_capita_ppp",
        "growth_rate"
    ],
    start_date="1960-01-01",
    detect_structural_breaks=True,
    output_format="both"
)
```

**Result:**
- 2 countries, 3 variants
- 63 years of data
- Both analysis and dataset formats
- Structural breaks detect 1979 Chinese reforms, 2008 financial crisis

**Insight:** Charts China's reform period, identifies growth regime shifts.

---

### Example 5: Custom Country List with Benchmark

**Goal:** Compare emerging markets to USA benchmark.

```python
result = analyze_gdp_cross_country(
    countries=["mexico", "brazil", "turkey", "indonesia"],
    gdp_variants=["per_capita_constant"],
    benchmark_against="usa",
    start_date="1990-01-01",
    include_rankings=True,
    output_format="analysis"
)
```

**Result:**
- 4 emerging markets + USA (benchmark)
- 33 years post-Cold War
- Relative performance vs USA
- Rankings show gap convergence

**Insight:** Identifies which countries are catching up to USA levels.

---

### Example 6: Eurozone Periphery Crisis Analysis

**Goal:** Analyze Eurozone periphery during debt crisis.

```python
result = analyze_gdp_cross_country(
    countries="eurozone_periphery",
    gdp_variants=["per_capita_constant", "growth_rate"],
    start_date="2000-01-01",
    end_date="2020-12-31",
    detect_structural_breaks=True,
    output_format="summary"
)
```

**Result:**
- 5 periphery countries (Spain, Italy, Portugal, Greece, Ireland)
- 2000-2020 period covers pre-Euro, crisis, recovery
- Structural breaks detect 2008-2012 crisis
- Markdown summary shows divergence patterns

**Insight:** Clear structural breaks 2008-2012, varied recovery paths.

---

### Example 7: Export Dataset for R Analysis

**Goal:** Get tidy data for statistical modeling in R.

```python
result = analyze_gdp_cross_country(
    countries="asia_pacific",
    gdp_variants=["per_capita_constant"],
    start_date="1980-01-01",
    output_format="dataset"
)

# Save to JSON for R import
import json
with open("asia_pacific_gdp.json", "w") as f:
    f.write(result)
```

**R Usage:**
```r
library(jsonlite)
library(tidyverse)

data <- fromJSON("asia_pacific_gdp.json")
df <- as_tibble(data$dataset)

# Ready for ggplot2, modeling
ggplot(df, aes(x=date, y=value, color=country)) +
  geom_line()
```

---

## Use Cases

### 1. Economic Research

**Problem:** Need comprehensive GDP data with convergence analysis for research paper.

**Solution:**
```python
result = analyze_gdp_cross_country(
    countries="oecd",
    gdp_variants=["per_capita_constant"],
    start_date="1960-01-01",
    include_convergence=True,
    include_growth_analysis=True,
    detect_structural_breaks=True,
    output_format="both"
)
```

**Benefits:**
- Complete OECD dataset
- Sigma/beta convergence pre-computed
- Structural breaks identified
- Both analysis and raw data

---

### 2. Policy Briefing

**Problem:** Executive summary for policy makers on regional economic trends.

**Solution:**
```python
result = analyze_gdp_cross_country(
    countries="latam",
    gdp_variants=["per_capita_constant"],
    start_date="2010-01-01",
    output_format="summary"
)
```

**Benefits:**
- Human-readable markdown
- Key findings highlighted
- Rankings for quick comparison
- No technical jargon

---

### 3. Investment Analysis

**Problem:** Compare emerging market growth for investment screening.

**Solution:**
```python
result = analyze_gdp_cross_country(
    countries="emerging",
    gdp_variants=["per_capita_constant", "growth_rate"],
    start_date="2015-01-01",
    include_growth_analysis=True,
    include_rankings=True,
    output_format="analysis"
)
```

**Benefits:**
- Growth metrics (CAGR, volatility)
- Stability index for risk assessment
- Rankings by growth and stability
- Recent 8-year period

---

### 4. Teaching Economics

**Problem:** Demonstrate convergence theory to students.

**Solution:**
```python
# Pre-convergence example
result = analyze_gdp_cross_country(
    countries=["usa", "japan", "south_korea", "china"],
    gdp_variants=["per_capita_constant"],
    comparison_mode="indexed",
    base_year=1960,
    include_convergence=True,
    output_format="summary"
)
```

**Benefits:**
- Clear visualization baseline (indexed)
- Convergence tests explained
- Real-world example of catch-up growth
- Markdown format for slides

---

### 5. AI-Powered Economic Assistant

**Problem:** LLM needs GDP data to answer user questions.

**Solution:**
```python
# User asks: "How fast is India growing compared to China?"
result = analyze_gdp_cross_country(
    countries=["india", "china"],
    gdp_variants=["per_capita_constant"],
    start_date="2000-01-01",
    include_growth_analysis=True,
    output_format="analysis"  # Default: AI-optimized
)
```

**Benefits:**
- Compact JSON minimizes tokens
- Pre-computed growth metrics
- Interpretation hints included
- Direct LLM consumption

---

## Supported Countries & Presets

### Preset Groups

**International Organizations:**
- `"g7"`: USA, Canada, UK, Germany, France, Italy, Japan (7 countries)
- `"g20"`: G7 + Argentina, Brazil, Mexico, Russia, Turkey, Saudi Arabia, India, China, South Korea, Indonesia, Australia, South Africa, Spain (20 countries)
- `"brics"`: Brazil, Russia, India, China, South Africa (5 countries)
- `"oecd"`: 38 OECD member countries

**Regional Groups:**
- `"latam"`: 11 Latin American countries (Argentina, Brazil, Chile, Colombia, Peru, Mexico, Uruguay, Venezuela, Bolivia, Ecuador, Paraguay)
- `"north_america"`: USA, Canada, Mexico (3 countries)
- `"eurozone"`: 11 Eurozone countries (Germany, France, Italy, Spain, etc.)
- `"asia_pacific"`: 12 Asia-Pacific countries (China, Japan, South Korea, India, ASEAN-5, Australia, New Zealand)
- `"middle_east"`: 5 Middle East countries (Saudi Arabia, Turkey, Israel, UAE, Egypt)
- `"africa"`: 6 major African economies (South Africa, Nigeria, Kenya, Ethiopia, Ghana, Morocco)

**Development Classification:**
- `"emerging"`: 19 emerging market economies (IMF classification)
- `"developed"`: 23 advanced economies (IMF classification)

**Special Groups:**
- `"eurozone_core"`: Germany, France, Netherlands, Austria, Belgium, Finland (6 countries)
- `"eurozone_periphery"`: Spain, Italy, Portugal, Greece, Ireland (5 countries)
- `"nordic"`: Sweden, Norway, Denmark, Finland (4 countries)
- `"east_asia"`: China, Japan, South Korea, Singapore (4 countries)
- `"southeast_asia"`: Indonesia, Thailand, Singapore, Malaysia, Philippines, Vietnam (6 countries)

### Individual Countries

**238 countries/territories supported** (World Bank members).

**Major Economies (Sample):**

**Americas:**
- USA, Canada, Mexico, Brazil, Argentina, Chile, Colombia, Peru

**Europe:**
- UK, Germany, France, Italy, Spain, Netherlands, Switzerland, Sweden, Norway, Poland, Austria, Belgium, Greece, Portugal, Ireland, Finland, Czech Republic, Denmark

**Asia-Pacific:**
- China, Japan, India, South Korea, Indonesia, Australia, Thailand, Singapore, Malaysia, Philippines, Vietnam, New Zealand

**Middle East:**
- Saudi Arabia, Turkey, Israel, UAE, Egypt

**Africa:**
- South Africa, Nigeria, Kenya, Ethiopia, Ghana, Morocco

**Full List:** See `gdp_mappings.py` for complete 238-country listing.

---

## GDP Variants

### Direct Fetch Variants

**1. `nominal_usd`** - GDP in Current USD
- **Description:** Gross Domestic Product in current US dollars
- **Unit:** Billions of USD
- **Use Case:** Compare absolute economic size
- **FRED Pattern:** `MKTGDP{country}646NWDB`
- **Note:** Affected by exchange rates and inflation

**2. `constant_2010`** - Real GDP (Constant 2010 USD)
- **Description:** GDP adjusted for inflation, base year 2010
- **Unit:** Billions of USD (2010 prices)
- **Use Case:** Real growth analysis, removes inflation
- **FRED Pattern:** `NYGDPMKTPKD{country}`
- **Note:** Best for growth rate calculations

**3. `per_capita_constant`** - GDP Per Capita (Constant Prices)
- **Description:** GDP per person in constant 2010 USD
- **Unit:** USD per capita (2010 prices)
- **Use Case:** Living standards, cross-country comparison (MOST COMMON)
- **FRED Pattern:** `NYGDPPCAPKD{country}`
- **Note:** Most widely available variant

**4. `per_capita_ppp`** - GDP Per Capita (PPP-Adjusted)
- **Description:** GDP per capita adjusted for purchasing power parity
- **Unit:** International dollars per capita
- **Use Case:** True living standard comparison, removes price level differences
- **FRED Pattern:** `NYGDPPCAPPPKD{country}`
- **Note:** Best for welfare comparisons

**5. `ppp_adjusted`** - Total GDP (PPP)
- **Description:** Total GDP adjusted for purchasing power parity
- **Unit:** International dollars (billions)
- **Use Case:** Economic size comparison without exchange rate distortions
- **FRED Pattern:** `PPPGDP{country}`

**6. `population`** - Population
- **Description:** Total population
- **Unit:** Number of persons
- **Use Case:** Required for per capita calculations
- **FRED Pattern:** `POPTOT{country}647NWDB`

### Computed Variants

**7. `growth_rate`** - Annual GDP Growth Rate
- **Computed From:** `constant_2010`
- **Formula:** `((value_t / value_t-1) - 1) * 100`
- **Unit:** Percent
- **Use Case:** Growth momentum, business cycle analysis
- **Note:** Automatically computed if `constant_2010` available

**8. `per_capita_*` (if not available directly)**
- **Computed From:** Base variant + `population`
- **Formula:** `(gdp_billions * 1e9) / population`
- **Fallback:** Tries direct FRED fetch first, computes if unavailable

### Variant Selection Guide

| Use Case | Recommended Variant | Reason |
|----------|-------------------|---------|
| Economic size comparison | `nominal_usd` or `ppp_adjusted` | Absolute economic power |
| Living standards | `per_capita_ppp` | Accounts for price levels |
| Growth analysis | `constant_2010` or `growth_rate` | Removes inflation |
| Long-run trends | `per_capita_constant` | Most available, real growth |
| Welfare comparisons | `per_capita_ppp` | True purchasing power |
| Business cycles | `growth_rate` | Momentum indicators |

---

## Analysis Features

### Growth Metrics

**CAGR (Compound Annual Growth Rate):**
- Formula: `((end_value / start_value)^(1/years) - 1) * 100`
- Interpretation: Average annual growth over period
- Unit: Percent per year
- Note: Not computed for `growth_rate` variant (CAGR of growth rates doesn't make economic sense)

**Volatility:**
- Formula: `std(year-over-year growth rates)`
- Interpretation: How much growth fluctuates
- Unit: Percentage points
- High volatility (>3%): Economic instability

**Stability Index:**
- Formula: `1 / (1 + volatility)`
- Range: 0 to 1 (higher = more stable)
- Interpretation: Investment attractiveness metric
- Example: Stability of 0.8 = low volatility

**Total Growth:**
- Formula: `((end_value / start_value) - 1) * 100`
- Interpretation: Cumulative growth over entire period
- Unit: Percent

### Rankings

**By Level:**
- Ranks countries by latest value
- Use: Who is richest/largest now?
- Example: USA #1 in per capita constant

**By Growth:**
- Ranks countries by CAGR
- Use: Who is growing fastest?
- Example: China #1 in growth rate (1960-2020)

**By Stability:**
- Ranks by stability index (low volatility)
- Use: Who has stable growth?
- Example: Switzerland high stability

### Convergence Analysis

**Sigma Convergence:**
- **Question:** Is dispersion between countries decreasing?
- **Method:** Linear regression of coefficient of variation over time
- **Null Hypothesis:** No convergence (slope = 0)
- **Result:**
  - Slope < 0, p < 0.05: **Significant convergence**
  - Slope > 0, p < 0.05: **Significant divergence**
  - p > 0.05: **No significant trend**
- **Interpretation:** Countries becoming more similar over time

**Beta Convergence:**
- **Question:** Do poor countries grow faster than rich (catch-up effect)?
- **Method:** Regression of growth rate on log(initial GDP)
- **Null Hypothesis:** No catch-up (β = 0)
- **Result:**
  - β < 0, p < 0.05: **Significant catch-up growth**
  - β > 0, p < 0.05: **Rich grow faster (divergence)**
  - p > 0.05: **No significant relationship**
- **Interpretation:** Solow growth model prediction

**Requirements:**
- Minimum 3 countries
- Minimum 5 overlapping observations
- Common time period

**Example Output:**
```json
"convergence": {
  "sigma": {
    "trend": "converging",
    "slope": -0.0023,
    "r_squared": 0.745,
    "p_value": 0.0001,
    "significant": true
  },
  "beta": {
    "coefficient": -0.0156,
    "r_squared": 0.523,
    "p_value": 0.0234,
    "significant": true,
    "interpretation": "catch-up growth"
  }
}
```

### Structural Break Detection

**Method (Current):**
- Rolling variance with 12-observation window
- Detects when variance doubles or halves
- Identifies regime changes and volatility shifts

**Method (Future):**
- Chow test for parameter stability
- Bai-Perron multiple break detection
- Requires `statsmodels` library

**Output:**
```json
"structural_breaks": [
  {
    "date": "2008-09-01",
    "type": "variance_increase",
    "ratio": 2.45
  },
  {
    "date": "2020-03-01",
    "type": "variance_increase",
    "ratio": 3.12
  }
]
```

**Interpretation:**
- **variance_increase:** Crisis, shock, instability
- **variance_decrease:** Stabilization, recovery
- **ratio > 2:** Major structural change

**Known Break Examples:**
- 2008-09: Financial crisis
- 2020-03: COVID-19 pandemic
- 1997-07: Asian financial crisis
- 1979-01: Chinese economic reforms

---

## Error Handling

### Common Errors

#### 1. Missing FRED API Key

**Error:**
```json
{
  "tool": "analyze_gdp_cross_country",
  "error": "FRED_API_KEY_MISSING",
  "error_message": "FRED API key not configured. Set FRED_API_KEY environment variable.",
  "metadata": {
    "fetch_timestamp": "2025-11-08T14:30:00Z"
  }
}
```

**Cause:** `FRED_API_KEY` environment variable not set

**Fix:**
```bash
export FRED_API_KEY="your_fred_api_key"
```

---

#### 2. No Valid Countries

**Error:**
```json
{
  "tool": "analyze_gdp_cross_country",
  "error": "Input validation failed",
  "validation_errors": ["No valid countries provided"],
  "warnings": ["Unknown countries (will be skipped): invalid_name"],
  "metadata": {
    "fetch_timestamp": "2025-11-08T14:30:00Z"
  }
}
```

**Cause:** Invalid country codes or preset names

**Fix:**
```python
# Bad
countries="invalid_country"

# Good
countries="usa"
countries="g7"
```

---

#### 3. No Data Fetched

**Error:**
```json
{
  "tool": "analyze_gdp_cross_country",
  "error": "NO_DATA_FETCHED",
  "error_message": "Could not fetch any data from FRED for the requested countries/variants",
  "details": {
    "requested_countries": ["usa"],
    "requested_variants": ["per_capita_constant"],
    "missing_series": ["usa/per_capita_constant"],
    "errors": []
  },
  "metadata": {
    "fetch_timestamp": "2025-11-08T14:30:00Z",
    "fetched_series_count": 0
  }
}
```

**Cause:** Series not available in FRED for country/variant combination

**Fix:**
- Try different variant (e.g., `per_capita_constant` instead of `per_capita_ppp`)
- Check if country has FRED data
- Use different date range

---

#### 4. Invalid Date Range

**Error:**
```json
{
  "validation_errors": ["Invalid date range"],
  "warnings": [
    "Invalid start_date format: 2020/01/01 (expected YYYY-MM-DD)",
    "start_date must be before end_date"
  ]
}
```

**Cause:** Date format incorrect or start >= end

**Fix:**
```python
# Bad
start_date="2020/01/01"
start_date="2023-01-01"
end_date="2020-01-01"

# Good
start_date="2020-01-01"
end_date="2023-12-31"
```

---

#### 5. Missing Variant Dependencies

**Error:**
```json
{
  "validation_errors": ["Missing dependencies: {'growth_rate': ['constant_2010']}"],
  "warnings": [
    "Cannot compute growth_rate: missing constant_2010 (missing for: country_x, country_y)"
  ]
}
```

**Cause:** Computed variant requires source variant not available

**Fix:**
- Use different variant
- Exclude countries without required data
- Set `validate_variants=False` (not recommended)

---

#### 6. Convergence Insufficient Data

**Result (not an error, but limitation noted):**
```json
"convergence": {
  "sigma": null,
  "beta": null,
  "note": "Insufficient overlapping data"
}
```

**Cause:** 
- Fewer than 3 countries
- Fewer than 5 common observations

**Fix:**
- Add more countries
- Extend date range
- Use `align_method="outer"` (may introduce gaps)

---

### Warnings vs Errors

**Warnings (analysis proceeds):**
- Some countries have missing data
- Computed variants used instead of direct fetch
- Short time period (< 5 years)
- Few countries for convergence (< 3)

**Errors (analysis stops):**
- No valid countries
- No data fetched
- Invalid date format
- Invalid parameters
- Missing FRED API key

---

## Performance

### Response Time

**Factors:**
- Number of countries
- Number of variants
- Date range
- Cache status
- FRED API latency

**Benchmarks:**

| Configuration | Series | Response Time | Notes |
|---------------|--------|---------------|-------|
| 3 countries, 1 variant, cached | 3 | 0.5-1.0s | Cache hit |
| 3 countries, 1 variant, uncached | 3 | 2-3s | FRED fetch |
| G7 (7 countries), 2 variants | 14 | 4-6s | Parallel fetch |
| OECD (38 countries), 1 variant | 38 | 8-12s | Max 10 concurrent |
| G20 (20 countries), 3 variants | 60 | 10-15s | With computation |

**Optimization:**
- **Caching:** 24-hour TTL (configurable)
- **Parallel Fetching:** Max 10 concurrent FRED requests
- **Rate Limiting:** Built-in (30 req/min for free tier)

### Token Usage (AI Applications)

**Output Format Token Estimates:**

| Format | Configuration | Approximate Tokens |
|--------|---------------|-------------------|
| `analysis` | 3 countries, 1 variant | ~1,500 |
| `analysis` | 10 countries, 2 variants | ~5,000 |
| `analysis` | 100 countries, 1 variant | ~15,000 |
| `dataset` | 3 countries, 64 years | ~8,000 |
| `summary` | Any | ~500-1,000 |
| `both` | 10 countries, 2 variants | ~13,000 |

**Tips for Token Efficiency:**
- Use `output_format="analysis"` (default, most compact)
- Limit `start_date` to recent period
- Request only needed variants
- Use `output_format="summary"` for human review

---

## Best Practices

### 1. Choose Appropriate Variant

```python
# For living standards comparison
analyze_gdp_cross_country(
    countries="g7",
    gdp_variants=["per_capita_ppp"]  # Best for welfare comparison
)

# For growth analysis
analyze_gdp_cross_country(
    countries="emerging",
    gdp_variants=["constant_2010", "growth_rate"]  # Real growth
)

# For economic size
analyze_gdp_cross_country(
    countries="g20",
    gdp_variants=["nominal_usd"]  # Absolute size
)
```

### 2. Set Meaningful Date Ranges

```python
# Post-Cold War analysis
analyze_gdp_cross_country(
    countries="eurozone",
    start_date="1990-01-01"
)

# Exclude COVID disruption
analyze_gdp_cross_country(
    countries="asia_pacific",
    end_date="2019-12-31"
)

# Focus on specific period
analyze_gdp_cross_country(
    countries="latam",
    start_date="2000-01-01",
    end_date="2019-12-31"  # Millennium to pre-pandemic
)
```

### 3. Use Presets for Common Groups

```python
# Good - use preset
analyze_gdp_cross_country(countries="g7")

# Avoid - typing all countries
analyze_gdp_cross_country(
    countries=["usa", "canada", "uk", "germany", "france", "italy", "japan"]
)

# Mix preset + custom
analyze_gdp_cross_country(countries=["g7", "china", "india"])
```

### 4. Match Output Format to Use Case

```python
# For LLM/AI consumption
output_format="analysis"  # Default, compact

# For pandas/statistical analysis
output_format="dataset"

# For reports/presentations
output_format="summary"

# For comprehensive archives
output_format="both"
```

### 5. Enable Relevant Analysis Features

```python
# Research paper - all features
analyze_gdp_cross_country(
    countries="oecd",
    include_convergence=True,
    include_growth_analysis=True,
    detect_structural_breaks=True
)

# Quick dashboard - minimal analysis
analyze_gdp_cross_country(
    countries="g7",
    include_convergence=False,
    include_growth_analysis=False,
    detect_structural_breaks=False
)
```

### 6. Handle Missing Data Appropriately

```python
# For complete time series (research)
align_method="inner"  # Only common dates

# For maximum coverage (visualization)
align_method="outer"  # All dates, may have gaps

# Interpolate gaps
fill_missing="interpolate"

# Conservative approach
fill_missing="drop"  # Only use observed values
```

### 7. Validate Before Heavy Queries

```python
# Validate availability first
result = analyze_gdp_cross_country(
    countries=["custom_country_1", "custom_country_2"],
    gdp_variants=["per_capita_ppp"],
    validate_variants=True,  # Check before fetching
    start_date="2010-01-01",
    end_date="2010-12-31"  # Small date range for test
)

# If successful, expand to full analysis
result = analyze_gdp_cross_country(
    countries=["custom_country_1", "custom_country_2"],
    gdp_variants=["per_capita_ppp"],
    start_date="1960-01-01"  # Full period
)
```

---

## Technical Implementation

### Layer 1: Fetch Data (`fetch_data.py`)

**Responsibilities:**
- Map country/variant to FRED series IDs
- Parallel data retrieval (ThreadPoolExecutor)
- Convert FRED JSON to pandas Series
- Compute derived variants
- Cache management

**Key Functions:**
- `fetch_gdp_data()` - Main entry point
- `_fetch_single_series()` - Individual FRED request
- Computation logic for `growth_rate`, `per_capita_*`

**Data Flow:**
```python
Input: countries, variants, dates
  ↓
Determine series_to_fetch (with dependencies)
  ↓
Parallel FRED fetches (max 10 workers)
  ↓
Convert observations to pd.Series
  ↓
Compute derived variants
  ↓
Output: Dict[country][variant] = pd.Series
```

### Layer 2: Analysis (`analyze_data.py`)

**Responsibilities:**
- Basic statistics (mean, std, min, max)
- Growth metrics (CAGR, volatility, stability)
- Structural break detection
- Cross-country analysis
- Rankings
- Convergence tests

**Key Functions:**
- `analyze_gdp_data()` - Main orchestrator
- `_compute_growth_metrics()` - CAGR, volatility
- `_compute_cagr()` - Compound annual growth
- `_detect_structural_breaks()` - Rolling variance method
- `_compute_convergence()` - Sigma/beta convergence
- `_apply_indexed_transformation()` - Normalize to base year

**Data Flow:**
```python
Input: Dict[country][variant] = pd.Series
  ↓
Apply comparison_mode transformations (indexed, etc.)
  ↓
Per-country analysis loop
  ├── Basic stats
  ├── Growth metrics
  └── Structural breaks
  ↓
Cross-country analysis
  ├── Latest snapshot stats
  ├── Rankings
  └── Convergence (if enabled)
  ↓
Output: AnalysisResult (by_country, cross_country, rankings, metadata)
```

### Layer 3: Format Output (`format_output.py`)

**Responsibilities:**
- Transform analysis results to output format
- Token optimization for AI consumption
- Tidy dataset generation
- Markdown summary generation

**Key Functions:**
- `format_analysis()` - AI-optimized JSON (default)
- `format_dataset()` - Tidy DataFrame
- `format_summary()` - Markdown report
- `format_both()` - Combined output
- `_generate_interpretation_hints()` - AI-friendly hints

**Format Decision Tree:**
```python
output_format == "analysis"
  ↓ format_analysis()
  → Compact JSON, ~1,500 tokens per 3 countries

output_format == "dataset"
  ↓ format_dataset()
  → Tidy DataFrame, one row per observation

output_format == "summary"
  ↓ format_summary()
  → Markdown report, ~500-1,000 tokens

output_format == "both"
  ↓ format_both()
  → Combined analysis + dataset
```

### Utility Modules

**`gdp_mappings.py`:**
- 238 country series ID mappings
- Preset group definitions
- Variant dependency rules
- Helper functions (expand_preset, get_series_id)

**`gdp_validators.py`:**
- Input validation logic
- Variant dependency checking
- Date range validation
- Comprehensive error messages

### Infrastructure Integration

**FRED Client:**
```python
from trabajo_ia_server.utils.fred_client import fred_client

response = fred_client.get_json(
    url="https://api.stlouisfed.org/fred/series/observations",
    params={"series_id": series_id, ...},
    namespace="gdp_series",
    ttl=86400  # 24-hour cache
)
```

**Rate Limiting:**
- Built into `fred_client`
- 30 requests/minute (free tier)
- 120 requests/minute (paid tier)

**Caching:**
- Redis backend (via `fred_client`)
- 24-hour default TTL
- Namespace: `gdp_series`

**Logging:**
```python
from trabajo_ia_server.utils.logger import setup_logger
logger = setup_logger(__name__)

logger.info(f"Fetching {len(countries)} countries...")
logger.warning(f"Missing data for {country}/{variant}")
logger.error(f"FRED API error: {error_message}")
```

---

## Related Tools

### MCP FRED Tools (Used Internally)

1. **`get_fred_series_observations`**
   - Core FRED data retrieval
   - Used by `fetch_data_layer`
   - Reference: [FRED_OBSERVATIONS_REFERENCE.md](../api/FRED_OBSERVATIONS_REFERENCE.MD)

2. **`search_fred_series`**
   - Find series IDs
   - Not used internally (series IDs pre-mapped)

3. **`get_fred_series_tags`**
   - Series metadata
   - Not used internally

### Complementary Analysis Tools

**For Next Steps After GDP Analysis:**

1. **Correlation Analysis**
   - Correlate GDP with other economic indicators
   - Example: GDP vs unemployment, inflation, trade balance

2. **Forecasting**
   - Project future GDP based on historical trends
   - Time series models (ARIMA, exponential smoothing)

3. **Visualization**
   - Generate charts from dataset output
   - Use `matplotlib`, `plotly`, or R `ggplot2`

4. **Regression Modeling**
   - GDP as dependent variable
   - Explanatory variables: education, investment, institutions

### Typical Workflow

```python
# Step 1: Get GDP data
gdp_result = analyze_gdp_cross_country(
    countries="g7",
    gdp_variants=["per_capita_constant"],
    output_format="both"
)

# Step 2: Parse results
import json
data = json.loads(gdp_result)
analysis = data["analysis"]
dataset = data["dataset"]

# Step 3: Further analysis (Python/pandas)
import pandas as pd
df = pd.DataFrame(dataset)

# Pivot to wide format
df_wide = df.pivot_table(index="date", columns="country", values="value")

# Plot
import matplotlib.pyplot as plt
df_wide.plot(figsize=(12, 6), title="G7 GDP Per Capita (Constant 2010 USD)")
plt.ylabel("USD per capita")
plt.show()

# Step 4: Statistical modeling
from scipy import stats

# Test for convergence (manual check)
initial = df_wide.iloc[0]
growth = ((df_wide.iloc[-1] / df_wide.iloc[0]) ** (1/len(df_wide)) - 1) * 100
stats.spearmanr(initial, growth)  # Negative = convergence
```

---

## Version Information

- **Tool Version:** v1.0.0 (introduced in MCP server v0.2.0)
- **Architecture:** 3-layer (fetch, analyze, format)
- **FRED API:** Uses `/fred/series/observations` endpoint
- **Dependencies:** pandas, numpy, scipy
- **Last Updated:** 2025-11-08

---

## Future Enhancements

### Planned Features (v1.1.0)

1. **Chow Test for Structural Breaks**
   - Replace rolling variance with proper Chow test
   - Requires `statsmodels` integration

2. **Quarterly Data Support**
   - Currently annual only
   - Add quarterly frequency for short-run analysis

3. **Benchmark Comparison**
   - `benchmark_against="usa"` implementation
   - Compute relative performance metrics

4. **Period Split Analysis**
   - `period_split="decade"` implementation
   - Compare growth across sub-periods

5. **Export to Excel**
   - `output_format="excel"` with formatted tables
   - Ready-to-use charts

6. **Productivity Metrics**
   - GDP per hour worked (requires labor data integration)
   - Total factor productivity (TFP)

### Under Consideration (v2.0)

1. **GDP Components**
   - Consumption, investment, government, net exports
   - Sector breakdowns (agriculture, industry, services)

2. **Forecast Mode**
   - Simple extrapolation
   - ARIMA/exponential smoothing models

3. **World Bank API Integration**
   - Fallback for missing FRED data
   - Additional indicators (poverty, inequality)

4. **Interactive Visualizations**
   - HTML output with Plotly charts
   - Embedded in markdown summary

---

## Support & Resources

### Documentation
- **This Reference:** Complete tool documentation
- **Architecture Doc:** [architecture.md](../architecture.md)
- **FRED Observations:** [FRED_OBSERVATIONS_REFERENCE.md](../api/FRED_OBSERVATIONS_REFERENCE.MD)

### External Resources
- **FRED Database:** https://fred.stlouisfed.org/
- **World Bank Data:** https://data.worldbank.org/
- **IMF Data:** https://www.imf.org/en/Data

### Support
- **Issues:** GitHub repository issues
- **Email:** [Project maintainer email]

---

## Summary

The `analyze_gdp_cross_country` tool is a comprehensive solution for:

✅ **Multi-country GDP analysis** with 238 countries
✅ **Preset groups** (G7, BRICS, OECD, regional)
✅ **6 GDP variants** with automatic computation
✅ **Convergence testing** (sigma and beta)
✅ **Structural break detection**
✅ **Growth metrics** (CAGR, volatility, stability)
✅ **Flexible output formats** (AI, dataset, summary, combined)
✅ **Production-ready** with caching, rate limiting, error handling

**Key Strengths:**
- 3-layer architecture (modular, maintainable)
- Parallel data fetching (performance)
- AI-optimized output (token efficient)
- Comprehensive analysis (research-grade)
- MCP-compatible (JSON string output)

**Best For:**
- Economic research and policy analysis
- Cross-country comparisons
- Convergence studies
- Investment analysis
- Teaching and learning economics
- AI-powered economic assistants

**Remember:**
- Use presets for common country groups
- Choose appropriate GDP variant for your question
- Set meaningful date ranges
- Match output format to your use case
- Enable only needed analysis features
- Validate inputs for custom configurations

---

**End of Reference Document**

*For questions, issues, or contributions, please refer to the project repository.*
