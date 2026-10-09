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
            ["git", "status", "--porcelain", "--", "tests", "art", "project.godot",
             "tools/s07_graphical"],
            cwd=RUNNER.ROOT,
            text=True,
        )

    def test_runner_exposes_only_capped_mode(self):
        """Keep the withdrawn uncapped mode out of defaults and command construction."""
        source = (ROOT / "tools/s07_graphical/run.py").read_text()
        fixture = (ROOT / "tests/fixtures/s07_graphical/run.gd").read_text()
        self.assertIn('choices=["capped60"]', source)
        self.assertNotIn('choices=["uncapped", "capped60"]', source)
        self.assertIn("*capped_window_arguments()", source)
        self.assertIn("Engine.max_fps = CAPPED_FPS", fixture)
        self.assertIn('push_error("S07 graphical requires capped60 mode")', fixture)
        self.assertNotIn("Engine.max_fps = 0", fixture)


if __name__ == "__main__":
    unittest.main()
