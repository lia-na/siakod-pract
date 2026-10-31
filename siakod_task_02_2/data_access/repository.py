from __future__ import annotations

from typing import Any

from data_access.interfaces import IDataAccessFactory, Query


class UserRepository:
    def __init__(self, factory: IDataAccessFactory) -> None:
        self._factory = factory
        self._connection = factory.create_connection()

    def find_adults(self, min_age: int = 18, limit: int = 10) -> list[dict[str, Any]]:
        query = (
            self._factory.create_query_builder()
            .select("users", ["id", "name"])
            .where("age", ">=", min_age)
            .limit(limit)
            .build()
        )
        return self._run_in_transaction(query)

    def find_by_city(self, city: str, min_age: int = 0) -> list[dict[str, Any]]:
        query = (
            self._factory.create_query_builder()
            .select("users")
            .where("city", "=", city)
            .where("age", ">=", min_age)
            .build()
        )
        return self._run_in_transaction(query)

    def close(self) -> None:
        self._connection.close()

    def _run_in_transaction(self, query: Query) -> list[dict[str, Any]]:
        # with: BEGIN -> запрос -> COMMIT; при ошибке вместо COMMIT будет ROLLBACK
        with self._factory.create_transaction():
            return self._connection.execute(query.sql, query.params)
