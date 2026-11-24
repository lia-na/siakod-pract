import random
import unittest

from resource_hints.char_trie import CharTrie


def count_terminals(node):
    
    return int(node.is_end) + sum(count_terminals(c) for c in node.children.values())


def has_dead_leaf(node, is_root=True):
   
    if not node.children and not node.is_end and not is_root:
        return True
    return any(has_dead_leaf(c, False) for c in node.children.values())


class TestPutGetSize(unittest.TestCase):
    def test_empty_trie(self):
        t = CharTrie()
        self.assertEqual(len(t), 0)
        self.assertFalse(t.contains("a"))
        self.assertIsNone(t.get("a"))

    def test_put_new_key(self):
        t = CharTrie()
        self.assertTrue(t.put("cat", 1))
        self.assertEqual(len(t), 1)
        self.assertTrue(t.contains("cat"))
        self.assertEqual(t.get("cat"), 1)

    def test_put_existing_key_replaces_value_and_keeps_size(self):
        t = CharTrie()
        t.put("cat", 1)
        self.assertFalse(t.put("cat", 2))
        self.assertEqual(len(t), 1)
        self.assertEqual(t.get("cat"), 2)

    def test_prefix_is_not_a_key(self):
        t = CharTrie()
        t.put("cattle")
        self.assertFalse(t.contains("cat"))
        self.assertEqual(len(t), 1)

    def test_key_and_its_prefix_both_stored(self):
        t = CharTrie()
        t.put("cat")
        t.put("cattle")
        self.assertTrue(t.contains("cat"))
        self.assertTrue(t.contains("cattle"))
        self.assertEqual(len(t), 2)

    def test_longer_than_stored_is_not_found(self):
        t = CharTrie()
        t.put("cat")
        self.assertFalse(t.contains("cats"))

    def test_invalid_keys(self):
        t = CharTrie()
        with self.assertRaises(ValueError):
            t.put("")
        with self.assertRaises(ValueError):
            t.put(None)

    def test_invariants_after_many_puts(self):
        rnd = random.Random(1)
        t = CharTrie()
        expected = set()
        for _ in range(2000):
            key = "".join(rnd.choice("abc") for _ in range(rnd.randint(1, 6)))
            t.put(key)
            expected.add(key)
        self.assertEqual(len(t), len(expected))
        self.assertEqual(count_terminals(t._root), len(t))
        self.assertFalse(has_dead_leaf(t._root))
        for key in expected:
            self.assertTrue(t.contains(key))


class TestFindOneMismatch(unittest.TestCase):
    def setUp(self):
        self.t = CharTrie()
        for name in ["grass", "glass", "brass", "class", "grasp", "gras", "grassy"]:
            self.t.put(name)

    def test_mismatch_in_first_position(self):
        self.assertEqual(self.t.find_one_mismatch("xrass"), ["brass", "grass"])

    def test_mismatch_in_last_position(self):
        self.assertEqual(self.t.find_one_mismatch("grasx"), ["grasp", "grass"])

    def test_result_sorted_alphabetically(self):
        self.assertEqual(self.t.find_one_mismatch("xlass"), ["class", "glass"])

    def test_two_mismatches_give_nothing(self):
        self.assertEqual(self.t.find_one_mismatch("gxasx"), [])

    def test_other_length_ignored(self):
        self.assertEqual(self.t.find_one_mismatch("xrass"), ["brass", "grass"])
        self.assertEqual(self.t.find_one_mismatch("grasz"), ["grasp", "grass"])

    def test_exact_word_is_not_its_own_hint(self):
        self.assertEqual(self.t.find_one_mismatch("grass"), ["brass", "glass", "grasp"])

    def test_empty_query(self):
        self.assertEqual(self.t.find_one_mismatch(""), [])

    def test_permutation_and_deletion_not_typos(self):
        self.assertEqual(self.t.find_one_mismatch("garss"), [])  # перестановка
        self.assertEqual(self.t.find_one_mismatch("grs"), [])    # пропуск буквы


if __name__ == "__main__":
    unittest.main()
