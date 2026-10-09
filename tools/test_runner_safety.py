"""Offline regression checks for shared measurement-runner safety helpers."""

from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import measurement_identity as identity_module  # noqa: E402
from incremental_log import prefixed_json_records
from measurement_identity import measurement_identity
from window_safety import capped_window_arguments, require_capped_modes, require_capped_window


class WindowSafetyTests(unittest.TestCase):
    """Prevent uncapped or incorrectly capped windowed Godot commands."""

    def test_exact_60_fps_cap_is_required(self):
        """Accept one exact cap and reject missing, uncapped, or alternate caps."""
        require_capped_window(["godot", "--windowed", *capped_window_arguments()])
        for command in (
            ["godot", "--windowed"],
            ["godot", "--disable-vsync", "--max-fps", "0"],
            ["godot", "--windowed", "--max-fps", "30"],
            ["godot", "--windowed", "--max-fps", "120"],
            ["godot", "--windowed", "--max-fps", "60", "--max-fps", "60"],
        ):
            with self.subTest(command=command), self.assertRaises(ValueError):
                require_capped_window(command)

    def test_uncapped_mode_is_withdrawn(self):
        """Permit only capped60 in graphical mode selections."""
        require_capped_modes(["capped60"])
        for modes in ([], ["uncapped"], ["uncapped", "capped60"]):
            with self.subTest(modes=modes), self.assertRaises(ValueError):
                require_capped_modes(modes)

    def test_windowed_runners_use_shared_explicit_cap(self):
        """Keep every windowed runner in this lane on the shared explicit cap."""
        runners = [
            "s02/observe_windows.py", "s05_draw/observe.py",
            "s05_draw/observe_windows.py", "s05_vsync_image/run.py",
            "s06/capture_windows.py", "s07_comparator/run.py", "s07_env/run.py",
            "s07_graphical/run.py", "s13/run.py", "s14/run.py", "s15/run.py",
        ]
        for relative in runners:
            with self.subTest(runner=relative):
                source = (TOOLS / relative).read_text()
                self.assertIn("capped_window_arguments", source)
                self.assertIn("require_capped_window", source)


class MeasurementIdentityTests(unittest.TestCase):
    """Protect complete reproduction binding in the shared receipt helper."""

    def test_identity_binds_sources_invocation_and_parameters(self):
        """Fingerprint recursive inputs and preserve explicit invocation details."""
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "runner.py").write_text("print('runner')\n")
            (root / "fixture").mkdir()
            (root / "fixture/input.gd").write_text("extends Node\n")
            with mock.patch.object(
                identity_module,
                "repository_identity",
                return_value={"commit": "abc", "tree": "def", "status_porcelain": []},
            ):
                receipt = measurement_identity(
                    root,
                    ["runner.py", "fixture"],
                    {"output": Path("outside"), "repeats": 3},
                    argv=["runner.py", "--repeats", "3"],
                    cwd=root,
                )

            self.assertEqual(receipt["repository"]["tree"], "def")
            self.assertEqual(set(receipt["measurement_sources"]), {
                "runner.py", "fixture/input.gd",
            })
            self.assertEqual(receipt["invocation"]["argv"], [
                "runner.py", "--repeats", "3",
            ])
            self.assertEqual(
                receipt["invocation"]["effective_parameters"]["output"], "outside"
            )


class EvidenceBindingSourceTests(unittest.TestCase):
    """Keep all quiet-pass runners on the shared identity helper."""

    def test_required_runners_use_shared_identity(self):
        """Require centralized identity capture in every runner named by the brief."""
        runners = [
            "run_s03.py", "run_s08_linux.py", "run_s11.py", "run_s12.py",
            "s07_driver/run.py", "s07_env/run.py", "s07_graphical/run.py",
            "s09/run.py", "s10/run.py", "s13/run.py", "s14/run.py", "s15/run.py",
        ]
        for relative in runners:
            with self.subTest(runner=relative):
                source = (TOOLS / relative).read_text()
                self.assertIn("from measurement_identity import measurement_identity", source)
                self.assertIn("measurement_identity(", source)


class QuietTimingSourceTests(unittest.TestCase):
    """Fence heavy workstation sampling to post-case code paths."""

    def test_samplers_follow_measured_child_completion(self):
        """Keep each heavy sampler textually after its bounded child wait or command."""
        checks = {
            "tools/s09/run.py": ("passed = checked_command", "snapshot = host_snapshot()"),
            "tools/s10/run.py": ("returncode = child.wait", "after = telemetry_snapshot()"),
            "tools/run_s11.py": (
                "if any(child.returncode != 0", "environment_after = process_environment()"
            ),
            "tools/run_s12.py": ("client_summary = results", "load = host_load()"),
            "tools/s13/run.py": ("child.wait(timeout=deadline_seconds)", "load = system_load()"),
            "tools/s14/run.py": ("completed = subprocess.run", "environment_after ="),
            "tools/s15/run.py": ("child.wait(timeout=args.warmup", "contention ="),
        }
        root = Path(__file__).resolve().parents[1]
        for relative, (completion, sample) in checks.items():
            with self.subTest(runner=relative):
                source = (root / relative).read_text()
                self.assertGreater(source.index(sample), source.index(completion))
                settle = source.index("time.sleep(QUIET_SETTLE_SECONDS)", source.index(sample))
                self.assertGreater(settle, source.index(sample))
        self.assertNotIn("environment_executor.submit", (root / "tools/run_s11.py").read_text())
        self.assertNotIn("during = telemetry_snapshot", (root / "tools/s10/run.py").read_text())


class IncrementalLogTests(unittest.TestCase):
    """Keep polling cost proportional to newly appended complete bytes."""

    def test_required_polling_runners_use_incremental_reader(self):
        """Fence all four audited whole-log polling loops to the shared offset reader."""
        runners = [
            "run_s05.py", "s05_vsync_image/run.py", "s05_draw/observe.py",
            "s05_draw/observe_windows.py",
        ]
        for relative in runners:
            with self.subTest(runner=relative):
                source = (TOOLS / relative).read_text()
                self.assertIn("prefixed_json_records", source)

    def test_reader_retains_offsets_and_retries_only_partial_tail(self):
        """Read each complete record once while withholding an incomplete final record."""
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "stdout.log"
            path.write_bytes(b'S05 {"event":"ready"}\nS05 {"event":"part')
            state = {}

            first = prefixed_json_records(path, b"S05 ", state)
            self.assertEqual(first, [{"event": "ready"}])
            first_offset = state[str(path.resolve())]["offset"]

            self.assertEqual(prefixed_json_records(path, b"S05 ", state), first)
            self.assertEqual(state[str(path.resolve())]["offset"], first_offset)
            with path.open("ab") as stream:
                stream.write(b'ial"}\nignored\n')

            self.assertEqual(prefixed_json_records(path, b"S05 ", state), [
                {"event": "ready"}, {"event": "partial"},
            ])


if __name__ == "__main__":
    unittest.main()
