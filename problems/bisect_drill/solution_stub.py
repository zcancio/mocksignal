"""
BISECT DRILL — 6 problems, ~2-3 min each.

Each function operates on a SORTED list. Implement using `bisect`.
No loops, no `if x in arr`. The whole point is to drill bisect syntax.

Run: python3 -m unittest test_bisect_drill.py -v

If you get stuck, look at the cheat sheet at the bottom of this file.
"""
import bisect


def count_equal(arr, value):
    """How many elements of `arr` equal `value`?
    
    Example: count_equal([1, 2, 2, 2, 3], 2) -> 3
    """
    raise NotImplementedError


def count_in_range(arr, lo, hi):
    """How many elements of `arr` are in [lo, hi] inclusive?
    
    Example: count_in_range([1, 3, 5, 7, 9], 3, 7) -> 3
    """
    raise NotImplementedError


def count_less_than(arr, value):
    """How many elements of `arr` are strictly less than `value`?
    
    Example: count_less_than([1, 3, 5, 7], 5) -> 2
    """
    raise NotImplementedError


def insert_keeping_sorted(arr, value):
    """Insert `value` into `arr` so it stays sorted. Return arr.
    
    Example: insert_keeping_sorted([1, 3, 5], 4) -> [1, 3, 4, 5]
    """
    raise NotImplementedError


def remove_one(arr, value):
    """Remove ONE occurrence of `value` from `arr`. Return arr.
    If value isn't present, return arr unchanged.
    
    Example: remove_one([1, 2, 2, 3], 2) -> [1, 2, 3]
    Example: remove_one([1, 3, 5], 4) -> [1, 3, 5]
    """
    raise NotImplementedError


def closest_value(arr, target):
    """Return the value in `arr` closest to `target`.
    Ties broken by lower value. Assume arr is non-empty.
    
    Example: closest_value([1, 5, 10, 20], 7) -> 5
    Example: closest_value([1, 5, 10, 20], 8) -> 10
    Example: closest_value([1, 5, 10, 20], 7.5) -> 5  (tie → lower)
    """
    raise NotImplementedError


# =============================================================================
# CHEAT SHEET (look here when stuck)
# =============================================================================
"""
bisect.bisect_left(arr, v)   → first index where arr[i] >= v
bisect.bisect_right(arr, v)  → first index where arr[i] > v
bisect.insort(arr, v)        → insert v keeping sorted (same as insort_right)

Common patterns:

  # Count equal to v
  count = bisect_right(arr, v) - bisect_left(arr, v)

  # Count in [lo, hi] inclusive
  count = bisect_right(arr, hi) - bisect_left(arr, lo)

  # Count strictly less than v
  count = bisect_left(arr, v)

  # Count <= v
  count = bisect_right(arr, v)

  # Find an existing value's index (or where it would go)
  idx = bisect_left(arr, v)
  if idx < len(arr) and arr[idx] == v:
      # v is present at idx
      ...

  # Insert keeping sorted
  bisect.insort(arr, v)  # this MUTATES arr
"""
