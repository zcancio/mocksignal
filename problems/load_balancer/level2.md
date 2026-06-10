## Level 2 — Data Processing

- **`stats(server_id)`**
  - Return `{"capacity": int, "current_load": int, "total_handled": int}`.
  - `RuntimeError` if server doesn't exist.
  - `total_handled` is the lifetime count of requests routed to this
    server, completed or not.

- **`top_servers(n)`**
  - Return the top `n` servers by `total_handled` (descending).
  - Ties broken by lowest `server_id` (ascending).
  - If fewer than `n` servers exist, return all of them.
