"""Focused tests for reproducible desktop export orchestration."""

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from export_builds import (
    MISSING_DEPENDENCY_MARKERS,
    TEMPLATE_HASHES,
    build_exports,
    missing_dependency_lines,
    timeout_command,
    verify_templates,
)


class ExportBuildsTest(unittest.TestCase):
    def test_every_godot_command_is_wrapped_by_external_timeout(self):
        command = timeout_command("timeout", 600, ["godot", "--headless"])

        self.assertEqual(command, ["timeout", "600s", "godot", "--headless"])

    def test_engine_mismatch_stops_before_any_export_invocation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            calls = []

            def fake_run_logged(command, log_path, _cwd, _timeout_seconds):
                calls.append(command)
                log_path.write_text("4.8.dev6.wrong\n", encoding="utf-8")
                return {
                    "command": command,
                    "duration_seconds": 0.01,
                    "exit_code": 0,
                    "log": log_path.as_posix(),
                    "missing_dependency_diagnostics": [],
                    "ok": True,
                }

            with mock.patch("export_builds.run_logged", side_effect=fake_run_logged):
                result = build_exports("wrong-godot", output, Path.cwd(), "timeout")

        self.assertFalse(result["ok"])
        self.assertEqual(result["exports"], [])
        self.assertEqual(len(calls), 1)
        self.assertFalse(any("--export-" in argument for argument in calls[0]))

    def test_dependency_scan_reports_only_missing_resource_diagnostics(self):
        text = "\n".join([
            "WARNING: editor plugin was skipped",
            "ERROR: Failed loading resource: res://missing.tres",
            "Could not resolve resource res://also_missing.tscn",
        ])

        failures = missing_dependency_lines(text)

        self.assertEqual(len(failures), 2)
        self.assertTrue(all(
            any(marker in line.lower() for marker in MISSING_DEPENDENCY_MARKERS)
            for line in failures
        ))

    def test_template_identity_requires_version_and_every_exact_member_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "version.txt").write_text("4.8.dev7\n", encoding="utf-8")
            for name in TEMPLATE_HASHES:
                (root / name).write_bytes(name.encode("utf-8"))

            result = verify_templates(root)

        self.assertFalse(result["ok"])
        self.assertEqual(set(result["members"]), set(TEMPLATE_HASHES))
        self.assertTrue(all(row["sha256"] for row in result["members"].values()))

    def test_template_identity_accepts_matching_synthetic_hashes_when_patched(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "version.txt").write_text("4.8.dev7\n", encoding="utf-8")
            original = TEMPLATE_HASHES.copy()
            try:
                for name in TEMPLATE_HASHES:
                    payload = name.encode("utf-8")
                    (root / name).write_bytes(payload)
                    TEMPLATE_HASHES[name] = hashlib.sha256(payload).hexdigest()

                result = verify_templates(root)
            finally:
                TEMPLATE_HASHES.clear()
                TEMPLATE_HASHES.update(original)

        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
