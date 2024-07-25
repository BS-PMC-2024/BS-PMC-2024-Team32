import unittest
from calc import calc

class TestCalc(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(calc(2, 3), 5)

if __name__ == '__main__':
    unittest.main()
