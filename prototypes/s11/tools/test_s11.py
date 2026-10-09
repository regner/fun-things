"""Focused offline checks for S11 wire-window accounting."""

import unittest

from run_s11 import (
    delivered_profile,
    delivery_delay_limit_ms,
    unexplained_delivery_excursions,
    worst_window_bytes,
)


class S11AccountingTests(unittest.TestCase):
    """Fence worst-window direction filtering and boundary inclusion."""

    def test_worst_window_uses_direction_and_includes_exact_boundary(self):
        events = [
            {"event": "ingress", "monotonic": 1.0, "direction": "down", "wire_bytes": 100},
            {"event": "ingress", "monotonic": 11.0, "direction": "down", "wire_bytes": 200},
            {"event": "ingress", "monotonic": 11.1, "direction": "down", "wire_bytes": 400},
            {"event": "ingress", "monotonic": 11.1, "direction": "up", "wire_bytes": 999},
            {"event": "drop", "monotonic": 11.1, "direction": "down"},
        ]

        self.assertEqual(worst_window_bytes(events, "down"), 600)
        self.assertEqual(worst_window_bytes(events, "up"), 999)

    def test_empty_window_is_zero(self):
        self.assertEqual(worst_window_bytes([], "down"), 0)

    def test_delivered_profile_separates_random_and_interruption_loss(self):
        events = [
            {"event": "ingress", "monotonic": 1.0, "direction": "down", "wire_bytes": 100},
            {"event": "ingress", "monotonic": 1.1, "direction": "down", "wire_bytes": 100},
            {"event": "ingress", "monotonic": 1.2, "direction": "up", "wire_bytes": 40},
            {"event": "drop", "monotonic": 1.0, "direction": "down", "reason": "random"},
            {"event": "drop", "monotonic": 1.1, "direction": "down",
             "reason": "blackout_pending"},
            {"event": "delivery", "monotonic": 1.3, "direction": "up",
             "actual_delay_ms": 80.0},
            {"event": "blackout_begin", "monotonic": 4.0},
            {"event": "blackout_end", "monotonic": 5.01},
        ]

        summary = delivered_profile(events)

        self.assertEqual(summary["directions"]["down"]["random_drop_datagrams"], 1)
        self.assertEqual(summary["directions"]["down"]["blackout_drop_datagrams"], 1)
        self.assertEqual(summary["directions"]["down"]["random_drop_percent"], 50.0)
        self.assertEqual(summary["directions"]["up"]["actual_delay_ms"]["p95"], 80.0)
        self.assertEqual(
            summary["directions"]["up"]["actual_delay_variation_ms"]["p95_absolute_deviation"],
            0.0,
        )
        self.assertAlmostEqual(summary["interruption"]["duration_ms"], 1010.0)

    def test_delivery_delay_guard_rejects_only_values_above_profile_bound(self):
        limit_ms = delivery_delay_limit_ms("normal")
        events = [
            {"event": "delivery", "actual_delay_ms": limit_ms},
            {"event": "delivery", "actual_delay_ms": limit_ms + 0.01},
            {"event": "ingress", "actual_delay_ms": limit_ms + 1000.0},
        ]

        excursions = unexplained_delivery_excursions(events, "normal")

        self.assertEqual(limit_ms, 355)
        self.assertEqual(excursions, [events[1]])
        self.assertEqual(delivery_delay_limit_ms("adverse"), 425)


if __name__ == "__main__":
    unittest.main()
