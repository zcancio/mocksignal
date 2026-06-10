## Level 3 — Expiry (TTL)

Add support for keys that expire after a time-to-live.

- `set_with_ttl(key, value, ttl, timestamp)` — store `value` under `key`,
  set at `timestamp`, expiring `ttl` seconds later (exactly at
  `timestamp + ttl`).
- `get(key, timestamp=None)` — if the key was set with a TTL and
  `timestamp >= expiry`, treat the key as absent and return `None`.
- A plain `set(key, value)` clears any TTL previously attached to `key`.

### Example

```python
store = KVStore()
store.set_with_ttl("session", "abc", ttl=10, timestamp=100)
store.get("session", timestamp=105)  # -> "abc"
store.get("session", timestamp=110)  # -> None  (expired)
```
