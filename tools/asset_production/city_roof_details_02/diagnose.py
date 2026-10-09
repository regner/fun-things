"""Retain exact degenerate polygon diagnosis before one owned fix cycle."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
rows=[]
for o in bpy.data.collections['export_city_roof_details_02'].objects:
 if o.type!='MESH': continue
 rows.append(dict(name=o.name,min_area=min(p.area for p in o.data.polygons),bad_faces=[dict(index=p.index,area=p.area,vertices=[list(o.data.vertices[v].co) for v in p.vertices]) for p in o.data.polygons if p.area<=1e-10]))
(R/'docs/assets/production/city_roof_details_02-evidence/initial_failure/geometry_diagnostic.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
