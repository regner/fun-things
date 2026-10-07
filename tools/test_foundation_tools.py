"""Focused failure/ownership tests for the foundation tooling."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from run_s03 import stop_children
from script_checks import checked_command, owned_scripts


class FoundationToolsTest(unittest.TestCase):
    def test_unused_and_owned_addon_scripts_are_discovered(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = ["tests/unused.gd", "addons/owned/unused.gd",
                     "addons/godotsteam/vendor.gd", "addons/godot_mcp_toolkit/vendor.gd",
                     ".hidden/hidden.gd", "art/source/ignored.gd"]
            for relative in paths:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            (root / "art/source/.gdignore").touch()
            self.assertEqual([path.relative_to(root).as_posix() for path in owned_scripts(root)],
                             ["addons/owned/unused.gd", "tests/unused.gd"])

    def test_success_exit_with_script_error_fails_and_retains_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / "check.log"
            ok = checked_command([sys.executable, "-c",
                                  "print('SCRIPT ERROR: unused script failed')"],
                                 log, {})
            self.assertFalse(ok)
            self.assertIn("unused script failed", log.read_text())

    def test_cleanup_leaves_unrelated_process_alive(self):
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            stop_children([child])
            self.assertIsNotNone(child.poll())
            self.assertIsNone(unrelated.poll())
        finally:
            stop_children([child, unrelated])


if __name__ == "__main__":
    unittest.main()
