import unittest

import jbussdieker


class TestJbussdieker(unittest.TestCase):
    def test_version(self):
        self.assertIn("__version__", dir(jbussdieker))


if __name__ == "__main__":
    unittest.main()
