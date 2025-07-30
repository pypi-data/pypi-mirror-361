import unittest

from jbussdieker import foo


class TestFoo(unittest.TestCase):
    def test_bar(self):
        self.assertEqual(foo.bar, 42)


if __name__ == "__main__":
    unittest.main()
