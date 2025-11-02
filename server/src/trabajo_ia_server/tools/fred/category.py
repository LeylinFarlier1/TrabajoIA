"""
FRED Category Tool.

Get information about a specific FRED category.
"""
import json
import logging
from datetime import datetime

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.fred_client import (
    FredAPIError,
    FredAPIResponse,
    fred_client,
)

logger = logging.getLogger(__name__)

# FRED API endpoint for category
FRED_CATEGORY_URL = "https://api.stlouisfed.org/fred/category"


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
        ttl = config.get_cache_ttl("category", fallback=3600)
        response: FredAPIResponse = fred_client.get_json(
            FRED_CATEGORY_URL,
            params,
            namespace="category",
            ttl=ttl,
        )
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
                "cache_hit": response.from_cache,
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

    except FredAPIError as e:
        if e.status_code == 404:
            error_msg = f"Category not found: {category_id}"
        elif e.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
        elif e.status_code == 400 and e.payload:
            detail = e.payload.get("error_message")
            error_msg = (
                f"Invalid parameters: {detail}"
                if detail
                else "Invalid category parameters provided"
            )
        else:
            error_msg = f"FRED API error: {e.message}"

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
