import unittest
from io import StringIO
from contextlib import redirect_stdout

from jbussdieker.cli import main


class TestCLI(unittest.TestCase):
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

    def test_config_set_username(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["config", "--set", "username=bar"])
        output = buf.getvalue()
        self.assertIn("Set username", output)

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


if __name__ == "__main__":
    unittest.main()
