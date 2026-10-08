"""Record scoped original preservation and a complete expected new-artifact byte manifest."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = '122978243dba25b3fb5d8d90fc50ffb1a468ecf5'
changed = subprocess.run(['git', 'diff', '--name-only', BASE], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.splitlines()
assert changed == ['TODO.md'], changed
tree = subprocess.run(['git', 'ls-tree', '-r', '--format=%(objectname)\t%(path)', BASE],
                      cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
entries = [line.split('\t', 1) for line in tree]
batch = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                       input=('\n'.join(sha for sha, name in entries) + '\n').encode(),
                       capture_output=True, check=True).stdout
offset, matches, differences = 0, 0, []
for sha, name in entries:
    end = batch.index(b'\n', offset)
    header = batch[offset:end].decode().split()
    assert header[0] == sha and header[1] == 'blob'
    length = int(header[2])
    original = batch[end + 1:end + 1 + length]
    offset = end + 1 + length + 1
    path = ROOT / name
    current = path.read_bytes()
    if current == original:
        matches += 1
    else:
        differences.append(dict(path=name, base_blob=sha, base_bytes=len(original),
                                current_bytes=len(current),
                                base_sha256=hashlib.sha256(original).hexdigest(),
                                current_sha256=hashlib.sha256(current).hexdigest()))
        assert name == 'TODO.md', name
assert offset == len(batch)
preservation = dict(base=BASE, base_tree=subprocess.run(['git', 'rev-parse', BASE + '^{tree}'],
                    cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip(),
                    original_tracked_paths=len(entries), raw_byte_identical=matches,
                    raw_differences=differences, git_changed_originals=changed,
                    explanation='Only the S05 TODO link changes an original path; all other original files match accepted base bytes, including vendor files.')
(HERE / 'preservation.json').write_text(json.dumps(preservation, indent=2) + '\n')
requirements = []
for name in ('AGENTS.md', 'docs/spikes/s05-evidence/raw-s05-todo.md', 'docs/spikes/s05-contracts.md',
             'docs/spikes/s05.md', 'docs/spikes/s02-drawability.md', 'docs/art-direction.md',
             'docs/concepts/p0-04/g-weapons-effects.png', 'docs/assets.md', 'docs/world-layout.md',
             'docs/scene-structure.md', '.agents/skills/art-review/SKILL.md',
             '.agents/skills/godot-mcp-toolkit/SKILL.md'):
    raw = subprocess.run(['git', 'show', BASE + ':' + name], cwd=ROOT,
                         capture_output=True, check=True).stdout
    requirements.append(dict(path=name, revision=BASE, bytes=len(raw),
                             sha256=hashlib.sha256(raw).hexdigest(),
                             blob=subprocess.run(['git', 'rev-parse', BASE + ':' + name], cwd=ROOT,
                                  capture_output=True, text=True, check=True).stdout.strip()))
(HERE / 'requirements.json').write_text(json.dumps(requirements, indent=2) + '\n')
paths = [ROOT / 'TODO.md', ROOT / 'docs/spikes/s05-effect-preparation.md',
         ROOT / 'art/source/models/spikes/s05_explosion_carrier.blend',
         ROOT / 'art/models/spikes/s05_explosion_carrier.glb']
paths.extend(sorted(p for p in HERE.rglob('*') if p.is_file() and p.name != 'manifest.json'))
manifest = []
for path in paths:
    raw = path.read_bytes()
    manifest.append(dict(path=str(path.relative_to(ROOT)), bytes=len(raw),
                         sha256=hashlib.sha256(raw).hexdigest()))
document = dict(schema=1, base=BASE, expected_set=[item['path'] for item in manifest],
                artifacts=manifest, excludes_only_self='docs/spikes/s05-effect-preparation-evidence/manifest.json')
(HERE / 'manifest.json').write_text(json.dumps(document, indent=2) + '\n')
readback = json.loads((HERE / 'manifest.json').read_text())
assert readback == document
assert len(set(readback['expected_set'])) == len(readback['artifacts'])
for item in readback['artifacts']:
    raw = (ROOT / item['path']).read_bytes()
    assert len(raw) == item['bytes'] and hashlib.sha256(raw).hexdigest() == item['sha256']
print(json.dumps(dict(checks='PASS', original_paths=len(entries),
                     raw_differences=len(differences), expected_artifact_count=len(manifest),
                     manifest_sha256=hashlib.sha256((HERE / 'manifest.json').read_bytes()).hexdigest())))
