import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='/tmp/six-engine-review-c4067ff/docs/assets/production/batch_01-evidence/calibration/five-source-metre-comparison.blend')
rows=[dict(name=o.name,type=o.type,instance_type=o.instance_type,instance_collection=o.instance_collection.name if o.instance_collection else None,library=o.library.filepath if o.library else None,location=list(o.location)) for o in bpy.data.objects]
Path(__file__).with_name('calibration-inventory.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps([o for o in rows if o['instance_type']=='COLLECTION'],indent=2))
