"""Focused negative tests for S08-X exported native-dependency inspection."""

from pathlib import Path
import tempfile
import unittest

from s08_x.inspect_exports import (
    find_forbidden_output_files,
    is_forbidden_export_path,
    missing_required_entries,
    project_export_requirements,
)


class S08XExportInspectionTest(unittest.TestCase):
    def test_discovers_main_scene_and_recursive_text_dependencies(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "project.godot").write_text(
                '[application]\nrun/main_scene="res://scenes/boot.tscn"\n'
            )
            (root / "scenes").mkdir()
            (root / "scripts").mkdir()
            (root / "scenes/boot.tscn").write_text(
                '[ext_resource type="Script" path="res://scripts/boot.gd" id="1"]\n'
            )
            (root / "scripts/boot.gd").write_text(
                'const VIEW = preload("res://scenes/view.tscn")\n'
            )
            (root / "scenes/view.tscn").write_text("[gd_scene format=3]\n")

            requirements = project_export_requirements(root)

        self.assertEqual(requirements, [
            "scenes/boot.tscn",
            "scenes/view.tscn",
            "scripts/boot.gd",
        ])

    def test_reports_missing_main_dependency_from_synthetic_package_listing(self):
        entries = ["scenes/boot.tscn.remap", "scripts/boot.gdc"]
        required = ["scenes/boot.tscn", "scripts/boot.gd", "scenes/view.tscn"]

        self.assertEqual(
            missing_required_entries(entries, required),
            ["scenes/view.tscn"],
        )

    def test_rejects_test_only_content_in_pack_paths(self):
        forbidden = [
            "addons/gut/gut.gd",
            "res://addons/gut/LICENSE.md",
            "tests/unit/tooling/test_gut_smoke.gd",
            "tests/fixtures/s06/intersection.tscn",
        ]
        for path in forbidden:
            with self.subTest(path=path):
                self.assertTrue(is_forbidden_export_path(path))

    def test_rejects_godotsteam_and_steamworks_dependencies_in_pack_paths(self):
        forbidden = [
            "addons/godotsteam/godotsteam.gdextension",
            "addons/godotsteam/win64/libgodotsteam.windows.template_release.x86_64.dll",
            "steam_api.dll",
            "steam_api64.dll",
            "libsteam_api.so",
            "libsteam_api.dylib",
            "native/libsteam_api.so.import",
        ]
        for path in forbidden:
            with self.subTest(path=path):
                self.assertTrue(is_forbidden_export_path(path))

    def test_rejects_steamworks_dependency_beside_executable(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / "FunThings.exe").touch()
            (output / "steam_api64.dll").touch()

            self.assertEqual(find_forbidden_output_files(output), ["steam_api64.dll"])


if __name__ == "__main__":
    unittest.main()
