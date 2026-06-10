"""
MICRO-ICF 1 — Inventory Tracker (target: 10 min)

Implement an Inventory class that tracks item quantities.

METHODS:
- add(item, quantity): add `quantity` units of `item`. Quantity is a
  positive integer.
- remove(item, quantity): remove `quantity` units. RuntimeError if not
  enough in stock or item doesn't exist.
- get(item): return the current quantity of `item`. Return 0 if not in
  inventory (don't raise).
- top_items(n): return the top n items by quantity, descending.
  Ties broken alphabetically. List of (item, quantity) tuples.

Run: python -m unittest test_micro_1_inventory.py -v
"""


class Inventory:
    def __init__(self):
        raise NotImplementedError

    def add(self, item, quantity):
        raise NotImplementedError

    def remove(self, item, quantity):
        raise NotImplementedError

    def get(self, item):
        raise NotImplementedError

    def top_items(self, n):
        raise NotImplementedError
