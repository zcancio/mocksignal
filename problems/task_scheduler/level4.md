## Level 4 — Scale

- 100,000 tasks queued, 100,000 process_due calls. `process_due` and
  `schedule` must each run in O(log N) amortized.
- `reschedule` may be O(log N) amortized — you don't need to mutate
  existing heap entries.
- `cancel` may be O(log N) amortized via lazy deletion.

---

## Hint (read if stuck on L4)

The hot path is `schedule` and `process_due`. Use a heap keyed on
`(deadline, -priority, task_id)`. Tuple ordering does the multi-level
sort for free. For cancel and reschedule, use **lazy deletion** — never
modify heap entries, just mark them invalid in a separate dict, and
skip them when they surface to the top.
