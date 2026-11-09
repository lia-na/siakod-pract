import random
import unittest

from heap import BinaryHeap


class TestBinaryHeap(unittest.TestCase):
    def test_empty(self):
        h = BinaryHeap()
        self.assertEqual(h.size(), 0)
        with self.assertRaises(IndexError):
            h.pop()
        with self.assertRaises(IndexError):
            h.peek()
        with self.assertRaises(IndexError):
            h.replace_top(1)

    def test_single_element(self):
        h = BinaryHeap()
        h.push(7)
        self.assertEqual(h.peek(), 7)
        self.assertEqual(h.pop(), 7)
        self.assertEqual(h.size(), 0)

    def test_min_heap_order(self):
        h = BinaryHeap()
        for x in [5, 3, 8, 1, 9, 2]:
            h.push(x)
        self.assertEqual(h.peek(), 1)
        self.assertEqual([h.pop() for _ in range(6)], [1, 2, 3, 5, 8, 9])

    def test_max_heap_order(self):
        h = BinaryHeap(less=lambda a, b: a > b)
        for x in [5, 3, 8, 1, 9, 2]:
            h.push(x)
        self.assertEqual([h.pop() for _ in range(6)], [9, 8, 5, 3, 2, 1])

    def test_duplicates(self):
        h = BinaryHeap()
        for x in [2, 2, 1, 1, 2]:
            h.push(x)
        self.assertEqual([h.pop() for _ in range(5)], [1, 1, 2, 2, 2])

    def test_peek_does_not_remove(self):
        h = BinaryHeap()
        h.push(4)
        h.push(2)
        h.peek()
        self.assertEqual(h.size(), 2)

    def test_replace_top(self):
        h = BinaryHeap()
        for x in [1, 3, 5]:
            h.push(x)
        self.assertEqual(h.replace_top(10), 1)   # вернул старую вершину
        self.assertTrue(h.is_valid())
        self.assertEqual(h.peek(), 3)
        self.assertEqual(h.size(), 3)
        h.replace_top(0)                          # новая вершина меньше всех
        self.assertEqual(h.peek(), 0)

    def test_heapify(self):
        data = [9, 4, 7, 1, 8, 2, 6, 3, 5, 0]
        h = BinaryHeap.heapify(data)
        self.assertTrue(h.is_valid())
        self.assertEqual([h.pop() for _ in range(10)], list(range(10)))

    def test_heapify_edge_and_max(self):
        self.assertEqual(BinaryHeap.heapify([]).size(), 0)
        self.assertEqual(BinaryHeap.heapify([1]).peek(), 1)
        h = BinaryHeap.heapify([1, 5, 3], less=lambda a, b: a > b)
        self.assertEqual(h.peek(), 5)

    def test_invariant_after_random_operations(self):
        rnd = random.Random(1)
        h = BinaryHeap()
        ref = []
        for _ in range(2000):
            op = rnd.choice(["push", "push", "pop", "replace"])
            if op == "push":
                x = rnd.randint(0, 100)
                h.push(x)
                ref.append(x)
            elif ref and op == "pop":
                self.assertEqual(h.pop(), min(ref))
                ref.remove(min(ref))
            elif ref:
                x = rnd.randint(0, 100)
                self.assertEqual(h.replace_top(x), min(ref))
                ref.remove(min(ref))
                ref.append(x)
            self.assertTrue(h.is_valid())
            self.assertEqual(h.size(), len(ref))


if __name__ == "__main__":
    unittest.main()
