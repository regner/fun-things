"""Independent analyzer checks for S12 agreement and false-positive accounting."""

import unittest

from run_s12 import analyze


class CombatAnalysisTests(unittest.TestCase):
    def test_options_are_scored_against_client_perception(self):
        summary = {
            "shots": [
                {"target": "pedestrian", "speed": 1.5, "client_hit": True,
                 "current_hit": False, "rewind_hit": True, "rewind_clamped": False,
                 "rewind_cpu_usec": 3},
                {"target": "pedestrian", "speed": 1.5, "client_hit": False,
                 "current_hit": True, "rewind_hit": False, "rewind_clamped": False,
                 "rewind_cpu_usec": 5},
                {"target": "car", "speed": 12.0, "client_hit": False,
                 "current_hit": False, "rewind_hit": False, "rewind_clamped": True,
                 "rewind_cpu_usec": 7},
            ],
            "rockets": [{"offset_m": 1.25}],
            "host": {"history_peak_bytes": 2048, "history_samples": 24,
                     "rejections": {"INVALID": 2}},
            "attempts": 3,
            "responses": 3,
        }
        result = analyze(summary)
        pedestrian = result["by_target"]["pedestrian"]
        self.assertEqual(pedestrian["current_agreement_rate"], 0.0)
        self.assertEqual(pedestrian["rewind_agreement_rate"], 1.0)
        self.assertEqual(pedestrian["current_false_positives"], 1)
        self.assertEqual(pedestrian["rewind_false_positives"], 0)
        self.assertEqual(result["rewind_cpu_usec"]["worst"], 7)
        self.assertEqual(result["rocket_presentation_offset_m"]["worst"], 1.25)


if __name__ == "__main__":
    unittest.main()
