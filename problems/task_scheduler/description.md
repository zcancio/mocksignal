# Task Scheduler

Implement a task scheduler that processes tasks at their scheduled times.
Tasks are queued with a deadline; the scheduler reports which tasks are
due as time progresses.

**Implementation tips:** Read all levels before coding. Don't change
existing method signatures. Submit often.

## Notes

- `task_id` is a non-empty string.
- `deadline` is a non-negative integer.
- `priority` is an integer (positive, negative, or zero).
- `now` is non-decreasing across `process_due` calls.
