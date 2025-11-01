"""
FRED Tags Discovery Tool.

Provides functionality to discover and search FRED tags for better series filtering.
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)

# HTTP session for connection pooling
_SESSION = requests.Session()
_SESSION.headers.update({
    'User-Agent': 'Trabajo-IA-MCP-Server/0.1.3',
    'Accept': 'application/json'
})

# FRED API endpoints
FRED_BASE_URL = "https://api.stlouisfed.org/fred"
FRED_TAGS_URL = f"{FRED_BASE_URL}/tags"


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
        logger.warning("Rate limited by FRED API")
        raise ValueError("Rate limit hit, retrying...")

    if not response.ok:
        raise ValueError(
            f"FRED API request failed: {response.status_code} - {response.text}"
        )

    return response


def get_fred_tags(
    search_text: Optional[str] = None,
    tag_names: Optional[str] = None,
    tag_group_id: Optional[Literal["freq", "gen", "geo", "geot", "rls", "seas", "src", "cc"]] = None,
    limit: int = 50,
    offset: int = 0,
    order_by: Literal["series_count", "popularity", "created", "name", "group_id"] = "popularity",
    sort_order: Literal["asc", "desc"] = "desc"
) -> str:
    """
    Get FRED tags to discover available tags for filtering series searches.

    This tool helps users discover what tags are available in FRED, making it easier
    to construct effective search queries with tag filters.

    Args:
        search_text: Words to find matching tags (optional)
        tag_names: Semicolon-delimited tag names to filter by (optional)
        tag_group_id: Filter by tag group type (optional):
            - "freq": Frequency (monthly, quarterly, annual, etc.)
            - "gen": General/Concept (gdp, employment, inflation, etc.)
            - "geo": Geography (usa, canada, japan, etc.)
            - "geot": Geography Type (nation, state, county, etc.)
            - "rls": Release (main economic indicators, etc.)
            - "seas": Seasonal Adjustment (sa, nsa)
            - "src": Source (bls, bea, census, etc.)
            - "cc": Citation & Copyright
        limit: Maximum results to return (1-1000, default: 50 - optimized for AI)
        offset: Starting offset (default: 0)
        order_by: Sort field (default: "popularity")
            - "series_count": Number of series with this tag
            - "popularity": FRED popularity score
            - "created": When tag was created
            - "name": Tag name alphabetically
            - "group_id": Group ID
        sort_order: Sort direction "asc" or "desc" (default: "desc")

    Returns:
        Compact JSON with list of tags and metadata

    Examples:
        >>> get_fred_tags()  # Get top 50 most popular tags
        >>> get_fred_tags(search_text="employment")  # Search for employment-related tags
        >>> get_fred_tags(tag_group_id="freq")  # Get all frequency tags
        >>> get_fred_tags(tag_group_id="geo", limit=100)  # Get top 100 geography tags
    """
    try:
        # Get API key from configuration
        api_key = config.get_fred_api_key()
        limit = max(1, min(limit, 1000))  # Clamp to valid range

        # Base API parameters
        params: Dict[str, Any] = {
            "api_key": api_key,
            "file_type": "json",
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        # Add optional filters
        if search_text:
            params["search_text"] = search_text
        if tag_names:
            params["tag_names"] = tag_names
        if tag_group_id:
            params["tag_group_id"] = tag_group_id

        logger.info(
            f"Fetching FRED tags "
            f"(search='{search_text}', group={tag_group_id}, limit={limit})"
        )

        response = _request_with_retries(FRED_TAGS_URL, params)
        json_data = response.json()

        # Check for API errors
        if "error_code" in json_data and json_data["error_code"] != 0:
            error_msg = json_data.get("error_message", "Unknown FRED API error")
            raise ValueError(f"FRED API Error {json_data['error_code']}: {error_msg}")

        # Extract results
        tags = json_data.get("tags", [])
        total_count = json_data.get("count", len(tags))

        # Build MCP-compatible output
        output: Dict[str, Any] = {
            "tool": "get_fred_tags",
            "data": tags,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "search_text": search_text,
                "tag_names": tag_names,
                "tag_group_id": tag_group_id,
                "total_count": total_count,
                "returned_count": len(tags),
                "limit": limit,
                "offset": offset,
                "order_by": order_by,
                "sort_order": sort_order,
                "api_info": {
                    "url": response.url,
                    "status_code": response.status_code,
                    "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining"),
                }
            }
        }

        logger.info(
            f"Successfully found {len(tags)} tags "
            f"(search='{search_text}', group={tag_group_id})"
        )

        # Always return compact JSON for AI consumption (saves tokens)
        return json.dumps(output, separators=(",", ":"), default=str)

    except Exception as e:
        error_msg = f"Error fetching FRED tags: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "error": str(e),
            "tool": "get_fred_tags",
            "metadata": {"fetch_date": datetime.utcnow().isoformat() + "Z"}
        }, separators=(",", ":"))
