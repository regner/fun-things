#!/usr/bin/env python3
"""Validate the S07 artifact's independent expected placements, links and scope."""
import argparse
import ast
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'docs/spikes/s07-run-card-evidence'
ORIGINAL = '52941da4b4c92a547a8066b5c13f733043ecbe48'
FINAL_BASE = '48aef3dbd133876743f504f94a1b788a26d5638f'
TODO_LINK = ('  Use the [static fixture inventory and concrete run cards]'
             '(docs/spikes/s07-run-cards.md) to prepare the baseline and growth experiment.\n')
EXPECTED = {
    's02/corner': {'s02_actor': 1, 's02_ground': 1, 's02_low': 2, 's02_near': 1,
                   's02_pistol': 1, 's02_tall': 1, 's02_target': 2},
    's02/corner_wide': {'s02_actor': 1, 's02_ground': 1, 's02_low': 2, 's02_near': 1,
                        's02_pistol': 1, 's02_tall': 1, 's02_target': 2},
    's02/weapon_studies': {'s02_actor': 3, 's02_ground': 1, 's02_launcher': 1,
                           's02_pistol': 1, 's02_smg': 1},
    's04/boot': {'s04_car': 2, 's04_track': 1},
    's04/body_comparison': {'s04_car': 3, 's04_track': 1},
    's05/boot': {'s04_car': 3, 's04_track': 1},
    's05/burst': {'s04_car': 12, 's04_track': 1},
    's05_effect/boot': {'s04_car': 3, 's04_track': 1, 's05_explosion_carrier': 8},
    's05_effect/burst': {'s04_car': 12, 's04_track': 1, 's05_explosion_carrier': 8},
    's06/intersection': {'s02_actor': 1, 's02_pistol': 1, 's04_car': 2,
                          's06_east': 1, 's06_west': 1},
    's06/intersection_wide': {'s02_actor': 1, 's02_pistol': 1, 's04_car': 2,
                               's06_east': 1, 's06_west': 1},
}


def git(*args):
    """Read repository bytes without changing Git state."""
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    """Check outcomes against literal scene expectations and the exact authorized delta."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, choices=(ORIGINAL, FINAL_BASE))
    args = parser.parse_args()
    receipt = json.loads((EVIDENCE / 'inventory.json').read_text())
    assert receipt['schema'] == 1 and receipt['accepted_base'] == ORIGINAL
    assert len(receipt['inputs']) == 186 and len(receipt['models']) == 14
    assert len(receipt['scenes_and_resources']) == 33
    actual_roots = receipt['saved_compositions']
    assert set(actual_roots) == {f'tests/fixtures/{name}.tscn' for name in EXPECTED}
    for name, expected in EXPECTED.items():
        row = actual_roots[f'tests/fixtures/{name}.tscn']
        assert {Path(p).stem: n for p, n in row['glb_placements'].items()} == expected, name
    for group in ('s02', 's04', 's05', 's05_effect', 's06'):
        paths = {str(p.relative_to(ROOT)) for p in
                 (ROOT / 'tests/fixtures' / group).iterdir() if p.is_file()}
        assert paths <= set(receipt['inputs']), ('omitted fixture input', group)
    for path, row in receipt['inputs'].items():
        data = (ROOT / path).read_bytes()
        assert len(data) == row['bytes']
        assert hashlib.sha256(data).hexdigest() == row['sha256'], path
        assert git('show', args.base + ':' + path) == data, ('input changed', path)
    assert all(m[k] == 0 for m in receipt['models'].values()
               for k in ('images', 'textures', 'skins', 'animations'))
    s06 = actual_roots['tests/fixtures/s06/intersection.tscn']
    assert s06['saved_types_excluding_glb_internal_nodes']['StaticBody3D'] == 4
    assert s06['saved_types_excluding_glb_internal_nodes']['CharacterBody3D'] == 3
    assert s06['cameras_and_lights']['Camera']['properties']['fov'] == '42.0'
    wide = actual_roots['tests/fixtures/s06/intersection_wide.tscn']
    assert wide['cameras_and_lights']['Camera']['properties']['fov'] == '50.0'
    previous = json.loads(gzip.decompress((ROOT /
        'docs/spikes/s05-saved-presentation-evidence/network/result.json.gz').read_bytes()))
    assert previous['ok'] and all(previous['checks'].values())
    assert previous['host']['damage'] == 12 and previous['host']['visits'] == 144
    assert previous['host']['effects'] == 8 and previous['host']['effect_drops'] == 4
    assert previous['late']['effects'] == 0
    owned_docs = [ROOT / 'docs/spikes/s07-run-cards.md', EVIDENCE / 'README.md',
                  EVIDENCE / 'review-brief.md']
    links = 0
    for doc in owned_docs:
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', doc.read_text()):
            if '://' in target:
                continue
            name, _, anchor = target.partition('#')
            destination = (doc.parent / name).resolve() if name else doc
            assert destination.is_file(), (doc, target)
            if anchor:
                headings = re.findall(r'^#+ (.+)$', destination.read_text(), re.M)
                slugs = {re.sub(r'[^\w -]', '', h.lower()).replace(' ', '-') for h in headings}
                assert anchor in slugs, (doc, target)
            links += 1
    ast.parse((ROOT / 'tools/s07/inventory.py').read_text())
    ast.parse(Path(__file__).read_text())
    before = git('show', args.base + ':TODO.md').decode()
    after = (ROOT / 'TODO.md').read_text()
    if args.base == FINAL_BASE:
        assert after.count(TODO_LINK) == 1
        assert after.replace(TODO_LINK, '') == before, 'TODO changed outside single evidence link'
        assert after.index(TODO_LINK) > after.index('**S07 —')
        assert after.index(TODO_LINK) < after.index('**S08 —')
        assert len(re.findall(r'^- \[ \] \*\*', after, re.M)) == 27
    else:
        assert before == after, 'pre-rebase TODO must be untouched'
    allowed = ('docs/spikes/s07-run-card-evidence/', 'tools/s07/')
    changed = git('diff', '--name-only', args.base).decode().splitlines()
    assert all(p in ('TODO.md', 'docs/spikes/s07-run-cards.md') or
               p.startswith(allowed) for p in changed), changed
    subprocess.run(['git', 'diff', '--check', args.base], cwd=ROOT, check=True)
    print(f'PASS {args.base}: 11 literal placement sets, 186 immutable input hashes, '
          f'14 GLB schemas, inherited cameras, prior finite receipt readback, '
          f'{links} local links/anchors, syntax, scoped diff and TODO')


if __name__ == '__main__':
    main()
