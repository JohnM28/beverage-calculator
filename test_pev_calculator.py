import json
import unittest

from pev_calculator import BevCalculator, calculate_total_inventory


class TestBevCalculator(unittest.TestCase):

    def setUp(self):
        with open('test_data.json', 'r') as file:
            inc_data = json.load(file)
        self.packages = inc_data["packages"]
        self.counts = inc_data["counts"]

    def test_normal_calculation(self):
        bc = BevCalculator(self.packages, self.counts)
        self.assertEqual(bc.calculate_total_quantity(), 112100)

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            calculate_total_inventory([], self.counts)
        with self.assertRaises(ValueError):
            calculate_total_inventory(self.packages, [])

    def test_infinit_reference(self):
        packages = self.packages.copy()
        packages[0]["content_package_id"] = "pkg1"
        packages[1]["content_package_id"] = "pkg0"
        bc = BevCalculator(packages, self.counts)
        with self.assertRaises(ValueError):
            bc.calculate_total_quantity()

    def test_missing_package(self):
        counts_with_missing = self.counts + [{"package_id": "pkg5", "quantity": 10}]
        bc = BevCalculator(self.packages, counts_with_missing)
        with self.assertRaises(ValueError):
            bc.calculate_total_quantity()

    def test_negative_quantity(self):
        negative_counts = self.counts.copy()
        negative_counts[0]["quantity"] = -10
        bc = BevCalculator(self.packages, negative_counts)
        with self.assertRaises(ValueError):
            bc.calculate_total_quantity()

    def test_missing_base_unit(self):
        packages_without_base = self.packages.copy()
        packages_without_base[3]["content_unit"] = None
        bc = BevCalculator(packages_without_base, self.counts)
        with self.assertRaises(ValueError):
            bc.calculate_total_quantity()

    def test_different_base_unit(self):
        packages_different_unit = self.packages.copy()
        packages_different_unit[3]["content_unit"] = "l"
        bc = BevCalculator(packages_different_unit, self.counts)
        with self.assertRaises(ValueError):
            bc.calculate_total_quantity()


if __name__ == '__main__':
    unittest.main()
