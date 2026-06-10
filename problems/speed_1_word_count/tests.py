import unittest
from solution import word_count, top_words


class TestWordCount(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(word_count("the quick brown fox"),
                         {"the": 1, "quick": 1, "brown": 1, "fox": 1})

    def test_repeats(self):
        self.assertEqual(word_count("a a a b b c"),
                         {"a": 3, "b": 2, "c": 1})

    def test_case_insensitive(self):
        self.assertEqual(word_count("Foo FOO foo"), {"foo": 3})

    def test_empty(self):
        self.assertEqual(word_count(""), {})

    def test_extra_whitespace(self):
        self.assertEqual(word_count("  a   b  a  "), {"a": 2, "b": 1})


class TestTopWords(unittest.TestCase):
    def test_basic(self):
        result = top_words("a a a b b c", 2)
        self.assertEqual(result, [("a", 3), ("b", 2)])

    def test_tiebreak_alphabetical(self):
        result = top_words("b b a a c c", 3)
        # All tied at 2; alphabetical
        self.assertEqual(result, [("a", 2), ("b", 2), ("c", 2)])

    def test_more_than_exist(self):
        result = top_words("a b", 5)
        self.assertEqual(result, [("a", 1), ("b", 1)])

    def test_zero(self):
        self.assertEqual(top_words("a b c", 0), [])


if __name__ == "__main__":
    unittest.main()
