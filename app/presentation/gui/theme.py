"""Тёмная тема Material 3 в стиле Grok Chat."""

import flet as ft

GROK_BG = "#0F0F0F"
GROK_SURFACE = "#171717"
GROK_SURFACE_CONTAINER = "#1F1F1F"
GROK_ON_SURFACE = "#E5E5E5"
GROK_ON_SURFACE_DIM = "#999999"
GROK_OUTLINE = "#2A2A2A"
GROK_PRIMARY = "#FFFFFF"
GROK_ON_PRIMARY = "#000000"
GROK_ERROR = "#FF4D4D"
GROK_SUCCESS = "#4CAF50"


def build_dark_theme() -> ft.Theme:
    """Собрать тему Flet Material 3 с Grok-палитрой.

    В актуальном Flet ColorScheme соответствует M3: полей background/on_background
    и surface_variant нет — используем surface_dim и surface_container.
    """
    return ft.Theme(
        use_material3=True,
        color_scheme=ft.ColorScheme(
            primary=GROK_PRIMARY,
            on_primary=GROK_ON_PRIMARY,
            surface_dim=GROK_BG,
            surface=GROK_SURFACE,
            on_surface=GROK_ON_SURFACE,
            on_surface_variant=GROK_ON_SURFACE_DIM,
            surface_container=GROK_SURFACE_CONTAINER,
            outline=GROK_OUTLINE,
            error=GROK_ERROR,
            on_error="#FFFFFF",
            secondary=GROK_ON_SURFACE_DIM,
        ),
    )
