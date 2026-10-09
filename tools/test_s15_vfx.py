"""Offline checks for the S15 graphical VFX runner; no engine launch."""
import importlib.util
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("s15_vfx_run", ROOT / "tools/s15/run.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class S15VfxRunnerChecks(unittest.TestCase):
    """Protect telemetry math and revision binding for the bounded runner."""

    def test_nearest_rank_percentiles(self):
        """Use nearest-rank p50/p95/p99 values consistently with graphical evidence."""
        values = list(range(1, 101))
        self.assertEqual(RUNNER.percentile(values, 0.5), 50)
        self.assertEqual(RUNNER.percentile(values, 0.95), 95)
        self.assertEqual(RUNNER.percentile(values, 0.99), 99)
        self.assertIsNone(RUNNER.percentile([], 0.95))

    def test_sample_summary_uses_declared_columns(self):
        """Summarize frame interval and measured renderer values by their field positions."""
        first = [0.0, 16.0, 1.0, 2.0, 3.0, 0.1, 60.0, 100.0, 50.0, 1000.0]
        second = [0.016, 20.0, 1.5, 2.5, 3.5, 0.2, 61.0, 110.0, 51.0, 1100.0]
        summary = RUNNER.summarize_samples({"samples": [first, second]})
        self.assertEqual(summary["frames"], 2)
        self.assertEqual(summary["frame_interval_ms"]["p95"], 20.0)
        self.assertEqual(summary["render_gpu_ms"]["max"], 2.5)
        self.assertEqual(summary["draw_calls"]["p50"], 60.0)

    def test_dirty_query_covers_every_copied_source(self):
        """Bind dependency fixtures, model imports, settings, S15 source, and runner to HEAD."""
        with mock.patch.object(
            RUNNER.subprocess, "check_output", return_value=" M tests/fixtures/s15/stress.gd\n"
        ) as check:
            self.assertEqual(RUNNER.dirty_inputs(), "M tests/fixtures/s15/stress.gd")
        check.assert_called_once_with(
            ["git", "status", "--porcelain", "--", *RUNNER.STAGED_INPUTS],
            cwd=RUNNER.ROOT,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
