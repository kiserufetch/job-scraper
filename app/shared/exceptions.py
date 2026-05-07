"""Кастомные исключения проекта."""


class ScraperError(Exception):
    """Ошибка при парсинге источника."""


class NotifierError(Exception):
    """Ошибка при отправке уведомления."""


class ConfigError(Exception):
    """Ошибка конфигурации."""
