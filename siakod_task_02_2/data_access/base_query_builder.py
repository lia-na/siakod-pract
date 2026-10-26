"""Общая часть всех построителей: хранение и проверка того, что запросил клиент.

Каждое хранилище наследует этот класс и реализует ТОЛЬКО build() -
то есть превращение собранных данных в запрос на своём «языке».
"""
from __future__ import annotations

from typing import Any, Optional, Sequence

from data_access.interfaces import IQueryBuilder

ALLOWED_OPERATORS = {"=", "!=", "<", "<=", ">", ">="}


class BaseQueryBuilder(IQueryBuilder):
    def __init__(self) -> None:
        self._table: Optional[str] = None
        self._columns: list[str] = []
        self._conditions: list[tuple[str, str, Any]] = []  # (колонка, оператор, значение)
        self._limit: Optional[int] = None

    def select(self, table: str, columns: Sequence[str] = ()) -> BaseQueryBuilder:
        self._check_identifier(table)
        for column in columns:
            self._check_identifier(column)
        self._table = table
        self._columns = list(columns)
        return self

    def where(self, column: str, operator: str, value: Any) -> BaseQueryBuilder:
        self._check_identifier(column)
        if operator not in ALLOWED_OPERATORS:
            raise ValueError(f"Недопустимый оператор: {operator!r}")
        self._conditions.append((column, operator, value))
        return self

    def limit(self, count: int) -> BaseQueryBuilder:
        if count < 0:
            raise ValueError("limit не может быть отрицательным")
        self._limit = count
        return self

    # --- помощники для наследников -------------------------------------
    def _check_ready(self) -> None:
        if self._table is None:
            raise ValueError("Сначала вызовите select(): не указана таблица")

    @staticmethod
    def _check_identifier(name: str) -> None:
        # Имена таблиц/колонок вставляются в текст запроса, поэтому
        # пускаем только безопасные имена (буквы, цифры, подчёркивание).
        if not name.isidentifier():
            raise ValueError(f"Недопустимое имя: {name!r}")
