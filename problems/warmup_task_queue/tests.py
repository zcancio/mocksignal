"""
Tests for TaskQueue warmup. Run with:
    python3 -m unittest test_warmup.py -v
"""

import unittest
from solution import TaskQueue


class TestLevel1(unittest.TestCase):
    def test_add_and_get(self):
        q = TaskQueue()
        q.add_task("t1", 5)
        self.assertEqual(q.get_next(), "t1")

    def test_get_empty(self):
        q = TaskQueue()
        self.assertIsNone(q.get_next())

    def test_highest_priority_first(self):
        q = TaskQueue()
        q.add_task("low", 1)
        q.add_task("high", 10)
        q.add_task("mid", 5)
        self.assertEqual(q.get_next(), "high")
        self.assertEqual(q.get_next(), "mid")
        self.assertEqual(q.get_next(), "low")

    def test_tiebreak_alphabetical(self):
        q = TaskQueue()
        q.add_task("banana", 5)
        q.add_task("apple", 5)
        q.add_task("cherry", 5)
        self.assertEqual(q.get_next(), "apple")
        self.assertEqual(q.get_next(), "banana")
        self.assertEqual(q.get_next(), "cherry")

    def test_duplicate_task_raises(self):
        q = TaskQueue()
        q.add_task("t1", 5)
        with self.assertRaises(RuntimeError):
            q.add_task("t1", 10)


class TestLevel2(unittest.TestCase):
    def test_size(self):
        q = TaskQueue()
        self.assertEqual(q.size(), 0)
        q.add_task("a", 1)
        q.add_task("b", 2)
        self.assertEqual(q.size(), 2)
        q.get_next()
        self.assertEqual(q.size(), 1)

    def test_peek_does_not_remove(self):
        q = TaskQueue()
        q.add_task("a", 5)
        q.add_task("b", 10)
        self.assertEqual(q.peek(), "b")
        self.assertEqual(q.peek(), "b")
        self.assertEqual(q.size(), 2)

    def test_peek_empty(self):
        q = TaskQueue()
        self.assertIsNone(q.peek())


class TestLevel3(unittest.TestCase):
    def test_get_next_at_filters_future(self):
        q = TaskQueue()
        q.add_task_at(10, "early", 5)
        q.add_task_at(20, "late", 10)
        # At t=15, only "early" is visible
        self.assertEqual(q.get_next_at(15), "early")
        # At t=25, "late" is now visible
        self.assertEqual(q.get_next_at(25), "late")


if __name__ == "__main__":
    unittest.main()
