"""
SPEED WARMUP 2 — Merge Intervals (target: under 5 min)

Given a list of [start, end] intervals (closed on both ends), merge any
overlapping or touching intervals and return the result sorted by start.

Intervals that touch (e.g. [1, 3] and [3, 5]) should be merged into [1, 5].

Example:
    merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])
    -> [[1, 6], [8, 10], [15, 18]]

Then implement total_coverage(intervals) which returns the total number
of integer units covered by the (possibly overlapping) intervals.
For [[1, 3], [2, 6]] the coverage is 1..6 = 6 units.

Run: python -m unittest test_speed_2_interval_merge.py -v
"""


def merge_intervals(intervals):
    raise NotImplementedError


def total_coverage(intervals):
    raise NotImplementedError
