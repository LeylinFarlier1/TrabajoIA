"""Test configuration providing lightweight stubs for optional dependencies."""
from __future__ import annotations

import sys
import types


def pytest_sessionstart(session):  # pragma: no cover - pytest hook
    if "requests" not in sys.modules:
        requests_stub = types.ModuleType("requests")

        class Session:  # type: ignore[too-few-public-methods]
            def __init__(self) -> None:
                self.headers = {}

            def get(self, *args, **kwargs):  # pragma: no cover - should be mocked in tests
                raise RuntimeError("requests stub cannot perform HTTP calls")

        exceptions = types.SimpleNamespace(RequestException=Exception)

        requests_stub.Session = Session
        requests_stub.exceptions = exceptions
        sys.modules["requests"] = requests_stub

    if "tenacity" not in sys.modules:
        tenacity_stub = types.ModuleType("tenacity")

        def retry(*args, **kwargs):  # pragma: no cover - simplified decorator
            def decorator(func):
                return func

            return decorator

        def retry_if_exception(predicate):  # pragma: no cover - passthrough
            return predicate

        def stop_after_attempt(attempts):  # pragma: no cover - placeholder
            return attempts

        def wait_exponential(**kwargs):  # pragma: no cover - placeholder
            return kwargs

        tenacity_stub.retry = retry
        tenacity_stub.retry_if_exception = retry_if_exception
        tenacity_stub.stop_after_attempt = stop_after_attempt
        tenacity_stub.wait_exponential = wait_exponential
        sys.modules["tenacity"] = tenacity_stub

    if "dotenv" not in sys.modules:
        dotenv_stub = types.ModuleType("dotenv")

        def load_dotenv(*args, **kwargs):  # pragma: no cover - simple placeholder
            return False

        dotenv_stub.load_dotenv = load_dotenv
        sys.modules["dotenv"] = dotenv_stub
