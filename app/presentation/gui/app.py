"""Главное окно Flet-приложения: навигация + маршрутизация views."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from app.presentation.gui.components.nav_rail import AppNavRail
from app.presentation.gui.theme import GROK_BG, GROK_OUTLINE, build_dark_theme
from app.presentation.gui.views.dashboard_view import DashboardView
from app.presentation.gui.views.filters_view import FiltersView
from app.presentation.gui.views.settings_view import SettingsView
from app.presentation.gui.views.sources_view import SourcesView
from app.presentation.gui.views.telegram_channels_view import TelegramChannelsView

if TYPE_CHECKING:
    from app.infrastructure.config.container import Container


class JobScraperApp:
    """Корневой контроллер GUI: владеет page, rail и набором views."""

    def __init__(self, container: Container) -> None:
        self._container = container
        self._page: ft.Page | None = None
        self._content_area: ft.Column | None = None
        self._views: list[ft.Control] = []

    async def build(self, page: ft.Page) -> None:
        """Инициализировать страницу Flet и отрисовать UI."""
        self._page = page
        page.title = "Job Scraper — Панель управления"
        page.theme = build_dark_theme()
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = GROK_BG
        page.padding = 0
        page.window.width = 1100
        page.window.height = 720
        page.window.min_width = 900
        page.window.min_height = 600

        self._views = await self._create_views()
        self._content_area = ft.Column(
            controls=[self._views[0]],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        nav_rail = AppNavRail(on_change=self._on_nav_change)

        page.add(
            ft.Row(
                controls=[
                    nav_rail,
                    ft.VerticalDivider(width=1, color=GROK_OUTLINE),
                    ft.Container(
                        content=self._content_area,
                        expand=True,
                        padding=24,
                    ),
                ],
                expand=True,
            )
        )

    async def _create_views(self) -> list[ft.Control]:
        """Создать все view-экраны (ленивая загрузка данных)."""
        return [
            DashboardView(self._container),
            SourcesView(self._container),
            FiltersView(self._container),
            TelegramChannelsView(self._container),
            SettingsView(self._container),
        ]

    def _on_nav_change(self, index: int) -> None:
        if self._content_area is None or self._page is None:
            return
        self._content_area.controls = [self._views[index]]
        self._page.update()
