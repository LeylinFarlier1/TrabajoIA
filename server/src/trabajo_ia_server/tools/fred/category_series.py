"""
FRED Category Series Tool.

Get the series in a specific category.
"""
import json
import logging
from datetime import datetime
from typing import Literal, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from trabajo_ia_server.config import config

logger = logging.getLogger(__name__)

# FRED API endpoint for category series
FRED_CATEGORY_SERIES_URL = "https://api.stlouisfed.org/fred/category/series"


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


def get_category_series(
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

    This tool retrieves all economic data series belonging to a given category, with
    extensive filtering, sorting, and pagination options. Essential for discovering
    available data series within a topic area and finding specific series based on
    attributes like frequency, units, or tags.

    Args:
        category_id: The ID for a category (required).
                    Example: 125 (Trade Balance), 32991 (Money, Banking & Finance)
        realtime_start: Start date for real-time period (YYYY-MM-DD, optional).
                       Default: today's date.
        realtime_end: End date for real-time period (YYYY-MM-DD, optional).
                     Default: today's date.
        limit: Maximum number of results to return (1-1000, default: 1000).
              Use with offset for pagination.
        offset: Result offset for pagination (default: 0).
               Example: offset=1000 gets results 1001-2000.
        order_by: Order results by specified attribute (default: "series_id").
                 Options: series_id, title, units, frequency, seasonal_adjustment,
                         realtime_start, realtime_end, last_updated, observation_start,
                         observation_end, popularity, group_popularity.
        sort_order: Sort order - "asc" or "desc" (default: "asc").
        filter_variable: Attribute to filter by (optional).
                        Options: "frequency", "units", "seasonal_adjustment".
        filter_value: Value of filter_variable to match (optional).
                     Example: filter_variable="frequency", filter_value="Monthly".
        tag_names: Semicolon-delimited tags that series must have ALL of (optional).
                  Example: "income;bea" matches series with both tags.
        exclude_tag_names: Semicolon-delimited tags that series must have NONE of (optional).
                          Example: "discontinued;annual" excludes series with either tag.
                          Requires tag_names to be set.

    Returns:
        JSON string with series list and metadata.

    Response Format:
        {
            "tool": "get_category_series",
            "data": [
                {
                    "id": "BOPGSTB",
                    "title": "Trade Balance: Goods and Services...",
                    "observation_start": "1992-01-01",
                    "observation_end": "2017-05-01",
                    "frequency": "Monthly",
                    "frequency_short": "M",
                    "units": "Millions of Dollars",
                    "units_short": "Mil. of $",
                    "seasonal_adjustment": "Seasonally Adjusted",
                    "seasonal_adjustment_short": "SA",
                    "last_updated": "2017-07-06 09:32:14-05",
                    "popularity": 62,
                    "group_popularity": 62,
                    "notes": "Optional series notes"
                }
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "category_id": 125,
                "total_count": 45,
                "returned_count": 45,
                "limit": 1000,
                "offset": 0,
                "order_by": "series_id",
                "sort_order": "asc",
                "realtime_start": "2025-11-01",
                "realtime_end": "2025-11-01"
            }
        }

    Examples:
        # Get all series in Trade Balance category
        get_category_series(125)

        # Get monthly series only
        get_category_series(125, filter_variable="frequency", filter_value="Monthly")

        # Get series sorted by popularity
        get_category_series(125, order_by="popularity", sort_order="desc")

        # Get series with specific tags
        get_category_series(125, tag_names="nsa;usa")

        # Paginate through results (first 100)
        get_category_series(125, limit=100, offset=0)

        # Get seasonally adjusted series only
        get_category_series(
            125,
            filter_variable="seasonal_adjustment",
            filter_value="Seasonally Adjusted"
        )
    """
    try:
        # 1. Obtain API key
        api_key = config.get_fred_api_key()

        # 2. Validate category_id
        if category_id is None or category_id < 0:
            error_msg = "Invalid category_id: must be a non-negative integer"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_category_series",
                "error": error_msg,
            }, separators=(",", ":"))

        # 3. Validate limit and offset
        if limit < 1 or limit > 1000:
            error_msg = "Invalid limit: must be between 1 and 1000"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_category_series",
                "error": error_msg,
            }, separators=(",", ":"))

        if offset < 0:
            error_msg = "Invalid offset: must be non-negative"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_category_series",
                "error": error_msg,
            }, separators=(",", ":"))

        # 4. Build base parameters
        params = {
            "api_key": api_key,
            "category_id": category_id,
            "file_type": "json",
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        # 5. Add optional parameters
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end
        if filter_variable:
            params["filter_variable"] = filter_variable
        if filter_value:
            params["filter_value"] = filter_value
        if tag_names:
            params["tag_names"] = tag_names
        if exclude_tag_names:
            params["exclude_tag_names"] = exclude_tag_names

        # 6. Log operation
        filter_info = ""
        if filter_variable and filter_value:
            filter_info = f" (filter: {filter_variable}={filter_value})"
        tag_info = ""
        if tag_names:
            tag_info = f" (tags: {tag_names})"
        logger.info(
            f"Fetching series for category_id: {category_id}{filter_info}{tag_info}, "
            f"limit={limit}, offset={offset}"
        )

        # 7. Make API request with retry
        response = _request_with_retries(FRED_CATEGORY_SERIES_URL, params)
        json_data = response.json()

        # 8. Extract series data
        series_list = json_data.get("seriess", [])

        # 9. Build structured output
        output = {
            "tool": "get_category_series",
            "data": series_list,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "category_id": category_id,
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

        # Add filter info if used
        if filter_variable and filter_value:
            output["metadata"]["filter_variable"] = filter_variable
            output["metadata"]["filter_value"] = filter_value

        # Add tag info if used
        if tag_names:
            output["metadata"]["tag_names"] = tag_names
        if exclude_tag_names:
            output["metadata"]["exclude_tag_names"] = exclude_tag_names

        # 10. Log success
        logger.info(
            f"Retrieved {len(series_list)} series for category {category_id} "
            f"(total available: {json_data.get('count', 'unknown')})"
        )

        # 11. Return compact JSON (AI-optimized)
        return json.dumps(output, separators=(",", ":"), default=str)

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors
        error_msg = f"FRED API error: {e.response.status_code}"

        if e.response.status_code == 400:
            try:
                error_detail = e.response.json().get("error_message", "Bad request")
                error_msg = f"Invalid parameters: {error_detail}"
            except Exception:
                error_msg = f"Invalid parameters for category_id: {category_id}"
        elif e.response.status_code == 404:
            error_msg = f"Category not found: {category_id}"
        elif e.response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."

        logger.error(error_msg)
        return json.dumps({
            "tool": "get_category_series",
            "error": error_msg,
            "category_id": category_id,
        }, separators=(",", ":"))

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "get_category_series",
            "error": error_msg,
            "category_id": category_id if category_id is not None else None,
        }, separators=(",", ":"))
