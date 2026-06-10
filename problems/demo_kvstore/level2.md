## Level 2 — Delete & List

Extend the store with removal and inspection.

- `delete(key)` — remove `key` from the store. Return `True` if the key was
  present, `False` otherwise.
- `keys()` — return a list of all current keys, sorted alphabetically.

### Example

```python
store = KVStore()
store.set("b", 1)
store.set("a", 2)
store.keys()        # -> ["a", "b"]
store.delete("a")   # -> True
store.delete("a")   # -> False
```
