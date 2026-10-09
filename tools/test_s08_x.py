"""Focused negative tests for S08-X exported native-dependency inspection."""

from pathlib import Path
import tempfile
import unittest

from s08_x.inspect_exports import find_forbidden_output_files, is_forbidden_export_path


class S08XExportInspectionTest(unittest.TestCase):
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
