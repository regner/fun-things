"""Exact original-file preservation and new saved inheritance/UID contract checks, without Godot."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = '233493abc7d2e3c106fb620105cfb766f542813b'
ALLOWED = {'TODO.md', 'docs/spikes/s07-run-cards.md'}


def check(base=BASE):
    """Compare all immutable originals and resolve every new saved UID/path and inheritance link."""
    lines = subprocess.check_output(['git', 'ls-tree', '-r', base], cwd=ROOT, text=True).splitlines()
    failures, originals = [], []
    for line in lines:
        metadata, name = line.split('\t', 1)
        mode, kind, blob = metadata.split()
        if kind != 'blob':
            failures.append('unexpected original type: ' + name)
            continue
        path = ROOT / name
        data = path.read_bytes() if path.is_file() else b''
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        same = actual == blob and path.exists()
        if not same and name not in ALLOWED:
            failures.append('original changed: ' + name)
        originals.append({'path': name, 'git_blob': blob, 'bytes': len(data),
                          'sha256': hashlib.sha256(data).hexdigest(), 'unchanged': same})
    scene = ROOT / 'tests/fixtures/s07_driver/intersection.tscn'
    text = scene.read_text()
    if '[node name="S06"' not in text or text.count('[node ') != 1 or 'instance=ExtResource("1")' not in text:
        failures.append('must inherit existing composition without authored new hierarchy/placement')
    if 'ArrayMesh' in text or 'transform =' in text or 'position =' in text:
        failures.append('new geometry/placement override')
    identities = re.findall(r'uid="(uid://[a-z0-9]+)"', text)
    if len(identities) != 3 or 'unique_id=' not in text:
        failures.append('genuine saved scene/dependency/node IDs missing')
    for uid, name in re.findall(r'\[ext_resource [^\n]*uid="([^"]+)" path="res://([^"]+)"', text):
        path = ROOT / name
        saved_uid = path.with_suffix(path.suffix + '.uid').read_text().strip() if path.suffix == '.gd' else re.search(r'uid="([^"]+)"', path.read_text()).group(1)
        if uid != saved_uid:
            failures.append('dependency UID mismatch: ' + name)
    for name in ['fixture', 'run', 'guards']:
        script = ROOT / f'tests/fixtures/s07_driver/{name}.gd'
        if not re.fullmatch(r'uid://[a-z0-9]+\n?', script.with_suffix('.gd.uid').read_text()):
            failures.append('missing script sidecar: ' + name)
    return {'base': base, 'failures': failures, 'originals': originals,
            'allowed_original_doc_deltas': sorted(ALLOWED), 'saved_scene_ids': identities}


def main():
    """Persist full preservation/readback expectations and fail on any unowned changed byte."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--base', default=BASE)
    args = parser.parse_args()
    result = check(args.base)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'original_files': len(result['originals']), 'failures': result['failures']}))
    return bool(result['failures'])


if __name__ == '__main__':
    raise SystemExit(main())
