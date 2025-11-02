"""
FRED Series Search Tool.

Provides advanced search functionality for FRED economic data series with pagination,
filters, and comprehensive metadata.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from urllib.parse import urlencode

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.fred_client import (
    FredAPIError,
    FredAPIResponse,
    fred_client,
)
from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)

# FRED API endpoints
FRED_BASE_URL = "https://api.stlouisfed.org/fred"
FRED_SEARCH_URL = f"{FRED_BASE_URL}/series/search"

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
        limit: Maximum results to return (1-100, default: 20).
               Clamped to 100 to prevent exceeding MCP token limits.
               Larger responses may cause token overflow errors.
        offset: Starting offset for pagination (0-based)
        search_type: Search mode:
            - "full_text": Search in title, description, and metadata
            - "series_id": Exact match on series ID
        category_id: Restrict search to specific FRED category ID
        filter_variable: Filter by metadata variable (e.g., "frequency", "units", "seasonal_adjustment")
        filter_value: Value for the filter variable (e.g., "Monthly", "Percent")
        tag_names: Semicolon-delimited tag names to include (e.g., "usa;nsa")
        exclude_tag_names: Semicolon-delimited tag names to exclude (e.g., "discontinued;quarterly").
                          Note: Requires tag_names to be set (FRED API requirement)
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
        
        # Validate and clamp limit to prevent token overflow (MCP limit: 25k tokens)
        # Responses with limit > 100 can exceed MCP token limits
        if limit > 100:
            logger.warning(
                f"Requested limit={limit} exceeds recommended maximum of 100. "
                f"Large responses may exceed MCP token limits. Clamping to 100."
            )
            limit = 100
        limit = max(1, min(limit, 100))  # Clamp to safe range (1-100)

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

        ttl = config.get_cache_ttl("search_series", fallback=300)
        response: FredAPIResponse = fred_client.get_json(
            FRED_SEARCH_URL,
            base_params,
            namespace="search_series",
            ttl=ttl,
        )
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
                    "cache_hit": response.from_cache,
                }
            }
        }

        logger.info(
            f"Successfully found {len(results)} series for '{search_text}'"
        )

        # Always return compact JSON for AI consumption (saves tokens)
        return json.dumps(output, separators=(",", ":"), default=str)

    except FredAPIError as e:
        if e.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
        elif e.status_code == 400 and e.payload:
            detail = e.payload.get("error_message")
            error_msg = (
                f"Invalid search parameters: {detail}"
                if detail
                else "Invalid search parameters provided"
            )
        else:
            error_msg = f"FRED API error: {e.message}"

        logger.error(error_msg)
        return json.dumps({
            "error": error_msg,
            "search_text": search_text,
            "tool": "search_fred_series",
            "metadata": {"fetch_date": datetime.utcnow().isoformat() + "Z"}
        }, indent=2)

    except Exception as e:
        error_msg = f"Error searching FRED series with text '{search_text}': {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "error": str(e),
            "search_text": search_text,
            "tool": "search_fred_series",
            "metadata": {"fetch_date": datetime.utcnow().isoformat() + "Z"}
        }, indent=2)
