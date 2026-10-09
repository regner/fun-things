"""Focused tests for the road generator preflight staging and launch boundary."""

from pathlib import Path
import tempfile
import unittest

from road_generator_preflight import (
    IMPORT_KNOWN_DIAGNOSTICS,
    classify_diagnostics,
    preflight_command,
    stage_project,
)
from window_safety import require_capped_window


class RoadGeneratorPreflightTest(unittest.TestCase):
    def test_staged_project_enables_the_vendored_plugin(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            stage_project(project)

            settings = (project / "project.godot").read_text(encoding="utf-8")
            license_present = (project / "addons/road-generator/LICENSE").is_file()

        self.assertIn('res://addons/road-generator/plugin.cfg', settings)
        self.assertTrue(license_present)

    def test_import_diagnostic_classifier_keeps_unknown_errors_fatal(self):
        known_line = next(iter(IMPORT_KNOWN_DIAGNOSTICS))
        text = f"{known_line}\nERROR: new road failure\n"

        known, unexpected = classify_diagnostics(text, IMPORT_KNOWN_DIAGNOSTICS)

        self.assertEqual(known, [known_line])
        self.assertEqual(unexpected, ["ERROR: new road failure"])

    def test_windowed_command_has_exact_safety_cap_and_external_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            command = preflight_command(
                "godot", output / "project", output, "windowed", windowed=True
            )

            require_capped_window(command)

        self.assertIn("--windowed-check", command)
        self.assertNotIn("--headless", command)


if __name__ == "__main__":
    unittest.main()
