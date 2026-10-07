"""Independent telemetry counterexamples for car response and stale held intent."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_s04 import analyze


class CarMetrics(unittest.TestCase):
    def analyze_rows(self, host, client):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for role, rows in [('host', host), ('client', client)]:
                (root / role).mkdir()
                (root / role / 'stdout.log').write_text(''.join(
                    'S04 ' + json.dumps(row) + '\n' for row in rows))
            return analyze(root, [])

    def test_coast_foreign_pose_and_unacknowledged_motion_do_not_count(self):
        onset = {'event': 'input', 'index': 1, 'move': 1, 'turn': 0,
                 'time_ms': 100, 'position': [0, 0, 0], 'yaw': 0,
                 'velocity': [0, 0, -5], 'sequence_floor': 10}
        def frame(at, entity, speed, sequence):
            return {'event': 'apply', 'entity': entity, 'time_ms': at,
                    'position': [0, 0, -1], 'yaw': 0,
                    'pose': {'entity': entity, 'tick': at, 'sequence': sequence,
                             'velocity': [0, 0, -speed]}}
        rows = [onset, frame(110, 1, 7, 10), frame(120, 2, 7, 9),
                frame(130, 2, 5, 10), frame(180, 2, 6, 10)]
        result = self.analyze_rows([], rows)
        self.assertEqual(result['responses'][0]['physics_ms'], 80)
        self.assertEqual(result['response_p95_ms']['rendered_frame_ms'], None)
        self.assertEqual(result['physics_response_missing'], 0)
        result = self.analyze_rows([], rows[:-1])
        self.assertEqual(result['responses'][0]['physics_ms'], None)
        self.assertEqual(result['physics_response_missing'], 1)

    def test_expiry_neutralizes_intent_without_requiring_parked_velocity(self):
        drive = {'throttle': 1.0, 'steer': 0.0, 'brake': 0.0, 'handbrake': False}
        neutral = dict(drive, throttle=0.0)
        def state(at, held):
            return {'event': 'simulation', 'time_ms': at, 'wall_ms': at,
                    'local_tick': 1, 'receipt_ms': 0, 'held': held,
                    'pose': {'entity': 2, 'tick': at, 'position': [0, 0, 0],
                             'velocity': [0, 0, -3]}}
        result = self.analyze_rows([state(250, drive), state(267, neutral)], [])
        self.assertTrue(result['input_expiry'])
        result = self.analyze_rows([state(250, drive), state(280, drive)], [])
        self.assertFalse(result['input_expiry'])


if __name__ == '__main__':
    unittest.main()
