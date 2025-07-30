import os
import unittest
import tempfile
import json
from unittest.mock import patch

from jbussdieker.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.tmpdir.name, "config.json")
        os.environ["JBUSSDIEKER_CONFIG"] = self.config_path

    def tearDown(self):
        self.tmpdir.cleanup()
        os.environ.pop("JBUSSDIEKER_CONFIG", None)

    def test_with_no_existing_config(self):
        config = Config.load()
        self.assertIsInstance(config, Config)

    def test_save_creates_file(self):
        config = Config(log_level="TRACE")
        config.save()
        self.assertTrue(os.path.exists(self.config_path))
        with open(self.config_path) as f:
            data = json.load(f)
        self.assertEqual(data["log_level"], "TRACE")

    def test_load_with_existing_file(self):
        data = {"log_level": "INFO", "custom_settings": {"customkey": "baz"}}
        with open(self.config_path, "w") as f:
            json.dump(data, f)
        config = Config.load()
        self.assertEqual(config.log_level, "INFO")
        self.assertIn("customkey", config.custom_settings)
        self.assertEqual(config.custom_settings["customkey"], "baz")


if __name__ == "__main__":
    unittest.main()
