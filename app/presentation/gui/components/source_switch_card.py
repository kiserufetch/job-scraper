"""SourceSwitchCard — карточка-переключатель источника."""

from __future__ import annotations

from typing import Callable

import flet as ft

from app.presentation.gui.theme import GROK_ON_SURFACE, GROK_ON_SURFACE_DIM, GROK_SURFACE_CONTAINER


class SourceSwitchCard(ft.Container):
    """Карточка с названием источника и Switch для вкл/выкл."""

    def __init__(
        self,
        title: str,
        subtitle: str,
        is_enabled: bool,
        on_toggle: Callable[[bool], None],
    ) -> None:
        self._switch = ft.Switch(value=is_enabled, on_change=lambda e: on_toggle(e.control.value))

        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Column(
                        [
                            ft.Text(title, size=16, weight=ft.FontWeight.W_500, color=GROK_ON_SURFACE),
                            ft.Text(subtitle, size=12, color=GROK_ON_SURFACE_DIM),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    self._switch,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=GROK_SURFACE_CONTAINER,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
        )

    def set_enabled(self, value: bool) -> None:
        self._switch.value = value
