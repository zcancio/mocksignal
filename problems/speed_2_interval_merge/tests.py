import unittest
from solution import merge_intervals, total_coverage


class TestMergeIntervals(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]),
            [[1, 6], [8, 10], [15, 18]],
        )

    def test_touching_merges(self):
        self.assertEqual(merge_intervals([[1, 3], [3, 5]]), [[1, 5]])

    def test_unsorted_input(self):
        self.assertEqual(
            merge_intervals([[5, 7], [1, 3], [2, 4]]),
            [[1, 4], [5, 7]],
        )

    def test_no_overlap(self):
        self.assertEqual(
            merge_intervals([[1, 2], [4, 5], [7, 8]]),
            [[1, 2], [4, 5], [7, 8]],
        )

    def test_empty(self):
        self.assertEqual(merge_intervals([]), [])

    def test_single(self):
        self.assertEqual(merge_intervals([[1, 5]]), [[1, 5]])

    def test_fully_contained(self):
        self.assertEqual(merge_intervals([[1, 10], [3, 5]]), [[1, 10]])


class TestTotalCoverage(unittest.TestCase):
    def test_basic(self):
        # [1,3] = 1,2,3 = 3 units
        self.assertEqual(total_coverage([[1, 3]]), 3)

    def test_overlap(self):
        # [1,3] + [2,6] -> [1,6] = 6 units
        self.assertEqual(total_coverage([[1, 3], [2, 6]]), 6)

    def test_separate(self):
        self.assertEqual(total_coverage([[1, 2], [5, 6]]), 4)

    def test_empty(self):
        self.assertEqual(total_coverage([]), 0)


if __name__ == "__main__":
    unittest.main()
