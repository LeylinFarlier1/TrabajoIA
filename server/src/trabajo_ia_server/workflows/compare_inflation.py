"""
Compare Inflation Across Regions Workflow.

End-to-end workflow for comparing inflation rates across multiple countries/regions.
Implements OECD/IMF/Eurostat best practices for cross-country inflation comparisons.

Key Features:
- Prioritizes HICP (harmonized) for European countries
- Uses year-over-year (YoY) % change as primary metric
- Analyzes distance from central bank inflation targets
- Detects potential base effects and methodological differences
- Provides rich comparability warnings

Best Practices (OECD/IMF/Eurostat):
- Use harmonized indices where available (HICP for Europe)
- Compare YoY rates (eliminates seasonality, consistent across countries)
- Document methodological differences (housing, quality adjustments)
- Consider central bank targets for context
- Warn about controls, subsidies, and temporary measures
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Literal, Optional
import concurrent.futures

from trabajo_ia_server.tools.fred import get_series_observations
from trabajo_ia_server.workflows.utils import (
    get_series_id,
    get_inflation_series,
    get_inflation_target,
    expand_region_preset,
    validate_region,
    get_supported_regions,
    get_methodological_note,
    get_comparability_warnings,
    align_time_series,
    calculate_basic_stats,
    rank_values,
    calculate_spread,
    analyze_convergence,
    calculate_linear_trend,
)

logger = logging.getLogger(__name__)

# Constants
MAX_REGIONS_MVP = 5  # Performance constraint for v0.2.0
INFLATION_TRANSFORMATION = "pc1"  # Year-over-year % change (FRED transformation)


def compare_inflation_across_regions(
    regions: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metric: Literal["latest", "trend", "all"] = "latest",
) -> str:
    """
    Compare inflation rates across multiple countries/regions.

    This workflow implements international best practices for cross-country
    inflation comparisons following OECD/IMF/Eurostat methodology.

    Args:
        regions: List of region codes or presets.
            Individual countries: ["usa", "euro_area", "uk", "japan", ...]
            Presets: ["g7"], ["brics"], ["north_america"], etc.
            Can mix: ["g7", "china"] expands to G7 countries + China
            Maximum: 5 regions for MVP (performance constraint)
        start_date: Start date for comparison (YYYY-MM-DD).
                   Default: 5 years ago
        end_date: End date for comparison (YYYY-MM-DD).
                 Default: latest available
        metric: Analysis focus:
            - "latest": Latest snapshot, ranking, target analysis
            - "trend": Trend analysis over period
            - "all": All metrics

    Returns:
        JSON string with:
        - comparison: Inflation rates, rankings, target analysis
        - metadata: Series used, index types, methodological notes
        - comparability_warnings: Important differences to consider
        - limitations: What this analysis does NOT do
        - suggestions: Recommendations for interpretation

    Response Format:
        {
            "tool": "compare_inflation_across_regions",
            "comparison": {
                "regions": ["usa", "euro_area", "uk"],
                "period": "2020-01-01 to 2025-11-01",
                "latest_snapshot": {
                    "date": "2025-10-01",
                    "ranking": [
                        {"region": "euro_area", "value": 2.22, "rank": 1,
                         "target": 2.0, "distance_from_target": 0.22},
                        ...
                    ]
                },
                "target_analysis": {
                    "regions_above_target": ["usa"],
                    "regions_at_target": ["euro_area", "uk"],
                    "regions_below_target": [],
                    "sticky_inflation": ["usa"]  # Persistently >3% for 6+ months
                },
                "trends": {...},
                "time_series": [...]
            },
            "metadata": {
                "series_used": [
                    {
                        "region": "usa",
                        "series_id": "CPIAUCSL",
                        "index_type": "CPI",
                        "includes_owner_housing": true,
                        "methodological_notes": "..."
                    },
                    ...
                ]
            },
            "comparability_warnings": [
                "Mixed index types: CPI, HICP. HICP excludes owner-occupied housing...",
                ...
            ],
            "limitations": [...],
            "suggestions": [...]
        }

    Examples:
        >>> compare_inflation_across_regions(["usa", "euro_area", "uk"])
        >>> compare_inflation_across_regions(["g7"], metric="all")
        >>> compare_inflation_across_regions(["eurozone_core", "eurozone_periphery"])

    Best Practices Implemented:
        - Uses HICP for European countries (harmonized, comparable)
        - Uses CPI YoY for non-European countries
        - Analyzes distance from central bank inflation targets
        - Warns about methodological differences (housing, etc.)
        - Identifies sticky inflation (persistently high)
        - Documents potential base effects

    Limitations (MVP v0.2.0):
        - Maximum 5 regions (performance constraint)
        - Year-over-year % only (no month-over-month)
        - No core/headline decomposition
        - No PPP adjustment
        - No food/energy breakdowns (yet)
        - Simple linear trends only

    See Also:
        - OECD CPI Methodology: https://www.oecd.org/sdd/prices-ppp/
        - Eurostat HICP: https://ec.europa.eu/eurostat/web/hicp
    """
    try:
        # =====================================================================
        # STEP 1: VALIDATE AND EXPAND PARAMETERS
        # =====================================================================

        # Expand region presets
        expanded_regions = expand_region_preset(regions)

        # Enforce MVP limit
        if len(expanded_regions) > MAX_REGIONS_MVP:
            logger.warning(
                f"Requested {len(expanded_regions)} regions exceeds MVP limit of {MAX_REGIONS_MVP}. "
                f"Truncating to first {MAX_REGIONS_MVP} regions."
            )
            expanded_regions = expanded_regions[:MAX_REGIONS_MVP]

        # Validate regions have mappings
        invalid_regions = [r for r in expanded_regions if not validate_region(r)]

        if invalid_regions:
            logger.warning(f"Regions without inflation data: {invalid_regions}")
            expanded_regions = [r for r in expanded_regions if r not in invalid_regions]

            if not expanded_regions:
                supported = get_supported_regions()
                error_msg = (
                    f"No valid regions found. Invalid: {invalid_regions}. "
                    f"Supported: {supported[:10]}..."
                )
                logger.error(error_msg)
                return json.dumps({
                    "tool": "compare_inflation_across_regions",
                    "error": error_msg,
                    "invalid_regions": invalid_regions,
                }, separators=(",", ":"))

        logger.info(
            f"Comparing inflation across {len(expanded_regions)} regions: {expanded_regions}"
        )

        # =====================================================================
        # STEP 2: FETCH SERIES IDS AND METADATA
        # =====================================================================

        series_mappings = {}
        series_metadata = {}

        for region in expanded_regions:
            series_id = get_series_id(region)
            series_info = get_inflation_series(region)

            if series_id and series_info:
                series_mappings[region] = series_id
                series_metadata[region] = series_info

        logger.info(f"Series IDs mapped: {series_mappings}")

        # =====================================================================
        # STEP 3: FETCH OBSERVATIONS IN PARALLEL
        # =====================================================================

        def fetch_observations(region_series):
            region, series_id = region_series
            try:
                logger.info(f"Fetching {series_id} for {region}")
                result = get_series_observations(
                    series_id=series_id,
                    observation_start=start_date,
                    observation_end=end_date,
                    units=INFLATION_TRANSFORMATION,  # pc1 = YoY %
                    limit=100000,
                )
                data = json.loads(result)
                return region, data
            except Exception as e:
                logger.error(f"Failed to fetch {series_id} for {region}: {e}")
                return region, None

        # Fetch in parallel
        series_data = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(fetch_observations, (region, series_id))
                for region, series_id in series_mappings.items()
            ]

            for future in concurrent.futures.as_completed(futures):
                region, data = future.result()
                if data and not data.get("error"):
                    series_data[region] = data.get("data", [])
                else:
                    logger.warning(f"No data for {region}")

        if not series_data:
            error_msg = "Failed to fetch data for any region"
            logger.error(error_msg)
            return json.dumps({
                "tool": "compare_inflation_across_regions",
                "error": error_msg,
            }, separators=(",", ":"))

        logger.info(f"Successfully fetched data for {len(series_data)} regions")

        # =====================================================================
        # STEP 4: ALIGN TIME SERIES
        # =====================================================================

        dates, aligned_data = align_time_series(series_data)

        if not dates:
            error_msg = "No common dates found across regions (inner join failed)"
            logger.error(error_msg)
            return json.dumps({
                "tool": "compare_inflation_across_regions",
                "error": error_msg,
                "regions": list(series_data.keys()),
            }, separators=(",", ":"))

        logger.info(f"Aligned to {len(dates)} common dates")

        # =====================================================================
        # STEP 5: CALCULATE STATISTICS AND ANALYSIS
        # =====================================================================

        # Latest snapshot
        latest_date = dates[-1]
        latest_values = {region: values[-1] for region, values in aligned_data.items()}

        # Ranking (lower inflation = better rank)
        ranking = rank_values(latest_values, reverse=False)

        # Add target analysis to ranking
        for item in ranking:
            region = item["region"]
            target_info = get_inflation_target(region)

            if target_info:
                if target_info.point_target is not None:
                    target = target_info.point_target
                elif target_info.target_range:
                    target = sum(target_info.target_range) / 2  # Midpoint
                else:
                    target = None

                if target is not None:
                    item["target"] = target
                    item["distance_from_target"] = round(item["value"] - target, 2)
                    item["target_measure"] = target_info.target_measure
                else:
                    item["target"] = None
                    item["distance_from_target"] = None
            else:
                item["target"] = None
                item["distance_from_target"] = None

        # Basic stats
        values_list = list(latest_values.values())
        stats = calculate_basic_stats(values_list)

        # Convergence analysis (compare latest vs 12 months ago if available)
        if len(dates) >= 13:
            past_values = {region: values[-13] for region, values in aligned_data.items()}
            convergence_analysis = analyze_convergence(
                values_list,
                list(past_values.values())
            )
        else:
            convergence_analysis = analyze_convergence(values_list)

        # Target analysis
        target_analysis = analyze_inflation_targets(latest_values, aligned_data, dates)

        # Trends for each region
        trends = {}
        for region, values in aligned_data.items():
            trend_info = calculate_linear_trend(values)
            trends[region] = trend_info

        # =====================================================================
        # STEP 6: FORMAT TIME SERIES FOR RESPONSE
        # =====================================================================

        # Build time series (latest 24 data points for compact response)
        time_series = []
        max_points = 24
        start_idx = max(0, len(dates) - max_points)

        for i in range(start_idx, len(dates)):
            date = dates[i]
            point = {"date": date}
            for region in aligned_data.keys():
                point[region] = aligned_data[region][i]
            time_series.append(point)

        # =====================================================================
        # STEP 7: GENERATE COMPARABILITY WARNINGS
        # =====================================================================

        comparability_warnings = get_comparability_warnings(list(series_data.keys()))

        # Add warnings about potential base effects
        base_effect_warnings = detect_base_effects(aligned_data, dates)
        comparability_warnings.extend(base_effect_warnings)

        # =====================================================================
        # STEP 8: BUILD OUTPUT
        # =====================================================================

        # Build series metadata for response
        series_used = []
        for region in series_data.keys():
            if region in series_metadata:
                meta = series_metadata[region]
                series_used.append({
                    "region": region,
                    "series_id": meta.series_id,
                    "index_type": meta.index_type,
                    "source": meta.source,
                    "includes_owner_housing": meta.includes_owner_housing,
                    "frequency": meta.frequency,
                    "methodological_notes": meta.methodological_notes,
                })

        output = {
            "tool": "compare_inflation_across_regions",
            "comparison": {
                "regions": list(series_data.keys()),
                "period": f"{dates[0]} to {dates[-1]}",
                "latest_snapshot": {
                    "date": latest_date,
                    "ranking": ranking,
                },
                "analysis": {
                    "highest": ranking[-1],
                    "lowest": ranking[0],
                    "spread": calculate_spread(values_list),
                    "mean": round(stats["mean"], 2),
                    "std": round(stats["std"], 2),
                    "convergence": convergence_analysis["interpretation"],
                },
                "target_analysis": target_analysis,
                "trends": trends,
                "time_series": time_series,
            },
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "transformation": "Year-over-year % change (pc1)",
                "series_used": series_used,
                "data_points": len(dates),
                "time_series_points_returned": len(time_series),
                "alignment_method": "inner_join",
                "regions_requested": regions,
                "regions_expanded": expanded_regions,
                "regions_with_data": list(series_data.keys()),
            },
            "comparability_warnings": comparability_warnings,
            "limitations": [
                "Comparison assumes series are methodologically comparable (see warnings)",
                "HICP (Europe) excludes owner-occupied housing; CPI (others) typically includes it",
                "No PPP (Purchasing Power Parity) adjustment - nominal comparison only",
                "Inner join may reduce data if update frequencies differ (e.g., AUS/NZ quarterly)",
                f"Maximum {MAX_REGIONS_MVP} regions for MVP (performance constraint)",
                "Year-over-year rates only (no month-over-month)",
                "No core/headline decomposition (total inflation only)",
                "No food/energy component breakdown",
                "Simple linear trends (may miss structural breaks)",
                "No statistical significance tests",
            ],
            "suggestions": [
                "Small differences (<0.5pp) often reflect measurement differences, not economic reality",
                "For European countries, HICP is harmonized and most comparable",
                "Check 'comparability_warnings' for methodological differences",
                "Distance from central bank target provides policy context",
                "Sticky inflation (>3% for 6+ months) may indicate structural pressures",
                "Consider food/energy prices separately (not available in this tool yet)",
                "For PPP-adjusted comparisons, use World Bank ICP data externally",
            ],
        }

        logger.info(
            f"Comparison complete: inflation across {len(series_data)} regions, "
            f"{len(dates)} aligned data points"
        )

        return json.dumps(output, separators=(",", ":"), default=str)

    except Exception as e:
        error_msg = f"Unexpected error in compare_inflation_across_regions: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "compare_inflation_across_regions",
            "error": error_msg,
            "regions": regions if regions else None,
        }, separators=(",", ":"))


def analyze_inflation_targets(
    latest_values: Dict[str, float],
    aligned_data: Dict[str, List[float]],
    dates: List[str],
) -> Dict:
    """
    Analyze inflation relative to central bank targets.

    Args:
        latest_values: Latest inflation value per region
        aligned_data: Full time series per region
        dates: Dates for time series

    Returns:
        Dict with target analysis
    """
    regions_above_target = []
    regions_at_target = []
    regions_below_target = []
    sticky_inflation = []

    AT_TARGET_TOLERANCE = 0.5  # Within 0.5pp of target = "at target"
    STICKY_THRESHOLD = 3.0  # >3% for extended period = "sticky"
    STICKY_MONTHS = 6  # 6+ months

    for region, current_inflation in latest_values.items():
        target_info = get_inflation_target(region)

        if not target_info:
            continue

        # Determine target
        if target_info.point_target is not None:
            target = target_info.point_target
        elif target_info.target_range:
            target = sum(target_info.target_range) / 2
        else:
            continue

        # Classify relative to target
        distance = current_inflation - target

        if abs(distance) <= AT_TARGET_TOLERANCE:
            regions_at_target.append(region)
        elif distance > AT_TARGET_TOLERANCE:
            regions_above_target.append(region)
        else:
            regions_below_target.append(region)

        # Check for sticky inflation (persistently high)
        if len(aligned_data[region]) >= STICKY_MONTHS:
            recent_values = aligned_data[region][-STICKY_MONTHS:]
            if all(v > STICKY_THRESHOLD for v in recent_values):
                sticky_inflation.append(region)

    return {
        "regions_above_target": regions_above_target,
        "regions_at_target": regions_at_target,
        "regions_below_target": regions_below_target,
        "sticky_inflation": sticky_inflation,
        "interpretation": (
            f"{len(regions_above_target)} region(s) above target, "
            f"{len(regions_at_target)} at target, "
            f"{len(regions_below_target)} below target. "
            f"Sticky inflation detected in: {', '.join(sticky_inflation) if sticky_inflation else 'none'}."
        )
    }


def detect_base_effects(
    aligned_data: Dict[str, List[float]],
    dates: List[str],
) -> List[str]:
    """
    Detect potential base effects in inflation data.

    Base effects occur when YoY inflation is distorted by unusually high/low
    prices in the comparison period (12 months ago).

    Args:
        aligned_data: Time series data per region
        dates: Dates

    Returns:
        List of warning strings
    """
    warnings = []

    # Look for sharp drops followed by sharp rises (classic base effect pattern)
    for region, values in aligned_data.items():
        if len(values) < 13:
            continue

        # Check last 12 months for base effect signature
        # (sharp drop in inflation followed by sharp rise)
        for i in range(len(values) - 12, len(values) - 1):
            if i < 1:
                continue

            # Drop of >2pp followed by rise of >2pp = potential base effect
            drop = values[i] - values[i-1]
            rise = values[i+1] - values[i]

            if drop < -2.0 and rise > 2.0:
                date = dates[i] if i < len(dates) else "unknown"
                warnings.append(
                    f"{region}: Potential base effect detected around {date}. "
                    f"Sharp drop ({drop:.1f}pp) followed by sharp rise ({rise:.1f}pp). "
                    "This may reflect temporary measures (VAT changes, subsidies) unwinding."
                )
                break  # One warning per region sufficient

    return warnings


__all__ = ["compare_inflation_across_regions"]
