"""
FRED Category Tool.

Get information about a specific FRED category.
"""
import json
import logging
from datetime import datetime

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from trabajo_ia_server.config import config

logger = logging.getLogger(__name__)

# FRED API endpoint for category
FRED_CATEGORY_URL = "https://api.stlouisfed.org/fred/category"


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


def get_category(category_id: int) -> str:
    """
    Get information about a specific FRED category.

    FRED organizes its economic data series into a hierarchical taxonomy of categories.
    This tool retrieves metadata about a specific category, including its name, parent
    category, and optional notes. Useful for navigating the FRED category tree and
    understanding how data is organized.

    Args:
        category_id: The ID for a FRED category (required).
                    Example: 0 (root), 125 (Trade Balance), 32991 (Money, Banking, & Finance)

    Returns:
        JSON string with category information and metadata.

    Response Format:
        {
            "tool": "get_category",
            "data": {
                "id": 125,
                "name": "Trade Balance",
                "parent_id": 13,
                "notes": "Optional category notes/description"
            },
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "category_id": 125
            }
        }

    Examples:
        # Get root category
        get_category(0)

        # Get Trade Balance category
        get_category(125)

        # Get Money, Banking, & Finance category
        get_category(32991)

        # Get National Accounts category
        get_category(32992)
    """
    try:
        # 1. Obtain API key
        api_key = config.get_fred_api_key()

        # 2. Validate category_id
        if category_id is None or category_id < 0:
            error_msg = "Invalid category_id: must be a non-negative integer"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_category",
                "error": error_msg,
            }, separators=(",", ":"))

        # 3. Build parameters
        params = {
            "api_key": api_key,
            "category_id": category_id,
            "file_type": "json",
        }

        # 4. Log operation
        logger.info(f"Fetching category information for category_id: {category_id}")

        # 5. Make API request with retry
        response = _request_with_retries(FRED_CATEGORY_URL, params)
        json_data = response.json()

        # 6. Extract category data
        categories = json_data.get("categories", [])

        if not categories:
            error_msg = f"Category not found: {category_id}"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_category",
                "error": error_msg,
                "category_id": category_id,
            }, separators=(",", ":"))

        # Get first (and only) category
        category = categories[0]

        # 7. Build structured output
        output = {
            "tool": "get_category",
            "data": {
                "id": category.get("id"),
                "name": category.get("name"),
                "parent_id": category.get("parent_id"),
            },
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "category_id": category_id,
            },
        }

        # Add notes if present
        if "notes" in category:
            output["data"]["notes"] = category["notes"]

        # 8. Log success
        logger.info(
            f"Retrieved category '{category.get('name')}' (id={category_id}, parent={category.get('parent_id')})"
        )

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
                error_msg = f"Invalid category_id: {category_id}"
        elif e.response.status_code == 404:
            error_msg = f"Category not found: {category_id}"
        elif e.response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."

        logger.error(error_msg)
        return json.dumps({
            "tool": "get_category",
            "error": error_msg,
            "category_id": category_id,
        }, separators=(",", ":"))

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "get_category",
            "error": error_msg,
            "category_id": category_id if category_id is not None else None,
        }, separators=(",", ":"))
