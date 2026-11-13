import subprocess
import sys
import unittest


class TestExample(unittest.TestCase):
    def run_main(self, *args):
        with open("v06_input.jsonl") as f:
            result = subprocess.run([sys.executable, "main.py", *args], stdin=f,
                                    capture_output=True, text=True, check=True)
        return result.stdout.replace(" ", "")

    def test_teacher_example(self):
        """Пример преподавателя: вход v06_input.jsonl -> выход v06_expected.jsonl."""
        with open("v06_expected.jsonl") as f:
            expected = f.read().replace(" ", "")
        self.assertEqual(self.run_main(), expected)

    def test_naive_gives_same_answer(self):
        """Эталон (--naive) на том же входе даёт тот же ответ, что и куча."""
        self.assertEqual(self.run_main("--naive"), self.run_main())


if __name__ == "__main__":
    unittest.main()
