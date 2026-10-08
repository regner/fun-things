"""Offline checks for the S02 Windows observation parser and retry boundary."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent / "s02"))
import observe_windows as observation  # noqa: E402


class WindowsObservationTest(unittest.TestCase):
    def test_prefixed_rows_ignore_other_output_and_keep_malformed_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "stdout.log"
            path.write_text(
                "Godot Engine\n"
                f"S02_DRAW {json.dumps({'event': 'frame', 'callback': 1})}\n"
                "S02_DRAW {broken}\n",
                newline="\n",
            )
            self.assertEqual(
                observation.prefixed_rows(path, "S02_DRAW "),
                [
                    {"event": "frame", "callback": 1},
                    {"event": "unparsed", "line": "S02_DRAW {broken}"},
                ],
            )

    def test_preflight_owner_before_restored_child_does_not_count_as_steal(self):
        attempt = {
            "stage_markers": [
                {"stage": "restore", "process_ms": 6000},
                {"stage": "check", "process_ms": 7000},
            ],
            "process": {
                "pid": 20,
                "foreground_before": {"pid": 10},
                "foreground_timeline": [
                    {"offset_seconds": 6.1, "pid": 10},
                    {"offset_seconds": 6.2, "pid": 10},
                    {"offset_seconds": 6.3, "pid": 10},
                    {"offset_seconds": 6.4, "pid": 20},
                    {"offset_seconds": 6.5, "pid": 20},
                ],
            },
        }
        self.assertFalse(observation.foreign_focus_stolen(attempt))

    def test_preflight_owner_steal_after_restored_child_authorizes_retry(self):
        attempt = {
            "stage_markers": [
                {"stage": "restore", "process_ms": 6000},
                {"stage": "check", "process_ms": 7000},
            ],
            "process": {
                "pid": 20,
                "foreground_before": {"pid": 10},
                "foreground_timeline": [
                    {"offset_seconds": 6.1, "pid": 10},
                    {"offset_seconds": 6.2, "pid": 20},
                    {"offset_seconds": 6.3, "pid": 10},
                    {"offset_seconds": 6.4, "pid": 10},
                    {"offset_seconds": 6.5, "pid": 10},
                ],
            },
        }
        self.assertTrue(observation.foreign_focus_stolen(attempt))

    def test_initial_focus_requires_sustained_child_ownership_before_stage(self):
        attempt = {
            "stage_markers": [{"stage": "press", "process_ms": 4500}],
            "process": {
                "pid": 20,
                "foreground_timeline": [
                    {"offset_seconds": 4.1, "pid": 20},
                    {"offset_seconds": 4.2, "pid": 20},
                    {"offset_seconds": 4.3, "pid": 20},
                    {"offset_seconds": 4.4, "pid": 20},
                ],
            },
        }
        self.assertTrue(observation.sustained_native_focus(attempt, "press"))
        attempt["process"]["foreground_timeline"][1]["pid"] = 10
        self.assertFalse(observation.sustained_native_focus(attempt, "press"))


if __name__ == "__main__":
    unittest.main()
