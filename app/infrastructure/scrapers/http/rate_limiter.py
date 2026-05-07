"""Token-bucket rate limiter для контролируемой нагрузки на источники."""

from __future__ import annotations

import asyncio
import time


class TokenBucketRateLimiter:
    """Асинхронный token-bucket: позволяет контролировать частоту запросов.

    rate     — кол-во токенов, добавляемых в секунду
    capacity — максимальная ёмкость бакета (burst-размер)
    """

    def __init__(self, rate: float = 1.0, capacity: float = 3.0) -> None:
        self._rate = rate
        self._capacity = capacity
        self._tokens = capacity
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Дождаться свободного токена."""
        async with self._lock:
            self._refill()
            while self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._refill()
            self._tokens -= 1.0

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
        self._last_refill = now
