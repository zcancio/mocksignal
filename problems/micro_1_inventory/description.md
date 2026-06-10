# Micro-ICF 1 — Inventory Tracker

_Micro-ICF warmup &middot; target: 10 minutes._

Implement an `Inventory` class that tracks item quantities.

- **`add(item, quantity)`** — add `quantity` units of `item` (a positive
  integer).
- **`remove(item, quantity)`** — remove `quantity` units. `RuntimeError` if
  there isn't enough in stock, or the item doesn't exist.
- **`get(item)`** — return the current quantity of `item`; `0` if it isn't in
  the inventory (don't raise).
- **`top_items(n)`** — the top `n` items by quantity, descending, ties broken
  alphabetically. A list of `(item, quantity)` tuples.

_The test file is the spec — open `tests.py` from the Files panel for the
exact expected behaviour._
