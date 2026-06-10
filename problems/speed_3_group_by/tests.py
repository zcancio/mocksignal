import unittest
from solution import group_by, count_by


class TestGroupBy(unittest.TestCase):
    def test_basic(self):
        items = [
            {"name": "alice", "team": "A"},
            {"name": "bob", "team": "B"},
            {"name": "carol", "team": "A"},
        ]
        result = group_by(items, "team")
        self.assertEqual(set(result.keys()), {"A", "B"})
        self.assertEqual([i["name"] for i in result["A"]], ["alice", "carol"])
        self.assertEqual([i["name"] for i in result["B"]], ["bob"])

    def test_empty(self):
        self.assertEqual(group_by([], "team"), {})

    def test_single_group(self):
        items = [{"team": "A"}, {"team": "A"}]
        result = group_by(items, "team")
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result["A"]), 2)


class TestCountBy(unittest.TestCase):
    def test_basic(self):
        items = [{"team": "A"}, {"team": "B"}, {"team": "A"}, {"team": "A"}]
        self.assertEqual(count_by(items, "team"), {"A": 3, "B": 1})

    def test_empty(self):
        self.assertEqual(count_by([], "team"), {})


if __name__ == "__main__":
    unittest.main()
