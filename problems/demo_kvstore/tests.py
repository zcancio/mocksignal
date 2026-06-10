import unittest

from solution import KVStore


class TestLevel1(unittest.TestCase):
    def test_set_then_get(self):
        s = KVStore()
        s.set("name", "ada")
        self.assertEqual(s.get("name"), "ada")

    def test_get_missing_returns_none(self):
        s = KVStore()
        self.assertIsNone(s.get("missing"))

    def test_set_overwrites(self):
        s = KVStore()
        s.set("k", 1)
        s.set("k", 2)
        self.assertEqual(s.get("k"), 2)


class TestLevel2(unittest.TestCase):
    def test_delete_present_key(self):
        s = KVStore()
        s.set("k", 1)
        self.assertTrue(s.delete("k"))
        self.assertIsNone(s.get("k"))

    def test_delete_missing_key(self):
        s = KVStore()
        self.assertFalse(s.delete("nope"))

    def test_keys_sorted(self):
        s = KVStore()
        s.set("banana", 1)
        s.set("apple", 2)
        s.set("cherry", 3)
        self.assertEqual(s.keys(), ["apple", "banana", "cherry"])


class TestLevel3(unittest.TestCase):
    def test_value_readable_before_expiry(self):
        s = KVStore()
        s.set_with_ttl("k", "v", ttl=10, timestamp=100)
        self.assertEqual(s.get("k", timestamp=105), "v")

    def test_value_gone_after_expiry(self):
        s = KVStore()
        s.set_with_ttl("k", "v", ttl=10, timestamp=100)
        self.assertIsNone(s.get("k", timestamp=110))

    def test_plain_set_clears_ttl(self):
        s = KVStore()
        s.set_with_ttl("k", "v", ttl=10, timestamp=100)
        s.set("k", "fresh")
        self.assertEqual(s.get("k", timestamp=10_000), "fresh")


if __name__ == "__main__":
    unittest.main()
