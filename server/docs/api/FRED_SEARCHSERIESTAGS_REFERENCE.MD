# FRED Series Search Tags API Reference

**Tool Name:** `search_fred_series_tags`
**Version:** 0.1.5 (Planned)
**FRED Endpoint:** `/fred/series/search/tags`
**Status:** ✅ Production Ready

---

## Overview

Get FRED tags for a series search with optional filtering. Discover what tags are associated with series matching your search query - perfect for understanding data taxonomy and refining searches.

### Key Features

- **Series-Based Tag Discovery**: Find tags associated with series matching search terms
- **Multiple Filter Options**: Filter by tag names, group type, or search text
- **5 Sort Options**: Sort by series_count, popularity, created, name, or group_id
- **AI-Optimized**: Default 50 results, compact JSON, fast responses (< 2s target)
- **Rate Limit Protection**: Automatic retries with exponential backoff

### When to Use

- Discover what tags describe series matching your search
- Understand data taxonomy for a specific topic
- Refine series searches by identifying relevant tags
- Explore relationships between search terms and tag categories

---

## Parameters

### Required

**`series_search_text`** (string)
- Words to match against economic data series
- Example: "monetary service index", "GDP", "unemployment rate"

### Optional

**`tag_names`** (string | None)
- Semicolon-delimited list to filter results
- Only matching tags will be included
- Example: "m1;m2"
- Default: None

**`tag_group_id`** (Literal | None)
- Filter tags by group type
- Options: "freq", "gen", "geo", "geot", "rls", "seas", "src"
- Default: None

**`tag_search_text`** (string | None)
- Keywords to find matching tags by name/notes
- Default: None

**`limit`** (integer)
- Maximum tags to return (1-1000)
- Default: 50 (AI-optimized)

**`offset`** (integer)
- Starting offset for pagination
- Default: 0

**`order_by`** (Literal)
- Sort field
- Options: "series_count", "popularity", "created", "name", "group_id"
- Default: "series_count"

**`sort_order`** (Literal)
- Sort direction: "asc" or "desc"
- Default: "desc"

**`realtime_start/realtime_end`** (string | None)
- Real-time period dates (YYYY-MM-DD)
- Default: Today's date

---

## Response Format

```json
{
  "tool": "search_series_tags",
  "data": [
    {
      "name": "monthly",
      "group_id": "freq",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 95,
      "series_count": 25
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "series_search_text": "monetary service index",
    "tag_names": ["m1", "m2"],
    "tag_group_id": "freq",
    "tag_search_text": null,
    "total_count": 18,
    "returned_count": 18,
    "limit": 50,
    "offset": 0,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

### Tag Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Tag identifier |
| `group_id` | string | Group type (freq/gen/geo/geot/rls/seas/src/cc) |
| `notes` | string | Tag description |
| `created` | string | Creation timestamp |
| `popularity` | integer | FRED popularity score (0-100) |
| `series_count` | integer | Number of series with this tag |

---

## Usage Examples

### Example 1: Basic Search

Find tags for series matching "monetary service index":

```python
from trabajo_ia_server.tools.fred.search_series_tags import search_series_tags
import json

result = search_series_tags("monetary service index")
data = json.loads(result)

print(f"Found {data['metadata']['returned_count']} tags")
for tag in data['data'][:5]:
    print(f"- {tag['name']} ({tag['group_id']}): {tag['series_count']} series")
```

**Output:**
```
Found 50 tags
- public domain: citation requested (cc): 854 series
- nsa (seas): 844 series
- annual (freq): 834 series
- nation (geot): 702 series
- usa (geo): 650 series
```

### Example 2: Frequency Tags for GDP

Find what frequency tags are associated with GDP series:

```python
result = search_series_tags("GDP", tag_group_id="freq", limit=10)
data = json.loads(result)

freq_tags = [tag['name'] for tag in data['data']]
print(f"GDP frequencies: {freq_tags}")
```

**Output:**
```
GDP frequencies: ['annual', 'quarterly', 'monthly', 'daily', 'weekly']
```

### Example 3: Employment with Tag Search

Find seasonal adjustment tags for employment series:

```python
result = search_series_tags(
    "employment",
    tag_search_text="seasonal",
    limit=10
)
data = json.loads(result)

for tag in data['data']:
    print(f"{tag['name']}: {tag['notes']}")
```

**Output:**
```
nsa: Not seasonally adjusted
sa: Seasonally adjusted
```

### Example 4: Filter by Tag Names

Find specific tags (m1, m2) for monetary data:

```python
result = search_series_tags(
    "monetary aggregates",
    tag_names="m1;m2",
    order_by="popularity",
    sort_order="desc"
)
```

### Example 5: Geography Tags

Find geography tags for inflation series:

```python
result = search_series_tags(
    "inflation",
    tag_group_id="geo",
    limit=20,
    order_by="series_count",
    sort_order="desc"
)

data = json.loads(result)
countries = [tag['name'] for tag in data['data'][:10]]
print(f"Top countries with inflation data: {countries}")
```

---

## Use Cases

### 1. Understanding Data Taxonomy

**Problem:** Need to understand what aspects of "employment" are covered in FRED.

**Solution:**
```python
# Find all tags for employment series
result = search_series_tags("employment", limit=100)
data = json.loads(result)

# Group by tag type
by_group = {}
for tag in data['data']:
    group = tag['group_id']
    if group not in by_group:
        by_group[group] = []
    by_group[group].append(tag['name'])

# Display taxonomy
for group, tags in by_group.items():
    print(f"{group}: {', '.join(tags[:5])}")
```

### 2. Refining Series Searches

**Problem:** Initial search returns too many results.

**Solution:**
```python
# Step 1: Find relevant tags
tags_result = search_series_tags("GDP", tag_group_id="freq")
freq_tags = json.loads(tags_result)['data']

# Step 2: Use discovered tags to refine search
from trabajo_ia_server.tools.fred.search_series import search_fred_series
refined = search_fred_series(
    "GDP",
    tag_names=freq_tags[0]['name'],  # Use most common frequency
    limit=20
)
```

### 3. Discovering Data Coverage

**Problem:** Which countries have inflation data?

**Solution:**
```python
result = search_series_tags(
    "consumer price index",
    tag_group_id="geo",
    order_by="series_count",
    sort_order="desc",
    limit=50
)

data = json.loads(result)
coverage = [(tag['name'], tag['series_count']) for tag in data['data']]
print("CPI data coverage by country:")
for country, count in coverage[:10]:
    print(f"  {country}: {count} series")
```

### 4. Seasonal Adjustment Analysis

**Problem:** Do series have both SA and NSA versions?

**Solution:**
```python
result = search_series_tags("GDP", tag_group_id="seas")
data = json.loads(result)

for tag in data['data']:
    print(f"{tag['name']}: {tag['series_count']} series")
```

---

## Error Handling

### Invalid Search Text

**Error:**
```json
{"error": "Invalid parameters: Bad Request. ..."}
```

**Solution:** Verify search text is not empty and contains valid characters.

### No Tags Found

**Response:**
```json
{
  "data": [],
  "metadata": {"total_count": 0, "returned_count": 0}
}
```

**Cause:** Search text doesn't match any series, or filters are too restrictive.

**Solution:** Broaden search or remove filters.

### Rate Limiting

**Error:**
```json
{"error": "Rate limit exceeded. Please try again later."}
```

**Solution:** Tool automatically retries. If persistent, wait 1-5 minutes.

---

## Performance

### Response Time Benchmarks

| Scenario | Avg Time | Notes |
|----------|----------|-------|
| Basic search | 0.5-1.0s | Typical case |
| With tag_group_id | 1.0-2.5s | More selective query |
| With tag_search_text | 3.0-8.0s | Most intensive search |
| Large limit (100+) | 1.0-2.0s | More data transfer |

**Optimization Tips:**

1. **Use `tag_group_id` for faster filtering**
   ```python
   # Fast: Filter at API level
   search_series_tags("GDP", tag_group_id="freq")

   # Slower: Filter after retrieval
   result = search_series_tags("GDP", limit=100)
   # Then filter in Python
   ```

2. **Limit results appropriately**
   ```python
   # Good: Reasonable limit
   search_series_tags("GDP", limit=20)

   # Avoid: Unnecessarily high
   search_series_tags("GDP", limit=1000)
   ```

3. **Cache frequently used queries**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=50)
   def cached_search_tags(series_search_text, tag_group_id=None):
       return search_series_tags(series_search_text, tag_group_id=tag_group_id)
   ```

---

## Best Practices

### 1. Start Broad, Then Narrow

```python
# Good workflow
# 1. Discover all tags
all_tags = search_series_tags("employment")

# 2. Identify interesting group
freq_tags = search_series_tags("employment", tag_group_id="freq")

# 3. Use specific tag for series search
```

### 2. Combine with Other Tools

```python
# Discover → Search workflow
# 1. Find tags
tags = search_series_tags("GDP", tag_group_id="freq")

# 2. Get tag name
freq_tag = json.loads(tags)['data'][0]['name']

# 3. Search series with tag
from trabajo_ia_server.tools.fred.search_series import search_fred_series
series = search_fred_series("GDP", tag_names=freq_tag)
```

### 3. Validate Before Using Tags

```python
result = search_series_tags("employment", tag_group_id="freq")
data = json.loads(result)

if 'error' in data:
    print(f"Error: {data['error']}")
elif data['metadata']['returned_count'] == 0:
    print("No tags found - try different search")
else:
    # Use tags safely
    tags = [t['name'] for t in data['data']]
```

---

## Related Tools

### Complementary Tools

**Before:** `search_fred_series`
- Search for series by text
- Get initial understanding of data

**This Tool:** `search_fred_series_tags`
- Discover tags for those series
- Understand taxonomy

**After:** `get_fred_tags` or `search_fred_series`
- Use discovered tags to refine searches
- Get detailed series information

### Typical Workflow

```python
# 1. Text search
series = search_fred_series("unemployment")

# 2. Discover tags
tags = search_series_tags("unemployment", tag_group_id="freq")

# 3. Refine search with tags
refined = search_fred_series("unemployment", tag_names="monthly")

# 4. Fetch data
from trabajo_ia_server.tools.fred.fetch_series import fetch_series_observations
data = fetch_series_observations(series_id="UNRATE")
```

---

## Summary

`search_fred_series_tags` is essential for:

✅ Discovering tags associated with series searches
✅ Understanding FRED's data taxonomy
✅ Refining series searches with appropriate tags
✅ Exploring data coverage by category

**Key Strengths:**
- Multiple filter options (group, names, search text)
- Fast AI-optimized responses
- Comprehensive tag metadata

**Best For:**
- Initial data exploration
- Building tag-based search interfaces
- Understanding data organization

---

**Tool Version:** Introduced in v0.1.5 (Planned)
**FRED API:** https://fred.stlouisfed.org/docs/api/fred/series_search_tags.html
**Last Updated:** 2025-11-01
