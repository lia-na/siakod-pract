from __future__ import annotations

import json

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


class FileConnection(PrintingConnection):
    TAG = "File"


class FileTransaction(PrintingTransaction):
    TAG = "File"
    BEGIN_TEXT = "LOCK FILE"
    COMMIT_TEXT = "SAVE CHANGES AND UNLOCK FILE"
    ROLLBACK_TEXT = "DISCARD CHANGES AND UNLOCK FILE"


class FileQueryBuilder(BaseQueryBuilder):
    def build(self) -> Query:
        self._check_ready()
        parts = [f"READ {self._table}"]
        if self._columns:
            parts.append("FIELDS " + ", ".join(self._columns))
        if self._conditions:
            conditions = [
                f"{column} {operator} {json.dumps(value)}"
                for column, operator, value in self._conditions
            ]
            parts.append("FILTER " + " AND ".join(conditions))
        if self._limit is not None:
            parts.append(f"LIMIT {self._limit}")
        return Query(" | ".join(parts))


class FileFactory(IDataAccessFactory):
    def __init__(self, out: Output = print) -> None:
        self._out = out

    def create_connection(self) -> IConnection:
        return FileConnection(self._out)

    def create_query_builder(self) -> IQueryBuilder:
        return FileQueryBuilder()

    def create_transaction(self) -> ITransaction:
        return FileTransaction(self._out)
