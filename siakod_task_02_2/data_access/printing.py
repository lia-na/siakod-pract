from __future__ import annotations

from typing import Any, Sequence

from data_access.interfaces import IConnection, ITransaction, Output


class PrintingConnection(IConnection):
    TAG = "?"

    def __init__(self, out: Output = print) -> None:
        self._out = out

    def execute(self, sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        self._out(f"[{self.TAG}] EXECUTE: {sql} | params={list(params)}")
        return []  # настоящих данных нет

    def close(self) -> None:
        self._out(f"[{self.TAG}] CLOSE CONNECTION")


class PrintingTransaction(ITransaction):
    TAG = "?"
    BEGIN_TEXT = "BEGIN"
    COMMIT_TEXT = "COMMIT"
    ROLLBACK_TEXT = "ROLLBACK"

    def __init__(self, out: Output = print) -> None:
        self._out = out

    def begin(self) -> None:
        self._out(f"[{self.TAG}] {self.BEGIN_TEXT}")

    def commit(self) -> None:
        self._out(f"[{self.TAG}] {self.COMMIT_TEXT}")

    def rollback(self) -> None:
        self._out(f"[{self.TAG}] {self.ROLLBACK_TEXT}")
