"""
FRED Category Children Tool.

Get the child categories for a specified parent category.
"""
import json
import logging
from datetime import datetime
from typing import Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from trabajo_ia_server.config import config

logger = logging.getLogger(__name__)

# FRED API endpoint for category children
FRED_CATEGORY_CHILDREN_URL = "https://api.stlouisfed.org/fred/category/children"


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


def get_category_children(
    category_id: int = 0,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get the child categories for a specified parent category.

    This tool retrieves all direct child categories of a given parent category,
    enabling top-down exploration of FRED's hierarchical category taxonomy. Essential
    for navigating the category tree and discovering sub-categories within a topic area.

    Args:
        category_id: The ID for a parent category (default: 0 - root category).
                    Example: 0 (root), 13 (International Data), 32991 (Money, Banking)
        realtime_start: Start date for real-time period (YYYY-MM-DD, optional).
                       Default: today's date.
        realtime_end: End date for real-time period (YYYY-MM-DD, optional).
                     Default: today's date.

    Returns:
        JSON string with child categories list and metadata.

    Response Format:
        {
            "tool": "get_category_children",
            "data": [
                {
                    "id": 16,
                    "name": "Exports",
                    "parent_id": 13,
                    "notes": "Optional notes"
                },
                {
                    "id": 17,
                    "name": "Imports",
                    "parent_id": 13
                }
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "parent_category_id": 13,
                "total_count": 5,
                "returned_count": 5,
                "realtime_start": "2025-11-01",
                "realtime_end": "2025-11-01"
            }
        }

    Examples:
        # Get top-level categories (children of root)
        get_category_children(0)

        # Get children of International Data category
        get_category_children(13)

        # Get children of Money, Banking, & Finance
        get_category_children(32991)

        # Get children with real-time period
        get_category_children(
            13,
            realtime_start="2020-01-01",
            realtime_end="2020-12-31"
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
                "tool": "get_category_children",
                "error": error_msg,
            }, separators=(",", ":"))

        # 3. Build base parameters
        params = {
            "api_key": api_key,
            "category_id": category_id,
            "file_type": "json",
        }

        # 4. Add optional real-time parameters
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        # 5. Log operation
        logger.info(f"Fetching child categories for parent category_id: {category_id}")

        # 6. Make API request with retry
        response = _request_with_retries(FRED_CATEGORY_CHILDREN_URL, params)
        json_data = response.json()

        # 7. Extract categories data
        categories = json_data.get("categories", [])

        # 8. Build structured output
        output = {
            "tool": "get_category_children",
            "data": categories,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "parent_category_id": category_id,
                "total_count": len(categories),
                "returned_count": len(categories),
                "realtime_start": json_data.get("realtime_start"),
                "realtime_end": json_data.get("realtime_end"),
            },
        }

        # 9. Log success
        logger.info(
            f"Retrieved {len(categories)} child categories for parent {category_id}"
        )

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
                error_msg = f"Invalid category_id: {category_id}"
        elif e.response.status_code == 404:
            error_msg = f"Category not found: {category_id}"
        elif e.response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."

        logger.error(error_msg)
        return json.dumps({
            "tool": "get_category_children",
            "error": error_msg,
            "category_id": category_id,
        }, separators=(",", ":"))

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "get_category_children",
            "error": error_msg,
            "category_id": category_id if category_id is not None else None,
        }, separators=(",", ":"))
