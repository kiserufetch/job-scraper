"""Инициализация и управление жизненным циклом aiogram-бота."""

from __future__ import annotations

from aiogram import Bot, Dispatcher
from loguru import logger

from app.infrastructure.bot.handlers import router
from app.infrastructure.bot.middlewares import AuthorizedUserMiddleware


class BotManager:
    """Управляет запуском и остановкой Telegram-бота."""

    def __init__(self, token: str, allowed_user_id: int | None = None) -> None:
        self._bot = Bot(token=token)
        self._dp = Dispatcher()
        self._auth_middleware = AuthorizedUserMiddleware(allowed_user_id)

        self._dp.update.middleware(self._auth_middleware)
        self._dp.include_router(router)

    def set_allowed_user(self, user_id: int | None) -> None:
        self._auth_middleware.set_allowed_user(user_id)

    async def start_polling(self) -> None:
        """Запустить бота в режиме polling (неблокирующий для event loop)."""
        logger.info("Запуск Telegram-бота (polling)...")
        await self._dp.start_polling(self._bot, close_bot_session=False)

    async def stop(self) -> None:
        """Остановить бота."""
        logger.info("Остановка Telegram-бота...")
        await self._dp.stop_polling()
        await self._bot.session.close()

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def dispatcher(self) -> Dispatcher:
        return self._dp
