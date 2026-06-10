import unittest
from solution import HitCounter


class TestHitCounter(unittest.TestCase):
    def test_hit_and_count(self):
        hc = HitCounter()
        hc.hit(1)
        hc.hit(2)
        hc.hit(3)
        self.assertEqual(hc.count_in_range(1, 3), 3)

    def test_count_in_range_partial(self):
        hc = HitCounter()
        hc.hit(1)
        hc.hit(5)
        hc.hit(10)
        self.assertEqual(hc.count_in_range(2, 9), 1)
        self.assertEqual(hc.count_in_range(1, 10), 3)
        self.assertEqual(hc.count_in_range(11, 100), 0)

    def test_count_in_last(self):
        hc = HitCounter()
        for t in [1, 5, 10, 15, 20]:
            hc.hit(t)
        # window=10 at now=20: (10, 20] = hits at 15, 20 = 2
        self.assertEqual(hc.count_in_last(20, 10), 2)
        # window=15 at now=20: (5, 20] = 3 hits — 10, 15, 20
        self.assertEqual(hc.count_in_last(20, 15), 3)

    def test_count_in_last_excludes_boundary(self):
        hc = HitCounter()
        hc.hit(10)
        # (10 - 5, 10] = (5, 10] includes 10 but not 5
        self.assertEqual(hc.count_in_last(10, 5), 1)

    def test_earliest_hit(self):
        hc = HitCounter()
        self.assertIsNone(hc.earliest_hit())
        hc.hit(5)
        hc.hit(10)
        self.assertEqual(hc.earliest_hit(), 5)

    def test_duplicate_timestamps(self):
        hc = HitCounter()
        hc.hit(5)
        hc.hit(5)
        hc.hit(5)
        self.assertEqual(hc.count_in_range(5, 5), 3)


if __name__ == "__main__":
    unittest.main()
