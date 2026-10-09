"""Focused offline checks for S11 wire-window accounting."""

import unittest

from run_s11 import worst_window_bytes


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


if __name__ == "__main__":
    unittest.main()
