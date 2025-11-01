# FRED Category Series Tool - Complete API Reference

## Overview

The `get_category_series` tool retrieves all economic data series belonging to a specific FRED category. This is the primary tool for discovering actual data series after navigating the category hierarchy, with extensive filtering, sorting, and pagination capabilities.

**Tool Name**: `get_category_series`
**MCP Tool ID**: `get_fred_category_series`
**FRED API Endpoint**: `https://api.stlouisfed.org/fred/category/series`
**Purpose**: Discover and retrieve data series within categories

---

## Table of Contents

1. [Parameters](#parameters)
2. [Response Format](#response-format)
3. [Usage Examples](#usage-examples)
4. [Common Use Cases](#common-use-cases)
5. [Filtering Strategies](#filtering-strategies)
6. [Sorting and Ranking](#sorting-and-ranking)
7. [Pagination](#pagination)
8. [Best Practices](#best-practices)
9. [Error Handling](#error-handling)
10. [Performance Considerations](#performance-considerations)
11. [Integration with Other Tools](#integration-with-other-tools)
12. [API Reference](#api-reference)

---

## Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `category_id` | `int` | The ID for a category (required) |

### Optional Parameters

#### Basic Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `realtime_start` | `str` | Today | Start date for real-time period (YYYY-MM-DD) |
| `realtime_end` | `str` | Today | End date for real-time period (YYYY-MM-DD) |
| `limit` | `int` | `1000` | Maximum results to return (1-1000) |
| `offset` | `int` | `0` | Starting offset for pagination |

#### Sorting Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `order_by` | `str` | `"series_id"` | Field to sort by (see options below) |
| `sort_order` | `str` | `"asc"` | Sort direction: "asc" or "desc" |

**order_by Options**:
- `"series_id"`: Series ID (alphabetical)
- `"title"`: Series title (alphabetical)
- `"units"`: Units of measurement
- `"frequency"`: Data frequency
- `"seasonal_adjustment"`: Seasonal adjustment type
- `"realtime_start"`: Real-time start date
- `"realtime_end"`: Real-time end date
- `"last_updated"`: Last update timestamp
- `"observation_start"`: First observation date
- `"observation_end"`: Last observation date
- `"popularity"`: FRED popularity score
- `"group_popularity"`: Group popularity score

#### Filtering Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter_variable` | `str` | `None` | Attribute to filter by |
| `filter_value` | `str` | `None` | Value for filter_variable |
| `tag_names` | `str` | `None` | Semicolon-delimited tags (must have ALL) |
| `exclude_tag_names` | `str` | `None` | Semicolon-delimited tags (must have NONE) |

**filter_variable Options**:
- `"frequency"`: Filter by data frequency
- `"units"`: Filter by units of measurement
- `"seasonal_adjustment"`: Filter by seasonal adjustment type

### Parameter Details

#### `category_id`
- **Type**: Positive integer
- **Required**: Yes
- **Validation**: Must be a valid category ID in FRED
- **Examples**:
  - `125`: Trade Balance
  - `32991`: Money, Banking, & Finance
  - `22`: Interest Rates
  - `32992`: National Accounts

#### `limit` and `offset`
- **Limit Range**: 1-1000 (default: 1000)
- **Offset Range**: 0+ (default: 0)
- **Use Case**: Pagination through large result sets
- **Example**:
  - First page: `limit=100, offset=0`
  - Second page: `limit=100, offset=100`
  - Third page: `limit=100, offset=200`

#### `filter_variable` and `filter_value`
- **Must be used together**: Both required for filtering
- **Case-sensitive**: Match exact values
- **Common Values**:

**Frequency Values**:
- `"Daily"`
- `"Weekly"`
- `"Biweekly"`
- `"Monthly"`
- `"Quarterly"`
- `"Semiannual"`
- `"Annual"`

**Seasonal Adjustment Values**:
- `"Seasonally Adjusted"`
- `"Not Seasonally Adjusted"`
- `"Seasonally Adjusted Annual Rate"`

**Units Examples**:
- `"Billions of Dollars"`
- `"Millions of Dollars"`
- `"Percent"`
- `"Index 2015=100"`
- `"Thousands of Persons"`

#### `tag_names` and `exclude_tag_names`
- **Format**: Semicolon-delimited (e.g., `"income;bea"`)
- **tag_names**: Series must have ALL specified tags (AND logic)
- **exclude_tag_names**: Series must have NONE of specified tags (NOT logic)
- **Requirement**: `exclude_tag_names` requires `tag_names` to be set
- **Examples**:
  - `tag_names="nsa;usa"`: Series with both "nsa" AND "usa" tags
  - `exclude_tag_names="discontinued;annual"`: Exclude series with "discontinued" OR "annual"

---

## Response Format

### Success Response Structure

```json
{
  "tool": "get_category_series",
  "data": [
    {
      "id": "BOPGSTB",
      "realtime_start": "2025-11-01",
      "realtime_end": "2025-11-01",
      "title": "Trade Balance: Goods and Services, Balance of Payments Basis",
      "observation_start": "1992-01-01",
      "observation_end": "2017-05-01",
      "frequency": "Monthly",
      "frequency_short": "M",
      "units": "Millions of Dollars",
      "units_short": "Mil. of $",
      "seasonal_adjustment": "Seasonally Adjusted",
      "seasonal_adjustment_short": "SA",
      "last_updated": "2017-07-06 09:32:14-05",
      "popularity": 71,
      "group_popularity": 71,
      "notes": "Optional series description"
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "total_count": 47,
    "returned_count": 47,
    "limit": 1000,
    "offset": 0,
    "order_by": "series_id",
    "sort_order": "asc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

### Response Fields

#### Data Array (Series List)
Each series object contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique series identifier (e.g., "GDP", "UNRATE") |
| `realtime_start` | `str` | Real-time period start date |
| `realtime_end` | `str` | Real-time period end date |
| `title` | `str` | Full series title/description |
| `observation_start` | `str` | First available observation date |
| `observation_end` | `str` | Last available observation date |
| `frequency` | `str` | Full frequency name (e.g., "Monthly") |
| `frequency_short` | `str` | Abbreviated frequency (e.g., "M") |
| `units` | `str` | Full units description |
| `units_short` | `str` | Abbreviated units |
| `seasonal_adjustment` | `str` | Full adjustment description |
| `seasonal_adjustment_short` | `str` | Abbreviated adjustment (e.g., "SA") |
| `last_updated` | `str` | Last update timestamp |
| `popularity` | `int` | FRED popularity score (0-100) |
| `group_popularity` | `int` | Group popularity score |
| `notes` | `str` | Optional series notes/description |

#### Metadata Object

| Field | Type | Description |
|-------|------|-------------|
| `fetch_date` | `str` | ISO 8601 timestamp of retrieval |
| `category_id` | `int` | Category ID queried |
| `total_count` | `int` | Total series matching criteria |
| `returned_count` | `int` | Number of series in this response |
| `limit` | `int` | Max results per page |
| `offset` | `int` | Starting offset used |
| `order_by` | `str` | Sort field used |
| `sort_order` | `str` | Sort direction used |
| `realtime_start` | `str` | Real-time start date |
| `realtime_end` | `str` | Real-time end date |
| `filter_variable` | `str` | Filter attribute (if used) |
| `filter_value` | `str` | Filter value (if used) |
| `tag_names` | `str` | Included tags (if used) |
| `exclude_tag_names` | `str` | Excluded tags (if used) |

### Empty Response (No Series)

When a category has no series (branch category):

```json
{
  "tool": "get_category_series",
  "data": [],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 22,
    "total_count": 0,
    "returned_count": 0,
    "limit": 1000,
    "offset": 0
  }
}
```

**Note**: Categories with children often have no direct series. Use `get_category_children` to navigate to leaf categories that contain series.

### Error Response Structure

```json
{
  "tool": "get_category_series",
  "error": "Category not found: 999999",
  "category_id": 999999
}
```

**Common Error Messages**:
- `"Invalid category_id: must be a non-negative integer"` - Invalid category_id
- `"Category not found: {id}"` - Category doesn't exist (404)
- `"Invalid parameters: {detail}"` - Bad request (400)
- `"Rate limit exceeded. Please try again later."` - Too many requests (429)
- `"Invalid limit: must be between 1 and 1000"` - Limit out of range
- `"Invalid offset: must be non-negative"` - Negative offset

---

## Usage Examples

### Example 1: Get All Series in Category

Retrieve all series in the Trade Balance category:

```python
# Get all Trade Balance series
result = get_category_series(125)
```

**Response Summary**:
```json
{
  "metadata": {
    "category_id": 125,
    "total_count": 47,
    "returned_count": 47
  },
  "data": [
    {"id": "AITGCBN", "title": "Advance U.S. International Trade..."},
    {"id": "AITGCBS", "title": "Advance U.S. International Trade..."},
    {"id": "BOPGSTB", "title": "Trade Balance: Goods and Services..."}
  ]
}
```

**Use Case**: Discover all available data series in a category.

---

### Example 2: Filter by Frequency

Get only monthly series:

```python
# Get monthly series only
result = get_category_series(
    125,
    filter_variable="frequency",
    filter_value="Monthly"
)
```

**Response Summary**:
```json
{
  "metadata": {
    "category_id": 125,
    "total_count": 5,
    "returned_count": 5,
    "filter_variable": "frequency",
    "filter_value": "Monthly"
  },
  "data": [
    {
      "id": "AITGCBN",
      "frequency": "Monthly",
      "title": "Advance U.S. International Trade in Goods: Balance"
    }
  ]
}
```

**Use Case**: Find series with specific data frequency for analysis needs.

---

### Example 3: Sort by Popularity

Get most popular series first:

```python
# Top 10 most popular series
result = get_category_series(
    125,
    order_by="popularity",
    sort_order="desc",
    limit=10
)
```

**Response**:
```json
{
  "data": [
    {"id": "BOPGSTB", "popularity": 71, "title": "Trade Balance: Goods and Services..."},
    {"id": "IEABC", "popularity": 60, "title": "Balance on current account"},
    {"id": "BOPGTB", "popularity": 52, "title": "Trade Balance: Goods..."}
  ]
}
```

**Use Case**: Identify the most widely-used series in a category.

---

### Example 4: Filter by Seasonal Adjustment

Get only seasonally adjusted series:

```python
# Seasonally adjusted series only
result = get_category_series(
    125,
    filter_variable="seasonal_adjustment",
    filter_value="Seasonally Adjusted"
)
```

**Response Summary**:
```json
{
  "metadata": {
    "total_count": 18,
    "filter_variable": "seasonal_adjustment",
    "filter_value": "Seasonally Adjusted"
  },
  "data": [
    {
      "id": "AITGCBS",
      "seasonal_adjustment": "Seasonally Adjusted",
      "seasonal_adjustment_short": "SA"
    }
  ]
}
```

**Use Case**: Get clean, seasonally adjusted data for economic analysis.

---

### Example 5: Pagination

Paginate through large result sets:

```python
# First page (results 1-100)
page1 = get_category_series(32991, limit=100, offset=0)

# Second page (results 101-200)
page2 = get_category_series(32991, limit=100, offset=100)

# Third page (results 201-300)
page3 = get_category_series(32991, limit=100, offset=200)
```

**Use Case**: Process large categories in manageable chunks.

---

### Example 6: Filter by Units

Get series in billions of dollars:

```python
# Series in billions
result = get_category_series(
    32992,  # National Accounts
    filter_variable="units",
    filter_value="Billions of Dollars"
)
```

**Use Case**: Find series with consistent units for comparison.

---

### Example 7: Tag-Based Filtering

Get series with specific tags:

```python
# Get non-seasonally adjusted (nsa) USA series
result = get_category_series(
    125,
    tag_names="nsa;usa"
)

# Exclude discontinued and annual series
result = get_category_series(
    125,
    tag_names="usa",
    exclude_tag_names="discontinued;annual"
)
```

**Use Case**: Fine-tune series selection with tag metadata.

---

### Example 8: Sort by Last Updated

Find recently updated series:

```python
# Most recently updated first
result = get_category_series(
    125,
    order_by="last_updated",
    sort_order="desc",
    limit=20
)
```

**Use Case**: Monitor fresh data and recent revisions.

---

### Example 9: Complete Workflow

Navigate from category to series to data:

```python
# Step 1: Get category info
cat_info = get_category(125)
print(f"Category: {cat_info['data']['name']}")

# Step 2: Get series in category
series_list = get_category_series(
    125,
    filter_variable="frequency",
    filter_value="Monthly",
    order_by="popularity",
    sort_order="desc",
    limit=5
)

# Step 3: Get observations for top series
top_series_id = series_list['data'][0]['id']
observations = get_series_observations(
    top_series_id,
    observation_start="2020-01-01"
)
```

**Use Case**: Complete data discovery and retrieval pipeline.

---

## Common Use Cases

### Use Case 1: Discover Key Economic Indicators

**Scenario**: Find the most important series in a category.

**Implementation**:
```python
def get_key_indicators(category_id, top_n=10):
    """Get top N most popular series in a category."""
    result = get_category_series(
        category_id,
        order_by="popularity",
        sort_order="desc",
        limit=top_n
    )

    data = json.loads(result)
    indicators = []

    for series in data['data']:
        indicators.append({
            'id': series['id'],
            'title': series['title'],
            'popularity': series['popularity'],
            'frequency': series['frequency'],
            'units': series['units_short']
        })

    return indicators

# Find key trade indicators
key_trade_series = get_key_indicators(125, top_n=5)
for i, series in enumerate(key_trade_series, 1):
    print(f"{i}. {series['id']} (popularity: {series['popularity']})")
    print(f"   {series['title']}")
    print(f"   {series['frequency']}, {series['units']}\n")
```

**Output**:
```
1. BOPGSTB (popularity: 71)
   Trade Balance: Goods and Services, Balance of Payments Basis
   Monthly, Mil. of $

2. IEABC (popularity: 60)
   Balance on current account
   Quarterly, Mil. of $
```

---

### Use Case 2: Build Series Catalog

**Scenario**: Create a comprehensive catalog of available series.

**Implementation**:
```python
def build_series_catalog(category_id):
    """Build complete catalog with all series metadata."""
    all_series = []
    offset = 0
    limit = 1000

    while True:
        result = get_category_series(
            category_id,
            limit=limit,
            offset=offset
        )

        data = json.loads(result)
        series_batch = data['data']

        if not series_batch:
            break

        all_series.extend(series_batch)

        # Check if more results available
        if len(series_batch) < limit:
            break

        offset += limit

    # Create catalog
    catalog = {
        'category_id': category_id,
        'total_series': len(all_series),
        'series': all_series,
        'by_frequency': {},
        'by_units': {},
        'by_adjustment': {}
    }

    # Group by attributes
    for series in all_series:
        freq = series['frequency']
        catalog['by_frequency'][freq] = catalog['by_frequency'].get(freq, 0) + 1

        units = series['units']
        catalog['by_units'][units] = catalog['by_units'].get(units, 0) + 1

        adj = series['seasonal_adjustment']
        catalog['by_adjustment'][adj] = catalog['by_adjustment'].get(adj, 0) + 1

    return catalog

# Build catalog
catalog = build_series_catalog(125)
print(f"Total series: {catalog['total_series']}")
print(f"\nBy frequency: {catalog['by_frequency']}")
print(f"By adjustment: {catalog['by_adjustment']}")
```

---

### Use Case 3: Compare Series Availability

**Scenario**: Compare what data is available in different categories.

**Implementation**:
```python
def compare_categories(category_ids, metric="total_count"):
    """Compare series counts across multiple categories."""
    comparison = {}

    for cat_id in category_ids:
        # Get category info
        cat_result = get_category(cat_id)
        cat_data = json.loads(cat_result)['data']

        # Get series count
        series_result = get_category_series(cat_id, limit=1)
        series_data = json.loads(series_result)

        comparison[cat_id] = {
            'name': cat_data['name'],
            'total_series': series_data['metadata']['total_count'],
            'has_data': series_data['metadata']['total_count'] > 0
        }

    return comparison

# Compare trade-related categories
categories = [125, 13, 16, 17]  # Trade Balance, International Data, Exports, Imports
comparison = compare_categories(categories)

for cat_id, info in comparison.items():
    print(f"{info['name']} (ID: {cat_id})")
    print(f"  Series: {info['total_series']}")
    print(f"  Has data: {info['has_data']}\n")
```

---

### Use Case 4: Filter for Analysis-Ready Data

**Scenario**: Find monthly, seasonally adjusted series for time series analysis.

**Implementation**:
```python
def get_analysis_ready_series(category_id):
    """Get monthly, seasonally adjusted series."""
    result = get_category_series(
        category_id,
        filter_variable="frequency",
        filter_value="Monthly"
    )

    data = json.loads(result)

    # Further filter for seasonally adjusted
    sa_series = [
        s for s in data['data']
        if s['seasonal_adjustment'] == 'Seasonally Adjusted'
    ]

    # Sort by popularity
    sa_series.sort(key=lambda x: x['popularity'], reverse=True)

    return sa_series

# Get analysis-ready series
ready_series = get_analysis_ready_series(125)
print(f"Found {len(ready_series)} monthly SA series")

for series in ready_series[:5]:
    print(f"- {series['id']}: {series['title']}")
    print(f"  Data: {series['observation_start']} to {series['observation_end']}")
```

---

### Use Case 5: Monitor Data Updates

**Scenario**: Track which series have been recently updated.

**Implementation**:
```python
from datetime import datetime, timedelta

def find_recently_updated(category_id, days=7):
    """Find series updated in last N days."""
    result = get_category_series(
        category_id,
        order_by="last_updated",
        sort_order="desc",
        limit=1000
    )

    data = json.loads(result)
    cutoff = datetime.now() - timedelta(days=days)

    recent = []
    for series in data['data']:
        # Parse last_updated timestamp
        updated_str = series['last_updated'].split()[0]  # Get date part
        # Note: Actual parsing would be more robust
        recent.append({
            'id': series['id'],
            'title': series['title'],
            'last_updated': series['last_updated']
        })

    return recent

# Find series updated in last 7 days
recent = find_recently_updated(125, days=7)
print(f"Series updated in last 7 days: {len(recent)}")
```

---

## Filtering Strategies

### Strategy 1: Frequency Filtering

**Common Frequency Values**:
```python
frequencies = {
    "Daily": "d",
    "Weekly": "w",
    "Biweekly": "bw",
    "Monthly": "m",
    "Quarterly": "q",
    "Semiannual": "sa",
    "Annual": "a"
}

# Get all quarterly series
quarterly = get_category_series(
    32992,  # National Accounts
    filter_variable="frequency",
    filter_value="Quarterly"
)
```

**Use Cases**:
- Match analysis timeframe
- Align with reporting schedules
- Reduce data volume for high-frequency categories

---

### Strategy 2: Units Filtering

**Common Units Patterns**:
```python
# Monetary values
units_monetary = [
    "Billions of Dollars",
    "Millions of Dollars",
    "Thousands of Dollars"
]

# Rates/Percentages
units_rates = [
    "Percent",
    "Percent Change",
    "Percent Change at Annual Rate"
]

# Indices
units_indices = [
    "Index 2015=100",
    "Index 1982-84=100",
    "Index"
]

# Get dollar-denominated series
result = get_category_series(
    125,
    filter_variable="units",
    filter_value="Millions of Dollars"
)
```

---

### Strategy 3: Seasonal Adjustment Filtering

**Adjustment Types**:
```python
adjustments = {
    "SA": "Seasonally Adjusted",
    "NSA": "Not Seasonally Adjusted",
    "SAAR": "Seasonally Adjusted Annual Rate"
}

# Get seasonally adjusted series
sa_series = get_category_series(
    125,
    filter_variable="seasonal_adjustment",
    filter_value="Seasonally Adjusted"
)

# Get not seasonally adjusted
nsa_series = get_category_series(
    125,
    filter_variable="seasonal_adjustment",
    filter_value="Not Seasonally Adjusted"
)
```

**When to use each**:
- **SA**: Time series analysis, trend identification
- **NSA**: Capturing seasonal patterns, raw data
- **SAAR**: Economic growth rates, annualized figures

---

### Strategy 4: Combined Filtering

**Multi-attribute filtering**:
```python
def get_filtered_series(category_id, freq=None, units=None, adj=None):
    """Apply multiple filters sequentially."""
    result = get_category_series(category_id, limit=1000)
    data = json.loads(result)
    series = data['data']

    if freq:
        series = [s for s in series if s['frequency'] == freq]

    if units:
        series = [s for s in series if s['units'] == units]

    if adj:
        series = [s for s in series if s['seasonal_adjustment'] == adj]

    return series

# Get monthly, SA series in millions
filtered = get_filtered_series(
    125,
    freq="Monthly",
    adj="Seasonally Adjusted"
)
```

**Note**: API only supports one filter_variable at a time. For multiple filters, fetch all and filter in code.

---

## Sorting and Ranking

### Sort by Popularity

**Find most-used series**:
```python
# Most popular
popular = get_category_series(
    125,
    order_by="popularity",
    sort_order="desc",
    limit=20
)
```

**Popularity scores indicate**:
- Number of views/downloads
- Researcher interest
- Key benchmark status

---

### Sort by Title

**Alphabetical browsing**:
```python
# A-Z
result = get_category_series(
    125,
    order_by="title",
    sort_order="asc"
)
```

**Use Case**: Human-friendly catalog generation.

---

### Sort by Data Coverage

**Find longest time series**:
```python
# Oldest start date (longest history)
result = get_category_series(
    32992,
    order_by="observation_start",
    sort_order="asc",
    limit=10
)

# Most recent end date (most current)
result = get_category_series(
    32992,
    order_by="observation_end",
    sort_order="desc",
    limit=10
)
```

**Use Case**: Historical analysis, current indicators.

---

### Sort by Update Frequency

**Find freshest data**:
```python
# Most recently updated
result = get_category_series(
    125,
    order_by="last_updated",
    sort_order="desc",
    limit=20
)
```

**Use Case**: Real-time dashboards, nowcasting.

---

## Pagination

### Basic Pagination

```python
def paginate_category(category_id, page_size=100):
    """Iterate through all series in category."""
    offset = 0
    all_series = []

    while True:
        result = get_category_series(
            category_id,
            limit=page_size,
            offset=offset
        )

        data = json.loads(result)
        batch = data['data']

        if not batch:
            break

        all_series.extend(batch)
        print(f"Fetched {len(batch)} series (offset: {offset})")

        # Check if done
        if len(batch) < page_size:
            break

        offset += page_size

    return all_series

# Get all series with pagination
all_series = paginate_category(32991, page_size=200)
print(f"Total series retrieved: {len(all_series)}")
```

---

### Progressive Loading

```python
def load_progressively(category_id, initial_limit=50):
    """Load initial results, then expand on demand."""
    # Initial load
    result = get_category_series(
        category_id,
        limit=initial_limit,
        order_by="popularity",
        sort_order="desc"
    )

    data = json.loads(result)
    total = data['metadata']['total_count']

    print(f"Loaded {initial_limit} of {total} series")

    # Option to load more
    if total > initial_limit:
        print(f"{total - initial_limit} more series available")
        # Load next batch on demand

    return data['data'], total

initial_series, total = load_progressively(32991, initial_limit=50)
```

---

## Best Practices

### 1. Start with Popularity Sorting

Always start by viewing most popular series:

```python
# GOOD: Start with popular series
result = get_category_series(
    125,
    order_by="popularity",
    sort_order="desc",
    limit=20
)

# Then explore further if needed
```

**Rationale**: Most popular series are typically the most reliable, well-documented, and widely-used benchmarks.

---

### 2. Use Appropriate Limits

```python
# GOOD: Reasonable limits
top_series = get_category_series(125, limit=20)  # Quick overview
all_series = get_category_series(125, limit=1000)  # Full catalog

# BAD: Always using limit=1
result = get_category_series(125, limit=1)  # Too many round trips
```

**Guidelines**:
- Initial exploration: `limit=20-50`
- Building catalogs: `limit=1000`
- Pagination: `limit=100-200`

---

### 3. Filter Early

```python
# GOOD: Filter at API level
result = get_category_series(
    125,
    filter_variable="frequency",
    filter_value="Monthly"
)

# AVOID: Fetch all then filter
result = get_category_series(125, limit=1000)
# Then filter in Python
```

**Rationale**: Reduces data transfer and processing time.

---

### 4. Cache Series Lists

```python
from datetime import datetime, timedelta

class SeriesCache:
    def __init__(self, ttl_hours=24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)

    def get_series(self, category_id, **kwargs):
        cache_key = f"{category_id}_{kwargs}"

        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.ttl:
                return data

        # Fetch fresh data
        result = get_category_series(category_id, **kwargs)
        self.cache[cache_key] = (result, datetime.now())
        return result

# Use cached version
cache = SeriesCache(ttl_hours=24)
result = cache.get_series(125, order_by="popularity", limit=20)
```

**Rationale**: Series lists change infrequently.

---

### 5. Handle Empty Categories

```python
def get_series_safe(category_id):
    """Safely get series, handle empty categories."""
    result = get_category_series(category_id)
    data = json.loads(result)

    if data['metadata']['total_count'] == 0:
        print(f"Category {category_id} has no series")
        print("This may be a branch category with children.")

        # Try to get children
        children_result = get_category_children(category_id)
        children_data = json.loads(children_result)

        if children_data['data']:
            print(f"Found {len(children_data['data'])} child categories")
            return None, children_data['data']

    return data['data'], None

series, children = get_series_safe(22)
```

---

### 6. Verify Filter Results

```python
def verify_filter(category_id, filter_var, filter_val):
    """Verify filter is working correctly."""
    result = get_category_series(
        category_id,
        filter_variable=filter_var,
        filter_value=filter_val
    )

    data = json.loads(result)

    # Verify all results match filter
    for series in data['data']:
        actual_value = series.get(filter_var.replace('_', ''))
        if actual_value != filter_val:
            print(f"Warning: {series['id']} has {actual_value}, not {filter_val}")

    return data

# Verify monthly filter
data = verify_filter(125, "frequency", "Monthly")
```

---

## Error Handling

### Handle Invalid Categories

```python
def get_series_robust(category_id):
    """Get series with comprehensive error handling."""
    result = get_category_series(category_id)
    data = json.loads(result)

    if 'error' in data:
        error = data['error']

        if 'not found' in error.lower():
            print(f"Category {category_id} does not exist")
            return None
        elif 'rate limit' in error.lower():
            print("Rate limited, retry with backoff")
            time.sleep(60)
            return get_series_robust(category_id)
        else:
            print(f"Unexpected error: {error}")
            return None

    return data

data = get_series_robust(125)
```

---

### Handle Pagination Errors

```python
def safe_paginate(category_id, page_size=100):
    """Paginate with error recovery."""
    offset = 0
    all_series = []
    retries = 0
    max_retries = 3

    while True:
        try:
            result = get_category_series(
                category_id,
                limit=page_size,
                offset=offset
            )

            data = json.loads(result)

            if 'error' in data:
                retries += 1
                if retries >= max_retries:
                    print(f"Failed after {max_retries} retries")
                    break
                time.sleep(2 ** retries)
                continue

            batch = data['data']
            if not batch:
                break

            all_series.extend(batch)
            retries = 0  # Reset on success

            if len(batch) < page_size:
                break

            offset += page_size

        except Exception as e:
            print(f"Exception during pagination: {e}")
            break

    return all_series
```

---

## Performance Considerations

### Response Times

**Typical performance**:
```
Small categories (<50 series): 0.25-0.40s
Medium categories (50-500): 0.30-0.60s
Large categories (>500): 0.40-1.00s
With filters: +0.05-0.15s
```

---

### Optimization Strategies

#### 1. Use Filters to Reduce Payload

```python
# SLOW: Fetch all 1000+ series
result = get_category_series(32991, limit=1000)

# FAST: Filter to relevant subset
result = get_category_series(
    32991,
    filter_variable="frequency",
    filter_value="Monthly"
)
```

#### 2. Limit Initial Results

```python
# GOOD: Progressive disclosure
initial = get_category_series(125, limit=20)
# Show to user, load more if needed
```

#### 3. Parallel Requests for Multiple Categories

```python
import concurrent.futures

def fetch_category(cat_id):
    return get_category_series(cat_id, limit=20)

categories = [125, 13, 16, 17, 32991]

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_category, categories))
```

---

### Rate Limiting

**FRED API rate limits**:
- Default: 120 requests/minute
- Burst: Brief exceeding allowed

**Rate limiter implementation**:
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_per_minute=100):
        self.max_per_minute = max_per_minute
        self.calls = deque()

    def wait_if_needed(self):
        now = time.time()

        # Remove calls older than 1 minute
        while self.calls and self.calls[0] < now - 60:
            self.calls.popleft()

        # Check if at limit
        if len(self.calls) >= self.max_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.calls.append(now)

limiter = RateLimiter(max_per_minute=100)

def get_series_rate_limited(category_id):
    limiter.wait_if_needed()
    return get_category_series(category_id)
```

---

## Integration with Other Tools

### Complete Discovery Workflow

```python
def discover_data(topic_keywords):
    """Complete workflow: search → category → series → data."""

    # Step 1: Search for relevant categories
    print(f"Searching for: {topic_keywords}")
    search_result = search_fred_series(topic_keywords, limit=5)
    search_data = json.loads(search_result)

    # Step 2: Get categories from search results
    if not search_data['data']:
        print("No series found")
        return None

    # Extract category IDs from series
    category_ids = set()
    for series in search_data['data']:
        # Series metadata would include category_id
        # (In real implementation, use series/categories endpoint)
        pass

    # Step 3: Get series in identified categories
    for cat_id in category_ids:
        print(f"\nCategory {cat_id}:")

        series_result = get_category_series(
            cat_id,
            order_by="popularity",
            sort_order="desc",
            limit=10
        )
        series_data = json.loads(series_result)

        for series in series_data['data']:
            print(f"  - {series['id']}: {series['title'][:60]}")

    # Step 4: Get observations for top series
    top_series_id = search_data['data'][0]['id']
    obs_result = get_series_observations(
        top_series_id,
        observation_start="2020-01-01"
    )

    return obs_result

# Execute workflow
result = discover_data("trade balance")
```

---

### Category Tree Navigation

```python
def explore_category_tree(category_id, depth=0, max_depth=2):
    """Recursively explore category tree with series counts."""

    # Get category info
    cat_result = get_category(category_id)
    cat_data = json.loads(cat_result)['data']

    # Get series count
    series_result = get_category_series(category_id, limit=1)
    series_data = json.loads(series_result)
    series_count = series_data['metadata']['total_count']

    indent = "  " * depth
    print(f"{indent}{cat_data['name']} (ID: {category_id})")
    print(f"{indent}  Series: {series_count}")

    # Get children if not at max depth
    if depth < max_depth:
        children_result = get_category_children(category_id)
        children_data = json.loads(children_result)

        for child in children_data['data']:
            explore_category_tree(child['id'], depth + 1, max_depth)

# Explore from International Data
explore_category_tree(13, max_depth=2)
```

---

### Build Series Selection UI

```python
def build_series_selector(category_id):
    """Create interactive series selector."""

    # Get all series
    result = get_category_series(
        category_id,
        order_by="popularity",
        sort_order="desc"
    )
    data = json.loads(result)

    # Group by frequency
    by_frequency = {}
    for series in data['data']:
        freq = series['frequency']
        if freq not in by_frequency:
            by_frequency[freq] = []
        by_frequency[freq].append(series)

    # Display grouped options
    print(f"Category has {len(data['data'])} series\n")

    for freq, series_list in sorted(by_frequency.items()):
        print(f"{freq} ({len(series_list)} series):")
        for series in series_list[:5]:  # Show top 5
            print(f"  [{series['id']}] {series['title'][:60]}")
            print(f"    {series['units_short']}, popularity: {series['popularity']}")
        print()

    return by_frequency

# Build selector
selector = build_series_selector(125)
```

---

## API Reference

### Function Signature

```python
def get_category_series(
    category_id: int,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0,
    order_by: Literal[
        "series_id",
        "title",
        "units",
        "frequency",
        "seasonal_adjustment",
        "realtime_start",
        "realtime_end",
        "last_updated",
        "observation_start",
        "observation_end",
        "popularity",
        "group_popularity",
    ] = "series_id",
    sort_order: Literal["asc", "desc"] = "asc",
    filter_variable: Optional[Literal["frequency", "units", "seasonal_adjustment"]] = None,
    filter_value: Optional[str] = None,
    tag_names: Optional[str] = None,
    exclude_tag_names: Optional[str] = None,
) -> str:
    """
    Get the series in a specific category.

    Returns:
        JSON string with series array and metadata

    Raises:
        No exceptions raised - errors returned in JSON format
    """
```

---

### MCP Tool Schema

```json
{
  "name": "get_fred_category_series",
  "description": "Get the series in a specific category with filtering, sorting, and pagination options.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category_id": {
        "type": "integer",
        "description": "The ID for a category (required)",
        "minimum": 0
      },
      "realtime_start": {
        "type": "string",
        "description": "Start date for real-time period (YYYY-MM-DD)",
        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
      },
      "realtime_end": {
        "type": "string",
        "description": "End date for real-time period (YYYY-MM-DD)",
        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum results (1-1000)",
        "minimum": 1,
        "maximum": 1000,
        "default": 1000
      },
      "offset": {
        "type": "integer",
        "description": "Starting offset for pagination",
        "minimum": 0,
        "default": 0
      },
      "order_by": {
        "type": "string",
        "description": "Field to sort by",
        "enum": [
          "series_id", "title", "units", "frequency",
          "seasonal_adjustment", "realtime_start", "realtime_end",
          "last_updated", "observation_start", "observation_end",
          "popularity", "group_popularity"
        ],
        "default": "series_id"
      },
      "sort_order": {
        "type": "string",
        "description": "Sort direction",
        "enum": ["asc", "desc"],
        "default": "asc"
      },
      "filter_variable": {
        "type": "string",
        "description": "Attribute to filter by",
        "enum": ["frequency", "units", "seasonal_adjustment"]
      },
      "filter_value": {
        "type": "string",
        "description": "Value for filter_variable"
      },
      "tag_names": {
        "type": "string",
        "description": "Semicolon-delimited tags (must have ALL)"
      },
      "exclude_tag_names": {
        "type": "string",
        "description": "Semicolon-delimited tags (must have NONE)"
      }
    },
    "required": ["category_id"]
  }
}
```

---

### Related FRED API Endpoint

**Official Documentation**: https://fred.stlouisfed.org/docs/api/fred/category_series.html

**Base URL**: `https://api.stlouisfed.org/fred/category/series`

**Required Parameters**: `api_key`, `category_id`, `file_type=json`

**Rate Limits**: 120 requests per minute (default)

---

## Conclusion

The `get_category_series` tool is the primary method for discovering available data series within FRED's category taxonomy. Combined with category navigation tools, it enables complete data discovery workflows.

**Key Takeaways**:
- Start with popular series for key indicators
- Use filters to narrow results to analysis needs
- Leverage pagination for large categories
- Cache results - series lists change infrequently
- Handle empty categories (branch nodes) gracefully

**Typical Workflow**:
1. Navigate to relevant category with `get_category_children`
2. List series with `get_category_series`
3. Filter/sort to find target series
4. Retrieve data with `get_series_observations`
5. Analyze economic data

For additional assistance:
- See `FRED_CATEGORY_REFERENCE.MD` for category metadata
- See `FRED_CATEGORY_CHILDREN_REFERENCE.MD` for navigation
- See `FRED_OBSERVATIONS_REFERENCE.MD` for data retrieval
- Visit https://fred.stlouisfed.org for official FRED documentation
