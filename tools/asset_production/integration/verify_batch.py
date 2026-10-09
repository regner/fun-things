"""Bounded readback of batch-one immutable sources and actual editor/runtime receipts."""
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/assets/production/batch_01-evidence'
RAW = OUT / 'transport'


def readback(index):
    rows = json.loads(index.read_text())
    rows = rows['files'] if isinstance(rows, dict) else rows
    for row in rows:
        payload = (ROOT / row['path']).read_bytes()
        assert len(payload) == row['bytes'], row['path']
        assert hashlib.sha256(payload).hexdigest() == row['sha256'], row['path']
    return len(rows)


def receipts(name):
    return [json.loads(line) for line in (RAW / name).read_text().splitlines()]


source_count = readback(ROOT / 'docs/reviews/asset-production/batch_01/candidate-scope-file-index.json')
review_count = readback(ROOT / 'docs/reviews/asset-production/batch_01/artifact-index.json')
audit = receipts('batch-final-audit-results.jsonl')
expected = {
    'city_lights_01': ([-.36, 0, -1.4], [.36, 6.2, .21]),
    'city_lights_01_cool': ([-.36, 0, -1.4], [.36, 6.2, .21]),
    'city_lights_02': ([-.36, 0, -.36], [.36, 3, .36]),
    'city_lights_02_cool': ([-.36, 0, -.36], [.36, 3, .36]),
    'city_lights_04': ([-.32, -.23, -.71], [.32, .305, 0]),
    'city_lights_04_cool': ([-.32, -.23, -.71], [.32, .305, 0]),
    'city_sign_supports_01': ([-.7, -.5, -.1], [.7, .5, 0]),
    'city_planting_01': ([-1.2, 0, -.45], [1.2, .6, .45]),
    'city_planting_02': ([-.9, 0, -.9], [.9, .48, .9]),
}
bounds = []
for row in audit:
    result = row['result'].get('result', {})
    if result.get('method') == 'inspect_prefab':
        value = result['result']
        asset = Path(value['prefab']).stem
        mesh_rows = value['mesh_rows']
        assert mesh_rows and all(m['resource'].startswith(value['model'] + '::') for m in mesh_rows)
        assert value['model_transform'] == '[X: (1.0, 0.0, 0.0), Y: (0.0, 1.0, 0.0), Z: (0.0, 0.0, 1.0), O: (0.0, 0.0, 0.0)]'
        lo = [min(m['min'][a] for m in mesh_rows) for a in range(3)]
        hi = [max(m['min'][a] + m['size'][a] for m in mesh_rows) for a in range(3)]
        assert all(abs(x - y) < .001 for actual, target in zip((lo, hi), expected[asset])
                   for x, y in zip(actual, target)), asset
        bounds.append({'id': asset, 'min': lo, 'max': hi, 'linked_model': value['model']})
    if result.get('method') == 'register_uids':
        assert all(v['path'] == v['resolved'] and v['was_registered'] for v in result['result'])
assert len(bounds) == 9
roundtrip = json.loads((RAW / 'final-before-roundtrip.json').read_text())
assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in roundtrip.items())
observations = []
for name in ['batch-final-styled-probe-results.jsonl', 'batch-repeat-probe-results.jsonl']:
    value = receipts(name)[0]['result']['result']['result']
    assert value['passed'] and value['motion_outcomes']['planter_stopped']
    assert value['motion_outcomes']['bypass_crossed']
    samples = value['render_samples'][-60:]
    observations.append({'receipt': name, 'query_batch_usec': value['query_batch_usec'],
                         'motion': value['motion_outcomes'],
                         'medians_last_60': {k: statistics.median(s[k] for s in samples)
                                             for k in samples[0]}})
calibration = json.loads((OUT / 'calibration/measurements.json').read_text())
assert calibration['scale_length'] == 1 and len(calibration['assets']) == 5
for row in calibration['assets']:
    digest = hashlib.sha256((ROOT / row['source']).read_bytes()).hexdigest()
    assert digest == row['source_sha256_before'] == row['source_sha256_after']
    assert row['instance_scale'] == [1, 1, 1] and row['instance_rotation_rad'] == [0, 0, 0]
    assert row['reference_dimensions_m'] == [1, 1, 1]
summary = {'passed': True, 'source_scope_readback_count': source_count,
           'review_artifact_readback_count': review_count, 'source_candidate':
           '390377dc6530e101eddcbf38b2946a1b235137c7', 'prefab_bounds': bounds,
           'stable_roundtrip_count': len(roundtrip), 'observations': observations,
           'scope': 'Saved engine/desktop standalone observation; no device/network/world acceptance'}
(OUT / 'validation-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
