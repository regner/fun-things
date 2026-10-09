"""Explain GLB import helper geometry before reporting actor scale."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'art/models/characters/coral_courier/coral_courier.glb'))
rows=[]
for ob in bpy.data.objects:
    rows.append({'name':ob.name,'type':ob.type,'scene_member':ob.name in bpy.context.scene.objects,'hide_render':ob.hide_render,'hide_viewport':ob.hide_viewport,'visible_get':ob.visible_get(),'collections':[c.name for c in ob.users_collection],'vertices':len(ob.data.vertices) if ob.type=='MESH' else None,'polygons':len(ob.data.polygons) if ob.type=='MESH' else None})
print(json.dumps(rows,indent=2))
