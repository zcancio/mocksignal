import unittest
from solution import Inventory


class TestInventory(unittest.TestCase):
    def test_add_and_get(self):
        inv = Inventory()
        inv.add("apple", 5)
        self.assertEqual(inv.get("apple"), 5)

    def test_add_existing_accumulates(self):
        inv = Inventory()
        inv.add("apple", 5)
        inv.add("apple", 3)
        self.assertEqual(inv.get("apple"), 8)

    def test_get_nonexistent_returns_zero(self):
        inv = Inventory()
        self.assertEqual(inv.get("banana"), 0)

    def test_remove_basic(self):
        inv = Inventory()
        inv.add("apple", 10)
        inv.remove("apple", 3)
        self.assertEqual(inv.get("apple"), 7)

    def test_remove_too_many_raises(self):
        inv = Inventory()
        inv.add("apple", 5)
        with self.assertRaises(RuntimeError):
            inv.remove("apple", 10)

    def test_remove_nonexistent_raises(self):
        inv = Inventory()
        with self.assertRaises(RuntimeError):
            inv.remove("banana", 1)

    def test_top_items_basic(self):
        inv = Inventory()
        inv.add("apple", 5)
        inv.add("banana", 10)
        inv.add("cherry", 3)
        self.assertEqual(inv.top_items(2), [("banana", 10), ("apple", 5)])

    def test_top_items_alphabetical_tiebreak(self):
        inv = Inventory()
        inv.add("banana", 5)
        inv.add("apple", 5)
        inv.add("cherry", 5)
        self.assertEqual(
            inv.top_items(3),
            [("apple", 5), ("banana", 5), ("cherry", 5)],
        )

    def test_top_items_more_than_exist(self):
        inv = Inventory()
        inv.add("apple", 5)
        self.assertEqual(inv.top_items(10), [("apple", 5)])


if __name__ == "__main__":
    unittest.main()
