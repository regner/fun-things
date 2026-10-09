"""Regression checks for ownership-sensitive experiment evidence, without engine mutation."""

import json
from pathlib import Path
import tempfile
import unittest

from run_s03_r import analyze, latency_budget


class ResponseOwnershipTests(unittest.TestCase):
    def test_host_ack_cannot_count_as_client_response(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "host").mkdir()
            (directory / "client").mkdir()
            (directory / "host/stdout.log").write_text("")
            rows = [
                {"event": "input", "index": 1, "time_ms": 100, "sequence_floor": 10,
                 "move": [0, -1], "aim_yaw": 0, "position": [0, 0, 0], "yaw": 0},
                {"event": "apply", "time_ms": 110, "entity": 1, "pose": {
                    "entity": 1, "tick": 1, "sequence": 10},
                 "position": [1, 0, 0], "yaw": 0},
                {"event": "apply", "time_ms": 200, "entity": 2, "pose": {
                    "entity": 2, "tick": 1, "sequence": 10},
                 "position": [1, 0, 0], "yaw": 0},
            ]
            (directory / "client/stdout.log").write_text(
                "".join("S03R " + json.dumps(row) + "\n" for row in rows))
            measured = analyze(directory, [])
            self.assertEqual(measured["responses"][0]["physics_ms"], 100)
            self.assertIsNone(measured["responses"][0]["rendered_frame_ms"])


class ExpiryBoundaryTests(unittest.TestCase):
    def test_match_decision_age_owns_expiry_boundary(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "host").mkdir()
            (directory / "client").mkdir()
            rows = []
            for tick, held, decision_age, telemetry_age in [
                    (1, [1, 0], 249, 253), (2, [0, 0], 253, 257),
                    (3, [0, 0], 269, 273)]:
                rows.append({"event": "simulation", "time_ms": 1000 + telemetry_age,
                             "wall_ms": 2000 + telemetry_age, "local_tick": tick,
                             "held": held, "receipt_ms": 1000,
                             "decision_age_ms": decision_age,
                             "pose": {"entity": 2, "tick": tick, "sequence": 1,
                                      "position": [0, 0, 0], "velocity": [0, 0, 0],
                                      "yaw": 0}})
            (directory / "host/stdout.log").write_text(
                "".join("S03R " + json.dumps(row) + "\n" for row in rows))
            (directory / "client/stdout.log").write_text("")
            measured = analyze(directory, [])
            self.assertTrue(measured["input_expiry"])
            transition = measured["expiry_transitions"][0]
            self.assertEqual(transition["previous_decision_age_ms"], 249)
            self.assertEqual(transition["decision_age_ms"], 253)
            self.assertGreater(transition["receipt_to_telemetry_ms"], 250)


class LatencyBudgetTests(unittest.TestCase):
    def test_correlates_one_sequence_across_all_stages(self):
        client = [
            {"event": "input", "index": 1, "sequence_floor": 7},
            {"event": "input_send", "index": 1, "sequence": 7,
             "sample_wall_ms": 100, "send_wall_ms": 101, "wall_ms": 101},
            {"event": "state_receive", "wall_ms": 108,
             "rows": [{"entity": 2, "sequence": 7}]},
            {"event": "apply", "entity": 2, "wall_ms": 110,
             "pose": {"entity": 2, "sequence": 7}},
            {"event": "render", "sequence": 7, "wall_ms": 111},
        ]
        host = [
            {"event": "host_receive", "participant": 2, "sequence": 7, "wall_ms": 103},
            {"event": "simulation", "entity": 2, "wall_ms": 105,
             "pose": {"entity": 2, "sequence": 7}},
            {"event": "state_send", "wall_ms": 106, "send_wall_ms": 107,
             "rows": [{"entity": 2, "sequence": 7}]},
        ]
        measured = latency_budget(host, client)
        self.assertEqual(measured["samples"], 1)
        self.assertEqual(measured["rows"][0]["sample_to_draw_ms"], 11)
        self.assertEqual(measured["rows"][0]["state_send_to_receive_ms"], 1)


if __name__ == "__main__":
    unittest.main()
