#!/usr/bin/env python3
"""New source-only checks; never calls an engine or any historical helper."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import zlib

BASE = '244089785b0d106451160acd89859c6977d30956'
ROOT = Path(__file__).resolve().parents[3]
DIR = ROOT / 'docs/spikes/s07-representative-evidence'
DOC = 'docs/spikes/s07-representative-preparation.md'
# Independent owned-set and coverage expectations, not extracted from the new document.
OWNED = {DOC, 'docs/spikes/s07.md', 'docs/plans/task-requirements.md'}
NEW = {'.gdignore', 'README.md', 'check.py', 'retain.py', 'references.json',
       'raw-requirements.md', 'launch.json'}
ROWS = ['T1', 'T2'] + [f'R{i}' for i in range(1, 12)] + ['G1', 'X1']
SLICES = [f'C{i}' for i in range(8)]
DECISIONS = [f'D{i}' for i in range(1, 5)]
SOURCE_PATHS = [
    'AGENTS.md', 'TODO.md', 'docs/plans/task-requirements.md',
    '.agents/skills/paseo-orchestrator/SKILL.md',
    '.agents/skills/paseo-orchestrator/references/implementer.md',
    '.agents/skills/paseo-orchestrator/references/reviewer.md',
    '.agents/skills/paseo-orchestrator/references/cards.md',
    'docs/reviews/plan-checkpoints.md', 'docs/reviews/plan-check-2026-10-08-09.md',
    'docs/reviews/plan-check-09-evidence/accepted-ledger.json.gz',
    'docs/reviews/p0-doc14.md', 'docs/spikes/s07.md', 'docs/spikes/s07-run-cards.md',
    'docs/spikes/s07-run-card-evidence/inventory.json',
    'docs/spikes/s07-sustained-driver.md',
    'docs/spikes/s07-sustained-driver-evidence/staged-inputs.json',
    'docs/spikes/s06-contracts.md', 'docs/spikes/s06-source-handoff.md',
    'docs/spikes/s05-contracts.md', 'docs/spikes/s05-saved-presentation.md',
    'docs/spikes/s05-effect-preparation.md', 'docs/assets/s02_kit.md',
    'docs/assets/s04_kit.md', 'docs/spikes/s02.md', 'docs/spikes/s04.md',
    'docs/spikes/s04-contracts.md', 'docs/spikes/s03-s-valve-api-interface.md',
    'docs/design.md', 'docs/world-layout.md', 'docs/art-direction.md',
    'docs/architecture.md', 'docs/api-contracts.md', 'docs/multiplayer.md',
    'docs/assets.md', 'docs/scene-structure.md', 'docs/development.md',
    'tests/fixtures/s07_driver/intersection.tscn',
    'tests/fixtures/s07_driver/fixture.gd',
    'tests/fixtures/s06/intersection.tscn', 'tests/fixtures/s06/intersection_wide.tscn',
    'tests/fixtures/s06/west.tscn', 'tests/fixtures/s06/east.tscn',
    'tests/fixtures/s06/derived.tres', 'tests/fixtures/s06/city.gd',
    'tests/fixtures/s06/fixture.gd', 'tests/fixtures/s06/controller.gd',
    'tests/fixtures/s02/actor.tscn', 'tests/fixtures/s02/actor_motion.gd',
    'tests/fixtures/s02/corner.tscn', 'tests/fixtures/s02/corner_wide.tscn',
    'tests/fixtures/s02/building_view.gd', 'tests/fixtures/s02/camera_rig.gd',
    'tests/fixtures/s02/aim_probe.gd', 'tests/fixtures/s04/kinematic.tscn',
    'tests/fixtures/s04/kinematic.gd', 'tests/fixtures/s04/drive_rules.gd',
    'tests/fixtures/s04/track.tscn', 'tests/fixtures/s04/match.gd',
    'tests/fixtures/s05_effect/burst.tscn', 'tests/fixtures/s05_effect/explosion.tscn',
    'tests/fixtures/s05_effect/match.gd', 'tests/fixtures/s05_effect/presentation.gd',
    'tests/fixtures/s05/burst.tscn', 'tests/fixtures/s05/car.tscn',
    'tests/fixtures/s05/car.gd', 'tests/fixtures/s05/damage.gd',
    'tests/fixtures/s05/match.gd', 'tests/fixtures/s05/replication.gd',
    'tests/fixtures/s05/presentation.gd',
    'tests/fixtures/s03/boot.tscn', 'tests/fixtures/s03/local_rig.tscn',
    'tests/fixtures/s03/session.gd', 'tests/fixtures/s03/transport.gd',
    'tests/fixtures/s03/match.gd', 'tests/fixtures/s03/replication.gd',
    'tests/fixtures/s03/proof.gd',
    'tests/fixtures/s03_r/boot.tscn', 'tests/fixtures/s03_r/actor.gd',
    'tests/fixtures/s03_r/match.gd', 'tests/fixtures/s03_r/replication.gd',
    'tools/s02/export_members.json', 'tools/s04/export_members.json',
    'tools/s06/export_members.json',
    'art/source/models/spikes/s02_kit.blend',
    'art/source/models/spikes/s04_kit.blend',
    'art/source/models/spikes/s06_intersection.blend',
    'art/source/models/spikes/s05_explosion_carrier.blend',
]
MODELS = ['s02_ground', 's02_low', 's02_near', 's02_tall', 's02_actor',
          's02_target', 's02_pistol', 's02_smg', 's02_launcher', 's04_car',
          's04_track', 's05_explosion_carrier', 's06_west', 's06_east']
SOURCE_PATHS += [f'art/models/spikes/{m}.glb{s}' for m in MODELS for s in ['', '.import']]
APIS = {
    'tests/fixtures/s07_driver/fixture.gd':
        ['begin_route', 'saved_start_valid', 'passive_valid', 'cancel_owned'],
    'tests/fixtures/s06/city.gd':
        ['validate_content', 'signature', 'bake_content', 'route', 'map_data'],
    'tests/fixtures/s06/fixture.gd': ['start_route', 'body_state', 'stop_route'],
    'tests/fixtures/s06/controller.gd': ['bind_route', 'intent', 'clear'],
    'tests/fixtures/s02/actor_motion.gd':
        ['step', 'neutralize', 'motion_state', 'muzzle_position'],
    'tests/fixtures/s04/drive_rules.gd': ['advance', 'neutral'],
    'tests/fixtures/s04/kinematic.gd': ['configure', 'step', 'neutralize',
        'install_pose', 'retire', 'motion_state', 'display_state'],
    'tests/fixtures/s05/damage.gd': ['begin', 'register_shooter', 'resolve_shot',
        'advance', 'cut', 'valid_cut', 'apply_cut', 'retire_shooter', 'clear'],
    'tests/fixtures/s05/car.gd': ['apply_life'],
    'tests/fixtures/s05/match.gd': ['baseline', 'apply_baseline', 'submit_fire',
        'apply_cars', 'rollback', 'clear'],
    'tests/fixtures/s05/replication.gd':
        ['send_fire', 'publish_cars', 'publish_blast', 'forget', 'clear'],
    'tests/fixtures/s05_effect/presentation.gd': ['bind', 'consume',
        'advance_cosmetic', 'clear', 'receipt', 'visible_count'],
    'tests/fixtures/s03_r/match.gd':
        ['local_body', 'prepare_resync', 'pose_for_entity', 'apply_movement'],
    'tests/fixtures/s03_r/actor.gd': ['install_pose', 'retire', 'display_state'],
}
UIDS = {
    'tests/fixtures/s07_driver/intersection.tscn': 'uid://cauba1m1nenjw',
    'tests/fixtures/s06/intersection.tscn': 'uid://c61a1l4vio22q',
    'tests/fixtures/s06/west.tscn': 'uid://b243gxu4qpp0a',
    'tests/fixtures/s06/east.tscn': 'uid://chhg1wj1jcwpu',
    'tests/fixtures/s06/derived.tres': 'uid://dt54nay70c1tr',
    'tests/fixtures/s02/actor.tscn': 'uid://dl05tre3pd6e0',
    'tests/fixtures/s04/kinematic.tscn': 'uid://cyyhi67pisbql',
    'tests/fixtures/s05_effect/burst.tscn': 'uid://bdtfsc6kyavum',
    'tests/fixtures/s05_effect/explosion.tscn': 'uid://dbge3dp3s53r3',
    'tests/fixtures/s03_r/boot.tscn': 'uid://jd5igfvwkrvk',
}
OLD_PREFIXES = ('2294a111', 'a15a7fbe', '30a97532', '8689168d', '30471e6a')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def fingerprint(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def strict_json(data):
    def pairs(rows):
        out = {}
        for key, val in rows:
            assert key not in out, ('duplicate JSON key', key)
            out[key] = val
        return out
    return json.loads(data, object_pairs_hook=pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))


def historical_reports(note, report):
    # Ledger selectors have dictionary paths containing '/' as literal keys.
    selector = report['selector']
    if selector.startswith('/complete_reports_verbatim/'):
        value = note['complete_reports_verbatim'][selector.rsplit('/', 1)[-1]]
    else:
        container = selector.split('/')[1]
        value = note[container][selector.split('/', 2)[2]]
    if isinstance(value, str):
        return value.encode()
    data = base64.b64decode(value.get('data', value.get('base64')), validate=True)
    encoding = value['encoding']
    if encoding == 'zlib+base64':
        data = zlib.decompress(data)
    elif encoding == 'gzip+base64':
        data = gzip.decompress(data)
    else:
        assert encoding == 'base64', encoding
    return data


def reference_record():
    entries = []
    for path in SOURCE_PATHS:
        data = git('show', f'{BASE}:{path}')
        entry = {'path': path, 'revision': BASE,
                 'blob': git('rev-parse', f'{BASE}:{path}').decode().strip(),
                 **fingerprint(data)}
        if path in APIS:
            entry['required_apis'] = APIS[path]
        if path in UIDS:
            entry['root_uid'] = UIDS[path]
            entry['saved_node_declarations'] = re.findall(r'^\[node [^\n]+', data.decode(), re.M)
        entries.append(entry)
    ledger = strict_json(gzip.decompress(git('show',
        f'{BASE}:docs/reviews/plan-check-09-evidence/accepted-ledger.json.gz')))
    old = [n for n in ledger['consulted_notes'] if n['commit'].startswith(OLD_PREFIXES)]
    assert len(old) == len(OLD_PREFIXES)
    return {'schema': 1, 'base': BASE, 'sources': entries,
            'historical_references': old,
            'limits': 'Selected source identities; source links from accepted handoffs, '
                      'not a new Blender export or engine bake. Old reports not recopied.'}


def anchors(text):
    values = set(re.findall(r'''<a\s+(?:id|name)=["']([^"']+)''', text))
    counts = {}
    for h in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
        slug = re.sub(r'[^\w\- ]', '', h.lower().replace('`', '')).replace(' ', '-')
        n = counts.get(slug, 0)
        values.add(slug + (f'-{n}' if n else ''))
        counts[slug] = n + 1
    return values


def links(path):
    text = path.read_text()
    for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        raw = re.sub(r'\s+', '', raw)
        if '://' in raw or raw.startswith('mailto:'):
            continue
        target, _, anchor = raw.partition('#')
        dest = (path.parent / target).resolve() if target else path
        assert dest.exists(), ('missing local link', str(path), raw)
        if anchor:
            assert anchor in anchors(dest.read_text()), ('missing anchor', str(path), raw)


def validate():
    assert git('rev-parse', BASE).decode().strip() == BASE
    ref = strict_json((DIR / 'references.json').read_bytes())
    assert ref == reference_record(), 'independently declared source/old-reference set mismatch'
    modified_allowed = {'docs/spikes/s07.md', 'docs/plans/task-requirements.md'}
    for row in ref['sources']:
        path = row['path']
        data = git('cat-file', 'blob', row['blob'])
        assert fingerprint(data) == {k: row[k] for k in ['bytes', 'sha256']}, path
        if path not in modified_allowed:
            assert (ROOT / path).read_bytes() == data, ('source changed', path)
        text = data.decode(errors='replace')
        if path in APIS:
            funcs = set(re.findall(r'^(?:static )?func (\w+)\(', text, re.M))
            assert set(APIS[path]) <= funcs, (path, set(APIS[path]) - funcs)
        if path in UIDS:
            assert f'uid="{UIDS[path]}"' in text.splitlines()[0], path
        if path.endswith(('.tscn', '.tres')):
            for uid, dependency in re.findall(
                r'\[ext_resource [^\n]*?uid="([^"]+)" path="res://([^"]+)"', text):
                dep_path = dependency + '.import' if dependency.endswith('.glb') else dependency
                dep = (ROOT / dep_path).read_text(errors='replace')
                if dependency.endswith('.gd'):
                    assert (ROOT / (dependency + '.uid')).read_text().strip() == uid
                else:
                    assert re.search(r'(?:uid=|uid = )"' + re.escape(uid) + '"', dep), dep_path
    for old in ref['historical_references']:
        data = git('cat-file', 'blob', old['blob'])
        assert fingerprint(data) == {k: old[k] for k in ['bytes', 'sha256']}
        note = strict_json(data)
        for r in old['reports']:
            assert fingerprint(historical_reports(note, r)) == {k: r[k] for k in ['bytes', 'sha256']}, r
    inventory = strict_json((ROOT / 'docs/spikes/s07-run-card-evidence/inventory.json').read_bytes())
    assert len(inventory['inputs']) == 186
    inventory_drift = []
    for path, expected in inventory['inputs'].items():
        original = git('show', f"{inventory['accepted_base']}:{path}")
        assert fingerprint(original) == expected, ('immutable inventory input mismatch', path)
        if fingerprint((ROOT / path).read_bytes()) != expected:
            inventory_drift.append(path)
            assert (ROOT / path).read_bytes() == git('show',
                f'53f0c8fd00a05271948087099eee9d7ca1c22989:{path}'), path
    assert inventory_drift == ['tests/fixtures/s03/proof.gd', 'tests/fixtures/s03/session.gd']
    total = 0
    model_stats = {}
    expected_geometry = {
        's02_actor': (7, 7, 1316), 's04_car': (8, 8, 1504),
        's04_track': (6, 6, 1128), 's05_explosion_carrier': (1, 3, 1344),
        's06_west': (17, 17, 204), 's06_east': (17, 17, 204)}
    for m in MODELS:
        data = (ROOT / f'art/models/spikes/{m}.glb').read_bytes()
        magic, version, length = struct.unpack_from('<III', data)
        assert magic == 0x46546C67 and version == 2 and length == len(data)
        n, chunk = struct.unpack_from('<II', data, 12)
        assert chunk == 0x4E4F534A
        model = strict_json(data[20:20+n].rstrip(b' \x00'))
        assert all(not model.get(k) for k in ['images', 'textures', 'skins', 'animations']), m
        assert 2 <= len(model['materials']) <= 4
        primitives = sum(len(mesh['primitives']) for mesh in model['meshes'])
        triangles = sum(model['accessors'][p['indices']]['count'] // 3
                        for node in model['nodes'] if 'mesh' in node
                        for p in model['meshes'][node['mesh']]['primitives'])
        model_stats[m] = (len(model['meshes']), primitives, triangles)
        if m in expected_geometry:
            assert model_stats[m] == expected_geometry[m], (m, model_stats[m])
        if m == 's05_explosion_carrier':
            assert all(v.get('alphaMode', 'OPAQUE') == 'OPAQUE' and v['doubleSided']
                       and v['pbrMetallicRoughness']['baseColorFactor'][3] == 1
                       for v in model['materials'])
        total += len(data)
    assert total == 433824
    for scene, expected in [('s06/intersection', (79, 59, 5108)),
                            ('s05_effect/burst', (179, 126, 29928))]:
        row = inventory['saved_compositions'][f'tests/fixtures/{scene}.tscn']
        assert (row['saved_nodes_excluding_glb_internal_nodes'],
                row['primitives_all_saved_glb_placements'],
                row['triangles_all_saved_glb_placements']) == expected
        assert sum(model_stats[Path(path).stem][2] * n
                   for path, n in row['glb_placements'].items()) == expected[2]
    doc = (ROOT / DOC).read_text()
    assert re.findall(r'^\| ((?:T|R|G|X)\d+) —', doc, re.M) == ROWS
    assert re.findall(r'^### (C\d) —', doc, re.M) == SLICES
    assert re.findall(r'^\| (D\d) —', doc, re.M) == DECISIONS
    for row in doc.splitlines():
        if re.match(r'^\| (?:T|R|G|X)\d+ —', row):
            assert any(f'**{s}**' in row for s in ['present', 'missing', 'blocked', 'extendable']), row
    for literal in ['UNEXECUTED', 'S07 TODO stays OPEN', 'R/G remain blocked',
                    'No fixture, model, gameplay code', 'Steam', 'NOT authorized',
                    '57-traversal/600-declared-second', 'No values are\napproved here',
                    'zero images, textures, skins and animations', 'maximum22 roots',
                    'T≤12', 'R≤18', 'G≤12', 'exactly ten cycles', 'Regner',
                    'free-space detours', 'four-lifetime-shooter', '100 m',
                    'no fifth slot', '1200 bytes', '65536']:
        # Unicode/case is intentional: gates must not disappear during edits.
        assert literal in doc or literal in doc.lower(), ('missing literal gate', literal)
    index = 'docs/plans/task-requirements.md'
    old = git('show', f'{BASE}:{index}').decode()
    now = (ROOT / index).read_text()
    pattern = r'(?ms)^- \*\*S07:\*\*.*?(?=^- \*\*S08:\*\*)'
    assert len(re.findall(pattern, old)) == len(re.findall(pattern, now)) == 1
    assert re.sub(pattern, '', old) == re.sub(pattern, '', now), 'non-S07 index bytes changed'
    old_spike = git('show', f'{BASE}:docs/spikes/s07.md')
    assert (ROOT / 'docs/spikes/s07.md').read_bytes().startswith(old_spike), 'historical spike edited'
    # All tracked base paths, including TODO/gameplay/vendor/settings/assets and old packs.
    base_paths = git('ls-tree', '-r', '--name-only', BASE).decode().splitlines()
    unchanged = 0
    for path in base_paths:
        if path in modified_allowed:
            continue
        assert (ROOT / path).read_bytes() == git('show', f'{BASE}:{path}'), ('outside-owned changed', path)
        unchanged += 1
    current = set(git('ls-files', '--cached', '--others', '--exclude-standard').decode().splitlines())
    additions = current - set(base_paths)
    expected_new = {DOC} | {f'docs/spikes/s07-representative-evidence/{p}' for p in NEW}
    assert additions == expected_new, ('unexpected/missing new paths', additions ^ expected_new)
    assert {p.name for p in DIR.iterdir()} == NEW
    for path in OWNED | expected_new:
        data = (ROOT / path).read_bytes()
        assert b'\r' not in data and (not data or data.endswith(b'\n')), ('LF', path)
        if path.endswith('.json'):
            strict_json(data)
        if path.endswith(('.md', '.py')):
            assert all(line.rstrip() == line for line in data.decode().splitlines()), ('whitespace', path)
        if path.endswith('.py'):
            compile(data, path, 'exec')
    for path in [ROOT / DOC, ROOT / index, ROOT / 'docs/spikes/s07.md', DIR / 'README.md']:
        links(path)
    # Incoming links to all affected documents; unchanged target anchors must survive.
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts:
            continue
        text = path.read_text(errors='replace')
        for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            raw = re.sub(r'\s+', '', raw)
            if '://' in raw:
                continue
            target, _, anchor = raw.partition('#')
            dest = (path.parent / target).resolve() if target else path.resolve()
            if dest in {ROOT / DOC, ROOT / index, ROOT / 'docs/spikes/s07.md'}:
                assert dest.exists()
                assert not anchor or anchor in anchors(dest.read_text()), ('incoming anchor', str(path), raw)
    subprocess.run(['git', 'diff', '--check', BASE], cwd=ROOT, check=True)
    print(json.dumps({'result': 'PASS', 'base': BASE, 'sources': len(ref['sources']),
                      'prior_notes': len(ref['historical_references']),
                      'accepted_inventory_inputs': 186, 'current_log_only_delta': inventory_drift,
                      'GLBs': 14, 'disk_bytes': total, 'source_geometry': model_stats,
                      'matrix_rows': ROWS, 'slices': SLICES, 'decisions': DECISIONS,
                      'outside_owned_base_files_unchanged': unchanged,
                      'TODO': 'byte-identical, S07 OPEN', 'runtime': 'NOT RUN'}, indent=2))


if __name__ == '__main__':
    if sys.argv[1:] == ['--record-references']:
        (DIR / 'references.json').write_text(json.dumps(reference_record(), indent=2) + '\n')
    else:
        assert not sys.argv[1:]
        validate()
