"""
MICRO-ICF 2 — Hit Counter (target: 10 min)

Implement a HitCounter that records timestamped hits and answers
range queries.

METHODS:
- hit(timestamp): record a hit at the given timestamp. Timestamps are
  non-decreasing across calls.
- count_in_range(start, end): return the number of hits with timestamp
  in [start, end] (inclusive).
- count_in_last(now, window): return the number of hits with timestamp
  in (now - window, now] (exclusive on lower end, inclusive on upper).
- earliest_hit(): return the earliest timestamp recorded, or None.

Hint: this is a good warmup for the L3 timestamp pattern in ICF — keep
hits in a sorted structure, leverage that they arrive in order.

Run: python -m unittest test_micro_2_hit_counter.py -v
"""


class HitCounter:
    def __init__(self):
        raise NotImplementedError

    def hit(self, timestamp):
        raise NotImplementedError

    def count_in_range(self, start, end):
        raise NotImplementedError

    def count_in_last(self, now, window):
        raise NotImplementedError

    def earliest_hit(self):
        raise NotImplementedError
