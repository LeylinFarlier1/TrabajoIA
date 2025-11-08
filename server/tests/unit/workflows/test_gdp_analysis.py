"""
Tests for GDP Analysis Tool - Basic validation and integration tests.
"""
import pytest
import json
from unittest.mock import patch
from trabajo_ia_server.config import Config
from trabajo_ia_server.workflows.utils.gdp_mappings import (
    GDP_MAPPINGS,
    GDP_PRESETS,
    expand_preset,
    get_series_id
)
from trabajo_ia_server.workflows.utils.gdp_validators import (
    validate_variants,
    validate_countries,
    validate_date_range
)
from trabajo_ia_server.workflows.analyze_gdp import analyze_gdp_cross_country


class TestGDPMappings:
    """Test GDP mappings and presets."""
    
    def test_gdp_mappings_structure(self):
        """All countries have required base series."""
        assert len(GDP_MAPPINGS) > 0
        
        # Check USA mapping (required for all tests)
        assert "usa" in GDP_MAPPINGS
        usa_mapping = GDP_MAPPINGS["usa"]
        
        # Essential variants must exist
        assert "per_capita_constant" in usa_mapping
        assert "population" in usa_mapping
        assert "constant_2010" in usa_mapping
    
    def test_get_series_id(self):
        """get_series_id returns correct series IDs."""
        # Valid mapping
        series_id = get_series_id("usa", "per_capita_constant")
        assert series_id == "NYGDPPCAPKDUSA"
        
        # Invalid country
        assert get_series_id("invalid", "per_capita_constant") is None
        
        # Invalid variant
        assert get_series_id("usa", "invalid_variant") is None
    
    def test_presets_expansion(self):
        """Presets expand correctly."""
        # G7 preset
        g7_countries = expand_preset("g7")
        assert len(g7_countries) == 7
        assert "usa" in g7_countries
        assert "japan" in g7_countries
        
        # Mix preset + country
        mixed = expand_preset(["g7", "china"])
        assert len(mixed) == 8  # 7 + 1
        assert "china" in mixed
        
        # Single country
        single = expand_preset("usa")
        assert single == ["usa"]
        
        # List of countries
        multiple = expand_preset(["usa", "canada"])
        assert len(multiple) == 2
    
    def test_presets_no_duplicates(self):
        """Presets don't have duplicates after expansion."""
        # Request G7 twice
        result = expand_preset(["g7", "g7"])
        assert len(result) == 7  # Not 14
        
        # Request USA explicitly + through G7
        result = expand_preset(["usa", "g7"])
        assert len(result) == 7  # Not 8


class TestGDPValidators:
    """Test validation functions."""
    
    def test_validate_countries_valid(self):
        """Valid countries pass validation."""
        result = validate_countries("usa")
        assert result["expanded"] == ["usa"]
        assert len(result["invalid"]) == 0
    
    def test_validate_countries_preset(self):
        """Presets expand correctly in validation."""
        result = validate_countries("g7")
        assert len(result["expanded"]) == 7
        assert "usa" in result["expanded"]
    
    def test_validate_countries_invalid(self):
        """Invalid countries are flagged."""
        result = validate_countries(["usa", "invalid_country"])
        assert "usa" in result["expanded"]
        assert "invalid_country" in result["invalid"]
        assert len(result["warnings"]) > 0
    
    def test_validate_variants_direct(self):
        """Direct variants (non-computed) validate correctly."""
        result = validate_variants(
            ["per_capita_constant"],
            ["usa"],
            check_availability=True
        )
        # per_capita_constant has fallback="fetch_direct", so it's computable
        assert "per_capita_constant" in result["computable"]
        assert len(result["missing_dependencies"]) == 0
        # Should have warning about trying direct fetch first
        assert any("direct FRED fetch" in w for w in result["warnings"])
    
    def test_validate_variants_computed(self):
        """Computed variants identify dependencies."""
        result = validate_variants(
            ["growth_rate"],
            ["usa"],
            check_availability=True
        )
        assert "growth_rate" in result["computable"]
        assert "constant_2010" in result["required_sources"]
    
    def test_validate_variants_missing_dependency(self):
        """Missing dependencies are detected."""
        # Create scenario with missing data
        result = validate_variants(
            ["per_capita_constant"],
            ["nonexistent_country"],
            check_availability=True
        )
        # Should have warnings about unavailability
        assert len(result["warnings"]) > 0
    
    def test_validate_date_range_valid(self):
        """Valid date ranges pass."""
        result = validate_date_range("2000-01-01", "2023-12-31")
        assert result["valid"] is True
        assert result["start_parsed"] is not None
        assert result["end_parsed"] is not None
    
    def test_validate_date_range_invalid_format(self):
        """Invalid date formats are caught."""
        result = validate_date_range("2000/01/01", "2023-12-31")
        assert result["valid"] is False
        assert len(result["warnings"]) > 0
    
    def test_validate_date_range_inverted(self):
        """Start after end is caught."""
        result = validate_date_range("2023-01-01", "2000-01-01")
        assert result["valid"] is False
        assert any("before" in w for w in result["warnings"])


class TestGDPAnalysisTool:
    """Test main GDP analysis tool (skeleton implementation)."""
    
    def test_analyze_gdp_missing_api_key(self):
        """Tool returns clear error when FRED_API_KEY is missing."""
        with patch.object(Config, 'FRED_API_KEY', None):
            result_str = analyze_gdp_cross_country(
                countries=["usa"],
                gdp_variants=["per_capita_constant"]
            )
            
            result = json.loads(result_str)
            assert "error" in result
            assert result["error"] == "FRED_API_KEY_MISSING"
            assert "FRED_API_KEY not configured" in result["error_message"]
            assert "https://fred.stlouisfed.org" in result["error_message"]
            assert "metadata" in result
    
    def test_fetch_data_all_series_fail(self):
        """Tool returns NO_DATA_FETCHED error when all fetches fail."""
        from trabajo_ia_server.workflows.layers.fetch_data import FetchResult
        
        # Mock fetch_gdp_data to return empty data
        def mock_fetch_empty(*args, **kwargs):
            return FetchResult(
                data={"usa": {}},  # Empty dict for country
                metadata={
                    "fetched_series": [],
                    "computed_variants": [],
                    "missing_series": ["usa/per_capita_constant"],
                    "errors": [{"series_id": "UNKNOWN", "error": "404 Not Found"}],
                    "source_series": {},
                    "fetch_timestamp": "2023-01-01T00:00:00Z"
                }
            )
        
        with patch('trabajo_ia_server.workflows.analyze_gdp.fetch_gdp_data', side_effect=mock_fetch_empty):
            result_str = analyze_gdp_cross_country(
                countries=["usa"],
                gdp_variants=["per_capita_constant"]
            )
            
            result = json.loads(result_str)
            assert "error" in result
            assert result["error"] == "NO_DATA_FETCHED"
            assert "Could not fetch any data" in result["error_message"]
            assert "details" in result
            assert "missing_series" in result["details"]
            assert "errors" in result["details"]
            assert result["details"]["requested_countries"] == ["usa"]
    
    def test_tool_basic_call(self):
        """Tool executes without crashing."""
        result_str = analyze_gdp_cross_country(
            countries=["usa"],
            gdp_variants=["per_capita_constant"]
        )
        
        # Should return valid JSON
        result = json.loads(result_str)
        assert result["tool"] == "analyze_gdp_cross_country"
        assert "metadata" in result
        assert "request" in result
    
    def test_tool_preset_expansion(self):
        """Tool handles presets correctly."""
        result_str = analyze_gdp_cross_country(
            countries=["g7"],
            gdp_variants=["per_capita_constant"]
        )
        
        result = json.loads(result_str)
        assert len(result["request"]["expanded_countries"]) == 7
    
    def test_tool_validation_error(self):
        """Tool handles validation errors gracefully."""
        result_str = analyze_gdp_cross_country(
            countries=["invalid_country"],
            gdp_variants=["per_capita_constant"]
        )
        
        result = json.loads(result_str)
        # Should have error or warnings
        assert "error" in result or len(result["metadata"]["validation_warnings"]) > 0
    
    def test_tool_invalid_date_format(self):
        """Tool catches invalid date formats."""
        result_str = analyze_gdp_cross_country(
            countries=["usa"],
            gdp_variants=["per_capita_constant"],
            start_date="invalid-date"
        )
        
        result = json.loads(result_str)
        assert "error" in result or "validation_errors" in result
    
    def test_tool_multiple_variants(self):
        """Tool handles multiple variants."""
        result_str = analyze_gdp_cross_country(
            countries=["usa"],
            gdp_variants=["per_capita_constant", "growth_rate"]
        )
        
        result = json.loads(result_str)
        assert "per_capita_constant" in result["request"]["gdp_variants"]
        assert "growth_rate" in result["request"]["gdp_variants"]
    
    def test_tool_json_format(self):
        """Tool returns compact JSON (MCP-compatible)."""
        result_str = analyze_gdp_cross_country(
            countries=["usa"],
            gdp_variants=["per_capita_constant"]
        )
        
        # Should be valid JSON
        result = json.loads(result_str)
        
        # Should be compact (no unnecessary whitespace)
        assert "\n" not in result_str or result_str.count("\n") < 5
        
        # Should have standard structure
        assert "tool" in result
        assert "metadata" in result
        assert "fetch_timestamp" in result["metadata"]


class TestMCPCompatibility:
    """Test MCP protocol compatibility."""
    
    def test_return_type_is_string(self):
        """Tool returns string (JSON), not dict."""
        result = analyze_gdp_cross_country(
            countries=["usa"],
            gdp_variants=["per_capita_constant"]
        )
        assert isinstance(result, str)
    
    def test_json_parseable(self):
        """Returned string is valid JSON."""
        result_str = analyze_gdp_cross_country(
            countries=["usa"],
            gdp_variants=["per_capita_constant"]
        )
        
        # Should not raise exception
        result = json.loads(result_str)
        assert isinstance(result, dict)
    
    def test_tool_name_in_response(self):
        """Response includes tool name (MCP standard)."""
        result_str = analyze_gdp_cross_country(
            countries=["usa"],
            gdp_variants=["per_capita_constant"]
        )
        
        result = json.loads(result_str)
        assert result["tool"] == "analyze_gdp_cross_country"
    
    def test_metadata_present(self):
        """Response includes metadata (MCP standard)."""
        result_str = analyze_gdp_cross_country(
            countries=["usa"],
            gdp_variants=["per_capita_constant"]
        )
        
        result = json.loads(result_str)
        assert "metadata" in result
        assert "fetch_timestamp" in result["metadata"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
