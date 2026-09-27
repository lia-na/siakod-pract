import unittest

from solution import naive_match


class TestNaiveMatch(unittest.TestCase):


    def test_simple_case(self): #happy path
        log1 = [1, 5, 9, 20]
        log2 = [0, 4, 10, 30]
        expected = [0, 4, 10, 30]
        self.assertEqual(naive_match(log1, log2), expected)

    def test_empty_log2(self): #краевые случаи
        self.assertEqual(naive_match([1, 2, 3], []), [None, None, None])

    def test_empty_log1(self):
        self.assertEqual(naive_match([], [1, 2, 3]), [])

    def test_both_empty(self):
        self.assertEqual(naive_match([], []), [])

    def test_single_element_each(self):
        self.assertEqual(naive_match([5], [100]), [100])

    def test_log2_single_element_many_log1(self):
        self.assertEqual(naive_match([1, 2, 3, 100, -50], [7]), [7, 7, 7, 7, 7])

    def test_duplicates_in_log2(self):
        self.assertEqual(naive_match([5, 5, 5], [1, 5, 5, 9]), [5, 5, 5])

    def test_duplicates_in_log1(self):
        self.assertEqual(naive_match([3, 3, 3, 3], [0, 10]),[0,0,0,0])

    def test_tie_exact_middle(self):
        # 5 равноудалён от 0 и 10 -> по правилу <= берём более позднее
        self.assertEqual(naive_match([5], [0, 10]), [10])

    def test_all_log1_events_before_log2(self):
        self.assertEqual(naive_match([-100, -50, -10], [1, 2, 3]), [1, 1, 1])

    def test_all_log1_events_after_log2(self):
        self.assertEqual(naive_match([100, 200, 300], [1, 2, 3]), [3, 3, 3])

    def test_negative_and_float_times(self):
        self.assertEqual(
            naive_match([-3.5, 0.0, 2.2, 7.9], [-10.0, -1.0, 1.5, 8.0]),
            [-1.0, -1.0, 1.5, 8.0],
        )

if __name__ == "__main__":
    unittest.main()
