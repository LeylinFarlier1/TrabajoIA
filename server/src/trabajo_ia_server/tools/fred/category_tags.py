"""
FRED Category Tags Tool.

Get FRED tags for a specific category with optional filtering.
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

# FRED API endpoint for category tags
FRED_CATEGORY_TAGS_URL = "https://api.stlouisfed.org/fred/category/tags"


def get_category_tags(
    category_id: int,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
    tag_names: Optional[str] = None,
    tag_group_id: Optional[Literal["freq", "gen", "geo", "geot", "rls", "seas", "src"]] = None,
    search_text: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0,
    order_by: Literal["series_count", "popularity", "created", "name", "group_id"] = "series_count",
    sort_order: Literal["asc", "desc"] = "desc",
) -> str:
    """
    Get the FRED tags for a category with optional filtering.

    Series are assigned tags and categories. Indirectly through series, it is possible
    to get the tags for a category. This tool retrieves all tags associated with series
    in the specified category. No tags exist for a category that does not have series.

    Use this tool to discover what tags are used by series in a specific category,
    helping to understand the characteristics of data in that category (frequency,
    geography, source, etc.).

    Args:
        category_id: The ID for a FRED category (required).
                    Example: 125 (Trade Balance), 32991 (Money, Banking, & Finance)
        realtime_start: Start date for real-time period (YYYY-MM-DD, optional).
                       Default: today's date
        realtime_end: End date for real-time period (YYYY-MM-DD, optional).
                     Default: today's date
        tag_names: Semicolon-delimited list of tag names to filter by (optional).
                  Example: "trade;goods" - only include these tags
        tag_group_id: Filter tags by type (optional):
            - "freq": Frequency (monthly, quarterly, annual, etc.)
            - "gen": General/Concept (balance, trade, investment, etc.)
            - "geo": Geography (usa, canada, japan, etc.)
            - "geot": Geography Type (nation, state, county, etc.)
            - "rls": Release
            - "seas": Seasonal Adjustment (sa, nsa)
            - "src": Source (bea, bls, census, etc.)
        search_text: Words to find matching tags with (optional).
        limit: Maximum results to return (1-1000). Default: 1000.
        offset: Starting offset for pagination. Default: 0.
        order_by: Sort field. Options: "series_count", "popularity", "created",
                 "name", "group_id". Default: "series_count".
        sort_order: Sort direction - "asc" or "desc". Default: "desc".

    Returns:
        JSON string with tags array and metadata.

    Response Format:
        {
            "tool": "get_category_tags",
            "data": [
                {
                    "name": "bea",
                    "group_id": "src",
                    "notes": "U.S. Department of Commerce: Bureau of Economic Analysis",
                    "created": "2012-02-27 10:18:19-06",
                    "popularity": 87,
                    "series_count": 24
                },
                ...
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "category_id": 125,
                "count": 21,
                "offset": 0,
                "limit": 1000,
                "order_by": "series_count",
                "sort_order": "desc",
                "realtime_start": "2025-11-01",
                "realtime_end": "2025-11-01"
            }
        }

    Examples:
        # Get all tags for Trade Balance category
        get_category_tags(125)

        # Get only frequency tags
        get_category_tags(125, tag_group_id="freq")

        # Search for specific tags
        get_category_tags(125, search_text="balance")

        # Filter by specific tag names
        get_category_tags(125, tag_names="trade;goods")

        # Get top 50 tags ordered by popularity
        get_category_tags(125, limit=50, order_by="popularity")
    """
    try:
        # 1. Obtain API key
        api_key = config.get_fred_api_key()

        # 2. Validate category_id
        if category_id is None or category_id < 0:
            error_msg = "Invalid category_id: must be a non-negative integer"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_category_tags",
                "error": error_msg,
            }, separators=(",", ":"))

        # 3. Validate and clamp limit
        limit = max(1, min(limit, 1000))

        # 4. Build parameters
        params = {
            "api_key": api_key,
            "category_id": category_id,
            "file_type": "json",
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        # Add optional parameters if provided
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end
        if tag_names:
            params["tag_names"] = tag_names
        if tag_group_id:
            params["tag_group_id"] = tag_group_id
        if search_text:
            params["search_text"] = search_text

        # 5. Log operation
        filters = []
        if tag_group_id:
            filters.append(f"group={tag_group_id}")
        if search_text:
            filters.append(f"search='{search_text}'")
        if tag_names:
            filters.append(f"names={tag_names}")
        filter_str = f" ({', '.join(filters)})" if filters else ""
        
        logger.info(f"Fetching tags for category_id: {category_id}{filter_str}")

        # 6. Make API request with retry and caching
        ttl = config.get_cache_ttl("category_tags", fallback=1800)
        response: FredAPIResponse = fred_client.get_json(
            FRED_CATEGORY_TAGS_URL,
            params,
            namespace="category_tags",
            ttl=ttl,
        )
        json_data = response.json()

        # 7. Extract tags data
        tags = json_data.get("tags", [])
        total_count = json_data.get("count", len(tags))

        # 8. Build structured output
        output = {
            "tool": "get_category_tags",
            "data": tags,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "category_id": category_id,
                "count": total_count,
                "offset": json_data.get("offset", offset),
                "limit": json_data.get("limit", limit),
                "order_by": json_data.get("order_by", order_by),
                "sort_order": json_data.get("sort_order", sort_order),
                "realtime_start": json_data.get("realtime_start"),
                "realtime_end": json_data.get("realtime_end"),
                "cache_hit": response.from_cache,
            },
        }

        # Add filter info to metadata if used
        if tag_group_id:
            output["metadata"]["tag_group_id"] = tag_group_id
        if search_text:
            output["metadata"]["search_text"] = search_text
        if tag_names:
            output["metadata"]["tag_names"] = tag_names

        # 9. Log success
        if tags:
            tag_sample = [tag.get("name", "Unknown") for tag in tags[:3]]
            preview = ", ".join(tag_sample)
            if len(tags) > 3:
                preview += f" and {len(tags) - 3} more"
            logger.info(
                f"Retrieved {len(tags)} tags (of {total_count} total) for category_id={category_id}: {preview}"
            )
        else:
            logger.info(
                f"No tags found for category_id={category_id}{filter_str}"
            )

        # 10. Return compact JSON (AI-optimized)
        return json.dumps(output, separators=(",", ":"), default=str)

    except FredAPIError as e:
        if e.status_code == 404:
            error_msg = f"Category not found or has no series: {category_id}"
        elif e.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
        elif e.status_code == 400 and e.payload:
            detail = e.payload.get("error_message")
            fallback = f"Invalid parameters for category_id: {category_id}"
            error_msg = f"Invalid parameters: {detail}" if detail else fallback
        else:
            error_msg = f"FRED API error: {e.message}"

        logger.error(error_msg)
        return json.dumps({
            "tool": "get_category_tags",
            "error": error_msg,
            "category_id": category_id,
        }, separators=(",", ":"))

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "get_category_tags",
            "error": error_msg,
            "category_id": category_id if category_id is not None else None,
        }, separators=(",", ":"))
