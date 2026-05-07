"""Aiogram-middleware для фильтрации по авторизованному user_id."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from loguru import logger


class AuthorizedUserMiddleware(BaseMiddleware):
    """Пропускает только сообщения от target_user_id; остальные — игнорирует."""

    def __init__(self, allowed_user_id: int | None = None) -> None:
        super().__init__()
        self._allowed_id = allowed_user_id

    def set_allowed_user(self, user_id: int | None) -> None:
        self._allowed_id = user_id

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if self._allowed_id is None:
            return await handler(event, data)

        user_id: int | None = None
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                user_id = event.message.from_user.id
            elif event.callback_query and event.callback_query.from_user:
                user_id = event.callback_query.from_user.id

        if user_id is not None and user_id != self._allowed_id:
            logger.debug("Заблокировано сообщение от user_id={}", user_id)
            return None

        return await handler(event, data)
