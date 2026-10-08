#!/usr/bin/env python3
"""Evaluate Card I literally, preserving negative outcomes and separate native/visual gates."""
import argparse
import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = '3f5fb4067c5ce5fca721f54d42165a833e4c884c'
OBSERVER = 'tests/fixtures/s05_draw/observer.gd'
STAGES = {'host': ['baseline', 'burst', 'expired'],
          'client': ['baseline', 'burst', 'expired'], 'late': ['hydrated']}


def load_original():
    """Reuse the existing saved-camera/resource assertions, without running old workloads."""
    spec = importlib.util.spec_from_file_location('s05_original_checks', ROOT / 'tools/s05_draw/check.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def static(base=BASE):
    """Check all base bytes except the two explicitly owned instrumentation/task paths."""
    ledger = []
    tree = subprocess.check_output(['git', 'ls-tree', '-rz', base], cwd=ROOT)
    for entry in tree.split(b'\0'):
        if not entry:
            continue
        metadata, name = entry.split(b'\t')
        mode, _, oid = metadata.decode().split()
        name = name.decode()
        if name in ['TODO.md', OBSERVER]:
            continue
        path = ROOT / name
        data = str(path.readlink()).encode() if mode == '120000' else path.read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == oid, name
        ledger.append({'path': name, 'git_blob': oid, 'bytes': len(data),
                       'sha256': hashlib.sha256(data).hexdigest()})
    before = subprocess.check_output(['git', 'show', base + ':TODO.md'], cwd=ROOT, text=True)
    after = (ROOT / 'TODO.md').read_text()
    assert before[:before.index('- [ ] **S05')] == after[:after.index('- [ ] **S05')]
    assert before[before.index('- [ ] **S06'):] == after[after.index('- [ ] **S06'):]
    source = (ROOT / OBSERVER).read_text()
    original = subprocess.check_output(['git', 'show', base + ':' + OBSERVER], cwd=ROOT, text=True)
    assert re.findall(r'^func .*', source, re.M) == re.findall(r'^func .*', original, re.M)
    assert 'MAX_FRAME_RECEIPTS: int = 65_536' in source
    assert 'DisplayServer.window_get_vsync_mode()' in source
    assert 'DisplayServer.can_any_window_draw(' not in source
    assert not re.search(r'force_draw|emit_signal|\.emit\(|window_set|Input\.|fixed.fps|movie', source)
    for path in (ROOT / 'tools/s05_vsync_image').glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    return {'originals': ledger, 'resources': load_original().resources(),
            'observer_api_preserved': True, 'python_ast': True,
            'todo_outside_s05_preserved': True}


def validate_sizes(image_size, png_size, receipt):
    """Keep image identity strict but viewport/native/requested dimensions independent."""
    assert image_size == png_size and all(value > 0 for value in image_size)
    for field in ['viewport', 'window_size', 'requested_project_size']:
        assert len(receipt[field]) == 2 and all(value > 0 for value in receipt[field])
    assert receipt['requested_project_size'] == [1280, 800]


def evaluate(group):
    """Evaluate actual streams and callback-bound PNGs; missing stages are explicit failures."""
    checks, errors, summaries, images = {}, [], {}, []
    original = load_original()
    life = json.loads((group / 'lifecycle.json').read_text())
    for field in ['collection_ok', 'source_preserved', 'streams_closed',
                  'all_owned_children_reaped', 'within_budget', 'normal_exits',
                  'preparation_within_budget', 'collection_within_budget',
                  'cleanup_within_budget', 'readback_within_budget']:
        checks[field] = life.get(field) is True
    checks['owned_roles'] = set(life['processes']) == {'import', 'host', 'client', 'late'}
    checks['no_cleanup_fallback'] = not life.get('cleanup_phases')
    checks['no_supervisor_failure'] = 'failure' not in life
    checks['loopback_binding_proven'] = life.get('bound_endpoint', {}).get('address') == '127.0.0.1'
    data, draws = {}, {}
    for role in STAGES:
        try:
            data[role] = original.production_rows(group / role / 'stdout')
            draws[role] = original.draw_rows(group / role)
        except (AssertionError, OSError, ValueError) as error:
            errors.append(role + ': ' + repr(error))
            data[role], draws[role] = [], []
        rows = data[role]
        final = [r for r in rows if r['event'] == 'result']
        checks[role + '_fixture_pass'] = len(final) == 1 and final[0]['ok'] and not final[0]['failures']
        cosmetic = [json.loads(line[len('S05_EFFECT '):]) for line in
                    (group / role / 'stdout').read_text().splitlines()
                    if line.startswith('S05_EFFECT ')] if (group / role / 'stdout').exists() else []
        checks[role + '_fences_and_negative_guards'] = len(cosmetic) == 3 and all(
            r['ok'] for r in cosmetic) and {r.get('guard') for r in cosmetic if r['event'] == 'negative'} == {
                'lifetime', 'epoch'}
        frames = [r for r in draws[role] if r['kind'] == 'frame']
        final_draw = [r for r in draws[role] if r['kind'] == 'result']
        checks[role + '_observer_complete'] = len(final_draw) == 1 and not (
            final_draw[0]['render_failures'] or final_draw[0]['fixture_failures'])
        checks[role + '_callback_cap_not_exhausted'] = len(final_draw) == 1 and (
            3 <= final_draw[0]['callbacks'] < 65536)
        checks[role + '_effective_vsync_disabled'] = bool(frames) and all(
            r.get('vsync_mode') == 0 and r.get('vsync_disabled') is True for r in frames)
        checks[role + '_wayland'] = bool(frames) and all(r['display'] == 'Wayland' for r in frames)
        indices, times = [r['render_index'] for r in frames], [r['monotonic_ms'] for r in frames]
        checks[role + '_automatic_monotonic_frames'] = len(frames) >= 3 and all(
            b > a for a, b in zip(indices, indices[1:])) and all(
            b >= a for a, b in zip(times, times[1:]))
        checks[role + '_current_saved_camera'] = bool(frames) and all(
            r['camera']['expected_current'] and r['camera']['current'] and
            r['camera']['position'] == [6, 47, 4] and r['camera']['projection'] == 0 and
            r['camera']['fov'] == 42 and math.isclose(r['camera']['near'], .1, abs_tol=1e-6) and
            r['camera']['far'] == 160 and r['camera']['path'].endswith('/ObservationView/Camera3D')
            for r in frames)
        captures = [r for r in frames if 'png' in r]
        checks[role + '_required_stages'] = {r['png']['stage'] for r in captures} == set(STAGES[role])
        for receipt in captures:
            png = receipt['png']
            key = role + '_' + png['stage']
            try:
                path = Path(png['path'])
                assert path.is_relative_to(group / role / 'data'), 'image outside owned role root'
                content = path.read_bytes()
                assert content[:8] == b'\x89PNG\r\n\x1a\n', 'PNG signature'
                size = list(struct.unpack('>II', content[16:24]))
                validate_sizes(size, [png['width'], png['height']], receipt)
                assert hashlib.sha256(content).hexdigest() == png['sha256'] and png['save_error'] == 0
                assert receipt['callback'] >= 3 and receipt['requested_project_size'] == [1280, 800]
                assert receipt['session'] == receipt['cut']['session'] and len(receipt['session']) == 32
                assert receipt['match_revision'] == receipt['cut']['match'] == 1
                assert receipt['revision'] == receipt['cut']['revision']
                assert receipt['damage_tick'] == receipt['cut']['tick']
                assert receipt['can_any_window_draw'] is None
                assert receipt['can_any_window_draw_reason'] == 'internal native method unavailable to GDScript'
                if png['stage'] in ['burst', 'expired', 'hydrated']:
                    assert len(receipt['cut']['rows']) == 12 and all(
                        r['health'] == 0 and r['explosions'] == 1 and r['phase'] == 'WRECK'
                        for r in receipt['cut']['rows'])
                if png['stage'] == 'burst':
                    visible = [s for s in receipt['slots'] if s['visible_in_tree']]
                    assert len(visible) == len({s['car'] for s in visible}) == 8
                    assert receipt['accepted'] == 8 and receipt['dropped'] == 4
                    assert all(s['mesh_nodes'] == 1 and s['model_scene'] ==
                        'res://art/models/spikes/s05_explosion_carrier.glb' for s in visible)
                if png['stage'] == 'hydrated':
                    assert receipt['presentation']['visible'] == receipt['accepted'] == receipt['live'] == 0
                if png['stage'] == 'expired':
                    assert receipt['presentation']['visible'] == 0 and receipt['accepted'] == 8
                    assert all(not active['busy'] for active in receipt['presentation']['active'])
                    assert receipt['presentation']['tick'] >= max(
                        active['local_deadline'] for active in receipt['presentation']['active'])
                checks[key + '_bound_image'] = True
                images.append({'role': role, 'stage': png['stage'], 'path': str(path),
                    'sha256': png['sha256'], 'bytes': len(content), 'image_size': size,
                    'viewport': receipt['viewport'], 'window_size': receipt['window_size'],
                    'requested_project_size': receipt['requested_project_size'],
                    'callback': receipt['callback'], 'render_index': receipt['render_index'],
                    'physics_index': receipt['physics_index'], 'session': receipt['session'],
                    'damage_tick': receipt['damage_tick'], 'watermark': receipt['watermark']})
            except (AssertionError, OSError, KeyError, ValueError) as error:
                checks[key + '_bound_image'] = False
                errors.append(key + ': ' + repr(error))
        summaries[role] = {'callbacks': final_draw[0]['callbacks'] if final_draw else None,
            'frame_rows': len(frames), 'indices': indices,
            'vsync_modes': sorted({r.get('vsync_mode') for r in frames}),
            'can_draw_values': sorted({r['can_draw'] for r in frames}),
            'viewport_sizes': sorted({tuple(r['viewport']) for r in frames}),
            'native_window_sizes': sorted({tuple(r['window_size']) for r in frames}),
            'captured_stages': [r['png']['stage'] for r in captures],
            'absent_stages': sorted(set(STAGES[role]) - {r['png']['stage'] for r in captures})}
    try:
        host = next(r for r in data['host'] if r['event'] == 'network')
        live = next(r for r in data['client'] if r['event'] == 'client_state')
        late = next(r for r in data['late'] if r['event'] == 'hydrate')
        checks['twelve_outcomes_144_visits'] = host['damage'] == 12 and host['visits'] == 144
        checks['twelve_completed_jobs'] = len(host['completed']) == 12 and host['active_jobs'] == 0
        checks['saturation_independent_of_chain'] = host['effects'] == 8 and host['effect_drops'] == 4
        checks['live_dedup'] = live['live'] == live['duplicates'] == 12
        checks['live_capacity'] = live['accepted'] == 8 and live['dropped'] == 4
        checks['late_hydration_before_input'] = late['effects'] == 0 and not late['input_enabled']
        for role, cut in [('host', host['cut']), ('client', live['cut']), ('late', late['cut'])]:
            checks[role + '_twelve_health0_explosion1'] = len(cut['rows']) == 12 and all(
                r['health'] == 0 and r['explosions'] == 1 for r in cut['rows'])
        fire = [r for r in data['client'] if r['event'] == 'fire']
        checks['original_remote_negatives'] = [r['actual'] for r in fire] == [
            'NOT_ADMITTED', 'OK', 'DUPLICATE', 'STALE_CONTEXT', 'RATE_LIMIT',
            'INVALID', 'INVALID', 'WINDOW', 'DUPLICATE'] and all(
                r['actual'] == r['expected'] for r in fire)
        blasts = [r for r in draws['host'] if r['kind'] == 'blast']
        checks['twelve_real_event_ids'] = len(blasts) == 12 and {
            r['event_id']['sequence'] for r in blasts} == set(range(2, 14)) and all(
            r['event_id']['session'] == host['cut']['session'] for r in blasts)
        expiry = [r for r in draws['client'] if r['kind'] == 'expiry']
        checks['natural_live_expiry'] = len(expiry) == 1 and expiry[0]['presentation']['visible'] == 0 and (
            0 <= expiry[0]['wait_ticks'] <= 120 and expiry[0]['live'] == expiry[0]['duplicates'] == 12)
    except (StopIteration, KeyError) as error:
        errors.append('workload receipts: ' + repr(error))
        checks['complete_gameplay_receipts'] = False
    return {'checks': checks, 'receipt_checks_ok': all(checks.values()), 'errors': errors,
            'observers': summaries, 'images': images, 'image_inspection_required': True,
            'image_partial_passed': False, 'native_criteria_passed': False,
            'inspection_status': 'pending actual PNG inspection' if images else 'no PNG; no inspection credit'}


def main():
    """Run offline/readback checks only; do not launch an engine or replay any attempt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--base', default=BASE)
    args = parser.parse_args()
    result = {'preservation_base': args.base, 'static': static(args.base)}
    if args.group:
        result['observation'] = evaluate(args.group.resolve())
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'static_originals': len(result['static']['originals']),
                      'observation': result.get('observation')}, indent=2))
    return 0 if not args.group or result['observation']['receipt_checks_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
