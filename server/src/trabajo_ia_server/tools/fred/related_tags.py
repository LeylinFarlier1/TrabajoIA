"""
FRED Related Tags Tool.

Get tags related to one or more FRED tags for discovering associated economic data categories.
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

# FRED API endpoint for related tags
FRED_RELATED_TAGS_URL = "https://api.stlouisfed.org/fred/related_tags"


def search_fred_related_tags(
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

    This tool helps discover related economic data categories by finding tags
    that frequently appear together with the specified tags. Useful for exploring
    FRED's data taxonomy and finding associated economic indicators.

    Args:
        tag_names: Semicolon-delimited list of tag names to find related tags for.
                  Example: "monetary aggregates;weekly" or "usa;gnp"
        exclude_tag_names: Optional semicolon-delimited list of tag names to exclude
                          from results. Example: "discontinued;annual"
        tag_group_id: Filter results to tags in specific group:
                     - freq: Frequency tags (monthly, quarterly, etc.)
                     - gen: General/concept tags (gdp, employment, etc.)
                     - geo: Geography tags (usa, canada, etc.)
                     - geot: Geography type tags (nation, state, etc.)
                     - rls: Release tags
                     - seas: Seasonal adjustment tags (sa, nsa)
                     - src: Source tags (bls, bea, etc.)
        search_text: Optional keywords to filter related tags by name or description.
        limit: Maximum number of tags to return (1-1000). Default: 50.
        offset: Starting offset for pagination. Default: 0.
        order_by: Sort field. Options: series_count, popularity, created, name, group_id.
                 Default: series_count.
        sort_order: Sort direction - "asc" or "desc". Default: asc.
        realtime_start: Optional start date for real-time period (YYYY-MM-DD).
                       Defaults to today's date if not specified.
        realtime_end: Optional end date for real-time period (YYYY-MM-DD).
                     Defaults to today's date if not specified.

    Returns:
        JSON string with related tags data and metadata.

    Response Format:
        {
            "tool": "search_fred_related_tags",
            "data": [
                {
                    "name": "tag_name",
                    "group_id": "group",
                    "notes": "Description",
                    "created": "2012-02-27 10:18:19-06",
                    "popularity": 85,
                    "series_count": 12345
                },
                ...
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "input_tags": ["tag1", "tag2"],
                "excluded_tags": ["tag3"],
                "tag_group_id": "freq",
                "search_text": "keyword",
                "total_count": 100,
                "returned_count": 50,
                "limit": 50,
                "offset": 0,
                "order_by": "series_count",
                "sort_order": "asc",
                "realtime_start": "2025-11-01",
                "realtime_end": "2025-11-01"
            }
        }

    Examples:
        # Find tags related to monetary aggregates
        search_fred_related_tags("monetary aggregates")

        # Find frequency tags related to GDP
        search_fred_related_tags("gdp", tag_group_id="freq")

        # Find related tags excluding discontinued series
        search_fred_related_tags("usa;employment", exclude_tag_names="discontinued")

        # Search for inflation-related tags associated with BLS data
        search_fred_related_tags("bls", search_text="inflation", limit=20)
    """
    try:
        api_key = config.get_fred_api_key()

        # Validate and clamp limit
        limit = max(1, min(limit, 1000))

        # Build request parameters
        params = {
            "api_key": api_key,
            "tag_names": tag_names,
            "file_type": "json",
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        # Add optional parameters
        if exclude_tag_names:
            params["exclude_tag_names"] = exclude_tag_names
        if tag_group_id:
            params["tag_group_id"] = tag_group_id
        if search_text:
            params["search_text"] = search_text
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        logger.info(
            f"Fetching related tags for: '{tag_names}' "
            f"(group={tag_group_id}, search='{search_text}')"
        )

        # Make API request with caching
        ttl = config.get_cache_ttl("search_fred_related_tags", fallback=1800)
        response: FredAPIResponse = fred_client.get_json(
            FRED_RELATED_TAGS_URL,
            params,
            namespace="search_fred_related_tags",
            ttl=ttl,
        )
        json_data = response.json()

        # Extract tags data
        tags = json_data.get("tags", [])

        # Build response
        output = {
            "tool": "search_fred_related_tags",
            "data": tags,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "input_tags": tag_names.split(";"),
                "excluded_tags": exclude_tag_names.split(";") if exclude_tag_names else None,
                "tag_group_id": tag_group_id,
                "search_text": search_text,
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

        logger.info(f"Found {len(tags)} related tags")

        # Return compact JSON (AI-optimized)
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
        return json.dumps({
            "tool": "search_fred_related_tags",
            "error": error_msg,
            "input_tags": tag_names.split(";"),
        }, separators=(",", ":"))

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "search_fred_related_tags",
            "error": error_msg,
            "input_tags": tag_names.split(";") if tag_names else [],
        }, separators=(",", ":"))
