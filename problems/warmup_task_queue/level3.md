## Level 3 — Timestamps

- **`add_task_at(timestamp, task_id, priority)`** — same as `add_task`, but
  with a `timestamp`. Timestamps are non-decreasing across calls.
- **`get_next_at(timestamp)`** — same as `get_next`, but only considers tasks
  added at or before the given `timestamp`.
