"""Compare actual saved-source reexport and final source/export audit observations."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_05-evidence'
a=R/'art/models/environment/city_shop_fittings_05/city_shop_fittings_05.glb';b=E/'reexport_city_shop_fittings_05.glb'
assert a.read_bytes()==b.read_bytes(),'Saved-source export differs'
s=json.loads((E/'source_export_checks.json').read_text());r=json.loads((E/'reexport_checks.json').read_text())
assert s==r
assert json.loads((E/'interface_checks.json').read_text())['passed']
report=dict(saved_source_reexport_byte_identical=True,bytes=a.stat().st_size,sha256=hashlib.sha256(a.read_bytes()).hexdigest(),source_sha256=hashlib.sha256((R/'art/source/models/environment/city_shop_fittings_05/city_shop_fittings_05.blend').read_bytes()).hexdigest(),source_and_reexport_reports_equal=True,triangles=s['triangles'],mesh_count=len(s['objects']),passed=True)
(E/'final_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
