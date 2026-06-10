## Level 1 — Basic scheduling

- **`schedule(task_id, deadline)`** — queue a task with the given integer
  deadline. `RuntimeError` if `task_id` is already queued.

- **`process_due(now)`** — return a list of `task_id`s whose deadline is
  `<= now`, in deadline order (earliest first), and remove them from the
  queue. Ties broken by `task_id` ascending.

- **`pending_count()`** — return the number of tasks still queued.
