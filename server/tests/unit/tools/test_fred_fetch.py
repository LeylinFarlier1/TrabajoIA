"""
Unit tests for FRED fetch series tool.
"""
import json
import pytest
from unittest.mock import Mock, patch
import pandas as pd

from trabajo_ia_server.tools.fred.fetch_series import fetch_series_observations


class TestFetchSeriesObservations:
    """Test cases for fetch_series_observations function."""

    @patch('trabajo_ia_server.tools.fred.fetch_series.Fred')
    @patch('trabajo_ia_server.config.config.get_fred_api_key')
    def test_successful_fetch(self, mock_get_key, mock_fred_class):
        """Test successful data fetch from FRED API."""
        # Arrange
        mock_get_key.return_value = "test_api_key"
        mock_fred = Mock()
        mock_fred_class.return_value = mock_fred

        # Create sample data
        sample_data = pd.Series({
            pd.Timestamp('2020-01-01'): 100.0,
            pd.Timestamp('2020-04-01'): 105.0,
        })
        mock_fred.get_series.return_value = sample_data

        # Act
        result = fetch_series_observations("GDP", "2020-01-01", "2020-12-31")
        result_data = json.loads(result)

        # Assert
        assert result_data["series_id"] == "GDP"
        assert result_data["tool"] == "fetch_series_observations"
        assert len(result_data["data"]) == 2
        assert result_data["metadata"]["total_count"] == 2

    @patch('trabajo_ia_server.config.config.get_fred_api_key')
    def test_invalid_series_id(self, mock_get_key):
        """Test handling of invalid series ID."""
        # Arrange
        mock_get_key.return_value = "test_api_key"

        # Act
        result = fetch_series_observations("", "2020-01-01", "2020-12-31")
        result_data = json.loads(result)

        # Assert
        assert "error" in result_data
        assert "Invalid series ID" in result_data["error"]

    @patch('trabajo_ia_server.config.config.get_fred_api_key')
    def test_invalid_date_format(self, mock_get_key):
        """Test handling of invalid date format."""
        # Arrange
        mock_get_key.return_value = "test_api_key"

        # Act
        result = fetch_series_observations("GDP", "2020/01/01", "2020-12-31")
        result_data = json.loads(result)

        # Assert
        assert "error" in result_data
        assert "Invalid start date format" in result_data["error"]

    @patch('trabajo_ia_server.tools.fred.fetch_series.Fred')
    @patch('trabajo_ia_server.config.config.get_fred_api_key')
    def test_api_error_handling(self, mock_get_key, mock_fred_class):
        """Test handling of FRED API errors."""
        # Arrange
        mock_get_key.return_value = "test_api_key"
        mock_fred = Mock()
        mock_fred_class.return_value = mock_fred
        mock_fred.get_series.side_effect = Exception("API Error")

        # Act
        result = fetch_series_observations("GDP")
        result_data = json.loads(result)

        # Assert
        assert "error" in result_data
        assert result_data["series_id"] == "GDP"
