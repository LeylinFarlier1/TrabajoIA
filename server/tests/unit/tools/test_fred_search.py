"""Unit tests for FRED search series tool with caching client."""

import json
from unittest.mock import patch

import pytest

from trabajo_ia_server.tools.fred.search_series import search_fred_series
from trabajo_ia_server.utils.fred_client import FredAPIError, FredAPIResponse


class TestSearchFredSeries:
    """Test cases for search_fred_series function."""

    @patch("trabajo_ia_server.utils.fred_client.fred_client.get_json")
    @patch("trabajo_ia_server.config.config.get_fred_api_key")
    def test_basic_search(self, mock_get_key, mock_get_json):
        mock_get_key.return_value = "test_api_key"
        payload = {
            "count": 2,
            "seriess": [
                {"id": "UNRATE", "title": "Unemployment Rate", "frequency": "Monthly"},
                {
                    "id": "UNRATENSA",
                    "title": "Unemployment Rate (Not Seasonally Adjusted)",
                    "frequency": "Monthly",
                },
            ],
        }
        mock_get_json.return_value = FredAPIResponse(
            payload=payload,
            url="https://api.stlouisfed.org/fred/series/search",
            status_code=200,
            headers={"X-RateLimit-Remaining": "100"},
            from_cache=False,
        )

        result = search_fred_series("unemployment")
        result_data = json.loads(result)

        assert result_data["tool"] == "search_fred_series"
        assert result_data["metadata"]["search_text"] == "unemployment"
        assert len(result_data["data"]) == 2
        assert result_data["metadata"]["total_count"] == 2
        assert result_data["metadata"]["api_info"]["cache_hit"] is False

    @patch("trabajo_ia_server.utils.fred_client.fred_client.get_json")
    @patch("trabajo_ia_server.config.config.get_fred_api_key")
    def test_search_with_filters(self, mock_get_key, mock_get_json):
        mock_get_key.return_value = "test_api_key"
        payload = {
            "count": 1,
            "seriess": [
                {
                    "id": "GDP",
                    "title": "Gross Domestic Product",
                    "frequency": "Quarterly",
                    "units": "Billions of Dollars",
                }
            ],
        }
        mock_get_json.return_value = FredAPIResponse(
            payload=payload,
            url="https://api.stlouisfed.org/fred/series/search",
            status_code=200,
            headers={"X-RateLimit-Remaining": "100"},
            from_cache=True,
        )

        result = search_fred_series(
            "GDP",
            filter_variable="frequency",
            filter_value="Quarterly",
        )
        result_data = json.loads(result)

        assert result_data["metadata"]["filters"]["filter_variable"] == "frequency"
        assert result_data["metadata"]["filters"]["filter_value"] == "Quarterly"
        assert len(result_data["data"]) == 1
        assert result_data["metadata"]["api_info"]["cache_hit"] is True

    @patch("trabajo_ia_server.utils.fred_client.fred_client.get_json")
    @patch("trabajo_ia_server.config.config.get_fred_api_key")
    def test_limit_parameter(self, mock_get_key, mock_get_json):
        mock_get_key.return_value = "test_api_key"
        payload = {
            "count": 100,
            "seriess": [{"id": f"SERIES{i}", "title": f"Series {i}"} for i in range(50)],
        }
        mock_get_json.return_value = FredAPIResponse(
            payload=payload,
            url="https://api.stlouisfed.org/fred/series/search",
            status_code=200,
            headers={"X-RateLimit-Remaining": "100"},
            from_cache=False,
        )

        result = search_fred_series("test", limit=50)
        result_data = json.loads(result)

        assert len(result_data["data"]) == 50
        assert result_data["metadata"]["limit"] == 50
        assert result_data["metadata"]["total_count"] == 100

    @patch("trabajo_ia_server.utils.fred_client.fred_client.get_json")
    @patch("trabajo_ia_server.config.config.get_fred_api_key")
    def test_api_error_handling(self, mock_get_key, mock_get_json):
        mock_get_key.return_value = "test_api_key"
        mock_get_json.side_effect = FredAPIError("API Error")

        result = search_fred_series("test")
        result_data = json.loads(result)

        assert "error" in result_data
        assert "API Error" in result_data["error"]


class TestSearchFredSeriesIntegration:
    """Lightweight integration checks for query building."""

    @pytest.mark.parametrize(
        "limit,expected_limit",
        [(0, 1), (2000, 1000), (50, 50)],
    )
    @patch("trabajo_ia_server.utils.fred_client.fred_client.get_json")
    @patch("trabajo_ia_server.config.config.get_fred_api_key", return_value="test_api_key")
    def test_limit_bounds(self, _mock_key, mock_get_json, limit, expected_limit):
        payload = {"count": 0, "seriess": []}
        mock_get_json.return_value = FredAPIResponse(
            payload=payload,
            url="https://api.stlouisfed.org/fred/series/search",
            status_code=200,
            headers={},
        )

        search_fred_series("bounds", limit=limit)

        args, kwargs = mock_get_json.call_args
        params = args[1]
        assert params["limit"] == expected_limit
