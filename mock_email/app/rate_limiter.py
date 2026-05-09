from __future__ import annotations

import time
import asyncio

from app.core.config import config
from app.core.exceptions import RateLimitExceededError


class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self._tokens = capacity
        self.refill_rate = refill_rate
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
        self._last_refill = now

    async def consume(self, tokens: float = 1.0) -> None:
        async with self._lock:
            self._refill()

            if self._tokens < tokens:
                raise RateLimitExceededError()

            self._tokens -= tokens


class RateLimiter:
    def __init__(self):
        rate = config.email.request_per_minute / 60.0
        capacity = config.email.burst_per_second
        self._bucket = TokenBucket(capacity, rate)

    async def check(self) -> None:
        await self._bucket.consume()


_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    return _rate_limiter
