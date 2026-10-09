"""Offline checks for S14 result validation and generated source audio."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "tools" / "s14" / "run.py"
SPEC = importlib.util.spec_from_file_location("s14_run", RUN_PATH)
assert SPEC is not None and SPEC.loader is not None
S14_RUN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S14_RUN)


class S14AudioTests(unittest.TestCase):
    """Protect independent cap accounting and generated WAV contracts."""

    @staticmethod
    def _valid_receipt() -> dict:
        """Build one independently expected bounded-storm receipt."""
        return {
            "success": True,
            "failures": [],
            "audio_driver": "Dummy",
            "peak": {
                "caps": {"engines": 8, "explosions": 8, "weapons": 6},
                "active": {"engines": 8, "explosions": 8, "weapons": 6},
                "requests": {
                    "explosions_accepted": 8,
                    "explosions_dropped": 16,
                    "weapon_accepted": 6,
                    "weapon_dropped": 6,
                },
            },
            "settings_roundtrip": {
                "passed": True,
                "malformed_defaults": {"passed": True},
            },
        }

    def test_validate_receipt_accepts_expected_bounded_storm(self) -> None:
        receipt = self._valid_receipt()
        self.assertEqual(S14_RUN.validate_receipt(receipt), [])

    def test_validate_receipt_rejects_under_active_voice(self) -> None:
        receipt = self._valid_receipt()
        receipt["peak"]["active"]["engines"] = 7
        self.assertIn(
            "instantaneous peak voices differ from independent expectations",
            S14_RUN.validate_receipt(receipt),
        )

    def test_validate_receipt_rejects_wrong_cap(self) -> None:
        receipt = self._valid_receipt()
        receipt["peak"]["caps"]["explosions"] = 9
        self.assertIn(
            "category caps differ from independent expectations",
            S14_RUN.validate_receipt(receipt),
        )

    def test_validate_receipt_rejects_malformed_settings_failure(self) -> None:
        receipt = self._valid_receipt()
        receipt["settings_roundtrip"]["malformed_defaults"]["passed"] = False
        self.assertIn(
            "malformed settings did not retain safe defaults",
            S14_RUN.validate_receipt(receipt),
        )

    def test_diagnostic_classifier_accepts_only_exact_dummy_observation(self) -> None:
        exact = [
            "WARNING: 23 ObjectDB instances were leaked at exit "
            "(run with `--verbose` for details).",
            "ERROR: 7 resources still in use at exit (run with --verbose for details).",
        ]
        known, unexpected = S14_RUN.classify_diagnostics(exact, self._valid_receipt())
        self.assertEqual(known, exact)
        self.assertEqual(unexpected, [])

    def test_diagnostic_classifier_rejects_different_count(self) -> None:
        diagnostic = "WARNING: 24 ObjectDB instances were leaked at exit"
        known, unexpected = S14_RUN.classify_diagnostics(
            [diagnostic], self._valid_receipt()
        )
        self.assertEqual(known, [])
        self.assertEqual(unexpected, [diagnostic])

    def test_diagnostic_classifier_rejects_exact_line_on_wasapi(self) -> None:
        receipt = self._valid_receipt()
        receipt["audio_driver"] = "WASAPI"
        diagnostic = "ERROR: 7 resources still in use at exit (run with --verbose for details)."
        known, unexpected = S14_RUN.classify_diagnostics([diagnostic], receipt)
        self.assertEqual(known, [])
        self.assertEqual(unexpected, [diagnostic])

    def test_saved_resources_have_stable_editor_identities(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "s14"
        scene_lines = (fixture / "audio_test.tscn").read_text(encoding="utf-8").splitlines()
        bus_header = (fixture / "bus_layout.tres").read_text(encoding="utf-8").splitlines()[0]
        self.assertIn('uid="uid://', scene_lines[0])
        self.assertIn('uid="uid://', bus_header)
        external_resources = [line for line in scene_lines if line.startswith("[ext_resource")]
        scene_nodes = [line for line in scene_lines if line.startswith("[node")]
        self.assertEqual(len(external_resources), 10)
        self.assertTrue(all('uid="uid://' in line for line in external_resources))
        self.assertEqual(len(scene_nodes), 59)
        self.assertTrue(all("unique_id=" in line for line in scene_nodes))

    def test_generated_wavs_are_mono_pcm_at_declared_rate(self) -> None:
        audio_dir = ROOT / "tests" / "fixtures" / "s14" / "audio"
        paths = sorted(audio_dir.glob("*.wav"))
        self.assertEqual(len(paths), 8)
        for path in paths:
            with self.subTest(path=path.name), wave.open(str(path), "rb") as audio:
                self.assertEqual(audio.getnchannels(), 1)
                self.assertEqual(audio.getsampwidth(), 2)
                self.assertEqual(audio.getframerate(), 44_100)
                self.assertGreater(audio.getnframes(), 4_000)


if __name__ == "__main__":
    unittest.main()
