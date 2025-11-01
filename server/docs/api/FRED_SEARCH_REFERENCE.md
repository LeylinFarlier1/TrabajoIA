# FRED Search Tool - API Reference

## Tool: `search_fred_series`

Advanced search tool for FRED economic data series with comprehensive filtering and pagination support.

## Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search_text` | string | Text to search for in series titles, descriptions, and metadata |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 50 | Max results per page (1-1000) |
| `paginate` | bool | False | Fetch all results across multiple pages |
| `offset` | int | 0 | Starting offset for pagination |
| `search_type` | string | "full_text" | Search mode: "full_text" or "series_id" |
| `category_id` | int | None | Restrict to specific FRED category ID |
| `filter_variable` | string | None | Metadata variable to filter by |
| `filter_value` | string | None | Value for filter_variable |
| `tag_names` | string | None | Tags to include (semicolon-delimited) |
| `exclude_tag_names` | string | None | Tags to exclude (semicolon-delimited) |
| `realtime_start` | string | None | Real-time window start (YYYY-MM-DD) |
| `realtime_end` | string | None | Real-time window end (YYYY-MM-DD) |
| `order_by` | string | "popularity" | Sort field (see valid values below) |
| `sort_order` | string | "desc" | Sort direction: "asc" or "desc" |

## Valid Parameter Values

### search_type

- **`"full_text"`** (default): Searches series attributes (title, units, frequency, tags)
  - Parses words into stems (e.g., "Industry" matches "Industries")
  - Supports multiple words (e.g., "money stock")
  - Remember to URL encode spaces

- **`"series_id"`**: Substring search on series IDs
  - `*` can be used as wildcard
  - Examples:
    - `"ex"` finds series containing "ex" anywhere
    - `"ex*"` finds series starting with "ex"
    - `"*ex"` finds series ending with "ex"
    - `"m*sl"` finds series starting with "m" and ending with "sl"

### filter_variable

Filter by metadata attributes:

- **`"frequency"`** - Data frequency
- **`"units"`** - Data units
- **`"seasonal_adjustment"`** - Seasonal adjustment type

### filter_value (examples by variable)

**For frequency:**
- `"Daily"`, `"Weekly"`, `"Biweekly"`, `"Monthly"`, `"Quarterly"`, `"Semiannual"`, `"Annual"`

**For units:**
- `"Percent"`, `"Index"`, `"Billions of Dollars"`, `"Millions of Dollars"`, `"Index 2012=100"`, etc.

**For seasonal_adjustment:**
- `"Seasonally Adjusted"`, `"Not Seasonally Adjusted"`

### order_by

Sort results by:

- **`"search_rank"`** - Relevance to search query
- **`"series_id"`** - Series identifier
- **`"title"`** - Series title
- **`"units"`** - Data units
- **`"frequency"`** - Data frequency
- **`"seasonal_adjustment"`** - Seasonal adjustment type
- **`"realtime_start"`** - Real-time period start
- **`"realtime_end"`** - Real-time period end
- **`"last_updated"`** - Last update date
- **`"observation_start"`** - First observation date
- **`"observation_end"`** - Last observation date
- **`"popularity"`** - FRED popularity score
- **`"group_popularity"`** - Group popularity score

### tag_names / exclude_tag_names

**Format:** Semicolon-delimited list (`;`)

**Common Tags:**
- `usa` - United States data
- `nsa` - Not Seasonally Adjusted
- `sa` - Seasonally Adjusted
- `monthly`, `quarterly`, `annual` - Frequency tags
- `discontinued` - Discontinued series

**Examples:**
- `"usa;nsa"` - Include series with both "usa" AND "nsa" tags
- `"discontinued;quarterly"` - Exclude series with "discontinued" OR "quarterly"

## Response Format

```json
{
  "tool": "search_fred_series",
  "data": [
    {
      "id": "UNRATE",
      "title": "Unemployment Rate",
      "observation_start": "1948-01-01",
      "observation_end": "2025-09-01",
      "frequency": "Monthly",
      "frequency_short": "M",
      "units": "Percent",
      "units_short": "%",
      "seasonal_adjustment": "Seasonally Adjusted",
      "seasonal_adjustment_short": "SA",
      "last_updated": "2025-10-04 07:45:02-05",
      "popularity": 95,
      "notes": "..."
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "search_text": "unemployment",
    "search_type": "full_text",
    "total_count": 1500,
    "returned_count": 50,
    "limit": 50,
    "offset": 0,
    "paginate": false,
    "filters": {
      "category_id": null,
      "filter_variable": null,
      "filter_value": null,
      "tag_names": null,
      "exclude_tag_names": null,
      "order_by": "popularity",
      "sort_order": "desc"
    },
    "api_info": {
      "url": "https://api.stlouisfed.org/fred/series/search?...",
      "status_code": 200,
      "rate_limit_remaining": "120"
    }
  }
}
```

## Usage Examples

### Example 1: Basic Search
```python
search_fred_series("unemployment rate")
```

### Example 2: Filter by Frequency
```python
search_fred_series(
    search_text="GDP",
    filter_variable="frequency",
    filter_value="Quarterly",
    limit=10
)
```

### Example 3: Filter by Tags
```python
search_fred_series(
    search_text="inflation",
    tag_names="usa;nsa",  # Semicolon-delimited
    order_by="last_updated"
)
```

### Example 4: Exclude Tags
```python
search_fred_series(
    search_text="employment",
    exclude_tag_names="discontinued",
    limit=20
)
```

### Example 5: Search by Series ID Pattern
```python
search_fred_series(
    search_text="UN*",  # All series starting with "UN"
    search_type="series_id",
    limit=15
)
```

### Example 6: Combined Filters
```python
search_fred_series(
    search_text="price index",
    filter_variable="frequency",
    filter_value="Monthly",
    tag_names="usa;sa",
    exclude_tag_names="discontinued",
    order_by="popularity",
    limit=25
)
```

### Example 7: Pagination
```python
# Get all results (may take longer)
search_fred_series(
    search_text="interest rate",
    limit=100,
    paginate=True
)

# Manual pagination
search_fred_series(
    search_text="interest rate",
    limit=50,
    offset=0  # First page
)

search_fred_series(
    search_text="interest rate",
    limit=50,
    offset=50  # Second page
)
```

### Example 8: Category Filter
```python
search_fred_series(
    search_text="employment",
    category_id=32991,  # Employment & Unemployment category
    limit=20
)
```

### Example 9: Real-time Window
```python
search_fred_series(
    search_text="GDP",
    realtime_start="2020-01-01",
    realtime_end="2023-12-31",
    limit=10
)
```

## Common Use Cases

### Find Series by Topic
```python
search_fred_series("housing prices")
search_fred_series("consumer confidence")
search_fred_series("industrial production")
```

### Find Monthly Economic Indicators
```python
search_fred_series(
    search_text="economic indicators",
    filter_variable="frequency",
    filter_value="Monthly",
    tag_names="usa;sa"
)
```

### Find Recent Updates
```python
search_fred_series(
    search_text="labor market",
    order_by="last_updated",
    sort_order="desc",
    limit=20
)
```

### Find Popular Series
```python
search_fred_series(
    search_text="economy",
    order_by="popularity",
    sort_order="desc",
    limit=10
)
```

## Tips

1. **Use Full-Text Search First**: Start with general terms to discover available series
2. **Refine with Filters**: Add frequency, units, or tag filters to narrow results
3. **Check Popularity**: Popular series are often more reliable and well-maintained
4. **Mind the Semicolons**: Tags use `;` not `,` as delimiters
5. **Pagination**: Use `paginate=True` for comprehensive results, or manual pagination for control
6. **Wildcard Searches**: Use `*` in series_id searches for pattern matching

## Error Handling

The tool returns JSON error responses with this structure:

```json
{
  "error": "Error message here",
  "search_text": "your search query",
  "tool": "search_fred_series",
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z"
  }
}
```

Common errors:
- Invalid filter_variable value
- Invalid order_by value
- Invalid date format
- API timeout or connectivity issues
- Rate limit exceeded

## Related Tools

- **`fetch_fred_series`**: Fetch historical data for a specific series ID
- FRED API Documentation: https://fred.stlouisfed.org/docs/api/

---

**Last Updated**: 2025-11-01 (v0.1.1)
