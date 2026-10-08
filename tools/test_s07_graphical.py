"""Offline checks for the S07 graphical runner; no engine launch."""
import importlib.util
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "s07_graphical_run", ROOT / "tools/s07_graphical/run.py"
)
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class GraphicalRunnerChecks(unittest.TestCase):
    """Protect revision binding for every copied input source."""

    def test_dirty_check_includes_project_settings(self):
        """Require project.godot beside fixture and art paths in the dirty query."""
        with mock.patch.object(
            RUNNER.subprocess, "check_output", return_value=" M project.godot\n"
        ) as check:
            self.assertEqual(RUNNER.dirty_inputs(), "M project.godot")
        check.assert_called_once_with(
            ["git", "status", "--porcelain", "--", "tests", "art", "project.godot"],
            cwd=RUNNER.ROOT,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
