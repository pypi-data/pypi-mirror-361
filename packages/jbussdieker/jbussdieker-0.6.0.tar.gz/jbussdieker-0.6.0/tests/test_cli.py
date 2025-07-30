import os
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stdout

from jbussdieker.cli import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.tmpdir.name, "config.json")
        os.environ["JBUSSDIEKER_CONFIG"] = self.config_path

    def tearDown(self):
        self.tmpdir.cleanup()
        os.environ.pop("JBUSSDIEKER_CONFIG", None)

    def test_version_output(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["version"])
        output = buf.getvalue()
        self.assertIn("jbussdieker v", output)

    def test_no_arguments(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main([])
        output = buf.getvalue()
        self.assertIn("usage: ", output)

    def test_config(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["config"])
        output = buf.getvalue()
        self.assertIn("Current config", output)

    def test_config_set_log_format(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["config", "--set", 'log_format="FOOLEVEL: %(message)s"'])
        output = buf.getvalue()
        self.assertIn("Set log_format", output)
        buf2 = StringIO()
        with redirect_stdout(buf2):
            main(["version"])
        output2 = buf2.getvalue()
        self.assertIn("FOOLEVEL:", output2)
        self.assertIn("jbussdieker v", output2)

    def test_config_set_log_level(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["config", "--set", 'log_format="%(levelname)s: %(message)s"'])
            main(["config", "--set", "log_level=DEBUG"])
        output = buf.getvalue()
        self.assertIn("Set log_level", output)
        self.assertIn("Set log_format", output)
        buf2 = StringIO()
        with redirect_stdout(buf2):
            main(["version"])
        output2 = buf2.getvalue()
        self.assertIn("DEBUG", output2)
        self.assertIn("jbussdieker v", output2)

    def test_config_set_debug(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["config", "--set", "debug=false"])
        output = buf.getvalue()
        self.assertIn("Set debug", output)

    def test_config_set_custom(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["config", "--set", "mycustomkey=42"])
        output = buf.getvalue()
        self.assertIn("Set custom setting", output)

    def test_config_set_invalid(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["config", "--set", "foo"])
        output = buf.getvalue()
        self.assertIn("Invalid format", output)

    def test_verbose_sets_debug_logging(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["--verbose", "version"])
        output = buf.getvalue()
        self.assertIn("Parsed args:", output)
        self.assertIn("jbussdieker v", output)


if __name__ == "__main__":
    unittest.main()
