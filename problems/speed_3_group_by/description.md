# Speed 3 — Group By

_Speed warmup &middot; target: under 5 minutes._

Given a list of dicts and a key, implement `group_by(items, key)` — return a
dict grouping the items by the value of that key. Items in each group keep
their original order.

```python
items = [
    {"name": "alice", "team": "A"},
    {"name": "bob",   "team": "B"},
    {"name": "carol", "team": "A"},
]
group_by(items, "team")
# -> {"A": [alice, carol], "B": [bob]}
```

Then implement `count_by(items, key)` — same shape, but values are counts
instead of lists: `count_by(items, "team")` → `{"A": 2, "B": 1}`.

_The test file is the spec — open `tests.py` from the Files panel for the
exact expected behaviour._
