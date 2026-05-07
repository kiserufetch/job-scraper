"""Telegram Channels view — управление каналами и ключевыми словами."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from app.domain.entities import TelegramChannel
from app.presentation.gui.theme import (
    GROK_ERROR,
    GROK_ON_SURFACE,
    GROK_ON_SURFACE_DIM,
    GROK_SURFACE_CONTAINER,
)

if TYPE_CHECKING:
    from app.infrastructure.config.container import Container


class TelegramChannelsView(ft.Column):
    """Экран управления TG-каналами: добавление, keywords, удаление."""

    def __init__(self, container: Container) -> None:
        self._container = container
        self._channels_list = ft.Column(spacing=8)
        self._username_field = ft.TextField(
            label="@username канала",
            hint_text="python_jobs",
            width=250,
        )
        self._keywords_field = ft.TextField(
            label="Ключевые слова (через запятую)",
            hint_text="python, django, fastapi",
            expand=True,
        )
        self._add_btn = ft.ElevatedButton(
            content="Добавить",
            icon=ft.Icons.ADD,
            on_click=self._on_add,
        )

        super().__init__(
            controls=[
                ft.Text(
                    "Telegram-каналы",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=GROK_ON_SURFACE,
                ),
                ft.Text(
                    "Каналы для парсинга вакансий с индивидуальными ключевыми словами",
                    size=14,
                    color=GROK_ON_SURFACE_DIM,
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row([self._username_field, self._keywords_field]),
                            ft.Row([self._add_btn], alignment=ft.MainAxisAlignment.END),
                        ],
                        spacing=12,
                    ),
                    bgcolor=GROK_SURFACE_CONTAINER,
                    border_radius=12,
                    padding=20,
                ),
                ft.Container(height=16),
                self._channels_list,
            ],
            spacing=8,
        )

    def did_mount(self) -> None:
        if self.page:
            self.page.run_task(self._load_channels)

    async def _load_channels(self) -> None:
        channels = await self._container.telegram_channel_repo.get_all()
        self._channels_list.controls = [self._build_channel_row(ch) for ch in channels]
        if self.page:
            self.page.update()

    def _build_channel_row(self, channel: TelegramChannel) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        [
                            ft.Text(
                                f"@{channel.channel_username}",
                                size=15,
                                weight=ft.FontWeight.W_500,
                                color=GROK_ON_SURFACE,
                            ),
                            ft.Text(
                                f"Слова: {', '.join(channel.keywords) or '(все сообщения)'}",
                                size=12,
                                color=GROK_ON_SURFACE_DIM,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Switch(
                        value=channel.is_enabled,
                        on_change=lambda e, ch=channel: (
                            self.page.run_task(self._toggle_channel, ch, e.control.value)
                            if self.page
                            else None
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=GROK_ERROR,
                        tooltip="Удалить",
                        on_click=lambda _e, ch=channel: (
                            self.page.run_task(self._delete_channel, ch)
                            if self.page
                            else None
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=GROK_SURFACE_CONTAINER,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        )

    async def _on_add(self, _e: ft.ControlEvent) -> None:
        username = (self._username_field.value or "").strip().lstrip("@")
        if not username:
            return

        keywords = [
            kw.strip()
            for kw in (self._keywords_field.value or "").split(",")
            if kw.strip()
        ]

        channel = TelegramChannel(
            channel_username=username,
            is_enabled=True,
            keywords=keywords,
        )
        await self._container.telegram_channel_repo.add(channel)

        self._username_field.value = ""
        self._keywords_field.value = ""
        await self._load_channels()

    async def _toggle_channel(self, channel: TelegramChannel, enabled: bool) -> None:
        channel.is_enabled = enabled
        await self._container.telegram_channel_repo.update(channel)

    async def _delete_channel(self, channel: TelegramChannel) -> None:
        if channel.id is not None:
            await self._container.telegram_channel_repo.delete(channel.id)
        await self._load_channels()
