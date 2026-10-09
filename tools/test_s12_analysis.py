"""Independent analyzer checks for S12 agreement and false-positive accounting."""

import unittest

from run_s12 import analyze, evaluate_case


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
            "probes": [],
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

    def test_runner_requires_exact_security_probes_and_adverse_schedule(self):
        measurements = {
            "attempts": 96,
            "responses": 96,
            "accepted_shots": 60,
            "by_target": {"pedestrian": {"samples": 30}, "car": {"samples": 30}},
            "history_samples": 24,
            "history_peak_bytes": 2988,
            "security_probes": [
                {"accepted": False, "sequence": 96, "reason": "STALE_SEQUENCE"},
                {"accepted": False, "sequence": 97, "reason": "INVALID"},
                {"accepted": False, "sequence": 98, "reason": "INVALID"},
            ],
            "rocket_presentation_offset_m": {"samples": 8},
        }
        proxy = [
            {"event": "blackout_begin"},
            {"event": "drop", "reason": "blackout"},
            {"event": "blackout_end"},
        ]
        host = [
            {"event": "stall_begin", "wall_usec": 1_000_000},
            {"event": "stall_end", "wall_usec": 1_250_000},
        ]
        criteria = evaluate_case(measurements, "adverse", proxy, host, True)
        self.assertTrue(all(criteria.values()))

        measurements["security_probes"][2]["reason"] = "OK"
        criteria = evaluate_case(measurements, "adverse", proxy, host, True)
        self.assertFalse(criteria["security_probe_outcomes"])
        measurements["security_probes"][2]["reason"] = "INVALID"

        criteria = evaluate_case(measurements, "adverse", [], host, True)
        self.assertFalse(criteria["adverse_interruption_and_stall"])
        criteria = evaluate_case(measurements, "adverse", proxy, host[:1], True)
        self.assertFalse(criteria["adverse_interruption_and_stall"])


if __name__ == "__main__":
    unittest.main()
