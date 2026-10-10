"""Focused tests for isolated owned-script compilation."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import script_checks


class ScriptChecksTest(unittest.TestCase):
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

            def run_engine(command, **kwargs):
                if "--check-only" in command:
                    compile_timeouts.append(kwargs["timeout"])
                return subprocess.CompletedProcess(command, 0)

            with (
                mock.patch.object(script_checks, "ROOT", root),
                mock.patch.object(script_checks, "owned_scripts", return_value=scripts),
                mock.patch.object(script_checks.subprocess, "run", side_effect=run_engine),
            ):
                compiled = script_checks.compile_all("godot", output)

            results = json.loads((output / "compilation.json").read_text(encoding="utf-8"))

        self.assertTrue(compiled)
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
            scripts = [root / "good.gd", root / "hung.gd"]
            hung_timeout = None

            def run_engine(command, **kwargs):
                nonlocal hung_timeout
                if command[-1] == "res://hung.gd":
                    hung_timeout = kwargs["timeout"]
                    raise subprocess.TimeoutExpired(command, hung_timeout)
                return subprocess.CompletedProcess(command, 0)

            with (
                mock.patch.object(script_checks, "ROOT", root),
                mock.patch.object(script_checks, "owned_scripts", return_value=scripts),
                mock.patch.object(script_checks.subprocess, "run", side_effect=run_engine),
            ):
                compiled = script_checks.compile_all("godot", output)

            results = json.loads((output / "compilation.json").read_text(encoding="utf-8"))
            timeout_log = (output / "compile-1.log").read_text(encoding="utf-8")

        self.assertFalse(compiled)
        self.assertEqual(
            results,
            [
                {"script": "good.gd", "ok": True},
                {"script": "hung.gd", "ok": False},
            ],
        )
        self.assertEqual(hung_timeout, script_checks.SCRIPT_COMPILE_TIMEOUT_SECONDS)
        self.assertIn("CHECK DEADLINE EXCEEDED", timeout_log)


if __name__ == "__main__":
    unittest.main()
