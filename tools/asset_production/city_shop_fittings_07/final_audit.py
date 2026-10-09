"""Verify exact saved-source reproduction, export agreement and completed evidence."""
import json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_07-evidence'
src=R/'art/source/models/environment/city_shop_fittings_07/city_shop_fittings_07.blend'
glb=R/'art/models/environment/city_shop_fittings_07/city_shop_fittings_07.glb'
re=E/'reexport_city_shop_fittings_07.glb'
assert glb.read_bytes()==re.read_bytes()
a=json.loads((E/'source_export_checks.json').read_text());b=json.loads((E/'reexport_checks.json').read_text());assert a==b
payload=json.loads((E/'glb_checks.json').read_text())[0]
assert payload['triangles']==a['triangles']==1760
assert json.loads((E/'interface_checks.json').read_text())['checks']=='PASS'
views=json.loads((E/'preview_checks.json').read_text())
for row in views['views']:
    data=(E/row['file']).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
    assert list(struct.unpack('>II',data[16:24]))==row['resolution']
records=json.loads((E/'execution.json').read_text())
for label in ['pin','author','export','glb_check','interface','previews','reexport','commission_snapshot']:
    assert any(r['label']==label and r['exit_status']==0 for r in records),label
report={'checks':'PASS','saved_source_byte_identical_reexport':True,'source_export_reports_identical':True,'triangles':a['triangles'],'production_files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [src,glb,re]],'views_verified':[v['file'] for v in views['views']],'limits':'No Godot import, prefab, collision, runtime, device, actual-shell attachment or independent acceptance.'}
(E/'final_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
