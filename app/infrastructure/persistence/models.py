"""SQLAlchemy ORM-модели, отражающие доменные сущности."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""


class AppSettingsModel(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    target_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    scrape_interval_minutes: Mapped[int] = mapped_column(Integer, default=30)
    is_worker_running: Mapped[bool] = mapped_column(Boolean, default=False)


class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    filter: Mapped[SiteFilterModel | None] = relationship(
        back_populates="source", uselist=False, cascade="all, delete-orphan"
    )


class SiteFilterModel(Base):
    __tablename__ = "site_filters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id"), unique=True, nullable=False
    )
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    stack: Mapped[list] = mapped_column(JSON, default=list)
    city: Mapped[str] = mapped_column(String(100), default="")
    query_text: Mapped[str] = mapped_column(String(500), default="")
    search_remote: Mapped[bool] = mapped_column(Boolean, default=True)

    source: Mapped[SourceModel] = relationship(back_populates="filter")


class TelegramChannelModel(Base):
    __tablename__ = "telegram_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_username: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    keywords: Mapped[list] = mapped_column(JSON, default=list)


class JobModel(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(200), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str] = mapped_column(String(300), default="")
    salary: Mapped[str] = mapped_column(String(200), default="")
    city: Mapped[str] = mapped_column(String(200), default="")
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    work_placement: Mapped[str] = mapped_column(String(20), default="unknown")
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SeenJobModel(Base):
    __tablename__ = "seen_jobs"

    hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    seen_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class DailyStatsModel(Base):
    __tablename__ = "daily_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    found_count: Mapped[int] = mapped_column(Integer, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
