import unittest
from typing import Any, Sequence

from data_access.interfaces import IConnection, IDataAccessFactory, IQueryBuilder, ITransaction, Query
from data_access.registry import FACTORIES, create_factory
from data_access.repository import UserRepository
from data_access.sqlite_storage import SqliteFactory


class SubstitutionTests(unittest.TestCase):
    def test_same_application_code_works_with_every_storage(self):
        outputs = {}
        for name in FACTORIES:
            log = []
            repo = UserRepository(create_factory(name, log.append))
            repo.find_adults(min_age=18, limit=10)
            outputs[name] = log
        self.assertIn("PostgreSQL", outputs["postgres"][0])
        self.assertIn("SQLite", outputs["sqlite"][0])
        self.assertIn("File", outputs["file"][0])
        self.assertNotEqual(outputs["postgres"][1], outputs["sqlite"][1])
        self.assertNotEqual(outputs["sqlite"][1], outputs["file"][1])

    def test_repository_works_with_a_completely_foreign_factory(self):
        calls = []

        class FakeConnection(IConnection):
            def execute(self, sql: str, params: Sequence[Any] = ()):
                calls.append(("execute", sql, tuple(params)))
                return [{"id": 1}]

            def close(self):
                calls.append(("close",))

        class FakeBuilder(IQueryBuilder):
            def select(self, table, columns=()):
                return self

            def where(self, column, operator, value):
                return self

            def limit(self, count):
                return self

            def build(self):
                return Query("FAKE QUERY", ("p",))

        class FakeTransaction(ITransaction):
            def begin(self):
                calls.append(("begin",))

            def commit(self):
                calls.append(("commit",))

            def rollback(self):
                calls.append(("rollback",))

        class FakeFactory(IDataAccessFactory):
            def create_connection(self):
                return FakeConnection()

            def create_query_builder(self):
                return FakeBuilder()

            def create_transaction(self):
                return FakeTransaction()

        repo = UserRepository(FakeFactory())
        self.assertEqual(repo.find_adults(), [{"id": 1}])
        repo.close()
        self.assertEqual(
            calls,
            [("begin",), ("execute", "FAKE QUERY", ("p",)), ("commit",), ("close",)],
        )


class CallOrderTests(unittest.TestCase):
    def test_find_adults_order_begin_execute_commit(self):
        log = []
        UserRepository(create_factory("postgres", log.append)).find_adults(21, 3)
        self.assertEqual(
            log,
            [
                "[PostgreSQL] BEGIN",
                '[PostgreSQL] EXECUTE: SELECT "id", "name" FROM "users" WHERE "age" >= $1 LIMIT 3; | params=[21]',
                "[PostgreSQL] COMMIT",
            ],
        )

    def test_each_query_gets_its_own_transaction(self):
        log = []
        repo = UserRepository(create_factory("sqlite", log.append))
        repo.find_adults()
        repo.find_by_city("Moscow")
        self.assertEqual(sum("BEGIN" in line for line in log), 2)
        self.assertEqual(sum("COMMIT" in line for line in log), 2)

    def test_builders_do_not_leak_conditions_between_queries(self):
        log = []
        repo = UserRepository(create_factory("sqlite", log.append))
        repo.find_by_city("Moscow", 21)
        repo.find_adults()
        second_query = [line for line in log if "EXECUTE" in line][1]
        self.assertNotIn("city", second_query)

    def test_close_closes_connection_after_everything(self):
        log = []
        repo = UserRepository(create_factory("file", log.append))
        repo.find_adults()
        repo.close()
        self.assertEqual(log[-1], "[File] CLOSE CONNECTION")

    def test_find_by_city_with_value_containing_quotes_in_file_storage(self):
        log = []
        UserRepository(create_factory("file", log.append)).find_by_city('O"Hara')
        self.assertIn('city = "O\\"Hara"', log[1])


class RollbackTests(unittest.TestCase):
    def test_failure_in_connection_rolls_back_and_propagates(self):
        log = []

        class BrokenConnection(IConnection):
            def execute(self, sql, params=()):
                raise ConnectionError("нет связи")

            def close(self):
                pass

        class BrokenFactory(SqliteFactory):
            def create_connection(self):
                return BrokenConnection()

        repo = UserRepository(BrokenFactory(log.append))
        with self.assertRaises(ConnectionError):
            repo.find_adults()
        self.assertEqual(log, ["[SQLite] BEGIN TRANSACTION", "[SQLite] ROLLBACK TRANSACTION"])

    def test_invalid_input_fails_before_transaction_is_opened(self):
        log = []
        repo = UserRepository(create_factory("sqlite", log.append))
        with self.assertRaises(ValueError):
            repo.find_adults(limit=-5)
        self.assertEqual(log, [])  


if __name__ == "__main__":
    unittest.main()
