## Level 1 — Set & Get

Implement the basics of the store.

- `set(key, value)` — store `value` under `key`. Overwrites any existing value.
- `get(key)` — return the value stored under `key`, or `None` if the key is
  not present.

### Example

```python
store = KVStore()
store.set("name", "ada")
store.get("name")     # -> "ada"
store.get("missing")  # -> None
```
