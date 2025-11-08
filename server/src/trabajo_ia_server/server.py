"""
Trabajo IA MCP Server - Main server implementation.

FastMCP server providing FRED data access through MCP protocol.
"""
from typing import Optional, Literal
import sys

from mcp.server.fastmcp import FastMCP

from trabajo_ia_server.config import config
from trabajo_ia_server.tools.fred.search_series import search_fred_series
from trabajo_ia_server.tools.fred.get_tags import get_fred_tags
from trabajo_ia_server.tools.fred.related_tags import search_fred_related_tags
from trabajo_ia_server.tools.fred.series_by_tags import get_series_by_tags
from trabajo_ia_server.tools.fred.search_series_tags import search_series_tags
from trabajo_ia_server.tools.fred.search_series_related_tags import search_series_related_tags
from trabajo_ia_server.tools.fred.get_series_tags import get_series_tags
from trabajo_ia_server.tools.fred.observations import get_series_observations
from trabajo_ia_server.tools.fred.category import get_category
from trabajo_ia_server.tools.fred.category_children import get_category_children
from trabajo_ia_server.tools.fred.category_series import get_category_series

# Workflows
from trabajo_ia_server.workflows.analyze_gdp import analyze_gdp_cross_country as analyze_gdp_internal

from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP(config.SERVER_NAME)


@mcp.tool("search_fred_series")
def search_series(
    search_text: str,
    limit: int = 20,
    offset: int = 0,
    search_type: Literal["full_text", "series_id"] = "full_text",
    category_id: Optional[int] = None,
    filter_variable: Optional[str] = None,
    filter_value: Optional[str] = None,
    tag_names: Optional[str] = None,
    exclude_tag_names: Optional[str] = None,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
    order_by: Literal[
        "popularity", "search_rank", "title", "units", "last_updated"
    ] = "popularity",
    sort_order: Literal["asc", "desc"] = "desc"
) -> str:
    """
    Search for FRED economic data series with advanced filters.

    Fast, AI-optimized search - returns top results only (no pagination).
    Designed for LLM consumption with compact JSON and reasonable result limits.

    Args:
        search_text: Search query (e.g., 'unemployment', 'GDP', 'inflation')
        limit: Max results to return (1-1000, default: 20 - optimized for AI)
        offset: Starting offset (default: 0)
        search_type: 'full_text' or 'series_id' (default: 'full_text')
        category_id: Filter by FRED category ID (optional)
        filter_variable: Metadata filter: 'frequency', 'units', or 'seasonal_adjustment' (optional)
        filter_value: Value for filter_variable (e.g., 'Monthly', 'Percent') (optional)
        tag_names: Include series with ALL these tags, semicolon-delimited (e.g., 'usa;nsa') (optional)
        exclude_tag_names: Exclude series with ANY of these tags, semicolon-delimited (optional)
        realtime_start: Real-time window start date YYYY-MM-DD (optional)
        realtime_end: Real-time window end date YYYY-MM-DD (optional)
        order_by: Sort field: 'popularity', 'search_rank', 'title', 'units',
                  'last_updated' (default: 'popularity')
        sort_order: 'asc' or 'desc' (default: 'desc')

    Returns:
        Compact JSON with series list and metadata (optimized for AI token usage)

    Examples:
        >>> search_series("unemployment rate")
        >>> search_series("GDP", limit=10, filter_variable="frequency", filter_value="Quarterly")
        >>> search_series("inflation", tag_names="usa;nsa", order_by="last_updated")
    """
    logger.info(f"Searching FRED series: {search_text}")
    return search_fred_series(
        search_text=search_text,
        limit=limit,
        offset=offset,
        search_type=search_type,
        category_id=category_id,
        filter_variable=filter_variable,
        filter_value=filter_value,
        tag_names=tag_names,
        exclude_tag_names=exclude_tag_names,
        realtime_start=realtime_start,
        realtime_end=realtime_end,
        order_by=order_by,
        sort_order=sort_order
    )


@mcp.tool("get_fred_tags")
def get_tags(
    search_text: Optional[str] = None,
    tag_names: Optional[str] = None,
    tag_group_id: Optional[Literal["freq", "gen", "geo", "geot", "rls", "seas", "src", "cc"]] = None,
    limit: int = 50,
    offset: int = 0,
    order_by: Literal["series_count", "popularity", "created", "name", "group_id"] = "popularity",
    sort_order: Literal["asc", "desc"] = "desc"
) -> str:
    """
    Get FRED tags to discover available tags for filtering series searches.

    This tool helps discover what tags exist in FRED, making it easier to construct
    effective search queries with tag filters. Tags are attributes assigned to series.

    Args:
        search_text: Words to find matching tags (optional)
        tag_names: Semicolon-delimited tag names to filter by (optional)
        tag_group_id: Filter by tag group type (optional):
            - "freq": Frequency tags (monthly, quarterly, annual)
            - "gen": General/Concept tags (gdp, employment, inflation)
            - "geo": Geography tags (usa, canada, japan)
            - "geot": Geography Type (nation, state, county)
            - "rls": Release tags
            - "seas": Seasonal Adjustment (sa, nsa)
            - "src": Source tags (bls, bea, census)
            - "cc": Citation & Copyright
        limit: Max results (1-1000, default: 50 - optimized for AI)
        offset: Starting offset (default: 0)
        order_by: Sort field (default: "popularity")
            - "series_count": Number of series with tag
            - "popularity": FRED popularity score
            - "created": Creation date
            - "name": Alphabetically
            - "group_id": By group
        sort_order: "asc" or "desc" (default: "desc")

    Returns:
        Compact JSON with list of tags and metadata

    Examples:
        >>> get_tags()  # Get top 50 most popular tags
        >>> get_tags(search_text="employment")  # Search employment tags
        >>> get_tags(tag_group_id="freq")  # Get all frequency tags
        >>> get_tags(tag_group_id="geo", limit=100)  # Top 100 geography tags
    """
    logger.info(f"Fetching FRED tags (search='{search_text}', group={tag_group_id})")
    return get_fred_tags(
        search_text=search_text,
        tag_names=tag_names,
        tag_group_id=tag_group_id,
        limit=limit,
        offset=offset,
        order_by=order_by,
        sort_order=sort_order
    )


@mcp.tool("search_fred_related_tags")
def search_related_tags(
    tag_names: str,
    exclude_tag_names: Optional[str] = None,
    tag_group_id: Optional[Literal["freq", "gen", "geo", "geot", "rls", "seas", "src"]] = None,
    search_text: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    order_by: Literal["series_count", "popularity", "created", "name", "group_id"] = "series_count",
    sort_order: Literal["asc", "desc"] = "asc",
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get FRED tags related to one or more specified tags.

    Discover tags that frequently appear together with specified tags. Helps explore
    FRED's taxonomy and find associated economic indicators.

    Args:
        tag_names: REQUIRED. Semicolon-delimited tag names (e.g., "monetary aggregates;weekly")
        exclude_tag_names: Semicolon-delimited tags to exclude (optional)
        tag_group_id: Filter to specific group (optional):
            - "freq": Frequency tags
            - "gen": General/Concept tags
            - "geo": Geography tags
            - "geot": Geography type tags
            - "rls": Release tags
            - "seas": Seasonal adjustment tags
            - "src": Source tags
        search_text: Keywords to filter related tags (optional)
        limit: Max results (1-1000, default: 50)
        offset: Starting offset (default: 0)
        order_by: Sort field (default: "series_count")
        sort_order: "asc" or "desc" (default: "asc")
        realtime_start: Real-time start date YYYY-MM-DD (optional)
        realtime_end: Real-time end date YYYY-MM-DD (optional)

    Returns:
        Compact JSON with related tags list and metadata

    Examples:
        >>> search_related_tags("monetary aggregates")
        >>> search_related_tags("gdp", tag_group_id="freq")
        >>> search_related_tags("usa;employment", exclude_tag_names="discontinued")
    """
    logger.info(f"Fetching related tags for: '{tag_names}' (group={tag_group_id})")
    return search_fred_related_tags(
        tag_names=tag_names,
        exclude_tag_names=exclude_tag_names,
        tag_group_id=tag_group_id,
        search_text=search_text,
        limit=limit,
        offset=offset,
        order_by=order_by,
        sort_order=sort_order,
        realtime_start=realtime_start,
        realtime_end=realtime_end
    )


@mcp.tool("get_fred_series_by_tags")
def get_series_by_tags_tool(
    tag_names: str,
    exclude_tag_names: Optional[str] = None,
    limit: int = 20,
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
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get FRED series matching ALL specified tags and NONE of the excluded tags.

    Perform precise series filtering using FRED's tag system. Returns series that have
    ALL tags listed in tag_names and NONE of the tags in exclude_tag_names.

    Args:
        tag_names: REQUIRED. Semicolon-delimited tag names that series must have ALL of.
                  Example: "slovenia;food;oecd" finds series with all three tags.
        exclude_tag_names: Semicolon-delimited tag names that series must have NONE of.
                          Example: "discontinued;daily" excludes series with either tag (optional).
        limit: Max series to return (1-1000, default: 20 - optimized for AI).
        offset: Starting offset (default: 0).
        order_by: Sort field (default: "series_id").
            - "series_id": By series ID
            - "title": By series title
            - "units": By units of measurement
            - "frequency": By data frequency
            - "seasonal_adjustment": By adjustment type
            - "last_updated": By last update date
            - "observation_start": By first observation date
            - "observation_end": By last observation date
            - "popularity": By popularity score
            - "group_popularity": By group popularity
        sort_order: "asc" or "desc" (default: "asc").
        realtime_start: Real-time start date YYYY-MM-DD (optional).
        realtime_end: Real-time end date YYYY-MM-DD (optional).

    Returns:
        Compact JSON with series list and metadata (optimized for AI token usage).

    Examples:
        >>> get_series_by_tags_tool("slovenia;food;oecd")
        >>> get_series_by_tags_tool("gdp;monthly", exclude_tag_names="discontinued")
        >>> get_series_by_tags_tool("employment;usa;nsa", limit=10, order_by="popularity", sort_order="desc")
    """
    logger.info(f"Fetching series by tags: '{tag_names}' (exclude: '{exclude_tag_names}')")
    return get_series_by_tags(
        tag_names=tag_names,
        exclude_tag_names=exclude_tag_names,
        limit=limit,
        offset=offset,
        order_by=order_by,
        sort_order=sort_order,
        realtime_start=realtime_start,
        realtime_end=realtime_end,
    )


@mcp.tool("search_fred_series_tags")
def search_series_tags_tool(
    series_search_text: str,
    tag_names: Optional[str] = None,
    tag_group_id: Optional[Literal["freq", "gen", "geo", "geot", "rls", "seas", "src"]] = None,
    tag_search_text: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    order_by: Literal["series_count", "popularity", "created", "name", "group_id"] = "series_count",
    sort_order: Literal["asc", "desc"] = "desc",
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get FRED tags for a series search with optional filtering.

    Discover what tags are associated with series matching your search query. Perfect for
    understanding data taxonomy, refining searches, and exploring related indicators.

    Args:
        series_search_text: The words to match against economic data series (REQUIRED).
            Example: "monetary service index", "GDP", "unemployment rate"
        tag_names: Semicolon-delimited list of tag names to filter by (optional).
            Only tags matching these names will be included.
            Example: "m1;m2" filters to only show m1 and m2 tags
        tag_group_id: Filter tags by group type (optional):
            - "freq": Frequency tags (monthly, quarterly, annual)
            - "gen": General/Concept tags (gdp, employment, cpi)
            - "geo": Geography tags (usa, canada, japan)
            - "geot": Geography Type (nation, state, county)
            - "rls": Release tags
            - "seas": Seasonal Adjustment (sa, nsa)
            - "src": Source tags (bls, bea, census)
        tag_search_text: Keywords to find matching tags by name/notes (optional).
        limit: Max tags to return (1-1000, default: 50 - optimized for AI).
        offset: Starting offset for pagination (default: 0).
        order_by: Sort field (default: "series_count").
            - "series_count": Number of series with tag
            - "popularity": FRED popularity score
            - "created": Creation date
            - "name": Alphabetically
            - "group_id": By group
        sort_order: "asc" or "desc" (default: "desc").
        realtime_start: Real-time start date YYYY-MM-DD (optional).
        realtime_end: Real-time end date YYYY-MM-DD (optional).

    Returns:
        Compact JSON with tags list and metadata.

    Examples:
        >>> search_series_tags_tool("monetary service index")
        >>> search_series_tags_tool("GDP", tag_group_id="freq")
        >>> search_series_tags_tool("employment", tag_names="usa;monthly")
        >>> search_series_tags_tool("inflation", tag_search_text="consumer price", limit=20)
    """
    logger.info(f"Searching tags for series: '{series_search_text}' (group={tag_group_id})")
    return search_series_tags(
        series_search_text=series_search_text,
        tag_names=tag_names,
        tag_group_id=tag_group_id,
        tag_search_text=tag_search_text,
        limit=limit,
        offset=offset,
        order_by=order_by,
        sort_order=sort_order,
        realtime_start=realtime_start,
        realtime_end=realtime_end,
    )


@mcp.tool("search_fred_series_related_tags")
def search_series_related_tags_tool(
    series_search_text: str,
    tag_names: str,
    exclude_tag_names: Optional[str] = None,
    tag_group_id: Optional[Literal["freq", "gen", "geo", "geot", "rls", "seas", "src"]] = None,
    tag_search_text: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    order_by: Literal["series_count", "popularity", "created", "name", "group_id"] = "series_count",
    sort_order: Literal["asc", "desc"] = "desc",
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get related FRED tags for series matching a search text and tag filter combination.

    Find tags that are related to specified tags within the context of series matching
    your search query. Perfect for discovering additional relevant tags to refine series
    searches and explore data relationships.

    Args:
        series_search_text: The words to match against economic data series (REQUIRED).
            Example: "mortgage rate", "GDP", "unemployment"
        tag_names: REQUIRED. Semicolon-delimited tag names that series must match.
            Example: "30-year;frb" or "usa;monthly"
        exclude_tag_names: Semicolon-delimited tag names to exclude (optional).
            Example: "discontinued;annual"
        tag_group_id: Filter to specific tag group (optional):
            - "freq": Frequency tags (monthly, quarterly, annual)
            - "gen": General/Concept tags (gdp, employment, inflation)
            - "geo": Geography tags (usa, canada, japan)
            - "geot": Geography Type (nation, state, county)
            - "rls": Release tags
            - "seas": Seasonal Adjustment (sa, nsa)
            - "src": Source tags (bls, bea, census)
        tag_search_text: Keywords to filter related tags (optional).
        limit: Max tags to return (1-1000, default: 50 - optimized for AI).
        offset: Starting offset (default: 0).
        order_by: Sort field (default: "series_count").
            - "series_count": Number of series with tag
            - "popularity": FRED popularity score
            - "created": Creation date
            - "name": Alphabetically
            - "group_id": By group
        sort_order: "asc" or "desc" (default: "desc").
        realtime_start: Real-time start date YYYY-MM-DD (optional).
        realtime_end: Real-time end date YYYY-MM-DD (optional).

    Returns:
        Compact JSON with related tags list and metadata.

    Examples:
        >>> search_series_related_tags_tool("mortgage rate", "30-year;frb")
        >>> search_series_related_tags_tool("GDP", "usa", tag_group_id="freq")
        >>> search_series_related_tags_tool("employment", "monthly;nsa", exclude_tag_names="discontinued")
        >>> search_series_related_tags_tool("consumer price", "usa;monthly", tag_search_text="inflation", limit=20)
    """
    logger.info(
        f"Searching related tags for series: '{series_search_text}' "
        f"with tags '{tag_names}' (group={tag_group_id})"
    )
    return search_series_related_tags(
        series_search_text=series_search_text,
        tag_names=tag_names,
        exclude_tag_names=exclude_tag_names,
        tag_group_id=tag_group_id,
        tag_search_text=tag_search_text,
        limit=limit,
        offset=offset,
        order_by=order_by,
        sort_order=sort_order,
        realtime_start=realtime_start,
        realtime_end=realtime_end,
    )


@mcp.tool("get_fred_series_tags")
def get_series_tags_tool(
    series_id: str,
    order_by: Literal["series_count", "popularity", "created", "name", "group_id"] = "series_count",
    sort_order: Literal["asc", "desc"] = "desc",
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get the FRED tags for a specific series.

    Retrieve all tags associated with a particular FRED series, helping you understand
    the categorization and metadata of the series. Useful for discovering what attributes
    (frequency, geography, source, seasonal adjustment, etc.) are assigned to a series.

    Args:
        series_id: The ID for a FRED series (REQUIRED).
            Example: "STLFSI", "GDP", "UNRATE", "CPIAUCSL"
        order_by: Sort field (default: "series_count").
            - "series_count": Number of series with this tag
            - "popularity": FRED popularity score
            - "created": Tag creation date
            - "name": Alphabetically by tag name
            - "group_id": By tag group
        sort_order: "asc" or "desc" (default: "desc").
        realtime_start: Real-time start date YYYY-MM-DD (optional).
        realtime_end: Real-time end date YYYY-MM-DD (optional).

    Returns:
        Compact JSON with tags list and metadata.

    Examples:
        >>> get_series_tags_tool("STLFSI")
        >>> get_series_tags_tool("GDP")
        >>> get_series_tags_tool("UNRATE", order_by="popularity", sort_order="desc")
        >>> get_series_tags_tool("CPIAUCSL", realtime_start="2020-01-01")
    """
    logger.info(f"Fetching tags for series: '{series_id}'")
    return get_series_tags(
        series_id=series_id,
        order_by=order_by,
        sort_order=sort_order,
        realtime_start=realtime_start,
        realtime_end=realtime_end,
    )


@mcp.tool("get_fred_series_observations")
def get_observations(
    series_id: str,
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
    limit: int = 100000,
    offset: int = 0,
    sort_order: Literal["asc", "desc"] = "asc",
    units: Literal["lin", "chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"] = "lin",
    frequency: Optional[Literal["d", "w", "bw", "m", "q", "sa", "a", "wef", "weth", "wew", "wetu", "wem", "wesu", "wesa", "bwew", "bwem"]] = None,
    aggregation_method: Literal["avg", "sum", "eop"] = "avg",
    output_type: Literal[1, 2, 3, 4] = 1,
) -> str:
    """
    Get observations or data values for an economic data series.

    Retrieves historical time-series data for a specific FRED series with support for
    date range filtering, data transformations, frequency aggregation, and various
    output formats for vintages and real-time data. Essential for obtaining the actual
    economic data values you'll analyze.

    Args:
        series_id: The ID for a FRED series (REQUIRED).
            Example: "GNPCA", "GDP", "UNRATE", "CPIAUCSL", "DFF"
        observation_start: Start date for observations YYYY-MM-DD (optional).
            Default: 1776-07-04 (earliest available)
        observation_end: End date for observations YYYY-MM-DD (optional).
            Default: 9999-12-31 (latest available)
        realtime_start: Real-time period start date YYYY-MM-DD (optional).
            Default: today's date
        realtime_end: Real-time period end date YYYY-MM-DD (optional).
            Default: today's date
        limit: Maximum results (1-100000, default: 100000 - all data).
        offset: Starting offset for pagination (default: 0).
        sort_order: "asc" (oldest first) or "desc" (newest first). Default: "asc".
        units: Data transformation to apply (default: "lin" - no transformation).
            - "lin": Levels (no transformation)
            - "chg": Change
            - "ch1": Change from Year Ago
            - "pch": Percent Change
            - "pc1": Percent Change from Year Ago
            - "pca": Compounded Annual Rate of Change
            - "cch": Continuously Compounded Rate of Change
            - "cca": Continuously Compounded Annual Rate of Change
            - "log": Natural Log
        frequency: Aggregate to lower frequency (optional). Options: 'd', 'w', 'bw',
            'm', 'q', 'sa', 'a', plus weekly variants (wef, weth, etc.)
        aggregation_method: How to aggregate when using frequency (default: "avg").
            - "avg": Average
            - "sum": Sum
            - "eop": End of Period
        output_type: Output format (default: 1).
            - 1: Observations by Real-Time Period
            - 2: Observations by Vintage Date, All
            - 3: Observations by Vintage Date, New and Revised Only
            - 4: Observations, Initial Release Only

    Returns:
        Compact JSON with observations data and comprehensive metadata.

    Examples:
        >>> get_observations("GNPCA")
        >>> get_observations("GDP", observation_start="2020-01-01", observation_end="2023-12-31")
        >>> get_observations("UNRATE", units="pc1")
        >>> get_observations("DFF", frequency="m", aggregation_method="avg")
        >>> get_observations("CPIAUCSL", limit=100, sort_order="desc")
    """
    logger.info(f"Fetching observations for series: '{series_id}'")
    return get_series_observations(
        series_id=series_id,
        observation_start=observation_start,
        observation_end=observation_end,
        realtime_start=realtime_start,
        realtime_end=realtime_end,
        limit=limit,
        offset=offset,
        sort_order=sort_order,
        units=units,
        frequency=frequency,
        aggregation_method=aggregation_method,
        output_type=output_type,
    )


@mcp.tool("get_fred_category")
def get_category_info(category_id: int) -> str:
    """
    Get information about a specific FRED category.

    FRED organizes its economic data series into a hierarchical taxonomy of categories.
    This tool retrieves metadata about a specific category including its name, parent
    category, and optional notes. Essential for navigating the FRED category tree and
    understanding how economic data is organized and classified.

    Categories form a tree structure starting from the root (category_id=0). Each category
    can have child categories and contains data series. Use this tool to explore the
    taxonomy and find related categories.

    Args:
        category_id: The ID for a FRED category (REQUIRED).
            Example values:
            - 0: Root category
            - 32991: Money, Banking, & Finance
            - 32992: National Accounts
            - 125: Trade Balance
            - 32455: Business Cycle Expansions & Contractions
            - 3008: Population, Employment, & Labor Markets

    Returns:
        Compact JSON with category information and metadata.

    Response includes:
        - id: Category ID
        - name: Category name
        - parent_id: Parent category ID (use to navigate up the tree)
        - notes: Optional category description/notes

    Examples:
        >>> get_category_info(0)  # Root category
        >>> get_category_info(125)  # Trade Balance
        >>> get_category_info(32991)  # Money, Banking, & Finance
        >>> get_category_info(32992)  # National Accounts
    """
    logger.info(f"Fetching category information: {category_id}")
    return get_category(category_id=category_id)


@mcp.tool("get_fred_category_children")
def get_children(
    category_id: int = 0,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get the child categories for a specified parent category.

    Retrieves all direct child categories of a given parent category, enabling top-down
    exploration of FRED's hierarchical taxonomy. Essential for discovering sub-categories,
    navigating the category tree, and understanding how FRED organizes economic data.

    Use this tool to explore the category hierarchy starting from any category. Combined
    with get_fred_category, you can navigate both up (to parents) and down (to children)
    through FRED's complete taxonomy tree.

    Args:
        category_id: The ID for a parent category (default: 0 - root category).
            Example values:
            - 0: Root (returns top-level categories like Money/Banking, National Accounts)
            - 13: U.S. Trade & International Transactions
            - 32991: Money, Banking, & Finance
            - 32992: National Accounts
        realtime_start: Real-time period start date YYYY-MM-DD (optional).
            Default: today's date
        realtime_end: Real-time period end date YYYY-MM-DD (optional).
            Default: today's date

    Returns:
        Compact JSON with child categories list and metadata.

    Response includes array of child categories, each with:
        - id: Category ID
        - name: Category name
        - parent_id: Parent category ID (will match input category_id)
        - notes: Optional category description

    Examples:
        >>> get_children(0)  # Get top-level categories
        >>> get_children(13)  # Get children of International Data
        >>> get_children(32991)  # Children of Money, Banking, & Finance
        >>> get_children(125)  # Children of Trade Balance (may be empty)
    """
    logger.info(f"Fetching child categories for parent: {category_id}")
    return get_category_children(
        category_id=category_id,
        realtime_start=realtime_start,
        realtime_end=realtime_end,
    )


@mcp.tool("get_fred_category_series")
def get_series_in_category(
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

    Retrieves all economic data series belonging to a given category with extensive
    filtering, sorting, and pagination options. Essential for discovering available
    data series within a topic area and finding specific series based on attributes
    like frequency, units, seasonal adjustment, or tags.

    This tool is the primary way to find actual data series after navigating the
    category tree. Once you identify a relevant category using get_fred_category or
    get_fred_category_children, use this tool to list all series in that category.

    Args:
        category_id: The ID for a category (REQUIRED).
            Example values:
            - 125: Trade Balance
            - 32991: Money, Banking, & Finance
            - 13: U.S. Trade & International Transactions
            - 22: Interest Rates
        realtime_start: Real-time period start date YYYY-MM-DD (optional).
            Default: today's date
        realtime_end: Real-time period end date YYYY-MM-DD (optional).
            Default: today's date
        limit: Maximum number of results (1-1000, default: 1000).
            Use with offset for pagination through large result sets.
        offset: Result offset for pagination (default: 0).
            Example: offset=1000 retrieves results 1001-2000.
        order_by: Sort field (default: "series_id"). Options:
            - "series_id": By series ID alphabetically
            - "title": By series title
            - "units": By units of measurement
            - "frequency": By data frequency
            - "seasonal_adjustment": By seasonal adjustment type
            - "realtime_start", "realtime_end": By real-time dates
            - "last_updated": By last update date
            - "observation_start", "observation_end": By observation date range
            - "popularity": By FRED popularity score (most useful for finding key series)
            - "group_popularity": By group popularity
        sort_order: "asc" (ascending) or "desc" (descending). Default: "asc".
        filter_variable: Filter by attribute (optional). Options:
            - "frequency": Filter by data frequency (Monthly, Quarterly, etc.)
            - "units": Filter by units (Dollars, Percent, Index, etc.)
            - "seasonal_adjustment": Filter by adjustment type (SA, NSA, SAAR)
        filter_value: Value for filter_variable (required if filter_variable set).
            Example: "Monthly", "Seasonally Adjusted", "Billions of Dollars"
        tag_names: Semicolon-delimited tags - series must have ALL of these (optional).
            Example: "income;bea" finds series with both "income" AND "bea" tags.
        exclude_tag_names: Semicolon-delimited tags - series must have NONE of these (optional).
            Example: "discontinued;annual" excludes series with either tag.
            Requires tag_names to be set.

    Returns:
        Compact JSON with series array and metadata.

    Response includes array of series, each with:
        - id: Series ID
        - title: Series title
        - observation_start, observation_end: Data availability dates
        - frequency: Data frequency (Monthly, Quarterly, Annual, etc.)
        - units: Units of measurement
        - seasonal_adjustment: Seasonal adjustment type
        - last_updated: Last update timestamp
        - popularity: FRED popularity score
        - notes: Optional series description

    Examples:
        >>> get_series_in_category(125)  # All Trade Balance series
        >>> get_series_in_category(125, filter_variable="frequency", filter_value="Monthly")
        >>> get_series_in_category(125, order_by="popularity", sort_order="desc", limit=10)
        >>> get_series_in_category(32991, tag_names="interest;rates")
        >>> get_series_in_category(22, filter_variable="seasonal_adjustment", filter_value="Seasonally Adjusted")
    """
    logger.info(f"Fetching series for category_id: {category_id}")
    return get_category_series(
        category_id=category_id,
        realtime_start=realtime_start,
        realtime_end=realtime_end,
        limit=limit,
        offset=offset,
        order_by=order_by,
        sort_order=sort_order,
        filter_variable=filter_variable,
        filter_value=filter_value,
        tag_names=tag_names,
        exclude_tag_names=exclude_tag_names,
    )


# =============================================================================
# v0.2.0 WORKFLOW TOOLS - Complete End-to-End Analysis
# =============================================================================

# Workflows removed - not needed


def main():
    """
    Main entry point for the MCP server.

    Validates configuration and starts the FastMCP server with stdio transport.
    """
    try:
        # Validate configuration before starting
        config.validate()
        logger.info(f"Starting {config.SERVER_NAME} v{config.SERVER_VERSION}")

        # Run server with stdio transport
        mcp.run(transport='stdio')

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


@mcp.tool("analyze_gdp_cross_country")
def analyze_gdp_cross_country(
    countries: str,
    gdp_variants: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    comparison_mode: str = "absolute",
    base_year: Optional[int] = None,
    include_rankings: bool = True,
    include_convergence: bool = True,
    include_growth_analysis: bool = True,
    detect_structural_breaks: bool = True,
    output_format: str = "analysis",
    frequency: str = "annual",
    fill_missing: str = "interpolate",
    align_method: str = "inner",
    benchmark_against: Optional[str] = None,
    validate_variants: bool = True,
    period_split: Optional[str] = None
) -> str:
    """
    Analyze GDP across countries with deep economic analysis.
    
    MCP tool providing comprehensive GDP cross-country analysis with rankings,
    convergence tests, structural breaks detection, and multiple output formats.
    
    Args:
        countries: Country codes or preset name. Examples:
            - Single country: "usa"
            - Multiple: "usa,canada,mexico" (comma-separated)
            - Preset: "g7", "latam", "brics", "oecd", "emerging", "developed"
        gdp_variants: GDP variants to analyze (comma-separated). Options:
            - "nominal_usd": GDP in current USD
            - "constant_2010": GDP in constant 2010 USD (real growth)
            - "per_capita_constant": GDP per capita, constant prices (most used)
            - "per_capita_ppp": GDP per capita PPP-adjusted
            - "growth_rate": Annual growth rate (computed)
            - "ppp_adjusted": Total GDP PPP-adjusted
            Default: "per_capita_constant"
        start_date: Start date YYYY-MM-DD (default: 1960-01-01)
        end_date: End date YYYY-MM-DD (default: latest available)
        comparison_mode: Analysis mode. Options:
            - "absolute": Actual values in USD
            - "indexed": Normalized to 100 at base_year
            - "growth_rates": Focus on growth rates
            - "ppp": PPP-adjusted comparison
        base_year: Base year for indexed mode (e.g., 2000)
        include_rankings: Include country rankings by variant
        include_convergence: Compute sigma/beta convergence analysis
        include_growth_analysis: CAGR, volatility, stability_index
        detect_structural_breaks: Chow test + rolling variance detection
        output_format: Output type. Options:
            - "analysis": Comprehensive JSON analysis (default)
            - "dataset": Tidy DataFrame as JSON records
            - "summary": Executive summary markdown
            - "both": JSON analysis + dataset combined
        frequency: "annual" (default) or "quarterly"
        fill_missing: Handle missing data: "interpolate", "forward", "drop"
        align_method: Date alignment: "inner" (common dates) or "outer" (all dates)
        benchmark_against: Benchmark country (e.g., "usa") or None
        validate_variants: Validate variant dependencies before fetching
        period_split: Split analysis: "decade", "5y", or None
    
    Returns:
        JSON string with analysis results, metadata, and warnings
    
    Examples:
        >>> analyze_gdp_cross_country("g7", "per_capita_constant")
        >>> analyze_gdp_cross_country("latam", "per_capita_constant,growth_rate", start_date="2000-01-01")
        >>> analyze_gdp_cross_country("usa,china,india", output_format="both")
    """
    logger.info(f"Analyzing GDP: countries={countries}, variants={gdp_variants}")
    
    # Parse comma-separated inputs
    countries_list = [c.strip() for c in countries.split(",")]
    
    variants_list = None
    if gdp_variants:
        variants_list = [v.strip() for v in gdp_variants.split(",")]
    
    # Call internal function
    return analyze_gdp_internal(
        countries=countries_list,
        gdp_variants=variants_list,
        include_population=True,
        start_date=start_date,
        end_date=end_date,
        period_split=period_split,
        comparison_mode=comparison_mode,
        base_year=base_year,
        include_rankings=include_rankings,
        include_convergence=include_convergence,
        include_growth_analysis=include_growth_analysis,
        calculate_productivity=False,
        detect_structural_breaks=detect_structural_breaks,
        output_format=output_format,
        frequency=frequency,
        fill_missing=fill_missing,
        align_method=align_method,
        benchmark_against=benchmark_against,
        validate_variants=validate_variants
    )


if __name__ == "__main__":
    main()
