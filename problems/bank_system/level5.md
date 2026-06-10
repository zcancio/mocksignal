## Level 5 — Concurrency

The `Simulation` must now be **thread-safe**. The methods from Levels 1–4 may
be called from many threads at once, and must still behave correctly.

- **No lost updates** — 100 threads each depositing \$10 to one account must
  leave exactly \$1000, never \$990 or \$1010.
- **Money is conserved** — concurrent `transfer`s between accounts must never
  create or destroy money. The system-wide total stays invariant.
- **Correct under mixed load** — concurrent readers (`get_balance`) and
  writers (`deposit`) must not crash, and the final state must be exact.
- **No deadlocks** — however you choose to lock, the program must always make
  progress and finish.

The external API does not change — add whatever synchronization you need
inside the class. The standard library is enough (`threading.Lock`,
`threading.RLock`).
