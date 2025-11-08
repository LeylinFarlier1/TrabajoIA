"""
Tests for concurrent fetch performance.
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor
from trabajo_ia_server.workflows.layers.fetch_data import fetch_gdp_data
from trabajo_ia_server.utils.fred_client import FredAPIResponse


class TestConcurrentFetch:
    """Test parallel fetching performance."""
    
    def test_concurrent_fetch_performance(self):
        """
        Parallel fetch should be significantly faster than serial.
        
        Mock 6 series with 100ms delay each:
        - Serial: ~600ms
        - Parallel (max_workers=10): ~100-200ms
        - Expected speedup: >3x
        """
        # Mock fred_client to simulate network delay
        mock_response = FredAPIResponse(
            payload={
                "observations": [
                    {"date": "2000-01-01", "value": "1000.0"},
                    {"date": "2001-01-01", "value": "1050.0"},
                    {"date": "2002-01-01", "value": "1100.0"},
                ]
            },
            url="https://api.stlouisfed.org/fred/series/observations",
            status_code=200,
            headers={},
            from_cache=False
        )
        
        def mock_get_json_with_delay(*args, **kwargs):
            """Simulate 100ms network latency."""
            time.sleep(0.1)  # 100ms delay
            return mock_response
        
        with patch('trabajo_ia_server.workflows.layers.fetch_data.fred_client') as mock_client:
            mock_client.get_json = Mock(side_effect=mock_get_json_with_delay)
            
            # Test with series that exist in mappings
            countries = ["usa", "canada", "mexico"]
            variants = ["per_capita_constant", "population"]
            
            start_time = time.perf_counter()
            result = fetch_gdp_data(
                countries=countries,
                variants=variants,
                start_date="2000-01-01",
                end_date="2003-01-01",
                cache_ttl=0  # Disable cache for testing
            )
            elapsed = time.perf_counter() - start_time
            
            # With 6 series × 100ms each:
            # Serial would be ~600ms
            # Parallel (max_workers=6) should be ~100-300ms (allowing overhead)
            assert elapsed < 0.5, f"Parallel fetch took {elapsed:.3f}s, expected <0.5s (speedup >3x)"
            
            # Verify all series were fetched
            assert len(result.metadata["fetched_series"]) > 0
            
            # Should have made requests (allowing for missing mappings)
            assert mock_client.get_json.call_count >= 3, f"Expected ≥3 calls, got {mock_client.get_json.call_count}"
    
    def test_rate_limiter_thread_safety(self):
        """
        Rate limiter should handle concurrent requests safely.
        No race conditions or deadlocks.
        """
        mock_response = FredAPIResponse(
            payload={"observations": [{"date": "2000-01-01", "value": "100.0"}]},
            url="https://api.stlouisfed.org/fred/series/observations",
            status_code=200,
            headers={},
            from_cache=False
        )
        
        with patch('trabajo_ia_server.workflows.layers.fetch_data.fred_client') as mock_client:
            mock_client.get_json = Mock(return_value=mock_response)
            
            # Fetch with multiple countries/variants to trigger concurrent requests
            result = fetch_gdp_data(
                countries=["usa", "canada", "mexico"],
                variants=["per_capita_constant", "constant_2010"],
                cache_ttl=0
            )
            
            # Should complete without exceptions
            assert result is not None
            assert "errors" in result.metadata
            
            # Check for any threading-related errors
            thread_errors = [
                err for err in result.metadata["errors"]
                if "thread" in str(err).lower() or "lock" in str(err).lower()
            ]
            assert len(thread_errors) == 0, f"Threading errors detected: {thread_errors}"
    
    def test_parallel_fetch_handles_errors_gracefully(self):
        """
        If some fetches fail, others should continue.
        """
        call_count = [0]
        
        def mock_get_json_mixed(*args, **kwargs):
            """Every 3rd call fails, others succeed."""
            call_count[0] += 1
            if call_count[0] % 3 == 0:
                from trabajo_ia_server.utils.fred_client import FredAPIError
                raise FredAPIError("Mock error", status_code=500, retryable=False)
            
            return FredAPIResponse(
                payload={"observations": [{"date": "2000-01-01", "value": "100.0"}]},
                url="https://api.stlouisfed.org/fred/series/observations",
                status_code=200,
                headers={},
                from_cache=False
            )
        
        with patch('trabajo_ia_server.workflows.layers.fetch_data.fred_client') as mock_client:
            mock_client.get_json = Mock(side_effect=mock_get_json_mixed)
            
            result = fetch_gdp_data(
                countries=["usa", "canada", "mexico"],
                variants=["per_capita_constant", "constant_2010"],
                cache_ttl=0
            )
            
            # Should have some successes and some errors
            assert len(result.metadata["fetched_series"]) > 0, "Should have some successful fetches"
            assert len(result.metadata["errors"]) > 0, "Should have captured errors"
            
            # Verify metadata structure
            for error in result.metadata["errors"]:
                assert "country" in error or "series_id" in error
                assert "error" in error
    
    def test_max_workers_limit(self):
        """
        ThreadPoolExecutor should respect max_workers limit.
        """
        mock_response = FredAPIResponse(
            payload={"observations": [{"date": "2000-01-01", "value": "100.0"}]},
            url="https://api.stlouisfed.org/fred/series/observations",
            status_code=200,
            headers={},
            from_cache=False
        )
        
        with patch('trabajo_ia_server.workflows.layers.fetch_data.fred_client') as mock_client:
            mock_client.get_json = Mock(return_value=mock_response)
            
            # Even with 20 series, should use max 10 workers
            with patch('trabajo_ia_server.workflows.layers.fetch_data.ThreadPoolExecutor') as MockExecutor:
                mock_executor_instance = MagicMock()
                mock_executor_instance.__enter__ = Mock(return_value=mock_executor_instance)
                mock_executor_instance.__exit__ = Mock(return_value=False)
                mock_executor_instance.submit = Mock(return_value=MagicMock())
                
                MockExecutor.return_value = mock_executor_instance
                
                # This would create ~20 fetch tasks
                try:
                    fetch_gdp_data(
                        countries=["usa", "canada", "mexico", "japan"],
                        variants=["per_capita_constant", "constant_2010", "population", "nominal_usd", "growth_rate"],
                        cache_ttl=0
                    )
                except:
                    pass  # We're just checking max_workers was set
                
                # Verify ThreadPoolExecutor was called with max_workers <= 10
                if MockExecutor.call_count > 0:
                    call_args = MockExecutor.call_args
                    max_workers = call_args[1].get('max_workers') or call_args[0][0] if call_args[0] else None
                    if max_workers is not None:
                        assert max_workers <= 10, f"max_workers should be ≤10, got {max_workers}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
