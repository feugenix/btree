import unittest
from typing import List, Iterable

from btree import BTree, TreeKeyValue, BTreeValidator


class TestCaseBTreeRefactoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # just random numbers from the head
        cls.test_values = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1050, 100, 1001, 1234, 222, 555, 666, 333, 777, 4321,
                           9999, 9090, 555, 11, 15, 109, 205, 512, 999, 888, 321, 432, 567, 654, 85, 66, 33, 876, 312,
                           564, 789, 811, 801, 800, 799, 991, 11)

    @staticmethod
    def _check_if_keys_not_in_tree(keys_to_find: Iterable[int], tree: BTree) -> List[int]:
        lost_keys = []
        for key in keys_to_find:
            found = tree.search_key(key)
            if found is None:
                lost_keys.append(key)

        return lost_keys

    @unittest.skip
    def test_search_many(self) -> None:
        tree = BTree(3)

        for val in self.test_values:
            tree.insert(TreeKeyValue(val, val))

        BTreeValidator.validate(tree)

        lost_keys = self._check_if_keys_not_in_tree(self.test_values, tree)
        self.assertEqual(lost_keys, [])

    def test_delete_many(self) -> None:
        tree = BTree(3)

        for _, val in enumerate(self.test_values):
            tree.insert(TreeKeyValue(val, val))

        BTreeValidator.validate(tree)

        keys_to_delete = (8,)

        for key in keys_to_delete:
            tree.delete(key)

        BTreeValidator.validate(tree)

        lost_keys = self._check_if_keys_not_in_tree(keys_to_delete, tree)
        self.assertEqual(lost_keys, list(keys_to_delete))


if __name__ == '__main__':
    unittest.main()
