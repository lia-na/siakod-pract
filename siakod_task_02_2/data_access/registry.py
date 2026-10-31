from __future__ import annotations

from data_access.file_storage import FileFactory
from data_access.interfaces import IDataAccessFactory, Output
from data_access.postgres_storage import PostgresFactory
from data_access.sqlite_storage import SqliteFactory

FACTORIES: dict[str, type[IDataAccessFactory]] = {
    "postgres": PostgresFactory,
    "sqlite": SqliteFactory,
    "file": FileFactory,
}


def create_factory(storage: str, out: Output = print) -> IDataAccessFactory:
    try:
        factory_class = FACTORIES[storage.lower()]
    except KeyError:
        available = ", ".join(FACTORIES)
        raise ValueError(f"Неизвестное хранилище {storage!r}. Доступны: {available}") from None
    return factory_class(out)  # type: ignore[call-arg]
