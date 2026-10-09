"""Regression checks for ownership-sensitive experiment evidence, without engine mutation."""

import json
from pathlib import Path
import tempfile
import unittest

from run_s03_r import analyze


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


if __name__ == "__main__":
    unittest.main()
