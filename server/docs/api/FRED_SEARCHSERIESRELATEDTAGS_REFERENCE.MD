# FRED Series Search Related Tags API Reference

**Tool Name:** `search_series_related_tags`

**Endpoint:** `https://api.stlouisfed.org/fred/series/search/related_tags`

**Description:** Get FRED tags that are related to specified tags within the context of series matching a search query. This tool discovers tags that co-occur with your input tags in series matching specific search text, enabling context-aware tag discovery and refined series searches.

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
10. [Comparison with Other Tag Tools](#comparison-with-other-tag-tools)

---

## Overview

The `search_series_related_tags` tool discovers tags that are related to your specified input tags **within the context of series matching a search query**. Unlike `search_fred_related_tags` which finds global tag relationships, this tool is **context-aware** and only considers tags from series that match your search text.

### Key Differences from `search_fred_related_tags`

| Feature | `search_fred_related_tags` | `search_series_related_tags` |
|---------|---------------------------|------------------------------|
| **Context** | Global (all FRED data) | Series search results only |
| **Input** | Tags only | Search text + tags |
| **Results** | All related tags | Related tags in search context |
| **Use Case** | General tag exploration | Refine specific searches |

### Key Features

- **Context-aware discovery**: Find related tags only within series matching your search
- **Dual filtering**: Combine series search with tag filtering for precise discovery
- **Group filtering**: Focus on specific tag groups (frequency, geography, source, etc.)
- **Exclusion support**: Remove unwanted tags from results
- **Tag search**: Additional keyword filtering within related tags
- **Flexible sorting**: Order by series count, popularity, creation date, name, or group
- **AI-optimized**: Default 50-result limit, compact JSON format
- **Retry logic**: Automatic retries with exponential backoff (3 attempts, 1-5s)

---

## Parameters

### Required Parameters

#### `series_search_text` (string, REQUIRED)

The words to match against economic data series. Searches series titles and descriptions.

**Format:** `"search terms"`

**Examples:**
```python
"mortgage rate"           # Find mortgage rate series
"GDP"                     # Find GDP-related series
"unemployment"            # Find unemployment series
"consumer price index"    # Find CPI series
"federal funds"           # Find federal funds rate series
```

**Search Behavior:**
- Case-insensitive
- Matches words in series **title** and **description**
- Multiple words create an **AND** query (all words must match)
- Partial word matching supported

---

#### `tag_names` (string, REQUIRED)

Semicolon-delimited list of tag names that series **must have** to be included in the search context.

**Format:** `"tag1;tag2;tag3"`

**Examples:**
```python
"30-year;frb"              # Series with both tags
"usa;monthly"              # USA monthly data
"nsa"                      # Not seasonally adjusted
"quarterly;sa;bea"         # Quarterly, SA, from BEA
```

**Important Notes:**
- Tag names are **case-insensitive**
- Must use **semicolons** (`;`) as delimiters, NOT commas
- Series must have **ALL** specified tags (AND logic)
- Invalid tag names will result in empty results

---

### Optional Parameters

#### `exclude_tag_names` (string, optional)

Semicolon-delimited list of tag names to **exclude** from related tag results.

**Default:** None

**Examples:**
```python
exclude_tag_names="discontinued"              # Exclude discontinued series tags
exclude_tag_names="discontinued;annual"       # Exclude multiple
exclude_tag_names="daily;weekly"              # Exclude high-frequency tags
```

**Use Cases:**
- Remove irrelevant or outdated data category tags
- Focus on specific frequencies by excluding others
- Filter out tags from copyright-restricted data

---

#### `tag_group_id` (string, optional)

Filter related tag results to a **specific group**.

**Default:** None (returns all groups)

**Valid Values:**
- `"freq"` - Frequency tags (monthly, quarterly, annual, daily, weekly, etc.)
- `"gen"` - General/concept tags (gdp, employment, inflation, interest rate, etc.)
- `"geo"` - Geography tags (usa, canada, japan, california, texas, etc.)
- `"geot"` - Geography type tags (nation, state, county, msa, cbsa)
- `"rls"` - Release tags (employment situation, gdp report, etc.)
- `"seas"` - Seasonal adjustment tags (sa, nsa)
- `"src"` - Source tags (bls, bea, census, frb, fred, etc.)

**Examples:**
```python
tag_group_id="freq"    # Only frequency-related tags
tag_group_id="geo"     # Only geography-related tags
tag_group_id="src"     # Only source-related tags
```

**Common Use Cases:**
- `"freq"`: Discover what data frequencies are available for your search
- `"geo"`: Find what geographies have data for your search
- `"src"`: Identify data sources for your search topic

---

#### `tag_search_text` (string, optional)

Filter related tags by **keyword match** in tag name or description.

**Default:** None

**Examples:**
```python
tag_search_text="inflation"     # Find inflation-related tags
tag_search_text="price"         # Find price-related tags
tag_search_text="employ"        # Find employment tags (partial match)
tag_search_text="state"         # Find state-level tags
```

**Behavior:**
- Case-insensitive matching
- Searches both tag names and tag descriptions (notes)
- Partial word matching supported
- Combines with other filters (tag_group_id, exclude_tag_names)

**Note:** This is different from `series_search_text`:
- `series_search_text`: Filters the **series** being searched
- `tag_search_text`: Filters the **related tags** returned

---

#### `limit` (integer, optional)

Maximum number of related tags to return.

**Default:** `50` (AI-optimized)

**Range:** 1 to 1000

**Examples:**
```python
limit=10     # Quick overview of top tags
limit=50     # Default (balanced for AI consumption)
limit=100    # Comprehensive tag discovery
```

**Recommendations:**
- **10-20**: Quick exploration of most relevant tags
- **50**: Default for most AI/LLM use cases
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

**Note:** For AI/LLM use cases, pagination is rarely needed. Use appropriate `limit` instead.

---

#### `order_by` (string, optional)

Field to sort related tags by.

**Default:** `"series_count"` (tags appearing in most series first)

**Valid Values:**
- `"series_count"` - Number of series using this tag (most common first)
- `"popularity"` - FRED's internal popularity score (0-100, highest first)
- `"created"` - Tag creation date (newest or oldest first depending on sort_order)
- `"name"` - Alphabetically by tag name
- `"group_id"` - By tag group (alphabetical group order)

**Examples:**
```python
order_by="series_count"    # Most common tags first (default)
order_by="popularity"      # Most popular tags first
order_by="name"            # Alphabetical order
order_by="created"         # Chronological order
```

**Recommendations:**
- **series_count**: Best for finding most relevant/common tags
- **popularity**: FRED's curated importance ranking
- **name**: Useful for organized lists or documentation
- **created**: Discover newly added tags or historical tags

---

#### `sort_order` (string, optional)

Sort direction.

**Default:** `"desc"` (descending - highest/newest first)

**Valid Values:**
- `"asc"` - Ascending (lowest to highest, oldest to newest, A to Z)
- `"desc"` - Descending (highest to lowest, newest to oldest, Z to A)

**Examples:**
```python
# Most common tags first
order_by="series_count", sort_order="desc"

# Least common tags first
order_by="series_count", sort_order="asc"

# Alphabetical A-Z
order_by="name", sort_order="asc"

# Alphabetical Z-A
order_by="name", sort_order="desc"

# Newest tags first
order_by="created", sort_order="desc"

# Oldest tags first
order_by="created", sort_order="asc"
```

---

#### `realtime_start` (string, optional)

Start date for real-time period query. Returns tags as they existed on this date.

**Default:** Today's date

**Format:** `"YYYY-MM-DD"`

**Examples:**
```python
realtime_start="2020-01-01"     # Tags as of January 1, 2020
realtime_start="2023-06-15"     # Tags as of June 15, 2023
```

**Use Cases:**
- Historical research requiring tag metadata as it existed at a specific time
- Tracking how tag relationships have changed over time
- Reproducing past analyses with period-accurate tag data

---

#### `realtime_end` (string, optional)

End date for real-time period query.

**Default:** Today's date

**Format:** `"YYYY-MM-DD"`

**Examples:**
```python
# Tags during 2020
realtime_start="2020-01-01", realtime_end="2020-12-31"

# Tags during Q1 2023
realtime_start="2023-01-01", realtime_end="2023-03-31"
```

**Note:** When both `realtime_start` and `realtime_end` are specified, returns tags as they existed during that time window.

---

## Response Format

### Success Response Structure

```json
{
  "tool": "search_series_related_tags",
  "data": [
    {
      "name": "conventional",
      "group_id": "gen",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 63,
      "series_count": 3
    },
    {
      "name": "discontinued",
      "group_id": "gen",
      "notes": "Series is no longer updated.",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 51,
      "series_count": 3
    },
    {
      "name": "interest rate",
      "group_id": "gen",
      "notes": "",
      "created": "2012-05-29 10:14:19-05",
      "popularity": 87,
      "series_count": 3
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "series_search_text": "mortgage rate",
    "input_tags": ["30-year", "frb"],
    "excluded_tags": null,
    "tag_group_id": null,
    "tag_search_text": null,
    "total_count": 13,
    "returned_count": 3,
    "limit": 50,
    "offset": 0,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

### Response Fields

#### `data` Array

Array of related tag objects. Each tag includes:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Tag name (lowercase, hyphenated) |
| `group_id` | string | Tag group: freq, gen, geo, geot, rls, seas, src |
| `notes` | string | Human-readable description (may be empty) |
| `created` | string | ISO timestamp when tag was created |
| `popularity` | integer | FRED popularity score (0-100, higher = more important) |
| `series_count` | integer | Number of series with this tag |

#### `metadata` Object

Comprehensive metadata about the query and results:

| Field | Type | Description |
|-------|------|-------------|
| `fetch_date` | string | UTC timestamp when data was fetched |
| `series_search_text` | string | The series search text used |
| `input_tags` | array | Tags that series must have |
| `excluded_tags` | array/null | Tags excluded from results |
| `tag_group_id` | string/null | Tag group filter applied |
| `tag_search_text` | string/null | Keyword filter applied to tags |
| `total_count` | integer | Total related tags available |
| `returned_count` | integer | Number of tags in this response |
| `limit` | integer | Maximum tags requested |
| `offset` | integer | Starting position for pagination |
| `order_by` | string | Sort field used |
| `sort_order` | string | Sort direction (asc/desc) |
| `realtime_start` | string | Real-time period start date |
| `realtime_end` | string | Real-time period end date |

---

### Error Response Structure

```json
{
  "tool": "search_series_related_tags",
  "error": "Invalid parameters: tag_names is required",
  "series_search_text": "mortgage rate",
  "input_tags": []
}
```

**Common Errors:**
- `"Invalid parameters"` - Missing required parameters or invalid values
- `"Rate limit exceeded"` - Too many requests, retry after waiting
- `"FRED API error: 400"` - Bad request (check parameter formats)
- `"FRED API error: 500"` - FRED server error (transient, retry)

---

## Usage Examples

### Example 1: Basic Usage - Find Related Tags for Mortgage Rate Search

**Goal:** Discover what other tags appear with "30-year" and "frb" in mortgage rate series.

```python
result = search_series_related_tags("mortgage rate", "30-year;frb")
```

**Response:**
```json
{
  "data": [
    {"name": "conventional", "group_id": "gen", "popularity": 63, "series_count": 3},
    {"name": "discontinued", "group_id": "gen", "popularity": 51, "series_count": 3},
    {"name": "interest rate", "group_id": "gen", "popularity": 87, "series_count": 3},
    {"name": "mortgage", "group_id": "gen", "popularity": 62, "series_count": 3}
  ],
  "metadata": {
    "series_search_text": "mortgage rate",
    "input_tags": ["30-year", "frb"],
    "total_count": 13
  }
}
```

**Insight:** Series with "30-year" and "frb" tags are also tagged as "conventional", "interest rate", and "mortgage".

---

### Example 2: Find Available Frequencies for GDP Data

**Goal:** Discover what data frequencies are available for GDP series tagged as "usa".

```python
result = search_series_related_tags(
    series_search_text="GDP",
    tag_names="usa",
    tag_group_id="freq"
)
```

**Response:**
```json
{
  "data": [
    {"name": "quarterly", "group_id": "freq", "series_count": 1245},
    {"name": "annual", "group_id": "freq", "series_count": 823},
    {"name": "monthly", "group_id": "freq", "series_count": 156}
  ],
  "metadata": {
    "series_search_text": "GDP",
    "input_tags": ["usa"],
    "tag_group_id": "freq",
    "total_count": 3
  }
}
```

**Insight:** Most GDP series are quarterly (1245 series), followed by annual (823) and monthly (156).

---

### Example 3: Exclude Discontinued Series Tags

**Goal:** Find related tags for employment data, excluding tags from discontinued series.

```python
result = search_series_related_tags(
    series_search_text="employment",
    tag_names="monthly;nsa",
    exclude_tag_names="discontinued",
    limit=20
)
```

**Use Case:** Focus on currently maintained series only.

---

### Example 4: Search for Inflation-Related Tags in CPI Context

**Goal:** Find inflation-related tags within Consumer Price Index series.

```python
result = search_series_related_tags(
    series_search_text="consumer price",
    tag_names="usa;monthly",
    tag_search_text="inflation",
    limit=15
)
```

**Response:**
```json
{
  "data": [
    {"name": "core inflation", "group_id": "gen"},
    {"name": "headline inflation", "group_id": "gen"},
    {"name": "inflation rate", "group_id": "gen"}
  ],
  "metadata": {
    "series_search_text": "consumer price",
    "input_tags": ["usa", "monthly"],
    "tag_search_text": "inflation"
  }
}
```

---

### Example 5: Find Data Sources for Unemployment Data

**Goal:** Identify what agencies provide monthly USA unemployment data.

```python
result = search_series_related_tags(
    series_search_text="unemployment rate",
    tag_names="usa;monthly",
    tag_group_id="src",
    order_by="popularity",
    sort_order="desc"
)
```

**Response:**
```json
{
  "data": [
    {"name": "bls", "group_id": "src", "popularity": 95, "series_count": 523},
    {"name": "oecd", "group_id": "src", "popularity": 78, "series_count": 45},
    {"name": "census", "group_id": "src", "popularity": 72, "series_count": 23}
  ]
}
```

**Insight:** BLS is the primary source (95 popularity, 523 series), followed by OECD and Census.

---

### Example 6: Find Geographic Coverage for Interest Rate Data

**Goal:** Discover what geographic levels have interest rate data from the Federal Reserve.

```python
result = search_series_related_tags(
    series_search_text="interest rate",
    tag_names="frb",
    tag_group_id="geo",
    limit=30
)
```

**Use Case:** Understand geographic coverage for Federal Reserve interest rate data.

---

### Example 7: Complete Refinement Workflow

**Goal:** Progressively refine a search by discovering related tags.

```python
# Step 1: Start with broad search
step1 = search_series_related_tags("inflation", "usa")
# Discover: monthly, quarterly, annual, cpi, pce, bls, bea, etc.

# Step 2: Add frequency filter
step2 = search_series_related_tags("inflation", "usa;monthly")
# Discover: cpi, pce, sa, nsa, bls, etc.

# Step 3: Add seasonal adjustment
step3 = search_series_related_tags("inflation", "usa;monthly;sa")
# Discover: cpi, pce, bls, core, headline, etc.

# Step 4: Use discovered tags in series search
series = search_fred_series("inflation", tag_names="usa;monthly;sa;cpi")
# Get: Precise filtered series list
```

---

### Example 8: Historical Tag Relationships

**Goal:** See what tags were related to GDP data in 2020.

```python
result = search_series_related_tags(
    series_search_text="GDP",
    tag_names="usa;quarterly",
    realtime_start="2020-01-01",
    realtime_end="2020-12-31"
)
```

**Use Case:** Historical research or reproducing past analyses with period-accurate tag metadata.

---

## Use Cases

### Use Case 1: Progressive Search Refinement

**Scenario:** You're searching for economic data but getting too many results. You need to discover what filtering options are available.

**Solution:**
```python
# Step 1: See what tags are available for your search
tags = search_series_related_tags("employment", "usa")
# Discover: monthly, quarterly, sa, nsa, bls, census, etc.

# Step 2: Add frequency
monthly_tags = search_series_related_tags("employment", "usa;monthly")
# Discover: sa, nsa, bls, state-level tags

# Step 3: Add seasonal adjustment
sa_tags = search_series_related_tags("employment", "usa;monthly;sa")
# Discover: bls, total, civilian, etc.

# Step 4: Build precise search
series = search_fred_series("employment", tag_names="usa;monthly;sa;bls")
```

**Benefits:**
- Discover available filters incrementally
- Build precise queries without guessing
- Understand data structure through exploration

---

### Use Case 2: Data Source Discovery

**Scenario:** You need to know what agencies provide data for your topic.

**Solution:**
```python
sources = search_series_related_tags(
    series_search_text="GDP",
    tag_names="usa;quarterly",
    tag_group_id="src",
    order_by="popularity",
    sort_order="desc"
)
# Returns: bea (primary), oecd, imf, etc.
```

**Benefits:**
- Identify authoritative sources
- Compare data availability across agencies
- Choose appropriate source for your analysis

---

### Use Case 3: Frequency Availability Check

**Scenario:** You need monthly data but want to check if it's available for your topic.

**Solution:**
```python
frequencies = search_series_related_tags(
    series_search_text="consumer confidence",
    tag_names="usa",
    tag_group_id="freq",
    order_by="series_count",
    sort_order="desc"
)
# Check if "monthly" appears with high series_count
```

**Benefits:**
- Verify data frequency availability before detailed search
- Discover alternative frequencies if preferred one unavailable
- Understand temporal coverage of your topic

---

### Use Case 4: Geographic Coverage Exploration

**Scenario:** You need to know what geographic levels have data for your indicator.

**Solution:**
```python
# Check geographic types available
geo_types = search_series_related_tags(
    series_search_text="unemployment",
    tag_names="monthly;sa;bls",
    tag_group_id="geot"
)
# Returns: nation, state, county, msa, etc.

# Check specific geographies
geographies = search_series_related_tags(
    series_search_text="unemployment",
    tag_names="monthly;sa;bls",
    tag_group_id="geo",
    limit=50
)
# Returns: usa, california, texas, new york, etc.
```

**Benefits:**
- Understand geographic granularity available
- Plan regional analysis scope
- Discover unexpected geographic coverage

---

### Use Case 5: Concept Discovery

**Scenario:** You're researching a topic and want to discover related economic concepts.

**Solution:**
```python
concepts = search_series_related_tags(
    series_search_text="housing",
    tag_names="usa;monthly",
    tag_group_id="gen",
    limit=50
)
# Discover: construction, permits, starts, sales, prices, mortgage, etc.
```

**Benefits:**
- Expand research scope systematically
- Discover related indicators you hadn't considered
- Build comprehensive economic indicator lists

---

### Use Case 6: Exclude Problematic Data Categories

**Scenario:** You want to exclude discontinued or low-quality series from your discovery.

**Solution:**
```python
clean_tags = search_series_related_tags(
    series_search_text="inflation",
    tag_names="usa;monthly",
    exclude_tag_names="discontinued;revision;preliminary",
    order_by="popularity",
    limit=20
)
```

**Benefits:**
- Focus on high-quality, maintained series
- Avoid including obsolete indicators
- Improve data reliability

---

### Use Case 7: Building Multi-Source Comparisons

**Scenario:** You want to compare how different agencies report the same indicator.

**Solution:**
```python
# Find all sources for unemployment data
sources = search_series_related_tags(
    series_search_text="unemployment rate",
    tag_names="usa;monthly;sa",
    tag_group_id="src"
)
# Returns: bls, oecd, imf, etc.

# For each source, search for series
for source in sources["data"]:
    series = search_fred_series(
        "unemployment rate",
        tag_names=f"usa;monthly;sa;{source['name']}"
    )
```

**Benefits:**
- Systematic cross-source comparison
- Identify methodology differences
- Validate data across agencies

---

## Tag Groups Reference

### Frequency Tags (`tag_group_id="freq"`)

Common frequency tags you'll encounter:

| Tag Name | Description | Typical Use |
|----------|-------------|-------------|
| `daily` | Daily data | Financial markets, Fed operations |
| `weekly` | Weekly data | Initial jobless claims, monetary aggregates |
| `biweekly` | Every two weeks | Some employment data |
| `monthly` | Monthly data | Most common: CPI, employment, retail sales |
| `quarterly` | Quarterly data | GDP, corporate earnings |
| `semiannual` | Twice per year | Some international data |
| `annual` | Annual data | Census data, some historical series |

---

### General/Concept Tags (`tag_group_id="gen"`)

Topical and concept tags (highly variable, thousands available):

**Common Examples:**
- `gdp`, `inflation`, `employment`, `unemployment`
- `interest rate`, `mortgage`, `federal funds`
- `cpi`, `pce`, `ppi` (price indices)
- `retail sales`, `industrial production`, `capacity utilization`
- `trade balance`, `imports`, `exports`

---

### Geography Tags (`tag_group_id="geo"`)

Specific geographic entities:

**National:**
- `usa`, `canada`, `japan`, `china`, `germany`, `united kingdom`

**US States:**
- `california`, `texas`, `new york`, `florida`, `illinois`

**US Metro Areas:**
- `new york-newark-jersey city ny-nj-pa`, `los angeles-long beach-anaheim ca`

---

### Geography Type Tags (`tag_group_id="geot"`)

Geographic classification levels:

| Tag Name | Description |
|----------|-------------|
| `nation` | Country-level data |
| `state` | US state-level |
| `county` | US county-level |
| `msa` | Metropolitan Statistical Area |
| `cbsa` | Core-Based Statistical Area |
| `region` | Regional groupings |

---

### Seasonal Adjustment Tags (`tag_group_id="seas"`)

| Tag Name | Full Name | Description |
|----------|-----------|-------------|
| `sa` | Seasonally Adjusted | Seasonal patterns removed |
| `nsa` | Not Seasonally Adjusted | Raw data with seasonal patterns |
| `saar` | Seasonally Adjusted Annual Rate | Annualized and seasonally adjusted |

---

### Source Tags (`tag_group_id="src"`)

Data provider agencies:

| Tag Name | Full Name |
|----------|-----------|
| `bls` | Bureau of Labor Statistics |
| `bea` | Bureau of Economic Analysis |
| `census` | US Census Bureau |
| `frb` | Federal Reserve Board |
| `fred` | Federal Reserve Economic Data (curated) |
| `oecd` | Organisation for Economic Co-operation and Development |
| `imf` | International Monetary Fund |
| `bis` | Bank for International Settlements |
| `ecb` | European Central Bank |

---

### Release Tags (`tag_group_id="rls"`)

Official data releases:

**Common Examples:**
- `employment situation`
- `consumer price index`
- `gross domestic product`
- `advance economic indicators`

---

## Error Handling

### Common Errors and Solutions

#### 1. Empty Results

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

**Possible Causes:**
- No series match your `series_search_text` + `tag_names` combination
- Invalid tag names
- Too restrictive filters (try removing some filters)

**Solutions:**
- Verify tag names with `get_fred_tags` tool
- Broaden your search (fewer tags, less restrictive search text)
- Check if series exist with `search_fred_series` first

---

#### 2. Rate Limit Error

**Error:**
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

**Cause:** Too many API requests in short time period.

**Solution:**
- Wait 10-60 seconds before retrying
- Implement exponential backoff (tool does this automatically)
- Reduce request frequency

---

#### 3. Invalid Tag Names

**Error:**
```json
{
  "error": "Invalid parameters: tag_names contains invalid tags"
}
```

**Cause:** One or more tag names don't exist in FRED.

**Solution:**
- Use `get_fred_tags` to discover valid tag names
- Check for typos in tag names
- Verify tag names are lowercase and hyphenated

---

#### 4. Bad Request (400)

**Error:**
```json
{
  "error": "Invalid parameters: Bad request"
}
```

**Possible Causes:**
- Missing required parameters (`series_search_text` or `tag_names`)
- Invalid parameter format (e.g., non-numeric `limit`)
- Invalid enum values (e.g., wrong `tag_group_id`)

**Solution:**
- Verify all required parameters are provided
- Check parameter value formats and types
- Ensure enum parameters use valid values

---

## Performance

### Response Times

**Typical Performance:**
- **Small result sets (< 20 tags):** 0.5-1.5 seconds
- **Medium result sets (20-50 tags):** 1.0-2.5 seconds
- **Large result sets (50+ tags):** 2.0-3.5 seconds
- **Complex searches with many filters:** 1.5-3.0 seconds

**Factors Affecting Performance:**
- **Series search complexity**: More matches = longer processing
- **Number of result tags**: More tags = larger response
- **Filter complexity**: Multiple filters may add 0.2-0.5s
- **FRED API load**: Peak times may be slower

### Optimization Features

The tool includes several performance optimizations:

1. **Retry Logic**: 3 automatic retries with exponential backoff (1-5s wait)
2. **Compact JSON**: ~25% smaller than pretty-printed (faster transfer, less token usage)
3. **Default Limit**: 50 results balances completeness with speed
4. **Connection Pooling**: Reuses HTTP connections (handled by requests library)
5. **Timeout Protection**: 30-second timeout prevents hanging requests

### Token Efficiency

**Typical Response Sizes:**
- **10 tags**: ~1,200 tokens
- **20 tags**: ~2,200 tokens
- **50 tags (default)**: ~5,000 tokens
- **100 tags**: ~9,500 tokens

**Metadata overhead**: ~300-400 tokens per response

**Recommendations for AI/LLM:**
- Use `limit=10-20` for quick explorations
- Use `limit=50` (default) for comprehensive but efficient results
- Use `limit=100+` only when full coverage needed

---

## Best Practices

### 1. Start Broad, Then Narrow

```python
# Step 1: Broad search to discover available tags
broad = search_series_related_tags("employment", "usa")

# Step 2: Add frequency based on discovery
monthly = search_series_related_tags("employment", "usa;monthly")

# Step 3: Add seasonal adjustment
refined = search_series_related_tags("employment", "usa;monthly;sa")

# Step 4: Use discovered tags in final series search
series = search_fred_series("employment", tag_names="usa;monthly;sa;bls")
```

**Why:** Incremental refinement ensures you don't miss relevant data.

---

### 2. Use Tag Group Filters for Focused Discovery

```python
# Find available frequencies
frequencies = search_series_related_tags(
    "GDP", "usa",
    tag_group_id="freq"
)

# Find data sources
sources = search_series_related_tags(
    "GDP", "usa",
    tag_group_id="src"
)

# Find geographic coverage
geographies = search_series_related_tags(
    "GDP", "usa",
    tag_group_id="geo"
)
```

**Why:** Focused queries return more actionable results faster.

---

### 3. Exclude Unwanted Categories Early

```python
# Exclude discontinued and low-quality series tags
clean_tags = search_series_related_tags(
    "inflation",
    "usa;monthly",
    exclude_tag_names="discontinued;revision;preliminary"
)
```

**Why:** Prevents wasting time on obsolete or low-quality data.

---

### 4. Use Popularity Sorting for Key Tags

```python
# Find most important related tags
important = search_series_related_tags(
    "unemployment",
    "usa;monthly",
    order_by="popularity",
    sort_order="desc",
    limit=10
)
```

**Why:** FRED's popularity scores help identify the most significant tags.

---

### 5. Verify Tag Existence First

```python
# Step 1: Verify tags exist
all_tags = get_fred_tags()
valid_tags = [t for t in ["usa", "monthly", "sa"] if t in all_tags]

# Step 2: Use verified tags
related = search_series_related_tags(
    "employment",
    ";".join(valid_tags)
)
```

**Why:** Prevents errors from invalid tag names.

---

### 6. Combine with Other Tools for Complete Workflow

```python
# Full discovery workflow:

# 1. Discover related tags
tags = search_series_related_tags("inflation", "usa;monthly")

# 2. Use discovered tags to search series
series_list = search_fred_series("inflation", tag_names="usa;monthly;sa;cpi")

# 3. Get tags for specific series to verify
series_tags = get_fred_series_tags("CPIAUCSL")

# 4. Retrieve observations
data = get_fred_series_observations("CPIAUCSL", units="pc1")
```

**Why:** Integrated workflow ensures comprehensive data discovery and retrieval.

---

### 7. Use Reasonable Limits for AI Consumption

```python
# Quick exploration: 10-20 tags
quick = search_series_related_tags("GDP", "usa", limit=10)

# Balanced (default): 50 tags
balanced = search_series_related_tags("GDP", "usa", limit=50)

# Comprehensive: 100+ tags
comprehensive = search_series_related_tags("GDP", "usa", limit=100)
```

**Why:** Balances completeness with token efficiency and processing speed.

---

## Comparison with Other Tag Tools

### When to Use Each Tool

| Tool | Use When | Context | Output |
|------|----------|---------|--------|
| `get_fred_tags` | Discover ALL available tags globally | No context | All FRED tags |
| `search_fred_related_tags` | Find globally related tags | Global relationships | Related tags (global) |
| `search_series_tags` | Find tags in search results | Series search context | Tags from matching series |
| **`search_series_related_tags`** | **Find related tags in search context** | **Series search + tag filter** | **Related tags (contextual)** |
| `get_fred_series_tags` | Get tags for ONE specific series | Single series | Tags for that series |

### Tool Workflow Integration

```python
# Complete tag discovery workflow:

# 1. Global tag discovery
all_tags = get_fred_tags(tag_group_id="freq")
# Learn: What frequencies exist globally

# 2. Search context tags
search_tags = search_series_tags("employment", "usa")
# Learn: What tags are on employment series

# 3. Related tags in search context (THIS TOOL)
related = search_series_related_tags("employment", "usa;monthly")
# Learn: What other tags appear with monthly employment series

# 4. Global tag relationships
global_related = search_fred_related_tags("employment")
# Learn: What tags are related to employment globally (not search-specific)

# 5. Specific series tags
series_tags = get_fred_series_tags("UNRATE")
# Learn: What tags does UNRATE have specifically
```

---

## Summary

**`search_series_related_tags` is the context-aware tag discovery tool:**

✅ **Context-Aware**: Discovers tags only within series matching your search
✅ **Dual Filtering**: Combines series search with tag requirements
✅ **Refinement Tool**: Perfect for progressive search refinement
✅ **7 Tag Groups**: Filter by frequency, geography, source, and more
✅ **Exclusion Support**: Remove unwanted tags from results
✅ **Flexible Sorting**: Order by popularity, series count, or other criteria
✅ **AI-Optimized**: Default 50-result limit, compact JSON format
✅ **Production Ready**: Retry logic, error handling, comprehensive metadata

**Use this tool when:**
- You're searching for specific series and want to refine the search
- You need to discover what filtering options are available for your search topic
- You want to understand tag relationships within a specific data domain
- You're building progressive query refinement workflows

**API Endpoint:** `https://api.stlouisfed.org/fred/series/search/related_tags`

**Version:** Added in v0.1.5
