"""
FRED Series Search Tool.

Provides advanced search functionality for FRED economic data series with pagination,
filters, and comprehensive metadata.
"""
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
import requests
from urllib.parse import urlencode
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)

# HTTP session for connection pooling
_SESSION = requests.Session()
_SESSION.headers.update({
    'User-Agent': 'Trabajo-IA-MCP-Server/0.1.1',
    'Accept': 'application/json'
})

# FRED API endpoints
FRED_BASE_URL = "https://api.stlouisfed.org/fred"
FRED_SEARCH_URL = f"{FRED_BASE_URL}/series/search"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type((requests.exceptions.RequestException, ValueError))
)
def _request_with_retries(url: str, params: Dict[str, Any]) -> requests.Response:
    """
    Make a request to FRED API with retries and rate limit handling.

    Args:
        url: FRED API endpoint URL
        params: Query parameters including API key

    Returns:
        HTTP response object

    Raises:
        ValueError: If request fails or rate limit is hit
    """
    response = _SESSION.get(url, params=params, timeout=30)

    if response.status_code == 429:  # Rate limited
        reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
        sleep_time = max(1, reset_time - time.time())
        logger.warning(f"Rate limited. Sleeping for {sleep_time:.1f} seconds.")
        time.sleep(sleep_time)
        raise ValueError("Rate limit hit, retrying...")

    if not response.ok:
        raise ValueError(
            f"FRED API request failed: {response.status_code} - {response.text}"
        )

    return response


def search_fred_series(
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
    Search FRED economic data series with advanced filters and pagination.

    This tool provides comprehensive search capabilities across the entire FRED database,
    supporting full-text search, filtering by categories, tags, and other metadata.

    Args:
        search_text: Text to search for (e.g., 'unemployment', 'GDP', 'inflation')
        limit: Maximum results to return (1-1000, default: 20 - optimized for AI consumption)
        offset: Starting offset for pagination (0-based)
        search_type: Search mode:
            - "full_text": Search in title, description, and metadata
            - "series_id": Exact match on series ID
        category_id: Restrict search to specific FRED category ID
        filter_variable: Filter by metadata variable (e.g., "frequency", "units", "seasonal_adjustment")
        filter_value: Value for the filter variable (e.g., "Monthly", "Percent")
        tag_names: Semicolon-delimited tag names to include (e.g., "usa;nsa")
        exclude_tag_names: Semicolon-delimited tag names to exclude (e.g., "discontinued;quarterly")
        realtime_start: Start date for real-time data window (YYYY-MM-DD)
        realtime_end: End date for real-time data window (YYYY-MM-DD)
        order_by: Sort field - "popularity", "search_rank", "title", "units",
                  or "last_updated"
        sort_order: Sort direction - "asc" or "desc"

    Returns:
        JSON string containing:
        - data: List of matching series with full metadata
        - metadata: Search parameters, counts, pagination info, and API details

    Examples:
        >>> search_fred_series("unemployment rate", limit=10)
        >>> search_fred_series("GDP", filter_variable="frequency", filter_value="Quarterly")
        >>> search_fred_series("inflation", tag_names="usa;nsa", order_by="last_updated")
    """
    try:
        # Get API key from configuration
        api_key = config.get_fred_api_key()
        limit = max(1, min(limit, 1000))  # Clamp to valid range

        # Base API parameters
        base_params = {
            "api_key": api_key,
            "file_type": "json",
            "limit": limit,
            "order_by": order_by,
            "sort_order": sort_order,
            "offset": offset,
        }

        # Configure search type
        if search_type == "series_id":
            base_params["search_type"] = "series_id"
            base_params["series_id"] = search_text
        else:
            base_params["search_text"] = search_text

        # Add optional filters
        if category_id is not None:
            base_params["category_id"] = category_id
        if filter_variable and filter_value:
            base_params["filter_variable"] = filter_variable
            base_params["filter_value"] = filter_value
        if tag_names:
            base_params["tag_names"] = tag_names
        if exclude_tag_names:
            base_params["exclude_tag_names"] = exclude_tag_names
        if realtime_start:
            base_params["realtime_start"] = realtime_start
        if realtime_end:
            base_params["realtime_end"] = realtime_end

        # Single request - no pagination for speed and AI optimization
        base_params["offset"] = offset

        logger.info(
            f"Searching FRED series: '{search_text}' (limit={limit}, offset={offset})"
        )

        response = _request_with_retries(FRED_SEARCH_URL, base_params)
        json_data = response.json()

        # Check for API errors
        if "error_code" in json_data and json_data["error_code"] != 0:
            error_msg = json_data.get("error_message", "Unknown FRED API error")
            raise ValueError(f"FRED API Error {json_data['error_code']}: {error_msg}")

        # Extract results
        results = json_data.get("seriess", [])
        total_count = json_data.get("count", len(results))

        # Build MCP-compatible output
        output: Dict[str, Any] = {
            "tool": "search_fred_series",
            "data": results,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "search_text": search_text,
                "search_type": search_type,
                "total_count": total_count,
                "returned_count": len(results),
                "limit": limit,
                "offset": offset,
                "filters": {
                    "category_id": category_id,
                    "filter_variable": filter_variable,
                    "filter_value": filter_value,
                    "tag_names": tag_names,
                    "exclude_tag_names": exclude_tag_names,
                    "realtime_start": realtime_start,
                    "realtime_end": realtime_end,
                    "order_by": order_by,
                    "sort_order": sort_order
                },
                "api_info": {
                    "url": response.url,
                    "status_code": response.status_code,
                    "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining"),
                }
            }
        }

        logger.info(
            f"Successfully found {len(results)} series for '{search_text}'"
        )

        # Always return compact JSON for AI consumption (saves tokens)
        return json.dumps(output, separators=(",", ":"), default=str)

    except Exception as e:
        error_msg = f"Error searching FRED series with text '{search_text}': {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "error": str(e),
            "search_text": search_text,
            "tool": "search_fred_series",
            "metadata": {"fetch_date": datetime.utcnow().isoformat() + "Z"}
        }, indent=2)
