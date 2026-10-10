from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


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

    def test_main_prints_pasteable_powershell_example(self):
        class FakeChild:
            def __init__(self, events=None):
                self.events = events or []
                self.hard_timed_out = False

            def wait_event(self, _predicate, _timeout):
                return {"brackett_loaded": True}

            def finish(self, timeout=5.0):
                return 0

        class FakeRunner:
            def __init__(self, _executable, _output):
                self.host = FakeChild([{"event": "host_ready", "port": 24567}])
                self.client = FakeChild()

            def pair(self, _case, _scenario):
                return self.host, self.client

            @staticmethod
            def event(name):
                return lambda event: event.get("event") == name

            def cleanup(self):
                pass

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "owner's build" / "FunThingsDebug.exe"
            executable.parent.mkdir()
            executable.touch()
            output = root / "owner-output"
            stdout = io.StringIO()
            arguments = [
                "launch_exported_pair.py",
                "--executable",
                str(executable),
                "--output",
                str(output),
            ]
            with (
                mock.patch.object(launch_exported_pair, "ExportedAcceptanceRunner", FakeRunner),
                mock.patch.object(sys, "argv", arguments),
                redirect_stdout(stdout),
            ):
                result = launch_exported_pair.main()

        printed = stdout.getvalue()
        example = next(line for line in printed.splitlines() if line.startswith("PowerShell example:"))
        self.assertEqual(result, 0)
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
