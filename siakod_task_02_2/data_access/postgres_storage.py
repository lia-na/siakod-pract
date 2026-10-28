from __future__ import annotations

from data_access.base_query_builder import BaseQueryBuilder
from data_access.interfaces import (
    IConnection,
    IDataAccessFactory,
    IQueryBuilder,
    ITransaction,
    Output,
    Query,
)
from data_access.printing import PrintingConnection, PrintingTransaction


class PostgresConnection(PrintingConnection):
    TAG = "PostgreSQL"


class PostgresTransaction(PrintingTransaction):
    TAG = "PostgreSQL"
    BEGIN_TEXT = "BEGIN"
    COMMIT_TEXT = "COMMIT"
    ROLLBACK_TEXT = "ROLLBACK"


class PostgresQueryBuilder(BaseQueryBuilder):
    def build(self) -> Query:
        self._check_ready()
        columns = ", ".join(f'"{c}"' for c in self._columns) or "*"
        sql = f'SELECT {columns} FROM "{self._table}"'
        if self._conditions:
            parts = [
                f'"{column}" {operator} ${number}'
                for number, (column, operator, _) in enumerate(self._conditions, start=1)
            ]
            sql += " WHERE " + " AND ".join(parts)
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        params = tuple(value for _, _, value in self._conditions)
        return Query(sql + ";", params)


class PostgresFactory(IDataAccessFactory):
    def __init__(self, out: Output = print) -> None:
        self._out = out

    def create_connection(self) -> IConnection:
        return PostgresConnection(self._out)

    def create_query_builder(self) -> IQueryBuilder:
        return PostgresQueryBuilder()

    def create_transaction(self) -> ITransaction:
        return PostgresTransaction(self._out)
