# Compare Inflation Across Regions - API Reference

## Tool: `compare_inflation_across_regions`

End-to-end workflow for comparing inflation rates across multiple countries/regions with international best practices from OECD/IMF/Eurostat. Handles HICP/CPI harmonization, central bank target analysis, comparability warnings, and base effects detection.

## Purpose & Design Philosophy

This workflow implements **OECD/IMF/Eurostat inflation comparison methodology**: prioritizing HICP for Europe, documenting methodological differences, analyzing central bank targets, and providing transparent comparability warnings.

### Key Features

- **HICP Prioritization**: Uses Harmonized Index for European countries (excludes owner housing, comparable across EU)
- **CPI for Non-Europe**: Uses Consumer Price Index for non-European countries (typically includes owner housing)
- **Central Bank Target Analysis**: Automatically compares inflation to stated targets (2% ECB, 2% Fed PCE, 2-3% RBA, etc.)
- **Comparability Warnings**: Flags methodological differences (housing treatment, quality adjustments, frequency)
- **Base Effects Detection**: Identifies temporary distortions from VAT changes or policy unwinding
- **Sticky Inflation Analysis**: Flags persistent high inflation (>3% for 6+ months)
- **Rich Metadata**: Index type, housing treatment, methodological notes per series
- **One-Call Simplicity**: Complete analysis from data retrieval to insights

## Why Inflation-Only?

**Philosophy**: "El que mucho abarca poco aprieta" - Better one excellent tool than four superficial ones.

**Methodological Complexity**: Inflation comparison requires:
- Understanding HICP vs CPI differences (~20-25% basket coverage difference for housing)
- Central bank targeting regimes (Fed targets PCE not CPI, ECB targets HICP)
- Base effects detection (VAT changes, subsidy unwinding)
- Quality adjustment methodologies (e.g., Sweden's more extensive electronics adjustments)
- Owner-occupied housing treatment (OER in USA, rental equivalence in UK, excluded in HICP)

## Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `regions` | list[string] | List of region codes or presets. Can mix both. Maximum 5 regions (MVP limit). |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start_date` | string | 5 years ago | Start date for comparison (YYYY-MM-DD format) |
| `end_date` | string | Latest available | End date for comparison (YYYY-MM-DD format) |
| `metric` | string | `"latest"` | Analysis focus: `"latest"`, `"trend"`, `"all"` |

### Removed Parameters (from generic workflow)

- ❌ `indicator`: No longer needed - workflow is inflation-only
- ❌ `normalize`: Removed - not relevant for YoY % change comparison

## Valid Parameter Values

### regions

#### Individual Region Codes

**North America:**
- `usa`, `canada`, `mexico`

**Europe (HICP):**
- `euro_area`, `germany`, `france`, `italy`, `spain`, `netherlands`, `belgium`, `austria`, `portugal`, `finland`, `ireland`, `greece`

**Europe (CPI):**
- `uk`, `switzerland`, `sweden`, `norway`, `poland`, `czech_republic`

**Asia-Pacific:**
- `japan`, `china`, `south_korea`, `australia`, `new_zealand`, `india`, `thailand`, `philippines`

**Other Major Economies:**
- `brazil`, `russia`, `south_africa`, `turkey`, `chile`, `colombia`

#### Region Presets

| Preset | Description | Countries | Index Types |
|--------|-------------|-----------|-------------|
| `g7` | Group of Seven | USA, Canada, UK, Germany, France, Italy, Japan | Mixed (CPI + HICP) |
| `brics` | BRICS Countries | Brazil, Russia, India, China, South Africa | All CPI |
| `eurozone_core` | Eurozone Core | Germany, France, Netherlands | All HICP |
| `eurozone_periphery` | Eurozone Periphery | Italy, Spain, Portugal, Greece | All HICP |
| `nordic` | Nordic Countries | Sweden, Norway, Finland | Mixed |
| `north_america` | North America | USA, Canada, Mexico | All CPI |
| `asia_pacific` | Asia-Pacific Major | Japan, China, South Korea, Australia, New Zealand, India | All CPI |
| `europe_major` | Major European Economies | UK, Germany, France, Italy, Spain | Mixed (CPI + HICP) |

**Mixing Presets and Individual Codes:**
```python
regions=["eurozone_core", "usa", "uk"]  # Germany, France, Netherlands + USA + UK
regions=["g7"]                          # All G7 countries (will be truncated to 5 for MVP)
```

**Duplicate Handling:** Automatically removed while preserving order

### metric

Analysis focus parameter:

- **`"latest"`** (default) - Latest snapshot and ranking
  - Returns: Latest value per region, ranking, central bank target analysis, basic statistics
  - Use case: Quick status check, current state comparison

- **`"trend"`** - Trend analysis over period
  - Returns: Latest + Linear regression trends, direction, velocity
  - Use case: Long-term trajectory comparison

- **`"all"`** - All metrics
  - Returns: Latest + Trends + Convergence analysis + Full time series (24 points)
  - Use case: Comprehensive analysis

## Response Format

### Complete Response Structure

```json
{
  "tool": "compare_inflation_across_regions",
  "comparison": {
    "latest_snapshot": {
      "date": "2025-10-01",
      "ranking": [
        {
          "region": "euro_area",
          "value": 2.22,
          "rank": 1,
          "target": 2.0,
          "distance_from_target": 0.22,
          "target_measure": "HICP YoY"
        },
        {
          "region": "uk",
          "value": 2.50,
          "rank": 2,
          "target": 2.0,
          "distance_from_target": 0.50,
          "target_measure": "CPI YoY"
        },
        {
          "region": "usa",
          "value": 3.02,
          "rank": 3,
          "target": 2.0,
          "distance_from_target": 1.02,
          "target_measure": "PCE YoY (not CPI)"
        }
      ]
    },
    "target_analysis": {
      "regions_above_target": ["usa"],
      "regions_at_target": ["euro_area", "uk"],
      "regions_below_target": [],
      "sticky_inflation": ["usa"],
      "notes": "Fed targets 2% PCE (not CPI) - CPI typically runs ~0.5pp higher"
    },
    "analysis": {
      "highest": {"region": "usa", "value": 3.02, "rank": 3},
      "lowest": {"region": "euro_area", "value": 2.22, "rank": 1},
      "spread": 0.80,
      "mean": 2.58,
      "std": 0.41,
      "convergence": "regions converging (CV decreased from 0.45 to 0.16)",
      "outliers": []
    },
    "trends": {
      "usa": {
        "slope": -0.15,
        "direction": "decreasing",
        "velocity": "-0.15/period"
      },
      "euro_area": {
        "slope": -0.08,
        "direction": "decreasing",
        "velocity": "-0.08/period"
      },
      "uk": {
        "slope": -0.12,
        "direction": "decreasing",
        "velocity": "-0.12/period"
      }
    },
    "time_series": [
      {"date": "2024-10-01", "usa": 3.50, "euro_area": 2.80, "uk": 2.90},
      {"date": "2024-11-01", "usa": 3.30, "euro_area": 2.60, "uk": 2.70},
      {"date": "2024-12-01", "usa": 3.10, "euro_area": 2.40, "uk": 2.55},
      ...  // up to 24 most recent points
    ]
  },
  "metadata": {
    "fetch_date": "2025-11-02T12:00:00Z",
    "series_used": [
      {
        "region": "usa",
        "series_id": "CPIAUCSL",
        "index_type": "CPI",
        "source": "BLS",
        "verified_date": "2025-01",
        "frequency": "Monthly",
        "includes_owner_housing": true,
        "methodological_notes": "CPI-U includes owner-occupied housing via OER (Owner's Equivalent Rent), which constitutes ~24% of the basket. This differs from HICP which excludes owner housing."
      },
      {
        "region": "euro_area",
        "series_id": "CP0000EZ19M086NEST",
        "index_type": "HICP",
        "source": "Eurostat",
        "verified_date": "2025-01",
        "frequency": "Monthly",
        "includes_owner_housing": false,
        "methodological_notes": "HICP EXCLUDES owner-occupied housing costs (no imputed rents or OER). This creates ~20-25% basket coverage difference vs CPI countries. HICP is harmonized across EU for comparability."
      },
      {
        "region": "uk",
        "series_id": "CPHP",
        "index_type": "CPI",
        "source": "ONS",
        "verified_date": "2025-01",
        "frequency": "Monthly",
        "includes_owner_housing": true,
        "methodological_notes": "UK CPI includes housing via rental equivalence approach. Switched from RPI to CPI as primary measure. CPI YoY is BoE's inflation target."
      }
    ],
    "data_points": 58,
    "time_series_points_returned": 24,
    "alignment_method": "inner_join",
    "transformation": "pc1",
    "transformation_description": "Year-over-year % change (eliminates seasonality)",
    "regions_requested": ["usa", "euro_area", "uk"],
    "regions_expanded": ["usa", "euro_area", "uk"],
    "regions_with_data": ["usa", "euro_area", "uk"]
  },
  "comparability_warnings": [
    "Mixed index types: CPI (usa, uk), HICP (euro_area) - see methodological notes for interpretation",
    "Owner-occupied housing: included in usa, uk but excluded in euro_area. This represents ~20-25% of basket coverage difference.",
    "Fed (USA) targets 2% PCE inflation, not CPI. CPI typically runs ~0.5pp higher than PCE due to broader coverage and different weights."
  ],
  "limitations": [
    "No PPP (Purchasing Power Parity) adjustment - compares nominal inflation rates only",
    "CPI vs HICP methodological differences may affect comparability (see warnings)",
    "Inner join alignment may reduce available data if update frequencies differ",
    "Maximum 5 regions for MVP (performance constraint)",
    "Time series truncated to 24 most recent points (use download_for_analysis for full data)",
    "Base effects detection is statistical - may miss policy-driven distortions"
  ],
  "suggestions": [
    "For maximum comparability, compare only HICP countries (eurozone_core, eurozone_periphery presets)",
    "Review 'series_used' metadata for methodological notes on each region's index",
    "Consider PCE for USA instead of CPI when comparing to Fed target",
    "Check 'target_analysis' to understand distance from central bank targets",
    "Use 'comparability_warnings' to identify interpretation caveats"
  ]
}
```

## HICP vs CPI: Key Differences

### What is HICP?

**HICP** (Harmonized Index of Consumer Prices) is the EU's standard for comparable inflation measurement across member states.

**Key Characteristics:**
- **Harmonized methodology** across all EU countries
- **Excludes owner-occupied housing** (no imputed rents, no OER)
- **Purpose**: Cross-country comparison within EU
- **Used by**: ECB for monetary policy target (2% HICP)
- **Coverage**: Euro Area + other EU countries

### What is CPI?

**CPI** (Consumer Price Index) is national inflation measure used by most non-EU countries.

**Key Characteristics:**
- **National methodologies** vary by country
- **Includes owner-occupied housing** (typically via OER, rental equivalence, or mortgage costs)
- **Purpose**: National inflation measurement
- **Used by**: Most central banks (with notable exception: Fed targets PCE)
- **Coverage**: Global (most countries)

### Owner-Occupied Housing Treatment

| Approach | Used By | Basket Weight | Methodology |
|----------|---------|---------------|-------------|
| **OER** (Owner's Equivalent Rent) | USA | ~24% | Asks homeowners: "If you rented your home, how much would it cost?" |
| **Rental Equivalence** | UK, Australia | ~15-20% | Uses actual rental market prices as proxy for housing costs |
| **Mortgage Interest** | Canada | ~4-6% | Includes mortgage interest costs directly |
| **Excluded** | Euro Area (HICP) | 0% | Treats housing as investment, not consumption |

**Impact**: This creates ~20-25% basket coverage difference when comparing HICP to CPI countries.

### Workflow Handling

The workflow automatically:
1. **Selects HICP for European countries** (where available)
2. **Documents index type** in `metadata.series_used[].index_type`
3. **Flags housing differences** in `comparability_warnings`
4. **Provides methodological notes** for each series

## Central Bank Inflation Targets

The workflow automatically analyzes inflation relative to central bank targets:

### Target Specifications

| Region | Point Target | Range Target | Target Measure | Regime Start | Notes |
|--------|--------------|--------------|----------------|--------------|-------|
| USA | 2.0% | - | **PCE** (not CPI!) | 2012 | Fed targets Personal Consumption Expenditures, not CPI. CPI typically ~0.5pp higher. |
| Euro Area | 2.0% | - | HICP YoY | 1999 | ECB symmetric target since 2021 (previously "below but close to 2%") |
| UK | 2.0% | - | CPI YoY | 2003 | BoE explicit target, Chancellor's remit |
| Canada | 2.0% | 1-3% | CPI YoY | 1991 | BoC targets midpoint of 1-3% range |
| Australia | - | 2-3% | CPI YoY | 1993 | RBA flexible target, "over time" average |
| Japan | 2.0% | - | CPI YoY | 2013 | BoJ target since 2013 (previously ~1%) |
| Switzerland | - | <2% | CPI YoY | 2000 | SNB defines price stability as <2% inflation |
| Sweden | 2.0% | - | CPIF YoY | 1995 | Riksbank uses CPIF (CPI at constant mortgage rates) |
| Norway | 2.0% | - | CPI YoY | 2001 | Norges Bank flexible inflation targeting |
| New Zealand | 2.0% | 1-3% | CPI YoY | 1990 | RBNZ targets midpoint over medium term |

### Target Analysis Output

The workflow provides:

```json
"target_analysis": {
  "regions_above_target": ["usa", "uk"],
  "regions_at_target": ["euro_area"],
  "regions_below_target": [],
  "sticky_inflation": ["usa"],
  "notes": "Fed targets 2% PCE (not CPI) - CPI typically runs ~0.5pp higher"
}
```

**Distance from Target:**
Each region's ranking includes `distance_from_target` (in percentage points):
- `+0.5` = 0.5pp above target
- `-0.3` = 0.3pp below target
- `null` = no formal target

**Sticky Inflation Detection:**
Regions flagged if inflation >3% for 6+ consecutive months.

## Comparability Warnings

The workflow automatically generates warnings based on region combinations:

### Warning Types

1. **Mixed Index Types**
   ```
   "Mixed index types: CPI (usa, canada), HICP (euro_area, germany) - see methodological notes"
   ```
   Triggered when comparing HICP and CPI countries.

2. **Owner Housing Differences**
   ```
   "Owner-occupied housing: included in usa, uk but excluded in euro_area, germany"
   ```
   Highlights ~20-25% basket coverage difference.

3. **Canada Mortgage Interest**
   ```
   "Canada includes mortgage interest costs (~4-6% of basket), unique among major economies"
   ```
   Flags Canada's distinct methodology.

4. **Frequency Mismatches**
   ```
   "Frequency mismatch: usa (Monthly), new_zealand (Quarterly) - alignment may reduce data points"
   ```
   Warns when mixing monthly and quarterly data.

5. **Quality Adjustment Differences**
   ```
   "Sweden uses more extensive hedonic quality adjustments for electronics - may lower measured inflation"
   ```
   Notes significant methodological variations.

### Minimizing Comparability Issues

**Best Practice**: Compare only HICP countries for Euro Area analysis:

```python
# Maximum comparability - all HICP, all exclude owner housing
compare_inflation_across_regions(regions=["eurozone_core"])
# Germany, France, Netherlands - all HICP

compare_inflation_across_regions(regions=["euro_area", "germany", "spain", "italy"])
# All HICP countries - minimal comparability warnings
```

## Base Effects Detection

The workflow detects potential base effects - temporary distortions in YoY inflation from prior-year events.

### Detection Logic

Identifies patterns like:
1. **Sharp drop** (>1.5pp decline in 2 months)
2. **Followed by sharp rise** (>1.5pp increase within 6 months)

### Common Causes

- **VAT rate changes** (e.g., Germany's temporary VAT cut in 2020)
- **Energy subsidies unwinding** (e.g., various European energy support measures)
- **Statistical anomalies** from pandemic, lockdowns, etc.

### Example Warning

```json
"comparability_warnings": [
  "Potential base effect detected in euro_area: sharp inflation drop in 2024-07 followed by rise in 2024-11. May indicate VAT change or subsidy unwinding."
]
```

### Interpretation

Base effects are **temporary** distortions that:
- Make YoY % changes look dramatic
- Don't reflect underlying inflation pressure
- Typically reverse after 12 months

## Use Cases & Examples

### Use Case 1: G7 Inflation Comparison

**Scenario**: Compare current inflation across all G7 countries.

**Request:**
```python
compare_inflation_across_regions(
    regions=["g7"]
)
```

**Note**: G7 has 7 countries but MVP limit is 5, so first 5 will be used: USA, Canada, UK, Germany, France.

**Comparability Issues**:
- Mixed HICP (Germany, France) and CPI (USA, Canada, UK)
- Owner housing treatment varies
- Canada includes mortgage interest costs

**Best Practice**: Split into groups:
```python
# North America
compare_inflation_across_regions(regions=["usa", "canada", "mexico"])

# Europe
compare_inflation_across_regions(regions=["eurozone_core", "uk"])

# Asia
compare_inflation_across_regions(regions=["japan", "south_korea", "china"])
```

### Use Case 2: Euro Area Core vs Periphery

**Scenario**: Compare inflation dynamics between core and peripheral Euro Area economies.

**Request:**
```python
compare_inflation_across_regions(
    regions=["eurozone_core", "eurozone_periphery"],
    metric="all"
)
```

**Expands To**:
- Core: Germany, France, Netherlands
- Periphery: Italy, Spain, Portugal, Greece
- Total: 7 countries (will be truncated to 5)

**Comparability**: All HICP - maximum comparability!

**Analysis Focus**:
- Convergence/divergence within Euro Area
- Distance from ECB's 2% target
- Trend differences (periphery often lags core)

### Use Case 3: Fed vs ECB vs BoE Inflation Targeting

**Scenario**: Compare inflation relative to central bank targets for major developed economies.

**Request:**
```python
compare_inflation_across_regions(
    regions=["usa", "euro_area", "uk"],
    metric="latest"
)
```

**Target Analysis Output**:
```json
"target_analysis": {
  "regions_above_target": ["usa"],
  "regions_at_target": ["euro_area", "uk"],
  "notes": "Fed targets 2% PCE (not CPI) - CPI typically runs ~0.5pp higher"
}
```

**Key Insight**: USA CPI at 3.0% is ~1.0pp above target, but since Fed targets PCE (not CPI), effective deviation is ~0.5pp (CPI-PCE spread).

### Use Case 4: Emerging vs Developed Market Inflation

**Scenario**: Compare inflation in emerging markets (BRICS) vs developed (G7 subset).

**Request:**
```python
# Developed
compare_inflation_across_regions(regions=["usa", "euro_area", "uk", "japan"])

# Emerging
compare_inflation_across_regions(regions=["brazil", "india", "south_africa", "turkey"])
```

**Comparability Issues**:
- BRICS countries often have:
  - Higher average inflation targets (e.g., Brazil 3.25%, India 4%)
  - Different basket compositions (higher food weight)
  - Less frequent data updates
  - More volatility

**Limitation**: Cannot directly compare in one call due to 5-region MVP limit.

### Use Case 5: Inflation Trends Over 5 Years

**Scenario**: Analyze long-term inflation trends for USA, Euro Area, UK.

**Request:**
```python
compare_inflation_across_regions(
    regions=["usa", "euro_area", "uk"],
    start_date="2020-01-01",
    metric="all"
)
```

**Returns**:
- Full trend analysis with linear regression slopes
- Convergence analysis (CV comparison over time)
- 24 most recent data points for time series graphing
- Sticky inflation detection (if >3% for 6+ months)

**Use Time Series For**:
- Plotting inflation trajectories
- Identifying pandemic spike and normalization
- Visualizing convergence/divergence

### Use Case 6: Current Snapshot for Dashboard

**Scenario**: Quick status check for live dashboard showing latest inflation rates.

**Request:**
```python
compare_inflation_across_regions(
    regions=["usa", "euro_area", "uk", "japan", "canada"],
    metric="latest"
)
```

**Returns**:
- Latest value per region
- Ranking (lowest to highest)
- Distance from central bank targets
- Basic statistics (mean, spread, std)
- Minimal time series data

**Performance**: Optimized for speed, <1.5s typical latency.

## Error Handling

### Invalid Regions

```python
compare_inflation_across_regions(regions=["invalid_region", "usa"])
```

**Behavior**:
- Invalid regions filtered out
- Proceeds with valid regions if any remain
- Returns error if all regions invalid

### No Common Dates

```python
compare_inflation_across_regions(
    regions=["usa", "new_zealand"],
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

**Behavior**:
- If USA monthly data doesn't align with New Zealand quarterly data
- Returns error: "No common dates after alignment"

**Solution**: Expand date range or use countries with same frequency.

### Region Limit Exceeded

```python
compare_inflation_across_regions(regions=["g7"])  # 7 countries
```

**Behavior**:
- Automatically truncates to first 5 regions
- Notes in metadata: `"regions_expanded": ["usa", "canada", "uk", "germany", "france"]`
- Logs warning

### API Failures

```python
# If FRED API returns errors for some regions
compare_inflation_across_regions(regions=["usa", "euro_area", "uk"])
```

**Behavior**:
- Fetches data for regions that succeed
- Proceeds with partial data if ≥2 regions succeed
- Returns error if <2 regions have data

## Performance Optimization

### Parallel Fetching

```python
# Fetches all regions concurrently using ThreadPoolExecutor
compare_inflation_across_regions(regions=["usa", "euro_area", "uk", "japan", "canada"])
```

**Performance**: ~1.5s for 5 regions (vs ~5s sequential)

### Caching

Leverages v0.1.9 tool caching:
- Series observations cached for 15 minutes
- Subsequent calls with same parameters hit cache
- Reduces API load and improves latency

### Response Size Management

Time series truncated to 24 most recent points:
- Sufficient for graphing recent trends
- Prevents response bloat
- Use `download_for_analysis` workflow for full data export

## Graphing & Visualization

The `time_series` array is optimized for graphing:

```json
"time_series": [
  {"date": "2024-10-01", "usa": 3.50, "euro_area": 2.80, "uk": 2.90},
  {"date": "2024-11-01", "usa": 3.30, "euro_area": 2.60, "uk": 2.70},
  ...
]
```

**Visualization Ideas:**

1. **Line Chart**: Inflation trajectories by country
2. **Bar Chart**: Latest value ranking with target lines
3. **Scatter Plot**: Spread vs mean over time
4. **Heatmap**: Distance from target by country and month
5. **Convergence Plot**: CV (coefficient of variation) over time

**JavaScript Example (Chart.js)**:
```javascript
const data = {
  labels: timeSeriesData.map(d => d.date),
  datasets: [
    {
      label: 'USA',
      data: timeSeriesData.map(d => d.usa),
      borderColor: 'blue'
    },
    {
      label: 'Euro Area',
      data: timeSeriesData.map(d => d.euro_area),
      borderColor: 'orange'
    }
  ]
};
```

**Python Example (matplotlib)**:
```python
import matplotlib.pyplot as plt
import pandas as pd

df = pd.DataFrame(time_series)
df.plot(x='date', y=['usa', 'euro_area', 'uk'])
plt.axhline(y=2.0, color='r', linestyle='--', label='2% Target')
plt.ylabel('Inflation (% YoY)')
plt.title('Inflation Comparison')
plt.legend()
plt.show()
```

## Limitations & Caveats

### 1. No PPP Adjustment

**Limitation**: Compares nominal inflation rates, not purchasing power parity adjusted.

**Impact**: Doesn't account for price level differences between countries.

**Example**: 3% inflation in USA and 3% in India represent different absolute price changes.

**Mitigation**: Use OECD PPP data separately if needed.

### 2. CPI vs HICP Methodological Differences

**Limitation**: ~20-25% basket coverage difference for owner housing.

**Impact**: Euro Area (HICP, no housing) may show lower inflation than USA (CPI, with housing) even if underlying pressures similar.

**Mitigation**: Workflow flags this in comparability warnings. Consider HICP-only comparisons for Euro Area.

### 3. Central Bank Target Measure Mismatch

**Limitation**: Fed targets PCE (2%), not CPI. Workflow shows CPI data.

**Impact**: USA CPI typically ~0.5pp higher than PCE target.

**Mitigation**: Workflow notes this in target analysis. Interpret USA distance_from_target with caution.

### 4. MVP Region Limit (5 regions)

**Limitation**: Maximum 5 regions for performance.

**Impact**: Cannot compare all G7 (7) or G20 (20) in single call.

**Mitigation**: Split into multiple calls or use region presets strategically.

### 5. Time Series Truncation (24 points)

**Limitation**: Response includes only 24 most recent data points.

**Impact**: Cannot analyze long-term trends (5+ years) from time series alone.

**Mitigation**: Use `download_for_analysis` workflow (v0.2.0 planned) for full data export.

### 6. Base Effects Detection Limitations

**Limitation**: Statistical detection may miss policy-driven base effects.

**Impact**: Some VAT changes or subsidies may not trigger warnings.

**Mitigation**: Review comparability warnings and cross-reference with known policy changes.

## Best Practices

### 1. Choose Comparable Regions

**Good**:
```python
# All HICP - maximum comparability
compare_inflation_across_regions(regions=["euro_area", "germany", "france", "italy"])
```

**Less Ideal**:
```python
# Mixed HICP/CPI - less comparable
compare_inflation_across_regions(regions=["usa", "euro_area", "uk", "canada"])
```

### 2. Review Metadata and Warnings

Always check:
- `metadata.series_used[]` for index types and methodological notes
- `comparability_warnings` for interpretation caveats
- `target_analysis` for central bank adherence

### 3. Use Appropriate Time Ranges

**Short-term** (1-2 years):
```python
compare_inflation_across_regions(
    regions=["usa", "euro_area"],
    start_date="2023-01-01"
)
```

**Long-term** (5+ years):
```python
compare_inflation_across_regions(
    regions=["usa", "euro_area"],
    start_date="2020-01-01",
    metric="all"
)
```

### 4. Combine with v0.1.9 Tools for Deep Dives

Use workflow for overview, then drill down:
```python
# 1. Overview with workflow
overview = compare_inflation_across_regions(regions=["usa", "euro_area", "uk"])

# 2. Deep dive on specific series with v0.1.9 tools
usa_detailed = get_series_observations(
    series_id="CPIAUCSL",
    observation_start="2015-01-01",
    units="lin"  # Levels, not YoY %
)
```

## Changelog

### 2025-11-02 - v0.2.0 Inflation-Focused Release
- **Breaking**: Renamed from `compare_across_regions` to `compare_inflation_across_regions`
- **Breaking**: Removed `indicator` parameter (inflation-only now)
- **New**: HICP prioritization for European countries
- **New**: Central bank inflation target analysis with distance_from_target
- **New**: Comparability warnings (HICP vs CPI, housing, frequency)
- **New**: Base effects detection (VAT changes, subsidy unwinding)
- **New**: Sticky inflation detection (>3% for 6+ months)
- **New**: Rich metadata per series (index_type, includes_owner_housing, methodological_notes)
- **New**: Target analysis (regions_above_target, regions_at_target, sticky_inflation)
- **Improved**: Documentation with OECD/IMF/Eurostat best practices
- **Tests**: 127 passing tests (54 mappings + 33 workflow + 40 calculations)

### 2025-11-01 - v0.2.0 Initial Generic Workflow (Deprecated)
- Generic `compare_across_regions` workflow
- Supported multiple indicators (inflation, unemployment, GDP, interest_rates)
- Limited inflation-specific features

---

**Maintained By:** TrabajoIA Server Team
**Last Updated:** 2025-11-02
**Version:** 2.0.0 (Inflation-Focused)
