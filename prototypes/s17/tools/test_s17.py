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
            samples["total_production_schedule"] = [3000, 3500]
            samples["traffic"] = [1400, 1600]
            samples["pedestrians"] = [900, 1100]
            receipts.append(
                {
                    "timing_usec_samples": samples,
                    "empty_timer_usec_samples": [0, 1],
                }
            )
        result = RUNNER.aggregate(receipts)
        self.assertEqual(result["timing_ms"]["total"]["count"], 6)
        self.assertEqual(result["timing_ms"]["total"]["p95"], 8.0)
        self.assertEqual(result["empty_timer_baseline_ms"]["count"], 6)
        self.assertFalse(result["budget"]["conservative_total_p95_pass"])
        self.assertTrue(result["budget"]["production_schedule_total_p95_pass"])
        self.assertFalse(result["budget"]["traffic_audit_share_pass"])
        self.assertFalse(result["budget"]["pedestrian_share_pass"])

    def test_godot_commands_have_an_external_deadline(self):
        """Keep every direct Godot invocation behind the lane's timeout wrapper."""
        command = RUNNER.godot_command("godot", 30, ["--version"])
        self.assertEqual(Path(command[0]).stem.lower(), "timeout")
        self.assertEqual(command[1:], ["30", "godot", "--version"])

    def test_s10_tick_domain_rejects_absolute_measured_ticks(self):
        """Keep warmup from shifting S10 beyond its intended ten-minute horizon."""
        domain = {
            "car_contact_active_through_tick": 35_699,
            "continuous": True,
            "first_measured_tick": 0,
            "last_measured_tick": 35_999,
            "terminal_suppression_ticks": 300,
            "warmup_final_tick": -1,
        }
        receipt = {"pedestrians": {"tick_domain": domain}}
        self.assertTrue(RUNNER.valid_pedestrian_tick_domain(receipt))
        domain["first_measured_tick"] = 3_600
        domain["last_measured_tick"] = 39_599
        self.assertFalse(RUNNER.valid_pedestrian_tick_domain(receipt))


if __name__ == "__main__":
    unittest.main()
