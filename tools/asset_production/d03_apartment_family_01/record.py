"""Generate/check the lean manifest last and require all final receipt dependencies to match."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
MANIFEST = EVIDENCE / "manifest.json"
HANDOFF = ROOT / f"docs/assets/production/{NID}.md"


def receipt(path):
    """Hash a final payload exactly as retained in validation and the manifest."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


validation = json.loads((EVIDENCE / 'validation.json').read_text())
assert validation['ok'] and validation['godot']['ok']
assert validation['godot']['roundtrip']['byte_stable']
checks = [validation['prefab'], *validation['linked_prefabs']]
for dependency in validation['dependencies']:
    checks.extend(dependency[key] for key in ('source', 'export', 'import'))
for expected in checks:
    assert receipt(ROOT / expected['path']) == expected, expected['path']
assert validation['prefab']['sha256'] in HANDOFF.read_text()
assert str(validation['prefab']['bytes']) in HANDOFF.read_text()
assert validation['prefab']['sha256'] == validation['godot']['roundtrip']['normalized_sha256']
paths = {HANDOFF, ROOT / validation['prefab']['path']}
for directory in (EVIDENCE, ROOT / f'tools/asset_production/{NID}'):
    paths.update(p for p in directory.rglob('*') if p.is_file() and p != MANIFEST)
assert not any(p.suffix in ('.pyc', '.blend1') for p in paths)
report = {'asset_id': 'd03_apartment_family.01',
          'scope': 'Every produced payload except this manifest; dependencies pinned in validation',
          'files': [receipt(p) for p in sorted(paths)]}
if '--check' in sys.argv:
    assert json.loads(MANIFEST.read_text()) == report
    print(f"PASS: {len(paths)} produced payloads and {len(checks)} dependency/scene receipts")
else:
    MANIFEST.write_text(json.dumps(report, indent=2) + '\n', newline='\n')
    print(f"Recorded {len(paths)} produced payloads")
