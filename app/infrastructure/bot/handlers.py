"""Обработчики команд Telegram-бота."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="main_router")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Привет! Я бот-агрегатор вакансий.\n"
        "Управление — через GUI-панель на рабочем столе.\n\n"
        f"Ваш Telegram ID: <code>{message.from_user.id}</code>",
        parse_mode="HTML",
    )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    await message.answer("ℹ️ Статус воркера отображается в GUI-панели.")
