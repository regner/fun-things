"""Consolidate final observed checks and hash every produced entrance-artwork file."""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
NID='d03_community_graphics_02'
EVIDENCE=ROOT/f'docs/assets/production/{NID}-evidence'
SCRATCH=Path(f'C:/tmp/ft/assets/{NID}')


def fingerprint(path):
    """Hash final payload bytes, not metadata or an intermediate export."""
    raw=path.read_bytes()
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


def receipt(path):
    """Read actual validator receipts with explicit UTF-8 encoding."""
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    """Require passing receipts, verify dependencies and handoff, then generate the manifest last."""
    validation=receipt(EVIDENCE/'validation.json')
    artwork=receipt(SCRATCH/'artwork-check.json')
    engine=receipt(SCRATCH/'prefab-check.json')
    roundtrip=receipt(SCRATCH/'roundtrip.json')
    assert validation['status']=='PASS' and validation['fresh_reexport_byte_identical']
    assert artwork['ok'] and artwork['byte_identical_reproduction']
    assert engine['ok'] and roundtrip['ok']
    assert engine==receipt(SCRATCH/'prefab-first-process.json')
    assert roundtrip['fresh_process_initial_byte_stable']
    assert all(roundtrip[f'roundtrip_{i}_byte_stable'] for i in (1,2))
    for path,value in validation['dependencies'].items():
        assert fingerprint(ROOT/path)==value,path
    for path,value in roundtrip['resource_hashes'].items():
        assert fingerprint(ROOT/path.removeprefix('res://'))['sha256']==value,path
    assert fingerprint(ROOT/f'art/source/models/environment/{NID}/{NID}.blend')==validation['source']
    assert fingerprint(ROOT/f'art/models/environment/{NID}/{NID}.glb')==validation['glb']
    for number,value in artwork['textures'].items():
        assert fingerprint(ROOT/f'art/textures/environment/{NID}/entrance_{number}_albedo.png')==value
    warnings=[]
    for name in ('import-final','roundtrip','prefab-check','prefab-second-process'):
        text=(SCRATCH/f'{name}.log').read_text(encoding='utf-8')
        assert 'ERROR' not in text,name
        warnings += [line for line in text.splitlines() if 'WARNING' in line]
    assert '1 file already formatted' in (SCRATCH/'format.log').read_text(encoding='utf-8')
    assert 'no issues found' in (SCRATCH/'style.log').read_text(encoding='utf-8')
    assert 'PYTHON_COMPILE_PASS' in (SCRATCH/'python-check.log').read_text(encoding='utf-8')
    renders=[]
    for name in ('hero','side','detail','overhead_47m_42deg'):
        path=EVIDENCE/f'{name}.png'
        with Image.open(path) as image:
            assert image.size==(1280,720) and image.mode=='RGB'
        assert path.stat().st_size<400*1024
        renders.append({'file':path.name,'dimensions':[1280,720],**fingerprint(path)})
    doc=ROOT/f'docs/assets/production/{NID}.md'
    text=doc.read_text(encoding='utf-8')
    assert set(re.findall(r'\b[0-9a-f]{64}\b',text))=={
        validation['source']['sha256'],validation['glb']['sha256']}
    for key in ('source','glb'):
        assert f"{validation[key]['bytes']:,}" in text
    validation.update({
        'artwork':artwork,'engine':engine,'roundtrip':roundtrip,
        'second_fresh_process_receipt_identical':True,
        'checks':{'final_import_error_lines':[],'runtime_error_lines':[],
                  'warnings':warnings,'python_compile':'PASS',
                  'gdstyle_format':'PASS','gdstyle_lint':'PASS: zero warnings',
                  'production_checks_run':False},
        'visual_self_review':{
            'renders_inspected':renders,'renderer':'Blender Cycles CPU, 32 samples, AgX',
            'encoding':'RGB8 PNG compression 95; no dithering or post-quantization',
            'overhead':{'position_blender_m':[0,0,47],'vertical_fov_degrees':42,
                        'north_up':True,'projection':'perspective'},
            'observation':'Four upright, distinct numbers use quiet teal/ivory and one coral accent. '
                          'Hero and side show the plaque fitting the pier with no overlap. '
                          'The isolated four-option detail is a swatch review, not world placement. '
                          'Overhead the building top occludes the vertical plaque; no essential '
                          'navigation or overhead-readable number is claimed.',
            'godot_gameplay_visual_acceptance':False},
        'remaining_acceptance':['Independent technical/art review and provisional four-number set',
                                'World placement, actual Godot views and moving-camera mip review',
                                'Packaged dependencies, repeat cost and target-device performance']})
    (EVIDENCE/'validation.json').write_text(
        json.dumps(validation,indent=2)+'\n',encoding='utf-8',newline='\n')
    log='''FINAL CHECKS: d03_community_graphics.02
Original four-number Pillow artwork: three independent tests pass; PNGs byte-identical.
Pinned Blender source/export validator and four-view preview exited 0.
156 triangles, 80 source / 280 GLB vertices, 1 mesh / 2 surfaces.
Zero degenerates/nonmanifold edges; unit normals, literal AABB and upright UVs pass.
Fresh saved-source GLB re-export is byte-identical; all shared payloads unchanged.
Four 1280x720 RGB evidence renders inspected; every render below 400 KiB.
Final pinned import and two fresh resource checks exited 0, no ERROR/SCRIPT ERROR lines.
Two complete byte-stable scene/material roundtrips; fresh-process initial bytes stable.
Header/dependency UIDs and node identities resolve; one identity-transform linked model.
Four actual material options affect face slot 0 only; all imported RGB8 mip chains pass.
Mounted plaque has 55 mm pier-side clearances; zero added collision, one existing wall box.
Python syntax, gdstyle format and 100-column zero-warning lint pass.
Initial test reproduction omitted PNG format on a BytesIO stream; fixed explicitly.
Initial lint flagged two allocations in loops; extracted scene repack and reused config.
Initial authoring shell payload was truncated; completed the test file before running it.
No failed attempt is treated as passing, and no diagnostics were suppressed.
Blender emits its pinned use_nodes future-removal warning.
No production_checks.py, live-editor access, sibling edits or gameplay changes.
Final engine warnings:
'''+ '\n'.join(warnings)+'\n'
    (EVIDENCE/'checks.log').write_text(log,encoding='utf-8',newline='\n')
    roots=[ROOT/f'art/{category}/environment/{NID}' for category in
           ('source/models','models','materials','textures')]
    roots += [ROOT/f'tools/asset_production/{NID}',EVIDENCE,doc,
              ROOT/f'scenes/prefabs/environment/{NID}.tscn']
    files=[]
    for root in roots:
        for path in sorted(root.rglob('*')) if root.is_dir() else [root]:
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            if path==EVIDENCE/'manifest.json':
                continue
            if path.suffix not in ('.blend','.glb','.png'):
                assert b'\r\n' not in path.read_bytes(),path
            files.append({'path':path.relative_to(ROOT).as_posix(),**fingerprint(path)})
    manifest={'asset_id':'d03_community_graphics.02','producer':'worker on lane/a-d03g',
              'scope':'Every produced file except this manifest; shared dependencies in validation',
              'files':sorted(files,key=lambda v:v['path'])}
    (EVIDENCE/'manifest.json').write_text(
        json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'ENTRANCE_RECORD_PASS: {len(files)} final payloads, receipts and document agree')


if __name__=='__main__':
    main()
