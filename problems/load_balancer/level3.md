## Level 3 — Timestamps & TTL

Requests now have an optional time-to-live. After TTL expires, the
request is considered completed automatically — the slot frees up and
the request counts toward `total_handled`.

Add timestamped variants. Original methods continue to work for
backward compatibility: treat them as occurring at the current logical
time (the max timestamp seen so far, or 0 if none).

- **`route_at(timestamp, request_id, ttl=None)`**
  - Route at the given timestamp. If `ttl` is provided, the request
    auto-completes at `timestamp + ttl`.

- **`complete_at(timestamp, request_id)`**
  - Complete a request at the given timestamp.
  - `RuntimeError` if the request has already expired due to TTL.

- **`stats_at(timestamp, server_id)`**
  - Stats reflecting the state at the given timestamp.

- **`top_servers_at(timestamp, n)`**
  - Top servers by `total_handled` as of the given timestamp,
  including TTL-expired requests.

Timestamps are strictly non-decreasing across `_at` calls.
