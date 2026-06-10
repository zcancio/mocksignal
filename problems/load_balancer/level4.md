## Level 4 — Snapshot & Restore

- **`snapshot(timestamp)`**
  - Record the state at this timestamp. Returns an opaque snapshot id.

- **`restore(snapshot_id)`**
  - Restore the load balancer to that snapshot.
  - TTLs are recalculated relative to the snapshot's timestamp: if a
    request had 5 seconds left at snapshot time, it still has 5 left
    after restore.
  - After restore, the current logical time is the snapshot's timestamp.
  - `RuntimeError` if the snapshot id is unknown.
