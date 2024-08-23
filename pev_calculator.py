from typing import Dict, List, Optional
import json


class BevCalculator:
    """
    Bev calculator class that calculates the total inventory of one product in different packaging in ml
    """

    def __init__(self, packages: List[Dict], counts: List[Dict]):
        self.packages = {p['id']: p for p in packages}
        self.counts = counts
        self.ml_content: Dict[str, float] = {}  # keep track of ml content for each package

    def calculate_total_quantity(self) -> float:
        """
        Calculate the total inventory in ml
        :return: Total inventory in ml
        """
        self._calculate_ml_content()
        return self._sum_quantity()

    def _calculate_ml_content(self) -> None:
        """
        calculate the ml content for each package
        :return:
        """
        for package_id in self.packages:
            self._calculate_package_ml(package_id)

    def _calculate_package_ml(self, package_id: str, visited: Optional[set] = None) -> float:
        """
        a recusrive function that calculates the ml content for a package and its sub-packages by updating the ml_content for each package
        :param package_id: package id
        :param visited: set of visited packages
        :return: ml content for the package
        """
        if visited is None:
            visited = set()  # keep track of visited packages to avoid infinite call stack

        if package_id in visited:  # handle infinite call stack for two packages referencing each other
            raise ValueError(f"Invalid reference for package {package_id}")
        visited.add(package_id)

        package = self.packages.get(package_id)
        if not package:  # invalid data with package id not found
            raise ValueError(f"Package {package_id} not found")

        if package['content_unit'] == 'ml':
            ml = package['quantity_of_content']
        elif package['content_package_id']:
            ml = package['quantity_of_content'] * self._calculate_package_ml(package['content_package_id'], visited)
        else:  # invalid data with no ml content or reference to another smaller package
            raise ValueError(f"Invalid data with no ml content or reference {package_id}")

        self.ml_content[package_id] = ml
        return ml

    def _sum_quantity(self) -> float:
        """
        calculate the total quantatiy in ml
        :return:  total inventory in ml
        """
        total_ml = 0
        for count in self.counts:
            package_id = count['package_id']
            if package_id not in self.ml_content: # in case of a package with no ml content given in the packages
                raise ValueError(f"Package {package_id} not found in packages data")
            if count['quantity'] < 0:  # in case of invalid data with negative quantity
                raise ValueError(f"Invalid data with negative quantity {count['quantity']}")
            quantity = count['quantity']
            total_ml += self.ml_content[package_id] * quantity
        return total_ml


def calculate_total_inventory(packages: List[Dict], counts: List[Dict]) -> float:
    """
    caller function to intiate and calculate the total quantaty through BevCalculator class
    :return: total
    """
    if not packages or not counts:  # incase of empty data we deem it invalid
        raise ValueError("Packages and counts cannot be empty")

    calculator = BevCalculator(packages, counts)
    return calculator.calculate_total_quantity()


if __name__ == "__main__":
    with open('test_data.json', 'r') as file:
        inc_data = json.load(file)
    packages = inc_data.get('packages', [])
    counts = inc_data.get('counts', [])
    try:
        total_inventory = calculate_total_inventory(packages, counts)
    except ValueError as e:
        print("Error:", e)
        total_inventory = "error"

    print(f"Total inventory: {total_inventory} ml")
