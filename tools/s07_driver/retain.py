"""Build/verify one complete S07 evidence expected-set manifest, including decoded trajectories."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from support import ROOT, identity, save

EVIDENCE = ROOT / 'docs/spikes/s07-sustained-driver-evidence'


def required_paths():
    """Declare required phase/source/failure/empty-stream paths independently of existing entries."""
    required = {'README.md', 'raw-requirements.md', 'predeclaration.md', 'simulation-declaration.md',
                'staged-inputs.json', 'budget.json', 'preservation-before-simulation.json',
                'preservation-final.json', 'static-checks.json', 'launch-receipt.json',
                'author/lifecycle.json', 'author/artifact-ledger.json', 'author/quiescence.json',
                'author/project-before.godot', 'author/project-after.godot',
                'author/project-settings.patch', 'author/project-settings-identities.json',
                'author/settings-seed.json', 'author/registry-binding.json',
                'author/staged-inputs.json', 'author/saved-artifact-recovery.json',
                'author/author.py', 'author/support-at-author.py'}
    required.update(f'author/call-{i:03}.json' for i in range(1, 18))
    for name in ['editor.stdout.log', 'editor.stderr.log', 'editor.engine.log',
                 'connector.stdout.log', 'connector.stderr.log',
                 'author-supervisor.stdout', 'author-supervisor.stderr']:
        required.add('author/' + name)
    for name in ['fixture.gd', 'run.gd', 'guards.gd', 'fixture.gd.uid', 'run.gd.uid',
                 'guards.gd.uid', 'intersection.tscn']:
        required.add('author/' + name + '.saved')
    for phase, commands in [('import', ['import']),
                            ('development', ['compile-fixture', 'compile-run', 'compile-guards', 'guards', 'routes']),
                            ('sustained', ['routes'])]:
        required.add(phase + '/phase.json')
        for command in commands:
            for name in ['command.json', 'stdout.log', 'stderr.log', 'engine.log', 'diagnostics.json']:
                required.add(f'{phase}/{command}/{name}')
        if phase != 'import':
            required.update(f'{phase}/{name}' for name in ['result.json', 'traversals.jsonl.gz', 'analysis.json'])
    required.add('development/guards.json')
    for command in ['import-supervisor', 'dev01-supervisor', 'dev01-analysis',
                    'sustained-supervisor', 'sustained-analysis', 'offline-tests']:
        required.update(command + suffix for suffix in ['.stdout', '.stderr'])
    return required


def build():
    """Bind actual sources and decoded stored bytes while rejecting omitted required streams."""
    actual = {str(p.relative_to(EVIDENCE)) for p in EVIDENCE.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    missing = required_paths() - actual
    if missing:
        raise RuntimeError('missing required evidence: ' + str(sorted(missing)))
    entries = []
    for name in sorted(actual):
        path = EVIDENCE / name
        row = {'path': name, **identity(path)}
        if path.suffix == '.gz':
            decoded = gzip.decompress(path.read_bytes())
            source = Path('/tmp/s07-driver-simulation-08760af5') / ('development-1' if name.startswith('development/') else 'sustained-1') / 'traversals.jsonl'
            if decoded != source.read_bytes():
                raise RuntimeError('decoded trajectory differs from actual source')
            row['decoded'] = {'bytes': len(decoded), 'sha256': hashlib.sha256(decoded).hexdigest()}
            row['actual_source'] = str(source)
        entries.append(row)
    return {'required_paths': sorted(required_paths()), 'expected_paths': sorted(actual), 'entries': entries,
            'immutable_base': '233493abc7d2e3c106fb620105cfb766f542813b',
            'engine_runtime_source_revision': '634d223',
            'scope': 'new evidence only; old source/resource/geometry references remain in reachable base Git'}


def verify():
    """Read every stored payload and enforce both required and exact expected path sets."""
    manifest = json.loads((EVIDENCE / 'manifest.json').read_text())
    actual = {str(p.relative_to(EVIDENCE)) for p in EVIDENCE.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    if actual != set(manifest['expected_paths']) or required_paths() - actual:
        raise RuntimeError('expected evidence path set differs')
    entries = manifest['entries']
    if {row['path'] for row in entries} != actual or len(entries) != len(actual):
        raise RuntimeError('manifest entry coverage differs')
    for row in entries:
        path = EVIDENCE / row['path']
        if identity(path) != {k: row[k] for k in ['bytes', 'sha256']}:
            raise RuntimeError('stored bytes differ: ' + row['path'])
        if 'decoded' in row:
            decoded = gzip.decompress(path.read_bytes())
            if {'bytes': len(decoded), 'sha256': hashlib.sha256(decoded).hexdigest()} != row['decoded']:
                raise RuntimeError('decoded bytes differ: ' + row['path'])
    return {'paths': len(actual), 'required_paths': len(required_paths()), 'stored_and_decoded_hashes_match': True}


def main():
    """Build once before freeze, or verify readback without mutating the package."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'verify'])
    args = parser.parse_args()
    if args.mode == 'build':
        save(EVIDENCE / 'manifest.json', build())
    print(json.dumps(verify()))


if __name__ == '__main__':
    raise SystemExit(main())
