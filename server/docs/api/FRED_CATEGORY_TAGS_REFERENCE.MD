# FRED Category Tags Tool – API Reference
## Tool: get_fred_category_tags

**Endpoint:** `https://api.stlouisfed.org/fred/category/tags`

**Description:** Get FRED tags for a specific category with optional filtering. Discover what tags are associated with series in a category to understand data characteristics.

---

## Table of Contents

1. [Overview](#overview)
2. [Parameters](#parameters)
3. [Response Format](#response-format)
4. [Usage Examples](#usage-examples)
5. [Use Cases](#use-cases)
6. [Tag Groups Explained](#tag-groups-explained)
7. [Filtering Strategies](#filtering-strategies)
8. [Error Handling](#error-handling)
9. [Performance](#performance)
10. [Best Practices](#best-practices)
11. [Related Tools](#related-tools)

---

## Overview

The `get_fred_category_tags` tool retrieves FRED tags associated with series in a specific category. Since series are assigned both tags and categories, this tool indirectly discovers tags through the series in the category. This is essential for understanding what types of data exist in a category before fetching series.

### Key Features

- **Tag Discovery**: Find what tags are used by series in a category
- **Type Filtering**: Filter by tag group (frequency, geography, source, etc.)
- **Search**: Find tags containing specific words
- **Sorting Options**: Order by series count, popularity, name, etc.
- **Pagination**: Support for large result sets (up to 1000 tags)
- **Fast Queries**: Typical response time < 0.5s
- **Compact JSON**: AI-optimized format

### Why Use Category Tags?

Category tags provide:
- **Data Characteristics**: Understand frequency, geography, source of data in a category
- **Pre-filtering**: Know what tags are available before searching series
- **Context**: See how FRED organizes data within a category
- **Discovery**: Find common themes and attributes across series
- **Query Building**: Construct better tag-based searches

### Important Note

**No tags exist for categories without series.** The tags come from series assigned to the category, so empty categories return no tags.

---

## Parameters

### Required Parameters

#### `category_id` (integer, REQUIRED)

The ID for a FRED category.

**Format:** Non-negative integer

**Examples:**
```python
125        # Trade Balance
32991      # Money, Banking, & Finance
32992      # National Accounts
125        # U.S. Trade & International Transactions
```

**Important Notes:**
- Must be a valid FRED category ID
- Category must have series to have tags
- Root category (0) aggregates tags from all series

---

### Optional Parameters

#### `realtime_start` (string, optional)

Start date for the real-time period.

**Format:** YYYY-MM-DD

**Default:** Today's date

**Examples:**
```python
"2024-01-01"
"2023-06-15"
"2025-11-01"
```

---

#### `realtime_end` (string, optional)

End date for the real-time period.

**Format:** YYYY-MM-DD

**Default:** Today's date

**Examples:**
```python
"2024-12-31"
"2023-12-31"
"2025-11-01"
```

**Note:** Must be >= realtime_start

---

#### `tag_names` (string, optional)

Semicolon-delimited list of tag names to filter by.

**Format:** Tag names separated by semicolons

**Default:** No filtering (all tags)

**Examples:**
```python
"trade"              # Only "trade" tag
"trade;goods"        # Only "trade" and "goods" tags
"nsa;quarterly"      # Only "nsa" and "quarterly" tags
```

**Use Cases:**
- Verify specific tags exist in category
- Get details about known tags
- Focus on subset of relevant tags

---

#### `tag_group_id` (string, optional)

Filter tags by type/group.

**Format:** One of the tag group codes

**Default:** No filtering (all groups)

**Valid Values:**
- **`"freq"`** - Frequency tags (monthly, quarterly, annual, etc.)
- **`"gen"`** - General/Concept tags (balance, trade, gdp, etc.)
- **`"geo"`** - Geography tags (usa, canada, japan, etc.)
- **`"geot"`** - Geography Type tags (nation, state, county, etc.)
- **`"rls"`** - Release tags
- **`"seas"`** - Seasonal Adjustment tags (sa, nsa)
- **`"src"`** - Source tags (bea, bls, census, etc.)

**Examples:**
```python
tag_group_id="freq"   # Only frequency tags
tag_group_id="geo"    # Only geography tags
tag_group_id="src"    # Only source tags
```

---

#### `search_text` (string, optional)

Search for tags containing specific words.

**Format:** Text string

**Default:** No search filtering

**Examples:**
```python
"balance"            # Tags containing "balance"
"employ"             # Tags containing "employ" (employment, employer, etc.)
"account"            # Tags containing "account"
```

**Important:**
- Case-insensitive search
- Partial word matching
- Searches tag name only

---

#### `limit` (integer, optional)

Maximum number of results to return.

**Format:** Integer between 1 and 1000

**Default:** 1000

**Examples:**
```python
50      # Top 50 tags
100     # Top 100 tags
1000    # All tags (up to max)
```

**Performance Notes:**
- Higher limits take slightly longer
- Default (1000) returns all tags for most categories
- Use lower limits for quick discovery

---

#### `offset` (integer, optional)

Starting offset for pagination.

**Format:** Non-negative integer

**Default:** 0

**Examples:**
```python
0       # Start from beginning
50      # Skip first 50 results
100     # Skip first 100 results
```

**Pagination Pattern:**
```python
# First page: limit=50, offset=0
# Second page: limit=50, offset=50
# Third page: limit=50, offset=100
```

---

#### `order_by` (string, optional)

Field to sort results by.

**Format:** One of the order_by values

**Default:** "series_count"

**Valid Values:**
- **`"series_count"`** - Number of series with this tag (default)
- **`"popularity"`** - FRED popularity score (0-100)
- **`"created"`** - When tag was created
- **`"name"`** - Tag name alphabetically
- **`"group_id"`** - Tag group/type

**Examples:**
```python
order_by="series_count"   # Most common tags first
order_by="popularity"     # Most popular tags first
order_by="name"           # Alphabetical order
```

---

#### `sort_order` (string, optional)

Sort direction for ordered results.

**Format:** "asc" or "desc"

**Default:** "desc"

**Examples:**
```python
sort_order="desc"   # Descending (high to low)
sort_order="asc"    # Ascending (low to high)
```

**Typical Combinations:**
- `order_by="series_count", sort_order="desc"` - Most common tags first
- `order_by="popularity", sort_order="desc"` - Most popular tags first
- `order_by="name", sort_order="asc"` - Alphabetical A-Z

---

## Response Format

### Success Response

```json
{
  "tool": "get_category_tags",
  "data": [
    {
      "name": "bea",
      "group_id": "src",
      "notes": "U.S. Department of Commerce: Bureau of Economic Analysis",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 87,
      "series_count": 24
    },
    {
      "name": "nation",
      "group_id": "geot",
      "notes": "Country Level",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 24
    },
    {
      "name": "usa",
      "group_id": "geo",
      "notes": "United States of America",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 24
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "count": 21,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

### Response Fields

#### `data` (array)

Array of tag objects. Each tag contains:

- **name** (string): Tag name
- **group_id** (string): Tag type/group code
  - "freq" = Frequency
  - "gen" = General/Concept
  - "geo" = Geography
  - "geot" = Geography Type
  - "rls" = Release
  - "seas" = Seasonal Adjustment
  - "src" = Source
- **notes** (string): Tag description (may be empty)
- **created** (string): Creation timestamp
- **popularity** (integer): FRED popularity score (0-100)
- **series_count** (integer): Number of series with this tag **in this category**

#### `metadata` (object)

Query metadata:
- **fetch_date** (string): UTC timestamp when data was retrieved
- **category_id** (integer): The input category ID
- **count** (integer): Total number of tags matching query
- **offset** (integer): Starting offset used
- **limit** (integer): Maximum results returned
- **order_by** (string): Sort field used
- **sort_order** (string): Sort direction used
- **realtime_start** (string): Real-time period start date
- **realtime_end** (string): Real-time period end date

**Optional metadata fields** (when filters used):
- **tag_group_id** (string): Tag group filter applied
- **search_text** (string): Search text filter applied
- **tag_names** (string): Tag names filter applied

---

### Empty Result Response

When a category has no series or no matching tags:

```json
{
  "tool": "get_category_tags",
  "data": [],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 999,
    "count": 0,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

---

### Error Response

```json
{
  "tool": "get_category_tags",
  "error": "Category not found or has no series: 999999",
  "category_id": 999999
}
```

---

## Usage Examples

### Example 1: Get All Tags for Trade Balance Category

**Request:**
```python
get_category_tags(category_id=125)
```

**Response:**
```json
{
  "tool": "get_category_tags",
  "data": [
    {
      "name": "bea",
      "group_id": "src",
      "notes": "U.S. Department of Commerce: Bureau of Economic Analysis",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 87,
      "series_count": 24
    },
    {
      "name": "nation",
      "group_id": "geot",
      "notes": "Country Level",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 24
    },
    {
      "name": "usa",
      "group_id": "geo",
      "notes": "United States of America",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 24
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "count": 21,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Explanation:**
Retrieves all 21 tags used by series in the Trade Balance category, ordered by how many series use each tag.

---

### Example 2: Get Only Frequency Tags

**Request:**
```python
get_category_tags(category_id=125, tag_group_id="freq")
```

**Response:**
```json
{
  "tool": "get_category_tags",
  "data": [
    {
      "name": "quarterly",
      "group_id": "freq",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 88,
      "series_count": 14
    },
    {
      "name": "annual",
      "group_id": "freq",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 83,
      "series_count": 7
    },
    {
      "name": "monthly",
      "group_id": "freq",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 95,
      "series_count": 3
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "count": 3,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "tag_group_id": "freq",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Explanation:**
Shows only frequency tags, revealing that the category has quarterly (14 series), annual (7 series), and monthly (3 series) data.

---

### Example 3: Search for Specific Tags

**Request:**
```python
get_category_tags(category_id=125, search_text="balance")
```

**Response:**
```json
{
  "tool": "get_category_tags",
  "data": [
    {
      "name": "balance",
      "group_id": "gen",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 65,
      "series_count": 18
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "count": 1,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "search_text": "balance",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Explanation:**
Searches for tags containing "balance" and finds one matching tag used by 18 series.

---

### Example 4: Get Specific Tags Only

**Request:**
```python
get_category_tags(category_id=125, tag_names="trade;goods")
```

**Response:**
```json
{
  "tool": "get_category_tags",
  "data": [
    {
      "name": "trade",
      "group_id": "gen",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 60,
      "series_count": 6
    },
    {
      "name": "goods",
      "group_id": "gen",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 73,
      "series_count": 5
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "count": 2,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "tag_names": "trade;goods",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Explanation:**
Returns information only about the "trade" and "goods" tags in this category.

---

### Example 5: Top 50 Tags by Popularity

**Request:**
```python
get_category_tags(
    category_id=125,
    limit=50,
    order_by="popularity",
    sort_order="desc"
)
```

**Response:**
```json
{
  "tool": "get_category_tags",
  "data": [
    {
      "name": "nation",
      "group_id": "geot",
      "notes": "Country Level",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 24
    },
    {
      "name": "usa",
      "group_id": "geo",
      "notes": "United States of America",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 24
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "count": 21,
    "offset": 0,
    "limit": 50,
    "order_by": "popularity",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Explanation:**
Returns up to 50 tags ordered by FRED popularity score, showing most popular tags first.

---

## Use Cases

### 1. Discover Data Characteristics

**Scenario:** Understand what types of data are in a category before fetching series.

**Example:**
```python
# Get all tags for Money, Banking, & Finance
tags = get_category_tags(32991)

# Check frequency tags
freq_tags = get_category_tags(32991, tag_group_id="freq")
# Shows: monthly, quarterly, annual, etc.

# Check geography
geo_tags = get_category_tags(32991, tag_group_id="geo")
# Shows: usa, europe, japan, etc.

# Check sources
source_tags = get_category_tags(32991, tag_group_id="src")
# Shows: bea, fed, etc.
```

**Benefits:**
- Understand data before querying series
- Know what filters are available
- Plan search strategy

---

### 2. Build Tag-Based Searches

**Scenario:** Construct effective tag-based series searches.

**Example:**
```python
# 1. Discover available tags in category
tags = get_category_tags(125)

# 2. Filter to find relevant tags
freq_tags = get_category_tags(125, tag_group_id="freq")
# Result: quarterly, annual, monthly

# 3. Use tags to search series
series = search_fred_series(
    search_text="trade balance",
    tag_names="quarterly;sa"  # Use discovered tags
)
```

---

### 3. Category Data Profiling

**Scenario:** Analyze what data is available in a category.

**Example:**
```python
# Get category info
category = get_category(125)
print(f"Category: {category['data']['name']}")

# Profile tags by group
for group in ["freq", "geo", "src", "seas"]:
    tags = get_category_tags(125, tag_group_id=group)
    print(f"{group}: {tags['metadata']['count']} tags")
    for tag in tags['data'][:3]:  # Top 3
        print(f"  - {tag['name']} ({tag['series_count']} series)")
```

**Output:**
```
Category: Trade Balance
freq: 3 tags
  - quarterly (14 series)
  - annual (7 series)
  - monthly (3 series)
geo: 1 tag
  - usa (24 series)
src: 2 tags
  - bea (24 series)
  - census (3 series)
seas: 2 tags
  - nsa (14 series)
  - sa (10 series)
```

---

### 4. Validate Tag Availability

**Scenario:** Check if specific tags exist in a category before using them.

**Example:**
```python
# Check if "quarterly" and "sa" tags exist
tags = get_category_tags(125, tag_names="quarterly;sa")

if tags['metadata']['count'] == 2:
    print("Both tags available!")
    # Safe to use in series search
    series = get_category_series(125, tag_names="quarterly;sa")
else:
    print("Tags not available in this category")
```

---

### 5. Popular Tags Discovery

**Scenario:** Find the most commonly used tags in a category.

**Example:**
```python
# Get top 10 most common tags
tags = get_category_tags(
    category_id=125,
    limit=10,
    order_by="series_count",
    sort_order="desc"
)

print("Top 10 most common tags:")
for tag in tags['data']:
    print(f"{tag['name']}: {tag['series_count']} series")
```

---

## Tag Groups Explained

### Tag Group Reference

| Group ID | Name | Purpose | Examples |
|----------|------|---------|----------|
| **freq** | Frequency | Data frequency | monthly, quarterly, annual, weekly, daily |
| **gen** | General/Concept | Economic concepts | gdp, inflation, employment, balance, trade |
| **geo** | Geography | Geographic entities | usa, canada, japan, europe, china |
| **geot** | Geography Type | Geographic level | nation, state, county, msa, cbsa |
| **rls** | Release | Data releases | employment situation, gdp advance, cpi |
| **seas** | Seasonal Adjustment | Adjustment type | sa (seasonally adjusted), nsa (not adjusted) |
| **src** | Source | Data source | bea, bls, census, fed, ecb |

### Frequency Tags (freq)

Common values:
- **daily** - Daily data
- **weekly** - Weekly data (e.g., initial claims)
- **biweekly** - Every two weeks
- **monthly** - Monthly data (most common)
- **quarterly** - Quarterly data (e.g., GDP)
- **semiannual** - Twice per year
- **annual** - Yearly data

### General/Concept Tags (gen)

Thematic tags describing data content:
- **gdp** - Gross Domestic Product
- **inflation** - Price changes
- **employment** - Labor market
- **interest** - Interest rates
- **balance** - Balance of payments/trade
- **income** - Income data
- **investment** - Investment flows

### Geography Tags (geo)

Geographic entities:
- **usa** - United States
- **canada** - Canada
- **japan** - Japan
- **europe** - European region
- **china** - China
- **uk** - United Kingdom

### Geography Type Tags (geot)

Administrative levels:
- **nation** - Country level
- **state** - U.S. state level
- **county** - U.S. county level
- **msa** - Metropolitan Statistical Area
- **region** - Multi-state region

### Seasonal Adjustment Tags (seas)

- **sa** - Seasonally Adjusted (removes seasonal patterns)
- **nsa** - Not Seasonally Adjusted (raw data)
- **saar** - Seasonally Adjusted Annual Rate

### Source Tags (src)

Data providers:
- **bea** - Bureau of Economic Analysis
- **bls** - Bureau of Labor Statistics
- **census** - Census Bureau
- **fed** - Federal Reserve
- **frb** - Federal Reserve Bank
- **oecd** - OECD

---

## Filtering Strategies

### Strategy 1: Narrow by Type

Start broad, then filter by tag group:

```python
# 1. Get all tags
all_tags = get_category_tags(125)
# Returns 21 tags

# 2. Focus on frequency
freq_tags = get_category_tags(125, tag_group_id="freq")
# Returns 3 tags: quarterly, annual, monthly

# 3. Focus on sources
source_tags = get_category_tags(125, tag_group_id="src")
# Returns 2 tags: bea, census
```

---

### Strategy 2: Search Then Filter

Search for keywords, then refine:

```python
# 1. Search for concept
balance_tags = get_category_tags(125, search_text="balance")
# Returns tags containing "balance"

# 2. Search for frequency
quarter_tags = get_category_tags(125, search_text="quarter")
# Returns "quarterly"

# 3. Combine with group filter
annual_tags = get_category_tags(125, tag_group_id="freq", search_text="annual")
# Returns only "annual" frequency tag
```

---

### Strategy 3: Verify Known Tags

Check if specific tags exist before using:

```python
# Check if we can filter by "quarterly" and "sa"
tags = get_category_tags(125, tag_names="quarterly;sa")

if tags['metadata']['count'] == 2:
    # Both tags exist, safe to use
    series = get_category_series(125, tag_names="quarterly;sa")
```

---

### Strategy 4: Progressive Discovery

Build tag knowledge incrementally:

```python
# 1. Start with category
category = get_category(125)

# 2. See all tags
tags = get_category_tags(125, limit=20)

# 3. Explore each group
for group in ["freq", "geo", "src", "seas", "gen"]:
    group_tags = get_category_tags(125, tag_group_id=group)
    print(f"{group}: {[t['name'] for t in group_tags['data']]}")

# 4. Use discovered tags
series = get_category_series(125, tag_names="quarterly;nsa;bea")
```

---

## Error Handling

### Common Errors

#### 1. Invalid Category ID

**Error:**
```json
{
  "tool": "get_category_tags",
  "error": "Invalid category_id: must be a non-negative integer"
}
```

**Cause:** Category ID is negative or invalid

**Solution:** Use non-negative integer category IDs

---

#### 2. Category Not Found or No Series

**Error:**
```json
{
  "tool": "get_category_tags",
  "error": "Category not found or has no series: 999999",
  "category_id": 999999
}
```

**Cause:** Category doesn't exist or has no series

**Solution:**
- Verify category ID using `get_category`
- Check if category has series using `get_category_series`

---

#### 3. Invalid Tag Group

**Error:**
```json
{
  "tool": "get_category_tags",
  "error": "Invalid parameters: tag_group_id must be one of: freq, gen, geo, geot, rls, seas, src",
  "category_id": 125
}
```

**Cause:** Invalid tag_group_id value

**Solution:** Use valid tag group: "freq", "gen", "geo", "geot", "rls", "seas", "src"

---

#### 4. Rate Limit Exceeded

**Error:**
```json
{
  "tool": "get_category_tags",
  "error": "Rate limit exceeded. Please try again later.",
  "category_id": 125
}
```

**Cause:** Too many requests to FRED API

**Solution:** Wait and retry. Tool has built-in exponential backoff (3 retries)

---

## Performance

### Response Times

| Scenario | Typical Time | Max Time |
|----------|-------------|----------|
| Small categories (<50 tags) | 150-400ms | 800ms |
| Medium categories (50-200 tags) | 200-500ms | 1s |
| Large categories (200+ tags) | 300-600ms | 1.5s |
| With filters applied | 150-400ms | 800ms |
| First request (cold) | 300-600ms | 1.5s |

### Performance Characteristics

- **Fast Filtering**: Applying filters doesn't significantly impact response time
- **No Complex Queries**: Tags are pre-indexed, responses are fast
- **Pagination Support**: Use limit/offset for controlled data transfer
- **Retry Logic**: 3 attempts with exponential backoff (1-5s)
- **Compact JSON**: AI-optimized format minimizes token usage
- **Session Reuse**: HTTP connection pooling for efficiency

### Optimization Tips

1. **Use Appropriate Limits**
   ```python
   # For discovery: low limit
   tags = get_category_tags(125, limit=20)
   
   # For complete data: default limit
   tags = get_category_tags(125)  # limit=1000 default
   ```

2. **Filter Early**
   ```python
   # More efficient: filter on API side
   tags = get_category_tags(125, tag_group_id="freq")
   
   # Less efficient: fetch all, filter client-side
   all_tags = get_category_tags(125)
   freq_tags = [t for t in all_tags['data'] if t['group_id'] == 'freq']
   ```

3. **Cache Results**
   ```python
   # Tags change rarely, safe to cache
   tags_cache = {}
   if category_id not in tags_cache:
       tags_cache[category_id] = get_category_tags(category_id)
   tags = tags_cache[category_id]
   ```

---

## Best Practices

### 1. Start with Tag Groups

```python
# Efficient: Get overview of tag types first
for group in ["freq", "geo", "src", "seas"]:
    tags = get_category_tags(125, tag_group_id=group, limit=10)
    print(f"{group}: {tags['metadata']['count']} tags")
```

---

### 2. Use Tags to Guide Series Searches

```python
# 1. Discover available tags
freq_tags = get_category_tags(125, tag_group_id="freq")
# Result: quarterly, annual, monthly

# 2. Use discovered tags in series search
series = get_category_series(125, tag_names="quarterly")
```

---

### 3. Validate Before Using

```python
# Check if specific tags exist
tags = get_category_tags(125, tag_names="quarterly;sa")

if tags['metadata']['count'] == 2:
    # Tags exist, safe to use
    series = get_category_series(125, tag_names="quarterly;sa")
else:
    # Fallback to available tags
    all_tags = get_category_tags(125, tag_group_id="freq")
    # Use most common tag
    top_tag = all_tags['data'][0]['name']
    series = get_category_series(125, tag_names=top_tag)
```

---

### 4. Handle Empty Results

```python
tags = get_category_tags(category_id)

if tags['metadata']['count'] == 0:
    print("Category has no series or tags")
    # Try getting series first
    series = get_category_series(category_id)
    if series['metadata']['count'] == 0:
        print("Category is empty")
else:
    # Process tags
    for tag in tags['data']:
        print(f"{tag['name']}: {tag['series_count']} series")
```

---

### 5. Combine with Other Category Tools

```python
# Complete category analysis workflow
# 1. Get category info
category = get_category(125)
print(f"Category: {category['data']['name']}")

# 2. Check children
children = get_category_children(125)
print(f"Child categories: {children['metadata']['count']}")

# 3. Check related
related = get_category_related(125)
print(f"Related categories: {related['metadata']['count']}")

# 4. Analyze tags
tags = get_category_tags(125)
print(f"Tags: {tags['metadata']['count']}")

# 5. Get series
series = get_category_series(125, limit=10)
print(f"Series: {series['metadata']['total_count']}")
```

---

## Related Tools

### Complementary Category Tools

| Tool | Purpose | When to Use |
|------|---------|------------|
| `get_fred_category` | Get category metadata | Get category name, parent, notes |
| `get_fred_category_children` | Get child categories | Navigate down the hierarchy |
| `get_fred_category_related` | Get related categories | Find cross-references |
| `get_fred_category_series` | Get series in category | Fetch actual data series |
| `get_fred_category_tags` | Get tags for category | Discover data characteristics (this tool) |

### Typical Workflow

```python
# 1. Start with category
category = get_category(125)
print(f"Exploring: {category['data']['name']}")

# 2. Discover tags (this tool)
tags = get_category_tags(125)
print(f"Available tags: {tags['metadata']['count']}")

# 3. Filter by tag type
freq_tags = get_category_tags(125, tag_group_id="freq")
print(f"Frequency options: {[t['name'] for t in freq_tags['data']]}")

# 4. Use tags to filter series
series = get_category_series(125, tag_names="quarterly;sa", limit=10)
print(f"Found {series['metadata']['total_count']} quarterly, SA series")

# 5. Fetch observations for interesting series
for s in series['data'][:3]:
    obs = get_series_observations(s['id'], limit=10)
    print(f"{s['title']}: {len(obs['data'])} observations")
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-01 | Initial implementation |

---

## Additional Resources

- **FRED API Documentation**: https://fred.stlouisfed.org/docs/api/fred/
- **FRED Category Tags Endpoint**: https://fred.stlouisfed.org/docs/api/fred/category_tags.html
- **FRED Tags Reference**: https://fred.stlouisfed.org/docs/api/fred/tags.html
- **FRED Website**: https://fred.stlouisfed.org/
- **Category Browser**: https://fred.stlouisfed.org/categories

---

## Support

For issues or questions:
1. Check FRED API status: https://fred.stlouisfed.org/docs/api/api_status.html
2. Review error messages in response JSON
3. Verify category_id has series using `get_category_series`
4. Check that filters (tag_group_id, tag_names) use valid values
5. Review server logs for detailed error information

---

**Last Updated:** 2025-11-01  
**Tool Version:** 1.0.0  
**FRED API Version:** Stable (no versioning)
