import unittest
from unittest.mock import patch

from jbussdieker.config import Config


class TestConfig(unittest.TestCase):
    @patch("jbussdieker.config.CONFIG_PATH", "/path/to/missing")
    def test_with_no_existing_config(self):
        config = Config.load()
        self.assertIsInstance(config, Config)


if __name__ == "__main__":
    unittest.main()
