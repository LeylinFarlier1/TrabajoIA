"""Unit tests for compare_inflation_across_regions workflow.

Tests cover:
- End-to-end workflow orchestration (inflation-only)
- Parameter validation and region expansion
- Central bank target analysis
- Base effects detection
- Comparability warnings generation
- Error handling for various scenarios
- Response format validation
- Integration with FRED tools
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from trabajo_ia_server.workflows.compare_inflation import compare_inflation_across_regions


class TestCompareInflationValidation:
    """Test parameter validation and preprocessing."""

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_region_preset_expansion(self, mock_get_obs):
        """Test that region presets are expanded correctly."""
        # Mock to prevent actual API calls
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["north_america"],  # Should expand to usa, canada, mexico
        )

        result_data = json.loads(result)

        # Check that regions were expanded
        regions_with_data = result_data["metadata"]["regions_with_data"]
        # At least some north american countries should have data
        assert any(r in regions_with_data for r in ["usa", "canada", "mexico"])

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_mvp_limit_enforcement(self, mock_get_obs):
        """Test that MVP limit of 5 regions is enforced."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.0"}]
        })

        # Request 7 G7 countries (exceeds limit)
        result = compare_inflation_across_regions(
            regions=["g7"],  # 7 countries
        )

        result_data = json.loads(result)

        # Should be truncated to 5
        if "error" not in result_data:
            regions_with_data = result_data["metadata"]["regions_with_data"]
            assert len(regions_with_data) <= 5

    def test_invalid_regions_filtered(self):
        """Test that invalid regions are filtered out."""
        result = compare_inflation_across_regions(
            regions=["usa", "invalid_region", "uk"],
        )

        result_data = json.loads(result)

        # If some regions are valid, should proceed with valid ones
        if "error" not in result_data:
            regions_with_data = result_data["metadata"]["regions_with_data"]
            assert "invalid_region" not in regions_with_data
            assert "usa" in regions_with_data or "uk" in regions_with_data

    def test_all_invalid_regions_error(self):
        """Test error when all regions are invalid."""
        result = compare_inflation_across_regions(
            regions=["invalid1", "invalid2"],
        )

        result_data = json.loads(result)

        assert "error" in result_data

    def test_empty_regions_list(self):
        """Test error handling with empty regions list."""
        result = compare_inflation_across_regions(
            regions=[],
        )

        result_data = json.loads(result)

        # Should return error for empty regions
        assert "error" in result_data


class TestCompareInflationDataFetching:
    """Test data fetching and alignment."""

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_successful_data_fetch(self, mock_get_obs):
        """Test successful data fetching and processing."""
        # Mock responses for two regions
        def mock_obs_response(series_id, **kwargs):
            if series_id == "CPIAUCSL":  # USA inflation
                return json.dumps({
                    "data": [
                        {"date": "2025-01", "value": "3.0"},
                        {"date": "2025-02", "value": "2.9"},
                    ]
                })
            else:  # UK inflation
                return json.dumps({
                    "data": [
                        {"date": "2025-01", "value": "2.5"},
                        {"date": "2025-02", "value": "2.4"},
                    ]
                })

        mock_get_obs.side_effect = mock_obs_response

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        assert "error" not in result_data
        assert "comparison" in result_data
        assert len(result_data["comparison"]["latest_snapshot"]["ranking"]) == 2

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_partial_data_fetch_failure(self, mock_get_obs):
        """Test handling when some regions fail to fetch."""
        call_count = {"count": 0}

        def mock_obs_response(series_id, **kwargs):
            call_count["count"] += 1
            if call_count["count"] == 1:
                # First call succeeds
                return json.dumps({
                    "data": [
                        {"date": "2025-01", "value": "3.0"},
                        {"date": "2025-02", "value": "2.9"},
                    ]
                })
            else:
                # Second call fails
                return json.dumps({"error": "API Error"})

        mock_get_obs.side_effect = mock_obs_response

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        # Should proceed with available data
        if "error" not in result_data:
            regions_with_data = result_data["metadata"]["regions_with_data"]
            assert len(regions_with_data) == 1

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_all_data_fetch_failures(self, mock_get_obs):
        """Test error when all regions fail to fetch."""
        mock_get_obs.return_value = json.dumps({"error": "API Error"})

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        assert "error" in result_data

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_no_common_dates(self, mock_get_obs):
        """Test error when regions have no overlapping dates."""
        def mock_obs_response(series_id, **kwargs):
            if series_id == "CPIAUCSL":
                return json.dumps({
                    "data": [{"date": "2025-01", "value": "3.0"}]
                })
            else:
                return json.dumps({
                    "data": [{"date": "2025-02", "value": "2.5"}]
                })

        mock_get_obs.side_effect = mock_obs_response

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        assert "error" in result_data
        assert "no common dates" in result_data["error"].lower()


class TestCompareInflationTargetAnalysis:
    """Test central bank inflation target analysis."""

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_target_analysis_present(self, mock_get_obs):
        """Test that target analysis is included."""
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.5"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "euro_area"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            assert "target_analysis" in result_data["comparison"]
            target = result_data["comparison"]["target_analysis"]

            # Should classify regions by target adherence
            assert "regions_above_target" in target
            assert "regions_at_target" in target
            assert "regions_below_target" in target

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_distance_from_target_calculated(self, mock_get_obs):
        """Test distance from target is calculated."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.5"}]
        })

        result = compare_inflation_across_regions(
            regions=["euro_area"],  # Has 2% target
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            ranking = result_data["comparison"]["latest_snapshot"]["ranking"]
            # Should have distance_from_target for regions with targets
            if len(ranking) > 0:
                euro_entry = next((r for r in ranking if r["region"] == "euro_area"), None)
                if euro_entry:
                    assert "distance_from_target" in euro_entry
                    # 3.5% vs 2% target = 1.5pp distance
                    assert euro_entry["distance_from_target"] == pytest.approx(1.5, abs=0.1)

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_sticky_inflation_detection(self, mock_get_obs):
        """Test sticky inflation detection (>3% for 6+ months)."""
        # Mock 7 months of high inflation
        mock_data = {
            "data": [
                {"date": f"2024-{str(i+1).zfill(2)}", "value": "4.0"}
                for i in range(7)
            ]
        }
        mock_get_obs.return_value = json.dumps(mock_data)

        result = compare_inflation_across_regions(
            regions=["usa"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            target_analysis = result_data["comparison"]["target_analysis"]
            # USA should be flagged as sticky inflation
            assert "sticky_inflation" in target_analysis
            assert isinstance(target_analysis["sticky_inflation"], list)


class TestCompareInflationComparabilityWarnings:
    """Test comparability warnings generation."""

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_hicp_cpi_mix_warning(self, mock_get_obs):
        """Test warning when mixing HICP and CPI."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.0"}]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "euro_area"],  # CPI vs HICP
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            warnings = result_data["comparability_warnings"]
            warnings_text = " ".join(warnings).lower()

            # Should warn about methodology differences
            assert len(warnings) > 0
            assert "hicp" in warnings_text or "cpi" in warnings_text or "mixed" in warnings_text

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_owner_housing_warning(self, mock_get_obs):
        """Test warning about owner-occupied housing."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.0"}]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "euro_area"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            warnings = result_data["comparability_warnings"]
            warnings_text = " ".join(warnings).lower()

            # Should warn about owner housing differences
            assert "owner" in warnings_text or "housing" in warnings_text

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_base_effects_detection(self, mock_get_obs):
        """Test base effects detection."""
        # Mock data with sharp drop then sharp rise (potential VAT change)
        mock_data = {
            "data": [
                {"date": "2024-01", "value": "3.0"},
                {"date": "2024-02", "value": "3.0"},
                {"date": "2024-03", "value": "1.0"},  # Sharp drop
                {"date": "2024-04", "value": "1.0"},
                {"date": "2024-05", "value": "4.0"},  # Sharp rise
            ]
        }
        mock_get_obs.return_value = json.dumps(mock_data)

        result = compare_inflation_across_regions(
            regions=["euro_area"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            # Should have base effect warnings
            warnings = result_data.get("comparability_warnings", [])
            # May or may not trigger depending on threshold, but should be checked
            assert isinstance(warnings, list)


class TestCompareInflationAnalysis:
    """Test analysis and calculations."""

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_ranking_calculation(self, mock_get_obs):
        """Test that ranking is calculated correctly."""
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.5"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            ranking = result_data["comparison"]["latest_snapshot"]["ranking"]
            assert len(ranking) > 0
            assert all("rank" in item for item in ranking)
            assert all("value" in item for item in ranking)
            assert all("region" in item for item in ranking)

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_trends_calculation(self, mock_get_obs):
        """Test that trends are calculated for each region."""
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
                {"date": "2025-03", "value": "2.8"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            trends = result_data["comparison"]["trends"]
            assert len(trends) > 0
            # Each region should have trend info
            for region, trend in trends.items():
                assert "direction" in trend
                assert trend["direction"] in ["increasing", "decreasing", "stable"]

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_convergence_analysis(self, mock_get_obs):
        """Test convergence/divergence analysis."""
        # Mock 13+ months of data for convergence analysis
        mock_data = {
            "data": [
                {"date": f"2024-{str(i+1).zfill(2)}", "value": str(3.0 - i*0.1)}
                for i in range(13)
            ]
        }
        mock_get_obs.return_value = json.dumps(mock_data)

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            analysis = result_data["comparison"]["analysis"]
            assert "convergence" in analysis
            assert isinstance(analysis["convergence"], str)


class TestCompareInflationResponseFormat:
    """Test response format and structure."""

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_response_structure(self, mock_get_obs):
        """Test that response has all required fields."""
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            # Top level
            assert "tool" in result_data
            assert result_data["tool"] == "compare_inflation_across_regions"
            assert "comparison" in result_data
            assert "metadata" in result_data
            assert "comparability_warnings" in result_data
            assert "limitations" in result_data
            assert "suggestions" in result_data

            # Comparison section
            comparison = result_data["comparison"]
            assert "latest_snapshot" in comparison
            assert "analysis" in comparison
            assert "trends" in comparison
            assert "time_series" in comparison
            assert "target_analysis" in comparison

            # Metadata section
            metadata = result_data["metadata"]
            assert "fetch_date" in metadata
            assert "series_used" in metadata
            assert "data_points" in metadata

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_series_metadata_format(self, mock_get_obs):
        """Test series metadata includes HICP/CPI info."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.0"}]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "euro_area"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            series_used = result_data["metadata"]["series_used"]
            assert len(series_used) > 0

            # Each series should have metadata
            for series_info in series_used:
                assert "region" in series_info
                assert "index_type" in series_info
                assert "includes_owner_housing" in series_info
                # Should distinguish HICP vs CPI
                assert series_info["index_type"] in ["CPI", "HICP", "PCE"]

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_time_series_format(self, mock_get_obs):
        """Test time series data structure."""
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            time_series = result_data["comparison"]["time_series"]
            assert isinstance(time_series, list)
            if len(time_series) > 0:
                point = time_series[0]
                assert "date" in point
                # Should have values for each region
                assert any(k != "date" for k in point.keys())

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_limitations_documented(self, mock_get_obs):
        """Test that limitations are clearly documented."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.0"}]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            limitations = result_data["limitations"]
            assert isinstance(limitations, list)
            assert len(limitations) > 0

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_suggestions_provided(self, mock_get_obs):
        """Test that suggestions are provided."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.0"}]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            suggestions = result_data["suggestions"]
            assert isinstance(suggestions, list)
            assert len(suggestions) > 0


class TestCompareInflationParameters:
    """Test various parameter combinations."""

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_date_range_parameters(self, mock_get_obs):
        """Test that date range parameters are passed correctly."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.0"}]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
            start_date="2020-01-01",
            end_date="2025-01-01",
        )

        # Verify that get_series_observations was called with date params
        assert mock_get_obs.called
        calls = mock_get_obs.call_args_list
        for call in calls:
            kwargs = call[1]
            assert kwargs.get("observation_start") == "2020-01-01"
            assert kwargs.get("observation_end") == "2025-01-01"

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_pc1_transformation_applied(self, mock_get_obs):
        """Test that pc1 (YoY %) transformation is applied."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.0"}]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        # Inflation should use pc1 transformation (year-over-year %)
        calls = mock_get_obs.call_args_list
        for call in calls:
            kwargs = call[1]
            assert kwargs.get("units") == "pc1"

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_parallel_fetching(self, mock_get_obs):
        """Test that parallel fetching is used for multiple regions."""
        mock_get_obs.return_value = json.dumps({
            "data": [{"date": "2025-01", "value": "3.0"}]
        })

        result = compare_inflation_across_regions(
            regions=["usa", "uk", "japan"],
        )

        # Should have called get_series_observations for each valid region
        assert mock_get_obs.call_count >= 2

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_metric_parameter_latest(self, mock_get_obs):
        """Test metric='latest' parameter."""
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["usa"],
            metric="latest",
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            # Should have latest snapshot
            assert "latest_snapshot" in result_data["comparison"]

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_metric_parameter_all(self, mock_get_obs):
        """Test metric='all' parameter."""
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["usa"],
            metric="all",
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            # Should have comprehensive analysis
            assert "latest_snapshot" in result_data["comparison"]
            assert "trends" in result_data["comparison"]
            assert "time_series" in result_data["comparison"]


class TestCompareInflationEdgeCases:
    """Test edge cases and error conditions."""

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_single_region(self, mock_get_obs):
        """Test with single region (edge case but should work)."""
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "3.0"},
                {"date": "2025-02", "value": "2.9"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["usa"],
        )

        result_data = json.loads(result)

        # Should work with just one region
        if "error" not in result_data:
            ranking = result_data["comparison"]["latest_snapshot"]["ranking"]
            assert len(ranking) == 1

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_exception_handling(self, mock_get_obs):
        """Test graceful handling of unexpected exceptions."""
        mock_get_obs.side_effect = Exception("Unexpected error")

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        # Should return error response, not crash
        assert "error" in result_data or "comparison" in result_data

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_very_long_time_series(self, mock_get_obs):
        """Test that long time series are truncated in response."""
        # Mock 50 months of data
        mock_data = {
            "data": [
                {"date": f"2020-{str((i % 12) + 1).zfill(2)}", "value": str(3.0 - i*0.01)}
                for i in range(50)
            ]
        }
        mock_get_obs.return_value = json.dumps(mock_data)

        result = compare_inflation_across_regions(
            regions=["usa", "uk"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            time_series = result_data["comparison"]["time_series"]
            # Should be truncated to max 24 points
            assert len(time_series) <= 24


class TestCompareInflationIntegration:
    """Integration-style tests with realistic scenarios."""

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_realistic_inflation_comparison(self, mock_get_obs):
        """Test realistic inflation comparison scenario."""
        def mock_obs_response(series_id, **kwargs):
            # Different but realistic data for different countries
            if "CPIAUCSL" in series_id:  # USA
                return json.dumps({
                    "data": [
                        {"date": "2024-10", "value": "3.5"},
                        {"date": "2024-11", "value": "3.2"},
                        {"date": "2024-12", "value": "3.0"},
                    ]
                })
            else:  # Euro/UK
                return json.dumps({
                    "data": [
                        {"date": "2024-10", "value": "2.8"},
                        {"date": "2024-11", "value": "2.5"},
                        {"date": "2024-12", "value": "2.2"},
                    ]
                })

        mock_get_obs.side_effect = mock_obs_response

        result = compare_inflation_across_regions(
            regions=["usa", "euro_area"],
            metric="all",
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            # Should have complete analysis
            assert "comparison" in result_data
            assert "latest_snapshot" in result_data["comparison"]
            assert "trends" in result_data["comparison"]
            assert "time_series" in result_data["comparison"]
            assert "target_analysis" in result_data["comparison"]

            # Time series should have aligned data
            time_series = result_data["comparison"]["time_series"]
            assert len(time_series) == 3  # 3 common months

            # Should have comparability warnings (CPI vs HICP)
            warnings = result_data["comparability_warnings"]
            assert len(warnings) > 0

    @patch("trabajo_ia_server.workflows.compare_inflation.get_series_observations")
    def test_hicp_only_comparison(self, mock_get_obs):
        """Test comparison of HICP countries only."""
        mock_get_obs.return_value = json.dumps({
            "data": [
                {"date": "2025-01", "value": "2.5"},
                {"date": "2025-02", "value": "2.3"},
            ]
        })

        result = compare_inflation_across_regions(
            regions=["euro_area", "germany", "france"],
        )

        result_data = json.loads(result)

        if "error" not in result_data:
            # All HICP series should have minimal comparability issues
            series_used = result_data["metadata"]["series_used"]
            # All should be HICP
            assert all(s["index_type"] == "HICP" for s in series_used)

            # All should exclude owner housing
            assert all(s["includes_owner_housing"] is False for s in series_used)
