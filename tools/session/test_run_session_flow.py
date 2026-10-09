"""Tests for bounded real-process session runner result handling."""

from pathlib import Path
import unittest
from unittest.mock import Mock

from tools.session.run_session_flow import SessionFlowRunner


class SessionFlowRunnerTest(unittest.TestCase):
    """Verify child process failures cannot produce a successful case result."""

    def test_settle_rejects_nonzero_child_exit(self):
        """Treat a nonzero exit as failure even after expected receipts were emitted."""
        child = Mock()
        child.name = "client"
        child.finish.return_value = 3
        child.diagnostics.return_value = []
        runner = SessionFlowRunner("godot", Path("unused"))

        with self.assertRaisesRegex(RuntimeError, "nonzero child exits"):
            runner.settle([child])


if __name__ == "__main__":
    unittest.main()
