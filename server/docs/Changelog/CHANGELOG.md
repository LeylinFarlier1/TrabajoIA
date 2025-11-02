# Changelog

All notable changes to Trabajo IA MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.9] - 2025-11-02

### Added - Cache, Telemetry, and Resilience Enhancements

- **Unified Cache Layer** with pluggable backends (in-memory, DiskCache, Redis) and per-namespace TTLs to keep the hottest FRED
  queries below 400 ms while respecting freshness requirements.
- **Coordinated Rate Limiter** that centralizes retry penalties and protects the shared FRED quota when bursts or 429 responses
  occur.
- **Structured Logging & Metrics** featuring JSON log output, request context helpers, and an in-process Prometheus-style
  registry that tracks cache hits, retries, latency, and limiter activity.
- **`system_health` MCP Tool** exposing cache configuration, limiter state, and the most recent telemetry snapshot for
  automation hooks and dashboards.

### Changed

- All FRED tools now delegate to the shared `FredClient`, ensuring consistent headers, retry handling, and cache metadata in
  responses.
- Configuration bootstrapping no longer depends on a vendored dotenv shim; runtime and tests share a lightweight inline
  fallback for optional dependency gaps.

### Fixed

- Hardened JSON parsing and error surfaces across the shared client so upstream API failures generate structured responses
  without leaking transport exceptions to MCP callers.

---

## [0.1.8] - 2025-11-01

### Added - Three Category Discovery Tools for Enhanced Data Navigation

**New Tools for Category-Based Data Discovery**

This release adds three powerful tools for exploring and discovering FRED data through the category and tag system, enabling progressive data discovery and precise tag-based filtering.

**1. New Tool: `get_fred_category_related`**

Get related categories for a specific FRED category. Discovers cross-references and semantic links between different parts of FRED's category taxonomy.

**Key Features:**
- **Cross-Hierarchy Links**: Connect categories across different organizational structures
- **Semantic Relationships**: Discover thematic connections beyond parent-child
- **Regional Mappings**: Link regional data across different taxonomies
- **Fast Queries**: Typical response time < 0.5s
- **One-way Relations**: Curated manual relationships by FRED

**Use Cases:**
- Navigate between Federal Reserve District and State hierarchies
- Find alternative organizational paths to related data
- Discover state-level categories from district categories

**Example:**
```python
# Get related categories for St. Louis Fed District
get_fred_category_related(32073)
# Returns: Arkansas, Illinois, Indiana, Kentucky, Mississippi, Missouri, Tennessee
```

**2. New Tool: `get_fred_category_tags`**

Get FRED tags for a specific category with optional filtering. Discover what tags are associated with series in a category to understand data characteristics.

**Key Features:**
- **Tag Discovery**: Find what tags are used by series in a category
- **Type Filtering**: Filter by tag group (frequency, geography, source, etc.)
- **Search**: Find tags containing specific words
- **7 Tag Groups**: freq, gen, geo, geot, rls, seas, src
- **Sorting Options**: Order by series count, popularity, name, etc.
- **Pagination**: Support for large result sets (up to 1000 tags)
- **AI-Optimized**: Compact JSON format, fast responses

**Use Cases:**
- Discover data characteristics before fetching series
- Find available frequencies for series in a category
- Identify sources that provide data in a category
- Build effective tag-based searches
- Understand data organization within categories

**Examples:**
```python
# Get all tags for Trade Balance category
get_fred_category_tags(125)

# Get only frequency tags
get_fred_category_tags(125, tag_group_id="freq")
# Returns: quarterly, annual, monthly

# Search for specific tags
get_fred_category_tags(125, search_text="balance")

# Get top 50 by popularity
get_fred_category_tags(125, limit=50, order_by="popularity")
```

**3. New Tool: `get_fred_category_related_tags`**

Get related FRED tags for one or more tags within a category. The most powerful tool for tag-based discovery - find what other tags co-occur with a given set of tags.

**Key Features:**
- **Tag Co-occurrence Discovery**: Find what tags appear together on series
- **Progressive Discovery**: Start with known tags, find related ones
- **AND/NOT Logic**: Required tags (AND) + excluded tags (NOT)
- **Result Filtering**: Filter by tag type, search text
- **7 Tag Groups**: freq, gen, geo, geot, rls, seas, src
- **Sorting & Pagination**: Order by series count, popularity, etc.
- **Complex Queries**: Combine multiple filters for precise discovery

**Logic:**
- `tag_names` = AND logic (must have ALL specified tags)
- `exclude_tag_names` = NOT logic (must have NONE of specified tags)
- Result: Tags assigned to series matching the criteria

**Use Cases:**
- Progressive tag discovery (start broad, narrow down)
- Find available frequencies for series with specific concept tags
- Identify sources that provide data with certain tags
- Build multi-tag queries progressively
- Refine searches by excluding unwanted tags

**Examples:**
```python
# Find tags related to "services" AND "quarterly"
get_fred_category_related_tags(125, "services;quarterly")
# Returns: balance, bea, nation, usa, goods, nsa, sa

# Exclude unwanted tags
get_fred_category_related_tags(
    125,
    "services;quarterly",
    exclude_tag_names="goods;sa"
)
# Returns: Tags for services+quarterly but NOT goods and NOT sa

# Find available frequencies for "services" data
get_fred_category_related_tags(125, "services", tag_group_id="freq")
# Returns: quarterly, annual, monthly

# Find data sources for specific combination
get_fred_category_related_tags(
    125,
    "quarterly;nsa",
    tag_group_id="src"
)
# Returns: bea, census
```

**Performance:**
- **Response Time**: 0.2-0.6s typical
- **Retry Logic**: 3 attempts with exponential backoff (1-5s)
- **Default Limit**: 1000 tags (category_tags, category_related_tags)
- **JSON Format**: Compact, AI-optimized separators

**Files Added:**
- `src/trabajo_ia_server/tools/fred/category_related.py`
- `src/trabajo_ia_server/tools/fred/category_tags.py`
- `src/trabajo_ia_server/tools/fred/category_related_tags.py`
- `docs/api/FRED_CATEGORY_RELATED_REFERENCE.MD`
- `docs/api/FRED_CATEGORY_TAGS_REFERENCE.MD`
- `docs/api/FRED_CATEGORY_RELATED_TAGS_REFERENCE.MD`

**Files Modified:**
- `src/trabajo_ia_server/server.py` - Added 3 new MCP tool registrations
- `src/trabajo_ia_server/tools/fred/__init__.py` - Added 3 new exports
- Version files updated to 0.1.8

**Total Tools in v0.1.8:** 14 FRED tools
- Category tools: 5 (get, children, related, series, tags, related_tags)
- Series tools: 4 (search, observations, tags, by_tags)
- Tag tools: 5 (get_tags, related_tags, search_series_tags, search_series_related_tags, category_related_tags)

## [0.1.7] - 2025-11-01

### Added - FRED Series Observations Tool and Category Navigation Tools

This release adds four essential tools: one for retrieving actual time-series data and three for navigating FRED's category hierarchy.

**Tool 1: `get_fred_series_observations`**

Get observations or data values for an economic data series. This is the primary tool for retrieving actual historical time-series data from FRED, completing the core functionality needed for comprehensive economic data analysis.

**Key Features:**
- **Complete Historical Data**: Access all available observations for any FRED series (up to 100,000 per request)
- **Date Range Filtering**: Specify exact observation_start and observation_end dates
- **9 Data Transformations**: Apply transformations including percent change, year-over-year, log, and more
- **Frequency Aggregation**: Convert high-frequency data to lower frequencies (daily→monthly, weekly→quarterly, etc.)
- **3 Aggregation Methods**: Average, sum, or end-of-period for frequency conversions
- **Vintage Data Support**: Access historical revisions with 4 output types
- **Real-time Period Queries**: Query data as it existed on specific historical dates
- **Flexible Sorting**: Ascending or descending by observation date
- **AI-Optimized**: Compact JSON format, fast responses (0.4-2.0s typical)
- **Retry Logic**: Automatic retries with exponential backoff (3 attempts, 1-5s)

**Data Transformations Available:**
- `lin`: Levels (no transformation)
- `chg`: Change
- `ch1`: Change from Year Ago
- `pch`: Percent Change
- `pc1`: Percent Change from Year Ago (inflation rate)
- `pca`: Compounded Annual Rate of Change
- `cch`: Continuously Compounded Rate of Change
- `cca`: Continuously Compounded Annual Rate of Change
- `log`: Natural Log

**Frequency Aggregation Options:**
- Daily → Weekly, Biweekly, Monthly, Quarterly, Semiannual, Annual
- Weekly → Monthly, Quarterly, Semiannual, Annual
- Monthly → Quarterly, Semiannual, Annual
- Quarterly → Semiannual, Annual
- Multiple weekly/biweekly end-day variants (Friday, Monday, Wednesday, etc.)

**Use Cases:**
1. **Time-Series Analysis**: Retrieve complete historical data for econometric modeling
2. **Dashboard Data Feeds**: Get recent observations for real-time economic dashboards
3. **Growth Rate Calculation**: Apply year-over-year transformations for inflation, GDP growth, etc.
4. **Frequency Conversion**: Aggregate daily rates to monthly averages automatically
5. **Historical Research**: Access vintage data to study data revisions over time
6. **Comparative Analysis**: Get multiple series with consistent date ranges

**Examples:**
```python
# Get all GDP observations
get_fred_series_observations("GDP")

# Get unemployment rate for 2020-2023
get_fred_series_observations(
    "UNRATE",
    observation_start="2020-01-01",
    observation_end="2023-12-31"
)

# Get inflation rate (year-over-year CPI change)
get_fred_series_observations("CPIAUCSL", units="pc1")

# Convert daily Fed Funds Rate to monthly average
get_fred_series_observations(
    "DFF",
    frequency="m",
    aggregation_method="avg"
)

# Get most recent 12 observations, newest first
get_fred_series_observations(
    "GDP",
    limit=12,
    sort_order="desc"
)

# Get GDP growth rate (percent change)
get_fred_series_observations(
    "GDP",
    units="pch",
    observation_start="2020-01-01"
)
```

**Response Example:**
```json
{
  "tool": "get_series_observations",
  "data": [
    {
      "realtime_start": "2013-08-14",
      "realtime_end": "2013-08-14",
      "date": "1929-01-01",
      "value": "1065.9"
    },
    {
      "realtime_start": "2013-08-14",
      "realtime_end": "2013-08-14",
      "date": "1930-01-01",
      "value": "975.5"
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "series_id": "GNPCA",
    "observation_start": "1776-07-04",
    "observation_end": "9999-12-31",
    "units": "lin",
    "frequency": null,
    "total_count": 84,
    "returned_count": 84
  }
}
```

**Performance:**
- Response time: 0.4-2.0s typical
- Large datasets (10,000+ obs): 1.0-3.0s
- With transformations: +0.2-0.5s
- With aggregation: +0.3-0.7s
- Compact JSON format (token-efficient)
- Fast retry mechanism
- Graceful rate limit handling

**Integration:**
- Complements `search_fred_series` (find series, then get data)
- Works with `get_fred_series_tags` (verify series metadata first)
- Integrates with `get_fred_series_by_tags` (discover series, then retrieve observations)
- Essential final step in data retrieval workflow

**Files Added:**
- `src/trabajo_ia_server/tools/fred/observations.py` - Tool implementation (331 lines)
- `docs/api/FRED_OBSERVATIONS_REFERENCE.MD` - Complete API reference (1,200+ lines)

**Files Modified:**
- `src/trabajo_ia_server/server.py` - Registered new MCP tool
- `src/trabajo_ia_server/tools/fred/__init__.py` - Exported new function
- `src/trabajo_ia_server/config.py` - Version bump to 0.1.7
- `src/trabajo_ia_server/__init__.py` - Version bump to 0.1.7
- `pyproject.toml` - Version bump to 0.1.7

**API Endpoint:** `https://api.stlouisfed.org/fred/series/observations`

**Test Results:**
- ✅ Basic usage (GDP observations): 1.45s, 16 observations retrieved
- ✅ Year-over-year transformation (CPI inflation): 0.92s, correct rates calculated
- ✅ Recent data with descending sort (UNRATE): 0.42s, proper ordering
- ✅ Error handling (invalid series): Proper error message returned

**Documentation:** Complete API reference with 7 usage examples, 5 detailed use cases, transformation formulas, frequency aggregation guide, error handling, performance tips, and best practices.

**Tool 2: `get_fred_category`**

Get information about a specific FRED category. Retrieves metadata including category name, parent category ID, and optional descriptive notes.

**Key Features:**
- **Category Metadata**: Get name, parent_id, and notes for any category
- **Hierarchy Navigation**: Understand category position in FRED's taxonomy
- **Fast Queries**: Typical response time < 0.5s
- **Retry Logic**: Automatic retries with exponential backoff (3 attempts, 1-5s)

**Use Cases:**
- Retrieve category details before browsing child categories
- Understand category hierarchy position
- Get human-readable category information
- Navigate upward in category tree

**Example:**
```python
# Get Trade Balance category info
get_fred_category(125)
# Returns: {"id": 125, "name": "Trade Balance", "parent_id": 13}

# Get root category
get_fred_category(0)
# Returns: {"id": 0, "name": "Categories", "parent_id": null}
```

**Tool 3: `get_fred_category_children`**

Get the child categories for a specified parent category. Enables top-down exploration of FRED's hierarchical category taxonomy.

**Key Features:**
- **Direct Children**: Get all immediate child categories of a parent
- **Root Exploration**: Use category_id=0 to see top-level categories
- **Real-time Support**: Query historical category structures
- **Complete Metadata**: Returns id, name, and parent_id for each child
- **Fast Queries**: Typical response time < 0.7s

**Use Cases:**
- Navigate category tree from top to bottom
- Discover available subcategories
- Build category navigation interfaces
- Explore FRED's data organization

**Examples:**
```python
# Get top-level categories (root children)
get_fred_category_children(0)
# Returns: Production & Business Activity, Money Banking & Finance, etc.

# Get subcategories of International Data
get_fred_category_children(13)
# Returns: Trade Balance, Exchange Rates, International Finance, etc.

# Get historical category structure
get_fred_category_children(
    13,
    realtime_start="2020-01-01",
    realtime_end="2020-12-31"
)
```

**Tool 4: `get_fred_category_series`**

Get the series in a specific category. Retrieves all economic data series that belong to a category with advanced filtering and sorting.

**Key Features:**
- **Series Discovery**: Find all series within a category
- **Advanced Filtering**: Filter by tag_names, realtime dates
- **11 Sort Options**: Sort by series_id, title, frequency, popularity, last_updated, observation dates, etc.
- **Pagination**: Support for large result sets (limit/offset)
- **Complete Metadata**: Full series information including observation ranges, frequency, units, seasonal adjustment
- **AI-Optimized**: Compact JSON, default 1000 limit

**Use Cases:**
- Discover all series in a category
- Find recently updated series in a topic area
- Browse series by popularity
- Get series with specific characteristics within a category
- Build category-based data catalogs

**Examples:**
```python
# Get all series in Trade Balance category
get_fred_category_series(125)

# Get top 20 most popular series
get_fred_category_series(
    125,
    order_by="popularity",
    sort_order="desc",
    limit=20
)

# Get recently updated series
get_fred_category_series(
    125,
    order_by="last_updated",
    sort_order="desc",
    limit=10
)

# Filter by tags and sort by frequency
get_fred_category_series(
    125,
    tag_names="usa;quarterly",
    order_by="frequency",
    limit=50
)
```

**Performance:**
- **get_category**: 0.3-0.6s typical
- **get_category_children**: 0.4-0.9s typical
- **get_category_series**: 0.8-2.5s typical (varies with result size)
- Compact JSON format (token-efficient)
- Fast retry mechanism
- Graceful rate limit handling

**Integration:**
All four tools work together for complete data discovery:
1. `get_category` - Get category info
2. `get_category_children` - Explore subcategories
3. `get_category_series` - Find series in category
4. `get_series_observations` - Retrieve actual data

**Files Added:**
- `src/trabajo_ia_server/tools/fred/observations.py` - Observations tool (331 lines)
- `src/trabajo_ia_server/tools/fred/category.py` - Category info tool (185 lines)
- `src/trabajo_ia_server/tools/fred/category_children.py` - Category children tool (198 lines)
- `src/trabajo_ia_server/tools/fred/category_series.py` - Category series tool (307 lines)
- `docs/api/FRED_OBSERVATIONS_REFERENCE.MD` - Complete observations API reference
- `docs/api/FRED_CATEGORY_REFERENCE.MD` - Complete category API reference
- `docs/api/FRED_CATEGORY_CHILDREN_REFERENCE.MD` - Complete category children API reference

**Files Modified:**
- `src/trabajo_ia_server/server.py` - Registered 4 new MCP tools
- `src/trabajo_ia_server/tools/fred/__init__.py` - Exported 4 new functions
- `src/trabajo_ia_server/config.py` - Version bump to 0.1.7
- `src/trabajo_ia_server/__init__.py` - Version bump to 0.1.7
- `pyproject.toml` - Version bump to 0.1.7

**API Endpoints:**
- `https://api.stlouisfed.org/fred/series/observations`
- `https://api.stlouisfed.org/fred/category`
- `https://api.stlouisfed.org/fred/category/children`
- `https://api.stlouisfed.org/fred/category/series`

**Total Tools in v0.1.7:** 11 FRED tools
- Category tools: 2 (get, children, series)
- Series tools: 4 (search, observations, tags, by_tags)
- Tag tools: 5 (get_tags, related_tags, search_series_tags, search_series_related_tags)

---

## [0.1.6] - 2025-11-01

### Added - FRED Series Tags Tool

**New Tool: `get_fred_series_tags`**

Get all FRED tags associated with a specific series by series ID. This tool enables precise understanding of series categorization and metadata, helping users discover what attributes (frequency, geography, source, seasonal adjustment, etc.) FRED has assigned to any particular series.

**Key Features:**
- **Direct Series Tag Lookup**: Get tags for a specific series by ID
- **Complete Tag Information**: Includes name, group, notes, creation date, popularity, and series count
- **Flexible Sorting**: Order by series_count, popularity, created, name, or group_id
- **Real-time Period Support**: Query historical tag metadata with realtime_start/realtime_end
- **AI-Optimized**: Compact JSON format, fast responses (< 1.5s typical)
- **Retry Logic**: Automatic retries with exponential backoff (3 attempts, 1-5s)

**Use Cases:**
1. **Series Exploration**: Discover what characteristics a series has (frequency, geography, source)
2. **Smart Filtering**: Find tags from known series to search for similar series
3. **Series Validation**: Confirm a series has expected characteristics
4. **Query Building**: Identify tags to use in precise multi-tag queries
5. **Metadata Analysis**: Document or audit series for reporting purposes

**Examples:**
```python
# Get tags for St. Louis Financial Stress Index
get_fred_series_tags("STLFSI")

# Get tags for GDP series
get_fred_series_tags("GDP")

# Get tags for unemployment rate, sorted by popularity
get_fred_series_tags("UNRATE", order_by="popularity", sort_order="desc")

# Get tags for CPI with specific real-time period
get_fred_series_tags(
    "CPIAUCSL",
    realtime_start="2020-01-01",
    realtime_end="2020-12-31"
)
```

**Response Example:**
```json
{
  "tool": "get_series_tags",
  "data": [
    {
      "name": "nation",
      "group_id": "geot",
      "notes": "Country Level",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 105200
    },
    {
      "name": "usa",
      "group_id": "geo",
      "notes": "United States of America",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 393339
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "series_id": "STLFSI",
    "total_count": 8,
    "returned_count": 8
  }
}
```

**Performance:**
- Response time: 0.5-1.5s typical
- Compact JSON format (token-efficient)
- Fast retry mechanism
- Graceful rate limit handling

**Integration:**
- Complements `get_fred_tags` (discover all tags vs. tags for one series)
- Works with `search_fred_series_tags` (tags for search matches vs. tags for specific series)
- Integrates with `get_fred_series_by_tags` (discover tags first, then find series with those tags)

**Files Added:**
- `src/trabajo_ia_server/tools/fred/get_series_tags.py` - Tool implementation (201 lines)
- `docs/api/FRED_SERIESTAGS_REFERENCE.MD` - Complete API reference documentation

**Files Modified:**
- `src/trabajo_ia_server/server.py` - Registered new MCP tool
- `src/trabajo_ia_server/tools/fred/__init__.py` - Exported new function
- `src/trabajo_ia_server/config.py` - Version bump to 0.1.6
- `src/trabajo_ia_server/__init__.py` - Version bump to 0.1.6
- `pyproject.toml` - Version bump to 0.1.6

### Fixed - Test Suite

**Test Updates:**
- Removed obsolete `test_fred_fetch.py` (fetch_series was removed in previous versions)
- Updated `test_fred_search.py` to remove pagination tests (pagination removed in v0.1.2)
- Fixed retry error handling tests to expect `RetryError` instead of `ValueError`
- All 7 tests now pass successfully

**API Endpoint:** `https://api.stlouisfed.org/fred/series/tags`

---

## [0.1.5] - 2025-11-01

### Added - FRED Series Search Related Tags Tool

**New Tool: `search_fred_series_related_tags`**

Get related FRED tags for series matching a search text and tag filter combination. This tool discovers tags that are related to specified tags within the context of series matching a search query, enabling deeper exploration of FRED's data relationships.

**Key Features:**
- **Context-Aware Tag Discovery**: Find related tags within the specific context of series matching your search
- **Dual Filtering**: Combine series search text with existing tag filters for precise discovery
- **Group Filtering**: Focus on specific tag groups (frequency, geography, source, etc.)
- **Exclusion Support**: Remove unwanted tags from results
- **Tag Search**: Additional keyword filtering within related tags
- **Flexible Sorting**: Order by series_count, popularity, creation date, name, or group
- **AI-Optimized**: Default 50 results, compact JSON, fast responses (~1-3s)
- **Retry Logic**: Automatic retries with exponential backoff (3 attempts, 1-5s)

**Use Cases:**
1. **Refine Series Searches**: Discover additional relevant tags to narrow down series searches
2. **Data Exploration**: Explore what other tags are commonly associated with your search context
3. **Taxonomy Navigation**: Understand relationships between tags in specific data domains
4. **Query Building**: Build more precise multi-tag queries by discovering related tags
5. **Frequency Discovery**: Find what data frequencies are available for specific series searches

**Examples:**
```python
# Find related tags for mortgage rate series with specific tags
search_fred_series_related_tags("mortgage rate", "30-year;frb")
# Returns: conventional, discontinued, h15, interest rate, mortgage, etc.

# Find frequency tags for GDP series in USA
search_fred_series_related_tags("GDP", "usa", tag_group_id="freq")
# Returns: annual, quarterly, monthly, daily

# Find related tags for employment data excluding discontinued
search_fred_series_related_tags(
    "employment",
    "monthly;nsa",
    exclude_tag_names="discontinued",
    limit=20
)

# Search for inflation-related tags in CPI context
search_fred_series_related_tags(
    "consumer price",
    "usa;monthly",
    tag_search_text="inflation",
    limit=15
)
```

**Response Example:**
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
    "total_count": 13,
    "returned_count": 13
  }
}
```

**Performance:**
- Response time: 0.5-3s typical (varies with series complexity)
- Compact JSON format (token-efficient)
- Fast retry mechanism
- Graceful rate limit handling

**Integration:**
- Complements `search_fred_series_tags` (discover tags for series vs. related tags)
- Works with `search_fred_related_tags` (context-aware vs. general tag relationships)
- Integrates with `search_fred_series` (refine searches using discovered tags)

**Files Added:**
- `src/trabajo_ia_server/tools/fred/search_series_related_tags.py` - Tool implementation (265 lines)
- `docs/api/FRED_SEARCHSERIESRELATEDTAGS_REFERENCE.MD` - Complete API reference documentation

**Files Modified:**
- `src/trabajo_ia_server/server.py` - Registered new MCP tool
- `src/trabajo_ia_server/tools/fred/__init__.py` - Exported new function
- `src/trabajo_ia_server/config.py` - Version bump to 0.1.5
- `src/trabajo_ia_server/__init__.py` - Version bump to 0.1.5
- `pyproject.toml` - Version bump to 0.1.5

**API Endpoint:** `https://api.stlouisfed.org/fred/series/search/related_tags`

---

## [0.1.4] - 2025-11-01

### Added - FRED Series by Tags Tool

**New Tool: `get_fred_series_by_tags`**

Get FRED series that match ALL specified tags and NONE of the excluded tags. Enables precise, tag-based series filtering with powerful AND/NOT logic.

**Key Features:**
- **AND Logic for Required Tags**: Series must have ALL tags in `tag_names` parameter
- **NOT Logic for Excluded Tags**: Series must have NONE of the tags in `exclude_tag_names` parameter
- **12 Sort Options**: Sort by series_id, title, units, frequency, seasonal_adjustment, popularity, last_updated, observation dates, and more
- **Comprehensive Filtering**: Combine multiple tags to create precise queries (e.g., "usa;monthly;nsa;employment")
- **Exclusion Support**: Filter out discontinued, revised, or unwanted series categories
- **AI-Optimized**: Default 20 results, compact JSON format, fast responses (< 2s target)
- **Rate Limit Protection**: Automatic retries with exponential backoff (3 attempts, 1-5s wait)

**Use Cases:**
1. **Precise Data Discovery**: Find series with exact characteristics (e.g., "monthly USA employment data, not seasonally adjusted")
2. **Tag-Based Filtering**: Use discovered tags from `get_fred_tags` to construct targeted searches
3. **Quality Filtering**: Exclude discontinued or low-quality series
4. **Taxonomy Exploration**: Discover what series exist for specific tag combinations
5. **Multi-Criteria Search**: Combine geography, frequency, concept, and adjustment tags

**Examples:**
```python
# Find monthly USA non-seasonally adjusted series
get_series_by_tags("usa;monthly;nsa")

# Find employment series, excluding discontinued
get_series_by_tags(
    tag_names="employment;usa",
    exclude_tag_names="discontinued",
    limit=10
)

# Find most popular GDP series
get_series_by_tags(
    tag_names="gdp;usa",
    order_by="popularity",
    sort_order="desc"
)

# Find recently updated inflation data
get_series_by_tags(
    tag_names="inflation;usa;monthly",
    exclude_tag_names="discontinued;revision",
    order_by="last_updated",
    sort_order="desc",
    limit=15
)
```

**Response Example:**
```json
{
  "tool": "get_series_by_tags",
  "data": [
    {
      "id": "UNRATE",
      "title": "Unemployment Rate",
      "observation_start": "1948-01-01",
      "observation_end": "2024-12-01",
      "frequency": "Monthly",
      "units": "Percent",
      "seasonal_adjustment": "Seasonally Adjusted",
      "last_updated": "2025-01-03 07:44:03-06",
      "popularity": 85
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T16:30:00Z",
    "required_tags": ["employment", "usa"],
    "excluded_tags": ["discontinued"],
    "total_count": 1247,
    "returned_count": 10,
    "limit": 10,
    "order_by": "popularity",
    "sort_order": "desc"
  }
}
```

**Performance:**
- Response time: 0.5-1.5s typical
- Compact JSON (token-efficient for AI)
- Fast retry mechanism
- Handles rate limits gracefully

**Integration:**
- Perfect complement to `get_fred_tags` (discover tags first, then search by tags)
- Works alongside `search_fred_series` (text search vs. tag-based precision)
- Integrates with `fetch_fred_series` (get series data after finding IDs)

**Parameters:**
- `tag_names` (required): Semicolon-delimited tags (ALL must match)
- `exclude_tag_names` (optional): Semicolon-delimited tags (NONE can match)
- `limit` (optional): Max results (1-1000, default: 20)
- `offset` (optional): Starting offset (default: 0)
- `order_by` (optional): Sort field (default: "series_id")
- `sort_order` (optional): "asc" or "desc" (default: "asc")
- `realtime_start` (optional): Real-time period start (YYYY-MM-DD)
- `realtime_end` (optional): Real-time period end (YYYY-MM-DD)

**Files Added:**
- `src/trabajo_ia_server/tools/fred/series_by_tags.py` (~270 lines) - New tool implementation
- `docs/api/FRED_SERIESBYTAGS_REFERENCE.MD` (~1000 lines) - Comprehensive API reference with 7 examples and 7 use cases

**Files Modified:**
- `src/trabajo_ia_server/server.py` - Registered `get_fred_series_by_tags` MCP tool
- `src/trabajo_ia_server/tools/fred/__init__.py` - Exported `get_series_by_tags` function
- `src/trabajo_ia_server/__init__.py` - Version bump to 0.1.4
- `src/trabajo_ia_server/config.py` - Version bump to 0.1.4
- `pyproject.toml` - Version bump to 0.1.4

**Documentation:**
- Complete API reference documentation with detailed examples
- 7 usage examples covering common scenarios
- 7 use cases with code samples
- Performance benchmarks and optimization tips
- Error handling guide
- Best practices and integration patterns

## [0.1.3] - 2025-11-01

### Added - FRED Tags Discovery Tool

**New Tool: `get_fred_tags`**

Discover available FRED tags to construct better filtered searches.

**Key Features:**
- **Tag Discovery**: Browse all available FRED tags
- **Search by Keyword**: Find tags matching specific terms (e.g., "employment", "inflation")
- **Filter by Group**: 8 tag group types:
  - `freq`: Frequency (monthly, quarterly, annual, etc.)
  - `gen`: General/Concept (gdp, employment, cpi, etc.)
  - `geo`: Geography (usa, canada, japan, etc.)
  - `geot`: Geography Type (nation, state, county, etc.)
  - `rls`: Release
  - `seas`: Seasonal Adjustment (sa, nsa)
  - `src`: Source (bls, bea, census, etc.)
  - `cc`: Citation & Copyright
- **Tag Metadata**: View popularity scores and series counts
- **AI-Optimized**: Default 50 results, compact JSON

**Use Cases:**
1. Discover what tags exist before searching series
2. Find correct tag names for `tag_names` parameter in `search_fred_series`
3. Explore FRED's data organization
4. Learn about available data categories

**Examples:**
```python
# Get top 50 most popular tags
get_fred_tags()

# Search for employment-related tags
get_fred_tags(search_text="employment")

# Get all frequency tags
get_fred_tags(tag_group_id="freq")

# Find geography tags
get_fred_tags(tag_group_id="geo", limit=100)
```

**Response Example:**
```json
{
  "data": [
    {
      "name": "nsa",
      "group_id": "seas",
      "notes": "Not seasonally adjusted",
      "popularity": 96,
      "series_count": 747558
    }
  ],
  "metadata": {
    "total_count": 5000,
    "returned_count": 50
  }
}
```

**Performance:**
- Response time: ~0.5-1s
- Compact JSON (token-efficient)
- Fast retry mechanism (3 attempts, 1-5s wait)

**Integration:**
- Complements `search_fred_series` perfectly
- Use discovered tags in `tag_names` parameter
- Helps users construct more effective searches

**Files Added:**
- `src/trabajo_ia_server/tools/fred/get_tags.py` (new tool implementation)
- Registered in `server.py` as `get_fred_tags` MCP tool
- Exported in `tools/fred/__init__.py`

## [0.1.2] - 2025-11-01

### Changed - Performance Optimization for AI Consumption

**Major Performance Improvements:**
- **Removed pagination** - Single fast request instead of multiple slow pages
- **Reduced default limit** from 50 to 20 results (optimal for LLM consumption)
- **Faster retry mechanism** - 3 attempts with 1-5s wait (was 5 attempts with 4-10s)
- **Compact JSON always** - Saves ~25% tokens for AI processing
- **Reduced logging** - Single INFO log per search instead of per-page

**Breaking Changes:**
- Removed `paginate` parameter from `search_fred_series`
- Removed `max_pages` parameter from `search_fred_series`
- Changed default `limit` from 50 to 20

**Performance Metrics:**
- Search time: ~0.5s (down from 5-30s with pagination)
- Token usage: ~25% reduction for typical searches
- Memory usage: Significantly reduced (no accumulation across pages)

**Rationale:**
This version is specifically optimized for AI/LLM consumption where:
- Large result sets cause token overflow and context issues
- Fast response times are critical for user experience
- Top N most relevant results are usually sufficient
- Pagination added unnecessary latency

**Migration:**
If you need more than 20 results, explicitly set `limit` parameter:
```python
# Before (v0.1.1)
search_fred_series("GDP", paginate=True)  # Could return thousands

# After (v0.1.2)
search_fred_series("GDP", limit=100)  # Get exactly what you need, fast
```

### Technical Details
- Retry decorator: `stop_after_attempt(3)` with `wait_exponential(min=1, max=5)`
- JSON serialization: Always `separators=(",", ":")` (compact)
- HTTP requests: Single request per search call
- Response size: Typically 6,000 tokens vs 8,000+ previously

## [0.1.1] - 2025-11-01

### Added
- **New Tool: `search_fred_series`** - Advanced FRED series search functionality
  - Full-text search across FRED database
  - Series ID exact match search
  - Advanced filtering by:
    - Category ID
    - Metadata variables (frequency, units, etc.)
    - Tags (include/exclude)
    - Real-time data windows
  - Pagination support with automatic multi-page fetching
  - Flexible sorting options (popularity, search rank, title, units, last updated)
  - Comprehensive metadata in responses including:
    - Total counts and pagination info
    - Applied filters
    - API rate limit information
- **Retry mechanism** with exponential backoff for API requests
- **Rate limit handling** with automatic retry and sleep
- **Connection pooling** via requests.Session for better performance

### Changed
- Updated server version to 0.1.1
- Enhanced logging with search operation details
- Improved error messages with more context

### Dependencies
- Added `requests>=2.31.0` - HTTP client for FRED search API
- Added `tenacity>=8.2.0` - Retry mechanism with exponential backoff

### Documentation
- Added comprehensive docstrings for new search tool
- Updated tool descriptions with examples
- Added parameter documentation with type hints

## [0.1.0] - 2025-11-01

### Added
- Initial release of Trabajo IA MCP Server
- **Tool: `fetch_fred_series`** - Fetch historical FRED series observations
  - Support for date range filtering
  - Data validation and cleaning
  - Comprehensive metadata
- **Professional project structure** with src-layout
- **Configuration management** with centralized config.py
- **Logging system** with customizable levels
- **Input validation** for dates and series IDs
- **Comprehensive test suite** with pytest
- **Full documentation**:
  - README with usage examples
  - Architecture documentation
  - Migration guide
  - API references

### Technical Features
- MCP protocol compliance via FastMCP
- Environment-based configuration with .env support
- Type hints throughout codebase
- Modular architecture for easy extension
- UV package manager support

### Dependencies
- `mcp[cli]>=1.20.0` - Model Context Protocol framework
- `fredapi>=0.5.0` - FRED API Python wrapper
- `pandas>=2.0.0` - Data processing
- `python-dotenv>=1.0.0` - Environment management
- `httpx>=0.28.1` - HTTP client

### Development Tools
- pytest for testing
- mypy for type checking
- ruff for linting and formatting
- pytest-cov for coverage reporting

---

## Version Comparison

### v0.1.1 vs v0.1.0

**New Capabilities:**
- Search for series without knowing exact IDs
- Filter results by multiple criteria
- Handle large result sets with pagination
- Automatic retry on transient failures
- Rate limit awareness

**Backwards Compatibility:**
- Fully backward compatible with v0.1.0
- Existing `fetch_fred_series` tool unchanged
- No breaking changes to configuration or API

**Performance Improvements:**
- Connection pooling for better throughput
- Exponential backoff prevents API throttling
- Efficient pagination reduces round trips

---

## Upgrade Guide

### From 0.1.0 to 0.1.1

1. **Update dependencies**:
   ```bash
   cd server
   uv sync
   ```

2. **No configuration changes required** - Existing .env files work as-is

3. **New tool available**:
   ```python
   # Old way - if you knew the series ID
   fetch_fred_series("UNRATE")

   # New way - search for series
   search_fred_series("unemployment rate")
   # Returns list of matching series with IDs
   ```

4. **Restart your MCP server** to enable the new tool

### Testing the New Tool

```bash
# In your MCP client, try:
search_fred_series("inflation")
search_fred_series("GDP", limit=10, filter_variable="frequency", filter_value="Quarterly")
search_fred_series("unemployment", tag_names="nsa,usa")
```

---

## Future Roadmap

### Planned for 0.2.0
- Async HTTP pipeline built on `httpx.AsyncClient`
- Batch operations tool for grouped series fetches
- Circuit breaker integration layered on top of rate limiter
- Metrics exporter for Prometheus/StatsD

### Planned for 0.3.0
- Series comparison helpers and statistical summaries
- Data transformation utilities
- Export to multiple formats (CSV, Parquet, Excel)
- Visualization helpers

### Long-term Goals
- Support for other economic data sources
- Real-time data updates
- Data aggregation and analysis tools
- Interactive data exploration

---

[0.1.1]: https://github.com/trabajo-ia/server/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/trabajo-ia/server/releases/tag/v0.1.0
