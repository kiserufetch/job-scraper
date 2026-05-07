"""Загрузка секретов из .env через pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    """Минимальная конфигурация из .env (только секреты)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    tg_bot_token: str
    api_id: int
    api_hash: str
