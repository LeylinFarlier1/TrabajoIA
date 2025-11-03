"""
Inflation Series Mappings and Metadata for Cross-Country Comparisons.

This module provides curated mappings for inflation data following international
best practices from OECD, IMF, Eurostat, and central banking standards.

Key Principles (based on OECD/IMF/Eurostat methodology):
- Prioritize HICP (Harmonized Index of Consumer Prices) for European countries
- Use year-over-year (YoY) % change as primary metric (eliminates seasonality)
- Document methodological differences (owner-occupied housing, etc.)
- Include central bank inflation targets for context
- Transparent about comparability limitations

References:
- OECD CPI Methodology: https://www.oecd.org/sdd/prices-ppp/
- Eurostat HICP: https://ec.europa.eu/eurostat/web/hicp
- IMF IFS Metadata: https://data.imf.org/
- BIS Central Bank Policy Rates: https://www.bis.org/statistics/
"""
from typing import Dict, List, Optional, Literal
from datetime import datetime


# =============================================================================
# INFLATION SERIES MAPPINGS
# =============================================================================

class InflationSeries:
    """Metadata for an inflation series."""

    def __init__(
        self,
        series_id: str,
        index_type: Literal["CPI", "HICP", "PCE"],
        source: str,
        verified_date: str,
        frequency: str = "Monthly",
        includes_owner_housing: bool = True,
        methodological_notes: Optional[str] = None,
    ):
        self.series_id = series_id
        self.index_type = index_type
        self.source = source
        self.verified_date = verified_date
        self.frequency = frequency
        self.includes_owner_housing = includes_owner_housing
        self.methodological_notes = methodological_notes


# Primary inflation series by country/region
# Priority: HICP for Europe (harmonized), CPI for others
INFLATION_SERIES: Dict[str, InflationSeries] = {
    # =========================================================================
    # NORTH AMERICA
    # =========================================================================
    "usa": InflationSeries(
        series_id="CPIAUCSL",
        index_type="CPI",
        source="U.S. Bureau of Labor Statistics",
        verified_date="2025-11-02",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI-U (All Urban Consumers). Includes owner-occupied housing via "
            "Owners' Equivalent Rent (~24% of basket). Uses geometric mean for "
            "elementary aggregates. Laspeyres-type index with biennial weight updates."
        )
    ),

    "canada": InflationSeries(
        series_id="CPALCY01CAM661N",
        index_type="CPI",
        source="OECD via Statistics Canada",
        verified_date="2025-11-02",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI All Items YoY. Includes mortgage interest costs (unique among "
            "developed countries). When interest rates rise, Canadian CPI shows higher "
            "inflation than other countries due to this methodological difference."
        )
    ),

    "mexico": InflationSeries(
        series_id="CPALCY01MXM661N",
        index_type="CPI",
        source="OECD via INEGI",
        verified_date="2025-11-02",
        frequency="Monthly",
        includes_owner_housing=True,
    ),

    # =========================================================================
    # EUROPE (HICP - Harmonized for Comparability)
    # =========================================================================
    "euro_area": InflationSeries(
        series_id="CP0000EZ19M086NEST",
        index_type="HICP",
        source="Eurostat",
        verified_date="2025-11-02",
        frequency="Monthly",
        includes_owner_housing=False,
        methodological_notes=(
            "HICP All Items, Not Seasonally Adjusted. EXCLUDES owner-occupied housing "
            "costs. Designed specifically for cross-country comparisons within EU. "
            "Uses arithmetic mean for elementary aggregates."
        )
    ),

    "germany": InflationSeries(
        series_id="DEUCPIHICMINMEI",
        index_type="HICP",
        source="OECD via Destatis (Eurostat HICP)",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=False,
        methodological_notes=(
            "HICP All Items, Index 2015=100. Harmonized methodology for EU comparisons. "
            "Notable: Germany had temporary VAT reduction in 2020 creating base effects in 2021. "
            "More extensive quality adjustments for electronics than some other countries. "
            "Data available through March 2025."
        )
    ),

    "france": InflationSeries(
        series_id="FRACPIHICMINMEI",
        index_type="HICP",
        source="OECD via INSEE (Eurostat HICP)",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=False,
        methodological_notes=(
            "HICP All Items, Index 2015=100. Harmonized methodology for EU comparisons. "
            "France implemented electricity price caps in 2021-2022, temporarily suppressing "
            "measured inflation relative to countries without such controls. "
            "Data available through April 2025."
        )
    ),

    "uk": InflationSeries(
        series_id="GBRCPIHICMINMEI",
        index_type="HICP",
        source="OECD via ONS (Office for National Statistics)",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=False,
        methodological_notes=(
            "HICP All Items, Index 2015=100. Harmonized methodology for comparisons. "
            "CPIH (CPI including owner-occupiers' housing costs) is UK's preferred measure, "
            "but this HICP series used for international comparability. "
            "Post-Brexit, UK continues to produce comparable data. Data available through March 2025."
        )
    ),

    "italy": InflationSeries(
        series_id="ITACPIHICMINMEI",
        index_type="HICP",
        source="OECD via ISTAT (Eurostat HICP)",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=False,
        methodological_notes=(
            "HICP All Items, Index 2015=100. Harmonized methodology for EU comparisons. "
            "Data available through April 2025."
        )
    ),

    "spain": InflationSeries(
        series_id="CP0000ESM086NEST",
        index_type="HICP",
        source="Eurostat",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=False,
        methodological_notes=(
            "HICP All Items, Index 2015=100, Not Seasonally Adjusted. Harmonized methodology for EU comparisons. "
            "Spain implemented natural gas price caps in 2022, temporarily lowering "
            "measured energy inflation relative to other EU countries. "
            "Data available through September 2025."
        )
    ),

    "netherlands": InflationSeries(
        series_id="CP0000NLM086NEST",
        index_type="HICP",
        source="Eurostat",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=False,
        methodological_notes=(
            "HICP All Items, Index 2015=100, Not Seasonally Adjusted. Harmonized methodology for EU comparisons. "
            "Data available through September 2025."
        )
    ),

    "switzerland": InflationSeries(
        series_id="CHECPIALLMINMEI",
        index_type="CPI",
        source="OECD via Swiss Federal Statistical Office",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI All Items, Index 2015=100. "
            "Switzerland not in EU, so uses national CPI (not HICP). Historically "
            "very low inflation due to strong franc and price stability culture. "
            "Data available through April 2025."
        )
    ),

    "sweden": InflationSeries(
        series_id="CP0000SEM086NEST",
        index_type="HICP",
        source="Eurostat",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=False,
        methodological_notes=(
            "HICP All Items, Index 2015=100, Not Seasonally Adjusted. Harmonized methodology for EU comparisons. "
            "Sweden performs more extensive quality adjustments for electronics than "
            "many other countries, potentially lowering measured inflation in those "
            "categories (Riksbank study 2023). Data available through September 2025."
        )
    ),

    "norway": InflationSeries(
        series_id="NORCPIALLMINMEI",
        index_type="CPI",
        source="OECD via Statistics Norway",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI All Items, Index 2015=100. "
            "Norway not in EU, uses national CPI. As major oil exporter, different "
            "exposure to energy price shocks than net importers. "
            "Data available through April 2025."
        )
    ),

    # =========================================================================
    # ASIA-PACIFIC
    # =========================================================================
    "japan": InflationSeries(
        series_id="JPNCPIALLMINMEI",
        index_type="CPI",
        source="OECD via Statistics Japan",
        verified_date="2025-11-02",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "Japan CPI All Items. Historically low inflation/deflation environment "
            "until recent years. BoJ targets 2% but measured differently than Fed/ECB."
        )
    ),

    "china": InflationSeries(
        series_id="CHNCPIALLMINMEI",
        index_type="CPI",
        source="OECD via National Bureau of Statistics of China",
        verified_date="2025-11-02",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI methodology differs from Western countries. Food has higher weight "
            "(~30% vs ~15% in developed markets). Housing measured differently."
        )
    ),

    "south_korea": InflationSeries(
        series_id="KORCPIALLMINMEI",
        index_type="CPI",
        source="OECD via Statistics Korea",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI All Items, Index 2015=100. "
            "Data available through November 2023."
        )
    ),

    "australia": InflationSeries(
        series_id="CPALTT01AUQ657N",
        index_type="CPI",
        source="OECD via Australian Bureau of Statistics",
        verified_date="2025-11-03",
        frequency="Quarterly",
        includes_owner_housing=True,
        methodological_notes=(
            "OECD CPI All Items - Growth rate previous period. "
            "QUARTERLY frequency (not monthly). RBA targets 2-3% inflation range "
            "(wider than most other central banks' 2% point target). "
            "Data available through October 2023."
        )
    ),

    "new_zealand": InflationSeries(
        series_id="CPALTT01NZQ657N",
        index_type="CPI",
        source="OECD via Stats NZ",
        verified_date="2025-11-03",
        frequency="Quarterly",
        includes_owner_housing=True,
        methodological_notes=(
            "OECD CPI All Items - Growth rate previous period. "
            "QUARTERLY frequency (not monthly). "
            "Data available through October 2023."
        )
    ),

    "india": InflationSeries(
        series_id="INDCPIALLMINMEI",
        index_type="CPI",
        source="OECD via Reserve Bank of India",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI All Items, Index 2015=100. "
            "Food and beverages represent ~46% of CPI basket (much higher than "
            "developed countries), making Indian CPI more volatile and sensitive to "
            "agricultural shocks. Data available through March 2025."
        )
    ),

    # =========================================================================
    # LATIN AMERICA & OTHER EMERGING
    # =========================================================================
    "brazil": InflationSeries(
        series_id="BRACPIALLMINMEI",
        index_type="CPI",
        source="OECD via IBGE",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI All Items, Index 2015=100. "
            "Brazil Central Bank targets 3% inflation with ±1.5% tolerance band. "
            "History of high inflation affects wage/price indexation behavior. "
            "Data available through April 2025."
        )
    ),

    "russia": InflationSeries(
        series_id="RUSCPIALLMINMEI",
        index_type="CPI",
        source="OECD via Rosstat",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI All Items, Index 2015=100. "
            "Data availability and reliability concerns post-2022. Geopolitical "
            "factors and sanctions affect price dynamics distinctly. "
            "Data available through March 2022 only."
        )
    ),

    "south_africa": InflationSeries(
        series_id="ZAFCPIALLMINMEI",
        index_type="CPI",
        source="OECD via Statistics South Africa",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI All Items, Index 2015=100. "
            "SARB targets 3-6% inflation range (midpoint 4.5%). Wider band than "
            "most developed economy central banks. Data available through January 2025."
        )
    ),

    "turkey": InflationSeries(
        series_id="TURCPIALLMINMEI",
        index_type="CPI",
        source="OECD via TurkStat",
        verified_date="2025-11-03",
        frequency="Monthly",
        includes_owner_housing=True,
        methodological_notes=(
            "CPI All Items, Index 2015=100. "
            "Historically high and volatile inflation. Unique monetary policy "
            "approach affects inflation dynamics. Lira depreciation major factor. "
            "Data available through April 2025."
        )
    ),
}


# =============================================================================
# CENTRAL BANK INFLATION TARGETS
# =============================================================================

class InflationTarget:
    """Central bank inflation targeting regime."""

    def __init__(
        self,
        point_target: Optional[float] = None,
        target_range: Optional[tuple] = None,
        target_measure: str = "CPI YoY",
        regime_start: Optional[int] = None,
        notes: Optional[str] = None,
    ):
        self.point_target = point_target
        self.target_range = target_range
        self.target_measure = target_measure
        self.regime_start = regime_start
        self.notes = notes


INFLATION_TARGETS: Dict[str, InflationTarget] = {
    "usa": InflationTarget(
        point_target=2.0,
        target_measure="PCE YoY (not CPI)",
        regime_start=2012,
        notes=(
            "Fed targets 2% PCE inflation (not CPI). PCE typically runs 0.3-0.5pp "
            "lower than CPI due to methodological differences. Flexible average "
            "inflation targeting since 2020."
        )
    ),
    "canada": InflationTarget(
        point_target=2.0,
        target_range=(1.0, 3.0),
        regime_start=1991,
        notes="Midpoint of 1-3% range. One of earliest inflation targeters."
    ),
    "mexico": InflationTarget(
        point_target=3.0,
        target_range=(2.0, 4.0),
        regime_start=2001,
        notes="Higher target than developed markets, reflecting emerging market status."
    ),
    "euro_area": InflationTarget(
        point_target=2.0,
        target_measure="HICP YoY",
        regime_start=1999,
        notes=(
            "ECB targets 2% HICP symmetric target (revised 2021 from 'below but "
            "close to 2%'). Measured by HICP, not national CPIs."
        )
    ),
    "germany": InflationTarget(
        point_target=2.0,
        target_measure="HICP YoY (Euro area)",
        notes="As Euro area member, subject to ECB's 2% HICP target."
    ),
    "france": InflationTarget(
        point_target=2.0,
        target_measure="HICP YoY (Euro area)",
        notes="As Euro area member, subject to ECB's 2% HICP target."
    ),
    "uk": InflationTarget(
        point_target=2.0,
        target_measure="CPI YoY (HICP equivalent)",
        regime_start=1992,
        notes=(
            "Bank of England targets 2% CPI (which is similar to HICP). "
            "Governor writes letter if inflation deviates ±1pp from target."
        )
    ),
    "italy": InflationTarget(
        point_target=2.0,
        target_measure="HICP YoY (Euro area)",
        notes="As Euro area member, subject to ECB's 2% HICP target."
    ),
    "spain": InflationTarget(
        point_target=2.0,
        target_measure="HICP YoY (Euro area)",
        notes="As Euro area member, subject to ECB's 2% HICP target."
    ),
    "netherlands": InflationTarget(
        point_target=2.0,
        target_measure="HICP YoY (Euro area)",
        notes="As Euro area member, subject to ECB's 2% HICP target."
    ),
    "switzerland": InflationTarget(
        point_target=None,
        target_range=(0.0, 2.0),
        target_measure="CPI YoY",
        regime_start=2000,
        notes=(
            "SNB defines price stability as CPI inflation below 2%. Unique among "
            "major central banks in targeting a range starting at 0%."
        )
    ),
    "sweden": InflationTarget(
        point_target=2.0,
        target_measure="HICP YoY",
        regime_start=1993,
        notes="Riksbank targets 2% CPI/HICP. Flexible inflation targeting."
    ),
    "norway": InflationTarget(
        point_target=2.0,
        regime_start=2001,
        notes="Norges Bank targets 2% CPI over time."
    ),
    "japan": InflationTarget(
        point_target=2.0,
        regime_start=2013,
        notes=(
            "BoJ adopted 2% target in 2013 after decades of deflation. Struggled "
            "to achieve target until recent years."
        )
    ),
    "china": InflationTarget(
        point_target=3.0,
        notes=(
            "Implicit ~3% target (varies yearly). Not formal inflation targeting "
            "regime like Western central banks. Multiple policy objectives."
        )
    ),
    "south_korea": InflationTarget(
        point_target=2.0,
        regime_start=1998,
        notes="BoK targets 2% CPI over medium term (2-year ahead)."
    ),
    "australia": InflationTarget(
        target_range=(2.0, 3.0),
        regime_start=1993,
        notes=(
            "RBA targets 2-3% CPI on average over time. Notable for being a range "
            "rather than point target."
        )
    ),
    "new_zealand": InflationTarget(
        point_target=2.0,
        target_range=(1.0, 3.0),
        regime_start=1990,
        notes=(
            "First country to adopt formal inflation targeting (1990). "
            "RBNZ targets 2% midpoint of 1-3% range."
        )
    ),
    "india": InflationTarget(
        point_target=4.0,
        target_range=(2.0, 6.0),
        regime_start=2016,
        notes=(
            "RBI targets 4% CPI with +/-2% tolerance band. Higher target reflects "
            "emerging market characteristics."
        )
    ),
    "brazil": InflationTarget(
        point_target=3.0,
        target_range=(1.5, 4.5),
        regime_start=1999,
        notes=(
            "Banco Central do Brasil targets 3% with ±1.5% tolerance band. "
            "Target reviewed annually by National Monetary Council."
        )
    ),
    "russia": InflationTarget(
        point_target=4.0,
        regime_start=2014,
        notes=(
            "CBR targets 4% CPI. Challenging environment post-2022 due to "
            "sanctions and geopolitical factors."
        )
    ),
    "south_africa": InflationTarget(
        target_range=(3.0, 6.0),
        regime_start=2000,
        notes=(
            "SARB targets 3-6% CPI range (midpoint 4.5%). Wider band than "
            "most developed economies."
        )
    ),
    "turkey": InflationTarget(
        point_target=5.0,
        regime_start=2006,
        notes=(
            "Official target 5% but frequently missed. Unique monetary policy "
            "approach with persistent high inflation environment."
        )
    ),
}


# =============================================================================
# REGION PRESETS
# =============================================================================

REGION_PRESETS: Dict[str, List[str]] = {
    "g7": ["usa", "canada", "uk", "germany", "france", "italy", "japan"],
    "g20_developed": ["usa", "canada", "uk", "germany", "france", "italy", "japan", "australia", "south_korea"],
    "g20_emerging": ["china", "india", "brazil", "russia", "south_africa", "mexico", "turkey"],
    "eurozone_core": ["germany", "france", "netherlands"],
    "eurozone_periphery": ["italy", "spain"],
    "nordic": ["sweden", "norway"],
    "brics": ["brazil", "russia", "india", "china", "south_africa"],
    "north_america": ["usa", "canada", "mexico"],
    "asia_pacific": ["japan", "china", "south_korea", "australia", "new_zealand", "india"],
    "europe_major": ["uk", "germany", "france", "italy", "spain"],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_inflation_series(region: str) -> Optional[InflationSeries]:
    """
    Get inflation series metadata for a region.

    Args:
        region: Region code (e.g., "usa", "euro_area")

    Returns:
        InflationSeries object or None if not found
    """
    return INFLATION_SERIES.get(region)


def get_series_id(region: str) -> Optional[str]:
    """
    Get FRED series ID for a region's inflation data.

    Args:
        region: Region code

    Returns:
        FRED series ID or None
    """
    series = get_inflation_series(region)
    return series.series_id if series else None


def get_inflation_target(region: str) -> Optional[InflationTarget]:
    """
    Get central bank inflation target for a region.

    Args:
        region: Region code

    Returns:
        InflationTarget object or None
    """
    return INFLATION_TARGETS.get(region)


def expand_region_preset(regions: List[str]) -> List[str]:
    """
    Expand region presets into individual region codes.

    Args:
        regions: List of region codes and/or presets

    Returns:
        List of expanded individual region codes (duplicates removed)

    Examples:
        >>> expand_region_preset(["g7"])
        ['usa', 'canada', 'uk', 'germany', 'france', 'italy', 'japan']
        >>> expand_region_preset(["usa", "g7"])  # Removes duplicate 'usa'
        ['usa', 'canada', 'uk', 'germany', 'france', 'italy', 'japan']
    """
    expanded = []
    for region in regions:
        if region in REGION_PRESETS:
            expanded.extend(REGION_PRESETS[region])
        else:
            expanded.append(region)

    # Remove duplicates while preserving order
    seen = set()
    result = []
    for item in expanded:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def validate_region(region: str) -> bool:
    """
    Check if a region has inflation data mapping.

    Args:
        region: Region code

    Returns:
        True if mapping exists, False otherwise
    """
    return region in INFLATION_SERIES


def get_supported_regions() -> List[str]:
    """
    Get list of all supported regions.

    Returns:
        List of region codes with inflation data
    """
    return list(INFLATION_SERIES.keys())


def get_methodological_note(region: str) -> Optional[str]:
    """
    Get methodological notes for a region's inflation measure.

    Useful for understanding comparability issues.

    Args:
        region: Region code

    Returns:
        Methodological notes string or None
    """
    series = get_inflation_series(region)
    return series.methodological_notes if series else None


def get_comparability_warnings(regions: List[str]) -> List[str]:
    """
    Generate comparability warnings for a set of regions.

    Identifies methodological differences that may affect comparison.

    Args:
        regions: List of region codes to compare

    Returns:
        List of warning strings
    """
    warnings = []

    # Check for mix of HICP and CPI
    index_types = set()
    housing_coverage = {}

    for region in regions:
        series = get_inflation_series(region)
        if not series:
            continue

        index_types.add(series.index_type)
        housing_coverage[region] = series.includes_owner_housing

    # Warn about index type mix
    if len(index_types) > 1:
        warnings.append(
            f"Mixed index types: {', '.join(sorted(index_types))}. "
            "HICP (Europe) excludes owner-occupied housing while CPI (others) typically includes it."
        )

    # Warn about housing coverage differences
    housing_included = [r for r, inc in housing_coverage.items() if inc]
    housing_excluded = [r for r, inc in housing_coverage.items() if not inc]

    if housing_included and housing_excluded:
        warnings.append(
            f"Owner-occupied housing: included in {', '.join(housing_included[:3])}... "
            f"but excluded in {', '.join(housing_excluded[:3])}... "
            "This represents ~20-25% of CPI basket and can create material differences."
        )

    # Warn about frequency differences
    frequencies = {}
    for region in regions:
        series = get_inflation_series(region)
        if series:
            frequencies[region] = series.frequency

    if len(set(frequencies.values())) > 1:
        quarterly = [r for r, f in frequencies.items() if f == "Quarterly"]
        if quarterly:
            warnings.append(
                f"Frequency mismatch: {', '.join(quarterly)} report QUARTERLY data "
                "while others are MONTHLY. Quarterly data less granular for recent trends."
            )

    # Add Canada-specific warning if present
    if "canada" in regions:
        warnings.append(
            "Canada includes mortgage interest costs in CPI (unique methodology). "
            "When interest rates rise, Canada shows higher inflation than other countries "
            "due to this technical difference."
        )

    return warnings


__all__ = [
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
]
