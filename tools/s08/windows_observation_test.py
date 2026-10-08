#!/usr/bin/env python3
"""Offline checks for windows_observation export gating; no engine is launched."""

from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import windows_observation as observation  # noqa: E402


class ExportGateTest(unittest.TestCase):
    def setUp(self):
        observation.ARGS = types.SimpleNamespace(godot=None)
        self.version = mock.patch.object(
            observation.subprocess, "run",
            return_value=types.SimpleNamespace(stdout=observation.PIN + "\n"))

    def test_missing_engine_on_path_is_a_structured_failure(self):
        with mock.patch.object(observation.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "godot not found"):
                observation.export(Path("."), Path("."), {})

    def test_import_diagnostic_with_zero_exit_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            engine = Path(temporary) / "godot.exe"
            engine.write_bytes(b"engine")
            observation.ARGS.godot = str(engine)
            noisy = {"exit": 0, "diagnostics": ["WARNING: unexpected"]}
            with self.version, mock.patch.object(observation, "checked", return_value=noisy):
                with self.assertRaisesRegex(RuntimeError, "diagnostics"):
                    observation.export(Path(temporary), Path(temporary), {})

    def test_export_diagnostic_with_zero_exit_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            task = Path(temporary)
            engine = task / "godot.exe"
            engine.write_bytes(b"engine")
            observation.ARGS.godot = str(engine)
            results = iter([{"exit": 0, "diagnostics": []},
                            {"exit": 0, "diagnostics": ["ERROR: export"]}])
            with self.version, mock.patch.object(observation, "checked",
                                                 side_effect=lambda *a: next(results)):
                with self.assertRaisesRegex(RuntimeError, "release export failed"):
                    observation.export(task, task, {})


if __name__ == "__main__":
    unittest.main()
