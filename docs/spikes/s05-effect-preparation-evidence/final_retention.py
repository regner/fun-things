"""Preserve the complete accepted-main delta and verify the declared final expected set."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD_BASE = '122978243dba25b3fb5d8d90fc50ffb1a468ecf5'
BASE = '0c84f01f2a0c817a5c6851a3a360e193a5f846d8'
OLD_CANDIDATE = 'c36db1704dc5a326ca2132a3d118706a41887e84'
REBASED_CANDIDATE = 'cc719cf588c6a3c30b28d623e15e96d3d3e03485'
LINK = ('  [Provisional source preparation](docs/spikes/s05-effect-preparation.md) adds one\n'
        '  provisional new Blender carrier/explicit GLB only; Godot import, saved presentation\n'
        '  and actual eight-effect drawable/saturation/live-versus-hydrated gates remain pending.\n')


def git(*arguments):
    """Read exact immutable Git bytes; no index/ref/working-tree mutation."""
    return subprocess.run(['git', *arguments], cwd=ROOT, capture_output=True, check=True).stdout


entries = [line.split('\t', 1) for line in
           git('ls-tree', '-r', '--format=%(objectname)\t%(path)', BASE).decode().splitlines()]
batch = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                       input=('\n'.join(sha for sha, name in entries) + '\n').encode(),
                       capture_output=True, check=True).stdout
offset, matches = 0, 0
for sha, name in entries:
    end = batch.index(b'\n', offset)
    header = batch[offset:end].decode().split()
    assert header[0] == sha and header[1] == 'blob'
    length = int(header[2])
    old = batch[end + 1:end + 1 + length]
    offset = end + 1 + length + 1
    current = (ROOT / name).read_bytes()
    if name == 'TODO.md':
        assert current.count(LINK.encode()) == 1
        assert current.replace(LINK.encode(), b'', 1) == old
    else:
        assert current == old, name
        matches += 1
assert offset == len(batch)
delta_paths = git('diff', '--name-only', OLD_BASE, BASE).decode().splitlines()
delta = []
for name in delta_paths:
    raw = git('show', BASE + ':' + name)
    if name.endswith('.json'):
        json.loads(raw)
    delta.append(dict(path=name, blob=git('rev-parse', BASE + ':' + name).decode().strip(),
                      bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                      preserved_byte_equal_except_scoped_todo_link=True))
rebase = dict(original_base=OLD_BASE, original_candidate=OLD_CANDIDATE,
              accepted_base=BASE, rebased_candidate=REBASED_CANDIDATE,
              accepted_delta=delta, accepted_tree=git('rev-parse', BASE + '^{tree}').decode().strip(),
              source_sha256_unchanged=hashlib.sha256((ROOT / 'art/source/models/spikes/s05_explosion_carrier.blend').read_bytes()).hexdigest(),
              export_sha256_unchanged=hashlib.sha256((ROOT / 'art/models/spikes/s05_explosion_carrier.glb').read_bytes()).hexdigest())
(HERE / 'rebase-receipt.json').write_text(json.dumps(rebase, indent=2) + '\n')
preservation = dict(base=BASE, original_paths=len(entries), raw_byte_identical=matches,
                    only_original_change='TODO.md', exact_scoped_addition=LINK,
                    master_tasks_parallel_readiness_watermark_preserved=True,
                    checks='PASS')
(HERE / 'final-preservation.json').write_text(json.dumps(preservation, indent=2) + '\n')
prefix = 'docs/spikes/s05-effect-preparation-evidence/'
original = json.loads((HERE / 'manifest.json').read_text())
new_names = ['manifest.json', 'godot_help.py', 'godot-help.stdout', 'godot-help.stderr',
             'godot-help-command.json', 'final_retention.py', 'rebase-receipt.json',
             'final-preservation.json']
expected = set(original['expected_set']) | {prefix + name for name in new_names}
actual = {'TODO.md', 'docs/spikes/s05-effect-preparation.md',
          'art/source/models/spikes/s05_explosion_carrier.blend',
          'art/models/spikes/s05_explosion_carrier.glb'}
actual |= {str(p.relative_to(ROOT)) for p in HERE.rglob('*')
           if p.is_file() and p.name != 'final-manifest.json'}
assert actual == expected, dict(missing=sorted(expected - actual), extra=sorted(actual - expected))
artifacts = []
for name in sorted(expected):
    raw = (ROOT / name).read_bytes()
    artifacts.append(dict(path=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
receipt = dict(schema=1, base=BASE, expected_set=sorted(expected), artifacts=artifacts,
               excludes_only_self=prefix + 'final-manifest.json',
               old_receipts='Initial manifest/preservation keep their actual historical scope; current bytes bound here')
(HERE / 'final-manifest.json').write_text(json.dumps(receipt, indent=2) + '\n')
readback = json.loads((HERE / 'final-manifest.json').read_text())
assert readback == receipt
for item in readback['artifacts']:
    raw = (ROOT / item['path']).read_bytes()
    assert len(raw) == item['bytes'] and hashlib.sha256(raw).hexdigest() == item['sha256']
print(json.dumps(dict(checks='PASS', accepted_delta_paths=len(delta), preserved_originals=matches,
                     expected_artifacts=len(artifacts),
                     manifest_sha256=hashlib.sha256((HERE / 'final-manifest.json').read_bytes()).hexdigest())))
