import unittest

from data_access.registry import FACTORIES, create_factory


class TransactionTests(unittest.TestCase):
    def test_commit_order_for_every_storage(self):
        for name in FACTORIES:
            with self.subTest(storage=name):
                log = []
                factory = create_factory(name, log.append)
                connection = factory.create_connection()
                with factory.create_transaction():
                    connection.execute("QUERY", [1])
                self.assertEqual(len(log), 3)
                self.assertIn("EXECUTE: QUERY", log[1])  
                self.assertNotIn("ROLLBACK", log[2])
                self.assertNotIn("DISCARD", log[2])

    def test_exact_texts_postgres(self):
        log = []
        factory = create_factory("postgres", log.append)
        connection = factory.create_connection()
        with factory.create_transaction():
            connection.execute("SELECT 1", [42])
        self.assertEqual(
            log,
            ["[PostgreSQL] BEGIN", "[PostgreSQL] EXECUTE: SELECT 1 | params=[42]", "[PostgreSQL] COMMIT"],
        )

    def test_error_inside_transaction_causes_rollback_and_is_not_swallowed(self):
        expected_last = {
            "postgres": "[PostgreSQL] ROLLBACK",
            "sqlite": "[SQLite] ROLLBACK TRANSACTION",
            "file": "[File] DISCARD CHANGES AND UNLOCK FILE",
        }
        for name, last in expected_last.items():
            with self.subTest(storage=name):
                log = []
                factory = create_factory(name, log.append)
                connection = factory.create_connection()
                with self.assertRaises(RuntimeError):
                    with factory.create_transaction():
                        connection.execute("QUERY")
                        raise RuntimeError("сбой")
                self.assertEqual(len(log), 3)
                self.assertEqual(log[-1], last)

    def test_no_commit_after_rollback(self):
        log = []
        factory = create_factory("sqlite", log.append)
        with self.assertRaises(ValueError):
            with factory.create_transaction():
                raise ValueError("x")
        self.assertEqual(log, ["[SQLite] BEGIN TRANSACTION", "[SQLite] ROLLBACK TRANSACTION"])

    def test_manual_begin_commit_rollback(self):
        log = []
        tx = create_factory("postgres", log.append).create_transaction()
        tx.begin()
        tx.rollback()
        self.assertEqual(log, ["[PostgreSQL] BEGIN", "[PostgreSQL] ROLLBACK"])

    def test_transaction_can_be_reused(self):
        log = []
        tx = create_factory("sqlite", log.append).create_transaction()
        with tx:
            pass
        with tx:
            pass
        self.assertEqual(len(log), 4)

    def test_invariant_every_begin_is_closed_exactly_once(self):
        closers = ("COMMIT", "ROLLBACK", "SAVE CHANGES", "DISCARD CHANGES")
        for name in FACTORIES:
            with self.subTest(storage=name):
                log = []
                factory = create_factory(name, log.append)
                for i in range(10):
                    try:
                        with factory.create_transaction():
                            if i % 3 == 0:
                                raise RuntimeError
                    except RuntimeError:
                        pass
                opened = False
                for line in log:
                    is_open = any(w in line for w in ("BEGIN", "LOCK FILE")) and "UNLOCK" not in line
                    is_close = any(w in line for w in closers)
                    self.assertNotEqual(is_open, is_close, line)
                    self.assertNotEqual(is_open, opened, f"нарушено чередование на {line!r}")
                    opened = is_open
                self.assertFalse(opened)
                self.assertEqual(len(log), 20)


class ConnectionTests(unittest.TestCase):
    def test_execute_prints_query_and_params_and_returns_empty_list(self):
        log = []
        connection = create_factory("sqlite", log.append).create_connection()
        result = connection.execute("SELECT 1 WHERE a = ?", ["x"])
        self.assertEqual(result, [])
        self.assertEqual(log, ["[SQLite] EXECUTE: SELECT 1 WHERE a = ? | params=['x']"])

    def test_execute_without_params(self):
        log = []
        create_factory("file", log.append).create_connection().execute("READ t")
        self.assertEqual(log, ["[File] EXECUTE: READ t | params=[]"])

    def test_close(self):
        log = []
        create_factory("postgres", log.append).create_connection().close()
        self.assertEqual(log, ["[PostgreSQL] CLOSE CONNECTION"])


if __name__ == "__main__":
    unittest.main()
