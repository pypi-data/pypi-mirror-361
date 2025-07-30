import unittest
from nuts_lookup import NutsLookup

class TestNutsLookup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lookup = NutsLookup()

    def test_valid_lookup(self):
        result = self.lookup.get_nuts_code("DE", "10115")
        self.assertEqual(result, "DE300")

    def test_valid_nuts1(self):
        result = self.lookup.get_nuts1_code("DE", "10115")
        self.assertEqual(result, "DE3")

    def test_valid_nuts2(self):
        result = self.lookup.get_nuts2_code("DE", "10115")
        self.assertEqual(result, "DE30")

    def test_invalid_country(self):
        self.assertIsNone(self.lookup.get_nuts_code("XX", "10115"))
        self.assertIsNone(self.lookup.get_nuts1_code("XX", "10115"))
        self.assertIsNone(self.lookup.get_nuts2_code("XX", "10115"))

    def test_invalid_zip(self):
        self.assertIsNone(self.lookup.get_nuts_code("DE", "99999"))
        self.assertIsNone(self.lookup.get_nuts1_code("DE", "99999"))
        self.assertIsNone(self.lookup.get_nuts2_code("DE", "99999"))

    def test_case_insensitivity(self):
        result = self.lookup.get_nuts_code("de", "10115")
        self.assertEqual(result, "DE300")

    def test_empty_input(self):
        self.assertIsNone(self.lookup.get_nuts_code("", ""))
        self.assertIsNone(self.lookup.get_nuts1_code("", ""))
        self.assertIsNone(self.lookup.get_nuts2_code("", ""))

if __name__ == '__main__':
    unittest.main()
