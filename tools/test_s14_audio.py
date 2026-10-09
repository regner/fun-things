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

    def test_validate_receipt_accepts_expected_bounded_storm(self) -> None:
        receipt = {
            "success": True,
            "failures": [],
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
            "settings_roundtrip": {"passed": True},
        }
        self.assertEqual(S14_RUN.validate_receipt(receipt), [])

    def test_validate_receipt_rejects_over_cap_voice(self) -> None:
        receipt = {
            "success": True,
            "failures": [],
            "peak": {
                "caps": {"engines": 8, "explosions": 8, "weapons": 6},
                "active": {"engines": 9, "explosions": 8, "weapons": 6},
                "requests": {
                    "explosions_accepted": 8,
                    "explosions_dropped": 16,
                    "weapon_accepted": 6,
                    "weapon_dropped": 6,
                },
            },
            "settings_roundtrip": {"passed": True},
        }
        self.assertIn("engines exceeded cap", S14_RUN.validate_receipt(receipt))

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
