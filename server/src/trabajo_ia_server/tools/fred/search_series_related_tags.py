"""
FRED Series Search Related Tags Tool.

Get related FRED tags for series matching a search and tag filter combination.
"""
import json
import logging
from datetime import datetime
from typing import Literal, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from trabajo_ia_server.config import config

logger = logging.getLogger(__name__)

# FRED API endpoint for series search related tags
FRED_SERIES_SEARCH_RELATED_TAGS_URL = "https://api.stlouisfed.org/fred/series/search/related_tags"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
def _request_with_retries(url: str, params: dict) -> requests.Response:
    """Make HTTP request with retry logic for transient failures."""
    session = requests.Session()
    try:
        response = session.get(url, params=params, timeout=30)

        if response.status_code == 429:
            logger.warning("Rate limit hit, retrying...")
            raise requests.exceptions.RequestException("Rate limit exceeded")

        response.raise_for_status()
        return response
    finally:
        session.close()


def search_series_related_tags(
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

    This tool finds tags that are related to specified tags within the context of series
    matching a search query. Useful for discovering additional relevant tags to refine
    series searches and explore data relationships.

    Args:
        series_search_text: The words to match against economic data series (required).
                           Example: "mortgage rate", "GDP", "unemployment"
        tag_names: Semicolon-delimited list of tag names that series must match (required).
                  Example: "30-year;frb" or "usa;monthly"
        exclude_tag_names: Semicolon-delimited list of tag names to exclude from results.
                          Example: "discontinued;annual"
        tag_group_id: Filter results to tags in specific group (optional):
                     - "freq": Frequency tags (monthly, quarterly, annual, etc.)
                     - "gen": General/concept tags (gdp, employment, inflation, etc.)
                     - "geo": Geography tags (usa, canada, japan, etc.)
                     - "geot": Geography type tags (nation, state, county, msa)
                     - "rls": Release tags
                     - "seas": Seasonal adjustment tags (sa, nsa)
                     - "src": Source tags (bls, bea, census, fed, etc.)
        tag_search_text: Keywords to find matching tags. Filters tags by name/description.
        limit: Maximum number of tags to return (1-1000). Default: 50 (AI-optimized).
        offset: Starting offset for pagination. Default: 0.
        order_by: Sort field. Options: series_count, popularity, created, name, group_id.
                 Default: "series_count".
        sort_order: Sort direction - "asc" or "desc". Default: "desc".
        realtime_start: Start date for real-time period (YYYY-MM-DD).
        realtime_end: End date for real-time period (YYYY-MM-DD).

    Returns:
        JSON string with related tags data and metadata.

    Response Format:
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
                }
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "series_search_text": "mortgage rate",
                "input_tags": ["30-year", "frb"],
                "excluded_tags": null,
                "tag_group_id": null,
                "tag_search_text": null,
                "total_count": 10,
                "returned_count": 10,
                "limit": 50,
                "offset": 0,
                "order_by": "series_count",
                "sort_order": "desc",
                "realtime_start": "2025-11-01",
                "realtime_end": "2025-11-01"
            }
        }

    Examples:
        # Find related tags for mortgage rate series with specific tags
        search_series_related_tags("mortgage rate", "30-year;frb")

        # Find frequency tags for GDP series tagged as USA
        search_series_related_tags("GDP", "usa", tag_group_id="freq")

        # Find related tags excluding discontinued series
        search_series_related_tags(
            "employment",
            "monthly;nsa",
            exclude_tag_names="discontinued"
        )

        # Search for inflation-related tags in CPI series
        search_series_related_tags(
            "consumer price",
            "usa;monthly",
            tag_search_text="inflation",
            limit=20
        )

        # Complete example with all filters
        search_series_related_tags(
            series_search_text="unemployment rate",
            tag_names="usa;monthly",
            tag_group_id="geo",
            order_by="popularity",
            sort_order="desc",
            limit=30
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
            "tag_names": tag_names,
            "file_type": "json",
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        # 4. Add optional parameters
        if exclude_tag_names:
            params["exclude_tag_names"] = exclude_tag_names
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
        if exclude_tag_names:
            filters.append(f"exclude={exclude_tag_names}")
        if tag_group_id:
            filters.append(f"group={tag_group_id}")
        if tag_search_text:
            filters.append(f"search='{tag_search_text}'")

        filter_str = ", ".join(filters) if filters else "no additional filters"
        logger.info(
            f"Searching related tags for series: '{series_search_text}' "
            f"with tags '{tag_names}' ({filter_str})"
        )

        # 6. Make API request with retry
        response = _request_with_retries(FRED_SERIES_SEARCH_RELATED_TAGS_URL, params)
        json_data = response.json()

        # 7. Extract tags data
        tags = json_data.get("tags", [])

        # 8. Build structured output
        output = {
            "tool": "search_series_related_tags",
            "data": tags,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "series_search_text": series_search_text,
                "input_tags": tag_names.split(";"),
                "excluded_tags": exclude_tag_names.split(";") if exclude_tag_names else None,
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
            },
        }

        # 9. Log success
        logger.info(f"Found {len(tags)} related tags for series search")

        # 10. Return compact JSON (AI-optimized)
        return json.dumps(output, separators=(",", ":"), default=str)

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors
        error_msg = f"FRED API error: {e.response.status_code}"

        if e.response.status_code == 400:
            try:
                error_detail = e.response.json().get("error_message", "Bad request")
                error_msg = f"Invalid parameters: {error_detail}"
            except Exception:
                error_msg = "Invalid parameters provided"
        elif e.response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."

        logger.error(error_msg)
        return json.dumps(
            {
                "tool": "search_series_related_tags",
                "error": error_msg,
                "series_search_text": series_search_text,
                "input_tags": tag_names.split(";"),
            },
            separators=(",", ":"),
        )

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps(
            {
                "tool": "search_series_related_tags",
                "error": error_msg,
                "series_search_text": series_search_text if series_search_text else None,
                "input_tags": tag_names.split(";") if tag_names else [],
            },
            separators=(",", ":"),
        )
