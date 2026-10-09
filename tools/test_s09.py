"""Focused aggregation checks for the S09 measurement runner."""
import unittest

from s09.run import aggregate_cases, distribution


class S09RunnerTest(unittest.TestCase):
    """Keep percentile and cross-seed aggregation independent of GDScript formulas."""

    def test_distribution_uses_nearest_rank(self):
        self.assertEqual(distribution([4.0, 1.0, 3.0, 2.0]), {
            "count": 4, "median": 2.0, "p95": 4.0, "p99": 4.0, "worst": 4.0,
        })

    def test_aggregate_uses_full_tick_samples(self):
        cases = []
        for population in (24, 32):
            for seed in (11, 29, 47):
                cases.append({
                    "population": population, "ai_tick_usec_samples": [100, 200],
                    "stuck_recovery_samples_seconds": [2.5], "ai_collisions": 0,
                    "deadlocks": 0, "stuck_events": 1,
                    "lane_error_m": {"p95": 0.4, "worst": 0.8},
                })
        result = aggregate_cases(cases)
        self.assertEqual(result["24"]["ai_tick_ms"]["count"], 6)
        self.assertEqual(result["24"]["ai_tick_ms"]["median"], 0.1)
        self.assertEqual(result["32"]["stuck_recovery_seconds"]["count"], 3)
        self.assertEqual(result["32"]["lane_error_worst_m_by_seed"], [0.8, 0.8, 0.8])


if __name__ == "__main__":
    unittest.main()
