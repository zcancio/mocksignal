class KVStore:
    """In-memory key-value store. Implement each level's methods below."""

    def __init__(self):
        pass

    # --- Level 1 ---
    def set(self, key, value):
        raise NotImplementedError

    def get(self, key, timestamp=None):
        raise NotImplementedError

    # --- Level 2 ---
    def delete(self, key):
        raise NotImplementedError

    def keys(self):
        raise NotImplementedError

    # --- Level 3 ---
    def set_with_ttl(self, key, value, ttl, timestamp):
        raise NotImplementedError
