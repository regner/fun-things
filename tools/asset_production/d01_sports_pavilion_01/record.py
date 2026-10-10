"""Consolidate final owned receipts and hash every delivered payload after checks and docs."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = 'd01_sports_pavilion_01'
EVIDENCE = ROOT / f'docs/assets/production/{NID}-evidence'
SCRATCH = Path(f'C:/tmp/ft/assets/{NID}')


def read_json(path):
    """Load a completed receipt, not an inferred process result."""
    return json.loads(path.read_text(encoding='utf-8'))


def diagnostics(path):
    """Retain actual diagnostic lines without treating an exit code as a clean log."""
    return [line for line in path.read_text(encoding='utf-8').splitlines()
            if re.search(r'(?:ERROR:|SCRIPT ERROR:|WARNING:)', line)]


validation = read_json(EVIDENCE / 'validation.json')
first = read_json(SCRATCH / 'prefab-check.json')
second = read_json(SCRATCH / 'prefab-second-process.json')
roundtrip = read_json(SCRATCH / 'roundtrip.json')
assert first == second and first['ok'] and not first['failures']
assert roundtrip['ok'] and roundtrip['save_reload_byte_stable']
assert first['prefab_uid'] == roundtrip['prefab_uid']
assert first['model_uid'] == roundtrip['model_uid']
assert len(first['physics_shape_queries']) == 15
assert len(first['footprint_face_ray_hits']) == 32
assert len(first['production_actor_motion']) == 2
for name in ('import-final', 'prefab-check', 'prefab-second-process'):
    errors = [line for line in diagnostics(SCRATCH / f'{name}.log') if 'ERROR:' in line]
    assert not errors, (name, errors)
normalization_diagnostics = diagnostics(SCRATCH / 'roundtrip.log')
normalization_errors = [line for line in normalization_diagnostics if 'ERROR:' in line]
assert all('RID allocations of type' in line and 'leaked at exit' in line
           for line in normalization_errors), normalization_errors
assert '1 file already formatted' in (SCRATCH / 'format.log').read_text(encoding='utf-8')
assert 'no issues found' in (SCRATCH / 'style.log').read_text(encoding='utf-8')
raw = (ROOT / f'art/models/environment/{NID}/{NID}.glb').read_bytes()
assert hashlib.sha256(raw).hexdigest() == validation['glb_sha256']
assert len(raw) == validation['glb_bytes']
assert validation['reexport_byte_identical']
handoff = (ROOT / f'docs/assets/production/{NID}.md').read_text(encoding='utf-8')
assert validation['glb_sha256'] in handoff
assert f"{validation['glb_bytes']:,}" in handoff
first['second_fresh_process_exact_match'] = True
first['save_reload_byte_stable'] = True
validation['engine'] = first
validation['checks'] = {
    'pinned_engine': '4.8.dev7.official.c971f93e7',
    'final_headless_import_error_lines': [],
    'owned_gdscript_format': 'PASS',
    'owned_gdscript_lint': 'PASS: zero warnings',
    'editor_normalization_diagnostics': normalization_diagnostics,
    'editor_normalization': 'Exit 0, byte-stable save/reload and matching UIDs; shutdown '
        'RID/ObjectDB leaks and scan-abort warning remain. Not a clean editor-log claim.',
    'production_checks_run': False,
}
renders = []
for name in ('hero', 'side', 'entry_detail', 'overhead_47m_42deg'):
    path = EVIDENCE / f'{name}.png'
    raw = path.read_bytes()
    assert raw[:8] == b'\x89PNG\r\n\x1a\n'
    width, height = struct.unpack_from('>II', raw, 16)
    assert (width, height) == (1280, 720)
    assert len(raw) < 400 * 1024
    renders.append({'file': path.name, 'width': width, 'height': height, 'bytes': len(raw)})
validation['visual_review'] = {
    'renders_inspected': renders,
    'observation': 'Whole crescent fits the calibrated overhead; quiet slate roof, four '
        'broad seams, open field-side negative space and no tower. Hero/side show two rear '
        'service wedges supporting a column-free canopy; detail shows closed amber/mint '
        'service entrance. Coplanar fascia and wall-band flicker corrected before final renders.',
    'renderer': 'Isolated Blender Cycles CPU, 32 samples, AgX; not Godot visual acceptance',
    'gameplay_camera': {'blender_position_m': [0, 0, 47], 'rotation_radians': [0, 0, 0],
                        'vertical_fov_degrees': 42, 'projection': 'perspective'},
    'png': 'RGB8, compression 95, dither disabled; no post-processing',
}
(EVIDENCE / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n', newline='\n')
summary = (
    'FINAL ASSET RECEIPT: d01_sports_pavilion.01\n'
    'Pinned Blender author and validator: exit 0; 5.2.2 LTS / exporter 5.2.40.\n'
    '8,718 triangles; 4,499 source / 5,395 GLB vertices; one mesh, seven surfaces.\n'
    'Zero degenerate source faces / GLB triangles; zero source non-manifold edges.\n'
    'Source/export normals, identity transforms, metre bounds and byte reexport PASS.\n'
    'Two eight-point dimension-authored convex wedges match source corners within 0.00001 m.\n'
    'Four final 1280x720 renders inspected; coplanar fascia/wall-band issue corrected.\n'
    'Blender version-only invocation reported one 0.000023 MB allocation at shutdown;\n'
    'actual author/validator complete normally (only Blender 6.0 future deprecation notices).\n'
    'Headless editor normalization: exit 0, stable second save and generated UIDs.\n'
    'Editor shutdown diagnostics below are retained, not called a clean-log pass.\n'
    'Initial style test found long/local-heavy/nested physics checker; split into named helpers.\n'
    'A later overlong clearance expression was split; final lint is zero-warning.\n'
    'Initial movement assertion incorrectly expected a fixed-axis stop on a slanted wall;\n'
    'replaced by independent plane/capsule-clearance and actual deflection expectations.\n'
    'Final format and zero-warning lint: exit 0.\n'
    'Final pinned import: exit 0, no ERROR/SCRIPT ERROR lines.\n'
    'Two fresh runtime checks: exit 0, no errors, exact matching JSON receipts.\n'
    '15 solid/clear queries, 32 literal face rays and six production ActorMotion cases PASS.\n'
    'Authority/replay match; no real transport, placement, car or device acceptance claimed.\n'
    'No production_checks.py invocation (decision 52).\n\n'
    'Editor normalization diagnostics (retained):\n'
    + '\n'.join(normalization_diagnostics) + '\n\n'
    + (SCRATCH / 'format.log').read_text(encoding='utf-8')
    + (SCRATCH / 'style.log').read_text(encoding='utf-8')
)
(EVIDENCE / 'final.log').write_text(summary, encoding='utf-8', newline='\n')
paths = [ROOT / f'art/source/models/environment/{NID}',
         ROOT / f'art/models/environment/{NID}', ROOT / f'tools/asset_production/{NID}',
         EVIDENCE, ROOT / f'docs/assets/production/{NID}.md',
         ROOT / f'scenes/prefabs/environment/{NID}.tscn']
files = []
for path in paths:
    for item in (sorted(path.rglob('*')) if path.is_dir() else [path]):
        if item.is_file() and item.name != 'manifest.json' and '__pycache__' not in item.parts:
            raw = item.read_bytes()
            files.append({'path': item.relative_to(ROOT).as_posix(), 'bytes': len(raw),
                          'sha256': hashlib.sha256(raw).hexdigest()})
manifest = {'asset_id': 'd01_sports_pavilion.01',
            'producer': 'Commissioned isolated asset-production worker on lane/a-d01',
            'scope': 'Every produced payload except this self-referential manifest; no scratch',
            'files': sorted(files, key=lambda item: item['path'])}
(EVIDENCE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', newline='\n')
print(f'PASS: final source, engine, style and visual receipts; {len(files)} payload hashes')
