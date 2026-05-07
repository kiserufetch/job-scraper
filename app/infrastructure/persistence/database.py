"""Управление AsyncEngine и фабрикой сессий (SQLite WAL mode)."""

from __future__ import annotations

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.domain.enums import SourceType
from app.infrastructure.persistence.models import AppSettingsModel, Base, SourceModel
from app.shared.constants import DB_URL


def _set_sqlite_wal(dbapi_conn, _connection_record) -> None:  # noqa: ANN001
    """Включить WAL-режим и оптимизации при каждом новом соединении."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class DatabaseManager:
    """Инкапсулирует создание engine, миграции и начальные данные."""

    def __init__(self, url: str = DB_URL) -> None:
        self._engine: AsyncEngine = create_async_engine(url, echo=False)
        event.listen(self._engine.sync_engine, "connect", _set_sqlite_wal)
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

    async def init(self) -> None:
        """Создать таблицы и заполнить начальные данные."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await self._run_migrations()
        await self._seed_defaults()

    async def _run_migrations(self) -> None:
        """Лёгкие миграции для добавления новых колонок в существующую БД."""
        async with self._session_factory() as session:
            try:
                await session.execute(
                    text("ALTER TABLE site_filters ADD COLUMN search_remote BOOLEAN DEFAULT 1")
                )
                await session.commit()
            except Exception:
                await session.rollback()

    async def _seed_defaults(self) -> None:
        """Создать начальные записи, если БД пуста."""
        async with self._session_factory() as session:
            existing = await session.get(AppSettingsModel, 1)
            if existing is None:
                session.add(AppSettingsModel(id=1))

            for src_type in SourceType:
                result = await session.execute(
                    text("SELECT id FROM sources WHERE type = :t"),
                    {"t": src_type.value},
                )
                if result.scalar_one_or_none() is None:
                    session.add(SourceModel(type=src_type.value))

            await session.commit()

    async def close(self) -> None:
        await self._engine.dispose()
