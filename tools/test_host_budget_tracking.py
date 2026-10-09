"""Focused tests for the capped host-budget runner."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import host_budget_tracking


class _CompletedTrackingProcess:
    """Stand in for the timeout-wrapped Godot child and emit its scene receipt."""

    def __init__(self, result_path, measured_ticks):
        self.result_path = result_path
        self.measured_ticks = measured_ticks

    def wait(self, timeout):
        del timeout
        self.result_path.write_text(
            json.dumps({
                "ok": True,
                "timing_ms": {"sample_count": self.measured_ticks},
                "soft_target": {"report_only": True},
            }),
            encoding="utf-8",
        )
        return 0

    def kill(self):
        """Mirror the subprocess API; successful tests never need to kill the child."""


class HostBudgetTrackingTest(unittest.TestCase):
    def test_run_tracking_accepts_existing_empty_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "existing-empty"
            output.mkdir()
            process = _CompletedTrackingProcess(output / "scene-result.json", 3)
            with (
                mock.patch.object(host_budget_tracking.subprocess, "Popen", return_value=process),
                mock.patch.object(host_budget_tracking.time, "sleep"),
                mock.patch.object(
                    host_budget_tracking,
                    "godot_process_count",
                    side_effect=[0, 1, 0],
                ),
            ):
                result = host_budget_tracking.run_tracking(
                    "godot", "timeout", output, warmup_ticks=2, measured_ticks=3
                )

            self.assertTrue(result["ok"])
            self.assertEqual(result["timing_ms"]["sample_count"], 3)
            self.assertTrue((output / "result.json").is_file())

    def test_main_forwards_existing_empty_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = (Path(temporary) / "existing-empty").resolve()
            output.mkdir()
            result = {
                "timing_ms": {},
                "soft_target": {},
                "contention": {},
            }
            arguments = [
                "host_budget_tracking.py",
                "--godot",
                "godot",
                "--output",
                str(output),
                "--warmup-ticks",
                "2",
                "--measured-ticks",
                "3",
            ]
            with (
                mock.patch.object(sys, "argv", arguments),
                mock.patch.object(host_budget_tracking.shutil, "which", return_value="timeout"),
                mock.patch.object(host_budget_tracking, "pinned_engine_version"),
                mock.patch.object(
                    host_budget_tracking, "run_tracking", return_value=result
                ) as run_tracking,
                redirect_stdout(io.StringIO()),
            ):
                returncode = host_budget_tracking.main()

            self.assertEqual(returncode, 0)
            run_tracking.assert_called_once_with("godot", "timeout", output, 2, 3)


if __name__ == "__main__":
    unittest.main()
