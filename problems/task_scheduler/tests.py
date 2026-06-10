"""
Tests for the Task Scheduler.

    python3 -m unittest tests.py -v
"""

import time
import unittest

from solution import Scheduler


class TestLevel1(unittest.TestCase):
    def test_schedule_and_process(self):
        s = Scheduler()
        s.schedule("a", 10)
        self.assertEqual(s.process_due(10), ["a"])

    def test_nothing_due_yet(self):
        s = Scheduler()
        s.schedule("a", 100)
        self.assertEqual(s.process_due(50), [])

    def test_process_removes_tasks(self):
        s = Scheduler()
        s.schedule("a", 10)
        s.process_due(10)
        self.assertEqual(s.process_due(10), [])

    def test_deadline_order(self):
        s = Scheduler()
        s.schedule("late", 30)
        s.schedule("early", 10)
        s.schedule("mid", 20)
        self.assertEqual(s.process_due(100), ["early", "mid", "late"])

    def test_tiebreak_alphabetical(self):
        s = Scheduler()
        s.schedule("c", 10)
        s.schedule("a", 10)
        s.schedule("b", 10)
        self.assertEqual(s.process_due(10), ["a", "b", "c"])

    def test_duplicate_raises(self):
        s = Scheduler()
        s.schedule("a", 10)
        with self.assertRaises(RuntimeError):
            s.schedule("a", 20)

    def test_pending_count(self):
        s = Scheduler()
        self.assertEqual(s.pending_count(), 0)
        s.schedule("a", 10)
        s.schedule("b", 20)
        self.assertEqual(s.pending_count(), 2)
        s.process_due(10)
        self.assertEqual(s.pending_count(), 1)


class TestLevel2(unittest.TestCase):
    def test_cancel_basic(self):
        s = Scheduler()
        s.schedule("a", 10)
        s.cancel("a")
        self.assertEqual(s.process_due(10), [])
        self.assertEqual(s.pending_count(), 0)

    def test_cancel_nonexistent_raises(self):
        s = Scheduler()
        with self.assertRaises(RuntimeError):
            s.cancel("nope")

    def test_cancel_one_of_many(self):
        s = Scheduler()
        s.schedule("a", 10)
        s.schedule("b", 20)
        s.schedule("c", 30)
        s.cancel("b")
        self.assertEqual(s.process_due(100), ["a", "c"])

    def test_peek_next(self):
        s = Scheduler()
        self.assertIsNone(s.peek_next())
        s.schedule("a", 100)
        s.schedule("b", 50)
        self.assertEqual(s.peek_next(), ("b", 50))

    def test_peek_does_not_remove(self):
        s = Scheduler()
        s.schedule("a", 10)
        s.peek_next()
        s.peek_next()
        self.assertEqual(s.pending_count(), 1)

    def test_tasks_due_by(self):
        s = Scheduler()
        s.schedule("a", 10)
        s.schedule("b", 20)
        s.schedule("c", 30)
        self.assertEqual(s.tasks_due_by(15), 1)
        self.assertEqual(s.tasks_due_by(25), 2)
        self.assertEqual(s.tasks_due_by(100), 3)
        # tasks_due_by does NOT remove
        self.assertEqual(s.pending_count(), 3)


class TestLevel3(unittest.TestCase):
    def test_reschedule_basic(self):
        s = Scheduler()
        s.schedule("a", 100)
        s.reschedule("a", 5)
        self.assertEqual(s.process_due(10), ["a"])

    def test_reschedule_nonexistent_raises(self):
        s = Scheduler()
        with self.assertRaises(RuntimeError):
            s.reschedule("nope", 10)

    def test_reschedule_changes_order(self):
        s = Scheduler()
        s.schedule("a", 10)
        s.schedule("b", 20)
        s.reschedule("a", 30)  # a now last
        self.assertEqual(s.process_due(100), ["b", "a"])

    def test_priority_tiebreaks_deadline(self):
        s = Scheduler()
        s.schedule_with_priority("low", 10, priority=1)
        s.schedule_with_priority("high", 10, priority=10)
        s.schedule_with_priority("mid", 10, priority=5)
        # Same deadline; priority desc decides order
        self.assertEqual(s.process_due(10), ["high", "mid", "low"])

    def test_priority_zero_default(self):
        s = Scheduler()
        s.schedule("plain", 10)            # priority 0
        s.schedule_with_priority("urgent", 10, priority=5)
        self.assertEqual(s.process_due(10), ["urgent", "plain"])

    def test_priority_negative(self):
        s = Scheduler()
        s.schedule_with_priority("low", 10, priority=-5)
        s.schedule("plain", 10)            # priority 0
        self.assertEqual(s.process_due(10), ["plain", "low"])

    def test_deadline_dominates_priority(self):
        s = Scheduler()
        s.schedule_with_priority("late_urgent", 100, priority=99)
        s.schedule_with_priority("early_low", 10, priority=1)
        # Deadline wins over priority
        self.assertEqual(s.process_due(10), ["early_low"])

    def test_priority_then_id_for_ties(self):
        s = Scheduler()
        s.schedule_with_priority("zebra", 10, priority=5)
        s.schedule_with_priority("apple", 10, priority=5)
        s.schedule_with_priority("banana", 10, priority=5)
        self.assertEqual(s.process_due(10), ["apple", "banana", "zebra"])


class TestLevel4(unittest.TestCase):
    """Scale: 100k tasks. O(log N) operations required."""

    def test_schedule_and_process_at_scale(self):
        s = Scheduler()
        start = time.time()
        for i in range(100000):
            s.schedule(f"t{i:06d}", i)
        elapsed = time.time() - start
        self.assertLess(elapsed, 3.0,
                        f"100k schedules took {elapsed:.2f}s; need O(log N)")

        start = time.time()
        # Process in chunks
        for chunk in range(0, 100000, 1000):
            s.process_due(chunk + 999)
        elapsed = time.time() - start
        self.assertLess(elapsed, 3.0,
                        f"100k tasks processed took {elapsed:.2f}s")

        self.assertEqual(s.pending_count(), 0)

    def test_cancel_at_scale(self):
        s = Scheduler()
        for i in range(100000):
            s.schedule(f"t{i:06d}", i)
        # Cancel every other task
        start = time.time()
        for i in range(0, 100000, 2):
            s.cancel(f"t{i:06d}")
        elapsed = time.time() - start
        self.assertLess(elapsed, 3.0,
                        f"50k cancels took {elapsed:.2f}s; need amortized O(log N)")
        self.assertEqual(s.pending_count(), 50000)

    def test_mixed_at_scale(self):
        s = Scheduler()
        for i in range(50000):
            s.schedule(f"t{i:06d}", i)
        # Mix of operations
        start = time.time()
        for i in range(0, 50000, 4):
            s.reschedule(f"t{i:06d}", 100000 + i)
        for i in range(1, 50000, 4):
            s.cancel(f"t{i:06d}")
        s.process_due(40000)
        elapsed = time.time() - start
        self.assertLess(elapsed, 3.0,
                        f"mixed ops took {elapsed:.2f}s")


if __name__ == "__main__":
    unittest.main()
