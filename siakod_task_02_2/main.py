from __future__ import annotations

import sys

from data_access.registry import FACTORIES, create_factory
from data_access.repository import UserRepository


def run(storage: str) -> None:
    print(f"=== Хранилище: {storage} ===")
    repository = UserRepository(create_factory(storage))  # единственное место выбора
    repository.find_adults(min_age=18, limit=10)
    repository.find_by_city("Moscow", min_age=21)
    repository.close()
    print()


if __name__ == "__main__":
    for name in sys.argv[1:] or list(FACTORIES):
        run(name)
