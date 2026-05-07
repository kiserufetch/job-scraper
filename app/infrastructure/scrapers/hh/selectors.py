"""CSS-селекторы для парсинга страницы поиска hh.ru.

После закрытия публичного API hh.ru (декабрь 2025) парсим HTML напрямую.
Используются стабильные data-qa атрибуты, на которые завязаны Selenium-тесты hh.
"""

from __future__ import annotations

VACANCY_CARD = '[data-qa="vacancy-serp__vacancy"]'
TITLE = '[data-qa="serp-item__title"]'
COMPANY = '[data-qa="vacancy-serp__vacancy-employer"], [data-qa="vacancy-serp__vacancy-employer-text"]'
SALARY = '[data-qa="vacancy-serp__vacancy-compensation"]'
ADDRESS = '[data-qa="vacancy-serp__vacancy-address"]'
SCHEDULE = '[data-qa="vacancy-label-work-schedule"]'
SNIPPET_REQUIREMENT = '[data-qa="vacancy-serp__vacancy_snippet_requirement"]'
SNIPPET_RESPONSIBILITY = '[data-qa="vacancy-serp__vacancy_snippet_responsibility"]'
