"""
Validation utilities for Trabajo IA Server.

Provides validators for common data formats and inputs.
"""
from datetime import datetime
from typing import Optional


def validate_date_format(date_str: Optional[str]) -> bool:
    """
    Validate if a string is in YYYY-MM-DD format.

    Args:
        date_str: Date string to validate

    Returns:
        True if valid format or None, False otherwise
    """
    if date_str is None:
        return True

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_series_id(series_id: str) -> bool:
    """
    Validate FRED series ID format.

    Args:
        series_id: FRED series identifier

    Returns:
        True if valid, False otherwise
    """
    if not series_id:
        return False

    # FRED series IDs are typically uppercase alphanumeric
    return series_id.replace("_", "").isalnum()
