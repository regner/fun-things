"""Offline checks for S08 Windows observation export gating; no engine is launched."""

from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent / "s08"))
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

    def test_import_diagnostic_with_zero_exit_stops_before_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            engine = Path(temporary) / "godot.exe"
            engine.write_bytes(b"engine")
            observation.ARGS.godot = str(engine)
            noisy = {"exit": 0, "diagnostics": ["WARNING: unexpected"]}
            with self.version, mock.patch.object(observation, "checked",
                                                 return_value=noisy) as checked:
                with self.assertRaisesRegex(RuntimeError, "import failed or reported"):
                    observation.export(Path(temporary), Path(temporary), {})
            self.assertEqual(checked.call_count, 1)

    def test_export_diagnostic_fails_even_with_exact_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            task = Path(temporary)
            engine = task / "godot.exe"
            engine.write_bytes(b"engine")
            observation.ARGS.godot = str(engine)
            name, size, digest = observation.TEMPLATES["release"]

            def fake_checked(_task, phase, *_rest):
                if phase.startswith("export-"):
                    folder = task / "export-release"
                    (folder / "FunThingsS08.exe").write_bytes(b"exe")
                    (folder / "FunThingsS08.pck").write_bytes(b"pck")
                    return {"exit": 0, "diagnostics": ["ERROR: export"]}
                return {"exit": 0, "diagnostics": []}

            exact = {"bytes": size, "sha256": digest}
            real_identity = observation.identity
            with self.version, mock.patch.object(observation, "checked", fake_checked), \
                    mock.patch.object(observation, "identity", side_effect=lambda p: (
                        exact if p.name == "FunThingsS08.exe" else real_identity(p))):
                with self.assertRaisesRegex(RuntimeError, "reported diagnostics"):
                    observation.export(task, task, {})


if __name__ == "__main__":
    unittest.main()
