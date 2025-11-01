"""
FRED Series Tags Tool.

Get the FRED tags for a specific series by series ID.
"""
import json
import logging
from datetime import datetime
from typing import Literal, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from trabajo_ia_server.config import config

logger = logging.getLogger(__name__)

# FRED API endpoint for series tags
FRED_SERIES_TAGS_URL = "https://api.stlouisfed.org/fred/series/tags"


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


def get_series_tags(
    series_id: str,
    order_by: Literal["series_count", "popularity", "created", "name", "group_id"] = "series_count",
    sort_order: Literal["asc", "desc"] = "desc",
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get the FRED tags for a specific series.

    This tool retrieves all tags associated with a particular FRED series, helping you
    understand the categorization and metadata of the series. Useful for discovering
    what attributes (frequency, geography, source, etc.) are assigned to a series.

    Args:
        series_id: The ID for a FRED series (required).
                  Example: "STLFSI", "GDP", "UNRATE", "CPIAUCSL"
        order_by: Sort field. Options: series_count, popularity, created, name, group_id.
                 Default: "series_count".
        sort_order: Sort direction - "asc" or "desc". Default: "desc".
        realtime_start: Start date for real-time period (YYYY-MM-DD).
                       Defaults to today's date if not specified.
        realtime_end: End date for real-time period (YYYY-MM-DD).
                     Defaults to today's date if not specified.

    Returns:
        JSON string with tags data and metadata.

    Response Format:
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
                }
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "series_id": "STLFSI",
                "total_count": 8,
                "returned_count": 8,
                "order_by": "series_count",
                "sort_order": "desc",
                "realtime_start": "2025-11-01",
                "realtime_end": "2025-11-01"
            }
        }

    Examples:
        # Get tags for St. Louis Financial Stress Index
        get_series_tags("STLFSI")

        # Get tags for GDP series
        get_series_tags("GDP")

        # Get tags for unemployment rate, sorted by popularity
        get_series_tags("UNRATE", order_by="popularity", sort_order="desc")

        # Get tags for CPI with specific real-time period
        get_series_tags(
            "CPIAUCSL",
            realtime_start="2020-01-01",
            realtime_end="2020-12-31"
        )
    """
    try:
        # 1. Obtain API key
        api_key = config.get_fred_api_key()

        # 2. Build base parameters
        params = {
            "api_key": api_key,
            "series_id": series_id,
            "file_type": "json",
            "order_by": order_by,
            "sort_order": sort_order,
        }

        # 3. Add optional parameters
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        # 4. Log operation
        logger.info(f"Fetching tags for series: '{series_id}'")

        # 5. Make API request with retry
        response = _request_with_retries(FRED_SERIES_TAGS_URL, params)
        json_data = response.json()

        # 6. Extract tags data
        tags = json_data.get("tags", [])

        # 7. Build structured output
        output = {
            "tool": "get_series_tags",
            "data": tags,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "series_id": series_id,
                "total_count": json_data.get("count", len(tags)),
                "returned_count": len(tags),
                "order_by": order_by,
                "sort_order": sort_order,
                "realtime_start": json_data.get("realtime_start"),
                "realtime_end": json_data.get("realtime_end"),
            },
        }

        # 8. Log success
        logger.info(f"Found {len(tags)} tags for series '{series_id}'")

        # 9. Return compact JSON (AI-optimized)
        return json.dumps(output, separators=(",", ":"), default=str)

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors
        error_msg = f"FRED API error: {e.response.status_code}"

        if e.response.status_code == 400:
            try:
                error_detail = e.response.json().get("error_message", "Bad request")
                error_msg = f"Invalid parameters: {error_detail}"
            except Exception:
                error_msg = f"Invalid series_id: {series_id}"
        elif e.response.status_code == 404:
            error_msg = f"Series not found: {series_id}"
        elif e.response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."

        logger.error(error_msg)
        return json.dumps(
            {
                "tool": "get_series_tags",
                "error": error_msg,
                "series_id": series_id,
            },
            separators=(",", ":"),
        )

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps(
            {
                "tool": "get_series_tags",
                "error": error_msg,
                "series_id": series_id if series_id else None,
            },
            separators=(",", ":"),
        )
