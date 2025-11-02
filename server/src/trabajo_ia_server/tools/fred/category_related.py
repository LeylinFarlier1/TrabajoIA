"""
FRED Category Related Tool.

Get related categories for a specific FRED category.
"""
import json
import logging
from datetime import datetime
from typing import Optional

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.fred_client import (
    FredAPIError,
    FredAPIResponse,
    fred_client,
)

logger = logging.getLogger(__name__)

# FRED API endpoint for category related
FRED_CATEGORY_RELATED_URL = "https://api.stlouisfed.org/fred/category/related"


def get_category_related(
    category_id: int,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get the related categories for a specific FRED category.

    A related category is a one-way relation between 2 categories that is not part of
    a parent-child category hierarchy. Most categories do not have related categories.
    This tool is useful for discovering cross-references and connections between
    different parts of FRED's data taxonomy.

    Related categories provide semantic links between different hierarchies. For example,
    a state category in the "Federal Reserve Districts" hierarchy might link to the same
    state in the "States" hierarchy.

    Args:
        category_id: The ID for a FRED category (required).
                    Example: 32073 (St. Louis Federal Reserve District > States in District)
        realtime_start: Start date for real-time period (YYYY-MM-DD, optional).
                       Default: today's date
        realtime_end: End date for real-time period (YYYY-MM-DD, optional).
                     Default: today's date

    Returns:
        JSON string with related categories and metadata.

    Response Format:
        {
            "tool": "get_category_related",
            "data": [
                {
                    "id": 149,
                    "name": "Arkansas",
                    "parent_id": 27281
                },
                ...
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "category_id": 32073,
                "count": 7,
                "realtime_start": "2025-11-01",
                "realtime_end": "2025-11-01"
            }
        }

    Examples:
        # Get related categories for St. Louis Fed District states
        get_category_related(32073)

        # With specific real-time period
        get_category_related(32073, realtime_start="2024-01-01", realtime_end="2024-12-31")

        # Category with no related categories returns empty list
        get_category_related(125)
    """
    try:
        # 1. Obtain API key
        api_key = config.get_fred_api_key()

        # 2. Validate category_id
        if category_id is None or category_id < 0:
            error_msg = "Invalid category_id: must be a non-negative integer"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_category_related",
                "error": error_msg,
            }, separators=(",", ":"))

        # 3. Build parameters
        params = {
            "api_key": api_key,
            "category_id": category_id,
            "file_type": "json",
        }

        # Add optional parameters if provided
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        # 4. Log operation
        logger.info(f"Fetching related categories for category_id: {category_id}")

        # 5. Make API request with retry and caching
        ttl = config.get_cache_ttl("category_related", fallback=3600)
        response: FredAPIResponse = fred_client.get_json(
            FRED_CATEGORY_RELATED_URL,
            params,
            namespace="category_related",
            ttl=ttl,
        )
        json_data = response.json()

        # 6. Extract related categories data
        categories = json_data.get("categories", [])

        # 7. Build structured output
        output = {
            "tool": "get_category_related",
            "data": categories,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "category_id": category_id,
                "count": len(categories),
                "realtime_start": json_data.get("realtime_start"),
                "realtime_end": json_data.get("realtime_end"),
                "cache_hit": response.from_cache,
            },
        }

        # 8. Log success
        if categories:
            category_names = [cat.get("name", "Unknown") for cat in categories[:3]]
            preview = ", ".join(category_names)
            if len(categories) > 3:
                preview += f" and {len(categories) - 3} more"
            logger.info(
                f"Retrieved {len(categories)} related categories for category_id={category_id}: {preview}"
            )
        else:
            logger.info(
                f"No related categories found for category_id={category_id}"
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
            "tool": "get_category_related",
            "error": error_msg,
            "category_id": category_id,
        }, separators=(",", ":"))

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "get_category_related",
            "error": error_msg,
            "category_id": category_id if category_id is not None else None,
        }, separators=(",", ":"))
