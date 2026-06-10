"""
Task Scheduler — solution stub.

Implement per SPEC.md.

    python3 -m unittest tests.py -v
"""


class Scheduler:
    def __init__(self):
        pass

    # ---- Level 1 ----
    def schedule(self, task_id, deadline):
        raise NotImplementedError

    def process_due(self, now):
        raise NotImplementedError

    def pending_count(self):
        raise NotImplementedError

    # ---- Level 2 ----
    def cancel(self, task_id):
        raise NotImplementedError

    def peek_next(self):
        raise NotImplementedError

    def tasks_due_by(self, now):
        raise NotImplementedError

    # ---- Level 3 ----
    def reschedule(self, task_id, new_deadline):
        raise NotImplementedError

    def schedule_with_priority(self, task_id, deadline, priority):
        raise NotImplementedError
