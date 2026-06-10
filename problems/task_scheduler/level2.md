## Level 2 — Cancellation & queries

- **`cancel(task_id)`** — remove a task without processing it.
  `RuntimeError` if not queued.

- **`peek_next()`** — return the `(task_id, deadline)` of the next task
  due, without removing it. Return `None` if queue is empty.

- **`tasks_due_by(now)`** — return the COUNT of tasks with deadline
  `<= now`, without removing them.
