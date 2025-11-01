# FRED Category Related Tags Tool – API Reference
## Tool: get_fred_category_related_tags

**Endpoint:** `https://api.stlouisfed.org/fred/category/related_tags`

**Description:** Get related FRED tags for one or more tags within a category. Discover what other tags co-occur with a given set of tags on series.

---

## Table of Contents

1. [Overview](#overview)
2. [Parameters](#parameters)
3. [Response Format](#response-format)
4. [Usage Examples](#usage-examples)
5. [Use Cases](#use-cases)
6. [Understanding Related Tags](#understanding-related-tags)
7. [Tag Filtering Logic](#tag-filtering-logic)
8. [Discovery Workflows](#discovery-workflows)
9. [Error Handling](#error-handling)
10. [Performance](#performance)
11. [Best Practices](#best-practices)
12. [Related Tools](#related-tools)

---

## Overview

The `get_fred_category_related_tags` tool retrieves tags that are related to a given set of tags within a specific category. This is one of the most powerful tools for tag-based data discovery in FRED.

### Key Concept

**Related tags** are tags assigned to series that:
1. Match **ALL** tags in `tag_names` (AND logic)
2. Match **NONE** of the tags in `exclude_tag_names` (NOT logic)
3. Belong to the specified `category_id`

### Key Features

- **Tag Co-occurrence Discovery**: Find what tags appear together on series
- **Progressive Discovery**: Start with known tags, find related ones
- **Filtering**: Include and exclude tags, filter by tag type
- **Sorting Options**: Order by series count, popularity, name, etc.
- **Pagination**: Support for large result sets (up to 1000 tags)
- **Fast Queries**: Typical response time < 0.5s
- **Compact JSON**: AI-optimized format

### Why Use Related Tags?

Related tags enable:
- **Data Exploration**: Start with known tags, discover related characteristics
- **Query Building**: Build progressive tag-based queries
- **Availability Discovery**: Find what frequencies, sources, geographies exist
- **Refinement**: Narrow searches by excluding unwanted tags
- **Context**: Understand what other attributes series with certain tags have

### Example Workflow

```
1. Category: Trade Balance (125)
2. Known tags: "services", "quarterly"
3. Question: What other tags do series with BOTH these tags have?
4. Answer: balance, bea, nation, usa, goods, nsa, sa (7 related tags)
5. Use case: Now you know these series are from BEA, nation-level, USA data
```

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
```

**Important Notes:**
- Must be a valid FRED category ID
- Category must have series to have tags
- Related tags come from series in this category only

---

#### `tag_names` (string, REQUIRED)

Semicolon-delimited list of tag names that series MUST match ALL of.

**Format:** Tag names separated by semicolons

**Logic:** AND - series must have all specified tags

**Examples:**
```python
"services"                    # Series with "services" tag
"services;quarterly"          # Series with BOTH "services" AND "quarterly"
"monthly;sa;usa"              # Series with ALL three tags
"interest;rates;monthly"      # Series with all three tags
```

**Important Notes:**
- **Required parameter** - cannot be empty
- Case-sensitive tag names
- Order doesn't matter
- More tags = narrower results (more restrictive)

**Common Patterns:**
- **Concept + Frequency**: "gdp;quarterly"
- **Geography + Adjustment**: "usa;sa"
- **Multiple Concepts**: "trade;goods;services"
- **Source + Geography**: "bea;usa"

---

### Optional Parameters

#### `realtime_start` (string, optional)

Start date for the real-time period.

**Format:** YYYY-MM-DD

**Default:** Today's date

---

#### `realtime_end` (string, optional)

End date for the real-time period.

**Format:** YYYY-MM-DD

**Default:** Today's date

---

#### `exclude_tag_names` (string, optional)

Semicolon-delimited list of tag names that series must match NONE of.

**Format:** Tag names separated by semicolons

**Default:** No exclusions

**Logic:** NOT - series must NOT have any specified tags

**Examples:**
```python
"goods"                       # Exclude series with "goods" tag
"goods;sa"                    # Exclude series with "goods" OR "sa"
"annual;semiannual"           # Exclude annual and semiannual data
```

**Use Cases:**
- Remove unwanted data types
- Filter out specific adjustments
- Exclude certain geographies
- Remove specific sources

**Combination Example:**
```python
# Include: services AND quarterly
# Exclude: goods OR sa
get_category_related_tags(
    category_id=125,
    tag_names="services;quarterly",
    exclude_tag_names="goods;sa"
)
# Result: Tags for services+quarterly series that are NOT goods and NOT sa
```

---

#### `tag_group_id` (string, optional)

Filter **result tags** by type/group.

**Format:** One of the tag group codes

**Default:** No filtering (all tag types in results)

**Valid Values:**
- **`"freq"`** - Frequency tags only
- **`"gen"`** - General/Concept tags only
- **`"geo"`** - Geography tags only
- **`"geot"`** - Geography Type tags only
- **`"rls"`** - Release tags only
- **`"seas"`** - Seasonal Adjustment tags only
- **`"src"`** - Source tags only

**Important:** This filters the **output**, not the input. The input `tag_names` can be any tags.

**Examples:**
```python
# Find what frequencies are available for "services" series
get_category_related_tags(125, "services", tag_group_id="freq")
# Result: quarterly, annual, monthly

# Find what sources provide "quarterly" data
get_category_related_tags(125, "quarterly", tag_group_id="src")
# Result: bea, census

# Find what geographies have "employment" data
get_category_related_tags(125, "employment", tag_group_id="geo")
# Result: usa, states, etc.
```

---

#### `search_text` (string, optional)

Search for **result tags** containing specific words.

**Format:** Text string

**Default:** No search filtering

**Examples:**
```python
"balance"            # Result tags containing "balance"
"season"             # Result tags containing "season" (seasonal, etc.)
"employ"             # Result tags containing "employ"
```

**Note:** Searches result tag names only, case-insensitive, partial matching.

---

#### `limit` (integer, optional)

Maximum number of result tags to return.

**Format:** Integer between 1 and 1000

**Default:** 1000

**Examples:**
```python
50      # Top 50 related tags
100     # Top 100 related tags
1000    # All related tags (up to max)
```

---

#### `offset` (integer, optional)

Starting offset for pagination.

**Format:** Non-negative integer

**Default:** 0

---

#### `order_by` (string, optional)

Field to sort result tags by.

**Format:** One of the order_by values

**Default:** "series_count"

**Valid Values:**
- **`"series_count"`** - Number of series with this tag (default)
- **`"popularity"`** - FRED popularity score
- **`"created"`** - When tag was created
- **`"name"`** - Tag name alphabetically
- **`"group_id"`** - Tag group/type

**Examples:**
```python
order_by="series_count"   # Most common tags first
order_by="popularity"     # Most popular tags first
order_by="name"           # Alphabetical A-Z
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

---

## Response Format

### Success Response

```json
{
  "tool": "get_category_related_tags",
  "data": [
    {
      "name": "balance",
      "group_id": "gen",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 65,
      "series_count": 4
    },
    {
      "name": "bea",
      "group_id": "src",
      "notes": "U.S. Department of Commerce: Bureau of Economic Analysis",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 87,
      "series_count": 4
    },
    {
      "name": "nation",
      "group_id": "geot",
      "notes": "Country Level",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 4
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "tag_names": "services;quarterly",
    "count": 7,
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

Array of related tag objects. Each tag contains:

- **name** (string): Tag name
- **group_id** (string): Tag type/group code
- **notes** (string): Tag description (may be empty)
- **created** (string): Creation timestamp
- **popularity** (integer): FRED popularity score (0-100)
- **series_count** (integer): Number of series matching the query with this tag

#### `metadata` (object)

Query metadata:
- **fetch_date** (string): UTC timestamp when data was retrieved
- **category_id** (integer): The input category ID
- **tag_names** (string): The required tags used in query
- **count** (integer): Total number of related tags found
- **offset** (integer): Starting offset used
- **limit** (integer): Maximum results returned
- **order_by** (string): Sort field used
- **sort_order** (string): Sort direction used
- **realtime_start** (string): Real-time period start date
- **realtime_end** (string): Real-time period end date

**Optional metadata fields** (when filters used):
- **exclude_tag_names** (string): Excluded tags filter
- **tag_group_id** (string): Tag group filter applied
- **search_text** (string): Search text filter applied

---

### Empty Result Response

When no series match the criteria or no related tags exist:

```json
{
  "tool": "get_category_related_tags",
  "data": [],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "tag_names": "nonexistent;tags",
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
  "tool": "get_category_related_tags",
  "error": "tag_names is required and cannot be empty",
  "category_id": 125,
  "tag_names": null
}
```

---

## Usage Examples

### Example 1: Find Related Tags for "services;quarterly"

**Request:**
```python
get_category_related_tags(
    category_id=125,
    tag_names="services;quarterly"
)
```

**Response:**
```json
{
  "tool": "get_category_related_tags",
  "data": [
    {"name": "balance", "group_id": "gen", "series_count": 4},
    {"name": "bea", "group_id": "src", "series_count": 4},
    {"name": "nation", "group_id": "geot", "series_count": 4},
    {"name": "usa", "group_id": "geo", "series_count": 4},
    {"name": "goods", "group_id": "gen", "series_count": 2},
    {"name": "nsa", "group_id": "seas", "series_count": 2},
    {"name": "sa", "group_id": "seas", "series_count": 2}
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "tag_names": "services;quarterly",
    "count": 7,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Interpretation:**
- 4 series have services+quarterly+balance+bea+nation+usa tags
- 2 series also have "goods" tag
- 2 series are NSA, 2 are SA

---

### Example 2: Exclude Unwanted Tags

**Request:**
```python
get_category_related_tags(
    category_id=125,
    tag_names="services;quarterly",
    exclude_tag_names="goods;sa"
)
```

**Response:**
```json
{
  "tool": "get_category_related_tags",
  "data": [
    {"name": "balance", "group_id": "gen", "series_count": 2},
    {"name": "bea", "group_id": "src", "series_count": 2},
    {"name": "nation", "group_id": "geot", "series_count": 2},
    {"name": "usa", "group_id": "geo", "series_count": 2},
    {"name": "nsa", "group_id": "seas", "series_count": 2}
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "tag_names": "services;quarterly",
    "exclude_tag_names": "goods;sa",
    "count": 5,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Interpretation:**
- Now only 2 series match (excluded goods and sa)
- Result tags show characteristics of those 2 series only

---

### Example 3: Find Available Frequencies

**Request:**
```python
get_category_related_tags(
    category_id=125,
    tag_names="services",
    tag_group_id="freq"
)
```

**Response:**
```json
{
  "tool": "get_category_related_tags",
  "data": [
    {"name": "quarterly", "group_id": "freq", "series_count": 4},
    {"name": "annual", "group_id": "freq", "series_count": 2},
    {"name": "monthly", "group_id": "freq", "series_count": 1}
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "tag_names": "services",
    "tag_group_id": "freq",
    "count": 3,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Interpretation:**
- Services data is available in 3 frequencies
- Most series are quarterly (4), some annual (2), one monthly (1)

---

### Example 4: Find Data Sources

**Request:**
```python
get_category_related_tags(
    category_id=125,
    tag_names="quarterly;nsa",
    tag_group_id="src"
)
```

**Response:**
```json
{
  "tool": "get_category_related_tags",
  "data": [
    {"name": "bea", "group_id": "src", "series_count": 12},
    {"name": "census", "group_id": "src", "series_count": 2}
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "tag_names": "quarterly;nsa",
    "tag_group_id": "src",
    "count": 2,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Interpretation:**
- Quarterly NSA data comes from 2 sources
- BEA provides 12 series, Census provides 2

---

### Example 5: Search for Specific Concepts

**Request:**
```python
get_category_related_tags(
    category_id=125,
    tag_names="quarterly",
    search_text="balance"
)
```

**Response:**
```json
{
  "tool": "get_category_related_tags",
  "data": [
    {"name": "balance", "group_id": "gen", "series_count": 14}
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "tag_names": "quarterly",
    "search_text": "balance",
    "count": 1,
    "offset": 0,
    "limit": 1000,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Interpretation:**
- 14 quarterly series have the "balance" tag

---

## Use Cases

### 1. Progressive Tag Discovery

**Scenario:** Start with one tag, discover related characteristics.

**Workflow:**
```python
# Step 1: Start with concept
related = get_category_related_tags(125, "services")
# Discover: quarterly, annual, monthly, nsa, sa, bea, etc.

# Step 2: Add frequency, find more
related = get_category_related_tags(125, "services;quarterly")
# Discover: nsa, sa, balance, goods

# Step 3: Add adjustment, narrow down
related = get_category_related_tags(125, "services;quarterly;nsa")
# Discover: final set of related tags

# Step 4: Use discovered tags to fetch series
series = get_category_series(125, tag_names="services;quarterly;nsa")
```

**Benefits:**
- Guided discovery process
- Understand data availability at each step
- Build precise queries progressively

---

### 2. Find Available Data Combinations

**Scenario:** Determine what combinations of tags exist.

**Example:**
```python
# What frequencies are available for "employment" data?
freq_tags = get_category_related_tags(
    32991,
    "employment",
    tag_group_id="freq"
)
# Result: monthly, quarterly, annual

# What geographies have "monthly" employment data?
geo_tags = get_category_related_tags(
    32991,
    "employment;monthly",
    tag_group_id="geo"
)
# Result: usa, states, metro areas

# What sources provide this data?
source_tags = get_category_related_tags(
    32991,
    "employment;monthly;usa",
    tag_group_id="src"
)
# Result: bls, census
```

---

### 3. Refine Searches with Exclusions

**Scenario:** Remove unwanted data types from results.

**Example:**
```python
# Find tags for trade data, but exclude goods
related = get_category_related_tags(
    125,
    "trade",
    exclude_tag_names="goods"
)
# Result: Only service-related trade tags

# Find quarterly data, exclude seasonally adjusted
related = get_category_related_tags(
    125,
    "quarterly",
    exclude_tag_names="sa"
)
# Result: Only NSA quarterly data tags

# Find USA data, exclude specific sources
related = get_category_related_tags(
    32991,
    "usa",
    exclude_tag_names="census;bls",
    tag_group_id="src"
)
# Result: Other sources besides census and bls
```

---

### 4. Understand Data Characteristics

**Scenario:** Learn about series with specific tags.

**Example:**
```python
# What do "gdp" series have in common?
category = get_category(32992)  # National Accounts
related = get_category_related_tags(32992, "gdp")

# Analyze results
for group in ["freq", "seas", "src", "geot"]:
    group_tags = get_category_related_tags(
        32992,
        "gdp",
        tag_group_id=group
    )
    print(f"{group}: {[t['name'] for t in group_tags['data']]}")

# Output:
# freq: ['quarterly', 'annual']
# seas: ['sa', 'nsa', 'saar']
# src: ['bea']
# geot: ['nation']
```

---

### 5. Build Complex Queries

**Scenario:** Construct multi-tag queries for precise data selection.

**Example:**
```python
# Goal: Find monthly, seasonally adjusted, national-level employment data from BLS

# Step 1: Verify tag combination exists
related = get_category_related_tags(
    3008,  # Employment category
    "employment;monthly;sa;nation;bls"
)

if related['metadata']['count'] > 0:
    # Tags are valid and co-occur
    # Step 2: Fetch series
    series = get_category_series(
        3008,
        tag_names="employment;monthly;sa;nation;bls",
        limit=20
    )
else:
    # Combination doesn't exist, try alternatives
    alt_related = get_category_related_tags(
        3008,
        "employment;monthly;sa"
    )
    # Use what's available
```

---

## Understanding Related Tags

### What Are Related Tags?

Related tags are tags that **co-occur** on series that match your criteria.

**Key Formula:**
```
Find series where:
  - Series belongs to category_id
  - Series has ALL tags in tag_names (AND logic)
  - Series has NONE of tags in exclude_tag_names (NOT logic)

Then return:
  - All other tags assigned to those series
```

### Example Breakdown

**Query:**
```python
get_category_related_tags(125, "services;quarterly")
```

**What happens:**
1. Find all series in category 125 (Trade Balance)
2. Filter to series with **both** "services" AND "quarterly" tags
3. Collect all tags from those filtered series
4. Remove "services" and "quarterly" from results (already known)
5. Return remaining tags with series counts

**Result interpretation:**
- "balance" appears on 4 of these series
- "bea" appears on 4 of these series  
- "nsa" appears on 2 of these series
- etc.

---

### AND vs OR Logic

**tag_names uses AND logic:**
```python
tag_names="services;quarterly"
# Means: services AND quarterly (must have both)
```

**exclude_tag_names uses OR logic:**
```python
exclude_tag_names="goods;sa"
# Means: NOT goods AND NOT sa (must have neither)
```

**Combined example:**
```python
get_category_related_tags(
    125,
    tag_names="services;quarterly",      # Must have BOTH
    exclude_tag_names="goods;sa"         # Must have NEITHER
)
# Result: Tags for series with services+quarterly but NOT goods and NOT sa
```

---

## Tag Filtering Logic

### Filter Order of Operations

1. **Category filter** (category_id)
2. **Required tags filter** (tag_names) - AND logic
3. **Exclusion filter** (exclude_tag_names) - NOT logic
4. **Result collection** - Gather all tags from matching series
5. **Result filters**:
   - tag_group_id (filter by type)
   - search_text (filter by name)
6. **Ordering** (order_by, sort_order)
7. **Pagination** (limit, offset)

### Examples of Filter Combinations

#### Example 1: Multiple Required Tags
```python
# Find tags for USA national-level quarterly data
get_category_related_tags(
    32991,
    tag_names="usa;nation;quarterly"
)
# Returns: Tags that co-occur with all three
```

#### Example 2: Required + Exclusions
```python
# Monthly data, but not seasonally adjusted
get_category_related_tags(
    125,
    tag_names="monthly",
    exclude_tag_names="sa;saar"
)
# Returns: Tags for monthly NSA data only
```

#### Example 3: Required + Result Filter
```python
# What sources provide quarterly USA data?
get_category_related_tags(
    32991,
    tag_names="quarterly;usa",
    tag_group_id="src"
)
# Returns: Only source tags (bea, bls, etc.)
```

#### Example 4: Full Filter Stack
```python
# Complex query with all filters
get_category_related_tags(
    32991,
    tag_names="employment;monthly;usa",
    exclude_tag_names="discontinued;preliminary",
    tag_group_id="src",
    search_text="bureau",
    limit=10,
    order_by="popularity"
)
# Returns: Top 10 popular sources containing "bureau" for 
#          USA monthly employment data (excluding discontinued)
```

---

## Discovery Workflows

### Workflow 1: Category → Concept → Frequency → Series

```python
# 1. Start with category
category = get_category(125)
print(f"Exploring: {category['data']['name']}")

# 2. Get all tags in category
all_tags = get_category_tags(125, limit=20)
print(f"Top tags: {[t['name'] for t in all_tags['data'][:5]]}")

# 3. Pick a concept, find related
concept_related = get_category_related_tags(125, "services")
print(f"Related to services: {[t['name'] for t in concept_related['data'][:5]]}")

# 4. Add frequency, narrow down
freq_related = get_category_related_tags(125, "services;quarterly")
print(f"Related to services+quarterly: {[t['name'] for t in freq_related['data'][:5]]}")

# 5. Fetch series with discovered tags
series = get_category_series(125, tag_names="services;quarterly", limit=5)
print(f"Found {series['metadata']['total_count']} series")
```

---

### Workflow 2: Find All Frequencies for a Concept

```python
# Goal: Discover all available frequencies for "gdp" data

# 1. Get frequency tags related to "gdp"
freq_tags = get_category_related_tags(
    32992,  # National Accounts
    "gdp",
    tag_group_id="freq"
)

# 2. Analyze results
for tag in freq_tags['data']:
    print(f"{tag['name']}: {tag['series_count']} series")

# Output example:
# quarterly: 125 series
# annual: 45 series
# monthly: 12 series

# 3. Choose frequency and fetch
series = get_category_series(32992, tag_names="gdp;quarterly", limit=10)
```

---

### Workflow 3: Progressive Refinement

```python
# Start broad, refine progressively

# Level 1: All trade data
tags_1 = get_category_related_tags(125, "trade")
print(f"Tags for trade: {tags_1['metadata']['count']}")

# Level 2: Trade + quarterly
tags_2 = get_category_related_tags(125, "trade;quarterly")
print(f"Tags for trade+quarterly: {tags_2['metadata']['count']}")

# Level 3: Trade + quarterly + USA
tags_3 = get_category_related_tags(125, "trade;quarterly;usa")
print(f"Tags for trade+quarterly+usa: {tags_3['metadata']['count']}")

# Level 4: Add seasonally adjusted
tags_4 = get_category_related_tags(125, "trade;quarterly;usa;sa")
print(f"Tags for trade+quarterly+usa+sa: {tags_4['metadata']['count']}")

# At each level, you narrow down and see what's left
```

---

### Workflow 4: Exclusion-Based Discovery

```python
# Goal: Find non-goods trade series

# 1. What tags exist for "trade" excluding "goods"?
non_goods_tags = get_category_related_tags(
    125,
    "trade",
    exclude_tag_names="goods"
)

# Result likely includes: services, income, transfers, etc.

# 2. Pick "services", find related
services_tags = get_category_related_tags(
    125,
    "trade;services",
    exclude_tag_names="goods"
)

# 3. Use to fetch series
series = get_category_series(
    125,
    tag_names="trade;services",
    exclude_tag_names="goods"
)
```

---

## Error Handling

### Common Errors

#### 1. Missing Required Parameter

**Error:**
```json
{
  "tool": "get_category_related_tags",
  "error": "tag_names is required and cannot be empty"
}
```

**Cause:** tag_names parameter is missing or empty

**Solution:** Provide at least one tag name

---

#### 2. Invalid Category ID

**Error:**
```json
{
  "tool": "get_category_related_tags",
  "error": "Invalid category_id: must be a non-negative integer"
}
```

**Cause:** Category ID is negative or invalid

**Solution:** Use valid non-negative integer category IDs

---

#### 3. Tags Not Found

**Error:**
```json
{
  "tool": "get_category_related_tags",
  "error": "Category not found, has no series, or tags not found: category_id=125, tag_names=nonexistent",
  "category_id": 125,
  "tag_names": "nonexistent"
}
```

**Cause:** Tags don't exist or don't co-occur in category

**Solution:**
- Verify tags exist using `get_category_tags`
- Check spelling
- Try fewer tags (more restrictive = fewer results)

---

#### 4. No Matching Series

**Response:**
```json
{
  "tool": "get_category_related_tags",
  "data": [],
  "metadata": {
    "count": 0,
    ...
  }
}
```

**Cause:** No series match the tag combination

**Solution:**
- Remove some required tags (less restrictive)
- Remove exclusions
- Try different tag combinations
- Use `get_category_tags` to discover valid tags first

---

#### 5. Rate Limit Exceeded

**Error:**
```json
{
  "tool": "get_category_related_tags",
  "error": "Rate limit exceeded. Please try again later.",
  "category_id": 125,
  "tag_names": "services;quarterly"
}
```

**Cause:** Too many requests to FRED API

**Solution:** Wait and retry. Tool has built-in exponential backoff (3 retries)

---

## Performance

### Response Times

| Scenario | Typical Time | Max Time |
|----------|-------------|----------|
| Simple query (1-2 tags) | 200-500ms | 1s |
| Complex query (3+ tags) | 250-600ms | 1.5s |
| With exclusions | 250-600ms | 1.5s |
| With multiple filters | 300-700ms | 2s |
| First request (cold) | 400-800ms | 2s |

### Performance Characteristics

- **More Tags = Faster**: More restrictive queries match fewer series, process faster
- **Exclusions Have Cost**: Each exclusion requires additional filtering
- **Result Filters Are Fast**: tag_group_id and search_text filter results quickly
- **Retry Logic**: 3 attempts with exponential backoff (1-5s)
- **Compact JSON**: AI-optimized format minimizes token usage
- **Session Reuse**: HTTP connection pooling for efficiency

### Optimization Tips

1. **Use Specific Tags**
   ```python
   # Faster: More specific
   tags = get_category_related_tags(125, "services;quarterly;nsa")
   
   # Slower: Less specific (more series to process)
   tags = get_category_related_tags(125, "services")
   ```

2. **Filter Results on API Side**
   ```python
   # Efficient: Filter on server
   tags = get_category_related_tags(125, "services", tag_group_id="freq")
   
   # Inefficient: Fetch all, filter client-side
   tags = get_category_related_tags(125, "services")
   freq_tags = [t for t in tags['data'] if t['group_id'] == 'freq']
   ```

3. **Use Lower Limits for Discovery**
   ```python
   # For quick discovery
   tags = get_category_related_tags(125, "services", limit=20)
   
   # For complete data
   tags = get_category_related_tags(125, "services")  # limit=1000 default
   ```

---

## Best Practices

### 1. Start Broad, Narrow Progressively

```python
# Good: Progressive discovery
tags_1 = get_category_related_tags(125, "trade")
tags_2 = get_category_related_tags(125, "trade;quarterly")
tags_3 = get_category_related_tags(125, "trade;quarterly;usa")

# Bad: Too specific immediately
tags = get_category_related_tags(125, "trade;quarterly;usa;sa;bea;nation")
# May return empty results
```

---

### 2. Validate Tags First

```python
# Good: Check tag exists
all_tags = get_category_tags(125)
if "services" in [t['name'] for t in all_tags['data']]:
    related = get_category_related_tags(125, "services")

# Bad: Assume tag exists
related = get_category_related_tags(125, "nonexistent")
# Will fail
```

---

### 3. Use Filters to Focus Discovery

```python
# Good: Use tag_group_id to focus
freq_tags = get_category_related_tags(125, "services", tag_group_id="freq")
src_tags = get_category_related_tags(125, "services", tag_group_id="src")

# Bad: Parse from all results
all_tags = get_category_related_tags(125, "services")
freq_tags = [t for t in all_tags['data'] if t['group_id'] == 'freq']
```

---

### 4. Handle Empty Results Gracefully

```python
related = get_category_related_tags(125, "rare;tag;combination")

if related['metadata']['count'] == 0:
    # Try with fewer tags
    related = get_category_related_tags(125, "rare;tag")
    
if related['metadata']['count'] == 0:
    # Try with just one tag
    related = get_category_related_tags(125, "rare")
```

---

### 5. Combine with Other Category Tools

```python
# Complete workflow
# 1. Get category info
category = get_category(125)

# 2. Discover available tags
all_tags = get_category_tags(125, limit=20)

# 3. Find related tags for interesting ones
for tag in all_tags['data'][:3]:
    related = get_category_related_tags(125, tag['name'], limit=10)
    print(f"Related to {tag['name']}: {[t['name'] for t in related['data']]}")

# 4. Use discovered tags to fetch series
series = get_category_series(125, tag_names="discovered;tags")
```

---

## Related Tools

### Complementary Tools

| Tool | Purpose | When to Use |
|------|---------|------------|
| `get_fred_category` | Get category metadata | Start here - get category info |
| `get_fred_category_tags` | Get all tags in category | Discover available tags |
| `get_fred_category_related_tags` | Get related tags | Find tag co-occurrences (this tool) |
| `get_fred_category_series` | Get series in category | Fetch actual series with tags |
| `get_fred_series_tags` | Get tags for a series | See what tags a specific series has |

### Typical Workflow

```python
# 1. Start with category
category = get_category(125)
print(f"Category: {category['data']['name']}")

# 2. Discover all available tags
all_tags = get_category_tags(125, limit=30)
print(f"Top tags: {[t['name'] for t in all_tags['data'][:10]]}")

# 3. Pick interesting tag, find related (this tool)
related = get_category_related_tags(125, "services")
print(f"Related to services: {[t['name'] for t in related['data'][:10]]}")

# 4. Find what frequencies are available
freq_tags = get_category_related_tags(125, "services", tag_group_id="freq")
print(f"Frequencies: {[t['name'] for t in freq_tags['data']]}")

# 5. Use discovered tags to fetch series
series = get_category_series(125, tag_names="services;quarterly", limit=5)
print(f"Found {series['metadata']['total_count']} series")

# 6. Get observations for interesting series
for s in series['data'][:2]:
    obs = get_series_observations(s['id'], limit=10)
    print(f"{s['title']}: latest {len(obs['data'])} observations")
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-01 | Initial implementation |

---

## Additional Resources

- **FRED API Documentation**: https://fred.stlouisfed.org/docs/api/fred/
- **FRED Category Related Tags Endpoint**: https://fred.stlouisfed.org/docs/api/fred/category_related_tags.html
- **FRED Tags Documentation**: https://fred.stlouisfed.org/docs/api/fred/tags.html
- **FRED Website**: https://fred.stlouisfed.org/
- **Tag Search**: https://fred.stlouisfed.org/tags/series

---

## Support

For issues or questions:
1. Check FRED API status: https://fred.stlouisfed.org/docs/api/api_status.html
2. Review error messages in response JSON
3. Verify tags exist using `get_category_tags`
4. Try with fewer tags if no results
5. Check that category has series
6. Review server logs for detailed error information

---

**Last Updated:** 2025-11-01  
**Tool Version:** 1.0.0  
**FRED API Version:** Stable (no versioning)
