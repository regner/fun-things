"""Validate immutable producer corrections, linked saved models and bounded engine evidence."""
import hashlib
import json
from pathlib import Path
import re
import statistics
import struct

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/assets/production/batch_03-evidence'
RAW = OUT / 'transport'
IDS = ['city_shop_fittings_02', 'city_shop_fittings_03', 'city_shop_fittings_05',
       'city_shop_fittings_06', 'city_shop_fittings_07', 'city_shop_fittings_08',
       'city_small_shop_shells_01']


def receipts(name):
    return [json.loads(s) for s in (RAW / name).read_text().splitlines()]


payloads = 0
for asset in IDS:
    manifest = json.loads((ROOT / f'docs/assets/production/{asset}-evidence/manifest.json').read_text())
    rows = manifest['files'] if isinstance(manifest, dict) else manifest
    for row in rows:
        data = (ROOT / row['path']).read_bytes()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    payloads += len(rows)
# Independent initial bounds remain literal expectations: corrections preserve envelopes.
initial = json.loads((ROOT / 'docs/reviews/asset-production/batch_03/initial/glb-audit.json').read_text())
expected = {row['name']: row['bounds_godot'] for row in initial}
models = []
uids = []
for row in receipts('audit-results.jsonl'):
    value = row['result'].get('result', {})
    if value.get('method') == 'register_uids':
        for identity in value['result']:
            assert identity['was_registered'] and identity['path'] == identity['resolved']
            p = ROOT / identity['path'].removeprefix('res://')
            data = p.read_text() if p.suffix == '.tscn' else Path(str(p) + '.import').read_text()
            assert re.search(r'uid="([^"]+)"', data).group(1) == identity['uid']
            uids.append(identity)
    if value.get('method') != 'inspect_prefab':
        continue
    value = value['result']
    name = Path(value['prefab']).stem
    mesh_rows = value['mesh_rows']
    assert all(m['resource'].startswith(value['model'] + '::') for m in mesh_rows)
    lo = [min(m['min'][a] for m in mesh_rows) for a in range(3)]
    hi = [max(m['min'][a] + m['size'][a] for m in mesh_rows) for a in range(3)]
    assert all(abs(a-b) < .001 for values, targets in zip((lo, hi), expected[name])
               for a, b in zip(values, targets)), name
    assert 'O: (0.0, 0.0, 0.0)' in value['model_transform']
    assert all(s['cull_mode'] == 0 and s['transparency'] == 0
               for m in mesh_rows for s in m['surfaces'])
    models.append({'name': name, 'bounds': [lo, hi], 'source': value['model'],
                   'material_count': sum(len(m['surfaces']) for m in mesh_rows)})
assert len(models) == 9 and len(uids) == 25
before = json.loads((OUT / 'roundtrip-stable-before.json').read_text())
assert len(before) == 15
for path, digest in before.items():
    assert hashlib.sha256((ROOT / path.removeprefix('res://')).read_bytes()).hexdigest() == digest
observations = []
for label in ['native-final-recapture', 'repeat-probe']:
    values = receipts(label + '-results.jsonl')
    motion = values[0]['result']['result']['result']
    assembly = values[1]['result']['result']['result']
    assert motion['passed'] and assembly['passed'] and len(motion['samples']) == 120
    samples = motion['samples'][-60:]
    observations.append({'label': label, 'motion': motion['motion'], 'aim_hit': motion['aim_hit'],
       'query_usec': motion['query_usec'], 'assembly': assembly,
       'medians_last_60': {k: statistics.median(s[k] for s in samples) for k in samples[0]}})
processes = []
for label in ['process_a', 'process_b']:
    execution = json.loads((OUT / f'processes/{label}.execution.json').read_text())
    assert execution['exit_code'] == 0
    assert not (OUT / f'processes/{label}.stderr.log').read_text()
    line = next(s for s in (OUT / f'processes/{label}.stdout.log').read_text().splitlines()
                if s.startswith('BATCH03_PROCESS '))
    value = json.loads(line.removeprefix('BATCH03_PROCESS '))
    assert value['passed'] and value['pid'] == execution['pid']
    processes.append(value)
assert all(len(value['rows']) == 6 for value in processes)
upper_fit = receipts('native-with-upper-fit-results.jsonl')[1]['result']['result']['result']['upper_fit']
assert upper_fit['passed'] and upper_fit['rear_vertices'] == 260
assert upper_fit['minimum_side_head_bottom_gap_m'] >= .018
assert processes[0]['pid'] != processes[1]['pid'] and processes[0]['rows'] == processes[1]['rows']
assert processes[0]['aim_hit'] == processes[1]['aim_hit']
for name in ['gameplay.png', 'frontage-close.png', 'repetition.png']:
    header = (OUT / name).read_bytes()[:24]
    assert header[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', header[16:24]) == (1280, 800)
# Explicit future art faces survive import with exact material-slot ownership.
by_name = {r['name']: r for r in models}
raw = [r['result']['result']['result'] for r in receipts('audit-results.jsonl')
       if r['result'].get('result', {}).get('method') == 'inspect_prefab']
fascia = next(m for r in raw if Path(r['prefab']).stem == 'city_shop_fittings_02'
              for m in r['mesh_rows'] if m['node'] == 'fascia_artwork_carrier')
assert fascia['surfaces'][0]['name'] == 'fascia_artwork_face'
for name, material in [('face_positive_x','blade_artwork_positive_x'),
                       ('face_negative_x','blade_artwork_negative_x')]:
    face = next(m for r in raw if Path(r['prefab']).stem == 'city_shop_fittings_08'
                for m in r['mesh_rows'] if m['node'] == name)
    assert face['surfaces'][0]['name'] == material
summary = {'passed': True, 'original_source': '028775618c4493ca672646e6e37fdc3c83e0e313',
    'corrected_source': '4f11c54d4abf4aa77813a1cf8bcf885fd040b7c9', 'producer_payloads': payloads,
    'linked_variants': models, 'registered_identities': len(uids), 'byte_stable_roundtrips': len(before),
    'observations': observations, 'separate_processes': processes, 'upper_fit': upper_fit,
    'scope': 'bounded static engine candidate; reviewer pending, no world/device/transport acceptance'}
(OUT / 'validation-summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
