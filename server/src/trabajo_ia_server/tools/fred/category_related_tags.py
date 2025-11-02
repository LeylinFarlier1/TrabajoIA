"""
FRED Category Related Tags Tool.

Get related FRED tags for one or more tags within a category.
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

# FRED API endpoint for category related tags
FRED_CATEGORY_RELATED_TAGS_URL = "https://api.stlouisfed.org/fred/category/related_tags"


def get_category_related_tags(
    category_id: int,
    tag_names: str,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
    exclude_tag_names: Optional[str] = None,
    tag_group_id: Optional[Literal["freq", "gen", "geo", "geot", "rls", "seas", "src"]] = None,
    search_text: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0,
    order_by: Literal["series_count", "popularity", "created", "name", "group_id"] = "series_count",
    sort_order: Literal["asc", "desc"] = "desc",
) -> str:
    """
    Get related FRED tags for one or more tags within a category.

    This tool finds tags that are related to a given set of tags within a specific
    category. Related tags are those assigned to series that match ALL tags in
    tag_names, match NONE of the tags in exclude_tag_names, and belong to the
    specified category.

    This is powerful for tag-based data discovery: start with known tags and find
    what other tags commonly co-occur on the same series. For example, find what
    frequencies and sources are available for "services" and "quarterly" tagged
    series in the Trade Balance category.

    Args:
        category_id: The ID for a FRED category (required).
                    Example: 125 (Trade Balance), 32991 (Money, Banking, & Finance)
        tag_names: Semicolon-delimited tag names that series must match ALL of (required).
                  Example: "services;quarterly" - find tags for series having BOTH tags
        realtime_start: Start date for real-time period (YYYY-MM-DD, optional).
                       Default: today's date
        realtime_end: End date for real-time period (YYYY-MM-DD, optional).
                     Default: today's date
        exclude_tag_names: Semicolon-delimited tag names that series must match NONE of (optional).
                          Example: "goods;sa" - exclude series with "goods" OR "sa"
        tag_group_id: Filter result tags by type (optional):
            - "freq": Frequency tags (monthly, quarterly, annual, etc.)
            - "gen": General/Concept tags (balance, trade, investment, etc.)
            - "geo": Geography tags (usa, canada, japan, etc.)
            - "geot": Geography Type tags (nation, state, county, etc.)
            - "rls": Release tags
            - "seas": Seasonal Adjustment tags (sa, nsa)
            - "src": Source tags (bea, bls, census, etc.)
        search_text: Words to find matching tags with (optional).
        limit: Maximum results to return (1-1000). Default: 1000.
        offset: Starting offset for pagination. Default: 0.
        order_by: Sort field. Options: "series_count", "popularity", "created",
                 "name", "group_id". Default: "series_count".
        sort_order: Sort direction - "asc" or "desc". Default: "desc".

    Returns:
        JSON string with related tags array and metadata.

    Response Format:
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
                ...
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

    Examples:
        # Find tags related to "services" AND "quarterly" in Trade Balance
        get_category_related_tags(125, "services;quarterly")

        # Exclude "goods" and "sa" tags
        get_category_related_tags(125, "services;quarterly", exclude_tag_names="goods;sa")

        # Get only frequency-related tags
        get_category_related_tags(125, "services", tag_group_id="freq")

        # Search for tags containing "balance"
        get_category_related_tags(125, "quarterly", search_text="balance")

        # Get top 50 tags ordered by popularity
        get_category_related_tags(125, "usa", limit=50, order_by="popularity")
    """
    try:
        # 1. Obtain API key
        api_key = config.get_fred_api_key()

        # 2. Validate required parameters
        if category_id is None or category_id < 0:
            error_msg = "Invalid category_id: must be a non-negative integer"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_category_related_tags",
                "error": error_msg,
            }, separators=(",", ":"))

        if not tag_names or not tag_names.strip():
            error_msg = "tag_names is required and cannot be empty"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_category_related_tags",
                "error": error_msg,
            }, separators=(",", ":"))

        # 3. Validate and clamp limit
        limit = max(1, min(limit, 1000))

        # 4. Build parameters
        params = {
            "api_key": api_key,
            "category_id": category_id,
            "tag_names": tag_names,
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
        if exclude_tag_names:
            params["exclude_tag_names"] = exclude_tag_names
        if tag_group_id:
            params["tag_group_id"] = tag_group_id
        if search_text:
            params["search_text"] = search_text

        # 5. Log operation
        filters = [f"tags={tag_names}"]
        if exclude_tag_names:
            filters.append(f"exclude={exclude_tag_names}")
        if tag_group_id:
            filters.append(f"group={tag_group_id}")
        if search_text:
            filters.append(f"search='{search_text}'")
        filter_str = f" ({', '.join(filters)})"
        
        logger.info(f"Fetching related tags for category_id: {category_id}{filter_str}")

        # 6. Make API request with retry and caching
        ttl = config.get_cache_ttl("category_related_tags", fallback=1800)
        response: FredAPIResponse = fred_client.get_json(
            FRED_CATEGORY_RELATED_TAGS_URL,
            params,
            namespace="category_related_tags",
            ttl=ttl,
        )
        json_data = response.json()

        # 7. Extract tags data
        tags = json_data.get("tags", [])
        total_count = json_data.get("count", len(tags))

        # 8. Build structured output
        output = {
            "tool": "get_category_related_tags",
            "data": tags,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "category_id": category_id,
                "tag_names": tag_names,
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
        if exclude_tag_names:
            output["metadata"]["exclude_tag_names"] = exclude_tag_names
        if tag_group_id:
            output["metadata"]["tag_group_id"] = tag_group_id
        if search_text:
            output["metadata"]["search_text"] = search_text

        # 9. Log success
        if tags:
            tag_sample = [tag.get("name", "Unknown") for tag in tags[:3]]
            preview = ", ".join(tag_sample)
            if len(tags) > 3:
                preview += f" and {len(tags) - 3} more"
            logger.info(
                f"Retrieved {len(tags)} related tags (of {total_count} total) for category_id={category_id}, tag_names={tag_names}: {preview}"
            )
        else:
            logger.info(
                f"No related tags found for category_id={category_id}, tag_names={tag_names}{filter_str}"
            )

        # 10. Return compact JSON (AI-optimized)
        return json.dumps(output, separators=(",", ":"), default=str)

    except FredAPIError as e:
        if e.status_code == 404:
            error_msg = (
                "Category not found, has no series, or tags not found: "
                f"category_id={category_id}, tag_names={tag_names}"
            )
        elif e.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
        elif e.status_code == 400 and e.payload:
            detail = e.payload.get("error_message")
            fallback = (
                f"Invalid parameters. Check category_id ({category_id}) and tag_names ({tag_names})"
            )
            error_msg = f"Invalid parameters: {detail}" if detail else fallback
        else:
            error_msg = f"FRED API error: {e.message}"

        logger.error(error_msg)
        return json.dumps({
            "tool": "get_category_related_tags",
            "error": error_msg,
            "category_id": category_id,
            "tag_names": tag_names if tag_names else None,
        }, separators=(",", ":"))

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "get_category_related_tags",
            "error": error_msg,
            "category_id": category_id if category_id is not None else None,
            "tag_names": tag_names if tag_names else None,
        }, separators=(",", ":"))
