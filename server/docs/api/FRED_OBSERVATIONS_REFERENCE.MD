# FRED Series Observations Tool – API Reference
## Tool: get_fred_series_observations

**Endpoint:** `https://api.stlouisfed.org/fred/series/observations`

**Description:** Get observations or data values for an economic data series. This is the primary tool for retrieving actual historical time-series data from FRED.

---

## Table of Contents

1. [Overview](#overview)
2. [Parameters](#parameters)
3. [Response Format](#response-format)
4. [Usage Examples](#usage-examples)
5. [Use Cases](#use-cases)
6. [Data Transformations](#data-transformations)
7. [Frequency Aggregation](#frequency-aggregation)
8. [Error Handling](#error-handling)
9. [Performance](#performance)
10. [Best Practices](#best-practices)
11. [Related Tools](#related-tools)

---

## Overview

The `get_fred_series_observations` tool retrieves historical observations (data points) for economic data series from the Federal Reserve Economic Data (FRED) database. This is the core tool for obtaining actual time-series data for analysis.

### Key Features

- **Complete Historical Data**: Get all available observations for any FRED series
- **Date Range Filtering**: Specify exact start and end dates for your analysis period
- **Data Transformations**: Apply 9 different transformations (percent change, log, etc.)
- **Frequency Aggregation**: Convert high-frequency data to lower frequencies (daily to monthly, etc.)
- **Vintage Data Support**: Access historical revisions and real-time data
- **Large Dataset Support**: Handle up to 100,000 observations per request
- **AI-Optimized**: Compact JSON format, fast responses

---

## Parameters

### Required Parameters

#### `series_id` (string, REQUIRED)

The ID for a FRED series.

**Format:** `"SERIES_ID"`

**Examples:**
```python
"GNPCA"     # Gross National Product
"GDP"       # Gross Domestic Product
"UNRATE"    # Unemployment Rate
"CPIAUCSL"  # Consumer Price Index
"DFF"       # Federal Funds Rate
```

**Important Notes:**
- Series ID is case-sensitive
- Must be valid FRED series identifier
- Can be found using `search_fred_series` tool

---

### Optional Date Parameters

#### `observation_start` (string, optional)

Start date for observations.

**Default:** `"1776-07-04"` (earliest available)

**Format:** `"YYYY-MM-DD"`

**Examples:**
```python
observation_start="2020-01-01"    # Start from Jan 2020
observation_start="2015-06-15"    # Start from mid-2015
```

#### `observation_end` (string, optional)

End date for observations.

**Default:** `"9999-12-31"` (latest available)

**Format:** `"YYYY-MM-DD"`

**Examples:**
```python
observation_end="2023-12-31"    # End at Dec 2023
observation_end="2021-03-31"    # End at Q1 2021
```

#### `realtime_start` (string, optional)

Start date for real-time period.

**Default:** Today's date

**Format:** `"YYYY-MM-DD"`

**Purpose:** Access historical metadata/revisions

#### `realtime_end` (string, optional)

End date for real-time period.

**Default:** Today's date

**Format:** `"YYYY-MM-DD"`

**Purpose:** Access historical metadata/revisions

---

### Optional Control Parameters

#### `limit` (integer, optional)

Maximum number of observations to return.

**Default:** `100000`

**Range:** 1-100000

**Examples:**
```python
limit=100     # Get last 100 observations
limit=1000    # Get last 1000 observations
limit=100000  # Get all observations (default)
```

#### `offset` (integer, optional)

Starting offset for pagination.

**Default:** `0`

**Range:** 0+

**Examples:**
```python
offset=0      # Start from beginning
offset=100    # Skip first 100, start from 101
```

#### `sort_order` (string, optional)

Sort order by observation date.

**Default:** `"asc"` (oldest first)

**Valid Values:**
- `"asc"` - Ascending (chronological, oldest to newest)
- `"desc"` - Descending (reverse chronological, newest to oldest)

**Examples:**
```python
sort_order="asc"     # 1929, 1930, 1931... (chronological)
sort_order="desc"    # 2023, 2022, 2021... (most recent first)
```

---

### Data Transformation Parameters

#### `units` (string, optional)

Data value transformation to apply.

**Default:** `"lin"` (no transformation)

**Valid Values:**
- `"lin"` - Levels (no transformation)
- `"chg"` - Change
- `"ch1"` - Change from Year Ago
- `"pch"` - Percent Change
- `"pc1"` - Percent Change from Year Ago
- `"pca"` - Compounded Annual Rate of Change
- `"cch"` - Continuously Compounded Rate of Change
- `"cca"` - Continuously Compounded Annual Rate of Change
- `"log"` - Natural Log

**Examples:**
```python
units="lin"    # Original values
units="pch"    # Percent change from previous period
units="pc1"    # Year-over-year percent change
units="log"    # Natural log transformation
```

**Use Cases by Transformation:**
- `"lin"`: Raw data analysis, levels comparison
- `"pch"`: Period-to-period growth rates
- `"pc1"`: Year-over-year growth, removes seasonality
- `"log"`: Growth rates, stabilize variance

---

### Frequency Aggregation Parameters

#### `frequency` (string, optional)

Lower frequency to aggregate values to.

**Default:** None (no aggregation)

**Valid Values:**

**Simple Frequencies:**
- `"d"` - Daily
- `"w"` - Weekly (defaults to ending Friday)
- `"bw"` - Biweekly (defaults to ending Wednesday)
- `"m"` - Monthly
- `"q"` - Quarterly
- `"sa"` - Semiannual
- `"a"` - Annual

**Weekly Variants (specific end days):**
- `"wef"` - Weekly, Ending Friday
- `"weth"` - Weekly, Ending Thursday
- `"wew"` - Weekly, Ending Wednesday
- `"wetu"` - Weekly, Ending Tuesday
- `"wem"` - Weekly, Ending Monday
- `"wesu"` - Weekly, Ending Sunday
- `"wesa"` - Weekly, Ending Saturday

**Biweekly Variants:**
- `"bwew"` - Biweekly, Ending Wednesday
- `"bwem"` - Biweekly, Ending Monday

**Examples:**
```python
frequency="m"     # Aggregate daily data to monthly
frequency="q"     # Aggregate monthly data to quarterly
frequency="a"     # Aggregate to annual
```

**Important Notes:**
- Cannot aggregate to higher frequency than native
- If frequency matches native, no aggregation occurs
- Most useful for daily → weekly/monthly conversions

#### `aggregation_method` (string, optional)

Method to use for frequency aggregation.

**Default:** `"avg"`

**Valid Values:**
- `"avg"` - Average (mean of values in period)
- `"sum"` - Sum (total of values in period)
- `"eop"` - End of Period (last value in period)

**Examples:**
```python
aggregation_method="avg"    # Average daily values to monthly
aggregation_method="sum"    # Sum daily values to monthly
aggregation_method="eop"    # Use last day value for month
```

**Best Practices:**
- Use `"avg"` for: Rates, prices, indexes
- Use `"sum"` for: Volumes, quantities, counts
- Use `"eop"` for: Stock variables, balances

---

### Output Format Parameters

#### `output_type` (integer, optional)

Output format for observations.

**Default:** `1`

**Valid Values:**
- `1` - Observations by Real-Time Period (most common)
- `2` - Observations by Vintage Date, All Observations
- `3` - Observations by Vintage Date, New and Revised Only
- `4` - Observations, Initial Release Only

**Examples:**
```python
output_type=1    # Standard current data
output_type=2    # All historical revisions
output_type=4    # Only first-published values
```

**Use Cases:**
- Type 1: Standard analysis with current data
- Type 2: Study data revisions over time
- Type 3: Track which values changed
- Type 4: Real-time forecasting research

---

## Response Format

### Success Response

```json
{
  "tool": "get_series_observations",
  "data": [
    {
      "realtime_start": "2013-08-14",
      "realtime_end": "2013-08-14",
      "date": "1929-01-01",
      "value": "1065.9"
    },
    {
      "realtime_start": "2013-08-14",
      "realtime_end": "2013-08-14",
      "date": "1930-01-01",
      "value": "975.5"
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "series_id": "GNPCA",
    "realtime_start": "2013-08-14",
    "realtime_end": "2013-08-14",
    "observation_start": "1776-07-04",
    "observation_end": "9999-12-31",
    "units": "lin",
    "frequency": null,
    "aggregation_method": "avg",
    "output_type": 1,
    "order_by": "observation_date",
    "sort_order": "asc",
    "total_count": 84,
    "returned_count": 84,
    "limit": 100000,
    "offset": 0
  }
}
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| `realtime_start` | string | Start of real-time period (when data was valid) |
| `realtime_end` | string | End of real-time period |
| `date` | string | Observation date (YYYY-MM-DD) |
| `value` | string | Observation value (string to preserve precision) |

**Note:** Value is string type to:
- Preserve exact precision from FRED
- Handle special values like "." (missing data)
- Avoid floating-point rounding issues

---

## Usage Examples

### Example 1: Basic Usage - Get All GDP Data

**Goal:** Retrieve all historical GDP observations.

```python
result = get_fred_series_observations("GDP")
```

**Result:**
```json
{
  "data": [
    {"date": "1947-01-01", "value": "243.164"},
    {"date": "1947-04-01", "value": "245.968"},
    ...
  ],
  "metadata": {
    "series_id": "GDP",
    "total_count": 308,
    "units": "lin"
  }
}
```

**Insight:** GDP has quarterly data from 1947 to present (308 observations).

---

### Example 2: Recent Data Only

**Goal:** Get unemployment rate for last 5 years.

```python
result = get_fred_series_observations(
    "UNRATE",
    observation_start="2019-01-01",
    observation_end="2023-12-31"
)
```

**Result:**
```json
{
  "data": [
    {"date": "2019-01-01", "value": "3.9"},
    {"date": "2019-02-01", "value": "3.8"},
    ...
    {"date": "2023-12-01", "value": "3.7"}
  ],
  "metadata": {
    "returned_count": 60
  }
}
```

**Insight:** 60 monthly observations from 2019-2023.

---

### Example 3: Year-over-Year Percent Change

**Goal:** Get CPI with year-over-year percent change (inflation rate).

```python
result = get_fred_series_observations(
    "CPIAUCSL",
    units="pc1",
    observation_start="2020-01-01"
)
```

**Result:**
```json
{
  "data": [
    {"date": "2021-01-01", "value": "1.4"},
    {"date": "2022-01-01", "value": "7.5"},
    {"date": "2023-01-01", "value": "6.4"}
  ],
  "metadata": {
    "units": "pc1"
  }
}
```

**Insight:** Shows inflation rate directly without manual calculation.

---

### Example 4: Aggregate Daily to Monthly

**Goal:** Convert Federal Funds Rate (daily) to monthly average.

```python
result = get_fred_series_observations(
    "DFF",
    frequency="m",
    aggregation_method="avg",
    observation_start="2023-01-01"
)
```

**Result:**
```json
{
  "data": [
    {"date": "2023-01-01", "value": "4.57"},
    {"date": "2023-02-01", "value": "4.65"},
    {"date": "2023-03-01", "value": "4.78"}
  ],
  "metadata": {
    "frequency": "m",
    "aggregation_method": "avg"
  }
}
```

**Insight:** Daily rates aggregated to monthly averages automatically.

---

### Example 5: Recent Values Only (Limit)

**Goal:** Get last 12 months of data, newest first.

```python
result = get_fred_series_observations(
    "UNRATE",
    limit=12,
    sort_order="desc"
)
```

**Result:**
```json
{
  "data": [
    {"date": "2023-10-01", "value": "3.9"},
    {"date": "2023-09-01", "value": "3.8"},
    ...
    {"date": "2022-11-01", "value": "3.6"}
  ],
  "metadata": {
    "returned_count": 12,
    "sort_order": "desc"
  }
}
```

**Insight:** Most recent 12 observations in reverse chronological order.

---

### Example 6: Natural Log Transformation

**Goal:** Get log-transformed GDP for growth rate analysis.

```python
result = get_fred_series_observations(
    "GDP",
    units="log",
    observation_start="2000-01-01"
)
```

**Result:**
```json
{
  "data": [
    {"date": "2000-01-01", "value": "9.185"},
    {"date": "2000-04-01", "value": "9.198"}
  ],
  "metadata": {
    "units": "log"
  }
}
```

**Insight:** Log transformation useful for constant growth rate analysis.

---

### Example 7: Quarterly Aggregation with Sum

**Goal:** Aggregate monthly retail sales to quarterly totals.

```python
result = get_fred_series_observations(
    "RSXFS",
    frequency="q",
    aggregation_method="sum",
    observation_start="2020-01-01"
)
```

**Result:**
```json
{
  "data": [
    {"date": "2020-01-01", "value": "1425.3"},
    {"date": "2020-04-01", "value": "1134.7"}
  ],
  "metadata": {
    "frequency": "q",
    "aggregation_method": "sum"
  }
}
```

**Insight:** Quarterly sales totals from monthly data.

---

## Use Cases

### 1. Time Series Analysis

**Problem:** Need historical data for econometric modeling.

**Solution:**
```python
# Get complete dataset
gdp_data = get_fred_series_observations("GDP")

# Process for analysis
import json
data = json.loads(gdp_data)
observations = data["data"]

# Extract dates and values
dates = [obs["date"] for obs in observations]
values = [float(obs["value"]) for obs in observations]

# Now ready for pandas, numpy, statistical analysis
```

**Benefits:**
- Complete historical record
- Consistent date format
- Ready for statistical packages

---

### 2. Dashboard Recent Data

**Problem:** Dashboard needs latest economic indicators.

**Solution:**
```python
# Get last 3 months of key indicators
unemployment = get_fred_series_observations("UNRATE", limit=3, sort_order="desc")
inflation = get_fred_series_observations("CPIAUCSL", units="pc1", limit=12, sort_order="desc")
gdp = get_fred_series_observations("GDP", limit=4, sort_order="desc")

# Display latest values
```

**Benefits:**
- Fast queries (limited data)
- Always current
- Multiple indicators

---

### 3. Year-over-Year Comparison

**Problem:** Compare current vs. year-ago values.

**Solution:**
```python
# Get with year-over-year transformation
yoy_change = get_fred_series_observations(
    "RETAILSA",
    units="ch1",  # Change from year ago
    observation_start="2020-01-01"
)

# Or get percent change
yoy_pct = get_fred_series_observations(
    "RETAILSA",
    units="pc1",  # Percent change from year ago
    observation_start="2020-01-01"
)
```

**Benefits:**
- No manual calculation needed
- Removes seasonality automatically
- Standard year-over-year format

---

### 4. Data Frequency Conversion

**Problem:** Need monthly averages of daily rates.

**Solution:**
```python
# Convert daily Federal Funds Rate to monthly
monthly_ffr = get_fred_series_observations(
    "DFF",
    frequency="m",
    aggregation_method="avg",
    observation_start="2020-01-01"
)

# Convert to quarterly average
quarterly_ffr = get_fred_series_observations(
    "DFF",
    frequency="q",
    aggregation_method="avg",
    observation_start="2020-01-01"
)
```

**Benefits:**
- Automatic aggregation
- Consistent with FRED methodology
- Multiple frequency options

---

### 5. Historical Revisions Analysis

**Problem:** Study how GDP data gets revised over time.

**Solution:**
```python
# Get all vintage data
all_vintages = get_fred_series_observations(
    "GDP",
    output_type=2,  # All observations by vintage
    observation_start="2020-01-01",
    observation_end="2020-12-31"
)

# Get only initial releases
initial_only = get_fred_series_observations(
    "GDP",
    output_type=4,  # Initial releases only
    observation_start="2020-01-01",
    observation_end="2020-12-31"
)

# Compare to see revisions
```

**Benefits:**
- Real-time data research
- Revision analysis
- Forecasting accuracy studies

---

## Data Transformations

### Transformation Formulas

**Change (`chg`):**
```
value[t] - value[t-1]
```

**Change from Year Ago (`ch1`):**
```
value[t] - value[t-n]  # where n = observations in 1 year
```

**Percent Change (`pch`):**
```
((value[t] - value[t-1]) / value[t-1]) * 100
```

**Percent Change from Year Ago (`pc1`):**
```
((value[t] - value[t-n]) / value[t-n]) * 100
```

**Compounded Annual Rate of Change (`pca`):**
```
(((value[t] / value[t-1]) ^ (n/t)) - 1) * 100
```

**Continuously Compounded Rate of Change (`cch`):**
```
(log(value[t]) - log(value[t-1])) * 100
```

**Continuously Compounded Annual Rate of Change (`cca`):**
```
((log(value[t]) - log(value[t-n])) / n) * 100
```

**Natural Log (`log`):**
```
log(value[t])
```

### When to Use Each Transformation

| Transformation | Best For | Example Use Case |
|----------------|----------|------------------|
| `lin` | Level analysis | GDP in billions |
| `chg` | Absolute changes | Employment change |
| `ch1` | Year-over-year change | Seasonal comparison |
| `pch` | Growth rates | Quarter-to-quarter growth |
| `pc1` | Annual growth rates | Inflation rate |
| `pca` | Annualized rates | Quarterly to annual |
| `cch` | Continuous growth | Finance applications |
| `cca` | Annualized continuous | Long-term growth |
| `log` | Proportional growth | Volatility stabilization |

---

## Frequency Aggregation

### Supported Conversions

✅ **Allowed:**
- Daily → Weekly, Monthly, Quarterly, Annual
- Weekly → Monthly, Quarterly, Annual
- Monthly → Quarterly, Annual
- Quarterly → Annual

❌ **Not Allowed:**
- Monthly → Daily (cannot create higher frequency)
- Annual → Quarterly (cannot disaggregate)

### Aggregation Method Guidelines

**Average (`avg`):**
- **Use for:** Interest rates, unemployment rate, price indexes
- **Example:** Daily Fed Funds Rate → Monthly average

**Sum (`sum`):**
- **Use for:** Sales volumes, production quantities, revenues
- **Example:** Monthly retail sales → Quarterly total

**End of Period (`eop`):**
- **Use for:** Stock variables, account balances, population
- **Example:** Weekly stock price → Monthly closing value

---

## Error Handling

### Common Errors

#### Invalid Series ID

**Error:**
```json
{
  "tool": "get_series_observations",
  "error": "Series not found: INVALID",
  "series_id": "INVALID"
}
```

**Cause:** Series ID doesn't exist in FRED

**Fix:**
```python
# Search for series first
from trabajo_ia_server.tools.fred.search_series import search_fred_series
results = search_fred_series("your search term")
# Use valid series_id from results
```

---

#### Invalid Date Format

**Error:**
```json
{
  "error": "Invalid parameters: observation_start date format is invalid"
}
```

**Cause:** Date not in YYYY-MM-DD format

**Fix:**
```python
# Bad
observation_start="01/01/2020"

# Good
observation_start="2020-01-01"
```

---

#### Invalid Transformation for Negative Values

**Error:**
```json
{
  "error": "Invalid parameters: cannot apply log transformation to negative values"
}
```

**Cause:** Trying to use `log` or percentage transformations on series with negative values

**Fix:**
```python
# Don't use log/pch on series that can be negative
# Use chg or ch1 instead
result = get_fred_series_observations("BALANCE", units="chg")
```

---

#### Frequency Aggregation Incompatible

**Error:**
```json
{
  "error": "Invalid parameters: cannot aggregate to higher frequency"
}
```

**Cause:** Trying to convert monthly data to daily

**Fix:**
```python
# Can only aggregate DOWN in frequency
# Monthly → Quarterly is OK
# Monthly → Daily is NOT OK
```

---

## Performance

### Response Time

- **Typical:** 0.5-2.0 seconds
- **Large datasets (10,000+ obs):** 1.0-3.0 seconds
- **With transformations:** +0.2-0.5 seconds
- **With aggregation:** +0.3-0.7 seconds

### Optimization Tips

1. **Limit date ranges for faster queries:**
```python
# Instead of all data
get_fred_series_observations("GDP")

# Use specific range
get_fred_series_observations(
    "GDP",
    observation_start="2020-01-01"
)
```

2. **Use limit for recent data:**
```python
# Get last 100 observations only
get_fred_series_observations("UNRATE", limit=100, sort_order="desc")
```

3. **Apply transformations server-side:**
```python
# Let FRED calculate (faster)
get_fred_series_observations("CPI", units="pc1")

# Instead of downloading raw data and calculating
```

### Token Efficiency

**Compact JSON format saves ~25% tokens:**
- 100 observations: ~3,000 tokens
- 1,000 observations: ~25,000 tokens
- 10,000 observations: ~230,000 tokens

**For AI/LLM applications:**
- Limit to needed observations
- Use date ranges
- Consider sampling for large datasets

---

## Best Practices

### 1. Always Specify Date Ranges

```python
# Good - explicit date range
get_fred_series_observations(
    "GDP",
    observation_start="2020-01-01",
    observation_end="2023-12-31"
)

# Bad - downloads all data unnecessarily
get_fred_series_observations("GDP")
```

### 2. Use Appropriate Transformations

```python
# For inflation rate
get_fred_series_observations("CPIAUCSL", units="pc1")

# For GDP growth rate
get_fred_series_observations("GDP", units="pch")

# For log-linear trends
get_fred_series_observations("GDP", units="log")
```

### 3. Handle Missing Values

```python
import json

result = get_fred_series_observations("SERIES_ID")
data = json.loads(result)

# Filter out missing values (represented as ".")
valid_obs = [obs for obs in data["data"] if obs["value"] != "."]
```

### 4. Use Frequency Aggregation Wisely

```python
# Good - appropriate aggregation
get_fred_series_observations(
    "DFF",           # Daily data
    frequency="m",   # To monthly
    aggregation_method="avg"  # Average the daily rates
)

# Good - sum for flow variables
get_fred_series_observations(
    "RETAILSA",      # Monthly sales
    frequency="q",   # To quarterly
    aggregation_method="sum"  # Sum the monthly totals
)
```

### 5. Check Metadata

```python
result = get_fred_series_observations("GDP")
data = json.loads(result)

# Always check metadata
print(f"Retrieved: {data['metadata']['returned_count']} observations")
print(f"Date range: {data['metadata']['observation_start']} to {data['metadata']['observation_end']}")
print(f"Units: {data['metadata']['units']}")
```

---

## Related Tools

### Complementary Tools

1. **`search_fred_series`**
   - Find series before getting observations
   - Discover series IDs
   - **Use BEFORE** `get_fred_series_observations`

2. **`get_fred_series_tags`**
   - Understand series characteristics
   - Check frequency, units, geography
   - **Use TO VERIFY** series before downloading data

3. **`get_fred_tags`**
   - Discover available tags
   - Filter by data type
   - **Use FOR** data discovery

### Typical Workflow

```python
# Step 1: Search for series
search_results = search_fred_series("unemployment rate")
# Find series_id: "UNRATE"

# Step 2: Check series metadata
tags = get_fred_series_tags("UNRATE")
# Verify: monthly, seasonally adjusted

# Step 3: Get observations
observations = get_fred_series_observations(
    "UNRATE",
    observation_start="2020-01-01"
)

# Step 4: Analyze data
import json
data = json.loads(observations)
for obs in data["data"][:5]:
    print(f"{obs['date']}: {obs['value']}%")
```

---

## Version Information

- **Tool Version:** Introduced in v0.1.7 (planned)
- **FRED API Version:** Uses FRED API `/fred/series/observations` endpoint
- **Last Updated:** 2025-11-01

---

## Support & Resources

- **FRED API Documentation:** https://fred.stlouisfed.org/docs/api/fred/
- **Endpoint Docs:** https://fred.stlouisfed.org/docs/api/fred/series_observations.html
- **Transformation Formulas:** https://alfred.stlouisfed.org/help#growth_formulas
- **FRED Homepage:** https://fred.stlouisfed.org/

---

## Summary

The `get_fred_series_observations` tool is essential for:

✅ **Retrieving actual economic data** for analysis
✅ **Time-series analysis** with complete historical records
✅ **Data transformation** with 9 built-in options
✅ **Frequency conversion** from high to low frequency
✅ **Real-time data research** with vintage support

**Key Strengths:**
- Complete, accurate FRED data
- Flexible date range filtering
- Powerful transformations
- Frequency aggregation
- AI-optimized compact JSON

**Best For:**
- Econometric analysis
- Dashboard data feeds
- Historical research
- Growth rate calculations
- Time-series modeling

**Remember:**
- Always specify date ranges when possible
- Choose appropriate transformations for your analysis
- Handle missing values (represented as ".")
- Use frequency aggregation wisely
- Check metadata before processing
