"""Independent counterexamples for S04-T transition telemetry acceptance."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from s04_t.run import analyze


class ProxyStub:
    """Supplies the analyzer's bounded proxy evidence surface."""

    blackout_done = True
    events = [{"event": "delivery", "actual_delay_ms": 75.0}]


class TransitionMetrics(unittest.TestCase):
    """Reject telemetry that claims a transition without clean replay domains."""

    def _analyze(self, dirty_stage: str = "", continuous: bool = True) -> dict:
        """Build a complete cut with optional dirty history or rejected-entry sequence reset."""
        expected = [
            ("race_entry", False, "SEAT_OCCUPIED", "foot"),
            ("parked_entry", True, "", "car"),
            ("moving_exit", False, "EXIT_MOVING", "car"),
            ("forced_blocked_exit", False, "EXIT_BLOCKED", "car"),
            ("successful_exit", True, "", "foot"),
            ("traffic_entry", True, "", "car"),
        ]
        client = []
        for index, (stage, accepted, failure, owner) in enumerate(expected):
            client.append({
                "event": "transition", "stage": stage, "accepted": accepted,
                "failure": failure, "correction_m": 0.2, "visual_jump_m": 0.1,
                "time_to_control_ms": 16, "round_trip_ms": 150,
                "foot_history": 1 if stage == dirty_stage else 0,
                "car_history": 0, "camera_owner": owner, "hud_owner": owner,
                "wall_ms": 1500.0 + index * 100.0,
            })
        client.append({"event": "result", "ok": True})
        host = [{"event": "seat_race", "winner": 1, "loser": 2}]
        for revision in range(1, 5):
            for index in range(2):
                host.append({
                    "event": "authority_input", "expired": False,
                    "revision": revision, "sequence": index + 1,
                    "sample": [float(revision), float(index), 0.0],
                    "wall_ms": (
                        1600.0 if continuous and revision == 1 and index == 1 else 1000.0
                    ),
                })
        host.append({
            "event": "result", "ok": True, "traffic_stolen": True,
            "traffic_ai_active": False, "disconnect_coast_m": 0.5,
            "final_speed_mps": 0.0, "input_queue_peak": 8,
            "action_queue_peak": 16, "action_processed_peak": 4,
            "action_cache_size": 6, "hydration_count": 1, "control_reset_count": 3,
        })
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for role, rows in [("host", host), ("client", client)]:
                (root / role / "captures").mkdir(parents=True)
                (root / role / "stdout.log").write_text("".join(
                    "S04T " + json.dumps(row) + "\n" for row in rows))
            (root / "client/captures/accepted.png").write_bytes(b"receipt")
            return analyze(root, "normal", ProxyStub())

    def test_complete_transition_cut_passes(self):
        """Accept all six verdicts with clean history and matched presentation owners."""
        self.assertTrue(self._analyze()["ok"])

    def test_dirty_source_history_fails(self):
        """Fail an otherwise valid cut when entry retains foot replay history."""
        result = self._analyze("parked_entry")
        self.assertFalse(result["ok"])
        self.assertFalse(result["criteria"]["history_clean"])

    def test_rejected_entry_sequence_reset_fails(self):
        """Reject telemetry with no newer revision-one input after rejected speculation."""
        result = self._analyze(continuous=False)
        self.assertFalse(result["ok"])
        self.assertFalse(result["criteria"]["rejected_entry_sequence_continuity"])


if __name__ == "__main__":
    unittest.main()
