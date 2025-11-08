"""
Tests for configuration validation.
"""
import pytest
import os
from unittest.mock import patch
from trabajo_ia_server.config import Config, ConfigError


class TestConfigValidation:
    """Test configuration validation logic."""
    
    def test_validate_with_valid_api_key(self):
        """Validation passes when FRED_API_KEY is present."""
        with patch.object(Config, 'FRED_API_KEY', 'test_api_key_123'):
            # Should not raise
            Config.validate()
    
    def test_validate_missing_api_key(self):
        """Validation fails when FRED_API_KEY is None."""
        with patch.object(Config, 'FRED_API_KEY', None):
            with pytest.raises(ConfigError) as exc_info:
                Config.validate()
            
            assert "FRED_API_KEY environment variable is required" in str(exc_info.value)
            assert "https://fred.stlouisfed.org" in str(exc_info.value)
    
    def test_validate_empty_api_key(self):
        """Validation fails when FRED_API_KEY is empty string."""
        with patch.object(Config, 'FRED_API_KEY', ''):
            with pytest.raises(ConfigError) as exc_info:
                Config.validate()
            
            assert "FRED_API_KEY environment variable is required" in str(exc_info.value)
    
    def test_validate_whitespace_only_api_key(self):
        """Validation fails when FRED_API_KEY is whitespace only."""
        with patch.object(Config, 'FRED_API_KEY', '   '):
            with pytest.raises(ConfigError) as exc_info:
                Config.validate()
            
            assert "cannot be empty or whitespace only" in str(exc_info.value)
    
    def test_get_fred_api_key_success(self):
        """get_fred_api_key returns key when valid."""
        with patch.object(Config, 'FRED_API_KEY', 'test_key_xyz'):
            key = Config.get_fred_api_key()
            assert key == 'test_key_xyz'
    
    def test_get_fred_api_key_missing(self):
        """get_fred_api_key raises ConfigError when key is None."""
        with patch.object(Config, 'FRED_API_KEY', None):
            with pytest.raises(ConfigError) as exc_info:
                Config.get_fred_api_key()
            
            assert "FRED_API_KEY not configured" in str(exc_info.value)
            assert "https://fred.stlouisfed.org" in str(exc_info.value)
