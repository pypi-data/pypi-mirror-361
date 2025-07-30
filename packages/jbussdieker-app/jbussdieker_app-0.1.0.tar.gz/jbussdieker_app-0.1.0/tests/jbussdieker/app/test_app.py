import unittest

import jbussdieker.app


class TestService(unittest.TestCase):
    def test_version(self):
        self.assertIn("__version__", dir(jbussdieker.app))


if __name__ == "__main__":
    unittest.main()
