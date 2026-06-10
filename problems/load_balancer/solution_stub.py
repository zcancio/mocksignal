"""
Load Balancer — solution stub.

Implement per SPEC.md. Run tests with:
    python -m unittest tests.py -v
"""


class LoadBalancer:
    def __init__(self):
        pass

    # ---- Level 1 ----
    def add_server(self, server_id, capacity):
        raise NotImplementedError

    def remove_server(self, server_id):
        raise NotImplementedError

    def route(self, request_id):
        raise NotImplementedError

    def complete(self, request_id):
        raise NotImplementedError

    # ---- Level 2 ----
    def stats(self, server_id):
        raise NotImplementedError

    def top_servers(self, n):
        raise NotImplementedError

    # ---- Level 3 ----
    def route_at(self, timestamp, request_id, ttl=None):
        raise NotImplementedError

    def complete_at(self, timestamp, request_id):
        raise NotImplementedError

    def stats_at(self, timestamp, server_id):
        raise NotImplementedError

    def top_servers_at(self, timestamp, n):
        raise NotImplementedError

    # ---- Level 4 ----
    def snapshot(self, timestamp):
        raise NotImplementedError

    def restore(self, snapshot_id):
        raise NotImplementedError
