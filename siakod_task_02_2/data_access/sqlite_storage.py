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


class SqliteConnection(PrintingConnection):
    TAG = "SQLite"


class SqliteTransaction(PrintingTransaction):
    TAG = "SQLite"
    BEGIN_TEXT = "BEGIN TRANSACTION"
    COMMIT_TEXT = "COMMIT TRANSACTION"
    ROLLBACK_TEXT = "ROLLBACK TRANSACTION"


class SqliteQueryBuilder(BaseQueryBuilder):
    def build(self) -> Query:
        self._check_ready()
        columns = ", ".join(self._columns) or "*"
        sql = f"SELECT {columns} FROM {self._table}"
        if self._conditions:
            parts = [f"{column} {operator} ?" for column, operator, _ in self._conditions]
            sql += " WHERE " + " AND ".join(parts)
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        params = tuple(value for _, _, value in self._conditions)
        return Query(sql + ";", params)


class SqliteFactory(IDataAccessFactory):
    def __init__(self, out: Output = print) -> None:
        self._out = out

    def create_connection(self) -> IConnection:
        return SqliteConnection(self._out)

    def create_query_builder(self) -> IQueryBuilder:
        return SqliteQueryBuilder()

    def create_transaction(self) -> ITransaction:
        return SqliteTransaction(self._out)
