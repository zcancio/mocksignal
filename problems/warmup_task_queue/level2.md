## Level 2 — State Queries

- **`size()`** — return the number of tasks currently in the queue.
- **`peek()`** — return the `task_id` of the task `get_next()` would return
  next, without removing it. Return `None` if the queue is empty.
