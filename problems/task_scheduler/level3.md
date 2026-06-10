## Level 3 — Reschedule & priorities

- **`reschedule(task_id, new_deadline)`** — change a task's deadline.
  `RuntimeError` if not queued.

- **`schedule_with_priority(task_id, deadline, priority)`** — same as
  schedule but with an integer priority. When multiple tasks have the
  same deadline, higher priority comes first. Default priority is 0
  for tasks queued via plain `schedule`.

- **`process_due(now)`** must respect priority for ties. Order within
  same deadline: priority desc, then task_id asc.
