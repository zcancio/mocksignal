# Speed 2 — Merge Intervals

_Speed warmup &middot; target: under 5 minutes._

Given a list of `[start, end]` intervals (closed on both ends), implement
`merge_intervals(intervals)` — merge any overlapping or touching intervals and
return the result sorted by start. Touching intervals (e.g. `[1, 3]` and
`[3, 5]`) merge into `[1, 5]`.

```python
merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])
# -> [[1, 6], [8, 10], [15, 18]]
```

Then implement `total_coverage(intervals)` — the total number of integer units
covered by the (possibly overlapping) intervals. For `[[1, 3], [2, 6]]` the
coverage is `1..6` = 6 units.

_The test file is the spec — open `tests.py` from the Files panel for the
exact expected behaviour._
