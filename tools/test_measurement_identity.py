"""Committed-source inventory tests for measurement identity receipts."""

from pathlib import Path
import subprocess
import tempfile
import unittest

from measurement_identity import source_fingerprints


class MeasurementSourceInventory(unittest.TestCase):
    """Keep ignored and untracked generated files out of reproducible identities."""

    def _git(self, root: Path, *arguments: str) -> None:
        """Run one setup command in the isolated repository."""
        subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)

    def test_directory_fingerprints_only_committed_files(self):
        """Exclude ignored bytecode and ordinary untracked files below a tracked directory."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._git(root, "init", "-q")
            (root / ".gitignore").write_text("__pycache__/\n*.pyc\n")
            sources = root / "tools/example"
            sources.mkdir(parents=True)
            (sources / "runner.py").write_text("print('tracked')\n")
            self._git(root, "add", ".gitignore", "tools/example/runner.py")
            self._git(root, "-c", "user.name=Test", "-c", "user.email=test@example.com",
                      "commit", "-qm", "fixture")

            generated = sources / "__pycache__/runner.cpython-314.pyc"
            generated.parent.mkdir()
            generated.write_bytes(b"ignored")
            (sources / "scratch.txt").write_text("untracked\n")

            result = source_fingerprints(root, ["tools/example"])
            self.assertEqual(list(result), ["tools/example/runner.py"])

    def test_explicit_untracked_source_is_rejected(self):
        """Do not produce a source-bound receipt for an unavailable explicit file."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._git(root, "init", "-q")
            source = root / "runner.py"
            source.write_text("print('untracked')\n")
            with self.assertRaisesRegex(ValueError, "not committed"):
                source_fingerprints(root, ["runner.py"])


if __name__ == "__main__":
    unittest.main()
