"""Tests for the coordinated rate limiter."""

from __future__ import annotations

from trabajo_ia_server.utils.rate_limiter import CoordinatedRateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, delay: float) -> None:
        self.now += delay


def test_rate_limiter_respects_per_second_budget():
    clock = FakeClock()
    limiter = CoordinatedRateLimiter(
        per_second=2,
        per_minute=None,
        time_func=clock.monotonic,
        sleep_func=clock.sleep,
    )

    limiter.acquire()
    limiter.acquire()
    limiter.acquire()

    # Third acquire should wait 1s to stay within 2 req/s
    assert clock.now == 1.0


def test_rate_limiter_penalty_extends_wait():
    clock = FakeClock()
    limiter = CoordinatedRateLimiter(
        per_second=5,
        per_minute=10,
        time_func=clock.monotonic,
        sleep_func=clock.sleep,
    )

    limiter.register_penalty(3.0)
    limiter.acquire()

    assert clock.now == 3.0
