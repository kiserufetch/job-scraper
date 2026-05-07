"""Tenacity retry-политика для HTTP-запросов."""

from __future__ import annotations

import httpx
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from app.shared.exceptions import ScraperError

RETRYABLE_EXCEPTIONS = (
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
    ScraperError,
)


def _before_log(retry_state: RetryCallState) -> None:
    from loguru import logger

    if retry_state.attempt_number > 1:
        logger.warning(
            "Retry #{} для {} после ошибки: {}",
            retry_state.attempt_number,
            retry_state.fn.__name__ if retry_state.fn else "?",
            retry_state.outcome.exception() if retry_state.outcome else "?",
        )


scraper_retry = retry(
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=2, max=15, jitter=3),
    before=_before_log,
    reraise=True,
)
