#!/usr/bin/env python3
"""Check exact saved-resource preservation and independent S05 draw/ENet expectations."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = '48aef3dbd133876743f504f94a1b788a26d5638f'


def save(path, value):
    """Retain explicit expectations and complete actual checked path sets."""
    path.write_text(json.dumps(value, indent=2) + '\n')


def originals(base=BASE):
    """Derive the entire immutable original tree from Git rather than a selected manifest."""
    tree = subprocess.check_output(['git', 'ls-tree', '-rz', base], cwd=ROOT)
    ledger = []
    for entry in tree.split(b'\0'):
        if not entry:
            continue
        metadata, name = entry.split(b'\t')
        mode, kind, oid = metadata.decode().split()
        name = name.decode()
        if name == 'TODO.md':
            continue  # Only the owned block is allowed to change; its diff is checked below.
        path = ROOT / name
        data = str(path.readlink()).encode() if mode == '120000' else path.read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if actual != oid:
            raise AssertionError('original byte change: ' + name)
        ledger.append({'path': name, 'git_blob': oid, 'bytes': len(data),
                       'sha256': hashlib.sha256(data).hexdigest()})
    before = subprocess.check_output(['git', 'show', base + ':TODO.md'], cwd=ROOT, text=True)
    after = (ROOT / 'TODO.md').read_text()
    start, end = before.index('- [ ] **S05'), before.index('- [ ] **S06')
    assert after[:after.index('- [ ] **S05')] == before[:start]
    assert after[after.index('- [ ] **S06'):] == before[end:]
    return ledger


def uid(path):
    """Resolve only saved UID owners, never engine-generated identities in code."""
    if path.suffix == '.gd':
        return Path(str(path) + '.uid').read_text().strip()
    if path.suffix == '.glb':
        path = Path(str(path) + '.import')
    return re.search(r'uid="(uid://[^\"]+)"', path.read_text())[1]


def resources():
    """Check authored camera and unchanged inherited placement through literal contracts."""
    folder = ROOT / 'tests/fixtures/s05_draw'
    record = {}
    for name in ['camera', 'burst']:
        path = folder / (name + '.tscn')
        source = path.read_text()
        ids = re.findall(r'^\[node[^\n]*unique_id=(\d+)', source, re.M)
        assert ids and len(ids) == len(set(ids)), 'saved node identities'
        assert not any(word in source for word in ['ArrayMesh', 'PrimitiveMesh', 'CSG'])
        for identity, dependency in re.findall(r'uid="([^\"]+)" path="res://([^\"]+)"', source):
            assert identity == uid(ROOT / dependency), 'UID/path mismatch'
        record[name] = {'uid': uid(path), 'node_ids': ids,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    camera = (folder / 'camera.tscn').read_text()
    assert camera.count('[node ') == 4 and 'type="Camera3D"' in camera
    assert '6, 47, 4)' in camera and 'fov = 42.0' in camera
    assert 'near = 0.1' in camera and 'far = 160.0' in camera
    assert '0, -1, -4.371139e-08' in camera and 'current = true' in camera
    burst = (folder / 'burst.tscn').read_text()
    assert 'path="res://tests/fixtures/s05_effect/burst.tscn"' in burst
    assert 'transform =' not in burst and burst.count('[node ') == 1
    observer = (folder / 'observer.gd').read_text()
    assert 'RenderingServer.frame_post_draw.connect(_post_draw)' in observer
    assert not re.search(r'force_draw|emit_signal|\.emit\(|Input\.|window_set', observer)
    assert 'await super._remote_fire_cases()' in observer
    assert 'presentation.advance' not in observer and 'effects.consume' not in observer
    record['observer_uid'] = uid(folder / 'observer.gd')
    return record


def production_rows(path):
    """Decode complete original production assertions from their actual stream."""
    return [json.loads(line[4:]) for line in path.read_text().splitlines()
            if line.startswith('S05 ')]


def draw_rows(folder):
    """Require exactly one complete observer receipt stream per owned process."""
    matches = list((folder / 'data').rglob('draw.jsonl'))
    assert len(matches) == 1, 'missing/ambiguous draw stream'
    return [json.loads(line) for line in matches[0].read_text().splitlines()]


def evaluate(group):
    """Keep automatic viewport partial evidence separate from native criteria and image review."""
    lifecycle = json.loads((group / 'lifecycle.json').read_text())
    assert set(lifecycle['processes']) == {'host', 'client', 'late'}
    assert lifecycle['collection_ok'] and lifecycle['all_owned_children_reaped']
    assert lifecycle['streams_closed'] and lifecycle['copy_bytes_preserved']
    assert len({p['owned_pid'] for p in lifecycle['processes'].values()}) == 3
    data = {role: production_rows(group / role / 'stdout') for role in ['host', 'client', 'late']}
    host = next(r for r in data['host'] if r['event'] == 'network')
    live = next(r for r in data['client'] if r['event'] == 'client_state')
    late = next(r for r in data['late'] if r['event'] == 'hydrate')
    checks = {'twelve_outcomes_144_visits': host['damage'] == 12 and host['visits'] == 144,
              'eight_reservations_four_drops': host['effects'] == 8 and host['effect_drops'] == 4,
              'live_dedup': live['live'] == 12 and live['duplicates'] == 12,
              'live_capacity': live['accepted'] == 8 and live['dropped'] == 4,
              'settled_late_zero_history': late['effects'] == 0 and not late['input_enabled'],
              'completed_jobs': len(host['completed']) == 12 and host['active_jobs'] == 0}
    for role, entries in data.items():
        final = [r for r in entries if r['event'] == 'result']
        checks[role + '_fixture_pass'] = len(final) == 1 and final[0]['ok']
        cut = host['cut'] if role == 'host' else next(r['cut'] for r in entries
                                                   if r['event'] == 'client_state')
        checks[role + '_twelve_wrecks'] = len(cut['rows']) == 12 and all(
            r['health'] == 0 and r['explosions'] == 1 for r in cut['rows'])
    observers = {}
    images = []
    for role in ['host', 'client', 'late']:
        receipts = draw_rows(group / role)
        frames = [r for r in receipts if r['kind'] == 'frame']
        final = [r for r in receipts if r['kind'] == 'result']
        checks[role + '_observer_complete'] = len(final) == 1 and (
            not final[0]['render_failures'] and not final[0]['fixture_failures'])
        indices = [r['render_index'] for r in frames]
        checks[role + '_automatic_frames'] = len(frames) >= 3 and all(
            b > a for a, b in zip(indices, indices[1:]))
        checks[role + '_current_saved_camera'] = bool(frames) and all(
            r['camera']['expected_current'] and r['camera']['current'] and
            r['camera']['position'] == [6, 47, 4] and r['camera']['fov'] == 42 and
            math.isclose(r['camera']['near'], .1, abs_tol=1e-6) and
            r['camera']['far'] == 160 and r['camera']['projection'] == 0 for r in frames)
        checks[role + '_camera_path_recorded'] = bool(frames) and all(
            r['camera']['path'].endswith('/ObservationView/Camera3D') for r in frames)
        for receipt in frames:
            if 'png' not in receipt:
                continue
            png = receipt['png']; path = Path(png['path']); content = path.read_bytes()
            assert content[:8] == b'\x89PNG\r\n\x1a\n'
            size = list(struct.unpack('>II', content[16:24]))
            assert size == [png['width'], png['height']] == receipt['viewport']
            images.append({'role': role, 'stage': png['stage'], 'path': str(path),
                           'size': size, 'callback': receipt['callback'],
                           'render_index': receipt['render_index'],
                           'physics_index': receipt['physics_index'],
                           'damage_tick': receipt['damage_tick'], 'watermark': receipt['watermark'],
                           'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)})
        burst = [r for r in frames if r.get('png', {}).get('stage') == 'burst']
        if role != 'late':
            checks[role + '_eight_linked_saturated_slots'] = len(burst) == 1 and (
                burst[0]['accepted'] == 8 and burst[0]['dropped'] == 4 and
                len({s['car'] for s in burst[0]['slots'] if s['visible_in_tree']}) == 8 and
                all(s['mesh_nodes'] == 1 and s['model_scene'] ==
                    'res://art/models/spikes/s05_explosion_carrier.glb'
                    for s in burst[0]['slots'] if s['visible_in_tree']))
        observers[role] = {'frame_rows': len(frames), 'render_indices_first_last':
                           [indices[0], indices[-1]] if indices else [],
                           'can_draw_values': sorted({r['can_draw'] for r in frames}),
                           'focus_values': sorted({r['focus'] for r in frames}),
                           'viewport_sizes': sorted({tuple(r['viewport']) for r in frames}),
                           'window_sizes': sorted({tuple(r['window_size']) for r in frames}),
                           'stages': [r['png']['stage'] for r in frames if 'png' in r]}
    live_draw = draw_rows(group / 'client')
    expiry = [r for r in live_draw if r['kind'] == 'expiry']
    checks['natural_live_expiry'] = len(expiry) == 1 and expiry[0]['presentation']['visible'] == 0 and (
        expiry[0]['wait_ticks'] <= 120 and expiry[0]['live'] == 12 and expiry[0]['duplicates'] == 12)
    host_draw = draw_rows(group / 'host')
    blasts = [r for r in host_draw if r['kind'] == 'blast']
    checks['twelve_actual_host_events'] = len(blasts) == 12 and len({
        r['event_id']['sequence'] for r in blasts}) == 12
    # Human image inspection is deliberately a distinct required receipt.
    return {'checks': checks, 'receipt_checks_ok': all(checks.values()),
            'automatic_viewport_images_require_independent_inspection': True,
            'native_criteria_passed': False, 'observers': observers, 'images': images}


def main():
    """Run only scoped static/readback checks; never start an engine or replay accepted suites."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--group', type=Path)
    parser.add_argument('--base', default=BASE)
    args = parser.parse_args()
    result = {'base': args.base, 'originals': originals(args.base), 'resources': resources()}
    if args.group:
        result['observation'] = evaluate(args.group)
    save(args.output, result)
    print(json.dumps({'original_files': len(result['originals']), 'resources': result['resources'],
                      'observation': result.get('observation')}, indent=2))
    return 0 if not args.group or result['observation']['receipt_checks_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
