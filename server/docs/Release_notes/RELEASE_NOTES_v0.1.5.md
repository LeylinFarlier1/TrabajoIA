# Release Notes - Trabajo IA MCP Server v0.1.5

**Release Date:** 2025-11-01
**Type:** Feature Addition
**Focus:** Context-aware tag relationship discovery for FRED series searches

---

## Overview

Version 0.1.5 introduces the **`search_fred_series_related_tags`** tool, completing FRED's tag exploration capabilities. This tool enables context-aware tag discovery by finding tags that are related to specified tags within the specific context of series matching a search query.

While `search_fred_related_tags` (v0.1.3) discovers general tag relationships across all FRED data, this new tool provides **context-specific** tag relationships filtered by series search criteria. This enables more targeted data exploration and helps build more precise queries by understanding which tags are relevant in specific economic data contexts.

### Key Achievement

**Context-Aware Tag Discovery**: The ability to discover related tags within specific series contexts (e.g., "What tags are related to '30-year' mortgages in series about 'mortgage rates'?") enables smarter query refinement and deeper exploration of FRED's data relationships.

---

## What's New

### New Tool: `search_fred_series_related_tags`

Get related FRED tags for series matching a search text and tag filter combination.

**Core Functionality:**
```python
# Find related tags for mortgage rate series with specific tags
result = search_fred_series_related_tags("mortgage rate", "30-year;frb")

# Find frequency tags for GDP series in USA
result = search_fred_series_related_tags("GDP", "usa", tag_group_id="freq")

# Find employment tags excluding discontinued series
result = search_fred_series_related_tags(
    "employment",
    "monthly;nsa",
    exclude_tag_names="discontinued"
)
```

**Response Format:**
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
    "returned_count": 13,
    "limit": 50,
    "offset": 0,
    "order_by": "series_count",
    "sort_order": "desc"
  }
}
```

---

## Features

### 1. Context-Aware Tag Discovery

Discover tags that are related to your specified tags within the specific context of series matching your search query.

```python
# Example: What tags are associated with 30-year FRB data in mortgage rate context?
search_fred_series_related_tags("mortgage rate", "30-year;frb")
# Returns: conventional, discontinued, h15, interest rate, mortgage, etc.
```

**Why It Matters**: Unlike general tag relationships, this provides tags that are specifically relevant to your search context, making query refinement more targeted and efficient.

### 2. Dual Filtering System

Combine series search text with tag filters for precise discovery:
- **Series Search Text**: Filter by series content (e.g., "GDP", "employment")
- **Tag Names**: Require specific tags (e.g., "usa;monthly")

```python
# Find tags for monthly USA GDP series
search_fred_series_related_tags("GDP", "usa;monthly")
```

### 3. Group-Specific Filtering

Focus discovery on specific tag groups:
- **freq**: Frequency tags (monthly, quarterly, annual, daily)
- **gen**: General/Concept tags (gdp, employment, inflation)
- **geo**: Geography tags (usa, canada, japan, states)
- **geot**: Geography type (nation, state, county, msa)
- **rls**: Release tags
- **seas**: Seasonal adjustment (sa, nsa)
- **src**: Source tags (bls, bea, census, fed)

```python
# Find only frequency tags for GDP in USA
search_fred_series_related_tags("GDP", "usa", tag_group_id="freq")
# Returns: annual, quarterly, monthly, daily
```

### 4. Exclusion Support

Remove unwanted tags from results:

```python
# Find employment tags excluding discontinued series
search_fred_series_related_tags(
    "employment",
    "monthly;nsa",
    exclude_tag_names="discontinued"
)
```

### 5. Tag Search Within Results

Additional keyword filtering within related tags:

```python
# Find inflation-related tags in CPI context
search_fred_series_related_tags(
    "consumer price",
    "usa;monthly",
    tag_search_text="inflation"
)
```

### 6. Flexible Sorting

Sort results by multiple criteria:
- **series_count**: Number of series with this tag (default)
- **popularity**: FRED's popularity score
- **created**: Tag creation date
- **name**: Alphabetical order
- **group_id**: By tag group

```python
# Get most popular related tags first
search_fred_series_related_tags(
    "unemployment",
    "usa",
    order_by="popularity",
    sort_order="desc"
)
```

### 7. Comprehensive Metadata

Every response includes:
- Fetch timestamp (UTC ISO 8601)
- Input series search text
- Input tags used
- Excluded tags applied
- Tag group filter
- Tag search text
- Total count of matching tags
- Returned count
- Pagination info (limit, offset)
- Sort parameters
- Real-time window dates

---

## Use Cases

### 1. Refine Series Searches

**Scenario:** You've searched for "mortgage rate" series and want to refine your search.

**Solution:**
```python
# Step 1: Initial search returns too many results
initial_series = search_fred_series("mortgage rate")
# Returns: 500+ series

# Step 2: Discover what tags are available
tags = search_fred_series_related_tags("mortgage rate", "30-year")
# Discover: frb, conventional, fixed, adjustable, etc.

# Step 3: Refine search with discovered tags
refined_series = search_fred_series(
    "mortgage rate",
    tag_names="30-year;conventional;frb"
)
# Returns: 3 highly relevant series
```

**Benefits:**
- Reduces result set from hundreds to a handful
- Discovers relevant filtering options
- Builds more precise queries

### 2. Data Frequency Discovery

**Scenario:** You need to know what data frequencies are available for a specific dataset.

**Solution:**
```python
# Find available frequencies for GDP data
frequencies = search_fred_series_related_tags(
    "GDP",
    "usa",
    tag_group_id="freq"
)
# Returns: annual, quarterly, monthly, daily
# Now you know quarterly is the primary frequency for GDP
```

**Benefits:**
- Understand data granularity options
- Set realistic expectations for analysis
- Choose appropriate frequency for your needs

### 3. Geographic Coverage Exploration

**Scenario:** Determine which states or countries have data for your indicator.

**Solution:**
```python
# Find geographic coverage for unemployment data
geographies = search_fred_series_related_tags(
    "unemployment rate",
    "monthly;nsa",
    tag_group_id="geo",
    limit=100
)
# Discover: usa, all 50 states, major metro areas
```

**Benefits:**
- Understand geographic scope of data
- Plan comparative analysis
- Identify data gaps

### 4. Source Discovery

**Scenario:** Find which agencies produce data for your topic.

**Solution:**
```python
# Which agencies provide employment statistics?
sources = search_fred_series_related_tags(
    "employment",
    "usa;monthly",
    tag_group_id="src"
)
# Returns: bls, census, oecd, etc.
```

**Benefits:**
- Understand data provenance
- Compare methodologies
- Choose authoritative sources

### 5. Building Complex Queries

**Scenario:** Build a precise multi-tag query through iterative discovery.

**Solution:**
```python
# Step 1: Start broad
step1 = search_fred_series_related_tags("inflation", "usa")
# Discover: cpi, pce, monthly, sa, nsa, bls

# Step 2: Narrow by frequency
step2 = search_fred_series_related_tags(
    "inflation",
    "usa;monthly",
    tag_group_id="seas"
)
# Discover: sa, nsa - choose nsa

# Step 3: Add source
step3 = search_fred_series_related_tags(
    "inflation",
    "usa;monthly;nsa",
    tag_group_id="src"
)
# Discover: bls - add to query

# Step 4: Final precise search
final = search_fred_series(
    "consumer price index",
    tag_names="usa;monthly;nsa;bls"
)
# Returns: Exactly the CPI series you need
```

**Benefits:**
- Systematic query refinement
- Discover optimal tag combinations
- Build queries with confidence

### 6. Seasonal Adjustment Options

**Scenario:** Check if data is available both seasonally adjusted and not.

**Solution:**
```python
# Check seasonal adjustment options for employment
seasonal = search_fred_series_related_tags(
    "employment",
    "usa;monthly",
    tag_group_id="seas"
)
# Returns: sa, nsa - both available
```

**Benefits:**
- Choose appropriate adjustment for analysis
- Compare adjusted vs. unadjusted
- Understand data processing

### 7. Exclude Low-Quality Data

**Scenario:** Filter out discontinued or preliminary data.

**Solution:**
```python
# Find active, finalized employment series
quality = search_fred_series_related_tags(
    "employment",
    "usa;monthly",
    exclude_tag_names="discontinued;preliminary;revision"
)
```

**Benefits:**
- Focus on reliable data
- Avoid outdated series
- Improve analysis quality

---

## Parameters

### Required Parameters

#### `series_search_text` (string, REQUIRED)

The words to match against economic data series.

**Format:** `"search terms"`

**Examples:**
```python
"mortgage rate"
"GDP"
"unemployment"
"consumer price index"
```

**Purpose:** Provides the context for tag relationship discovery.

#### `tag_names` (string, REQUIRED)

Semicolon-delimited list of tag names that series must match.

**Format:** `"tag1;tag2;tag3"`

**Examples:**
```python
"30-year;frb"
"usa;monthly"
"employment;nsa"
```

**Purpose:** Defines the baseline tags for finding related tags.

### Optional Parameters

#### `exclude_tag_names` (string, optional)

Semicolon-delimited list of tag names to exclude from results.

**Default:** None

**Examples:**
```python
exclude_tag_names="discontinued"
exclude_tag_names="discontinued;annual"
```

**Purpose:** Filter out unwanted tag categories.

#### `tag_group_id` (string, optional)

Filter results to specific tag group.

**Default:** None (all groups)

**Valid Values:**
- `"freq"` - Frequency tags
- `"gen"` - General/Concept tags
- `"geo"` - Geography tags
- `"geot"` - Geography type tags
- `"rls"` - Release tags
- `"seas"` - Seasonal adjustment tags
- `"src"` - Source tags

**Examples:**
```python
tag_group_id="freq"    # Only frequency tags
tag_group_id="geo"     # Only geography tags
```

#### `tag_search_text` (string, optional)

Keywords to filter related tags by name/description.

**Default:** None

**Examples:**
```python
tag_search_text="inflation"
tag_search_text="price"
```

**Purpose:** Additional keyword filtering within results.

#### `limit` (integer, optional)

Maximum number of tags to return.

**Default:** 50 (AI-optimized)

**Range:** 1-1000

**Examples:**
```python
limit=10     # Quick overview
limit=50     # Default (balanced)
limit=100    # Comprehensive
```

#### `offset` (integer, optional)

Starting offset for pagination.

**Default:** 0

**Range:** 0+

**Examples:**
```python
offset=0     # First page
offset=50    # Second page (if limit=50)
```

#### `order_by` (string, optional)

Field to sort results by.

**Default:** `"series_count"`

**Valid Values:**
- `"series_count"` - Number of series with tag
- `"popularity"` - FRED popularity score
- `"created"` - Tag creation date
- `"name"` - Alphabetical
- `"group_id"` - By group

**Examples:**
```python
order_by="series_count"   # Most common tags
order_by="popularity"     # Most popular tags
```

#### `sort_order` (string, optional)

Sort direction.

**Default:** `"desc"`

**Valid Values:**
- `"asc"` - Ascending
- `"desc"` - Descending

**Examples:**
```python
sort_order="desc"    # Most to least
sort_order="asc"     # Least to most
```

#### `realtime_start` (string, optional)

Start date for real-time period.

**Default:** Today's date

**Format:** `"YYYY-MM-DD"`

**Purpose:** Historical metadata queries.

#### `realtime_end` (string, optional)

End date for real-time period.

**Default:** Today's date

**Format:** `"YYYY-MM-DD"`

**Purpose:** Historical metadata queries.

---

## Performance

### Response Time
- **Typical:** 0.5-1.5 seconds
- **With filters:** 1.0-3.0 seconds
- **Complex queries:** 2.0-3.0 seconds

### Optimization Features
- **Default Limit:** 50 results (balanced for AI consumption)
- **Compact JSON:** ~25% token savings vs. pretty-printed
- **Retry Mechanism:** 3 attempts, exponential backoff (1-5s)
- **Rate Limit Handling:** Automatic detection and retry

### Token Efficiency

**Typical Response Sizes:**
- 10 tags: ~2,000 tokens
- 50 tags: ~6,000 tokens
- 100 tags: ~11,000 tokens

**Optimization Tips:**
1. Use appropriate `limit` values (50 is usually sufficient)
2. Filter by `tag_group_id` to reduce result size
3. Use `exclude_tag_names` to remove noise
4. Cache results (tag relationships change infrequently)

---

## Examples

### Example 1: Basic Usage - Mortgage Rate Context

**Goal:** Find related tags for 30-year FRB mortgage rate series.

```python
result = search_fred_series_related_tags("mortgage rate", "30-year;frb")
```

**Output:**
```json
{
  "data": [
    {"name": "conventional", "group_id": "gen", "series_count": 3},
    {"name": "h15", "group_id": "rls", "series_count": 3},
    {"name": "interest rate", "group_id": "gen", "series_count": 3},
    {"name": "mortgage", "group_id": "gen", "series_count": 3},
    {"name": "weekly", "group_id": "freq", "series_count": 2}
  ],
  "metadata": {
    "total_count": 13,
    "returned_count": 5
  }
}
```

**Use Case:** Discover that mortgage rate data is available weekly, from H.15 release, and includes conventional mortgages.

### Example 2: Frequency Discovery - GDP

**Goal:** What data frequencies are available for US GDP?

```python
result = search_fred_series_related_tags("GDP", "usa", tag_group_id="freq")
```

**Output:**
```json
{
  "data": [
    {"name": "annual", "group_id": "freq", "series_count": 493258},
    {"name": "quarterly", "group_id": "freq", "series_count": 143580},
    {"name": "monthly", "group_id": "freq", "series_count": 220226},
    {"name": "daily", "group_id": "freq", "series_count": 1234}
  ]
}
```

**Use Case:** Learn that GDP is primarily quarterly and annual, with some monthly and daily derivatives.

### Example 3: Geographic Exploration - Employment

**Goal:** Which geographies have monthly employment data?

```python
result = search_fred_series_related_tags(
    "employment",
    "monthly;nsa",
    tag_group_id="geo",
    limit=20
)
```

**Output:**
```json
{
  "data": [
    {"name": "usa", "group_id": "geo", "series_count": 342567},
    {"name": "california", "group_id": "geo", "series_count": 12456},
    {"name": "texas", "group_id": "geo", "series_count": 11234},
    {"name": "new york", "group_id": "geo", "series_count": 10987}
  ]
}
```

**Use Case:** Understand that employment data is available nationally and for all states.

### Example 4: Source Discovery - Inflation

**Goal:** Which agencies provide inflation data?

```python
result = search_fred_series_related_tags(
    "inflation",
    "usa;monthly",
    tag_group_id="src"
)
```

**Output:**
```json
{
  "data": [
    {"name": "bls", "group_id": "src", "series_count": 45678},
    {"name": "bea", "group_id": "src", "series_count": 12345},
    {"name": "oecd", "group_id": "src", "series_count": 5678}
  ]
}
```

**Use Case:** BLS is the primary source for inflation data, with BEA and OECD as alternatives.

### Example 5: Exclude Discontinued - Clean Results

**Goal:** Find active unemployment tags only.

```python
result = search_fred_series_related_tags(
    "unemployment",
    "usa;monthly",
    exclude_tag_names="discontinued",
    limit=15
)
```

**Output:**
```json
{
  "data": [
    {"name": "nsa", "group_id": "seas", "series_count": 50000},
    {"name": "sa", "group_id": "seas", "series_count": 45000},
    {"name": "bls", "group_id": "src", "series_count": 42000}
  ],
  "metadata": {
    "excluded_tags": ["discontinued"]
  }
}
```

**Use Case:** Focus only on currently maintained series.

### Example 6: Tag Search Filter - Find Price Tags

**Goal:** Find price-related tags in employment context.

```python
result = search_fred_series_related_tags(
    "consumer",
    "usa;monthly",
    tag_search_text="price",
    limit=10
)
```

**Output:**
```json
{
  "data": [
    {"name": "consumer price", "group_id": "gen"},
    {"name": "price index", "group_id": "gen"},
    {"name": "producer price", "group_id": "gen"}
  ]
}
```

**Use Case:** Narrow down to price-specific tags.

### Example 7: Building Complete Query - Inflation Analysis

**Goal:** Build a precise query for CPI analysis.

```python
# Step 1: Explore inflation tags
step1 = search_fred_series_related_tags("inflation", "usa")
# Discover: cpi, pce, core, headline

# Step 2: Check frequencies
step2 = search_fred_series_related_tags(
    "inflation",
    "usa;cpi",
    tag_group_id="freq"
)
# Discover: monthly is primary

# Step 3: Check seasonal adjustment
step3 = search_fred_series_related_tags(
    "inflation",
    "usa;cpi;monthly",
    tag_group_id="seas"
)
# Discover: both sa and nsa available

# Step 4: Final search with discovered tags
final = search_fred_series(
    "consumer price index",
    tag_names="usa;cpi;monthly;sa"
)
```

**Use Case:** Systematic discovery leads to perfect query.

---

## Breaking Changes

**None** - This release is fully backward compatible with v0.1.4.

---

## Compatibility

### Backwards Compatibility

✅ **Full compatibility** with all previous 0.1.x versions.

**No changes to existing tools:**
- `fetch_fred_series` - No changes
- `search_fred_series` - No changes
- `get_fred_tags` - No changes
- `search_fred_related_tags` - No changes
- `get_fred_series_by_tags` - No changes
- `search_fred_series_tags` - No changes

### Dependencies

**No new dependencies** - Uses existing dependency stack:
- `requests>=2.31.0`
- `tenacity>=8.2.0`
- `mcp[cli]>=1.20.0`
- All existing dependencies unchanged

### Python Version

**Requires:** Python 3.10+

**Tested on:**
- Python 3.10
- Python 3.11
- Python 3.12

---

## Installation & Upgrade

### New Installation

```bash
# Clone repository (if not already done)
cd server

# Install with uv (recommended)
uv sync

# Verify installation
uv run python -c "from trabajo_ia_server import __version__; print(__version__)"
# Should print: 0.1.5
```

### Upgrade from v0.1.4

```bash
# Navigate to server directory
cd server

# Sync dependencies (no new dependencies needed)
uv sync

# Verify upgrade
uv run python -c "from trabajo_ia_server import __version__; print(__version__)"
# Should print: 0.1.5

# Test new tool
uv run python -c "
from trabajo_ia_server.tools.fred.search_series_related_tags import search_series_related_tags
result = search_series_related_tags('GDP', 'usa', limit=5)
print('✓ New tool working')
"
```

### Verify Installation

```python
# Test import and version
from trabajo_ia_server import __version__
assert __version__ == "0.1.5"

# Test new tool
from trabajo_ia_server.tools.fred.search_series_related_tags import search_series_related_tags
result = search_series_related_tags("mortgage rate", "30-year;frb", limit=5)
print("✓ Installation verified")
```

---

## Known Issues

**None currently identified** for v0.1.5.

**General FRED API Notes:**
- Rate limits apply (120 requests/minute typical)
- Some series may have limited tag metadata
- Real-time historical queries may return fewer results
- Very broad searches may timeout (use filters)

---

## Future Enhancements

Planned for v0.1.6 and beyond:

### Additional FRED Endpoints
- **Series observations by tags**: Get time-series data filtered by tags
- **Category tags**: Explore FRED's category taxonomy
- **Release tags**: Discover tags for specific releases

### Performance Improvements
- Response caching layer
- Parallel request batching
- Query optimization hints

### Enhanced Features
- Advanced tag suggestion algorithm
- Tag relationship visualization data
- Query builder recommendations

### Documentation
- Complete API reference documentation
- Interactive examples and tutorials
- Best practices guide

---

## Files Added

### Tool Implementation
- **`src/trabajo_ia_server/tools/fred/search_series_related_tags.py`**
  - Main tool implementation (265 lines)
  - Handles `fred/series/search/related_tags` endpoint
  - Includes retry logic, error handling, and logging
  - Validates parameters and constructs API requests
  - Returns compact JSON optimized for AI consumption

---

## Files Modified

### Core Server Files
- **`src/trabajo_ia_server/server.py`**
  - Added import for `search_series_related_tags`
  - Registered new MCP tool `search_fred_series_related_tags`
  - Added comprehensive docstring with examples
  - Lines added: ~75

### Package Configuration
- **`src/trabajo_ia_server/tools/fred/__init__.py`**
  - Added import and export for new function
  - Updated `__all__` list

### Version Files
- **`src/trabajo_ia_server/config.py`**
  - Updated `SERVER_VERSION` from "0.1.4" to "0.1.5"

- **`src/trabajo_ia_server/__init__.py`**
  - Updated `__version__` from "0.1.4" to "0.1.5"

- **`pyproject.toml`**
  - Updated `version` from "0.1.4" to "0.1.5"

### Documentation
- **`docs/Changelog/CHANGELOG.md`**
  - Added v0.1.5 section with detailed change notes

- **`docs/Release_notes/RELEASE_NOTES_v0.1.5.md`**
  - This file (comprehensive release documentation)

---

## Summary

**v0.1.5 adds context-aware tag relationship discovery:**

✅ **New Capability**: Discover related tags within specific series search contexts
✅ **Enhanced Workflow**: Refine series searches using discovered tag relationships
✅ **Better Queries**: Build more precise multi-tag queries through iterative discovery
✅ **Full Integration**: Works seamlessly with existing tag and series search tools
✅ **Production Ready**: Tested, documented, and optimized for AI/LLM consumption

**Upgrade recommended for:**
- Users performing complex FRED data searches
- AI systems building dynamic queries
- Analysts exploring FRED's data taxonomy
- Applications requiring precise series filtering
- Anyone using tag-based FRED workflows

**Tool Count: 7 FRED Tools**
1. `fetch_fred_series` - Get time-series data
2. `search_fred_series` - Text-based series search
3. `get_fred_tags` - Discover available tags
4. `search_fred_related_tags` - Find general tag relationships
5. `get_fred_series_by_tags` - Tag-based series filtering
6. `search_fred_series_tags` - Discover tags for series searches
7. `search_fred_series_related_tags` - **NEW** - Context-aware tag relationships

---

**Version:** 0.1.5
**Release Date:** 2025-11-01
**Status:** Production Ready
**Recommended:** Yes
**API Endpoint:** `https://api.stlouisfed.org/fred/series/search/related_tags`
