# Warmup — Task Queue

A small, self-contained ICF micro-rep for test-day morning — one class, six
methods, three levels, ~50 lines. The goal isn't to learn anything new; it's
to be in problem-mode with your fingers warm before the real timer starts.

Build the `TaskQueue` class in `solution.py`, one level at a time. Time-box it
to about 15 minutes — if you don't finish, that's fine; the rep is the point.

This problem's directory also contains `hang_check.py`. In the **Terminal**
tab, run `python3 hang_check.py` for a quick hang-debugging sanity check — it
deliberately deadlocks, dumps both thread stacks via `faulthandler`, and exits
in ~2 seconds. If you can read the dump and spot the lock-ordering bug, your
hang-debugging muscle is warm.
