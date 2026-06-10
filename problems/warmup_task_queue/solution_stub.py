"""
WARMUP — Task Queue

Build a simple priority task queue with timestamped operations.

Level 1: basic add/get
- add_task(task_id, priority): add a task with an integer priority.
  RuntimeError if task_id already exists.
- get_next(): return the task_id of the highest-priority task and remove
  it from the queue. Ties broken by lowest task_id (string compare).
  Return None if the queue is empty.

Level 2: state queries
- size(): return the number of tasks currently in the queue.
- peek(): return the task_id of the next task to be returned by
  get_next(), without removing it. Return None if empty.

Level 3: timestamps
- add_task_at(timestamp, task_id, priority): same as add_task, with a
  timestamp. Timestamps are non-decreasing across calls.
- get_next_at(timestamp): same as get_next, but only considers tasks
  added at or before the given timestamp.

Reasonable to aim for in 15 minutes. The point is a clean rep, not
finishing every level.
"""


class TaskQueue:
    def __init__(self):
        # TODO
        pass

    def add_task(self, task_id, priority):
        raise NotImplementedError

    def get_next(self):
        raise NotImplementedError

    def size(self):
        raise NotImplementedError

    def peek(self):
        raise NotImplementedError

    def add_task_at(self, timestamp, task_id, priority):
        raise NotImplementedError

    def get_next_at(self, timestamp):
        raise NotImplementedError
