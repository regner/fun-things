"""Focused tests for the bounded Brackett capacity runner."""

from pathlib import Path
import tempfile
import unittest

from world.run_brackett_baseline import godot_command, percentile


class BrackettBaselineRunnerTest(unittest.TestCase):
    def test_nearest_rank_percentile_retains_observed_tail(self):
        self.assertEqual(percentile([1.0, 2.0, 3.0, 40.0], 95), 40.0)
        self.assertEqual(percentile([], 95), 0.0)

    def test_godot_command_applies_cap_before_test_script(self):
        with tempfile.TemporaryDirectory() as temporary:
            command = godot_command("godot", Path(temporary))

        self.assertIn("--max-fps", command)
        self.assertEqual(command[command.index("--max-fps") + 1], "60")
        self.assertEqual(command[-1], "res://tests/performance/world/brackett_capacity.gd")


if __name__ == "__main__":
    unittest.main()
