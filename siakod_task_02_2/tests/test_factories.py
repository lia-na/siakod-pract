import unittest

from data_access.file_storage import FileConnection, FileFactory, FileQueryBuilder, FileTransaction
from data_access.interfaces import IConnection, IDataAccessFactory, IQueryBuilder, ITransaction
from data_access.postgres_storage import (
    PostgresConnection,
    PostgresFactory,
    PostgresQueryBuilder,
    PostgresTransaction,
)
from data_access.registry import FACTORIES, create_factory
from data_access.sqlite_storage import SqliteConnection, SqliteFactory, SqliteQueryBuilder, SqliteTransaction

FAMILIES = {
    "postgres": (PostgresFactory, PostgresConnection, PostgresQueryBuilder, PostgresTransaction),
    "sqlite": (SqliteFactory, SqliteConnection, SqliteQueryBuilder, SqliteTransaction),
    "file": (FileFactory, FileConnection, FileQueryBuilder, FileTransaction),
}


class FactoryTests(unittest.TestCase):
    def test_each_factory_creates_its_own_consistent_family(self):
        for name, (factory_cls, conn_cls, builder_cls, tx_cls) in FAMILIES.items():
            with self.subTest(storage=name):
                factory = factory_cls(lambda line: None)
                self.assertIsInstance(factory.create_connection(), conn_cls)
                self.assertIsInstance(factory.create_query_builder(), builder_cls)
                self.assertIsInstance(factory.create_transaction(), tx_cls)

    def test_products_follow_interfaces(self):
        for name in FACTORIES:
            with self.subTest(storage=name):
                factory = create_factory(name, lambda line: None)
                self.assertIsInstance(factory, IDataAccessFactory)
                self.assertIsInstance(factory.create_connection(), IConnection)
                self.assertIsInstance(factory.create_query_builder(), IQueryBuilder)
                self.assertIsInstance(factory.create_transaction(), ITransaction)

    def test_all_products_of_one_factory_print_the_same_tag(self):
        # Согласованность: и соединение, и транзакция одной фабрики - из одного хранилища.
        tags = {"postgres": "[PostgreSQL]", "sqlite": "[SQLite]", "file": "[File]"}
        for name, tag in tags.items():
            with self.subTest(storage=name):
                log = []
                factory = create_factory(name, log.append)
                factory.create_connection().execute("x")
                with factory.create_transaction():
                    pass
                self.assertTrue(log)
                self.assertTrue(all(line.startswith(tag) for line in log), log)

    def test_factory_creates_independent_products(self):
        factory = create_factory("sqlite", lambda line: None)
        self.assertIsNot(factory.create_query_builder(), factory.create_query_builder())
        self.assertIsNot(factory.create_connection(), factory.create_connection())

    def test_registry_is_case_insensitive(self):
        self.assertIsInstance(create_factory("PostgreS", lambda line: None), PostgresFactory)

    def test_unknown_storage_fails_with_helpful_message(self):
        with self.assertRaises(ValueError) as ctx:
            create_factory("mongodb")
        self.assertIn("postgres", str(ctx.exception))

    def test_abstract_classes_cannot_be_instantiated(self):
        for cls in (IConnection, IQueryBuilder, ITransaction, IDataAccessFactory):
            with self.subTest(cls=cls.__name__):
                with self.assertRaises(TypeError):
                    cls()


if __name__ == "__main__":
    unittest.main()
