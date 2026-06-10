# Micro-ICF 3 — TTL Key-Value Store

_Micro-ICF warmup &middot; target: 12 minutes. The closest analog to the ICF
Level 3 timestamp/TTL pattern, in miniature._

Implement an in-memory key-value store with TTL (time-to-live) support.

- **`set_at(timestamp, key, value, ttl=None)`** — set a key. If `ttl` is
  given, the key expires at `timestamp + ttl`.
- **`get_at(timestamp, key)`** — return the value if the key is set and not
  expired at this timestamp; `None` otherwise.
- **`delete_at(timestamp, key)`** — explicitly delete a key. `RuntimeError` if
  the key isn't currently set (doesn't exist, or already expired).
- **`keys_at(timestamp)`** — a list of all currently-set (non-expired) keys,
  sorted alphabetically.

Timestamps are non-decreasing across calls.

_The test file is the spec — open `tests.py` from the Files panel for the
exact expected behaviour._
