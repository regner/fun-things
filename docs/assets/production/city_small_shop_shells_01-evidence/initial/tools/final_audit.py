"""Compare saved-source reexport bytes and recheck immutable fitting inputs."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_small_shop_shells_01-evidence'
p=R/'art/models/environment/city_small_shop_shells_01/city_small_shop_shells_01.glb'; q=E/'reexport.glb'
assert p.read_bytes()==q.read_bytes()
a=json.loads((E/'source_export_checks.json').read_text()); b=json.loads((E/'reexport_checks.json').read_text()); assert a==b
s=json.loads((E/'source_assembly_checks.json').read_text()); g=json.loads((E/'glb_assembly_checks.json').read_text())
assert s['reference_hashes_before']==g['reference_hashes_before']
for path,digest in s['reference_hashes_before'].items(): assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
report={'byte_identical_saved_source_reexport':True,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_audit_identical':True,'all_fitting_source_export_report_hashes_unchanged':True,'geometry_triangles':a['triangles'],'scope':'Candidate source/export + numerical scratch assembly only'}
(E/'final_audit.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report))
