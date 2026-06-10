# Micro-ICF 2 — Hit Counter

_Micro-ICF warmup &middot; target: 10 minutes._

Implement a `HitCounter` that records timestamped hits and answers range
queries.

- **`hit(timestamp)`** — record a hit. Timestamps are non-decreasing across
  calls.
- **`count_in_range(start, end)`** — number of hits with timestamp in
  `[start, end]` (inclusive).
- **`count_in_last(now, window)`** — number of hits with timestamp in
  `(now - window, now]` (exclusive lower bound, inclusive upper).
- **`earliest_hit()`** — the earliest timestamp recorded, or `None`.

A good warmup for the ICF Level 3 timestamp pattern — keep hits in a sorted
structure and lean on the fact that they arrive in order.

_The test file is the spec — open `tests.py` from the Files panel for the
exact expected behaviour._
