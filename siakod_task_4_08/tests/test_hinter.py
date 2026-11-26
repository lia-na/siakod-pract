import random
import unittest

from resource_hints.baseline import find_one_mismatch_bruteforce
from resource_hints.hinter import ResourceHinter


def make_hinter(names):
    h = ResourceHinter()
    for n in names:
        h.add(n)
    return h


class TestHinter(unittest.TestCase):
    def test_exact_match_returns_name(self):
        h = make_hinter(["cmd_start", "cmd_stop"])
        self.assertEqual(h.suggest("cmd_stop"), ["cmd_stop"])

    def test_exact_match_has_priority_over_neighbours(self):
        h = make_hinter(["cmd_stop", "cmd_step"])
        self.assertEqual(h.suggest("cmd_stop"), ["cmd_stop"])

    def test_no_answer(self):
        h = make_hinter(["cmd_start"])
        self.assertEqual(h.suggest("zzzzzzzzz"), [])

    def test_first_and_last_position(self):
        h = make_hinter(["sound_jump"])
        self.assertEqual(h.suggest("bound_jump"), ["sound_jump"])
        self.assertEqual(h.suggest("sound_jumb"), ["sound_jump"])

    def test_two_mismatches(self):
        h = make_hinter(["sound_jump"])
        self.assertEqual(h.suggest("bound_jumb"), [])

    def test_other_length(self):
        h = make_hinter(["sound_jump"])
        self.assertEqual(h.suggest("sound_jum"), [])
        self.assertEqual(h.suggest("sound_jumpp"), [])

    def test_dictionary_can_grow(self):
        h = make_hinter(["abc"])
        self.assertEqual(h.suggest("abx"), ["abc"])
        h.add("abd")
        self.assertEqual(h.suggest("abx"), ["abc", "abd"])
        self.assertEqual(len(h), 2)

    def test_duplicate_add_does_not_change_size(self):
        h = make_hinter(["abc"])
        self.assertFalse(h.add("abc"))
        self.assertEqual(len(h), 1)

    def test_logging(self):
        messages = []
        h = ResourceHinter(log=messages.append)
        h.add("abc")
        h.suggest("abx")
        self.assertEqual(len(messages), 2)

    def test_matches_bruteforce_on_random_data(self):
        rnd = random.Random(42)
        alphabet = "abc_"
        names = {"".join(rnd.choice(alphabet) for _ in range(rnd.randint(3, 7)))
                 for _ in range(400)}
        h = make_hinter(names)
        for _ in range(1000):
            q = "".join(rnd.choice(alphabet) for _ in range(rnd.randint(2, 8)))
            expected = [q] if q in names else find_one_mismatch_bruteforce(names, q)
            self.assertEqual(h.suggest(q), expected, q)


if __name__ == "__main__":
    unittest.main()
