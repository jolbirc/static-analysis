import importlib.util
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

spec = importlib.util.spec_from_file_location(
    "file_analysis",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "file-analysis.py"),
)
fa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fa)


def capture(fn, *args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        result = fn(*args)
    return buf.getvalue(), result


class TestCheckExists(unittest.TestCase):
    def test_existing_file_passes(self):
        with tempfile.NamedTemporaryFile() as f:
            out, _ = capture(fa.check_exists, f.name)
        self.assertIn("OK", out)
        self.assertNotIn("!FOUND", out)

    def test_missing_file_exits(self):
        with self.assertRaises(SystemExit):
            capture(fa.check_exists, "/tmp/__nonexistent_test_xyz__.txt")


class TestCheckLs(unittest.TestCase):
    def test_normal_file_passes(self):
        with tempfile.NamedTemporaryFile(mode="wb") as f:
            f.write(b"hello world\n")
            f.flush()
            out, size = capture(fa.check_ls, f.name)
        self.assertNotIn("!FOUND", out)
        self.assertIn("OK", out)
        self.assertEqual(size, 12)

    def test_empty_file_flagged_as_decoy(self):
        with tempfile.NamedTemporaryFile() as f:
            out, size = capture(fa.check_ls, f.name)
        self.assertIn("!FOUND", out)
        self.assertIn("decoy", out)
        self.assertEqual(size, 0)

    def test_large_file_flagged(self):
        with tempfile.NamedTemporaryFile(mode="wb") as f:
            f.write(b"A" * 10_001)
            f.flush()
            out, size = capture(fa.check_ls, f.name)
        self.assertIn("!FOUND", out)
        self.assertIn("unusually large", out)
        self.assertEqual(size, 10_001)

    def test_boundary_size_not_flagged(self):
        with tempfile.NamedTemporaryFile(mode="wb") as f:
            f.write(b"B" * 10_000)
            f.flush()
            out, size = capture(fa.check_ls, f.name)
        self.assertNotIn("!FOUND", out)
        self.assertEqual(size, 10_000)


class TestCheckWc(unittest.TestCase):
    def test_matching_sizes_passes(self):
        with tempfile.NamedTemporaryFile(mode="wb") as f:
            f.write(b"hello\n")
            f.flush()
            size = os.path.getsize(f.name)
            out, _ = capture(fa.check_wc, f.name, size)
        self.assertIn("OK", out)
        self.assertNotIn("!FOUND", out)

    def test_mismatched_size_flagged(self):
        with tempfile.NamedTemporaryFile(mode="wb") as f:
            f.write(b"hello\n")
            f.flush()
            size = os.path.getsize(f.name)
            out, _ = capture(fa.check_wc, f.name, size + 99)
        self.assertIn("!FOUND", out)
        self.assertIn("mismatch", out)


class TestCheckCatA(unittest.TestCase):
    def test_clean_text_passes(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as f:
            f.write("hello world\nfoo bar\nbaz\n")
            f.flush()
            out, _ = capture(fa.check_cat_a, f.name)
        self.assertIn("OK", out)
        self.assertNotIn("!FOUND", out)

    def test_trailing_spaces_flagged(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as f:
            f.write("hello   \nworld\n")
            f.flush()
            out, _ = capture(fa.check_cat_a, f.name)
        self.assertIn("!FOUND", out)

    def test_null_byte_flagged(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt") as f:
            f.write(b"hello\x00world\n")
            f.flush()
            out, _ = capture(fa.check_cat_a, f.name)
        self.assertIn("!FOUND", out)

    def test_backspace_char_flagged(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt") as f:
            f.write(b"hello\x08world\n")
            f.flush()
            out, _ = capture(fa.check_cat_a, f.name)
        self.assertIn("!FOUND", out)

    def test_escape_char_flagged(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt") as f:
            f.write(b"hello\x1bworld\n")
            f.flush()
            out, _ = capture(fa.check_cat_a, f.name)
        self.assertIn("!FOUND", out)

    def test_multiple_suspicious_lines_each_reported(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt") as f:
            f.write(b"clean line\nhidden  \nnull\x00byte\n")
            f.flush()
            out, _ = capture(fa.check_cat_a, f.name)
        self.assertEqual(out.count("!FOUND"), 2)


if __name__ == "__main__":
    unittest.main()
