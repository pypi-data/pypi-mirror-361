import unittest
from io import StringIO
from contextlib import redirect_stdout

from jbussdieker.cli import main


class TestCLI(unittest.TestCase):
    def test_version_output(self):
        buf = StringIO()
        with redirect_stdout(buf):
            main(["--version"])
        output = buf.getvalue()
        self.assertIn("jbussdieker v", output)


if __name__ == "__main__":
    unittest.main()
