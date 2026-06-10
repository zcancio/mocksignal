"""
SPEED WARMUP 3 — Group By (target: under 5 min)

Given a list of dicts and a key, return a dict that groups the items by
the value of that key.

Example:
    items = [
        {"name": "alice", "team": "A"},
        {"name": "bob", "team": "B"},
        {"name": "carol", "team": "A"},
    ]
    group_by(items, "team")
    -> {"A": [{"name": "alice", ...}, {"name": "carol", ...}], "B": [{"name": "bob", ...}]}

Items in each group should retain their original order.

Then implement count_by(items, key) — same shape, but values are counts
instead of lists.
    count_by(items, "team") -> {"A": 2, "B": 1}

Run: python -m unittest test_speed_3_group_by.py -v
"""


def group_by(items, key):
    raise NotImplementedError


def count_by(items, key):
    raise NotImplementedError
