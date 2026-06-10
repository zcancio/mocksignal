import unittest
from solution import TTLStore


class TestTTLStore(unittest.TestCase):
    def test_set_and_get(self):
        s = TTLStore()
        s.set_at(0, "a", "alpha")
        self.assertEqual(s.get_at(0, "a"), "alpha")

    def test_get_unset_returns_none(self):
        s = TTLStore()
        self.assertIsNone(s.get_at(0, "nope"))

    def test_overwrite(self):
        s = TTLStore()
        s.set_at(0, "a", "alpha")
        s.set_at(5, "a", "beta")
        self.assertEqual(s.get_at(5, "a"), "beta")

    def test_ttl_expires(self):
        s = TTLStore()
        s.set_at(0, "a", "alpha", ttl=10)
        self.assertEqual(s.get_at(5, "a"), "alpha")
        # At exactly t=10 the key has expired
        self.assertIsNone(s.get_at(10, "a"))
        self.assertIsNone(s.get_at(11, "a"))

    def test_no_ttl_never_expires(self):
        s = TTLStore()
        s.set_at(0, "a", "alpha")
        self.assertEqual(s.get_at(1000000, "a"), "alpha")

    def test_overwrite_resets_ttl(self):
        s = TTLStore()
        s.set_at(0, "a", "alpha", ttl=10)
        s.set_at(5, "a", "beta", ttl=10)
        # New TTL means expiry at 5+10=15
        self.assertEqual(s.get_at(14, "a"), "beta")
        self.assertIsNone(s.get_at(15, "a"))

    def test_delete_at(self):
        s = TTLStore()
        s.set_at(0, "a", "alpha")
        s.delete_at(5, "a")
        self.assertIsNone(s.get_at(5, "a"))

    def test_delete_nonexistent_raises(self):
        s = TTLStore()
        with self.assertRaises(RuntimeError):
            s.delete_at(0, "nope")

    def test_delete_expired_raises(self):
        s = TTLStore()
        s.set_at(0, "a", "alpha", ttl=5)
        with self.assertRaises(RuntimeError):
            s.delete_at(10, "a")

    def test_keys_at(self):
        s = TTLStore()
        s.set_at(0, "banana", 1)
        s.set_at(0, "apple", 1, ttl=5)
        s.set_at(0, "cherry", 1)
        self.assertEqual(s.keys_at(3), ["apple", "banana", "cherry"])
        # At t=10, "apple" has expired
        self.assertEqual(s.keys_at(10), ["banana", "cherry"])


if __name__ == "__main__":
    unittest.main()
