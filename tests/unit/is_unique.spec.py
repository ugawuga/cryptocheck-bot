import unittest
from utils.is_unique import is_unique


class MyTestCase(unittest.TestCase):
    def test_unique(self):
        self.assertEqual(is_unique([1, 2, 3, 4]), True)

    def test_non_unique(self):
        self.assertEqual(is_unique([1, 1, 1, 1]), False)


if __name__ == '__main__':
    unittest.main()
