## Level 6 — Concurrency

All public methods must be thread-safe. The capacity invariant must
hold under concurrent `route` calls: if a server has capacity C and
many threads call `route` simultaneously, at most C succeed before
either `None` is returned or another server is chosen.

No deadlocks.
