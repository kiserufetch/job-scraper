"""StatCard — карточка статистики для Dashboard."""

from __future__ import annotations

import flet as ft

from app.presentation.gui.theme import GROK_ON_SURFACE, GROK_ON_SURFACE_DIM, GROK_SURFACE_CONTAINER


class StatCard(ft.Container):
    """Карточка с заголовком и числовым значением."""

    def __init__(self, title: str, value: str = "0", icon: str = ft.Icons.INFO) -> None:
        self._title_text = ft.Text(title, size=13, color=GROK_ON_SURFACE_DIM)
        self._value_text = ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=GROK_ON_SURFACE)
        self._icon = ft.Icon(icon, size=28, color=GROK_ON_SURFACE_DIM)

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Row([self._icon, self._title_text], alignment=ft.MainAxisAlignment.START),
                    self._value_text,
                ],
                spacing=8,
            ),
            bgcolor=GROK_SURFACE_CONTAINER,
            border_radius=12,
            padding=20,
            expand=True,
        )

    def update_value(self, value: str) -> None:
        self._value_text.value = value
