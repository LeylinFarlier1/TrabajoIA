# Release Notes - Trabajo IA MCP Server v0.1.3

**Release Date:** November 1, 2025
**Type:** Feature Addition Release
**Focus:** Tag Discovery & Search Enhancement

---

## Overview

Version 0.1.3 adds the **`get_fred_tags` tool**, enabling users to discover and explore available FRED tags before constructing search queries. This complements the existing `search_fred_series` tool by helping users understand FRED's taxonomy and find the correct tag names for filtering.

### Key Achievement

**Complete tag discovery system** with search, filtering by group type, and detailed metadata about each tag.

---

## What's New

### New Tool: `get_fred_tags`

Discover available FRED tags to construct more effective searches.

**Core Functionality:**
```python
# Get top 50 most popular tags
get_fred_tags()

# Search for specific tags
get_fred_tags(search_text="employment")

# Filter by tag group
get_fred_tags(tag_group_id="freq")  # All frequency tags

# Custom results
get_fred_tags(tag_group_id="geo", limit=100)
```

**Response Format:**
```json
{
  "tool": "get_fred_tags",
  "data": [
    {
      "name": "nsa",
      "group_id": "seas",
      "notes": "Not seasonally adjusted",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 96,
      "series_count": 747558
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
    "search_text": null,
    "tag_group_id": null,
    "total_count": 5000,
    "returned_count": 50,
    "limit": 50,
    "offset": 0,
    "order_by": "popularity",
    "sort_order": "desc"
  }
}
```

---

## Features

### 1. Tag Search

Find tags by keyword:

```python
# Find employment-related tags
get_fred_tags(search_text="employment")
# Returns: employment, unemployment, employment cost index, etc.

# Find inflation tags
get_fred_tags(search_text="inflation")
# Returns: inflation, cpi, pce, core inflation, etc.
```

### 2. Filter by Tag Group

8 tag group types available:

| Group ID | Description | Example Tags |
|----------|-------------|--------------|
| `freq` | Frequency | monthly, quarterly, annual, weekly |
| `gen` | General/Concept | gdp, employment, cpi, rate |
| `geo` | Geography | usa, canada, japan, china |
| `geot` | Geography Type | nation, state, county, msa |
| `rls` | Release | main economic indicators |
| `seas` | Seasonal Adjustment | sa, nsa |
| `src` | Source | bls, bea, census, oecd |
| `cc` | Citation & Copyright | public domain, copyrighted |

**Examples:**
```python
# Get all frequency tags
get_fred_tags(tag_group_id="freq")

# Get all geography tags
get_fred_tags(tag_group_id="geo", limit=100)

# Get all source tags
get_fred_tags(tag_group_id="src")
```

### 3. Tag Metadata

Each tag includes:
- **name**: Tag identifier
- **group_id**: Category (freq, gen, geo, etc.)
- **notes**: Description of the tag
- **created**: When tag was created
- **popularity**: FRED popularity score (0-100)
- **series_count**: Number of series with this tag

### 4. Sorting Options

Sort by different criteria:

```python
# By popularity (default)
get_fred_tags(order_by="popularity", sort_order="desc")

# By series count
get_fred_tags(order_by="series_count", sort_order="desc")

# Alphabetically
get_fred_tags(order_by="name", sort_order="asc")

# By creation date
get_fred_tags(order_by="created", sort_order="desc")
```

---

## Use Cases

### 1. Discover Available Tags

Before searching for series, discover what tags exist:

```python
# Workflow:
# Step 1: Find tags
tags = get_fred_tags(search_text="unemployment")

# Step 2: Use discovered tags in search
series = search_fred_series(
    "labor market",
    tag_names="usa;nsa;unemployment"
)
```

### 2. Explore FRED Taxonomy

Learn how FRED organizes data:

```python
# Get all frequency options
freq_tags = get_fred_tags(tag_group_id="freq")
# Returns: monthly, quarterly, annual, weekly, daily, etc.

# Get all seasonal adjustment options
seas_tags = get_fred_tags(tag_group_id="seas")
# Returns: sa (seasonally adjusted), nsa (not seasonally adjusted)
```

### 3. Find Correct Tag Names

Tags must be exact for filtering. This tool helps find the right names:

```python
# Wrong: tag_names="US"
# Right: tag_names="usa"

# Discover the correct name:
geo_tags = get_fred_tags(tag_group_id="geo", search_text="united states")
# Shows: "usa" is the correct tag name
```

### 4. Popular Tags Discovery

Find the most commonly used tags:

```python
# Top 10 most popular tags across all of FRED
popular_tags = get_fred_tags(limit=10, order_by="popularity")
```

---

## Integration with search_fred_series

Perfect complement to the search tool:

```python
# Workflow Example: Find monthly employment data

# Step 1: Check what frequency tags exist
freq_tags = get_fred_tags(tag_group_id="freq")
# Discover: "monthly" tag exists

# Step 2: Check employment tags
emp_tags = get_fred_tags(search_text="employment")
# Discover: "employment", "unemployment" tags

# Step 3: Search with discovered tags
results = search_fred_series(
    "labor force",
    tag_names="monthly;employment;usa",
    limit=20
)
```

---

## Parameters

### Required
None - all parameters are optional

### Optional

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search_text` | string | None | Search for tags matching this text |
| `tag_names` | string | None | Filter by semicolon-delimited tag names |
| `tag_group_id` | string | None | Filter by group: freq, gen, geo, geot, rls, seas, src, cc |
| `limit` | integer | 50 | Max results (1-1000) |
| `offset` | integer | 0 | Starting offset for pagination |
| `order_by` | string | "popularity" | Sort field: series_count, popularity, created, name, group_id |
| `sort_order` | string | "desc" | Sort direction: asc or desc |

---

## Performance

- **Response Time:** ~0.5-1 second
- **Default Limit:** 50 tags (optimized for AI consumption)
- **JSON Format:** Compact (token-efficient)
- **Retry Mechanism:** 3 attempts with 1-5s exponential backoff
- **Rate Limiting:** Automatic detection and handling

---

## Examples

### Example 1: Basic Discovery

```python
get_fred_tags()
```

**Returns:** Top 50 most popular tags across FRED

**Use:** General exploration of FRED's tag system

### Example 2: Find Frequency Tags

```python
get_fred_tags(tag_group_id="freq")
```

**Returns:**
```json
{
  "data": [
    {"name": "monthly", "series_count": 220226},
    {"name": "annual", "series_count": 493258},
    {"name": "quarterly", "series_count": 143580},
    {"name": "weekly", "series_count": 12458},
    ...
  ]
}
```

**Use:** Discover all available frequency options for filtering

### Example 3: Search Employment Tags

```python
get_fred_tags(search_text="employment", limit=20)
```

**Returns:** All tags containing "employment" in name or notes

**Use:** Find employment-related tags for targeted searches

### Example 4: Geography Tags

```python
get_fred_tags(tag_group_id="geo", limit=100)
```

**Returns:** Top 100 geography tags (usa, canada, japan, etc.)

**Use:** Discover country/region tags for geographic filtering

### Example 5: Find Data Sources

```python
get_fred_tags(tag_group_id="src")
```

**Returns:**
```json
{
  "data": [
    {"name": "bls", "notes": "U.S. Department of Labor: Bureau of Labor Statistics"},
    {"name": "bea", "notes": "U.S. Department of Commerce: Bureau of Economic Analysis"},
    {"name": "census", "notes": "U.S. Census Bureau"},
    ...
  ]
}
```

**Use:** Understand data provenance and filter by source

---

## Common Tag Groups

### Frequency Tags (`freq`)
- `monthly` - Monthly frequency
- `quarterly` - Quarterly frequency
- `annual` - Annual frequency
- `weekly` - Weekly frequency
- `daily` - Daily frequency
- `semiannual` - Semiannual frequency
- `biweekly` - Biweekly frequency

### Seasonal Adjustment (`seas`)
- `sa` - Seasonally Adjusted
- `nsa` - Not Seasonally Adjusted

### Popular Geography Tags (`geo`)
- `usa` - United States
- `canada` - Canada
- `japan` - Japan
- `germany` - Germany
- `uk` - United Kingdom

### Common Concept Tags (`gen`)
- `gdp` - Gross Domestic Product
- `employment` - Employment data
- `unemployment` - Unemployment data
- `cpi` - Consumer Price Index
- `inflation` - Inflation measures
- `interest rate` - Interest rates

---

## Tips & Best Practices

### 1. Start Broad, Then Narrow

```python
# 1. Start with general search
all_tags = get_fred_tags(search_text="price")

# 2. Then filter by group
price_concept_tags = get_fred_tags(
    search_text="price",
    tag_group_id="gen"
)
```

### 2. Use Tag Discovery Before Searching Series

```python
# Good workflow:
# 1. Discover tags first
tags = get_fred_tags(tag_group_id="freq")

# 2. Use discovered tags in search
series = search_fred_series("GDP", tag_names="quarterly")

# Bad workflow:
# Guessing tag names without verification
series = search_fred_series("GDP", tag_names="quarterly data")  # Wrong!
```

### 3. Check Series Counts

Tags with higher `series_count` have more data:

```python
tags = get_fred_tags(order_by="series_count", sort_order="desc")
# Focus on tags with many series for better search results
```

### 4. Combine with search_fred_series

```python
# Discover -> Search workflow
# 1. Find relevant tags
employment_tags = get_fred_tags(search_text="employment")

# 2. Use in search
results = search_fred_series(
    "labor market",
    tag_names="employment;usa;nsa"
)
```

---

## Breaking Changes

None - this is a purely additive release.

---

## Compatibility

### Backwards Compatibility

Fully backward compatible with v0.1.2:
- All existing tools unchanged
- No configuration changes required
- No dependency updates needed

### Dependencies

No new dependencies added. Uses existing:
- `requests>=2.31.0`
- `tenacity>=8.2.0`

---

## Installation & Upgrade

### New Installation

```bash
cd server
uv sync
```

### Upgrade from v0.1.2

```bash
cd server
uv sync
# Server automatically uses new version
```

### Verify Installation

```python
from trabajo_ia_server import __version__
print(__version__)  # Should print: 0.1.3

# Test the new tool
from trabajo_ia_server.tools.fred.get_tags import get_fred_tags
result = get_fred_tags(limit=5)
print(result)  # Should return JSON with 5 tags
```

---

## Known Issues

None currently identified.

---

## Future Enhancements

Planned for v0.2.0:
- `get_series_info` - Detailed metadata for specific series
- `get_series_categories` - Browse FRED category hierarchy
- Response caching for frequently accessed tags
- Tag relationship exploration

---

## Files Added

- `src/trabajo_ia_server/tools/fred/get_tags.py` - New tool implementation (200+ lines)
- `docs/Release_notes/RELEASE_NOTES_v0.1.3.md` - This file
- Updated `docs/Changelog/CHANGELOG.md` with v0.1.3 entry

## Files Modified

- `src/trabajo_ia_server/server.py` - Registered `get_fred_tags` tool
- `src/trabajo_ia_server/tools/fred/__init__.py` - Exported new function
- `src/trabajo_ia_server/__init__.py` - Version bump to 0.1.3
- `src/trabajo_ia_server/config.py` - Version bump to 0.1.3
- `pyproject.toml` - Version bump to 0.1.3

---

## Summary

**v0.1.3 enhances discoverability:**

- New `get_fred_tags` tool for tag discovery
- 8 tag group types for organized exploration
- Search, filter, and sort tags
- Perfect complement to `search_fred_series`
- Fast, AI-optimized responses

**Upgrade recommended for:**
- Users new to FRED who need to discover available tags
- Advanced users wanting to explore FRED's taxonomy
- Anyone constructing complex filtered searches
- Applications needing tag validation

---

**Version:** 0.1.3
**Release Date:** November 1, 2025
**Status:** Production Ready
**Recommended:** Yes
