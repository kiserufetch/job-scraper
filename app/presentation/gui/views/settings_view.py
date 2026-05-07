"""Settings view — глобальные настройки: User ID, интервал таймера."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from app.presentation.gui.theme import (
    GROK_ON_SURFACE,
    GROK_ON_SURFACE_DIM,
    GROK_SUCCESS,
    GROK_SURFACE_CONTAINER,
)

if TYPE_CHECKING:
    from app.infrastructure.config.container import Container


class SettingsView(ft.Column):
    """Экран настроек: Telegram User ID и интервал скрапинга."""

    def __init__(self, container: Container) -> None:
        self._container = container

        self._user_id_field = ft.TextField(
            label="Telegram User ID",
            hint_text="123456789",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )
        self._interval_field = ft.TextField(
            label="Интервал (мин.)",
            hint_text="30",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
        )
        self._save_btn = ft.ElevatedButton(
            content="Сохранить настройки",
            icon=ft.Icons.SAVE,
            style=ft.ButtonStyle(bgcolor=GROK_SUCCESS, color="#FFFFFF"),
            on_click=self._on_save,
        )
        self._status_text = ft.Text("", size=13, color=GROK_ON_SURFACE_DIM)

        super().__init__(
            controls=[
                ft.Text("Настройки", size=28, weight=ft.FontWeight.BOLD, color=GROK_ON_SURFACE),
                ft.Text(
                    "Общие параметры работы агрегатора",
                    size=14,
                    color=GROK_ON_SURFACE_DIM,
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Telegram User ID",
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color=GROK_ON_SURFACE,
                            ),
                            ft.Text(
                                "ID пользователя, которому бот будет отправлять вакансии. "
                                "Узнать можно командой /start в боте.",
                                size=12,
                                color=GROK_ON_SURFACE_DIM,
                            ),
                            self._user_id_field,
                            ft.Container(height=16),
                            ft.Text(
                                "Интервал сканирования",
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color=GROK_ON_SURFACE,
                            ),
                            ft.Text(
                                "Как часто воркер будет проверять источники (в минутах).",
                                size=12,
                                color=GROK_ON_SURFACE_DIM,
                            ),
                            self._interval_field,
                            ft.Container(height=16),
                            ft.Row(
                                [self._save_btn, self._status_text],
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=16,
                            ),
                        ],
                        spacing=6,
                    ),
                    bgcolor=GROK_SURFACE_CONTAINER,
                    border_radius=12,
                    padding=24,
                ),
            ],
            spacing=8,
        )

    def did_mount(self) -> None:
        if self.page:
            self.page.run_task(self._load_settings)

    async def _load_settings(self) -> None:
        settings = await self._container.settings_repo.get()
        if settings.target_user_id:
            self._user_id_field.value = str(settings.target_user_id)
        self._interval_field.value = str(settings.scrape_interval_minutes)
        if self.page:
            self.page.update()

    async def _on_save(self, _e: ft.ControlEvent) -> None:
        settings = await self._container.settings_repo.get()

        user_id_str = (self._user_id_field.value or "").strip()
        if user_id_str.isdigit():
            settings.target_user_id = int(user_id_str)
        else:
            settings.target_user_id = None

        interval_str = (self._interval_field.value or "").strip()
        if interval_str.isdigit() and int(interval_str) > 0:
            settings.scrape_interval_minutes = int(interval_str)

        await self._container.settings_repo.update(settings)

        self._status_text.value = "✓ Сохранено"
        if self.page:
            self.page.update()
