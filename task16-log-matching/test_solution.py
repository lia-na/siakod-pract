
import random
import unittest

from solution import naive_match, two_pointer_match


def reference_match(log1, log2): # верное решение для проверки

    if not log2:
        return [None] * len(log1)

    return [min(log2, key=lambda s: (abs(t - s), -s)) for t in log1] #при = брать <S, -s -> сдвигаем наибольшее влево (наименьшее)


class TestBothAlgorithmsAgree(unittest.TestCase): #алгоритмы согласованы

    def assert_both_equal(self, log1, log2):
        expected = reference_match(log1, log2)
        self.assertEqual(naive_match(log1, log2), expected, "naive_match разошёлся с эталоном")
        self.assertEqual(two_pointer_match(log1, log2), expected, "two_pointer_match разошёлся с эталоном")

    def test_simple_case(self): # happy path
        log1 = [1, 5, 9, 20]
        log2 = [0, 4, 10, 30]
        self.assert_both_equal(log1, log2)

    #краевые случаи 
    def test_empty_log2(self):
        self.assertEqual(naive_match([1, 2, 3], []), [None, None, None])
        self.assertEqual(two_pointer_match([1, 2, 3], []), [None, None, None])

    def test_empty_log1(self):
        self.assertEqual(naive_match([], [1, 2, 3]), [])
        self.assertEqual(two_pointer_match([], [1, 2, 3]), [])

    def test_both_empty(self):
        self.assertEqual(naive_match([], []), [])
        self.assertEqual(two_pointer_match([], []), [])

    def test_single_element_each(self):
        self.assert_both_equal([5], [100])

    def test_log2_single_element_many_log1(self):
        self.assert_both_equal([1, 2, 3, 100, -50], [7])

    def test_duplicates_in_log2(self):
        self.assert_both_equal([5, 5, 5], [1, 5, 5, 9])

    def test_duplicates_in_log1(self):
        self.assert_both_equal([3, 3, 3, 3], [0, 10])

    def test_tie_exact_middle(self):
        # 5 равноудалён от 0 и 10 -> более позднее 10
        log1 = [5]
        log2 = [0, 10]
        self.assertEqual(naive_match(log1, log2), [10])
        self.assertEqual(two_pointer_match(log1, log2), [10])

    def test_tie_with_duplicate_plateau(self): #пригодился <= (273 и 273)

        log1 = [312]
        log2 = [25, 39, 39, 247, 280, 308, 473]
        self.assert_both_equal(log1, log2)

    def test_all_log1_events_before_log2(self):
        self.assert_both_equal([-100, -50, -10], [1, 2, 3])

    def test_all_log1_events_after_log2(self):
        self.assert_both_equal([100, 200, 300], [1, 2, 3])

    def test_negative_and_float_times(self):
        self.assert_both_equal([-3.5, 0.0, 2.2, 7.9], [-10.0, -1.0, 1.5, 8.0])


    def test_random_stress(self): # стресс тест
        random.seed(42)
        for _ in range(200):
            n = random.randint(0, 30)
            m = random.randint(0, 30)
            log1 = sorted(random.randint(-1000, 1000) for _ in range(n))
            log2 = sorted(random.randint(-1000, 1000) for _ in range(m))
            self.assert_both_equal(log1, log2)


if __name__ == "__main__":
    unittest.main()
