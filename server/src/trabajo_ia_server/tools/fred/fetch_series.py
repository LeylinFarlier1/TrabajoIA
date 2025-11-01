"""
FRED Series Data Fetching Tool.

Provides functionality to fetch historical observations from FRED API.
"""
import json
from datetime import datetime
from typing import Optional
from fredapi import Fred
import pandas as pd

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.logger import setup_logger
from trabajo_ia_server.utils.validators import validate_date_format, validate_series_id

logger = setup_logger(__name__)


def fetch_series_observations(
    series_id: str,
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None
) -> str:
    """
    Fetch historical observations for a FRED series.

    Args:
        series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
        observation_start: Start date in 'YYYY-MM-DD' format (optional)
        observation_end: End date in 'YYYY-MM-DD' format (optional)

    Returns:
        JSON string with historical data and metadata

    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if not validate_series_id(series_id):
        error_msg = f"Invalid series ID format: {series_id}"
        logger.error(error_msg)
        return json.dumps({
            "error": error_msg,
            "series_id": series_id,
            "tool": "fetch_series_observations"
        })

    if not validate_date_format(observation_start):
        error_msg = f"Invalid start date format: {observation_start}. Use YYYY-MM-DD"
        logger.error(error_msg)
        return json.dumps({
            "error": error_msg,
            "series_id": series_id,
            "tool": "fetch_series_observations"
        })

    if not validate_date_format(observation_end):
        error_msg = f"Invalid end date format: {observation_end}. Use YYYY-MM-DD"
        logger.error(error_msg)
        return json.dumps({
            "error": error_msg,
            "series_id": series_id,
            "tool": "fetch_series_observations"
        })

    try:
        # Get API key from config
        api_key = config.get_fred_api_key()
        fred = Fred(api_key)

        # Fetch data from FRED
        df = fred.get_series(
            series_id,
            observation_start=observation_start or "1776-07-04",  # FRED default start
            observation_end=observation_end
        )

        # Process data with pandas
        df = pd.Series(df).dropna().reset_index()
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"])

        # Convert to list of records
        observations = df.to_dict("records")

        # Build response with data and metadata
        output = {
            "tool": "fetch_series_observations",
            "series_id": series_id,
            "data": observations,
            "metadata": {
                "fetch_date": datetime.now().isoformat(),
                "observation_start": observation_start or "all",
                "observation_end": observation_end or "latest",
                "total_count": len(observations),
                "date_range": {
                    "start": df["date"].min().isoformat() if not df.empty else None,
                    "end": df["date"].max().isoformat() if not df.empty else None
                }
            }
        }

        logger.info(f"Successfully fetched {len(observations)} observations for {series_id}")
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_msg = f"Error fetching observations for {series_id}: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "error": str(e),
            "series_id": series_id,
            "tool": "fetch_series_observations"
        })
