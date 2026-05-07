"""Перечисления доменного слоя."""

from enum import StrEnum


class SourceType(StrEnum):
    """Тип источника вакансий."""

    HH = "hh"
    HABR = "habr"
    GEEKJOB = "geekjob"
    TELEGRAM = "telegram"


class GradeLevel(StrEnum):
    """Уровень грейда (опыта) для фильтрации вакансий."""

    INTERN = "intern"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"
