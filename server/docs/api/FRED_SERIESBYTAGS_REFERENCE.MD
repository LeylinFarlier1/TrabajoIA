# FRED Series by Tags API Reference

**Tool Name:** `get_fred_series_by_tags`
**Version:** 0.1.4
**FRED Endpoint:** `/fred/tags/series`
**Status:** ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Parameters](#parameters)
3. [Response Format](#response-format)
4. [Usage Examples](#usage-examples)
5. [Use Cases](#use-cases)
6. [Error Handling](#error-handling)
7. [Performance](#performance)
8. [Best Practices](#best-practices)
9. [Related Tools](#related-tools)

---

## Overview

The `get_fred_series_by_tags` tool retrieves FRED economic data series that match **ALL** specified tags and **NONE** of the excluded tags. This provides precise, tag-based filtering for discovering relevant economic indicators.

### Key Features

- **AND Logic for Required Tags:** Series must have ALL tags in `tag_names`
- **NOT Logic for Excluded Tags:** Series must have NONE of the tags in `exclude_tag_names`
- **12 Sort Options:** Sort by series_id, title, units, frequency, popularity, and more
- **Comprehensive Metadata:** Returns series details including observation dates, frequency, units, and notes
- **AI-Optimized:** Compact JSON format, reasonable limits (default: 20), fast responses (< 2s target)
- **Rate Limit Protection:** Automatic retries with exponential backoff
- **Production Ready:** Full error handling, logging, and validation

### When to Use This Tool

Use `get_fred_series_by_tags` when you:

1. **Know Specific Tag Combinations:** You have exact tags from `get_fred_tags` or `search_fred_related_tags`
2. **Need Precise Filtering:** Want series with ALL specified characteristics (e.g., "monthly + USA + NSA")
3. **Want to Exclude Categories:** Need to filter out discontinued, revised, or specific types of series
4. **Explore Tag Taxonomy:** Discover what series exist for specific tag combinations

**Complementary to `search_fred_series`:**
- Use `search_fred_series` for text-based searches ("unemployment rate")
- Use `get_fred_series_by_tags` for precise tag-based filtering ("employment;usa;nsa")

---

## Parameters

### Required Parameters

#### `tag_names` (str)
Semicolon-delimited list of tag names. Series must have **ALL** of these tags.

- **Format:** `"tag1;tag2;tag3"`
- **Logic:** AND - All tags must be present
- **Example:** `"slovenia;food;oecd"` finds only series tagged with all three
- **Case Sensitive:** Tags are case-sensitive
- **Validation:** FRED API will return error if tags don't exist

**Common Tag Patterns:**
```
Geography + Concept:     "usa;gdp"
Geography + Frequency:   "canada;monthly"
Concept + Adjustment:    "employment;nsa"
Multi-criteria:          "usa;inflation;monthly;nsa"
Source + Concept:        "bls;unemployment"
```

### Optional Parameters

#### `exclude_tag_names` (str | None)
Semicolon-delimited list of tag names. Series must have **NONE** of these tags.

- **Format:** `"tag1;tag2"`
- **Logic:** NOT - Any excluded tag disqualifies the series
- **Default:** `None` (no exclusions)
- **Example:** `"discontinued;daily"` excludes series with either tag
- **Use Cases:**
  - Filter out discontinued series: `"discontinued"`
  - Exclude revision series: `"revision"`
  - Remove specific frequencies: `"daily;weekly"`
  - Avoid specific geographies: `"county;state"`

#### `limit` (int)
Maximum number of series to return.

- **Range:** 1-1000
- **Default:** 20 (AI-optimized)
- **Validation:** Automatically clamped to valid range
- **Recommendation:**
  - Quick exploration: 10-20
  - Comprehensive search: 50-100
  - Full category: 200-500

#### `offset` (int)
Starting offset for pagination.

- **Default:** 0 (start from beginning)
- **Use Case:** Retrieving results beyond the first page
- **Example:** `limit=20, offset=20` gets results 21-40
- **Note:** For AI/LLM use, prefer single requests with appropriate limits over pagination

#### `order_by` (Literal)
Field to sort results by.

**Available Options:**

| Value | Description | Use Case |
|-------|-------------|----------|
| `series_id` | Alphabetical by ID | Default ordering, predictable |
| `title` | Alphabetical by title | Browsing by name |
| `units` | By units of measurement | Grouping similar units |
| `frequency` | By data frequency | Grouping by update cycle |
| `seasonal_adjustment` | By adjustment type | SA vs NSA comparison |
| `realtime_start` | By real-time start | Historical analysis |
| `realtime_end` | By real-time end | Current data availability |
| `last_updated` | By last update date | Finding most recent data |
| `observation_start` | By first observation | Historical depth |
| `observation_end` | By last observation | Current data availability |
| `popularity` | By popularity score | Most-used indicators |
| `group_popularity` | By group popularity | Related popular series |

- **Default:** `"series_id"`
- **Recommendation:** Use `"popularity"` or `"last_updated"` for most relevant results

#### `sort_order` (Literal["asc", "desc"])
Sort direction.

- **Values:** `"asc"` (ascending) or `"desc"` (descending)
- **Default:** `"asc"`
- **Common Patterns:**
  - `order_by="popularity", sort_order="desc"` → Most popular first
  - `order_by="last_updated", sort_order="desc"` → Most recent first
  - `order_by="series_id", sort_order="asc"` → Alphabetical (default)

#### `realtime_start` (str | None)
Start date for real-time period in `YYYY-MM-DD` format.

- **Default:** Today's date (set by FRED)
- **Format:** `"YYYY-MM-DD"` (e.g., `"2024-01-01"`)
- **Use Case:** Historical analysis, viewing series as they existed on a specific date
- **Note:** Most users don't need this; it's for advanced real-time data analysis

#### `realtime_end` (str | None)
End date for real-time period in `YYYY-MM-DD` format.

- **Default:** Today's date (set by FRED)
- **Format:** `"YYYY-MM-DD"`
- **Use Case:** Same as `realtime_start`

---

## Response Format

### Success Response Structure

```json
{
  "tool": "get_series_by_tags",
  "data": [
    {
      "id": "CPGDFD02SIA657N",
      "realtime_start": "2025-11-01",
      "realtime_end": "2025-11-01",
      "title": "Consumer Price Index: Food for Slovenia",
      "observation_start": "1996-01-01",
      "observation_end": "2016-01-01",
      "frequency": "Annual",
      "frequency_short": "A",
      "units": "Growth Rate Previous Period",
      "units_short": "Growth Rate Previous Period",
      "seasonal_adjustment": "Not Seasonally Adjusted",
      "seasonal_adjustment_short": "NSA",
      "last_updated": "2017-04-20 00:48:35-05",
      "popularity": 0,
      "group_popularity": 0,
      "notes": "OECD descriptor ID: CPGDFD02..."
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T16:30:00Z",
    "required_tags": ["slovenia", "food", "oecd"],
    "excluded_tags": ["discontinued"],
    "total_count": 18,
    "returned_count": 18,
    "limit": 20,
    "offset": 0,
    "order_by": "series_id",
    "sort_order": "asc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

### Response Fields

#### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `tool` | string | Tool identifier: `"get_series_by_tags"` |
| `data` | array | List of series objects matching criteria |
| `metadata` | object | Request information and statistics |

#### Series Object Fields (`data[]`)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | FRED series identifier | `"UNRATE"` |
| `realtime_start` | string | Real-time period start | `"2025-11-01"` |
| `realtime_end` | string | Real-time period end | `"2025-11-01"` |
| `title` | string | Full series title | `"Unemployment Rate"` |
| `observation_start` | string | First available observation | `"1948-01-01"` |
| `observation_end` | string | Last available observation | `"2024-12-01"` |
| `frequency` | string | Update frequency (full) | `"Monthly"` |
| `frequency_short` | string | Frequency abbreviation | `"M"` |
| `units` | string | Units of measurement (full) | `"Percent"` |
| `units_short` | string | Units abbreviation | `"%" ` |
| `seasonal_adjustment` | string | Adjustment type (full) | `"Seasonally Adjusted"` |
| `seasonal_adjustment_short` | string | Adjustment abbreviation | `"SA"` |
| `last_updated` | string | Last update timestamp | `"2024-01-05 07:44:03-06"` |
| `popularity` | integer | Popularity score | `85` |
| `group_popularity` | integer | Group popularity score | `85` |
| `notes` | string | Series description and notes | `"The unemployment rate..."` |

#### Metadata Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `fetch_date` | string | ISO 8601 timestamp of fetch |
| `required_tags` | array | List of required tags (split from `tag_names`) |
| `excluded_tags` | array\|null | List of excluded tags (split from `exclude_tag_names`) |
| `total_count` | integer | Total series matching criteria (from FRED) |
| `returned_count` | integer | Number of series in this response |
| `limit` | integer | Requested limit |
| `offset` | integer | Requested offset |
| `order_by` | string | Sort field used |
| `sort_order` | string | Sort direction used |
| `realtime_start` | string | Real-time period start used |
| `realtime_end` | string | Real-time period end used |

### Error Response Structure

```json
{
  "tool": "get_series_by_tags",
  "error": "Invalid parameters: Bad Request. The value for variable tag_names is not valid.",
  "required_tags": ["invalid-tag", "nonexistent"]
}
```

#### Error Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `tool` | string | Tool identifier |
| `error` | string | Human-readable error message |
| `required_tags` | array | Tags that were requested (for debugging) |

---

## Usage Examples

### Example 1: Basic Tag Combination

Find all series tagged with USA, monthly frequency, and not seasonally adjusted.

```python
from trabajo_ia_server.tools.fred.series_by_tags import get_series_by_tags
import json

result = get_series_by_tags(
    tag_names="usa;monthly;nsa"
)

data = json.loads(result)
print(f"Found {data['metadata']['returned_count']} of {data['metadata']['total_count']} series")

# Display first 3 series
for series in data['data'][:3]:
    print(f"{series['id']}: {series['title']}")
    print(f"  Period: {series['observation_start']} to {series['observation_end']}")
    print(f"  Frequency: {series['frequency']}, Units: {series['units']}")
```

**Output:**
```
Found 20 of 160340 series
AIMSBQV2B0ZAUS: Retail Sales: Apparel (Excludes Leased Departments): Merchandising Year-to-Year Percentage Change
  Period: 1993-01-01 to 2024-11-01
  Frequency: Monthly, Units: Percent
```

### Example 2: Exclude Discontinued Series

Find employment series for USA, excluding discontinued ones.

```python
result = get_series_by_tags(
    tag_names="employment;usa",
    exclude_tag_names="discontinued",
    limit=10
)

data = json.loads(result)
print(f"Active employment series: {data['metadata']['returned_count']}")
```

**Use Case:** Ensuring analysis uses only currently maintained series.

### Example 3: Sort by Popularity

Get the most popular GDP-related series.

```python
result = get_series_by_tags(
    tag_names="gdp;usa",
    limit=10,
    order_by="popularity",
    sort_order="desc"
)

data = json.loads(result)
print("Most popular GDP series:")
for i, series in enumerate(data['data'], 1):
    print(f"{i}. {series['id']} (popularity: {series['popularity']})")
    print(f"   {series['title']}")
```

**Use Case:** Finding the most commonly used indicators for analysis.

### Example 4: Find Most Recently Updated Series

Get latest inflation data for USA.

```python
result = get_series_by_tags(
    tag_names="inflation;usa;monthly",
    exclude_tag_names="discontinued",
    limit=15,
    order_by="last_updated",
    sort_order="desc"
)

data = json.loads(result)
print("Most recently updated inflation series:")
for series in data['data'][:5]:
    print(f"{series['id']}: Updated {series['last_updated']}")
    print(f"  Latest data: {series['observation_end']}")
```

**Use Case:** Ensuring you're working with the most current data.

### Example 5: Quarterly Economic Indicators

Find quarterly economic indicators from BLS (Bureau of Labor Statistics).

```python
result = get_series_by_tags(
    tag_names="bls;quarterly;usa",
    exclude_tag_names="discontinued;revision",
    limit=20,
    order_by="series_id",
    sort_order="asc"
)

data = json.loads(result)
print(f"BLS quarterly series: {data['metadata']['returned_count']}")

# Group by category from title
for series in data['data']:
    category = series['title'].split(':')[0] if ':' in series['title'] else 'Other'
    print(f"[{category}] {series['id']}: {series['units_short']}")
```

**Use Case:** Building a quarterly economic dashboard.

### Example 6: Geographic-Specific Analysis

Find all OECD food price indices for Slovenia.

```python
result = get_series_by_tags(
    tag_names="slovenia;food;oecd",
    limit=50,
    order_by="observation_end",
    sort_order="desc"
)

data = json.loads(result)
print(f"Slovenia food price series: {data['metadata']['returned_count']}")

# Check data availability
for series in data['data']:
    years = int(series['observation_end'][:4]) - int(series['observation_start'][:4])
    print(f"{series['id']}:")
    print(f"  {years} years of data ({series['observation_start']} to {series['observation_end']})")
    print(f"  Frequency: {series['frequency']}, Units: {series['units_short']}")
```

**Use Case:** Country-specific economic analysis.

### Example 7: Seasonal Adjustment Comparison

Find both SA and NSA versions of employment data.

```python
# Get seasonally adjusted
result_sa = get_series_by_tags(
    tag_names="employment;usa;monthly;sa",
    limit=10,
    order_by="popularity",
    sort_order="desc"
)

# Get not seasonally adjusted
result_nsa = get_series_by_tags(
    tag_names="employment;usa;monthly;nsa",
    limit=10,
    order_by="popularity",
    sort_order="desc"
)

data_sa = json.loads(result_sa)
data_nsa = json.loads(result_nsa)

print(f"SA series: {data_sa['metadata']['returned_count']}")
print(f"NSA series: {data_nsa['metadata']['returned_count']}")

# Find matching series IDs
sa_ids = {s['id'].replace('SA', '') for s in data_sa['data']}
nsa_ids = {s['id'].replace('NSA', '') for s in data_nsa['data']}
common = sa_ids & nsa_ids

print(f"Series available in both formats: {len(common)}")
```

**Use Case:** Comparing seasonal patterns vs. adjusted trends.

---

## Use Cases

### 1. Building Economic Dashboards

**Scenario:** Create a comprehensive economic dashboard with specific data characteristics.

**Solution:**
```python
# Get key monthly economic indicators (SA, not discontinued)
dashboard_series = [
    "gdp;monthly;sa",           # GDP indicators
    "employment;monthly;sa",    # Employment metrics
    "inflation;monthly;sa",     # Inflation measures
    "interest;monthly;sa",      # Interest rates
]

dashboard_data = {}
for tags in dashboard_series:
    result = get_series_by_tags(
        tag_names=tags,
        exclude_tag_names="discontinued;revision",
        limit=10,
        order_by="popularity",
        sort_order="desc"
    )
    category = tags.split(';')[0]
    dashboard_data[category] = json.loads(result)
```

**Benefits:**
- Consistent data characteristics (monthly, SA)
- High-quality data (popular, not discontinued)
- Organized by economic category

### 2. International Economic Comparison

**Scenario:** Compare economic indicators across multiple countries.

**Solution:**
```python
countries = ["usa", "canada", "japan", "germany"]
metric = "gdp"

comparison_data = {}
for country in countries:
    result = get_series_by_tags(
        tag_names=f"{country};{metric};quarterly",
        exclude_tag_names="discontinued",
        limit=5,
        order_by="popularity",
        sort_order="desc"
    )
    comparison_data[country] = json.loads(result)

    # Get the most popular series for each country
    if comparison_data[country]['data']:
        top_series = comparison_data[country]['data'][0]
        print(f"{country.upper()}: {top_series['id']} - {top_series['title']}")
```

**Benefits:**
- Consistent metrics across countries
- Standardized frequency (quarterly)
- Focus on primary indicators (by popularity)

### 3. Data Quality Filtering

**Scenario:** Find only high-quality, actively maintained series for production analysis.

**Solution:**
```python
result = get_series_by_tags(
    tag_names="usa;employment;monthly",
    exclude_tag_names="discontinued;preliminary;revision;estimated",
    limit=20,
    order_by="popularity",
    sort_order="desc"
)

data = json.loads(result)

# Additional filtering: Check data recency
recent_series = []
for series in data['data']:
    last_obs_year = int(series['observation_end'][:4])
    if last_obs_year >= 2023:  # Data extends to recent years
        recent_series.append(series)

print(f"High-quality, recent series: {len(recent_series)}")
```

**Benefits:**
- Excludes low-quality data tags
- Focuses on maintained series
- Ensures data recency

### 4. Frequency-Specific Analysis

**Scenario:** Build a high-frequency monitoring system using weekly data.

**Solution:**
```python
result = get_series_by_tags(
    tag_names="usa;weekly;nsa",
    exclude_tag_names="discontinued",
    limit=50,
    order_by="last_updated",
    sort_order="desc"
)

data = json.loads(result)

# Categorize by data type
categories = {}
for series in data['data']:
    # Extract category from title
    if ':' in series['title']:
        cat = series['title'].split(':')[0].strip()
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(series['id'])

print("Weekly indicators by category:")
for cat, ids in categories.items():
    print(f"  {cat}: {len(ids)} series")
```

**Benefits:**
- High-frequency monitoring (weekly updates)
- Organized by category
- Most recent data first

### 5. Source-Specific Data Collection

**Scenario:** Collect all series from a specific data source (e.g., Bureau of Labor Statistics).

**Solution:**
```python
result = get_series_by_tags(
    tag_names="bls;usa;monthly",
    exclude_tag_names="discontinued",
    limit=100,
    order_by="group_popularity",
    sort_order="desc"
)

data = json.loads(result)

print(f"BLS monthly series: {data['metadata']['total_count']}")
print(f"Retrieved: {data['metadata']['returned_count']}")

# Analyze frequency of units
unit_counts = {}
for series in data['data']:
    unit = series['units_short']
    unit_counts[unit] = unit_counts.get(unit, 0) + 1

print("\nUnits distribution:")
for unit, count in sorted(unit_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {unit}: {count} series")
```

**Benefits:**
- Source-specific analysis
- Understanding data provider's coverage
- Unit standardization insights

### 6. Historical Data Discovery

**Scenario:** Find series with longest historical coverage for long-term analysis.

**Solution:**
```python
result = get_series_by_tags(
    tag_names="usa;annual;nsa",
    exclude_tag_names="discontinued;estimated",
    limit=50,
    order_by="observation_start",
    sort_order="asc"
)

data = json.loads(result)

# Calculate historical depth
historical_series = []
for series in data['data']:
    start_year = int(series['observation_start'][:4])
    end_year = int(series['observation_end'][:4])
    years = end_year - start_year

    if years >= 50:  # At least 50 years of data
        historical_series.append({
            'id': series['id'],
            'title': series['title'],
            'years': years,
            'start': start_year
        })

# Sort by historical depth
historical_series.sort(key=lambda x: -x['years'])

print("Series with 50+ years of data:")
for s in historical_series[:10]:
    print(f"{s['id']}: {s['years']} years (from {s['start']})")
```

**Benefits:**
- Long-term trend analysis
- Historical economic research
- Structural change detection

### 7. Taxonomy Exploration

**Scenario:** Explore what series exist for specific tag combinations to understand FRED's data structure.

**Solution:**
```python
# Start with a base concept
base_tags = "gdp;usa"

result = get_series_by_tags(
    tag_names=base_tags,
    limit=100,
    order_by="popularity",
    sort_order="desc"
)

data = json.loads(result)

# Analyze frequency distribution
freq_counts = {}
for series in data['data']:
    freq = series['frequency']
    freq_counts[freq] = freq_counts.get(freq, 0) + 1

print(f"GDP USA series by frequency:")
for freq, count in sorted(freq_counts.items(), key=lambda x: -x[1]):
    print(f"  {freq}: {count} series")

# Analyze seasonal adjustment
sa_counts = {}
for series in data['data']:
    sa = series['seasonal_adjustment_short']
    sa_counts[sa] = sa_counts.get(sa, 0) + 1

print(f"\nGDP USA series by seasonal adjustment:")
for sa, count in sa_counts.items():
    print(f"  {sa}: {count} series")
```

**Benefits:**
- Understanding data availability
- Discovering data characteristics
- Planning comprehensive analysis

---

## Error Handling

### Common Errors

#### 1. Invalid Tags

**Error Message:**
```json
{
  "tool": "get_series_by_tags",
  "error": "Invalid parameters: Bad Request. The value for variable tag_names is not valid.",
  "required_tags": ["invalid-tag", "nonexistent"]
}
```

**Cause:** One or more tags in `tag_names` don't exist in FRED.

**Solution:**
1. Use `get_fred_tags` to search for valid tags:
   ```python
   # Search for tags
   tags_result = get_fred_tags(search_text="employment")
   # Verify tag names before using
   ```

2. Check tag spelling and case (tags are case-sensitive)

3. Use `search_fred_related_tags` to find tags that work together

#### 2. No Series Found

**Response:**
```json
{
  "tool": "get_series_by_tags",
  "data": [],
  "metadata": {
    "total_count": 0,
    "returned_count": 0,
    ...
  }
}
```

**Cause:** Tag combination is too restrictive or no series match.

**Solution:**
1. Reduce number of required tags
2. Remove exclude tags
3. Use `search_fred_related_tags` to find viable tag combinations:
   ```python
   # Check if tags have related series
   related = search_fred_related_tags(
       tag_names="employment;usa",
       tag_group_id="freq"
   )
   # Shows which frequency tags are available
   ```

#### 3. Rate Limiting

**Error Message:**
```json
{
  "tool": "get_series_by_tags",
  "error": "Rate limit exceeded. Please try again later.",
  "required_tags": ["usa", "gdp"]
}
```

**Cause:** Too many requests to FRED API in short time.

**Solution:**
- Tool automatically retries with exponential backoff (3 attempts)
- If error persists, wait 1-5 minutes before retry
- Reduce request frequency in loops
- Consider batching operations

#### 4. Network/Timeout Errors

**Error Message:**
```json
{
  "tool": "get_series_by_tags",
  "error": "Unexpected error: HTTPSConnectionPool(...): Read timed out.",
  "required_tags": ["usa", "monthly"]
}
```

**Cause:** Network connectivity issues or FRED API downtime.

**Solution:**
- Check network connectivity
- Check FRED API status: https://fred.stlouisfed.org/
- Retry request (automatic retries already attempted)
- Reduce complexity of request (lower limit)

### Error Handling Best Practices

```python
import json
from trabajo_ia_server.tools.fred.series_by_tags import get_series_by_tags

def safe_get_series_by_tags(tag_names, **kwargs):
    """Wrapper with comprehensive error handling."""
    try:
        result = get_series_by_tags(tag_names=tag_names, **kwargs)
        data = json.loads(result)

        # Check for API errors
        if 'error' in data:
            print(f"API Error: {data['error']}")
            return None

        # Check for empty results
        if data['metadata']['returned_count'] == 0:
            print(f"No series found for tags: {tag_names}")
            print("Try reducing tag restrictions or checking tag validity")
            return None

        return data

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
data = safe_get_series_by_tags("usa;gdp;quarterly", limit=10)
if data:
    print(f"Found {data['metadata']['returned_count']} series")
```

---

## Performance

### Response Time Benchmarks

Based on production testing with FRED API:

| Scenario | Avg Time | Notes |
|----------|----------|-------|
| Simple tag combo (2-3 tags) | 0.5-1.0s | Fast, typical use case |
| Complex combo (4+ tags) | 0.8-1.5s | More selective, fewer results |
| With exclusions | 0.6-1.2s | Similar to simple combo |
| High limit (100-500) | 1.0-2.0s | Larger payload transfer |
| No results | 0.4-0.8s | Fast return, small response |

**Target:** < 2 seconds for 95% of requests

### Optimization Tips

#### 1. Limit Results Appropriately

```python
# Good: Reasonable limit for exploration
result = get_series_by_tags("usa;monthly", limit=20)

# Avoid: Unnecessarily high limit
result = get_series_by_tags("usa;monthly", limit=1000)  # Slower, huge response
```

#### 2. Use Specific Tag Combinations

```python
# Good: Specific tags = fewer results = faster
result = get_series_by_tags("slovenia;food;oecd")  # ~18 results

# Slower: Generic tags = many results
result = get_series_by_tags("usa;monthly")  # 160,000+ results
```

#### 3. Leverage Exclusions for Faster Filtering

```python
# Good: Exclude at API level
result = get_series_by_tags(
    "employment;usa",
    exclude_tag_names="discontinued;revision"
)

# Avoid: Filter after retrieval (wastes bandwidth)
result = get_series_by_tags("employment;usa", limit=100)
# Then manually filter in code
```

#### 4. Sort by Relevant Fields

```python
# Efficient: Sort by indexed fields
result = get_series_by_tags(
    "gdp;usa",
    order_by="popularity",  # Fast, indexed
    sort_order="desc"
)

# Also efficient: series_id, last_updated, observation_end
```

#### 5. Cache Results for Repeated Queries

```python
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_get_series_by_tags(tag_names, limit=20):
    """Cache results for frequently used tag combinations."""
    return get_series_by_tags(tag_names=tag_names, limit=limit)

# First call: ~1s (API request)
start = time.time()
result1 = cached_get_series_by_tags("usa;gdp;quarterly", limit=10)
print(f"First call: {time.time() - start:.2f}s")

# Second call: ~0.001s (cached)
start = time.time()
result2 = cached_get_series_by_tags("usa;gdp;quarterly", limit=10)
print(f"Cached call: {time.time() - start:.4f}s")
```

### Token Efficiency (AI/LLM)

The tool uses compact JSON format to minimize token usage:

```python
# Compact format (separators=(",", ":"))
result = get_series_by_tags("usa;gdp", limit=5)
# ~1,200 tokens for 5 series

# vs. Pretty format (if used, not recommended)
# ~1,600 tokens for 5 series

# Token savings: ~25% with compact format
```

**Recommendations for AI/LLM:**
- Use `limit=10-20` for initial exploration (balance info vs. tokens)
- Use `limit=5` for quick checks
- Use `limit=50-100` only when comprehensive view needed
- Filter results in code if more specific selection needed after initial fetch

---

## Best Practices

### 1. Discover Tags First

**Do:**
```python
# Step 1: Find relevant tags
tags_result = get_fred_tags(search_text="employment", limit=20)
tags_data = json.loads(tags_result)

# Step 2: Explore tag relationships
related_result = search_fred_related_tags(
    tag_names="employment",
    tag_group_id="freq"
)
related_data = json.loads(related_result)

# Step 3: Use discovered tags
result = get_series_by_tags(
    tag_names="employment;monthly;nsa",
    limit=15
)
```

**Don't:**
```python
# Bad: Guessing tag names
result = get_series_by_tags("employment-rate;usa")  # Wrong format
```

### 2. Start Broad, Then Narrow

**Do:**
```python
# Step 1: Start with broad tags
result1 = get_series_by_tags("gdp;usa", limit=50)
data1 = json.loads(result1)
print(f"Total GDP series: {data1['metadata']['total_count']}")

# Step 2: Analyze frequencies available
freqs = {s['frequency_short'] for s in data1['data']}
print(f"Available frequencies: {freqs}")

# Step 3: Narrow to specific frequency
result2 = get_series_by_tags("gdp;usa;quarterly", limit=20)
```

**Don't:**
```python
# Bad: Starting too specific (might get zero results)
result = get_series_by_tags("gdp;usa;quarterly;sa;real;per-capita")
```

### 3. Use Exclusions Strategically

**Do:**
```python
# Good: Exclude common unwanted categories
result = get_series_by_tags(
    tag_names="inflation;usa;monthly",
    exclude_tag_names="discontinued;revision;preliminary",
    limit=20
)
```

**Don't:**
```python
# Bad: Over-excluding (might eliminate all results)
result = get_series_by_tags(
    tag_names="inflation;usa",
    exclude_tag_names="discontinued;revision;preliminary;estimated;forecast;survey",
    limit=20
)
```

### 4. Sort Intelligently

**Do:**
```python
# For discovery: Use popularity
result = get_series_by_tags(
    "employment;usa",
    order_by="popularity",
    sort_order="desc",
    limit=10
)

# For current data: Use last_updated
result = get_series_by_tags(
    "employment;usa",
    order_by="last_updated",
    sort_order="desc",
    limit=10
)

# For historical: Use observation_start
result = get_series_by_tags(
    "employment;usa",
    order_by="observation_start",
    sort_order="asc",
    limit=10
)
```

### 5. Validate Results

**Do:**
```python
result = get_series_by_tags("usa;gdp", limit=10)
data = json.loads(result)

# Check for errors
if 'error' in data:
    print(f"Error: {data['error']}")
    # Handle error appropriately

# Check result count
if data['metadata']['returned_count'] == 0:
    print("No series found. Try different tags.")

# Validate data quality
for series in data['data']:
    # Check recency
    last_obs_year = int(series['observation_end'][:4])
    if last_obs_year < 2020:
        print(f"Warning: {series['id']} has old data (ends {series['observation_end']})")
```

### 6. Document Tag Combinations

**Do:**
```python
# Maintain a registry of useful tag combinations
USEFUL_TAG_COMBOS = {
    "monthly_employment": {
        "tags": "employment;usa;monthly;nsa",
        "exclude": "discontinued",
        "limit": 20,
        "order_by": "popularity"
    },
    "quarterly_gdp": {
        "tags": "gdp;usa;quarterly;sa",
        "exclude": "discontinued;revision",
        "limit": 15,
        "order_by": "last_updated"
    },
    "weekly_indicators": {
        "tags": "usa;weekly;nsa",
        "exclude": "discontinued",
        "limit": 30,
        "order_by": "last_updated"
    }
}

# Use documented combos
def get_series_preset(preset_name):
    """Get series using predefined tag combination."""
    config = USEFUL_TAG_COMBOS.get(preset_name)
    if not config:
        raise ValueError(f"Unknown preset: {preset_name}")

    return get_series_by_tags(
        tag_names=config["tags"],
        exclude_tag_names=config.get("exclude"),
        limit=config["limit"],
        order_by=config.get("order_by", "series_id")
    )

result = get_series_preset("monthly_employment")
```

### 7. Handle Pagination Thoughtfully

**Do:**
```python
# For comprehensive collection, paginate carefully
def get_all_series_by_tags(tag_names, max_total=500):
    """Get all series up to max_total."""
    all_series = []
    offset = 0
    limit = 100

    while len(all_series) < max_total:
        result = get_series_by_tags(
            tag_names=tag_names,
            limit=limit,
            offset=offset
        )
        data = json.loads(result)

        if 'error' in data or data['metadata']['returned_count'] == 0:
            break

        all_series.extend(data['data'])
        offset += limit

        # Check if we've retrieved all available
        if len(all_series) >= data['metadata']['total_count']:
            break

    return all_series[:max_total]

series = get_all_series_by_tags("usa;monthly", max_total=500)
print(f"Collected {len(series)} series")
```

**Don't:**
```python
# Bad: Uncontrolled pagination (could retrieve 100,000+ series)
offset = 0
while True:
    result = get_series_by_tags("usa;monthly", limit=100, offset=offset)
    # No exit condition!
    offset += 100
```

---

## Related Tools

### Tool Comparison

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **get_fred_series_by_tags** | Get series matching ALL tags | You have specific tag combinations |
| **search_fred_series** | Text search for series | You're searching by keywords/concepts |
| **get_fred_tags** | Discover available tags | You need to find valid tags first |
| **search_fred_related_tags** | Find tags related to given tags | Exploring tag relationships |
| **fetch_fred_series** | Get observations for a series | You have series ID, need actual data |

### Recommended Workflows

#### Workflow 1: Exploration → Discovery → Retrieval

```python
# 1. Explore: Find relevant tags
tags_result = get_fred_tags(search_text="employment")

# 2. Discover: Get series with those tags
series_result = get_series_by_tags(
    tag_names="employment;usa;monthly",
    limit=10,
    order_by="popularity",
    sort_order="desc"
)

# 3. Retrieve: Fetch actual data for chosen series
data_result = fetch_fred_series(
    series_id="UNRATE",
    observation_start="2020-01-01"
)
```

#### Workflow 2: Tag-Based Series Discovery

```python
from trabajo_ia_server.tools.fred.get_tags import get_fred_tags
from trabajo_ia_server.tools.fred.related_tags import search_fred_related_tags
from trabajo_ia_server.tools.fred.series_by_tags import get_series_by_tags

# 1. Get base tags
base_tags = get_fred_tags(search_text="inflation", limit=10)

# 2. Find related frequency tags
related = search_fred_related_tags(
    tag_names="inflation;usa",
    tag_group_id="freq"
)

# 3. Get series with specific combination
series = get_series_by_tags(
    tag_names="inflation;usa;monthly",
    exclude_tag_names="discontinued",
    limit=15
)
```

#### Workflow 3: Text Search → Tag Refinement

```python
from trabajo_ia_server.tools.fred.search_series import search_fred_series
from trabajo_ia_server.tools.fred.series_by_tags import get_series_by_tags

# 1. Start with text search
text_search = search_fred_series("unemployment rate", limit=5)

# Extract tags from results to understand taxonomy
# ...

# 2. Refine with precise tag-based search
precise_search = get_series_by_tags(
    tag_names="unemployment;usa;monthly;sa",
    exclude_tag_names="discontinued",
    limit=10,
    order_by="popularity",
    sort_order="desc"
)
```

### Tool Synergies

#### Synergy 1: Tags Discovery + Series by Tags

Perfect for systematic exploration:

```python
# Discover what tags exist for a concept
tags = get_fred_tags(search_text="labor", limit=20)

# For each major tag, find series
for tag_data in json.loads(tags)['data'][:5]:
    tag_name = tag_data['name']
    series = get_series_by_tags(
        tag_names=f"{tag_name};usa",
        limit=10
    )
    print(f"Tag '{tag_name}': {json.loads(series)['metadata']['total_count']} series")
```

#### Synergy 2: Related Tags + Series by Tags

Explore tag relationships systematically:

```python
# Find what frequency tags work with employment
related = search_fred_related_tags(
    tag_names="employment;usa",
    tag_group_id="freq"
)

# Get series for each frequency
for tag in json.loads(related)['data']:
    freq_tag = tag['name']
    series = get_series_by_tags(
        tag_names=f"employment;usa;{freq_tag}",
        limit=5
    )
    count = json.loads(series)['metadata']['total_count']
    print(f"{freq_tag}: {count} series")
```

#### Synergy 3: Series by Tags + Fetch Series

Complete data pipeline:

```python
# 1. Find relevant series
series_list = get_series_by_tags(
    tag_names="gdp;usa;quarterly",
    limit=5,
    order_by="popularity",
    sort_order="desc"
)

# 2. Fetch observations for each series
for series in json.loads(series_list)['data']:
    observations = fetch_fred_series(
        series_id=series['id'],
        observation_start="2020-01-01"
    )
    obs_data = json.loads(observations)
    print(f"{series['id']}: {obs_data['metadata']['observation_count']} observations")
```

---

## Changelog

### v0.1.4 (2025-11-01)
- ✅ Initial implementation of `get_fred_series_by_tags`
- ✅ Full support for 12 sort options
- ✅ AND logic for required tags, NOT logic for exclusions
- ✅ Comprehensive error handling with retry mechanism
- ✅ AI-optimized compact JSON output
- ✅ Complete API reference documentation

---

## See Also

- [FRED Tags Reference](./FRED_TAGS_REFERENCE.MD) - Understanding FRED's tag system
- [FRED Related Tags Reference](./FRED_RELATEDTAGS_REFERENCE.MD) - Finding related tags
- [FRED Search Series Reference](./FRED_SEARCH_REFERENCE.MD) - Text-based series search
- [FRED Fetch Series Reference](./FRED_FETCH_REFERENCE.MD) - Getting observation data
- [Implementation Guide](../guides/IMPLEMENTACION_NUEVA_TOOL_GUIA.md) - How this tool was built

---

## Support

For issues, questions, or feature requests related to this tool:

1. Check this documentation thoroughly
2. Review FRED API documentation: https://fred.stlouisfed.org/docs/api/
3. Test with the usage examples provided
4. Verify tag names using `get_fred_tags` or `search_fred_related_tags`

---

**Documentation Version:** 1.0.0
**Last Updated:** 2025-11-01
**Tool Version:** 0.1.4
