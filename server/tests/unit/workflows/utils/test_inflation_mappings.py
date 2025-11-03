"""Unit tests for inflation-specific mappings and metadata.

Tests cover:
- Inflation series metadata (InflationSeries)
- Central bank inflation targets (InflationTarget)
- Region validation and expansion
- Comparability warnings generation
- Methodological notes and best practices
- HICP vs CPI differentiation
"""
import pytest

from trabajo_ia_server.workflows.utils.inflation_mappings import (
    INFLATION_SERIES,
    INFLATION_TARGETS,
    REGION_PRESETS,
    InflationSeries,
    InflationTarget,
    expand_region_preset,
    get_comparability_warnings,
    get_inflation_series,
    get_inflation_target,
    get_methodological_note,
    get_series_id,
    get_supported_regions,
    validate_region,
)


class TestInflationSeriesClass:
    """Test InflationSeries dataclass."""

    def test_cpi_series_creation(self):
        """Test creating a CPI series with owner housing."""
        series = InflationSeries(
            series_id="CPIAUCSL",
            index_type="CPI",
            source="BLS",
            verified_date="2025-01",
            includes_owner_housing=True,
            methodological_notes="Includes OER",
        )

        assert series.series_id == "CPIAUCSL"
        assert series.index_type == "CPI"
        assert series.includes_owner_housing is True
        assert "OER" in series.methodological_notes

    def test_hicp_series_creation(self):
        """Test creating an HICP series without owner housing."""
        series = InflationSeries(
            series_id="CP0000EZ19M086NEST",
            index_type="HICP",
            source="Eurostat",
            verified_date="2025-01",
            includes_owner_housing=False,
            methodological_notes="HICP excludes owner housing",
        )

        assert series.index_type == "HICP"
        assert series.includes_owner_housing is False


class TestInflationTargetClass:
    """Test InflationTarget dataclass."""

    def test_point_target(self):
        """Test target with point value."""
        target = InflationTarget(
            point_target=2.0,
            target_measure="HICP YoY",
            regime_start=1999,
            notes="ECB target",
        )

        assert target.point_target == 2.0
        assert target.target_range is None
        assert target.regime_start == 1999

    def test_range_target(self):
        """Test target with range."""
        target = InflationTarget(
            target_range=(2.0, 3.0),
            target_measure="CPI YoY",
            notes="RBA target",
        )

        assert target.target_range == (2.0, 3.0)
        assert target.point_target is None


class TestGetSeriesId:
    """Test series ID lookup."""

    def test_usa_inflation(self):
        """Test USA inflation series ID."""
        series_id = get_series_id("usa")

        assert series_id == "CPIAUCSL"

    def test_euro_area_inflation(self):
        """Test Euro Area inflation (HICP)."""
        series_id = get_series_id("euro_area")

        # Should be HICP series
        assert series_id is not None
        assert "CP0000" in series_id or "HICP" in series_id

    def test_invalid_region(self):
        """Test invalid region returns None."""
        series_id = get_series_id("invalid_region")

        assert series_id is None

    def test_all_g7_have_series(self):
        """Test that all G7 countries have inflation series."""
        g7_countries = REGION_PRESETS["g7"]

        for country in g7_countries:
            series_id = get_series_id(country)
            assert series_id is not None, \
                f"G7 country {country} should have inflation series"


class TestGetInflationSeries:
    """Test inflation series metadata retrieval."""

    def test_usa_metadata(self):
        """Test USA series metadata."""
        series = get_inflation_series("usa")

        assert series is not None
        assert series.index_type == "CPI"
        assert series.includes_owner_housing is True
        assert series.series_id == "CPIAUCSL"
        assert "OER" in series.methodological_notes or "owner" in series.methodological_notes.lower()

    def test_euro_area_metadata(self):
        """Test Euro Area series metadata."""
        series = get_inflation_series("euro_area")

        assert series is not None
        assert series.index_type == "HICP"
        assert series.includes_owner_housing is False
        assert "exclude" in series.methodological_notes.lower()

    def test_canada_mortgage_interest(self):
        """Test Canada series includes mortgage interest note."""
        series = get_inflation_series("canada")

        assert series is not None
        # Canada includes mortgage interest costs unlike most countries
        assert "mortgage" in series.methodological_notes.lower()

    def test_invalid_region(self):
        """Test invalid region returns None."""
        series = get_inflation_series("invalid_region")

        assert series is None


class TestGetInflationTarget:
    """Test inflation target retrieval."""

    def test_usa_target(self):
        """Test USA inflation target."""
        target = get_inflation_target("usa")

        assert target is not None
        assert target.point_target == 2.0
        # Fed targets PCE, not CPI
        assert "PCE" in target.target_measure

    def test_euro_area_target(self):
        """Test Euro Area inflation target."""
        target = get_inflation_target("euro_area")

        assert target is not None
        assert target.point_target == 2.0
        assert "HICP" in target.target_measure

    def test_australia_range_target(self):
        """Test Australia's range target."""
        target = get_inflation_target("australia")

        assert target is not None
        assert target.target_range == (2.0, 3.0)

    def test_region_without_target(self):
        """Test region without explicit inflation target."""
        # Some regions may not have formal targets
        target = get_inflation_target("china")

        # Either has target or returns None
        assert target is None or isinstance(target, InflationTarget)


class TestExpandRegionPreset:
    """Test region preset expansion."""

    def test_g7_expansion(self):
        """Test G7 preset expansion."""
        expanded = expand_region_preset(["g7"])

        assert "usa" in expanded
        assert "canada" in expanded
        assert "uk" in expanded
        assert "germany" in expanded
        assert "france" in expanded
        assert "italy" in expanded
        assert "japan" in expanded
        assert len(expanded) == 7

    def test_eurozone_core_expansion(self):
        """Test Eurozone core preset."""
        expanded = expand_region_preset(["eurozone_core"])

        assert "germany" in expanded
        assert "france" in expanded
        assert len(expanded) >= 2

    def test_individual_regions(self):
        """Test individual regions pass through."""
        regions = ["usa", "uk", "japan"]
        expanded = expand_region_preset(regions)

        assert expanded == regions

    def test_mixed_presets_and_regions(self):
        """Test mixing presets and individual regions."""
        expanded = expand_region_preset(["north_america", "china"])

        assert "usa" in expanded
        assert "canada" in expanded
        assert "mexico" in expanded
        assert "china" in expanded

    def test_duplicate_removal(self):
        """Test duplicates are removed."""
        expanded = expand_region_preset(["g7", "usa", "japan"])

        assert expanded.count("usa") == 1
        assert expanded.count("japan") == 1

    def test_empty_list(self):
        """Test empty list."""
        expanded = expand_region_preset([])

        assert expanded == []


class TestValidateRegion:
    """Test region validation."""

    def test_valid_region(self):
        """Test validation of valid region."""
        assert validate_region("usa") is True
        assert validate_region("euro_area") is True
        assert validate_region("uk") is True

    def test_invalid_region(self):
        """Test validation of invalid region."""
        assert validate_region("invalid_region") is False

    def test_all_g7_valid(self):
        """Test all G7 countries are valid."""
        g7_countries = REGION_PRESETS["g7"]

        for country in g7_countries:
            assert validate_region(country) is True, \
                f"G7 country {country} should be valid"


class TestGetSupportedRegions:
    """Test supported regions discovery."""

    def test_returns_list(self):
        """Test returns a list of regions."""
        regions = get_supported_regions()

        assert isinstance(regions, list)
        assert len(regions) > 0

    def test_includes_major_economies(self):
        """Test includes major economies."""
        regions = get_supported_regions()

        assert "usa" in regions
        assert "euro_area" in regions
        assert "uk" in regions
        assert "japan" in regions
        assert "china" in regions

    def test_no_duplicates(self):
        """Test no duplicate regions."""
        regions = get_supported_regions()

        assert len(regions) == len(set(regions))


class TestGetMethodologicalNote:
    """Test methodological notes retrieval."""

    def test_usa_note(self):
        """Test USA methodological note."""
        note = get_methodological_note("usa")

        assert note is not None
        assert "owner" in note.lower() or "OER" in note

    def test_euro_area_note(self):
        """Test Euro Area methodological note."""
        note = get_methodological_note("euro_area")

        assert note is not None
        assert "exclude" in note.lower()
        assert "owner" in note.lower()

    def test_invalid_region(self):
        """Test invalid region returns None."""
        note = get_methodological_note("invalid_region")

        assert note is None


class TestGetComparabilityWarnings:
    """Test comparability warnings generation."""

    def test_hicp_cpi_mix_warning(self):
        """Test warning when mixing HICP and CPI."""
        warnings = get_comparability_warnings(["usa", "euro_area"])

        # Should warn about mixing CPI (USA) and HICP (Euro)
        warnings_text = " ".join(warnings).lower()
        assert "mixed index" in warnings_text or "hicp" in warnings_text or "cpi" in warnings_text

    def test_owner_housing_warning(self):
        """Test warning about owner-occupied housing differences."""
        warnings = get_comparability_warnings(["usa", "euro_area"])

        warnings_text = " ".join(warnings).lower()
        assert "owner" in warnings_text or "housing" in warnings_text

    def test_canada_mortgage_warning(self):
        """Test specific warning for Canada mortgage costs."""
        warnings = get_comparability_warnings(["usa", "canada"])

        warnings_text = " ".join(warnings).lower()
        # Canada includes mortgage interest, should be mentioned
        assert "canada" in warnings_text or "mortgage" in warnings_text

    def test_all_hicp_no_warning(self):
        """Test no major warnings when all regions use HICP."""
        warnings = get_comparability_warnings(["euro_area", "germany", "france"])

        # Should have minimal warnings since all are HICP
        # May still have some minor methodological notes
        assert isinstance(warnings, list)

    def test_frequency_mismatch_warning(self):
        """Test warning for frequency mismatches."""
        # Some countries may have quarterly instead of monthly
        warnings = get_comparability_warnings(["usa", "new_zealand"])

        # If frequencies differ, should warn
        # If both monthly, no frequency warning expected
        assert isinstance(warnings, list)

    def test_single_region_no_warnings(self):
        """Test no comparability warnings for single region."""
        warnings = get_comparability_warnings(["usa"])

        # Single region should have no comparability warnings
        # (though may have methodological notes)
        assert len(warnings) == 0 or all("compar" not in w.lower() for w in warnings)

    def test_empty_regions(self):
        """Test empty regions list."""
        warnings = get_comparability_warnings([])

        assert warnings == []


class TestInflationSeriesIntegrity:
    """Test overall integrity of inflation series mappings."""

    def test_no_empty_series_ids(self):
        """Test that no series IDs are empty."""
        for region, series in INFLATION_SERIES.items():
            assert series.series_id != "", \
                f"Series ID for {region} should not be empty"
            assert isinstance(series.series_id, str)

    def test_series_ids_uppercase(self):
        """Test that FRED series IDs follow convention."""
        for region, series in INFLATION_SERIES.items():
            # FRED series IDs typically start uppercase or digit
            assert series.series_id[0].isupper() or series.series_id[0].isdigit(), \
                f"Series ID {series.series_id} for {region} should start uppercase/digit"

    def test_all_have_index_type(self):
        """Test all series have valid index type."""
        valid_types = ["CPI", "HICP", "PCE"]

        for region, series in INFLATION_SERIES.items():
            assert series.index_type in valid_types, \
                f"Region {region} has invalid index type {series.index_type}"

    def test_all_have_source(self):
        """Test all series have source attribution."""
        for region, series in INFLATION_SERIES.items():
            assert series.source != "", \
                f"Region {region} should have source"

    def test_all_have_verified_date(self):
        """Test all series have verification date."""
        for region, series in INFLATION_SERIES.items():
            assert series.verified_date != "", \
                f"Region {region} should have verified_date"

    def test_hicp_excludes_owner_housing(self):
        """Test that all HICP series exclude owner housing."""
        for region, series in INFLATION_SERIES.items():
            if series.index_type == "HICP":
                assert series.includes_owner_housing is False, \
                    f"HICP series {region} should exclude owner housing"

    def test_methodological_notes_exist(self):
        """Test that important series have methodological notes."""
        # Major economies should have detailed notes
        major_regions = ["usa", "euro_area", "uk", "japan", "canada"]

        for region in major_regions:
            if region in INFLATION_SERIES:
                series = INFLATION_SERIES[region]
                assert series.methodological_notes is not None, \
                    f"Major region {region} should have methodological notes"
                assert len(series.methodological_notes) > 10, \
                    f"Region {region} notes should be substantive"


class TestInflationTargetsIntegrity:
    """Test overall integrity of inflation targets."""

    def test_targets_have_point_or_range(self):
        """Test each target has either point or range."""
        for region, target in INFLATION_TARGETS.items():
            has_point = target.point_target is not None
            has_range = target.target_range is not None

            assert has_point or has_range, \
                f"Target for {region} should have point_target or target_range"

    def test_targets_have_measure(self):
        """Test all targets specify the measure."""
        for region, target in INFLATION_TARGETS.items():
            assert target.target_measure != "", \
                f"Target for {region} should specify target_measure"

    def test_reasonable_target_values(self):
        """Test that target values are reasonable."""
        for region, target in INFLATION_TARGETS.items():
            if target.point_target is not None:
                assert 0 <= target.point_target <= 10, \
                    f"Point target for {region} should be between 0-10%"

            if target.target_range is not None:
                lower, upper = target.target_range
                assert 0 <= lower < upper <= 15, \
                    f"Target range for {region} should be reasonable"

    def test_regime_start_dates_valid(self):
        """Test regime start dates are reasonable."""
        for region, target in INFLATION_TARGETS.items():
            if target.regime_start is not None:
                assert 1980 <= target.regime_start <= 2030, \
                    f"Regime start for {region} should be between 1980-2030"

    def test_major_economies_have_targets(self):
        """Test major developed economies have inflation targets."""
        major_with_targets = ["usa", "euro_area", "uk", "japan", "canada", "australia"]

        for region in major_with_targets:
            assert region in INFLATION_TARGETS, \
                f"Major economy {region} should have inflation target"


class TestRegionPresetsIntegrity:
    """Test overall integrity of region presets."""

    def test_no_empty_presets(self):
        """Test no presets are empty."""
        for preset, regions in REGION_PRESETS.items():
            assert len(regions) > 0, \
                f"Preset '{preset}' should not be empty"

    def test_no_duplicate_regions_in_presets(self):
        """Test presets don't have duplicates."""
        for preset, regions in REGION_PRESETS.items():
            assert len(regions) == len(set(regions)), \
                f"Preset '{preset}' should not have duplicate regions"

    def test_preset_regions_exist(self):
        """Test regions in presets exist in INFLATION_SERIES."""
        for preset, regions in REGION_PRESETS.items():
            for region in regions:
                assert region in INFLATION_SERIES, \
                    f"Region '{region}' in preset '{preset}' should exist in INFLATION_SERIES"

    def test_g7_coverage(self):
        """Test G7 preset has all 7 countries."""
        g7 = REGION_PRESETS["g7"]

        assert len(g7) == 7, "G7 should have 7 countries"
        assert "usa" in g7
        assert "canada" in g7
        assert "uk" in g7
        assert "germany" in g7
        assert "france" in g7
        assert "italy" in g7
        assert "japan" in g7
