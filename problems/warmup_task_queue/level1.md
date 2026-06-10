## Level 1 — Basic Add & Get

- **`add_task(task_id, priority)`** — add a task with an integer `priority`.
  Raise `RuntimeError` if `task_id` already exists.
- **`get_next()`** — return the `task_id` of the highest-priority task and
  remove it from the queue. Ties are broken by lowest `task_id` (string
  comparison). Return `None` if the queue is empty.
