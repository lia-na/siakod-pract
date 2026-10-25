from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Callable, Optional, Sequence

Output = Callable[[str], None]


@dataclass(frozen=True)
class Query:
   # построитель 

    sql: str
    params: tuple[Any, ...] = ()


class IConnection(ABC):
    # соединить с хранилищем

    @abstractmethod
    def execute(self, sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        """ Настоящих драйверов нет, то запрос печатается """

    @abstractmethod
    def close(self) -> None:
        """ закрыть """


class IQueryBuilder(ABC):
    """ построитель запросов """

    @abstractmethod
    def select(self, table: str, columns: Sequence[str] = ()) -> IQueryBuilder:
        """ выбор табл """

    @abstractmethod
    def where(self, column: str, operator: str, value: Any) -> IQueryBuilder:
        """ + условие, AND """

    @abstractmethod
    def limit(self, count: int) -> IQueryBuilder:
        """ ограничение числа строк """

    @abstractmethod
    def build(self) -> Query:
        """ собрать запрос """


class ITransaction(ABC):
    """ транзакция """

    @abstractmethod
    def begin(self) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    def __enter__(self) -> ITransaction:
        self.begin()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> bool:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False  


class IDataAccessFactory(ABC):
    """ абстрактная фабрика, согл набор """

    @abstractmethod
    def create_connection(self) -> IConnection: ...

    @abstractmethod
    def create_query_builder(self) -> IQueryBuilder: ...

    @abstractmethod
    def create_transaction(self) -> ITransaction: ...
