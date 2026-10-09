"""Freeze check results, preview receipt completeness and unchanged delivery bytes."""
import json,hashlib,struct,re
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_08-evidence'
def read(name):return json.loads((E/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read('source_export_checks.json');reexport=read('reexport_checks.json');a=read('attachment_and_reexport_checks.json');g=read('glb_checks.json')[0];p=read('preview_checks.json')
source=R/'art/source/models/environment/city_shop_fittings_08/city_shop_fittings_08.blend';glb=R/'art/models/environment/city_shop_fittings_08/city_shop_fittings_08.glb'
assert sha(source)==a['source_sha256']
assert glb.read_bytes()==(E/'reexport_city_shop_fittings_08.glb').read_bytes()
assert sha(glb)==s['sha256']==reexport['sha256']==a['glb_sha256']
assert s['triangles']==g['triangles']==3624 and len(s['objects'])==16
assert len(g['artwork_uv_checks'])==2 and a['saved_source_byte_identical_reexport']
assert p['reference_dimensions_m']==[1,1,1]
assert len(p['views'])==8
expected={'hero','bracket_detail','source_elevation','measured_1m_comparison','uv_positive_x','uv_negative_x','mounting_preview','project_camera'}
assert {Path(v['file']).stem for v in p['views']}==expected
for v in p['views']:
    b=(E/v['file']).read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n'
    assert list(struct.unpack('>II',b[16:24]))==v['resolution']
assert next(v for v in p['views'] if v['file']=='measured_1m_comparison.png')['orthographic_scale']==2.8
receipts=read('execution.json')
assert all(r['exit_status']==(127 if r['label']=='requested_pin' else 0) for r in receipts)
assert all(not r['terminated_owned_process'] for r in receipts)
report_path=R/'docs/assets/production/city_shop_fittings_08.md'
for target in re.findall(r'\]\(([^)]+)\)',report_path.read_text()):
    if target.endswith('manifest.json'):continue
    assert (report_path.parent/target).exists(),target
result={'status':'PASS','source_sha256':sha(source),'source_bytes':source.stat().st_size,'glb_sha256':sha(glb),'glb_bytes':glb.stat().st_size,'triangles':3624,'editable_meshes':16,'source_unchanged_through_previews':True,'saved_source_byte_identical_reexport':True,'eight_previews_with_complete_camera_receipts':True,'report_links_resolve':True,'prior_subprocess_receipts':len(receipts),'retained_launch_failure':'Requested binary pathname absent, exit 127; exact authorized build verified at /usr/bin/blender','self_visual_check':'Hero, bracket, elevation, dimension sheet, metre reference, both asymmetric UV charts, mounting jig and project-camera view inspected. Evidence fix resolved label overlap/cropping/perspective comparison. No independent acceptance claimed.','pending':['Godot import','prefab','save/reopen','real-shell mounting','collision','runtime/network','device/performance','world placement','independent technical/art acceptance']}
(E/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
