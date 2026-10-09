"""Independent aggregation checks for the S17 integrated host-tick runner."""

import importlib.util
from pathlib import Path
import unittest


RUNNER_PATH = Path(__file__).parent / "s17" / "run.py"
SPEC = importlib.util.spec_from_file_location("s17_run", RUNNER_PATH)
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class S17AggregationTests(unittest.TestCase):
    """Protect complete-sample nearest-rank and budget verdict calculations."""

    def test_distribution_uses_nearest_rank_tail(self):
        """Keep p95/p99 sensitive to retained high samples instead of interpolation."""
        samples = list(range(1, 101))
        result = RUNNER.distribution(samples)
        self.assertEqual(result["median"], 0.050)
        self.assertEqual(result["p95"], 0.095)
        self.assertEqual(result["p99"], 0.099)
        self.assertEqual(result["worst"], 0.100)

    def test_aggregate_pools_all_equal_duration_seed_samples(self):
        """Evaluate the host budget over all seed ticks rather than seed summaries."""
        receipts = []
        for total in ((3000, 4000), (5000, 6000), (7000, 8000)):
            samples = {
                subsystem: [1000, 1000]
                for subsystem in RUNNER.SUBSYSTEMS
            }
            samples["total"] = list(total)
            samples["traffic"] = [1400, 1600]
            samples["pedestrians"] = [900, 1100]
            receipts.append({"timing_usec_samples": samples})
        result = RUNNER.aggregate(receipts)
        self.assertEqual(result["timing_ms"]["total"]["count"], 6)
        self.assertEqual(result["timing_ms"]["total"]["p95"], 8.0)
        self.assertFalse(result["budget"]["total_p95_pass"])
        self.assertFalse(result["budget"]["traffic_audit_share_pass"])
        self.assertFalse(result["budget"]["pedestrian_share_pass"])


if __name__ == "__main__":
    unittest.main()
