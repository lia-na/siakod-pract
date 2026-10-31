import unittest

from data_access.file_storage import FileQueryBuilder
from data_access.postgres_storage import PostgresQueryBuilder
from data_access.sqlite_storage import SqliteQueryBuilder

ALL_BUILDERS = [PostgresQueryBuilder, SqliteQueryBuilder, FileQueryBuilder]


class SyntaxTests(unittest.TestCase):

    @staticmethod
    def _full(builder):
        return (
            builder.select("users", ["id", "name"])
            .where("age", ">=", 18)
            .where("city", "=", "Moscow")
            .limit(5)
            .build()
        )

    def test_postgres(self):
        q = self._full(PostgresQueryBuilder())
        self.assertEqual(
            q.sql,
            'SELECT "id", "name" FROM "users" WHERE "age" >= $1 AND "city" = $2 LIMIT 5;',
        )
        self.assertEqual(q.params, (18, "Moscow"))

    def test_sqlite(self):
        q = self._full(SqliteQueryBuilder())
        self.assertEqual(
            q.sql, "SELECT id, name FROM users WHERE age >= ? AND city = ? LIMIT 5;"
        )
        self.assertEqual(q.params, (18, "Moscow"))

    def test_file(self):
        q = self._full(FileQueryBuilder())
        self.assertEqual(
            q.sql,
            'READ users | FIELDS id, name | FILTER age >= 18 AND city = "Moscow" | LIMIT 5',
        )
        self.assertEqual(q.params, ())  

    def test_same_request_gives_different_text_everywhere(self):
        texts = {self._full(cls()).sql for cls in ALL_BUILDERS}
        self.assertEqual(len(texts), 3)


class EdgeCaseTests(unittest.TestCase):
    def test_no_columns_means_all(self):
        self.assertEqual(PostgresQueryBuilder().select("t").build().sql, 'SELECT * FROM "t";')
        self.assertEqual(SqliteQueryBuilder().select("t").build().sql, "SELECT * FROM t;")
        self.assertEqual(FileQueryBuilder().select("t").build().sql, "READ t")

    def test_limit_zero_is_kept(self):
        q = SqliteQueryBuilder().select("t").limit(0).build()
        self.assertIn("LIMIT 0", q.sql)

    def test_postgres_placeholders_are_numbered_in_order(self):
        q = PostgresQueryBuilder().select("t").where("a", "=", 1).where("b", "<", 2).where("c", ">", 3).build()
        self.assertIn("$1", q.sql)
        self.assertIn("$3", q.sql)
        self.assertEqual(q.params, (1, 2, 3))

    def test_build_without_select_fails(self):
        for cls in ALL_BUILDERS:
            with self.subTest(builder=cls.__name__):
                with self.assertRaises(ValueError):
                    cls().build()

    def test_bad_operator_fails(self):
        for cls in ALL_BUILDERS:
            with self.subTest(builder=cls.__name__):
                with self.assertRaises(ValueError):
                    cls().select("t").where("a", "; DROP TABLE t; --", 1)

    def test_bad_identifier_fails(self):
        for cls in ALL_BUILDERS:
            with self.subTest(builder=cls.__name__):
                with self.assertRaises(ValueError):
                    cls().select("users; DROP TABLE users")
                with self.assertRaises(ValueError):
                    cls().select("users", ["na me"])
                with self.assertRaises(ValueError):
                    cls().select("users").where("a b", "=", 1)

    def test_negative_limit_fails(self):
        for cls in ALL_BUILDERS:
            with self.subTest(builder=cls.__name__):
                with self.assertRaises(ValueError):
                    cls().select("t").limit(-1)

    def test_build_twice_gives_same_result(self):
        builder = PostgresQueryBuilder().select("t").where("a", "=", 1)
        self.assertEqual(builder.build(), builder.build())

    def test_fluent_methods_return_same_builder(self):
        builder = SqliteQueryBuilder()
        self.assertIs(builder.select("t"), builder)
        self.assertIs(builder.where("a", "=", 1), builder)
        self.assertIs(builder.limit(1), builder)


if __name__ == "__main__":
    unittest.main()
