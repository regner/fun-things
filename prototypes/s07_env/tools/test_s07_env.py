"""Offline checks for the S07 environment measurement runner; no engine launch."""
import importlib.util
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("s07_env_run", ROOT / "tools/s07_env/run.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class EnvironmentRunnerChecks(unittest.TestCase):
    """Protect clean-input binding and the predeclared growth stop rules."""

    def test_dirty_check_includes_project_and_runner_directory(self):
        """Require project settings and both S07 environment tools in the Git query."""
        with mock.patch.object(
            RUNNER.subprocess, "check_output", return_value=" M tools/s07_env/run.py\n"
        ) as check:
            self.assertEqual(RUNNER.dirty_inputs(), "M tools/s07_env/run.py")
        check.assert_called_once_with(
            ["git", "status", "--porcelain", "--", *RUNNER.CLEAN_INPUTS],
            cwd=RUNNER.ROOT,
            text=True,
        )
        self.assertIn("project.godot", RUNNER.CLEAN_INPUTS)
        self.assertIn("tools/s07_env", RUNNER.CLEAN_INPUTS)

    def test_stop_reasons_cover_frame_load_and_memory_limits(self):
        """Stop growth when any predeclared numerical limit is exceeded."""
        record = {
            "ok": True,
            "result": {"cold_first_load_ms": 30_001, "warm_reload_ms": 100},
            "resident_bytes": {"max": RUNNER.RAM_STOP_BYTES + 1},
            "frames": {"frame_interval_ms": {"p99": 20.01}},
        }
        self.assertEqual(
            RUNNER.stop_reasons(record),
            [
                "cold first load exceeded 30 s",
                "working set exceeded 2 GiB",
                "measured frame interval p99 exceeded 20 ms",
            ],
        )

    def test_limits_are_strictly_greater_than_thresholds(self):
        """Treat values exactly at owner limits as inside the measured envelope."""
        record = {
            "ok": True,
            "result": {"cold_first_load_ms": 30_000, "warm_reload_ms": 30_000},
            "resident_bytes": {"max": RUNNER.RAM_STOP_BYTES},
            "frames": {"frame_interval_ms": {"p99": 20.0}},
        }
        self.assertEqual(RUNNER.stop_reasons(record), [])


if __name__ == "__main__":
    unittest.main()
