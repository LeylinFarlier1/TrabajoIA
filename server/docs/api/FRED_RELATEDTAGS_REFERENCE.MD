# FRED Related Tags API Reference

**Tool Name:** `search_fred_related_tags`

**Endpoint:** `https://api.stlouisfed.org/fred/related_tags`

**Description:** Get FRED tags that are related to one or more specified tags. This tool helps discover tags that frequently appear together with the input tags, enabling exploration of FRED's data taxonomy and finding associated economic indicators.

---

## Table of Contents

1. [Overview](#overview)
2. [Parameters](#parameters)
3. [Response Format](#response-format)
4. [Usage Examples](#usage-examples)
5. [Use Cases](#use-cases)
6. [Tag Groups Reference](#tag-groups-reference)
7. [Error Handling](#error-handling)
8. [Performance](#performance)
9. [Best Practices](#best-practices)

---

## Overview

The `search_fred_related_tags` tool discovers tags that are related to your specified input tags. This is useful for:

- **Exploring FRED's taxonomy**: Understanding how different economic concepts are connected
- **Refining searches**: Finding additional relevant tags to improve series filtering
- **Data discovery**: Uncovering related economic indicators you might not have considered
- **Building tag combinations**: Creating effective multi-tag filters for precise searches

### Key Features

- **Tag relationship discovery**: Find tags that frequently co-occur with your input tags
- **Group filtering**: Limit results to specific tag groups (frequency, geography, etc.)
- **Search within results**: Filter related tags by keyword
- **Exclusion support**: Remove unwanted tags from results
- **Flexible sorting**: Order by popularity, series count, or other criteria
- **Real-time windows**: Scope results to specific time periods
- **AI-optimized**: Compact JSON output with reasonable default limits

---

## Parameters

### Required Parameters

#### `tag_names` (string, REQUIRED)

Semicolon-delimited list of tag names to find related tags for.

**Format:** `"tag1;tag2;tag3"`

**Examples:**
```python
"monetary aggregates"           # Single tag
"monetary aggregates;weekly"    # Multiple tags
"usa;gdp"                       # Country + indicator
"nsa;monthly"                   # Seasonal adjustment + frequency
```

**Important Notes:**
- Tag names are **case-insensitive**
- Must use **semicolons** (`;`) as delimiters, NOT commas
- Invalid tag names will result in empty results or errors
- Use `get_fred_tags` tool to discover valid tag names first

---

### Optional Parameters

#### `exclude_tag_names` (string, optional)

Semicolon-delimited list of tag names to **exclude** from results.

**Default:** None

**Examples:**
```python
exclude_tag_names="discontinued"              # Exclude discontinued series
exclude_tag_names="discontinued;annual"       # Exclude multiple
exclude_tag_names="daily;weekly;biweekly"     # Exclude high-frequency data
```

**Use Cases:**
- Remove irrelevant or outdated data categories
- Focus on specific frequencies by excluding others
- Filter out copyright-restricted data

---

#### `tag_group_id` (string, optional)

Filter results to tags in a **specific group**.

**Default:** None (returns all groups)

**Valid Values:**
- `"freq"` - Frequency tags (monthly, quarterly, annual, etc.)
- `"gen"` - General/concept tags (gdp, employment, inflation, etc.)
- `"geo"` - Geography tags (usa, canada, japan, etc.)
- `"geot"` - Geography type tags (nation, state, county, msa)
- `"rls"` - Release tags
- `"seas"` - Seasonal adjustment tags (sa, nsa)
- `"src"` - Source tags (bls, bea, census, fed, etc.)

**Note:** `"cc"` (Citation & Copyright) is **NOT** supported for related_tags (only in get_tags)

**Examples:**
```python
tag_group_id="freq"    # Only return frequency-related tags
tag_group_id="geo"     # Only return geography-related tags
tag_group_id="src"     # Only return source-related tags
```

---

#### `search_text` (string, optional)

Filter related tags by **keyword match** in tag name or notes.

**Default:** None

**Examples:**
```python
search_text="inflation"     # Find inflation-related tags
search_text="price"         # Find price-related tags
search_text="employ"        # Find employment-related tags (partial match works)
```

**Behavior:**
- Case-insensitive matching
- Searches both tag names and tag descriptions
- Partial word matching supported
- Combines with other filters (tag_group_id, exclude_tag_names)

---

#### `limit` (integer, optional)

Maximum number of tags to return.

**Default:** `50` (AI-optimized)

**Range:** 1 to 1000

**Examples:**
```python
limit=10     # Quick overview
limit=50     # Default (balanced)
limit=100    # Comprehensive results
```

**Recommendations:**
- **10-20**: Quick exploration
- **50**: Default for most use cases
- **100+**: Comprehensive analysis or data export

---

#### `offset` (integer, optional)

Starting position for pagination.

**Default:** `0`

**Range:** 0 to positive integer

**Examples:**
```python
# First page
limit=50, offset=0

# Second page
limit=50, offset=50

# Third page
limit=50, offset=100
```

**Note:** For AI/LLM use cases, pagination is usually unnecessary. Use appropriate `limit` instead.

---

#### `order_by` (string, optional)

Field to sort results by.

**Default:** `"series_count"` (tags with most series first)

**Valid Values:**
- `"series_count"` - Number of series using this tag
- `"popularity"` - FRED's internal popularity score (0-100)
- `"created"` - Tag creation date
- `"name"` - Alphabetically by tag name
- `"group_id"` - By tag group

**Examples:**
```python
order_by="series_count"   # Most commonly used tags first
order_by="popularity"     # FRED's recommended tags first
order_by="name"           # Alphabetical listing
```

**Use Cases:**
- `series_count`: Find most data-rich related tags
- `popularity`: FRED's editorial recommendations
- `name`: Systematic browsing

---

#### `sort_order` (string, optional)

Sort direction for `order_by` field.

**Default:** `"asc"` (ascending)

**Valid Values:**
- `"asc"` - Ascending (A’Z, 0’100, oldest’newest)
- `"desc"` - Descending (Z’A, 100’0, newest’oldest)

**Common Combinations:**
```python
order_by="series_count", sort_order="desc"  # Most series first
order_by="popularity", sort_order="desc"    # Most popular first
order_by="name", sort_order="asc"           # Alphabetical A-Z
order_by="created", sort_order="desc"       # Newest tags first
```

---

#### `realtime_start` (string, optional)

Start date for real-time period constraint.

**Default:** Today's date

**Format:** `"YYYY-MM-DD"`

**Examples:**
```python
realtime_start="2020-01-01"     # Data as it existed on Jan 1, 2020
realtime_start="2023-06-15"     # Mid-year snapshot
```

**Purpose:**
- Access historical versions of FRED metadata
- Understand how tag relationships evolved over time
- Research reproducibility

---

#### `realtime_end` (string, optional)

End date for real-time period constraint.

**Default:** Today's date

**Format:** `"YYYY-MM-DD"`

**Examples:**
```python
realtime_end="2023-12-31"      # End of year snapshot
realtime_start="2023-01-01", realtime_end="2023-12-31"  # Full year 2023
```

---

## Response Format

### Success Response

```json
{
  "tool": "search_fred_related_tags",
  "data": [
    {
      "name": "weekly",
      "group_id": "freq",
      "notes": "Weekly",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 65,
      "series_count": 12458
    },
    {
      "name": "m1",
      "group_id": "gen",
      "notes": "M1 Money Stock",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 76,
      "series_count": 567
    },
    {
      "name": "usa",
      "group_id": "geo",
      "notes": "United States of America",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 673858
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "input_tags": ["monetary aggregates"],
    "excluded_tags": null,
    "tag_group_id": null,
    "search_text": null,
    "total_count": 156,
    "returned_count": 3,
    "limit": 50,
    "offset": 0,
    "order_by": "series_count",
    "sort_order": "asc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

### Tag Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Tag identifier (use in tag_names parameters) |
| `group_id` | string | Tag group: freq, gen, geo, geot, rls, seas, src |
| `notes` | string | Human-readable description |
| `created` | string | Creation timestamp (ISO 8601 with timezone) |
| `popularity` | integer | FRED popularity score (0-100, higher = more popular) |
| `series_count` | integer | Number of series using this tag |

### Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `fetch_date` | string | When this data was retrieved (UTC ISO 8601) |
| `input_tags` | array | List of input tag names used for search |
| `excluded_tags` | array/null | List of excluded tag names (null if none) |
| `tag_group_id` | string/null | Group filter applied (null if none) |
| `search_text` | string/null | Keyword filter applied (null if none) |
| `total_count` | integer | Total tags matching criteria in FRED |
| `returned_count` | integer | Number of tags in this response |
| `limit` | integer | Max results requested |
| `offset` | integer | Starting offset used |
| `order_by` | string | Sort field applied |
| `sort_order` | string | Sort direction applied |
| `realtime_start` | string | Real-time window start date |
| `realtime_end` | string | Real-time window end date |

### Error Response

```json
{
  "tool": "search_fred_related_tags",
  "error": "Invalid parameters: tag_names is required",
  "input_tags": []
}
```

**Common Error Messages:**
- `"Invalid parameters: tag_names is required"` - Missing required parameter
- `"Invalid parameters: [FRED API error message]"` - Bad parameter values
- `"Rate limit exceeded. Please try again later."` - Too many requests
- `"FRED API error: 400"` - General bad request
- `"Unexpected error: [details]"` - Internal tool error

---

## Usage Examples

### Example 1: Basic Usage - Find Related Tags

**Goal:** Find tags related to "monetary aggregates"

```python
search_fred_related_tags("monetary aggregates")
```

**Result:**
```json
{
  "data": [
    {"name": "weekly", "group_id": "freq", "series_count": 12458},
    {"name": "m1", "group_id": "gen", "series_count": 567},
    {"name": "nsa", "group_id": "seas", "series_count": 747558},
    {"name": "usa", "group_id": "geo", "series_count": 673858}
  ],
  "metadata": {
    "total_count": 156,
    "returned_count": 50
  }
}
```

**Insights:** Monetary aggregates are commonly tagged with:
- Weekly frequency
- M1, M2 money supply concepts
- Not seasonally adjusted data
- USA geography

---

### Example 2: Filter by Group - Find Frequency Tags

**Goal:** What frequencies are available for GDP data?

```python
search_fred_related_tags("gdp", tag_group_id="freq")
```

**Result:**
```json
{
  "data": [
    {"name": "quarterly", "group_id": "freq", "series_count": 143580},
    {"name": "annual", "group_id": "freq", "series_count": 493258},
    {"name": "monthly", "group_id": "freq", "series_count": 220226}
  ],
  "metadata": {
    "input_tags": ["gdp"],
    "tag_group_id": "freq",
    "total_count": 3
  }
}
```

**Insight:** GDP data is primarily quarterly, with some annual and monthly variations.

---

### Example 3: Exclude Unwanted Tags

**Goal:** Find employment-related tags, excluding discontinued series

```python
search_fred_related_tags(
    "employment",
    exclude_tag_names="discontinued",
    limit=20
)
```

**Result:**
```json
{
  "data": [
    {"name": "nsa", "group_id": "seas", "series_count": 650000},
    {"name": "monthly", "group_id": "freq", "series_count": 180000},
    {"name": "usa", "group_id": "geo", "series_count": 520000}
  ],
  "metadata": {
    "input_tags": ["employment"],
    "excluded_tags": ["discontinued"]
  }
}
```

**Benefit:** Cleaner results focusing on active data series.

---

### Example 4: Multiple Input Tags

**Goal:** Find tags related to both USA and inflation

```python
search_fred_related_tags("usa;inflation", limit=30)
```

**Result:**
```json
{
  "data": [
    {"name": "cpi", "group_id": "gen", "series_count": 45678},
    {"name": "pce", "group_id": "gen", "series_count": 12345},
    {"name": "monthly", "group_id": "freq", "series_count": 123456},
    {"name": "sa", "group_id": "seas", "series_count": 98765}
  ]
}
```

**Insight:** US inflation data commonly uses CPI and PCE indicators, monthly frequency, seasonally adjusted.

---

### Example 5: Search Within Related Tags

**Goal:** Find inflation-related tags associated with BLS (Bureau of Labor Statistics)

```python
search_fred_related_tags(
    "bls",
    search_text="inflation",
    limit=15
)
```

**Result:**
```json
{
  "data": [
    {"name": "cpi", "group_id": "gen", "notes": "Consumer Price Index"},
    {"name": "core inflation", "group_id": "gen", "notes": "Inflation excluding food and energy"},
    {"name": "ppi", "group_id": "gen", "notes": "Producer Price Index"}
  ],
  "metadata": {
    "input_tags": ["bls"],
    "search_text": "inflation"
  }
}
```

**Use Case:** Discovering BLS's inflation measurement methodologies.

---

### Example 6: Sort by Popularity

**Goal:** Find FRED's recommended tags related to unemployment

```python
search_fred_related_tags(
    "unemployment",
    order_by="popularity",
    sort_order="desc",
    limit=10
)
```

**Result:**
```json
{
  "data": [
    {"name": "usa", "group_id": "geo", "popularity": 100},
    {"name": "nsa", "group_id": "seas", "popularity": 96},
    {"name": "monthly", "group_id": "freq", "popularity": 92},
    {"name": "bls", "group_id": "src", "popularity": 88}
  ]
}
```

**Benefit:** FRED's editorial team's recommendations for most useful related tags.

---

### Example 7: Complex Query - Build Effective Search

**Goal:** Find geography tags for employment data, excluding discontinued, ordered by data availability

```python
search_fred_related_tags(
    tag_names="employment;nsa",
    exclude_tag_names="discontinued",
    tag_group_id="geo",
    order_by="series_count",
    sort_order="desc",
    limit=25
)
```

**Result:**
```json
{
  "data": [
    {"name": "usa", "group_id": "geo", "series_count": 342567},
    {"name": "california", "group_id": "geo", "series_count": 12456},
    {"name": "texas", "group_id": "geo", "series_count": 11234},
    {"name": "new york", "group_id": "geo", "series_count": 10987}
  ],
  "metadata": {
    "input_tags": ["employment", "nsa"],
    "excluded_tags": ["discontinued"],
    "tag_group_id": "geo"
  }
}
```

**Workflow:** Now use these geography tags in `search_fred_series`:
```python
search_fred_series(
    "employment",
    tag_names="employment;nsa;usa",
    limit=20
)
```

---

## Use Cases

### 1. Tag Discovery Workflow

**Problem:** Don't know what tags exist for a topic

**Solution:**
```python
# Step 1: Start with a general tag
related = search_fred_related_tags("inflation")

# Step 2: Examine results, find interesting tags
# Result shows: cpi, pce, core inflation, headline inflation

# Step 3: Explore specific tag
cpi_related = search_fred_related_tags("cpi", tag_group_id="freq")

# Step 4: Use discovered tags in search
series = search_fred_series("consumer prices", tag_names="cpi;monthly;usa")
```

---

### 2. Data Source Exploration

**Problem:** What data sources provide employment statistics?

**Solution:**
```python
sources = search_fred_related_tags(
    "employment",
    tag_group_id="src",
    order_by="series_count",
    sort_order="desc"
)

# Results: bls, census, oecd, etc.
# Now you know which agencies produce employment data
```

---

### 3. Frequency Discovery

**Problem:** What data frequencies are available for a concept?

**Solution:**
```python
frequencies = search_fred_related_tags(
    "gdp",
    tag_group_id="freq"
)

# Results: quarterly (primary), annual, monthly
# Helps determine realistic data granularity expectations
```

---

### 4. Geographic Coverage

**Problem:** Which countries/regions have data for an indicator?

**Solution:**
```python
geographies = search_fred_related_tags(
    "gdp;quarterly",
    tag_group_id="geo",
    limit=100
)

# Results: usa, canada, japan, germany, uk, france, etc.
# Understand international data availability
```

---

### 5. Building Tag Combinations

**Problem:** Need to construct precise multi-tag filters

**Solution:**
```python
# Start broad
related = search_fred_related_tags("inflation")

# Narrow by frequency
freq_tags = search_fred_related_tags("inflation", tag_group_id="freq")
# Choose: monthly

# Narrow by geography
geo_tags = search_fred_related_tags("inflation;monthly", tag_group_id="geo")
# Choose: usa

# Narrow by source
src_tags = search_fred_related_tags("inflation;monthly;usa", tag_group_id="src")
# Choose: bls

# Final search with optimized tags
series = search_fred_series(
    "consumer price index",
    tag_names="inflation;monthly;usa;bls"
)
```

---

### 6. Discovering Seasonal Adjustment Options

**Problem:** Is data available both seasonally adjusted and not?

**Solution:**
```python
seasonal = search_fred_related_tags(
    "unemployment rate",
    tag_group_id="seas"
)

# Results: sa, nsa
# Both versions available - choose based on analysis needs
```

---

### 7. Finding Related Economic Concepts

**Problem:** What related economic indicators exist?

**Solution:**
```python
concepts = search_fred_related_tags(
    "gdp",
    tag_group_id="gen",
    order_by="popularity",
    sort_order="desc",
    limit=30
)

# Results: gnp, consumption, investment, government spending, net exports
# Discover components and related measures
```

---

## Tag Groups Reference

### freq - Frequency Tags

**Common Values:**
- `daily` - Daily frequency
- `weekly` - Weekly frequency
- `biweekly` - Biweekly frequency
- `monthly` - Monthly frequency
- `quarterly` - Quarterly frequency
- `semiannual` - Semiannual frequency
- `annual` - Annual frequency

**Use:** Determine data update frequency and granularity

---

### gen - General/Concept Tags

**Common Values:**
- `gdp` - Gross Domestic Product
- `gnp` - Gross National Product
- `cpi` - Consumer Price Index
- `ppi` - Producer Price Index
- `employment` - Employment data
- `unemployment` - Unemployment data
- `inflation` - Inflation measures
- `interest rate` - Interest rates
- `money stock` - Monetary aggregates (M1, M2, etc.)

**Use:** Identify economic concepts and indicators

---

### geo - Geography Tags

**Common Values:**
- `usa` - United States
- `canada` - Canada
- `japan` - Japan
- `germany` - Germany
- `uk` - United Kingdom
- `france` - France
- `china` - China
- `california` - US state
- `new york` - US state

**Use:** Filter by country, region, or state

---

### geot - Geography Type Tags

**Common Values:**
- `nation` - National level
- `state` - State level
- `county` - County level
- `msa` - Metropolitan Statistical Area
- `region` - Regional aggregations

**Use:** Understand geographic aggregation level

---

### rls - Release Tags

**Common Values:**
- `employment situation` - Monthly employment report
- `gdp release` - Quarterly GDP report
- `cpi release` - Monthly CPI report

**Use:** Group data by official statistical releases

---

### seas - Seasonal Adjustment Tags

**Values:**
- `sa` - Seasonally Adjusted
- `nsa` - Not Seasonally Adjusted
- `saar` - Seasonally Adjusted Annual Rate

**Use:** Critical for time series analysis - choose based on methodology needs

---

### src - Source Tags

**Common Values:**
- `bls` - U.S. Bureau of Labor Statistics
- `bea` - U.S. Bureau of Economic Analysis
- `census` - U.S. Census Bureau
- `frb` - Federal Reserve Board
- `oecd` - Organisation for Economic Co-operation and Development
- `eurostat` - European Statistical Office
- `imf` - International Monetary Fund

**Use:** Understand data provenance and methodology

---

## Error Handling

### Common Errors

#### Missing Required Parameter

**Error:**
```json
{
  "error": "Invalid parameters: tag_names is required",
  "input_tags": []
}
```

**Cause:** Called without `tag_names` parameter

**Fix:**
```python
# Wrong
search_fred_related_tags()

# Right
search_fred_related_tags("gdp")
```

---

#### Invalid Tag Names

**Error:**
```json
{
  "data": [],
  "metadata": {
    "total_count": 0,
    "returned_count": 0
  }
}
```

**Cause:** Tag names don't exist in FRED

**Fix:** Use `get_fred_tags` to discover valid tag names first:
```python
# Discover valid tags
tags = get_fred_tags(search_text="employment")

# Use discovered tag names
related = search_fred_related_tags("employment")  # Valid
```

---

#### Rate Limit Exceeded

**Error:**
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

**Cause:** Too many API requests in short time

**Fix:**
- Wait 30-60 seconds before retrying
- Implement request throttling in your application
- Use caching to reduce duplicate requests

---

#### Invalid tag_group_id

**Error:**
```json
{
  "error": "Invalid parameters: tag_group_id must be one of: freq, gen, geo, geot, rls, seas, src"
}
```

**Cause:** Used `"cc"` or invalid group value

**Fix:**
```python
# Wrong
search_fred_related_tags("gdp", tag_group_id="cc")

# Right
search_fred_related_tags("gdp", tag_group_id="freq")
```

---

## Performance

### Response Time

- **Typical:** 0.5-1.0 seconds
- **With filters:** 0.5-1.5 seconds
- **High limit (500+):** 1-2 seconds

### Optimization Tips

1. **Use appropriate limits**
   - Default 50 is optimized for most use cases
   - Avoid 1000 unless truly needed

2. **Cache results**
   - Tag relationships change infrequently
   - Cache for 24 hours minimum

3. **Batch operations**
   - Don't call for every tag individually
   - Use multiple input tags in single call

4. **Retry mechanism**
   - Tool has 3-attempt retry with exponential backoff (1-5s)
   - Handles transient failures automatically

### Token Efficiency

**Compact JSON format:**
- Saves ~25% tokens vs pretty-printed JSON
- Optimized for AI/LLM consumption
- Default limit (50) balances information density

**Typical response size:**
```
10 tags  H 2,000 tokens
50 tags  H 6,000 tokens
100 tags H 11,000 tokens
```

---

## Best Practices

### 1. Start Broad, Then Narrow

```python
# Good workflow
step1 = search_fred_related_tags("employment")  # Explore
step2 = search_fred_related_tags("employment", tag_group_id="freq")  # Narrow
step3 = search_fred_related_tags("employment;monthly", tag_group_id="geo")  # Refine
```

---

### 2. Use with get_fred_tags

```python
# Comprehensive discovery workflow

# 1. Find base tags
base_tags = get_fred_tags(search_text="inflation")

# 2. Explore relationships
related = search_fred_related_tags("inflation")

# 3. Examine specific groups
freq_tags = search_fred_related_tags("inflation", tag_group_id="freq")
geo_tags = search_fred_related_tags("inflation", tag_group_id="geo")

# 4. Build final search
series = search_fred_series(
    "consumer price",
    tag_names="cpi;monthly;usa"
)
```

---

### 3. Validate Before Using Tags

```python
# Don't assume - verify first
related = search_fred_related_tags("myindicator")

if related["metadata"]["total_count"] == 0:
    print("No related tags found - check tag name")
else:
    # Proceed with results
    for tag in related["data"]:
        print(f"Found: {tag['name']}")
```

---

### 4. Leverage series_count

```python
# Find tags with most data
search_fred_related_tags(
    "gdp",
    order_by="series_count",
    sort_order="desc",
    limit=20
)

# Tags with high series_count = more data availability
```

---

### 5. Exclude Noise

```python
# Clean results by excluding common noise tags
search_fred_related_tags(
    "economic indicators",
    exclude_tag_names="discontinued;revision;preliminary",
    limit=30
)
```

---

## Related Tools

### Complementary Tools

1. **`get_fred_tags`**
   - Discover available tags
   - **Use before** `search_fred_related_tags`

2. **`search_fred_series`**
   - Search for series using discovered tags
   - **Use after** `search_fred_related_tags`

3. **`fetch_fred_series`**
   - Retrieve actual time series data
   - **Use after** finding series IDs

### Typical Workflow

```python
# 1. Discover base tags
tags = get_fred_tags(search_text="employment")

# 2. Explore relationships
related = search_fred_related_tags("employment")

# 3. Search for series
series = search_fred_series(
    "labor force",
    tag_names="employment;monthly;usa;nsa"
)

# 4. Fetch data
data = fetch_fred_series("UNRATE")
```

---

## Version Information

- **Tool Version:** Introduced in v0.1.3
- **FRED API Version:** Uses FRED API
- **Last Updated:** 2025-11-01

---

## Support & Resources

- **FRED API Documentation:** https://fred.stlouisfed.org/docs/api/fred/
- **FRED Tags Endpoint:** https://fred.stlouisfed.org/docs/api/fred/related_tags.html
- **Tag Search Tool:** https://fred.stlouisfed.org/tags/
- **FRED Homepage:** https://fred.stlouisfed.org/

---

## Summary

The `search_fred_related_tags` tool is essential for:

 Discovering tag relationships in FRED's taxonomy
 Exploring related economic concepts and indicators
 Building effective multi-tag search filters
 Understanding data availability across frequencies, geographies, and sources
 Refining searches by finding complementary tags

**Key Strengths:**
- Fast, AI-optimized responses
- Flexible filtering and sorting
- Comprehensive tag metadata
- Integration with other FRED tools

**Best For:**
- Data exploration and discovery
- Building complex search queries
- Understanding FRED's data organization
- Finding associated economic indicators
