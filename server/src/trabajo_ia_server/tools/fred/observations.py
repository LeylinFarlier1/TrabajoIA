"""
FRED Series Observations Tool.

Get observations or data values for an economic data series.
"""
import json
import logging
from datetime import datetime
from typing import Literal, Optional

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.fred_client import (
    FredAPIError,
    FredAPIResponse,
    fred_client,
)

logger = logging.getLogger(__name__)

# FRED API endpoint for series observations
FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"


def get_series_observations(
    series_id: str,
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
    limit: int = 100000,
    offset: int = 0,
    sort_order: Literal["asc", "desc"] = "asc",
    units: Literal["lin", "chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"] = "lin",
    frequency: Optional[Literal["d", "w", "bw", "m", "q", "sa", "a", "wef", "weth", "wew", "wetu", "wem", "wesu", "wesa", "bwew", "bwem"]] = None,
    aggregation_method: Literal["avg", "sum", "eop"] = "avg",
    output_type: Literal[1, 2, 3, 4] = 1,
) -> str:
    """
    Get observations or data values for an economic data series.

    This tool retrieves historical time-series data for a specific FRED series.
    It supports date range filtering, data transformations, frequency aggregation,
    and various output formats for vintages and real-time data.

    Args:
        series_id: The ID for a FRED series (required).
                  Example: "GNPCA", "GDP", "UNRATE", "CPIAUCSL"
        observation_start: Start date for observations (YYYY-MM-DD).
                          Default: 1776-07-04 (earliest available).
        observation_end: End date for observations (YYYY-MM-DD).
                        Default: 9999-12-31 (latest available).
        realtime_start: Start date for real-time period (YYYY-MM-DD).
                       Default: today's date.
        realtime_end: End date for real-time period (YYYY-MM-DD).
                     Default: today's date.
        limit: Maximum number of results (1-100000). Default: 100000.
        offset: Starting offset for pagination. Default: 0.
        sort_order: Sort by observation_date - "asc" or "desc". Default: "asc".
        units: Data value transformation. Default: "lin" (no transformation).
              - "lin": Levels (no transformation)
              - "chg": Change
              - "ch1": Change from Year Ago
              - "pch": Percent Change
              - "pc1": Percent Change from Year Ago
              - "pca": Compounded Annual Rate of Change
              - "cch": Continuously Compounded Rate of Change
              - "cca": Continuously Compounded Annual Rate of Change
              - "log": Natural Log
        frequency: Lower frequency to aggregate values to. Default: None (no aggregation).
                  Options: 'd', 'w', 'bw', 'm', 'q', 'sa', 'a', 'wef', 'weth', 'wew',
                  'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem'
        aggregation_method: Method for frequency aggregation. Default: "avg".
                           - "avg": Average
                           - "sum": Sum
                           - "eop": End of Period
        output_type: Output format for observations. Default: 1.
                    - 1: Observations by Real-Time Period
                    - 2: Observations by Vintage Date, All Observations
                    - 3: Observations by Vintage Date, New and Revised Only
                    - 4: Observations, Initial Release Only

    Returns:
        JSON string with observations data and metadata.

    Response Format:
        {
            "tool": "get_series_observations",
            "data": [
                {
                    "realtime_start": "2013-08-14",
                    "realtime_end": "2013-08-14",
                    "date": "1929-01-01",
                    "value": "1065.9"
                }
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "series_id": "GNPCA",
                "observation_start": "1776-07-04",
                "observation_end": "9999-12-31",
                "units": "lin",
                "frequency": null,
                "aggregation_method": "avg",
                "output_type": 1,
                "total_count": 84,
                "returned_count": 84
            }
        }

    Examples:
        # Get all observations for a series
        get_series_observations("GNPCA")

        # Get observations for specific date range
        get_series_observations(
            "GDP",
            observation_start="2020-01-01",
            observation_end="2023-12-31"
        )

        # Get percent change from year ago
        get_series_observations("UNRATE", units="pc1")

        # Get monthly aggregation of daily data
        get_series_observations(
            "DFF",
            frequency="m",
            aggregation_method="avg"
        )

        # Get limited recent observations
        get_series_observations(
            "CPIAUCSL",
            observation_start="2020-01-01",
            limit=100,
            sort_order="desc"
        )
    """
    try:
        # 1. Obtain API key
        api_key = config.get_fred_api_key()

        # 2. Validate series_id
        if not series_id or not series_id.strip():
            error_msg = "Invalid series ID: series_id cannot be empty"
            logger.error(error_msg)
            return json.dumps({
                "tool": "get_series_observations",
                "error": error_msg,
            }, separators=(",", ":"))

        # 3. Validate and clamp limit
        limit = max(1, min(limit, 100000))

        # 4. Build base parameters
        params = {
            "api_key": api_key,
            "series_id": series_id.strip(),
            "file_type": "json",
            "limit": limit,
            "offset": offset,
            "sort_order": sort_order,
            "units": units,
            "aggregation_method": aggregation_method,
            "output_type": output_type,
        }

        # 5. Add optional date parameters
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        # 6. Add frequency aggregation if specified
        if frequency:
            params["frequency"] = frequency

        # 7. Log operation
        date_range = ""
        if observation_start or observation_end:
            start = observation_start or "earliest"
            end = observation_end or "latest"
            date_range = f" ({start} to {end})"

        transform = f" with {units} transformation" if units != "lin" else ""
        freq = f", aggregated to {frequency}" if frequency else ""

        logger.info(
            f"Fetching observations for series '{series_id}'{date_range}{transform}{freq}"
        )

        # 8. Make API request with retry
        ttl = config.get_cache_ttl("observations", fallback=900)
        response: FredAPIResponse = fred_client.get_json(
            FRED_OBSERVATIONS_URL,
            params,
            namespace="observations",
            ttl=ttl,
        )
        json_data = response.json()

        # 9. Extract observations
        observations = json_data.get("observations", [])

        # 10. Build structured output
        output = {
            "tool": "get_series_observations",
            "data": observations,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "series_id": series_id,
                "realtime_start": json_data.get("realtime_start"),
                "realtime_end": json_data.get("realtime_end"),
                "observation_start": json_data.get("observation_start"),
                "observation_end": json_data.get("observation_end"),
                "units": json_data.get("units"),
                "frequency": json_data.get("frequency"),
                "aggregation_method": aggregation_method,
                "output_type": json_data.get("output_type"),
                "order_by": json_data.get("order_by", "observation_date"),
                "sort_order": json_data.get("sort_order"),
                "total_count": json_data.get("count", len(observations)),
                "returned_count": len(observations),
                "limit": limit,
                "offset": offset,
                "cache_hit": response.from_cache,
            },
        }

        # 11. Log success
        logger.info(
            f"Retrieved {len(observations)} observations for series '{series_id}'"
        )

        # 12. Return compact JSON (AI-optimized)
        return json.dumps(output, separators=(",", ":"), default=str)

    except FredAPIError as e:
        if e.status_code == 404:
            error_msg = f"Series not found: {series_id}"
        elif e.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
        elif e.status_code == 400 and e.payload:
            detail = e.payload.get("error_message")
            fallback = f"Invalid series_id or parameters: {series_id}"
            error_msg = f"Invalid parameters: {detail}" if detail else fallback
        else:
            error_msg = f"FRED API error: {e.message}"

        logger.error(error_msg)
        return json.dumps({
            "tool": "get_series_observations",
            "error": error_msg,
            "series_id": series_id,
        }, separators=(",", ":"))

    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "get_series_observations",
            "error": error_msg,
            "series_id": series_id if series_id else None,
        }, separators=(",", ":"))
