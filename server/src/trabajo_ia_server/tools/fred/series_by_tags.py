"""
FRED Series by Tags Tool.

Get series that match ALL specified tags and NONE of the excluded tags.
"""
import json
import logging
from datetime import datetime
from typing import Literal, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from trabajo_ia_server.config import config

logger = logging.getLogger(__name__)

# FRED API endpoint for series by tags
FRED_SERIES_BY_TAGS_URL = "https://api.stlouisfed.org/fred/tags/series"


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


def get_series_by_tags(
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

    This tool performs precise series filtering using FRED's tag system. It returns
    series that have ALL tags listed in tag_names and NONE of the tags in
    exclude_tag_names, enabling powerful multi-criteria searches.

    Args:
        tag_names: REQUIRED. Semicolon-delimited list of tag names that series must
                  have ALL of. Example: "slovenia;food;oecd" returns only series
                  tagged with all three tags.
        exclude_tag_names: Optional semicolon-delimited list of tag names that series
                          must have NONE of. Example: "discontinued;daily" excludes
                          series with either tag.
        limit: Maximum number of series to return (1-1000). Default: 20 (AI-optimized).
        offset: Starting offset for pagination. Default: 0.
        order_by: Sort field. Options: series_id, title, units, frequency,
                 seasonal_adjustment, realtime_start, realtime_end, last_updated,
                 observation_start, observation_end, popularity, group_popularity.
                 Default: series_id.
        sort_order: Sort direction - "asc" or "desc". Default: asc.
        realtime_start: Optional start date for real-time period (YYYY-MM-DD).
                       Defaults to today's date if not specified.
        realtime_end: Optional end date for real-time period (YYYY-MM-DD).
                     Defaults to today's date if not specified.

    Returns:
        JSON string with series data and metadata.

    Response Format:
        {
            "tool": "get_series_by_tags",
            "data": [
                {
                    "id": "CPGDFD02SIA657N",
                    "title": "Consumer Price Index...",
                    "observation_start": "1996-01-01",
                    "observation_end": "2016-01-01",
                    "frequency": "Annual",
                    "frequency_short": "A",
                    "units": "Growth Rate Previous Period",
                    "units_short": "Growth Rate Previous Period",
                    "seasonal_adjustment": "Not Seasonally Adjusted",
                    "seasonal_adjustment_short": "NSA",
                    "last_updated": "2017-04-20 00:48:35-05",
                    "popularity": 0,
                    "group_popularity": 0,
                    "notes": "..."
                },
                ...
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "required_tags": ["slovenia", "food", "oecd"],
                "excluded_tags": ["discontinued"],
                "total_count": 18,
                "returned_count": 18,
                "limit": 20,
                "offset": 0,
                "order_by": "series_id",
                "sort_order": "asc",
                "realtime_start": "2025-11-01",
                "realtime_end": "2025-11-01"
            }
        }

    Examples:
        # Find series with ALL tags: slovenia, food, oecd
        get_series_by_tags("slovenia;food;oecd")

        # Find monthly GDP series, excluding discontinued
        get_series_by_tags("gdp;monthly", exclude_tag_names="discontinued")

        # Find popular employment series
        get_series_by_tags(
            "employment;usa;nsa",
            limit=10,
            order_by="popularity",
            sort_order="desc"
        )

        # Find recent inflation data
        get_series_by_tags(
            "inflation;monthly;cpi",
            exclude_tag_names="discontinued;revision",
            order_by="last_updated",
            sort_order="desc",
            limit=15
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
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        # 5. Log operation
        logger.info(
            f"Fetching series with tags: '{tag_names}' "
            f"(exclude: '{exclude_tag_names}', order: {order_by})"
        )

        # 6. Make API request with retry
        response = _request_with_retries(FRED_SERIES_BY_TAGS_URL, params)
        json_data = response.json()

        # 7. Extract series data (note: FRED uses "seriess" with double 's')
        series_list = json_data.get("seriess", [])

        # 8. Build structured output
        output = {
            "tool": "get_series_by_tags",
            "data": series_list,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "required_tags": tag_names.split(";"),
                "excluded_tags": exclude_tag_names.split(";") if exclude_tag_names else None,
                "total_count": json_data.get("count", len(series_list)),
                "returned_count": len(series_list),
                "limit": limit,
                "offset": offset,
                "order_by": order_by,
                "sort_order": sort_order,
                "realtime_start": json_data.get("realtime_start"),
                "realtime_end": json_data.get("realtime_end"),
            },
        }

        # 9. Log success
        logger.info(f"Found {len(series_list)} series matching tags")

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
                "tool": "get_series_by_tags",
                "error": error_msg,
                "required_tags": tag_names.split(";"),
            },
            separators=(",", ":"),
        )

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps(
            {
                "tool": "get_series_by_tags",
                "error": error_msg,
                "required_tags": tag_names.split(";") if tag_names else [],
            },
            separators=(",", ":"),
        )
