"""
MICRO-ICF 3 — TTL Key-Value Store (target: 12 min)

Implement an in-memory key-value store that supports TTL (time to live).
This is the closest analog to the ICF L3 pattern, in miniature.

METHODS:
- set_at(timestamp, key, value, ttl=None): set a key. If ttl is given,
  the key expires at timestamp + ttl.
- get_at(timestamp, key): return the current value if the key is set
  and not expired at this timestamp. Return None otherwise.
- delete_at(timestamp, key): explicitly delete a key. RuntimeError if
  the key isn't currently set (i.e. doesn't exist or already expired).
- keys_at(timestamp): return a list of all currently-set (non-expired)
  keys, sorted alphabetically.

Timestamps are non-decreasing across calls.

Run: python -m unittest test_micro_3_ttl_kv.py -v
"""


class TTLStore:
    def __init__(self):
        raise NotImplementedError

    def set_at(self, timestamp, key, value, ttl=None):
        raise NotImplementedError

    def get_at(self, timestamp, key):
        raise NotImplementedError

    def delete_at(self, timestamp, key):
        raise NotImplementedError

    def keys_at(self, timestamp):
        raise NotImplementedError
