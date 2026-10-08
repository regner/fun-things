"""Offline S07 comparator receipt evaluator counterexamples; no engine launch."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "s07_comparator_run", ROOT / "tools/s07_comparator/run.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class ComparatorReceiptChecks(unittest.TestCase):
    """Protect literal lifecycle and draw criteria against corrupted receipts."""

    def setUp(self):
        """Build a compact valid two-trial receipt without copying gameplay formulas."""
        self.result = {"ok": True, "trials_requested": 2, "trials_completed": 2}
        self.rows = []
        for trial in [1, 2]:
            row = {field: True for field in RUNNER.REQUIRED_TRUE}
            row.update({"trial": trial, "session": f"{trial:032x}", "admission": "OK",
                        "damage": 12, "visits": 144, "target_peak": 4, "completed": 12,
                        "effects_accepted": 8, "effects_dropped": 4,
                        "loading_seconds": .01, "first_draw_seconds": .02,
                        "chain_seconds": .2, "reset_seconds": .01, "drawn": True,
                        "draw": {"visible": 8, "visible_in_tree": 8, "dropped": 4,
                                 "can_draw": True, "png": {"save_error": 0}}})
            self.rows.append(row)

    def test_valid_and_lifecycle_counterexamples(self):
        """Accept the baseline and reject stale-session, visit and cleanup corruption."""
        self.assertEqual(RUNNER.evaluate(self.result, self.rows, False), [])
        changes = [lambda rows: rows[1].update(session=rows[0]["session"]),
                   lambda rows: rows[0].update(visits=143),
                   lambda rows: rows[0].update(stale_event_rejected=False),
                   lambda rows: rows[0].update(no_live_job=False),
                   lambda rows: rows.pop()]
        for change in changes:
            rows = copy.deepcopy(self.rows)
            change(rows)
            self.assertTrue(RUNNER.evaluate(self.result, rows, False))

    def test_graphical_counterexamples(self):
        """Require a genuine drawable callback, eight visible slots and a saved PNG."""
        self.assertEqual(RUNNER.evaluate(self.result, self.rows, True), [])
        changes = [lambda rows: rows[0].update(drawn=False),
                   lambda rows: rows[0]["draw"].update(visible_in_tree=7),
                   lambda rows: rows[0]["draw"].update(can_draw=False),
                   lambda rows: rows[0]["draw"]["png"].update(save_error=1)]
        for change in changes:
            rows = copy.deepcopy(self.rows)
            change(rows)
            self.assertTrue(RUNNER.evaluate(self.result, rows, True))


if __name__ == "__main__":
    unittest.main()
