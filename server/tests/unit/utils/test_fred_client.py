"""Unit tests for the shared FredClient."""

from unittest.mock import MagicMock, patch

import pytest

from trabajo_ia_server.utils.cache import CacheManager, InMemoryCache
from trabajo_ia_server.utils.fred_client import FredAPIError, FredClient


def build_client() -> FredClient:
    cache = CacheManager(backend=InMemoryCache(default_ttl=30), enabled=True, default_ttl=30)
    cache.configure_namespace("test", 30)
    client = FredClient(cache=cache, timeout=0.1)
    return client


def mock_response(payload, *, url="https://example.com", status=200, headers=None):
    response = MagicMock()
    response.status_code = status
    response.ok = status == 200
    response.url = url
    response.headers = headers or {}
    response.json.return_value = payload
    return response


def test_fred_client_caches_successful_responses():
    client = build_client()
    payload = {"seriess": [], "count": 0}
    response = mock_response(payload)

    assert client._session is not None

    with patch.object(client._session, "get", return_value=response) as mock_get:
        first = client.get_json("https://example.com", {"q": "1"}, namespace="test", ttl=10)
        second = client.get_json("https://example.com", {"q": "1"}, namespace="test", ttl=10)

        assert first.from_cache is False
        assert second.from_cache is True
        assert mock_get.call_count == 1


def test_fred_client_does_not_cache_error_payloads():
    client = build_client()
    error_payload = {"error_code": 400, "error_message": "bad"}
    response = mock_response(error_payload)

    with patch.object(client._session, "get", return_value=response) as mock_get:
        client.get_json("https://example.com", {}, namespace="test", ttl=10)
        client.get_json("https://example.com", {}, namespace="test", ttl=10)
        assert mock_get.call_count == 2


def test_fred_client_cache_errors_when_requested():
    client = build_client()
    error_payload = {"error_code": 500, "error_message": "fail"}
    response = mock_response(error_payload)

    with patch.object(client._session, "get", return_value=response) as mock_get:
        first = client.get_json(
            "https://example.com", {}, namespace="test", ttl=10, cache_errors=True
        )
        second = client.get_json(
            "https://example.com", {}, namespace="test", ttl=10, cache_errors=True
        )

        assert first.from_cache is False
        assert second.from_cache is True
        assert mock_get.call_count == 1


def test_fred_client_raises_fred_api_error_on_http_error():
    client = build_client()
    payload = {"error_message": "bad request"}
    response = mock_response(payload, status=400)

    with patch.object(client._session, "get", return_value=response):
        with pytest.raises(FredAPIError) as exc_info:
            client.get_json("https://example.com", {}, namespace="test", ttl=10)

    error = exc_info.value
    assert error.status_code == 400
    assert "bad request" in str(error)
