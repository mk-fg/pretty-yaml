import io
import os
import sys
import tempfile
import unittest

try:
    import pyaml.cli
except ImportError:
    sys.path.insert(1, os.path.join(__file__, *[".."] * 3))
    import pyaml.cli


class CliInputErrorTests(unittest.TestCase):
    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with self.assertRaises(SystemExit) as cm:
            pyaml.cli.main(
                argv=argv, stdin=io.StringIO(""), stdout=out, stderr=err
            )
        return cm.exception.code, out.getvalue(), err.getvalue()

    def test_missing_file_clean_error(self):
        code, _out, err = self.run_cli(["does-not-exist.yaml"])
        self.assertEqual(code, 2)
        self.assertIn("does-not-exist.yaml", err)

    def test_directory_clean_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            code, _out, err = self.run_cli([tmpdir])
        self.assertEqual(code, 2)
        self.assertIn("cannot open input file", err)
        self.assertIn(os.path.basename(tmpdir), err)
