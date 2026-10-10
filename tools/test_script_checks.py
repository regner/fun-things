"""Focused tests for isolated owned-script compilation."""

import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest import mock

import script_checks

OLD_SHARED_DEADLINE_SECONDS = 120
SIMULATED_LAUNCH_SECONDS = 1.0


class _AdvancingClock:
    """Advance only when a mocked engine launch consumes simulated wall time."""

    def __init__(self):
        self.current = 0.0

    def monotonic(self):
        return self.current

    def advance_launch(self):
        self.current += SIMULATED_LAUNCH_SECONDS


class ScriptChecksTest(unittest.TestCase):
    def test_hung_setup_import_fails_at_the_project_import_timeout(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            root = temporary_path / "source"
            output = temporary_path / "output"
            root.mkdir()
            output.mkdir()
            (root / "project.godot").write_text("[application]\n", encoding="utf-8")
            scripts = [root / "script.gd"]
            setup_timeout = None
            clock = _AdvancingClock()

            def run_engine(command, **kwargs):
                nonlocal setup_timeout
                if "--import" in command:
                    setup_timeout = kwargs["timeout"]
                    clock.current += setup_timeout
                    raise subprocess.TimeoutExpired(command, setup_timeout)
                clock.advance_launch()
                return subprocess.CompletedProcess(command, 0)

            with (
                mock.patch.object(time, "monotonic", side_effect=clock.monotonic),
                mock.patch.object(script_checks, "ROOT", root),
                mock.patch.object(script_checks, "owned_scripts", return_value=scripts),
                mock.patch.object(script_checks.subprocess, "run", side_effect=run_engine),
            ):
                compiled = script_checks.compile_all("godot", output)

            setup = json.loads((output / "compiler-setup.json").read_text(encoding="utf-8"))
            timeout_log = (output / "compiler-import.log").read_text(encoding="utf-8")

        self.assertFalse(compiled)
        self.assertEqual(setup, {"ok": False})
        self.assertEqual(setup_timeout, script_checks.PROJECT_IMPORT_TIMEOUT_SECONDS)
        self.assertEqual(clock.current, script_checks.PROJECT_IMPORT_TIMEOUT_SECONDS + 1.0)
        self.assertIn("CHECK DEADLINE EXCEEDED", timeout_log)

    def test_many_scripts_each_receive_the_full_per_script_timeout(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            root = temporary_path / "source"
            output = temporary_path / "output"
            root.mkdir()
            output.mkdir()
            (root / "project.godot").write_text("[application]\n", encoding="utf-8")
            scripts = [root / f"script_{index:03}.gd" for index in range(200)]
            compile_timeouts = []
            clock = _AdvancingClock()

            def run_engine(command, **kwargs):
                if "--check-only" in command:
                    compile_timeouts.append(kwargs["timeout"])
                clock.advance_launch()
                return subprocess.CompletedProcess(command, 0)

            with (
                mock.patch.object(time, "monotonic", side_effect=clock.monotonic),
                mock.patch.object(script_checks, "ROOT", root),
                mock.patch.object(script_checks, "owned_scripts", return_value=scripts),
                mock.patch.object(script_checks.subprocess, "run", side_effect=run_engine),
            ):
                compiled = script_checks.compile_all("godot", output)

            results = json.loads((output / "compilation.json").read_text(encoding="utf-8"))

        self.assertTrue(compiled)
        self.assertGreater(clock.current, OLD_SHARED_DEADLINE_SECONDS)
        self.assertEqual(len(results), 200)
        self.assertTrue(all(row["ok"] for row in results))
        self.assertEqual(
            compile_timeouts,
            [script_checks.SCRIPT_COMPILE_TIMEOUT_SECONDS] * len(scripts),
        )

    def test_hung_script_fails_at_the_per_script_timeout(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            root = temporary_path / "source"
            output = temporary_path / "output"
            root.mkdir()
            output.mkdir()
            (root / "project.godot").write_text("[application]\n", encoding="utf-8")
            scripts = [root / f"good_{index:03}.gd" for index in range(130)]
            scripts.append(root / "hung.gd")
            hung_timeout = None
            clock = _AdvancingClock()

            def run_engine(command, **kwargs):
                nonlocal hung_timeout
                clock.advance_launch()
                if command[-1] == "res://hung.gd":
                    hung_timeout = kwargs["timeout"]
                    raise subprocess.TimeoutExpired(command, hung_timeout)
                return subprocess.CompletedProcess(command, 0)

            with (
                mock.patch.object(time, "monotonic", side_effect=clock.monotonic),
                mock.patch.object(script_checks, "ROOT", root),
                mock.patch.object(script_checks, "owned_scripts", return_value=scripts),
                mock.patch.object(script_checks.subprocess, "run", side_effect=run_engine),
            ):
                compiled = script_checks.compile_all("godot", output)

            results = json.loads((output / "compilation.json").read_text(encoding="utf-8"))
            timeout_log = (output / "compile-130.log").read_text(encoding="utf-8")

        self.assertFalse(compiled)
        self.assertGreater(clock.current, OLD_SHARED_DEADLINE_SECONDS)
        self.assertTrue(all(row["ok"] for row in results[:-1]))
        self.assertEqual(results[-1], {"script": "hung.gd", "ok": False})
        self.assertEqual(hung_timeout, script_checks.SCRIPT_COMPILE_TIMEOUT_SECONDS)
        self.assertIn("CHECK DEADLINE EXCEEDED", timeout_log)


if __name__ == "__main__":
    unittest.main()
