"""NavigationRail — боковая навигация в стиле Grok."""

from __future__ import annotations

from typing import Callable

import flet as ft


class AppNavRail(ft.NavigationRail):
    """Боковая навигация: Dashboard / Sources / Filters / Telegram / Settings."""

    def __init__(self, on_change: Callable[[int], None]) -> None:
        super().__init__(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=80,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SOURCE_OUTLINED,
                    selected_icon=ft.Icons.SOURCE,
                    label="Источники",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FILTER_ALT_OUTLINED,
                    selected_icon=ft.Icons.FILTER_ALT,
                    label="Фильтры",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.TELEGRAM,
                    selected_icon=ft.Icons.TELEGRAM,
                    label="Telegram",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Настройки",
                ),
            ],
            on_change=lambda e: on_change(e.control.selected_index),
        )
