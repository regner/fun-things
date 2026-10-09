"""Assert bounded batch-two source retention, saved engine evidence and process equivalence."""
import hashlib
import json
from pathlib import Path
import re
import statistics
import struct

from fixture_paths import assert_reviewed_roundtrips, current_path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/assets/production/batch_02-evidence'
RAW = OUT / 'transport'
IDS = ['city_planting_03', 'city_planting_04', 'city_planting_05',
       'city_roof_details_01', 'city_roof_details_02', 'city_shop_fittings_01']


def receipts(name):
    return [json.loads(line) for line in (RAW / name).read_text().splitlines()]


payload_count = 0
for asset in IDS:
    manifest = json.loads((ROOT / f'docs/assets/production/{asset}-evidence/manifest.json').read_text())
    rows = manifest['files']
    for row in rows:
        data = (ROOT / row['path']).read_bytes()
        assert len(data) == row['bytes']
        assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
    payload_count += len(rows)
expected = {
    'city_planting_03': ([-.543030, 0, -.356221], [.540500, .670000, .334672]),
    'city_planting_04_compact': ([-.908597, 0, -.953385], [1.089992, 3.596365, .894191]),
    'city_planting_04_broad': ([-1.288243, 0, -1.238169], [1.483806, 3.317199, 1.203524]),
    'city_planting_05_short_tuft': ([-.28, 0, -.21], [.28, .26, .21]),
    'city_planting_05_spreading_clump': ([-.5, 0, -.31], [.5, .2, .31]),
    'city_roof_details_01': ([-1.3, 0, -.8], [1.3, .76, .8]),
    'city_roof_details_02': ([-1.6, 0, -1.1], [1.6, 1.55, 1.1]),
    'city_shop_fittings_01': ([-1.6, -.42, -1.1], [1.6, .24, 0]),
}
bounds_rows = []
uid_count = 0
for name in ['audit-results.jsonl', 'source-uid-results.jsonl']:
    for row in receipts(name):
        value = row['result'].get('result', {})
        if value.get('method') == 'register_uids':
            for item in value['result']:
                assert item['was_registered'] and item['path'] == item['resolved']
                path = current_path(ROOT, item['path'])
                identity_file = path if path.suffix == '.tscn' else Path(str(path) + '.import')
                identity = re.search(r'uid="([^"]+)"', identity_file.read_text()).group(1)
                assert identity == item['uid']
                uid_count += 1
        if value.get('method') != 'inspect_prefab':
            continue
        value = value['result']
        asset = Path(value['prefab']).stem
        rows = value['mesh_rows']
        assert rows and all(m['resource'].startswith(value['model'] + '::') for m in rows)
        assert 'O: (0.0, 0.0, 0.0)' in value['model_transform']
        lo = [min(m['min'][a] for m in rows) for a in range(3)]
        hi = [max(m['min'][a] + m['size'][a] for m in rows) for a in range(3)]
        assert all(abs(x - y) < .001 for actual, target in zip((lo, hi), expected[asset])
                   for x, y in zip(actual, target)), asset
        assert all(s['transparency'] == 0 for m in rows for s in m['surfaces'])
        bounds_rows.append({'asset': asset, 'min': lo, 'max': hi,
                            'linked_model': value['model'], 'surfaces': sum(len(m['surfaces']) for m in rows)})
assert len(bounds_rows) == 8 and uid_count == 21
roundtrip = json.loads((RAW / 'roundtrip-before.json').read_text())
assert_reviewed_roundtrips(ROOT, roundtrip)
observations = []
for name in ['final-native-probe-results.jsonl', 'repeat-final-probe-results.jsonl']:
    value = receipts(name)[0]['result']['result']['result']
    assert value['passed'] and len(value['frame_samples']) == 120
    samples = value['frame_samples'][-60:]
    observations.append({'receipt': name, 'query_batch_usec': value['query_batch_usec'],
                         'motion': value['motion'], 'aim_hit': value['aim_hit'],
                         'medians_last_60': {k: statistics.median(s[k] for s in samples)
                                            for k in samples[0]}})
placement = receipts('repeat-final-probe-results.jsonl')[1]['result']['result']['result']
assert placement['passed'] and placement['tree_surround_ground_datum_error_m'] < .002
process_rows = []
for label in ['process_a', 'process_b']:
    execution = json.loads((OUT / f'processes/{label}.execution.json').read_text())
    assert execution['exit_code'] == 0
    assert not (OUT / f'processes/{label}.stderr.log').read_text()
    line = next(s for s in (OUT / f'processes/{label}.stdout.log').read_text().splitlines()
                if s.startswith('BATCH02_PROCESS '))
    value = json.loads(line.removeprefix('BATCH02_PROCESS '))
    assert value['passed'] and value['pid'] == execution['pid']
    process_rows.append(value)
assert process_rows[0]['pid'] != process_rows[1]['pid']
assert process_rows[0]['rows'] == process_rows[1]['rows']
assert process_rows[0]['aim_hit'] == process_rows[1]['aim_hit']
calibration = json.loads((OUT / 'calibration/tree-roof-measurements.json').read_text())
assert len(calibration['assets']) == 4 and calibration['scale_length'] == 1
for row in calibration['assets']:
    digest = hashlib.sha256((ROOT / row['source']).read_bytes()).hexdigest()
    assert digest == row['source_sha256_before'] == row['source_sha256_after']
    assert hashlib.sha256((ROOT / row['glb']).read_bytes()).hexdigest() == row['glb_sha256']
    assert row['reference_dimensions_m'] == [1, 1, 1]
    assert row['instance_scale'] == [1, 1, 1] and row['instance_rotation_rad'] == [0, 0, 0]
    assert row['front_vector_blender'] == [0, 1, 0] and row['up_vector_blender'] == [0, 0, 1]
for name in ['gameplay.png', 'mounting-close.png', 'roof-close.png', 'repetition.png']:
    header = (OUT / name).read_bytes()[:24]
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", header[16:24]) == (1280, 800)
summary = {'passed': True, 'source_payload_count': payload_count,
           'source_candidate': '5e94cc0ea4155219285db49c64b5728e0882b093',
           'bounds': bounds_rows, 'uid_resolution_count': uid_count,
           'byte_stable_roundtrips': len(roundtrip), 'observations': observations,
           'placement': placement, 'separate_process_equivalence': process_rows,
           'scope': 'Imported static props and bounded desktop/command replay; no network/device/world acceptance'}
(OUT / 'validation-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
