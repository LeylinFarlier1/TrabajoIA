"""
Workflow Utilities - Inflation Mappings and Statistical Calculations.
"""
from trabajo_ia_server.workflows.utils.inflation_mappings import (
    InflationSeries,
    InflationTarget,
    INFLATION_SERIES,
    INFLATION_TARGETS,
    REGION_PRESETS,
    get_inflation_series,
    get_series_id,
    get_inflation_target,
    expand_region_preset,
    validate_region,
    get_supported_regions,
    get_methodological_note,
    get_comparability_warnings,
)
from trabajo_ia_server.workflows.utils.calculations import (
    align_time_series,
    calculate_basic_stats,
    calculate_coefficient_of_variation,
    detect_outliers,
    calculate_linear_trend,
    calculate_change_rates,
    rank_values,
    calculate_spread,
    analyze_convergence,
)

__all__ = [
    # Inflation Mappings
    "InflationSeries",
    "InflationTarget",
    "INFLATION_SERIES",
    "INFLATION_TARGETS",
    "REGION_PRESETS",
    "get_inflation_series",
    "get_series_id",
    "get_inflation_target",
    "expand_region_preset",
    "validate_region",
    "get_supported_regions",
    "get_methodological_note",
    "get_comparability_warnings",
    # Statistical Calculations
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
