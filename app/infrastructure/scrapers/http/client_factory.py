"""Фабрика httpx.AsyncClient с http/2, ротацией UA и rate-limiter'ом.

Проблема CERTIFICATE_VERIFY_FAILED на Windows для российских сайтов
(geekjob.ru с сертификатом Russian Trusted CA) решается через truststore —
он использует системное хранилище сертификатов Windows, в котором обычно
уже есть нужные корневые CA (через установленный браузер/Минцифры).
"""

from __future__ import annotations

import ssl

import httpx
import truststore

from app.infrastructure.scrapers.http.rate_limiter import TokenBucketRateLimiter
from app.infrastructure.scrapers.http.user_agents import get_default_headers


def _make_ssl_context() -> ssl.SSLContext:
    """SSLContext поверх системного хранилища (Windows / macOS / Linux)."""
    return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


class HttpClientFactory:
    """Создаёт и управляет жизненным циклом httpx.AsyncClient."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._rate_limiters: dict[str, TokenBucketRateLimiter] = {}

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                http2=True,
                headers=get_default_headers(),
                timeout=httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0),
                limits=httpx.Limits(max_connections=30, max_keepalive_connections=10),
                follow_redirects=True,
                verify=_make_ssl_context(),
            )
        return self._client

    def rate_limiter_for(self, domain: str, rate: float = 1.0) -> TokenBucketRateLimiter:
        if domain not in self._rate_limiters:
            self._rate_limiters[domain] = TokenBucketRateLimiter(rate=rate, capacity=3.0)
        return self._rate_limiters[domain]

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
