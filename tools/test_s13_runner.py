"""Unit checks for S13 measurement summarization boundaries."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("s13_run", ROOT / "tools/s13/run.py")
S13_RUN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S13_RUN)


class S13RunnerTests(unittest.TestCase):
    """Keep percentile and mode-delta reporting independent of engine measurements."""

    def test_distribution_retains_tail_and_ignores_unavailable_values(self):
        """Unavailable renderer monitors must not break valid headless distributions."""
        self.assertEqual(
            S13_RUN.distribution([1.0, 2.0, 3.0, 100.0]),
            {"samples": 4, "median": 2.0, "p95": 100.0, "p99": 100.0, "worst": 100.0},
        )
        self.assertIsNone(S13_RUN.percentile([None, None], 0.95))

    def test_aggregate_reports_headless_process_median_delta(self):
        """The optimization claim compares measured full and throttled process medians."""
        cases = []
        for mode, samples in [("full", [3.0, 4.0, 5.0]), ("throttled", [1.0, 1.0, 2.0])]:
            values = {"process_ms": samples, "render_gpu_ms": []}
            cases.append({
                "group": "headless",
                "mode": mode,
                "ok": True,
                "system_load": {},
                "telemetry": {"samples": values},
                "distributions": {
                    field: S13_RUN.distribution(field_samples)
                    for field, field_samples in values.items()
                },
            })
        result = S13_RUN.aggregate(cases)
        self.assertEqual(result["headless"]["full"]["telemetry"]["process_ms"]["median"], 4.0)
        self.assertEqual(
            result["headless"]["throttled"]["telemetry"]["process_ms"]["median"], 1.0
        )
        self.assertEqual(result["headless_process_median_delta_ms"], 3.0)


if __name__ == "__main__":
    unittest.main()
