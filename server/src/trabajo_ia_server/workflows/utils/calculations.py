"""
Statistical Calculations for Economic Data Analysis.

This module provides statistical functions for analyzing and comparing
economic time series data across multiple countries/regions.

Based on econometric best practices:
- Coefficient of Variation for convergence/divergence analysis
- Z-score method for outlier detection (2-sigma rule)
- Linear regression for trend analysis
- Inner join for temporal alignment (conservative approach)
"""
import statistics
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# TIME SERIES ALIGNMENT
# =============================================================================

def align_time_series(
    series_data: Dict[str, List[Dict[str, any]]]
) -> Tuple[List[str], Dict[str, List[float]]]:
    """
    Align multiple time series by date (inner join).

    Args:
        series_data: Dict mapping region -> list of observations
                    Each observation: {"date": "2025-01-01", "value": "123.45"}

    Returns:
        Tuple of (dates, aligned_data)
        - dates: List of common dates in chronological order
        - aligned_data: Dict mapping region -> list of values (aligned by date)

    Examples:
        >>> data = {
        ...     "usa": [{"date": "2025-01", "value": "3.0"}, {"date": "2025-02", "value": "2.9"}],
        ...     "uk": [{"date": "2025-01", "value": "2.5"}, {"date": "2025-03", "value": "2.4"}]
        ... }
        >>> dates, aligned = align_time_series(data)
        >>> dates
        ['2025-01']
        >>> aligned
        {'usa': [3.0], 'uk': [2.5]}
    """
    if not series_data:
        return [], {}

    # Build date → region → value mapping
    date_map: Dict[str, Dict[str, Optional[float]]] = {}

    for region, observations in series_data.items():
        for obs in observations:
            date = obs.get("date")
            value_str = obs.get("value", ".")

            # Parse value (FRED uses "." for missing)
            try:
                value = float(value_str) if value_str != "." else None
            except (ValueError, TypeError):
                value = None

            if date:
                if date not in date_map:
                    date_map[date] = {}
                date_map[date][region] = value

    # Inner join: keep only dates with data for ALL regions
    regions = list(series_data.keys())
    common_dates = [
        date for date, values in date_map.items()
        if all(values.get(region) is not None for region in regions)
    ]

    # Sort dates chronologically
    common_dates.sort()

    # Build aligned data structure
    aligned_data: Dict[str, List[float]] = {region: [] for region in regions}

    for date in common_dates:
        for region in regions:
            value = date_map[date][region]
            aligned_data[region].append(value)

    logger.info(
        f"Aligned {len(series_data)} series: {len(common_dates)} common dates "
        f"(from {common_dates[0] if common_dates else 'N/A'} to {common_dates[-1] if common_dates else 'N/A'})"
    )

    return common_dates, aligned_data


# =============================================================================
# STATISTICAL MEASURES
# =============================================================================

def calculate_basic_stats(values: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistical measures.

    Args:
        values: List of numeric values

    Returns:
        Dict with mean, median, std, min, max

    Examples:
        >>> calculate_basic_stats([1.0, 2.0, 3.0, 4.0, 5.0])
        {'mean': 3.0, 'median': 3.0, 'std': 1.58..., 'min': 1.0, 'max': 5.0}
    """
    if not values:
        return {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0}

    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0,
        "min": min(values),
        "max": max(values),
    }


def calculate_coefficient_of_variation(values: List[float]) -> float:
    """
    Calculate Coefficient of Variation (CV = std / mean).

    CV is used to measure convergence/divergence across regions.
    Lower CV indicates more convergence (values closer together).

    Args:
        values: List of numeric values

    Returns:
        Coefficient of Variation (0-1+ scale)

    Examples:
        >>> calculate_coefficient_of_variation([10.0, 10.5, 9.5])  # Low CV = convergent
        0.05...
        >>> calculate_coefficient_of_variation([10.0, 20.0, 5.0])  # High CV = divergent
        0.64...
    """
    if not values or len(values) < 2:
        return 0.0

    mean_val = statistics.mean(values)
    if mean_val == 0:
        return 0.0

    std_val = statistics.stdev(values)
    return std_val / abs(mean_val)


def detect_outliers(values: List[float], threshold_sigma: float = 2.0) -> List[int]:
    """
    Detect outliers using Z-score method.

    Args:
        values: List of numeric values
        threshold_sigma: Number of standard deviations for outlier threshold

    Returns:
        List of indices that are outliers

    Examples:
        >>> detect_outliers([1.0, 2.0, 3.0, 100.0])  # 100 is outlier
        [3]
        >>> detect_outliers([10.0, 11.0, 10.5, 10.2])  # No outliers
        []
    """
    if not values or len(values) < 3:
        return []

    mean_val = statistics.mean(values)
    std_val = statistics.stdev(values)

    if std_val == 0:
        return []

    outliers = []
    for i, value in enumerate(values):
        z_score = abs((value - mean_val) / std_val)
        if z_score > threshold_sigma:
            outliers.append(i)

    return outliers


# =============================================================================
# TREND ANALYSIS
# =============================================================================

def calculate_linear_trend(values: List[float]) -> Dict[str, any]:
    """
    Calculate linear trend (simple linear regression).

    Args:
        values: List of values in chronological order

    Returns:
        Dict with:
        - slope: Trend slope (positive = increasing, negative = decreasing)
        - direction: "increasing", "decreasing", or "stable"
        - velocity: Descriptive change rate

    Examples:
        >>> calculate_linear_trend([1.0, 2.0, 3.0, 4.0])
        {'slope': 1.0, 'direction': 'increasing', 'velocity': '+1.00/period'}
    """
    if not values or len(values) < 2:
        return {"slope": 0, "direction": "stable", "velocity": "0.00/period"}

    n = len(values)
    x = list(range(n))
    y = values

    # Calculate slope: (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x_i * y_i for x_i, y_i in zip(x, y))
    sum_x2 = sum(x_i ** 2 for x_i in x)

    denominator = n * sum_x2 - sum_x ** 2
    if denominator == 0:
        slope = 0
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denominator

    # Determine direction
    if abs(slope) < 0.01:  # Threshold for "stable"
        direction = "stable"
    elif slope > 0:
        direction = "increasing"
    else:
        direction = "decreasing"

    # Format velocity
    velocity = f"{slope:+.2f}/period" if slope != 0 else "0.00/period"

    return {
        "slope": slope,
        "direction": direction,
        "velocity": velocity,
    }


def calculate_change_rates(values: List[float]) -> Dict[str, Optional[float]]:
    """
    Calculate various change rates.

    Args:
        values: List of values in chronological order

    Returns:
        Dict with change_1m, change_3m, change_12m (if enough data)

    Examples:
        >>> values = [1.0, 1.1, 1.2, 1.3, 1.4]  # 5 months
        >>> changes = calculate_change_rates(values)
        >>> changes['change_1m']  # Last vs previous
        0.1
    """
    changes = {
        "change_1m": None,
        "change_3m": None,
        "change_12m": None,
    }

    if not values:
        return changes

    n = len(values)
    latest = values[-1]

    if n >= 2:
        changes["change_1m"] = latest - values[-2]

    if n >= 4:
        changes["change_3m"] = latest - values[-4]

    if n >= 13:
        changes["change_12m"] = latest - values[-13]

    return changes


# =============================================================================
# RANKING AND COMPARISON
# =============================================================================

def rank_values(data: Dict[str, float], reverse: bool = False) -> List[Dict[str, any]]:
    """
    Rank values across regions.

    Args:
        data: Dict mapping region -> value
        reverse: If True, higher values get lower rank (better)

    Returns:
        List of dicts with region, value, rank (sorted by rank)

    Examples:
        >>> rank_values({"usa": 3.0, "uk": 2.5, "euro_area": 2.2})
        [{'region': 'euro_area', 'value': 2.2, 'rank': 1},
         {'region': 'uk', 'value': 2.5, 'rank': 2},
         {'region': 'usa', 'value': 3.0, 'rank': 3}]
    """
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=reverse)

    ranked = []
    for rank, (region, value) in enumerate(sorted_items, start=1):
        ranked.append({
            "region": region,
            "value": value,
            "rank": rank,
        })

    return ranked


def calculate_spread(values: List[float]) -> float:
    """
    Calculate spread (range) of values.

    Args:
        values: List of numeric values

    Returns:
        Max - Min

    Examples:
        >>> calculate_spread([1.0, 2.0, 3.0])
        2.0
    """
    if not values:
        return 0.0
    return max(values) - min(values)


# =============================================================================
# CONVERGENCE ANALYSIS
# =============================================================================

def analyze_convergence(
    current_values: List[float],
    past_values: Optional[List[float]] = None
) -> Dict[str, any]:
    """
    Analyze convergence/divergence using Coefficient of Variation.

    Args:
        current_values: Recent values across regions
        past_values: Historical values for comparison (optional)

    Returns:
        Dict with:
        - current_cv: Current coefficient of variation
        - past_cv: Past coefficient of variation (if provided)
        - direction: "converging", "diverging", or "stable"
        - interpretation: Human-readable message

    Examples:
        >>> analyze_convergence([10.0, 10.5, 10.2], [10.0, 15.0, 5.0])
        {'current_cv': 0.024..., 'past_cv': 0.5, 'direction': 'converging', ...}
    """
    current_cv = calculate_coefficient_of_variation(current_values)

    result = {
        "current_cv": current_cv,
        "past_cv": None,
        "direction": "stable",
        "interpretation": "",
    }

    if past_values:
        past_cv = calculate_coefficient_of_variation(past_values)
        result["past_cv"] = past_cv

        cv_change = current_cv - past_cv

        if abs(cv_change) < 0.05:  # Small change threshold
            result["direction"] = "stable"
            result["interpretation"] = f"Regions remain stable (CV: {current_cv:.2f})"
        elif cv_change < 0:
            result["direction"] = "converging"
            result["interpretation"] = f"Regions converging (CV decreased from {past_cv:.2f} to {current_cv:.2f})"
        else:
            result["direction"] = "diverging"
            result["interpretation"] = f"Regions diverging (CV increased from {past_cv:.2f} to {current_cv:.2f})"
    else:
        if current_cv < 0.1:
            result["interpretation"] = "Regions tightly clustered (low variation)"
        elif current_cv < 0.3:
            result["interpretation"] = "Moderate variation across regions"
        else:
            result["interpretation"] = "High variation across regions"

    return result


__all__ = [
    "align_time_series",
    "calculate_basic_stats",
    "calculate_coefficient_of_variation",
    "detect_outliers",
    "calculate_linear_trend",
    "calculate_change_rates",
    "rank_values",
    "calculate_spread",
    "analyze_convergence",
]
