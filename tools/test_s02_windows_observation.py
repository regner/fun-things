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

    def test_foreign_focus_steal_requires_three_consecutive_new_owner_samples(self):
        attempt = {
            "process": {
                "pid": 20,
                "foreground_before": {"pid": 10},
                "foreground_timeline": [
                    {"offset_seconds": 3.3, "pid": 30},
                    {"offset_seconds": 3.4, "pid": 30},
                    {"offset_seconds": 3.5, "pid": 30},
                ],
            }
        }
        self.assertTrue(observation.foreign_focus_stolen(attempt))
        attempt["process"]["foreground_timeline"][1]["pid"] = 20
        self.assertFalse(observation.foreign_focus_stolen(attempt))

    def test_preexisting_foreground_owner_does_not_authorize_retry(self):
        attempt = {
            "process": {
                "pid": 20,
                "foreground_before": {"pid": 10},
                "foreground_timeline": [
                    {"offset_seconds": 3.3 + index / 10, "pid": 10}
                    for index in range(5)
                ],
            }
        }
        self.assertFalse(observation.foreign_focus_stolen(attempt))


if __name__ == "__main__":
    unittest.main()
