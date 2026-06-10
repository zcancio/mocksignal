"""
Tests for the bisect drill.

Run with: python3 -m unittest test_bisect_drill.py -v
"""
import unittest
from solution import (
    count_equal,
    count_in_range,
    count_less_than,
    insert_keeping_sorted,
    remove_one,
    closest_value,
)


class TestCountEqual(unittest.TestCase):
    def test_multiple(self):
        self.assertEqual(count_equal([1, 2, 2, 2, 3], 2), 3)

    def test_one(self):
        self.assertEqual(count_equal([1, 2, 3], 2), 1)

    def test_zero(self):
        self.assertEqual(count_equal([1, 3, 5], 2), 0)

    def test_empty(self):
        self.assertEqual(count_equal([], 5), 0)

    def test_all_same(self):
        self.assertEqual(count_equal([5, 5, 5, 5], 5), 4)


class TestCountInRange(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(count_in_range([1, 3, 5, 7, 9], 3, 7), 3)

    def test_inclusive_boundaries(self):
        self.assertEqual(count_in_range([1, 3, 5, 7, 9], 1, 9), 5)

    def test_no_match(self):
        self.assertEqual(count_in_range([1, 3, 5], 10, 20), 0)

    def test_between_elements(self):
        # 2 is between 1 and 3, 4 is between 3 and 5 — no exact matches
        self.assertEqual(count_in_range([1, 3, 5], 2, 4), 1)  # just 3

    def test_empty(self):
        self.assertEqual(count_in_range([], 1, 10), 0)


class TestCountLessThan(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(count_less_than([1, 3, 5, 7], 5), 2)  # 1, 3

    def test_strict(self):
        # 5 is NOT less than 5
        self.assertEqual(count_less_than([1, 3, 5, 7], 5), 2)

    def test_all_less(self):
        self.assertEqual(count_less_than([1, 2, 3], 100), 3)

    def test_none_less(self):
        self.assertEqual(count_less_than([5, 10, 15], 1), 0)


class TestInsertKeepingSorted(unittest.TestCase):
    def test_middle(self):
        result = insert_keeping_sorted([1, 3, 5], 4)
        self.assertEqual(result, [1, 3, 4, 5])

    def test_beginning(self):
        result = insert_keeping_sorted([5, 10, 15], 1)
        self.assertEqual(result, [1, 5, 10, 15])

    def test_end(self):
        result = insert_keeping_sorted([1, 2, 3], 100)
        self.assertEqual(result, [1, 2, 3, 100])

    def test_duplicate(self):
        result = insert_keeping_sorted([1, 2, 3], 2)
        # 2 should be inserted; order between original 2 and new 2 doesn't matter
        self.assertEqual(result, [1, 2, 2, 3])

    def test_empty(self):
        result = insert_keeping_sorted([], 5)
        self.assertEqual(result, [5])


class TestRemoveOne(unittest.TestCase):
    def test_present(self):
        result = remove_one([1, 2, 2, 3], 2)
        self.assertEqual(result, [1, 2, 3])

    def test_not_present(self):
        result = remove_one([1, 3, 5], 4)
        self.assertEqual(result, [1, 3, 5])

    def test_first(self):
        result = remove_one([1, 2, 3], 1)
        self.assertEqual(result, [2, 3])

    def test_last(self):
        result = remove_one([1, 2, 3], 3)
        self.assertEqual(result, [1, 2])


class TestClosestValue(unittest.TestCase):
    def test_below(self):
        self.assertEqual(closest_value([1, 5, 10, 20], 7), 5)

    def test_above(self):
        self.assertEqual(closest_value([1, 5, 10, 20], 8), 10)

    def test_tie_picks_lower(self):
        self.assertEqual(closest_value([1, 5, 10, 20], 7.5), 5)

    def test_target_smaller_than_all(self):
        self.assertEqual(closest_value([5, 10, 15], 1), 5)

    def test_target_larger_than_all(self):
        self.assertEqual(closest_value([5, 10, 15], 100), 15)

    def test_exact_match(self):
        self.assertEqual(closest_value([1, 5, 10], 5), 5)


if __name__ == "__main__":
    unittest.main()
