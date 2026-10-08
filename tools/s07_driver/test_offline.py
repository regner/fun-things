"""Offline evidence-validator counterexamples and private-closure checks; no engine launch."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from support import ROOT, stage_runtime

spec = importlib.util.spec_from_file_location('s07_analysis', ROOT / 'tools/s07_driver/analyze.py')
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


class DriverChecks(unittest.TestCase):
    """Protect independent evidence checks with deliberately invalid receipts."""

    def setUp(self):
        """Load an actual development receipt as the known-valid counterexample baseline."""
        self.folder = tempfile.TemporaryDirectory(prefix='s07-offline-negative-')
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name)
        source = ROOT / 'docs/spikes/s07-sustained-driver-evidence/development'
        self.result = json.loads((source / 'result.json').read_text())
        import gzip
        self.rows = [json.loads(line) for line in gzip.decompress((source / 'traversals.jsonl.gz').read_bytes()).decode().splitlines()]

    def inspect(self, rows=None, result=None):
        """Use the real independent analyzer on temporary encoded receipt bytes."""
        (self.path / 'result.json').write_text(json.dumps(result or self.result))
        (self.path / 'traversals.jsonl').write_text('\n'.join(json.dumps(r) for r in (rows or self.rows)) + '\n')
        return analysis.analyze(self.path)['failures']

    def test_actual_receipt_and_faults(self):
        """Require actual positives and refusal of independent lifecycle/trajectory corruptions."""
        self.assertEqual(self.inspect(), [])
        changes = [lambda r: r[0].update(timed_out=True),
                   lambda r: r[0].update(samples=[]),
                   lambda r: r[0]['start'].update(position=[20, .001, 6.5]),
                   lambda r: r[0]['end'].update(yaw=0),
                   lambda r: r[0]['samples'][10].update(contacts=['solid']),
                   lambda r: r[0].update(freed=False),
                   lambda r: r[0].update(signature='different'),
                   lambda r: r[0]['start'].update(velocity=[1, 0, 0]),
                   lambda r: r[0]['samples'][10].update(position=[0, 0, 20])]
        for change in changes:
            rows = copy.deepcopy(self.rows)
            change(rows)
            self.assertTrue(self.inspect(rows))
        result = copy.deepcopy(self.result)
        result['requested_wall_seconds'] = 600
        self.assertTrue(self.inspect(result=result))

    def test_minimal_runtime_closure(self):
        """Require linked saved originals without service/native addons or arbitrary fixture copies."""
        project = self.path / 'closure'
        project.mkdir()
        manifest = stage_runtime(project)
        self.assertEqual(len(manifest), 46)
        self.assertEqual(sum(name.endswith('.glb') for name in manifest), 5)
        self.assertFalse((project / 'addons').exists())
        settings = (project / 'project.godot').read_text()
        self.assertNotIn('[autoload]', settings)
        self.assertNotIn('[editor_plugins]', settings)
        self.assertNotIn('tests/fixtures/s06/proof.gd', manifest)
        for name in manifest:
            if name != 'project.godot':
                self.assertEqual((project / name).read_bytes(), (ROOT / name).read_bytes())


if __name__ == '__main__':
    unittest.main()
