"""Centralized rate limiting utilities for coordinating FRED requests."""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Callable, Deque, Dict, Optional

from trabajo_ia_server.config import config
from trabajo_ia_server.utils.logger import setup_logger
from trabajo_ia_server.utils.metrics import metrics

logger = setup_logger(__name__)


class _RateWindow:
    """Sliding window tracker enforcing an upper bound on events."""

    def __init__(self, capacity: int, window_seconds: float) -> None:
        self.capacity = capacity
        self.window = window_seconds
        self._timestamps: Deque[float] = deque()

    def _prune(self, now: float) -> None:
        threshold = now - self.window
        while self._timestamps and self._timestamps[0] <= threshold:
            self._timestamps.popleft()

    def required_wait(self, now: float) -> float:
        self._prune(now)
        if len(self._timestamps) < self.capacity:
            return 0.0
        earliest = self._timestamps[0]
        return max(0.0, earliest + self.window - now)

    def record(self, timestamp: float) -> None:
        self._prune(timestamp)
        self._timestamps.append(timestamp)


class CoordinatedRateLimiter:
    """Coordinates access to FRED respecting per-second and per-minute budgets."""

    def __init__(
        self,
        per_second: Optional[int],
        per_minute: Optional[int],
        *,
        enabled: bool = True,
        time_func: Callable[[], float] | None = None,
        sleep_func: Callable[[float], None] | None = None,
    ) -> None:
        self._now = time_func or time.monotonic
        self._sleep = sleep_func or time.sleep
        self._lock = threading.RLock()
        self._penalty_until = 0.0
        self._per_second = per_second
        self._per_minute = per_minute

        windows: list[_RateWindow] = []
        if per_second and per_second > 0:
            windows.append(_RateWindow(per_second, 1.0))
        if per_minute and per_minute > 0:
            windows.append(_RateWindow(per_minute, 60.0))

        self._windows = windows
        self.enabled = enabled and bool(windows)

        if self.enabled:
            logger.info(
                "Rate limiter configured (per_second=%s, per_minute=%s)",
                per_second,
                per_minute,
            )
        else:
            logger.info("Rate limiter disabled")

    def _required_wait_locked(self, now: float) -> float:
        wait = max(0.0, self._penalty_until - now)
        for window in self._windows:
            wait = max(wait, window.required_wait(now))
        return wait

    def acquire(self) -> None:
        """Block until the next request is allowed under all configured budgets."""

        if not self.enabled:
            return

        while True:
            with self._lock:
                now = self._now()
                wait = self._required_wait_locked(now)
                if wait <= 0:
                    for window in self._windows:
                        window.record(now)
                    metrics.increment("rate_limiter_acquire_total")
                    return
            self._sleep(wait)
            metrics.observe("rate_limiter_wait_seconds", wait)

    def register_penalty(self, delay: float) -> None:
        """Extend the cooldown window after a 429 or manual throttle event."""

        if not self.enabled or delay <= 0:
            return

        with self._lock:
            now = self._now()
            penalty_until = now + delay
            if penalty_until > self._penalty_until:
                logger.warning("Applying shared backoff of %.2fs", delay)
            self._penalty_until = max(self._penalty_until, penalty_until)
        metrics.observe("rate_limiter_penalty_seconds", delay)

    def snapshot(self) -> Dict[str, Optional[float]]:
        """Return a serializable representation of the limiter state."""

        with self._lock:
            penalty_remaining = max(0.0, self._penalty_until - self._now())

        return {
            "enabled": self.enabled,
            "per_second": float(self._per_second or 0) if self._per_second else None,
            "per_minute": float(self._per_minute or 0) if self._per_minute else None,
            "penalty_seconds": penalty_remaining if penalty_remaining > 0 else 0.0,
        }


def _build_rate_limiter() -> CoordinatedRateLimiter:
    per_second, per_minute = config.get_rate_limits()
    limiter = CoordinatedRateLimiter(
        per_second,
        per_minute,
        enabled=config.FRED_RATE_LIMIT_ENABLED,
    )
    return limiter


rate_limiter = _build_rate_limiter()

__all__ = ["CoordinatedRateLimiter", "rate_limiter"]

