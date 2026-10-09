"""Offline checks for S10 result aggregation; no engine launch."""

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("s10_run", ROOT / "tools/s10/run.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class S10RunnerChecks(unittest.TestCase):
    """Protect repetition aggregation and correctness counters."""

    def test_aggregate_keeps_median_and_worst_repetitions_distinct(self):
        """Do not mislabel a percentile of three already summarized runs."""
        rows = []
        for seed, median, p95, p99 in (
            (1, 0.1, 0.2, 0.3), (2, 0.2, 0.4, 0.5), (3, 0.3, 0.9, 1.1)
        ):
            rows.append(
                {
                    "seed": seed,
                    "scenario": "normal",
                    "motion": "graph_kinematic",
                    "ai_movement_ms": {
                        "median": median,
                        "p95": p95,
                        "p99": p99,
                        "max": p99 + 1.0,
                    },
                    "metrics": {
                        "flee_latency_ms": {"max": 50.0},
                        "stuck_entities": seed,
                        "max_overlap_pairs": seed + 1,
                        "off_sidewalk_agent_ticks": 0,
                        "road_outside_crossing_agent_ticks": 0,
                    },
                }
            )
        summary = RUNNER.aggregate(rows)["normal/graph_kinematic"]
        self.assertEqual(summary["repetitions"], 3)
        self.assertEqual(summary["median_of_tick_p95_ms"], 0.4)
        self.assertEqual(summary["worst_tick_p95_ms"], 0.9)
        self.assertEqual(summary["max_stuck_entities"], 3)


if __name__ == "__main__":
    unittest.main()
