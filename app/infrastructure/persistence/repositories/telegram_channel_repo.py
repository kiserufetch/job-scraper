"""Репозиторий Telegram-каналов."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.repositories import ITelegramChannelRepository
from app.domain.entities import TelegramChannel
from app.infrastructure.persistence.models import TelegramChannelModel


class TelegramChannelRepository(ITelegramChannelRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def get_all(self) -> list[TelegramChannel]:
        async with self._sf() as session:
            result = await session.execute(select(TelegramChannelModel))
            return [self._to_entity(m) for m in result.scalars().all()]

    async def get_enabled(self) -> list[TelegramChannel]:
        async with self._sf() as session:
            stmt = select(TelegramChannelModel).where(
                TelegramChannelModel.is_enabled.is_(True)
            )
            result = await session.execute(stmt)
            return [self._to_entity(m) for m in result.scalars().all()]

    async def add(self, channel: TelegramChannel) -> TelegramChannel:
        async with self._sf() as session:
            model = TelegramChannelModel(
                channel_username=channel.channel_username,
                is_enabled=channel.is_enabled,
                keywords=channel.keywords,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            channel.id = model.id
            return channel

    async def update(self, channel: TelegramChannel) -> None:
        async with self._sf() as session:
            model = await session.get(TelegramChannelModel, channel.id)
            if model is None:
                return
            model.channel_username = channel.channel_username
            model.is_enabled = channel.is_enabled
            model.keywords = channel.keywords
            await session.commit()

    async def delete(self, channel_id: int) -> None:
        async with self._sf() as session:
            model = await session.get(TelegramChannelModel, channel_id)
            if model is not None:
                await session.delete(model)
                await session.commit()

    @staticmethod
    def _to_entity(m: TelegramChannelModel) -> TelegramChannel:
        return TelegramChannel(
            id=m.id,
            channel_username=m.channel_username,
            is_enabled=m.is_enabled,
            keywords=m.keywords or [],
        )
