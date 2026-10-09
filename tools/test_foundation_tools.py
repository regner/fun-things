"""Focused failure/ownership tests for the foundation tooling."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from run_s03 import Proxy, stop_children
from script_checks import compile_project_settings, checked_command, environment, owned_scripts


class ResettingSocket:
    """Fake UDP socket: one Windows-style reset notification, one datagram, then empty."""

    def __init__(self):
        self.events = [ConnectionResetError(10054), (b"hello", ("127.0.0.1", 5555))]
        self.sent = []

    def recvfrom(self, _size):
        if not self.events:
            raise BlockingIOError
        event = self.events.pop(0)
        if isinstance(event, Exception):
            raise event
        return event

    def sendto(self, data, address):
        self.sent.append((data, address))


class FoundationToolsTest(unittest.TestCase):
    def test_unused_and_owned_addon_scripts_are_discovered(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = ["tests/unused.gd", "addons/owned/unused.gd",
                     "addons/godotsteam/vendor.gd", "addons/godot_mcp_toolkit/vendor.gd",
                     ".hidden/hidden.gd", "art/source/ignored.gd"]
            for relative in paths:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            (root / "art/source/.gdignore").touch()
            self.assertEqual([path.relative_to(root).as_posix() for path in owned_scripts(root)],
                             ["addons/owned/unused.gd", "tests/unused.gd"])

    def test_compile_mirror_disables_only_development_startup(self):
        settings = """[autoload]
Gameplay="*res://gameplay.gd"
MCPRuntimeServer="*res://addons/godot_mcp_toolkit/runtime/mcp_runtime_server.gd"

[editor_plugins]
enabled=PackedStringArray("res://addons/godot_mcp_toolkit/plugin.cfg")

[display]
window/size/viewport_width=1280
"""
        stripped = compile_project_settings(settings)
        self.assertIn('Gameplay="*res://gameplay.gd"', stripped)
        self.assertNotIn("MCPRuntimeServer", stripped)
        self.assertNotIn("[editor_plugins]", stripped)
        self.assertIn("[display]", stripped)

    def test_success_exit_with_script_error_fails_and_retains_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / "check.log"
            ok = checked_command([sys.executable, "-c",
                                  "print('SCRIPT ERROR: unused script failed')"],
                                 log, {})
            self.assertFalse(ok)
            self.assertIn("unused script failed", log.read_text())

    def test_proxy_survives_windows_udp_reset_notification(self):
        proxy = Proxy.__new__(Proxy)
        proxy.socket = ResettingSocket()
        proxy.host = ("127.0.0.1", 6666)
        proxy.client = None
        proxy.armed = False
        proxy.held = None
        proxy.resets = 0
        proxy.poll()
        self.assertEqual(proxy.resets, 1)
        self.assertEqual(proxy.socket.sent, [(b"hello", ("127.0.0.1", 6666))])

    def test_child_environment_isolates_windows_user_roots(self):
        with tempfile.TemporaryDirectory() as temporary:
            env = environment(Path(temporary))
            for variable in ["APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"]:
                self.assertTrue(Path(env[variable]).is_relative_to(Path(temporary)))
                self.assertTrue(Path(env[variable]).is_dir())

    def test_cleanup_leaves_unrelated_process_alive(self):
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            stop_children([child])
            self.assertIsNotNone(child.poll())
            self.assertIsNone(unrelated.poll())
        finally:
            stop_children([child, unrelated])


if __name__ == "__main__":
    unittest.main()
