"""Focused tests for the canonical production-check orchestration."""

from pathlib import Path
import tempfile
import unittest

from production_checks import GUT_VERSION, gut_command, verify_gut_pin


class ProductionChecksTest(unittest.TestCase):
    def test_gut_vendor_pin_matches_reviewed_release(self):
        self.assertEqual(GUT_VERSION, "9.7.1")
        self.assertTrue(verify_gut_pin())

    def test_default_gut_command_uses_project_config_and_junit_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            command = gut_command("godot", root / "project", root / "results.xml")

        self.assertIn("res://addons/gut/gut_cmdln.gd", command)
        self.assertTrue(any(argument.startswith("-gjunit_xml_file=") for argument in command))
        self.assertNotIn("-gconfig=", command)

    def test_subset_gut_command_disables_default_discovery(self):
        command = gut_command(
            "godot",
            Path("project"),
            Path("results.xml"),
            test_dirs=["tests/unit/session"],
        )

        self.assertIn("-gconfig=", command)
        self.assertIn("-gdir=res://tests/unit/session", command)
        self.assertIn("-ginclude_subdirs", command)

    def test_negative_gut_command_isolated_from_default_suite(self):
        command = gut_command("godot", Path("project"), diagnostic_failure=True)

        self.assertIn("-gconfig=", command)
        self.assertIn("-gdir=res://tests/diagnostic/gut_failure", command)
        self.assertNotIn("res://tests/unit", command)


if __name__ == "__main__":
    unittest.main()
