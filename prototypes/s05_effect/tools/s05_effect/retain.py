#!/usr/bin/env python3
"""Retain the explicit stopped S05 attempt payload set and verify stored readback."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = 'ef730df936b5b159f0894033f5d01e2b7124386c'
OUT = ROOT / 'docs/spikes/s05-saved-presentation-evidence'
RUNS = [Path('/tmp/s05-author-56eb6b28-run0' + str(i)) for i in [1, 2, 3]]
SESSION = Path('/home/regner/.codex/sessions/2026/10/08/'
               'rollout-2026-10-08T09-37-15-01a11aa8-d994-7832-989e-29f10b183857.jsonl')


def digest(data):
    """Bind retained raw source bytes to stored decoded readback."""
    return hashlib.sha256(data).hexdigest()


def main():
    """Copy exact expected logs/calls and preserve limitations rather than fabricating streams."""
    expected = {}
    fixed = ['commands-before-engine.json', 'lifecycle.json', 'context.gd',
             'observe.stdout', 'observe.stderr', 'observe.engine.log']
    for index, run in enumerate(RUNS, 1):
        names = fixed + (['initialize.stdout', 'initialize.stderr', 'initialize.engine.log',
                          'inputs.json', 'poststop-inputs.json', 'connector.stderr',
                          'client.mjs', 'tool-inventory.json', 'call.py'] if index == 1 else [])
        if index == 3:
            names += ['connector.stderr', 'client.mjs']
        calls = 8 if index == 1 else 2 if index == 3 else 0
        for sequence in range(1, calls + 1):
            names.extend(['call-%03d.%s.json' % (sequence, kind)
                          for kind in ['request', 'response']])
        for name in names:
            expected['run%02d/' % index + name] = run / name
    expected['offline-registry-gate.json'] = Path('/tmp/s05-run03-offline.json')
    for name in ['presentation', 'match', 'proof', 'editor_probe']:
        expected['unexecuted-drafts/' + name + '.gd.draft'] = RUNS[0] / (name + '.gd.draft')
    expected['private-saved-root/explosion.tscn'] = (
        RUNS[0] / 'project/tests/fixtures/s05_effect/explosion.tscn')
    expected['private-generated-import/s05_explosion_carrier.glb.import'] = (
        RUNS[0] / 'project/art/models/spikes/s05_explosion_carrier.glb.import')
    manifest = []
    for relative, source in sorted(expected.items()):
        data = source.read_bytes()
        target = OUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise RuntimeError('never overwrite preliminary payload: ' + relative)
        target.write_bytes(data)
        assert target.read_bytes() == data
        manifest.append({'path': relative, 'source': str(source),
                         'bytes': len(data), 'sha256': digest(data)})
    grants = []
    recovered = []
    for line in SESSION.open():
        item = json.loads(line)
        value = item.get('payload', {})
        if value.get('type') == 'message' and value.get('role') == 'user':
            texts = [part.get('text', '') for part in value.get('content', [])]
            text = '\n'.join(texts)
            if 'ROOT' in text:
                grants.append(text)
        if value.get('type') == 'custom_tool_call_output':
            for part in value.get('output', []):
                text = part.get('text', '')
                try:
                    decoded = json.loads(text)
                except (ValueError, TypeError):
                    continue
                output = decoded.get('output', '') if isinstance(decoded, dict) else ''
                if output.startswith('{"ready": true') or output.startswith('{"STOP":'):
                    recovered.append({'tool_result': decoded, 'original_result_text': text})
    artifacts = {'raw-root-requirements-and-grants.json': grants,
                 'recovered-supervisor-tool-results.json': recovered,
                 'expected-payload-set.json': sorted(expected), 'payload-manifest.json': manifest}
    for name, value in artifacts.items():
        (OUT / name).write_text(json.dumps(value, indent=2) + '\n')
    assert set(expected) == {row['path'] for row in manifest}
    assert len(recovered) >= 4, 'missing actual supervisor ready/stop tool results'
    assert len(grants) >= 4, 'missing root requirements/continuation grants'
    originals = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE],
                                        cwd=ROOT, text=True).splitlines()
    prefixes = ('art/', 'tests/', 'addons/', '.agents/', '.codex/', 'tools/',
                'project.godot', 'mise.toml', 'gdstyle.toml', '.gdstyle-version', 'AGENTS.md')
    checked = []
    for name in originals:
        if name.startswith(prefixes):
            actual = (ROOT / name).read_bytes()
            before = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
            assert actual == before, 'original changed: ' + name
            checked.append({'path': name, 'bytes': len(actual), 'sha256': digest(actual)})
    (OUT / 'original-bytes.json').write_text(json.dumps(checked, indent=2) + '\n')
    print(json.dumps({'payloads': len(manifest), 'originals_checked': len(checked),
                      'supervisor_results_recovered': len(recovered), 'root_grants': len(grants)}))


if __name__ == '__main__':
    main()
