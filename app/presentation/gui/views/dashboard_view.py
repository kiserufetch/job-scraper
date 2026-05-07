"""Dashboard — главный экран: статистика + управление воркером."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from app.presentation.gui.components.stat_card import StatCard
from app.presentation.gui.theme import (
    GROK_ERROR,
    GROK_ON_SURFACE,
    GROK_ON_SURFACE_DIM,
    GROK_SUCCESS,
    GROK_SURFACE_CONTAINER,
)

if TYPE_CHECKING:
    from app.infrastructure.config.container import Container


class DashboardView(ft.Column):
    """Экран Dashboard: 3 карточки статистики + кнопка Start/Stop."""

    def __init__(self, container: Container) -> None:
        self._container = container

        self._found_card = StatCard("Найдено сегодня", "0", ft.Icons.SEARCH)
        self._sent_card = StatCard("Отправлено", "0", ft.Icons.SEND)
        self._status_card = StatCard("Статус", "Остановлен", ft.Icons.CIRCLE)

        self._start_btn = ft.ElevatedButton(
            content="Запустить воркер",
            icon=ft.Icons.PLAY_ARROW,
            style=ft.ButtonStyle(bgcolor=GROK_SUCCESS, color="#FFFFFF"),
            width=220,
            height=48,
            on_click=self._on_start,
        )
        self._stop_btn = ft.ElevatedButton(
            content="Остановить",
            icon=ft.Icons.STOP,
            style=ft.ButtonStyle(bgcolor=GROK_ERROR, color="#FFFFFF"),
            width=220,
            height=48,
            visible=False,
            on_click=self._on_stop,
        )
        self._run_now_btn = ft.OutlinedButton(
            content="Запустить сейчас",
            icon=ft.Icons.BOLT,
            width=220,
            height=48,
            on_click=self._on_run_now,
        )
        self._clear_seen_btn = ft.OutlinedButton(
            content="Очистить seen_jobs",
            icon=ft.Icons.DELETE_SWEEP,
            width=250,
            height=48,
            style=ft.ButtonStyle(color=GROK_ERROR),
            on_click=self._on_clear_seen,
        )

        super().__init__(
            controls=[
                ft.Text(
                    "Dashboard",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=GROK_ON_SURFACE,
                ),
                ft.Text(
                    "Обзор работы агрегатора вакансий",
                    size=14,
                    color=GROK_ON_SURFACE_DIM,
                ),
                ft.Container(height=16),
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(self._found_card, col={"sm": 12, "md": 4}),
                        ft.Container(self._sent_card, col={"sm": 12, "md": 4}),
                        ft.Container(self._status_card, col={"sm": 12, "md": 4}),
                    ],
                ),
                ft.Container(height=24),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._start_btn,
                            self._stop_btn,
                            self._run_now_btn,
                            self._clear_seen_btn,
                        ],
                        spacing=16,
                        wrap=True,
                    ),
                    bgcolor=GROK_SURFACE_CONTAINER,
                    border_radius=12,
                    padding=20,
                ),
            ],
            spacing=8,
        )

    async def _on_start(self, _e: ft.ControlEvent) -> None:
        from app.presentation.gui.view_models.dashboard_vm import DashboardViewModel

        vm = DashboardViewModel(self._container)
        await vm.start_worker()
        self._start_btn.visible = False
        self._stop_btn.visible = True
        self._status_card.update_value("Работает")
        if self.page:
            self.page.update()

    async def _on_stop(self, _e: ft.ControlEvent) -> None:
        from app.presentation.gui.view_models.dashboard_vm import DashboardViewModel

        vm = DashboardViewModel(self._container)
        await vm.stop_worker()
        self._start_btn.visible = True
        self._stop_btn.visible = False
        self._status_card.update_value("Остановлен")
        if self.page:
            self.page.update()

    async def _on_run_now(self, _e: ft.ControlEvent) -> None:
        from app.presentation.gui.view_models.dashboard_vm import DashboardViewModel

        vm = DashboardViewModel(self._container)
        self._status_card.update_value("Выполняется…")
        if self.page:
            self.page.update()
        await vm.run_now()
        await self._refresh_stats()

    async def _on_clear_seen(self, _e: ft.ControlEvent) -> None:
        """Удалить все записи из seen_jobs (debug)."""
        count = await self._container.seen_jobs_repo.clear_all()
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Удалено {count} записей из seen_jobs"), open=True
            )
            self.page.update()

    async def _refresh_stats(self) -> None:
        stats = await self._container.daily_stats_repo.get_or_create_today()
        self._found_card.update_value(str(stats.found_count))
        self._sent_card.update_value(str(stats.sent_count))
        if self.page:
            self.page.update()
