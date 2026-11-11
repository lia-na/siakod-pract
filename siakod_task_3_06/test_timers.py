import random
import unittest

from timers import NaiveScheduler, TimerScheduler


class TestTimers(unittest.TestCase):
    def setUp(self):
        self.s = TimerScheduler()

    def test_basic_fire(self):
        self.s.set("a", 5)
        self.assertEqual(self.s.advance(5), [("a", 5)])  # граница to включается

    def test_at_equal_to_now_fires_only_on_advance(self):
        self.s.set("a", 0)                                # at == текущему времени
        self.assertEqual(self.s.advance(0), [("a", 0)])   # сработает только на ADVANCE

    def test_advance_without_events(self):
        self.s.set("a", 10)
        self.assertEqual(self.s.advance(5), [])
        self.assertEqual(self.s.advance(10), [("a", 10)])

    def test_advance_on_empty(self):
        self.assertEqual(self.s.advance(100), [])

    def test_move_later(self):
        self.s.set("a", 5)
        self.s.set("a", 15)
        self.assertEqual(self.s.advance(10), [])          # старое назначение не сработало
        self.assertEqual(self.s.advance(15), [("a", 15)])

    def test_move_earlier(self):
        self.s.set("a", 15)
        self.s.set("a", 5)
        self.assertEqual(self.s.advance(5), [("a", 5)])
        self.assertEqual(self.s.advance(20), [])          # старое назначение (15) не сработало

    def test_cancel(self):
        self.s.set("a", 5)
        self.s.cancel("a")
        self.assertEqual(self.s.advance(10), [])

    def test_cancel_missing_id_ignored(self):
        self.s.cancel("nope")
        self.assertEqual(self.s.advance(10), [])

    def test_reuse_id_after_cancel(self):
        self.s.set("a", 5)
        self.s.cancel("a")
        self.s.set("a", 7)
        self.assertEqual(self.s.advance(10), [("a", 7)])

    def test_reuse_id_after_fire(self):
        self.s.set("a", 5)
        self.s.advance(5)
        self.s.set("a", 8)
        self.assertEqual(self.s.advance(8), [("a", 8)])

    def test_equal_times_order_of_assignment(self):
        self.s.set("c", 5)
        self.s.set("a", 5)
        self.s.set("b", 5)
        self.assertEqual(self.s.advance(5), [("c", 5), ("a", 5), ("b", 5)])

    def test_reassign_changes_order_among_equal_times(self):
        self.s.set("a", 5)
        self.s.set("b", 5)
        self.s.set("a", 5)                                # a переназначен позже b
        self.assertEqual(self.s.advance(5), [("b", 5), ("a", 5)])

    def test_sorted_by_time(self):
        self.s.set("x", 9)
        self.s.set("y", 3)
        self.s.set("z", 6)
        self.assertEqual(self.s.advance(10), [("y", 3), ("z", 6), ("x", 9)])

    def test_stale_entries_stay_in_heap(self):
        for t in range(1, 101):
            self.s.set("a", t)                            # 100 переносов одного таймера
        self.assertEqual(len(self.s.active), 1)           # активный - один
        self.assertEqual(self.s.heap.size(), 100)         # в куче - все 100 назначений
        self.assertEqual(self.s.advance(1000), [("a", 100)])
        self.assertEqual(self.s.heap.size(), 0)           # после извлечения мусор ушёл

    def test_heap_invariant(self):
        rnd = random.Random(3)
        for i in range(500):
            self.s.set(rnd.randint(0, 20), rnd.randint(0, 1000))
            self.assertTrue(self.s.heap.is_valid())

    def test_matches_naive_on_random_scenarios(self):
        for seed in range(50):
            rnd = random.Random(seed)
            fast, naive = TimerScheduler(), NaiveScheduler()
            now = 0
            for _ in range(300):
                op = rnd.choice(["set", "set", "cancel", "advance"])
                id = rnd.randint(0, 10)
                if op == "set":
                    at = now + rnd.randint(0, 20)
                    fast.set(id, at)
                    naive.set(id, at)
                elif op == "cancel":
                    fast.cancel(id)
                    naive.cancel(id)
                else:
                    now += rnd.randint(0, 15)
                    self.assertEqual(fast.advance(now), naive.advance(now))


if __name__ == "__main__":
    unittest.main()
