"""
Tests for the Load Balancer problem.

Run with: python -m unittest tests.py -v
"""

import itertools
import threading
import time
import unittest

from solution import LoadBalancer


# ===========================================================================
# LEVEL 1
# ===========================================================================
class TestLevel1(unittest.TestCase):
    def test_route_to_only_server(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        self.assertEqual(lb.route("r1"), "s1")

    def test_route_no_servers_returns_none(self):
        lb = LoadBalancer()
        self.assertIsNone(lb.route("r1"))

    def test_route_full_server_returns_none(self):
        lb = LoadBalancer()
        lb.add_server("s1", 2)
        lb.route("r1")
        lb.route("r2")
        self.assertIsNone(lb.route("r3"))

    def test_route_picks_lowest_load(self):
        lb = LoadBalancer()
        lb.add_server("s1", 10)
        lb.add_server("s2", 10)
        # Both empty: s1 wins by id
        self.assertEqual(lb.route("r1"), "s1")
        # s1=1, s2=0: s2 wins by load
        self.assertEqual(lb.route("r2"), "s2")
        # both=1: s1 wins by id
        self.assertEqual(lb.route("r3"), "s1")

    def test_complete_frees_slot(self):
        lb = LoadBalancer()
        lb.add_server("s1", 1)
        lb.route("r1")
        self.assertIsNone(lb.route("r2"))
        lb.complete("r1")
        self.assertEqual(lb.route("r2"), "s1")

    def test_add_duplicate_raises(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        with self.assertRaises(RuntimeError):
            lb.add_server("s1", 10)

    def test_remove_nonexistent_raises(self):
        lb = LoadBalancer()
        with self.assertRaises(RuntimeError):
            lb.remove_server("s1")

    def test_complete_unrouted_raises(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        with self.assertRaises(RuntimeError):
            lb.complete("nope")

    def test_complete_twice_raises(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        lb.route("r1")
        lb.complete("r1")
        with self.assertRaises(RuntimeError):
            lb.complete("r1")

    def test_remove_server_works(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        lb.add_server("s2", 5)
        lb.remove_server("s1")
        for i in range(5):
            self.assertEqual(lb.route(f"r{i}"), "s2")
        self.assertIsNone(lb.route("r5"))


# ===========================================================================
# LEVEL 2
# ===========================================================================
class TestLevel2(unittest.TestCase):
    def test_stats_initial(self):
        lb = LoadBalancer()
        lb.add_server("s1", 10)
        self.assertEqual(
            lb.stats("s1"),
            {"capacity": 10, "current_load": 0, "total_handled": 0},
        )

    def test_stats_after_routing(self):
        lb = LoadBalancer()
        lb.add_server("s1", 10)
        lb.route("r1")
        lb.route("r2")
        s = lb.stats("s1")
        self.assertEqual(s["current_load"], 2)
        self.assertEqual(s["total_handled"], 2)

    def test_stats_after_completion(self):
        lb = LoadBalancer()
        lb.add_server("s1", 10)
        lb.route("r1")
        lb.complete("r1")
        s = lb.stats("s1")
        self.assertEqual(s["current_load"], 0)
        self.assertEqual(s["total_handled"], 1)

    def test_stats_unknown_server_raises(self):
        lb = LoadBalancer()
        with self.assertRaises(RuntimeError):
            lb.stats("nope")

    def test_top_servers_basic(self):
        lb = LoadBalancer()
        lb.add_server("a", 100)
        lb.add_server("b", 100)
        lb.add_server("c", 100)
        # Route 6 round-robin (per L1 policy): r1->a, r2->b, r3->c, r4->a, ...
        # totals: a=2, b=2, c=2 — all tied.  top_servers(2) returns alphabetical.
        for i in range(6):
            lb.route(f"r{i}")
        self.assertEqual(lb.top_servers(2), ["a", "b"])

    def test_top_servers_more_than_exist(self):
        lb = LoadBalancer()
        lb.add_server("s1", 10)
        self.assertEqual(lb.top_servers(5), ["s1"])

    def test_top_servers_zero(self):
        lb = LoadBalancer()
        lb.add_server("s1", 10)
        self.assertEqual(lb.top_servers(0), [])

    def test_top_servers_alphabetical_tiebreak(self):
        lb = LoadBalancer()
        lb.add_server("banana", 10)
        lb.add_server("apple", 10)
        lb.add_server("cherry", 10)
        self.assertEqual(lb.top_servers(3), ["apple", "banana", "cherry"])

    def test_top_servers_by_total_uneven(self):
        lb = LoadBalancer()
        lb.add_server("a", 100)
        lb.add_server("b", 100)
        # Drive uneven totals: route 5 to 'a' while 'b' is removed
        lb.remove_server("b")
        for i in range(5):
            lb.route(f"r{i}")
            lb.complete(f"r{i}")
        lb.add_server("b", 100)
        # a: total=5, load=0. b: total=0, load=0.
        self.assertEqual(lb.top_servers(2), ["a", "b"])


# ===========================================================================
# LEVEL 3
# ===========================================================================
class TestLevel3(unittest.TestCase):
    def test_route_at_basic(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        self.assertEqual(lb.route_at(0, "r1"), "s1")

    def test_ttl_auto_completes(self):
        lb = LoadBalancer()
        lb.add_server("s1", 1)
        lb.route_at(0, "r1", ttl=10)
        # At t=5, still occupied
        self.assertIsNone(lb.route_at(5, "r2"))
        # At t=11, r1 has expired
        self.assertEqual(lb.route_at(11, "r3"), "s1")

    def test_no_ttl_stays_until_completed(self):
        lb = LoadBalancer()
        lb.add_server("s1", 1)
        lb.route_at(0, "r1")
        self.assertIsNone(lb.route_at(1000000, "r2"))

    def test_complete_at_after_ttl_raises(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        lb.route_at(0, "r1", ttl=10)
        with self.assertRaises(RuntimeError):
            lb.complete_at(20, "r1")

    def test_complete_at_before_ttl_works(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        lb.route_at(0, "r1", ttl=100)
        lb.complete_at(5, "r1")

    def test_stats_at_reflects_ttl(self):
        lb = LoadBalancer()
        lb.add_server("s1", 10)
        lb.route_at(0, "r1", ttl=5)
        lb.route_at(1, "r2", ttl=100)
        lb.route_at(2, "r3")
        # At t=3, all 3 active
        s = lb.stats_at(3, "s1")
        self.assertEqual(s["current_load"], 3)
        self.assertEqual(s["total_handled"], 3)
        # At t=10, r1 expired
        s = lb.stats_at(10, "s1")
        self.assertEqual(s["current_load"], 2)
        self.assertEqual(s["total_handled"], 3)

    def test_top_servers_at_counts_expirations(self):
        lb = LoadBalancer()
        lb.add_server("s1", 10)
        lb.add_server("s2", 10)
        lb.route_at(0, "a", ttl=1)
        lb.route_at(0, "b", ttl=1)
        lb.route_at(0, "c", ttl=1)
        lb.route_at(0, "d", ttl=100)
        # After 4 routes with L1 policy (lowest load + id):
        # r=a → s1 (both 0, s1 wins); r=b → s2; r=c → s1; r=d → s2
        # totals: s1=2, s2=2
        # top_servers_at(50, 2) — alphabetical tie
        self.assertEqual(lb.top_servers_at(50, 2), ["s1", "s2"])

    def test_backward_compatible_route(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        lb.route_at(100, "r1")
        # route() with no timestamp uses current logical time
        lb.route("r2")
        s = lb.stats("s1")
        self.assertEqual(s["current_load"], 2)


# ===========================================================================
# LEVEL 4
# ===========================================================================
class TestLevel4(unittest.TestCase):
    def test_snapshot_and_restore_basic(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        lb.route_at(0, "r1")
        snap = lb.snapshot(5)
        lb.route_at(6, "r2")
        s = lb.stats_at(6, "s1")
        self.assertEqual(s["current_load"], 2)
        lb.restore(snap)
        s = lb.stats_at(5, "s1")
        self.assertEqual(s["current_load"], 1)

    def test_restore_unknown_raises(self):
        lb = LoadBalancer()
        with self.assertRaises(RuntimeError):
            lb.restore("bogus")

    def test_ttl_recalculated_after_restore(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        lb.route_at(0, "r1", ttl=10)  # expires at t=10
        snap = lb.snapshot(3)          # at snapshot time, 7 seconds left
        lb.route_at(4, "r2", ttl=10)
        lb.route_at(5, "r3")
        lb.restore(snap)
        # After restore, logical time = 3, r1 still has 7 left → expires at t=10
        s = lb.stats_at(9, "s1")
        self.assertEqual(s["current_load"], 1)
        s = lb.stats_at(11, "s1")
        self.assertEqual(s["current_load"], 0)

    def test_snapshot_preserves_total_handled(self):
        lb = LoadBalancer()
        lb.add_server("s1", 5)
        for i in range(3):
            lb.route_at(i, f"r{i}")
            lb.complete_at(i, f"r{i}")
        snap = lb.snapshot(5)
        for i in range(5):
            lb.route_at(10 + i, f"x{i}")
        lb.restore(snap)
        s = lb.stats_at(5, "s1")
        self.assertEqual(s["total_handled"], 3)


# ===========================================================================
# LEVEL 5 — scale
# ===========================================================================
class TestLevel5(unittest.TestCase):
    """These tests will fail with a naive O(S) route() implementation."""

    def test_many_routes(self):
        lb = LoadBalancer()
        for i in range(10000):
            lb.add_server(f"s{i:05d}", 100)
        start = time.time()
        for i in range(50000):
            lb.route(f"r{i}")
        elapsed = time.time() - start
        # With 10k servers and 50k routes, a naive O(S) scan is 500M ops.
        # An O(log S) implementation should finish in <3s. 5s margin.
        self.assertLess(elapsed, 5.0,
                        f"50k routes over 10k servers took {elapsed:.2f}s")

    def test_top_servers_at_scale(self):
        lb = LoadBalancer()
        for i in range(10000):
            lb.add_server(f"s{i:05d}", 100)
        for i in range(50000):
            lb.route(f"r{i}")
        start = time.time()
        for _ in range(100):
            lb.top_servers(10)
        elapsed = time.time() - start
        self.assertLess(elapsed, 3.0,
                        f"100x top_servers(10) over 10k servers took {elapsed:.2f}s")


# ===========================================================================
# LEVEL 6 — concurrency
# ===========================================================================
class TestLevel6(unittest.TestCase):
    def test_concurrent_routes_respect_capacity(self):
        lb = LoadBalancer()
        lb.add_server("s1", 100)
        results = []
        results_lock = threading.Lock()

        def worker(i):
            r = lb.route(f"r{i}")
            with results_lock:
                results.append(r)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(500)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        routed = sum(1 for r in results if r == "s1")
        self.assertEqual(routed, 100)

    def test_concurrent_mixed_ops_no_crash(self):
        lb = LoadBalancer()
        for i in range(5):
            lb.add_server(f"s{i}", 1000)

        counter = itertools.count()
        cl = threading.Lock()
        def next_id():
            with cl:
                return next(counter)

        def router():
            for _ in range(500):
                lb.route(f"r{next_id()}")

        def querier():
            for _ in range(500):
                try:
                    lb.stats("s0")
                except RuntimeError:
                    pass

        threads = [threading.Thread(target=router) for _ in range(3)]
        threads += [threading.Thread(target=querier) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # No deadlock and no crash = pass


if __name__ == "__main__":
    unittest.main()
