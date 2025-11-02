"""
FRED Series Search Tags Tool.

Get FRED tags for a series search, optionally filtered by tag name, group, or search text.
"""
import json
import logging
from datetime import datetime
from typing import Literal, Optional

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.fred_client import (
    FredAPIError,
    FredAPIResponse,
    fred_client,
)

logger = logging.getLogger(__name__)

# FRED API endpoint for series search tags
FRED_SERIES_SEARCH_TAGS_URL = "https://api.stlouisfed.org/fred/series/search/tags"


def search_series_tags(
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

    This tool discovers what tags are associated with series matching a search query.
    Useful for understanding data taxonomy and refining searches using tag filters.

    Args:
        series_search_text: The words to match against economic data series (required).
                           Example: "monetary service index", "GDP", "unemployment rate"
        tag_names: Semicolon-delimited list of tag names to filter results.
                  Only tags that match will be included. Example: "m1;m2"
        tag_group_id: Filter tags by group type (optional):
            - "freq": Frequency tags (monthly, quarterly, annual, etc.)
            - "gen": General/Concept tags (gdp, employment, cpi, etc.)
            - "geo": Geography tags (usa, canada, japan, etc.)
            - "geot": Geography Type tags (nation, state, county, etc.)
            - "rls": Release tags
            - "seas": Seasonal Adjustment tags (sa, nsa)
            - "src": Source tags (bls, bea, census, etc.)
        tag_search_text: Keywords to find matching tags. Filters tags by name/notes.
        limit: Maximum number of tags to return (1-1000). Default: 50 (AI-optimized).
        offset: Starting offset for pagination. Default: 0.
        order_by: Sort field. Options: series_count, popularity, created, name, group_id.
                 Default: "series_count".
        sort_order: Sort direction - "asc" or "desc". Default: "desc".
        realtime_start: Start date for real-time period (YYYY-MM-DD).
        realtime_end: End date for real-time period (YYYY-MM-DD).

    Returns:
        JSON string with tags data and metadata.

    Response Format:
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

    Examples:
        # Find tags for series matching "monetary service index"
        search_series_tags("monetary service index")

        # Find frequency tags for GDP series
        search_series_tags("GDP", tag_group_id="freq")

        # Find tags with name filter
        search_series_tags("employment", tag_names="usa;monthly")

        # Find tags with search text filter
        search_series_tags("inflation", tag_search_text="consumer price")

        # Complete example with all filters
        search_series_tags(
            "unemployment rate",
            tag_group_id="geo",
            limit=20,
            order_by="popularity",
            sort_order="desc"
        )
    """
    try:
        # 1. Obtain API key
        api_key = config.get_fred_api_key()

        # 2. Validate and clamp limit
        limit = max(1, min(limit, 1000))

        # 3. Build base parameters
        params = {
            "api_key": api_key,
            "series_search_text": series_search_text,
            "file_type": "json",
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        # 4. Add optional parameters
        if tag_names:
            params["tag_names"] = tag_names
        if tag_group_id:
            params["tag_group_id"] = tag_group_id
        if tag_search_text:
            params["tag_search_text"] = tag_search_text
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        # 5. Log operation
        filters = []
        if tag_names:
            filters.append(f"tags={tag_names}")
        if tag_group_id:
            filters.append(f"group={tag_group_id}")
        if tag_search_text:
            filters.append(f"search='{tag_search_text}'")

        filter_str = ", ".join(filters) if filters else "no filters"
        logger.info(
            f"Searching tags for series: '{series_search_text}' ({filter_str})"
        )

        # 6. Make API request with retry and caching
        ttl = config.get_cache_ttl("search_series_tags", fallback=300)
        response: FredAPIResponse = fred_client.get_json(
            FRED_SERIES_SEARCH_TAGS_URL,
            params,
            namespace="search_series_tags",
            ttl=ttl,
        )
        json_data = response.json()

        # 7. Extract tags data
        tags = json_data.get("tags", [])

        # 8. Build structured output
        output = {
            "tool": "search_series_tags",
            "data": tags,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "series_search_text": series_search_text,
                "tag_names": tag_names.split(";") if tag_names else None,
                "tag_group_id": tag_group_id,
                "tag_search_text": tag_search_text,
                "total_count": json_data.get("count", len(tags)),
                "returned_count": len(tags),
                "limit": limit,
                "offset": offset,
                "order_by": order_by,
                "sort_order": sort_order,
                "realtime_start": json_data.get("realtime_start"),
                "realtime_end": json_data.get("realtime_end"),
                "cache_hit": response.from_cache,
            },
        }

        # 9. Log success
        logger.info(f"Found {len(tags)} tags for series search")

        # 10. Return compact JSON (AI-optimized)
        return json.dumps(output, separators=(",", ":"), default=str)

    except FredAPIError as e:
        if e.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
        elif e.status_code == 400 and e.payload:
            detail = e.payload.get("error_message")
            error_msg = f"Invalid parameters: {detail}" if detail else "Invalid parameters provided"
        else:
            error_msg = f"FRED API error: {e.message}"

        logger.error(error_msg)
        return json.dumps(
            {
                "tool": "search_series_tags",
                "error": error_msg,
                "series_search_text": series_search_text,
            },
            separators=(",", ":"),
        )

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps(
            {
                "tool": "search_series_tags",
                "error": error_msg,
                "series_search_text": series_search_text if series_search_text else None,
            },
            separators=(",", ":"),
        )
