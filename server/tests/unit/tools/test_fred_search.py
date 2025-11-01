"""
Unit tests for FRED search series tool.
"""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from trabajo_ia_server.tools.fred.search_series import search_fred_series, _request_with_retries


class TestSearchFredSeries:
    """Test cases for search_fred_series function."""

    @patch('trabajo_ia_server.tools.fred.search_series._request_with_retries')
    @patch('trabajo_ia_server.config.config.get_fred_api_key')
    def test_basic_search(self, mock_get_key, mock_request):
        """Test basic search functionality."""
        # Arrange
        mock_get_key.return_value = "test_api_key"

        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 2,
            "seriess": [
                {
                    "id": "UNRATE",
                    "title": "Unemployment Rate",
                    "frequency": "Monthly"
                },
                {
                    "id": "UNRATENSA",
                    "title": "Unemployment Rate (Not Seasonally Adjusted)",
                    "frequency": "Monthly"
                }
            ]
        }
        mock_response.status_code = 200
        mock_response.url = "https://api.stlouisfed.org/fred/series/search"
        mock_response.headers = {"X-RateLimit-Remaining": "100"}
        mock_request.return_value = mock_response

        # Act
        result = search_fred_series("unemployment")
        result_data = json.loads(result)

        # Assert
        assert result_data["tool"] == "search_fred_series"
        assert result_data["metadata"]["search_text"] == "unemployment"
        assert len(result_data["data"]) == 2
        assert result_data["metadata"]["total_count"] == 2

    @patch('trabajo_ia_server.tools.fred.search_series._request_with_retries')
    @patch('trabajo_ia_server.config.config.get_fred_api_key')
    def test_search_with_filters(self, mock_get_key, mock_request):
        """Test search with filter parameters."""
        # Arrange
        mock_get_key.return_value = "test_api_key"

        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 1,
            "seriess": [
                {
                    "id": "GDP",
                    "title": "Gross Domestic Product",
                    "frequency": "Quarterly",
                    "units": "Billions of Dollars"
                }
            ]
        }
        mock_response.status_code = 200
        mock_response.url = "https://api.stlouisfed.org/fred/series/search"
        mock_response.headers = {"X-RateLimit-Remaining": "100"}
        mock_request.return_value = mock_response

        # Act
        result = search_fred_series(
            "GDP",
            filter_variable="frequency",
            filter_value="Quarterly"
        )
        result_data = json.loads(result)

        # Assert
        assert result_data["metadata"]["filters"]["filter_variable"] == "frequency"
        assert result_data["metadata"]["filters"]["filter_value"] == "Quarterly"
        assert len(result_data["data"]) == 1

    @patch('trabajo_ia_server.tools.fred.search_series._request_with_retries')
    @patch('trabajo_ia_server.config.config.get_fred_api_key')
    def test_limit_parameter(self, mock_get_key, mock_request):
        """Test limit parameter functionality (pagination removed in v0.1.2)."""
        # Arrange
        mock_get_key.return_value = "test_api_key"

        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 100,
            "seriess": [{"id": f"SERIES{i}", "title": f"Series {i}"} for i in range(50)]
        }
        mock_response.status_code = 200
        mock_response.url = "https://api.stlouisfed.org/fred/series/search"
        mock_response.headers = {"X-RateLimit-Remaining": "100"}
        mock_request.return_value = mock_response

        # Act
        result = search_fred_series("test", limit=50)
        result_data = json.loads(result)

        # Assert
        assert len(result_data["data"]) == 50
        assert result_data["metadata"]["limit"] == 50
        assert result_data["metadata"]["total_count"] == 100

    @patch('trabajo_ia_server.config.config.get_fred_api_key')
    def test_api_error_handling(self, mock_get_key):
        """Test handling of API errors."""
        # Arrange
        mock_get_key.return_value = "test_api_key"

        with patch('trabajo_ia_server.tools.fred.search_series._request_with_retries') as mock_request:
            mock_request.side_effect = ValueError("API Error")

            # Act
            result = search_fred_series("test")
            result_data = json.loads(result)

            # Assert
            assert "error" in result_data
            assert "API Error" in result_data["error"]


class TestRequestWithRetries:
    """Test cases for _request_with_retries function."""

    @patch('trabajo_ia_server.tools.fred.search_series._SESSION')
    def test_successful_request(self, mock_session):
        """Test successful API request."""
        # Arrange
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response

        # Act
        result = _request_with_retries("https://test.com", {})

        # Assert
        assert result == mock_response

    @patch('trabajo_ia_server.tools.fred.search_series._SESSION')
    def test_rate_limit_handling(self, mock_session):
        """Test rate limit retry behavior."""
        # Arrange
        from tenacity import RetryError
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"X-RateLimit-Reset": "0"}
        mock_session.get.return_value = mock_response

        # Act & Assert
        with pytest.raises(RetryError):
            _request_with_retries("https://test.com", {})

    @patch('trabajo_ia_server.tools.fred.search_series._SESSION')
    def test_request_failure(self, mock_session):
        """Test handling of failed requests."""
        # Arrange
        from tenacity import RetryError
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_session.get.return_value = mock_response

        # Act & Assert
        with pytest.raises(RetryError):
            _request_with_retries("https://test.com", {})
