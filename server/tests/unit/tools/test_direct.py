"""
Direct test of get_series_tags without package imports.
"""
import json
import logging
import time
import os
from datetime import datetime
from typing import Literal, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment
FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    print("ERROR: FRED_API_KEY not found in environment")
    exit(1)

# FRED API endpoint
FRED_SERIES_TAGS_URL = "https://api.stlouisfed.org/fred/series/tags"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
def _request_with_retries(url: str, params: dict) -> requests.Response:
    """Make HTTP request with retry logic."""
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
    """Get FRED tags for a series."""
    try:
        params = {
            "api_key": FRED_API_KEY,
            "series_id": series_id,
            "file_type": "json",
            "order_by": order_by,
            "sort_order": sort_order,
        }
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        logger.info(f"Fetching tags for series: '{series_id}'")
        response = _request_with_retries(FRED_SERIES_TAGS_URL, params)
        json_data = response.json()
        tags = json_data.get("tags", [])

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

        logger.info(f"Found {len(tags)} tags for series '{series_id}'")
        return json.dumps(output, separators=(",", ":"), default=str)

    except requests.exceptions.HTTPError as e:
        error_msg = f"FRED API error: {e.response.status_code}"
        if e.response.status_code == 400:
            error_msg = f"Invalid series_id: {series_id}"
        elif e.response.status_code == 404:
            error_msg = f"Series not found: {series_id}"
        elif e.response.status_code == 429:
            error_msg = "Rate limit exceeded"
        logger.error(error_msg)
        return json.dumps({"tool": "get_series_tags", "error": error_msg, "series_id": series_id}, separators=(",", ":"))

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({"tool": "get_series_tags", "error": error_msg, "series_id": series_id}, separators=(",", ":"))

# Run tests
print('=== Testing get_series_tags ===\n')

# Test 1: STLFSI
print('Test 1: STLFSI (St. Louis Financial Stress Index)')
start = time.time()
result = get_series_tags('STLFSI')
elapsed = time.time() - start
data = json.loads(result)
if 'error' in data:
    print(f'  ERROR: {data["error"]}')
else:
    print(f'  Time: {elapsed:.2f}s')
    print(f'  Total tags: {data["metadata"]["returned_count"]}')
    print(f'  Sample tags: {[tag["name"] for tag in data["data"][:5]]}')
print()

# Test 2: GDP
print('Test 2: GDP')
start = time.time()
result = get_series_tags('GDP')
elapsed = time.time() - start
data = json.loads(result)
if 'error' in data:
    print(f'  ERROR: {data["error"]}')
else:
    print(f'  Time: {elapsed:.2f}s')
    print(f'  Tags: {[tag["name"] for tag in data["data"]]}')
print()

# Test 3: UNRATE
print('Test 3: UNRATE (sorted by popularity)')
start = time.time()
result = get_series_tags('UNRATE', order_by='popularity', sort_order='desc')
elapsed = time.time() - start
data = json.loads(result)
if 'error' in data:
    print(f'  ERROR: {data["error"]}')
else:
    print(f'  Time: {elapsed:.2f}s')
    print(f'  Top 3 tags:')
    for i, tag in enumerate(data['data'][:3], 1):
        print(f'    {i}. {tag["name"]} (pop: {tag["popularity"]}, group: {tag["group_id"]})')
print()

# Test 4: Invalid ID
print('Test 4: Invalid series ID (error test)')
start = time.time()
result = get_series_tags('INVALID123')
elapsed = time.time() - start
data = json.loads(result)
if 'error' in data:
    print(f'  Expected error: {data["error"]}')
    print(f'  Time: {elapsed:.2f}s')
else:
    print(f'  Unexpected success')
print()

print('All tests completed!')
