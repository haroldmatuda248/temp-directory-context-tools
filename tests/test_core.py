import os
import tempfile
import unittest

from temp_directory_context_tools import temp_cwd


class TestTempCwd(unittest.TestCase):
    def setUp(self):
        self._cwd_before = os.getcwd()

    def tearDown(self):
        os.chdir(self._cwd_before)

    def test_changes_cwd_inside_block(self):
        with temp_cwd() as tmp:
            self.assertEqual(os.path.realpath(os.getcwd()), os.path.realpath(tmp))

    def test_restores_cwd_after_block(self):
        original = os.getcwd()
        with temp_cwd():
            pass
        self.assertEqual(os.getcwd(), original)

    def test_yields_absolute_path_string(self):
        with temp_cwd() as tmp:
            self.assertIsInstance(tmp, str)
            self.assertTrue(os.path.isabs(tmp))
            self.assertTrue(os.path.isdir(tmp))

    def test_directory_removed_after_block(self):
        with temp_cwd() as tmp:
            self.assertTrue(os.path.isdir(tmp))
        self.assertFalse(os.path.exists(tmp))

    def test_restores_cwd_on_exception(self):
        original = os.getcwd()
        with self.assertRaises(RuntimeError):
            with temp_cwd() as tmp:
                raise RuntimeError("boom")
        self.assertEqual(os.getcwd(), original)
        self.assertFalse(os.path.exists(tmp))

    def test_directory_removed_on_exception(self):
        with self.assertRaises(ValueError):
            with temp_cwd() as tmp:
                with open(os.path.join(tmp, "leftover.txt"), "w") as f:
                    f.write("data")
                raise ValueError("oops")
        self.assertFalse(os.path.exists(tmp))

    def test_nested_contexts(self):
        with temp_cwd() as outer:
            outer_real = os.path.realpath(os.getcwd())
            self.assertEqual(outer_real, os.path.realpath(outer))
            with temp_cwd() as inner:
                inner_real = os.path.realpath(os.getcwd())
                self.assertEqual(inner_real, os.path.realpath(inner))
                self.assertNotEqual(outer_real, inner_real)
            self.assertEqual(os.path.realpath(os.getcwd()), outer_real)
        self.assertEqual(os.getcwd(), self._cwd_before)

    def test_files_written_are_visible_in_cwd(self):
        with temp_cwd() as tmp:
            with open("test_file.txt", "w") as f:
                f.write("hello")
            self.assertTrue(os.path.exists("test_file.txt"))
            self.assertTrue(os.path.exists(os.path.join(tmp, "test_file.txt")))
            with open("test_file.txt", "r") as f:
                self.assertEqual(f.read(), "hello")

    def test_prefix_applied(self):
        with temp_cwd(prefix="mytest_") as tmp:
            self.assertTrue(os.path.basename(tmp).startswith("mytest_"))

    def test_suffix_applied(self):
        with temp_cwd(suffix="_end") as tmp:
            self.assertTrue(os.path.basename(tmp).endswith("_end"))

    def test_explicit_parent_dir(self):
        parent = tempfile.mkdtemp()
        try:
            with temp_cwd(dir=parent) as tmp:
                self.assertEqual(
                    os.path.realpath(os.path.dirname(tmp)),
                    os.path.realpath(parent),
                )
        finally:
            import shutil
            shutil.rmtree(parent, ignore_errors=True)

    def test_isolation_between_contexts(self):
        with temp_cwd() as first:
            with open("first_file.txt", "w") as f:
                f.write("a")
        with temp_cwd() as second:
            self.assertFalse(os.path.exists("first_file.txt"))
            self.assertNotEqual(
                os.path.realpath(first), os.path.realpath(second)
            )


if __name__ == "__main__":
    unittest.main()
