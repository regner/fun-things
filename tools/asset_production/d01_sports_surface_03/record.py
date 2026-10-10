"""Consolidate actual court-asset receipts and hash final delivery payloads, excluding scratch."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = 'd01_sports_surface_03'
EVIDENCE = ROOT / f'docs/assets/production/{NID}-evidence'
SCRATCH = Path(f'C:/tmp/ft/assets/{NID}')


def read_json(path):
    """Read an already completed validator receipt, never synthesize check outcomes."""
    return json.loads(path.read_text(encoding='utf-8'))


def diagnostics(name):
    """Keep concrete error/warning lines distinct from a successful process exit."""
    return [line for line in (SCRATCH / f'{name}.log').read_text(encoding='utf-8').splitlines()
            if re.search(r'(?:ERROR:|SCRIPT ERROR:|WARNING:)', line)]


def main():
    """Require receipt agreement, preserve normalization diagnostics and write the manifest last."""
    validation = read_json(EVIDENCE / 'validation.json')
    artwork = read_json(SCRATCH / 'artwork-check.json')
    engine = read_json(SCRATCH / 'prefab-check.json')
    roundtrip = read_json(SCRATCH / 'roundtrip.json')
    assert engine == read_json(SCRATCH / 'prefab-first-process.json')
    assert engine['ok'] and not engine['failures'] and roundtrip['ok']
    assert all(roundtrip[f'roundtrip_{index}_byte_stable'] for index in (1, 2))
    assert all(engine[key] == roundtrip[key] for key in engine if key.endswith('_uid'))
    assert artwork['ok'] and artwork['byte_identical_reproduction']
    assert validation['fresh_reexport_byte_identical']
    assert validation['texture_sha256'] == artwork['png_sha256']
    glb = ROOT / f'art/models/environment/{NID}/{NID}.glb'
    assert glb.stat().st_size == validation['glb_bytes']
    assert hashlib.sha256(glb.read_bytes()).hexdigest() == validation['glb_sha256']
    for name in ('import-final', 'prefab-check', 'prefab-second-process'):
        assert not any('ERROR:' in line for line in diagnostics(name)), name
    normalization = diagnostics('roundtrip')
    assert all('RID allocations of type' in line and 'leaked at exit' in line
               for line in normalization if 'ERROR:' in line)
    assert '1 file already formatted' in (SCRATCH / 'format.log').read_text(encoding='utf-8')
    assert 'no issues found' in (SCRATCH / 'style.log').read_text(encoding='utf-8')
    handoff = ROOT / f'docs/assets/production/{NID}.md'
    text = handoff.read_text(encoding='utf-8')
    assert set(re.findall(r'\b[0-9a-f]{64}\b', text)) == {
        validation['glb_sha256'], artwork['png_sha256']}
    assert f'{validation["glb_bytes"]:,}' in text and f'{artwork["png_bytes"]:,}' in text
    renders = []
    for name in ('hero', 'side', 'line_detail', 'overhead_47m_42deg'):
        path = EVIDENCE / f'{name}.png'
        raw = path.read_bytes()
        assert raw[:8] == b'\x89PNG\r\n\x1a\n'
        size = struct.unpack_from('>II', raw, 16)
        assert size == (1280, 720) and len(raw) < 400 * 1024
        renders.append({'file': path.name, 'size': size, 'bytes': len(raw)})
    validation.update({
        'artwork': artwork, 'engine': engine, 'roundtrip': roundtrip,
        'second_runtime_process_exact_match': True,
        'checks': {'final_import_error_lines': [], 'runtime_error_lines': [],
                   'gdstyle_format': 'PASS', 'gdstyle_lint': 'PASS: zero warnings',
                   'python_compile': 'PASS', 'production_checks_run': False,
                   'normalization_diagnostics': normalization,
                   'normalization_disposition': 'Two byte-stable passes; known editor shutdown '
                       'leaks and plugin warning retained, not a clean-log claim.'},
        'visual_review': {
            'renders_inspected': renders,
            'renderer': 'Isolated Blender Cycles CPU, 24 samples, AgX, RGB8 PNG compression 95',
            'camera': {'blender_position': [0, 0, 47], 'rotation_radians': [0, 0, 0],
                       'vertical_fov_degrees': 42, 'projection': 'perspective',
                       'framing': 'Entire court, north-up'},
            'observation': 'Broad ivory sidelines and four service boxes remain distinct at gameplay '
                'height; quiet green finish and darker apron stay subordinate to the field.',
            'studio_ground': 'Read-only existing short_grass PNG on unexported studio plane',
            'godot_visual_acceptance': False},
        'remaining_acceptance': [
            'Independent review and owner acceptance of provisional proportions/plot fit',
            'World placement, continuous supporting terrain, foot and car contacts',
            'Godot lighting, actor contrast, moving mip/depth review',
            'LOD, packaged builds, world multiplayer and sustained Deck/performance checks'],
    })
    (EVIDENCE / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n',
                                           encoding='utf-8', newline='\n')
    log = (
        'FINAL RECEIPT: d01_sports_surface.03\n'
        'Original Pillow artwork and Blender court-face construction. No external fonts/models.\n'
        'Pinned Blender author and validator completed normally; fresh export byte-identical.\n'
        '2 triangles, 4 source/export vertices, one mesh/surface; upward unit normals.\n'
        'Zero degenerates; four justified boundary edges, zero other non-manifold edges.\n'
        'PNG regeneration exact; 13 paint, 7 green and 6 apron samples; border/palette/coverage pass.\n'
        'Four 1280x720 evidence renders inspected; each below 400 KiB.\n'
        'Python syntax and GDScript format/zero-warning lint: PASS.\n'
        'Headless normalization exit 0; two byte-stable scene/material rounds and matching UIDs.\n'
        'Final pinned import exit 0; no ERROR/SCRIPT ERROR lines.\n'
        'Two fresh runtime checks exit 0; identical receipts, no ERROR/SCRIPT ERROR lines.\n'
        'Linked identity model, external opaque material, generated mips, no collision.\n'
        'No failed asset checks; GDScript formatting already matched the pinned style.\n'
        'No production_checks.py or owner live-session access. No world/gameplay changes.\n'
        'Editor warnings/shutdown leaks below are retained, not a clean editor-log pass:\n\n'
        + '\n'.join(normalization) + '\n'
    )
    (EVIDENCE / 'final.log').write_text(log, encoding='utf-8', newline='\n')
    roots = [ROOT / f'art/{category}/environment/{NID}' for category in
             ('source/models', 'models', 'textures', 'materials')]
    roots.extend([ROOT / f'tools/asset_production/{NID}', EVIDENCE, handoff,
                  ROOT / f'scenes/prefabs/environment/{NID}.tscn'])
    files = []
    for root in roots:
        for path in (sorted(root.rglob('*')) if root.is_dir() else [root]):
            if not path.is_file() or path.name == 'manifest.json' or '__pycache__' in path.parts:
                continue
            raw = path.read_bytes()
            if path.suffix in ('.py', '.gd', '.tscn', '.tres', '.import', '.md', '.json', '.uid', '.log'):
                assert b'\r\n' not in raw, f'Normalize LF before hashing: {path}'
            files.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': len(raw),
                          'sha256': hashlib.sha256(raw).hexdigest()})
    manifest = {'asset_id': 'd01_sports_surface.03',
                'producer': 'Commissioned isolated asset-production worker on lane/a-d01',
                'scope': 'Every delivery payload except self; scratch excluded',
                'files': sorted(files, key=lambda item: item['path'])}
    (EVIDENCE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n',
                                         encoding='utf-8', newline='\n')
    print(f'COURT_RECORD_PASS: {len(files)} final payload hashes; receipt/doc hashes agree')


if __name__ == '__main__':
    main()
