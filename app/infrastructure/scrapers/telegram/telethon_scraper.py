"""Скрейпер Telegram-каналов через Telethon."""

from __future__ import annotations

from collections.abc import AsyncIterator

from loguru import logger
from telethon import TelegramClient
from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    UsernameNotOccupiedError,
)

from app.application.interfaces.repositories import ITelegramChannelRepository
from app.application.interfaces.scrapers import IJobScraper
from app.domain.entities import Job, SiteFilter
from app.infrastructure.scrapers.telegram.message_parser import (
    message_matches_keywords,
    message_to_job,
)

_MESSAGES_LIMIT = 50


class TelethonScraper(IJobScraper):
    """Парсит включённые TG-каналы через Telethon user-клиент."""

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        channel_repo: ITelegramChannelRepository,
    ) -> None:
        self._api_id = api_id
        self._api_hash = api_hash
        self._channel_repo = channel_repo
        self._client: TelegramClient | None = None

    async def _ensure_client(self) -> TelegramClient:
        if self._client is None or not self._client.is_connected():
            self._client = TelegramClient("data/tg_session", self._api_id, self._api_hash)
            await self._client.start()
        return self._client

    async def fetch(self, site_filter: SiteFilter) -> AsyncIterator[Job]:
        channels = await self._channel_repo.get_enabled()
        if not channels:
            return

        client = await self._ensure_client()

        for channel in channels:
            try:
                async for job in self._parse_channel(
                    client, channel.channel_username, channel.keywords
                ):
                    yield job
            except (ChannelInvalidError, ChannelPrivateError, UsernameNotOccupiedError) as exc:
                logger.warning("TG канал @{} недоступен: {}", channel.channel_username, exc)
            except Exception as exc:
                logger.error(
                    "TG: ошибка парсинга канала @{}: {}", channel.channel_username, exc
                )

    @staticmethod
    async def _parse_channel(
        client: TelegramClient,
        username: str,
        keywords: list[str],
    ) -> AsyncIterator[Job]:
        entity = await client.get_entity(username)
        channel_id = entity.id

        async for msg in client.iter_messages(entity, limit=_MESSAGES_LIMIT):
            if not msg.text:
                continue
            if not message_matches_keywords(msg.text, keywords):
                continue
            yield message_to_job(
                channel_id=channel_id,
                channel_username=username,
                message_id=msg.id,
                text=msg.text,
                date=msg.date,
            )

    async def close(self) -> None:
        if self._client and self._client.is_connected():
            await self._client.disconnect()
