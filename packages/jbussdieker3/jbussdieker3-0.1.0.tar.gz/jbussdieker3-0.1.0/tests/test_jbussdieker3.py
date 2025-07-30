import unittest

from jbussdieker import bar


class TestBar(unittest.TestCase):
    def test_foo(self):
        self.assertEqual(bar.foo, 24)


if __name__ == "__main__":
    unittest.main()
