"""
Tests for security features - secret redaction in logs and cache keys.
"""
import pytest
import logging
from io import StringIO
from trabajo_ia_server.utils.logger import SecretRedactingFilter, setup_logger
from trabajo_ia_server.utils.fred_client import FredClient


class TestSecretRedaction:
    """Test secret redaction in logs."""
    
    def test_logger_redacts_api_keys(self):
        """Logger should redact api_key patterns."""
        # Create logger with string stream to capture output
        logger = logging.getLogger("test_redaction")
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Add handler with redacting filter
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.addFilter(SecretRedactingFilter())
        logger.addHandler(handler)
        
        # Log message with API key
        logger.info("Calling API with api_key=super_secret_123")
        
        output = stream.getvalue()
        assert "super_secret_123" not in output
        assert "***REDACTED***" in output
        assert "api_key=" in output
    
    def test_logger_redacts_fred_api_key(self):
        """Logger should redact FRED_API_KEY patterns."""
        logger = logging.getLogger("test_fred_redaction")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.addFilter(SecretRedactingFilter())
        logger.addHandler(handler)
        
        # Log with FRED_API_KEY
        logger.info("Config loaded: FRED_API_KEY=abc123xyz")
        
        output = stream.getvalue()
        assert "abc123xyz" not in output
        assert "***REDACTED***" in output
    
    def test_logger_redacts_authorization_header(self):
        """Logger should redact Authorization headers."""
        logger = logging.getLogger("test_auth_redaction")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.addFilter(SecretRedactingFilter())
        logger.addHandler(handler)
        
        # Log with Authorization header
        logger.info("HTTP headers: Authorization: Bearer token123")
        
        output = stream.getvalue()
        assert "token123" not in output
        assert "***REDACTED***" in output
    
    def test_logger_redacts_bearer_tokens(self):
        """Logger should redact Bearer tokens."""
        logger = logging.getLogger("test_bearer_redaction")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.addFilter(SecretRedactingFilter())
        logger.addHandler(handler)
        
        # Log with Bearer token
        logger.info("Auth: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        
        output = stream.getvalue()
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in output
        assert "***REDACTED***" in output
    
    def test_logger_preserves_non_sensitive_data(self):
        """Logger should not redact non-sensitive data."""
        logger = logging.getLogger("test_preserve")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.addFilter(SecretRedactingFilter())
        logger.addHandler(handler)
        
        # Log normal message
        logger.info("Fetching series_id=GDP from FRED")
        
        output = stream.getvalue()
        assert "series_id=GDP" in output
        assert "FRED" in output
        assert "***REDACTED***" not in output
    
    def test_setup_logger_includes_redacting_filter(self):
        """setup_logger should automatically include SecretRedactingFilter."""
        logger = setup_logger("test_auto_redact")
        
        # Check filters
        has_redacting_filter = any(
            isinstance(f, SecretRedactingFilter)
            for f in logger.filters
        )
        assert has_redacting_filter, "SecretRedactingFilter not found in logger filters"


class TestCacheKeySecurity:
    """Test that cache keys don't include sensitive params."""
    
    def test_cache_key_excludes_api_key(self):
        """Cache key should not include api_key parameter."""
        client = FredClient()
        
        url = "https://api.example.com/data"
        params = {
            "series_id": "GDP",
            "api_key": "SECRET_KEY_123",
            "file_type": "json"
        }
        
        cache_key = client._build_cache_key(url, params)
        
        assert "SECRET_KEY_123" not in cache_key
        assert "api_key" not in cache_key.lower()
        assert "GDP" in cache_key
        assert "json" in cache_key
    
    def test_cache_key_excludes_token(self):
        """Cache key should not include token parameter."""
        client = FredClient()
        
        params = {
            "series_id": "UNRATE",
            "token": "bearer_token_xyz",
            "format": "json"
        }
        
        cache_key = client._build_cache_key("https://api.example.com", params)
        
        assert "bearer_token_xyz" not in cache_key
        assert "token" not in cache_key.lower()
        assert "UNRATE" in cache_key
    
    def test_cache_key_excludes_authorization(self):
        """Cache key should not include authorization parameter."""
        client = FredClient()
        
        params = {
            "series_id": "DFF",
            "authorization": "Basic abc123",
            "limit": "100"
        }
        
        cache_key = client._build_cache_key("https://api.example.com", params)
        
        assert "abc123" not in cache_key
        assert "authorization" not in cache_key.lower()
        assert "DFF" in cache_key
    
    def test_cache_key_case_insensitive_exclusion(self):
        """Cache key exclusion should be case-insensitive."""
        client = FredClient()
        
        params = {
            "series_id": "GDP",
            "API_KEY": "SECRET",
            "Api_Key": "ALSO_SECRET"
        }
        
        cache_key = client._build_cache_key("https://api.example.com", params)
        
        assert "SECRET" not in cache_key
        assert "ALSO_SECRET" not in cache_key
        assert "api_key" not in cache_key.lower()
    
    def test_cache_key_includes_non_sensitive_params(self):
        """Cache key should include all non-sensitive parameters."""
        client = FredClient()
        
        params = {
            "series_id": "CPIAUCSL",
            "observation_start": "2020-01-01",
            "observation_end": "2023-12-31",
            "file_type": "json",
            "api_key": "secret_key"
        }
        
        cache_key = client._build_cache_key("https://api.stlouisfed.org/fred/series/observations", params)
        
        # Should include these
        assert "CPIAUCSL" in cache_key
        assert "2020-01-01" in cache_key
        assert "2023-12-31" in cache_key
        assert "json" in cache_key
        
        # Should NOT include this
        assert "secret_key" not in cache_key
        assert "api_key" not in cache_key.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
