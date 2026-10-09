"""Bootstrap ONLY the new neutral S06 intersection; refuse existing source overwrite."""
import json
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'art/source/models/spikes/s06_intersection.blend'
assert not source.exists()
assert bpy.app.version_string=='5.2.2 LTS'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1
mats={}
for name,rgb in {'road':(18,54,70),'walk':(133,146,157),'mark':(246,241,220),'island':(21,86,79)}.items():
 m=bpy.data.materials.new(name);m.use_nodes=True
 color=tuple(((v/255+.055)/1.055)**2.4 if v>10 else v/3294.6 for v in rgb)
 next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(*color,1)
 next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Roughness'].default_value=.8
 mats[name]=m

def box(col,name,size,pos,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(pos[0],-pos[2],pos[1]))
 obj=bpy.context.object;obj.name=name;obj.scale=(size[0],size[2],size[1])
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 for old in list(obj.users_collection):old.objects.unlink(obj)
 col.objects.link(obj);obj.data.materials.append(mats[material])
 mod=obj.modifiers.new('triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
for side,sign in [('west',-1),('east',1)]:
 col=bpy.data.collections.new('export_s06_'+side);bpy.context.scene.collection.children.link(col)
 box(col,'RoadHorizontal_'+side,(24,.2,9),(sign*12,-.1,0),'road')
 for zsign,label in [(-1,'North'),(1,'South')]:
  box(col,'RoadVertical'+label+'_'+side,(4.5,.2,19.5),(sign*2.25,-.1,zsign*14.25),'road')
  box(col,'WalkHorizontal'+label+'_'+side,(19.5,.2,4),(sign*14.25,-.085,zsign*6.5),'walk')
  box(col,'WalkVertical'+label+'_'+side,(4,.2,15.5),(sign*6.5,-.085,zsign*16.25),'walk')
  box(col,'Island'+label+'_'+side,(15.5,.6,15.5),(sign*16.25,.3,zsign*16.25),'island')
 # Crosswalk spans vertical road at Z6.5. Two halves meet exactly at X0.
 for index in range(4):
  box(col,'Crossing_%s_%s'%(side,index),(.5,.02,3),(sign*(.5+index),.01,6.5),'mark')
 for x in range(10,24,4):
  box(col,'Centre_%s_%s'%(side,x), (2,.02,.12),(sign*x,.01,0),'mark')
manifest={c.name:sorted(o.name for o in c.all_objects) for c in bpy.context.scene.collection.children}
(ROOT/'tools/s06/export_members.json').write_text(json.dumps(manifest,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print('S06_SOURCE',bpy.app.version_string,bpy.app.build_hash,source)
