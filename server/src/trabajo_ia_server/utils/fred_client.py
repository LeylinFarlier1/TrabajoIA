"""Shared FRED HTTP client with caching support."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple
from urllib.parse import urlencode

import requests
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.cache import cache_manager
from trabajo_ia_server.utils.logger import setup_logger

logger = setup_logger(__name__)


class FredAPIError(Exception):
    """Exception raised when the FRED API returns an error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.url = url
        self.payload = payload
        self.retryable = retryable

    def __str__(self) -> str:  # pragma: no cover - trivial
        if self.status_code is not None:
            return f"{self.message} (status={self.status_code})"
        return self.message


def _is_retryable_exception(exception: BaseException) -> bool:
    if isinstance(exception, requests.exceptions.RequestException):
        return True
    if isinstance(exception, FredAPIError):
        return exception.retryable
    return False


@dataclass(frozen=True)
class FredAPIResponse:
    """Lightweight representation of a FRED HTTP response."""

    payload: Dict[str, Any]
    url: str
    status_code: int
    headers: Mapping[str, Any]
    from_cache: bool = False

    def json(self) -> Dict[str, Any]:
        return self.payload

    def as_cache_hit(self) -> "FredAPIResponse":
        return FredAPIResponse(
            payload=self.payload,
            url=self.url,
            status_code=self.status_code,
            headers=self.headers,
            from_cache=True,
        )


class FredClient:
    """HTTP client for FRED API with centralized caching and retry logic."""

    def __init__(
        self,
        *,
        cache=cache_manager,
        timeout: float = 30.0,
        max_attempts: int = 3,
    ) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": f"Trabajo-IA-MCP-Server/{config.SERVER_VERSION}",
                "Accept": "application/json",
            }
        )
        self._timeout = timeout
        self._cache = cache
        self._max_attempts = max_attempts

    @staticmethod
    def _build_cache_key(url: str, params: Mapping[str, Any]) -> str:
        normalized_items: list[Tuple[str, str]] = []
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, (list, tuple, set)):
                for item in value:
                    normalized_items.append((key, str(item)))
            else:
                normalized_items.append((key, str(value)))
        normalized_items.sort()
        query = urlencode(normalized_items)
        return f"{url}?{query}" if query else url

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception(_is_retryable_exception),
        reraise=True,
    )
    def _request_with_retries(self, url: str, params: Mapping[str, Any]) -> requests.Response:
        response = self._session.get(url, params=params, timeout=self._timeout)

        if response.status_code == 429:
            reset_header = response.headers.get("X-RateLimit-Reset")
            if reset_header:
                try:
                    reset_time = float(reset_header)
                    delay = max(1.0, reset_time - time.time())
                    logger.warning("FRED rate limit hit. Sleeping for %.1f seconds", delay)
                    time.sleep(delay)
                except ValueError:
                    logger.warning("FRED rate limit hit. Retrying without delay")
            else:
                logger.warning("FRED rate limit hit. Retrying")
            raise FredAPIError(
                "Rate limit exceeded",
                status_code=429,
                url=response.url,
                retryable=True,
            )

        if 500 <= response.status_code < 600:
            raise FredAPIError(
                f"FRED API request failed with status {response.status_code}",
                status_code=response.status_code,
                url=response.url,
                retryable=True,
            )

        return response

    def get_json(
        self,
        url: str,
        params: Mapping[str, Any],
        *,
        namespace: str,
        ttl: Optional[int] = None,
        cache_errors: bool = False,
    ) -> FredAPIResponse:
        cache_key = self._build_cache_key(url, params)

        cached_value, hit = self._cache.get(namespace, cache_key)
        if hit and isinstance(cached_value, FredAPIResponse):
            logger.debug("Cache hit for namespace '%s' and key '%s'", namespace, cache_key)
            return cached_value.as_cache_hit()

        response = self._request_with_retries(url, params)

        try:
            payload = response.json()
        except ValueError as exc:  # pragma: no cover - defensive
            raise FredAPIError(
                "Invalid JSON payload returned by FRED",
                status_code=response.status_code,
                url=response.url,
            ) from exc

        if not response.ok:
            error_message = "FRED API request failed"
            if isinstance(payload, dict):
                error_message = payload.get("error_message", error_message)
            raise FredAPIError(
                error_message,
                status_code=response.status_code,
                url=response.url,
                payload=payload if isinstance(payload, dict) else None,
                retryable=False,
            )

        api_response = FredAPIResponse(
            payload=payload,
            url=response.url,
            status_code=response.status_code,
            headers=dict(response.headers),
            from_cache=False,
        )

        should_cache = cache_errors or not payload.get("error_code")
        if should_cache:
            stored = self._cache.set(namespace, cache_key, api_response, ttl=ttl)
            if stored:
                logger.debug(
                    "Stored response in cache (namespace=%s, ttl=%s)", namespace, ttl
                )

        return api_response


fred_client = FredClient()

__all__ = ["FredClient", "FredAPIError", "FredAPIResponse", "fred_client"]

