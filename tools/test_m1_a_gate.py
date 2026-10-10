from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parent
MODULE_ROOT = ROOT / "m1_a_gate"
sys.path.insert(0, str(MODULE_ROOT))

import launch_exported_pair
import run_exported_acceptance


class M1AGateLauncherTest(unittest.TestCase):
    def test_default_output_is_fresh_and_external(self):
        first = launch_exported_pair._default_output()
        second = launch_exported_pair._default_output()

        self.assertNotEqual(first, second)
        self.assertTrue(first.as_posix().startswith("C:/tmp/ft/"))
        self.assertIn("m1-a-gate-owner-pair", first.parts)

    def test_powershell_example_quotes_apostrophes(self):
        example = launch_exported_pair._powershell_example(
            Path("C:/tmp/owner's build/FunThingsDebug.exe")
        )

        self.assertIn("PowerShell", "PowerShell example")
        self.assertIn("owner''s build", example)
        self.assertNotIn("--output", example)

    def test_exported_command_needs_no_external_timeout_executable(self):
        command = run_exported_acceptance.exported_process_command(
            Path("C:/tmp/FunThingsDebug.exe"),
            ["--max-fps", "60"],
            Path("C:/tmp/output"),
            "host",
            "sustained",
            24567,
        )

        self.assertEqual(command[0].replace("\\", "/"), "C:/tmp/FunThingsDebug.exe")
        self.assertNotIn("timeout", command)
        self.assertIn("--m1-a-gate-scenario=sustained", command)


if __name__ == "__main__":
    unittest.main()
