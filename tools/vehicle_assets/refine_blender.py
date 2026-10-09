"""Astra-authored rigid door refinement of the preserved first-pass Blender sources."""
import importlib.util
import json
from pathlib import Path

import bpy
from mathutils import Vector

module_spec=importlib.util.spec_from_file_location('car_author',Path(__file__).with_name('author_blender.py'))
a=importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(a)


def boolean(obj, cutter, operation):
    """Apply a source-only solid operation; cutters never enter the export collection."""
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('source_door_'+operation.lower(),'BOOLEAN')
    mod.operation=operation;mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)


def cutter(size, position):
    """Create a temporary axis-aligned source cutter with applied scale."""
    bpy.ops.mesh.primitive_cube_add(size=1,location=position)
    obj=bpy.context.object;obj.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    return obj


def panel(col, parent, name, points, material):
    """Create a slightly thick glass panel from an explicitly authored quadrilateral."""
    obj=a.mesh(col,parent,name,points,[(0,1,2,3)],material,0)
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('glass_thickness','SOLIDIFY');mod.thickness=.008
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def reparent_world(obj, parent):
    """Retain the closed assembled pose while making the rigid hinge the sole pivot."""
    pose=obj.matrix_world.copy();obj.parent=parent
    obj.matrix_world=pose


def refine(spec):
    """Cut true side openings and author door panels/windows around front-edge hinges."""
    asset=spec['id'];source=a.SOURCES/(asset+'.blend')
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert Path(bpy.data.filepath).resolve()==source.resolve()
    assert bpy.data.objects.get('Doors') is None,'Refinement is one-time; edit saved source thereafter'
    col=bpy.data.collections['export_'+asset];root=bpy.data.objects[asset]
    body=bpy.data.objects['Body'];W,H=spec['width'],spec['height']
    mats={name:bpy.data.materials[name] for name in ['glass','body_paint','trim','tire','wheel_hub']}
    gf,gb=spec['glass_front'],spec['glass_back']
    rf,rb=spec['roof_front'],spec['roof_back'];lo=1.06;hi=H-.035
    low_width=(W-.34)/2;high_width=spec['roof_width']/2
    bpy.data.objects.remove(bpy.data.objects['CabinGlass'],do_unlink=True)
    # Roof remains independent; windshield and rear glazing remain fixed to the body.
    panel(col,root,'Windshield',[(-low_width,gf,lo),(low_width,gf,lo),
        (high_width,rf,hi),(-high_width,rf,hi)],mats['glass'])
    panel(col,root,'RearGlass',[(low_width,gb,lo),(-low_width,gb,lo),
        (-high_width,rb,hi),(high_width,rb,hi)],mats['glass'])
    well=cutter((W-.55,gf-gb-.20,1.2),(0,(gf+gb)/2,.50+.60))
    boolean(body,well,'DIFFERENCE');bpy.data.objects.remove(well,do_unlink=True)
    a.box(col,root,'CabinFloor',(W-.53,gf-gb-.18,.08),(0,(gf+gb)/2,.50),mats['trim'],.03)
    for sign in (-1,1):
        a.box(col,root,'SeatCushion_'+str(sign),(.47,.51,.16),(sign*.34,-.17,.66),mats['trim'],.06)
        a.box(col,root,'SeatBack_'+str(sign),(.47,.14,.43),(sign*.34,-.40,.92),mats['trim'],.06)
    a.box(col,root,'Dashboard',(W-.57,.20,.19),(0,gf-.12,.94),mats['trim'],.05)
    doors=a.empty(col,'Doors',root)
    seam=-.27
    spans=[('Front',gb+.05,gf-.08)] if asset=='car_latch_a' else [
        ('Front',seam+.02,gf-.08),('Rear',gb+.07,seam-.02)]
    for side,sign in [('Left',-1),('Right',1)]:
        for end,yback,yfront in spans:
            hinge=a.empty(col,'Hinge'+end+side,doors,(sign*(W/2-.12),yfront,.56))
            cut=cutter((.41,yfront-yback-.018,.65),
                (sign*(W/2-.11),(yfront+yback)/2,.785))
            door=body.copy();door.data=body.data.copy();col.objects.link(door)
            door.name='DoorPanel'+end+side
            boolean(door,cut,'INTERSECT');boolean(body,cut,'DIFFERENCE')
            bpy.data.objects.remove(cut,do_unlink=True)
            bpy.context.view_layer.update();reparent_world(door,hinge)
            top_front=rf if end=='Front' else seam-.04
            top_back=rb if end=='Rear' or asset=='car_latch_a' else seam+.04
            glass=panel(col,root,'DoorWindow'+end+side,[
                (sign*low_width,yfront,lo),(sign*low_width,yback,lo),
                (sign*high_width,top_back,hi-.025),(sign*high_width,top_front,hi-.025)],mats['glass'])
            bpy.context.view_layer.update();reparent_world(glass,hinge)
            handle=a.box(col,root,'DoorHandle'+end+side,(.045,.17,.05),
                (sign*(W/2-.06),yback+.17,.94),mats['trim'],.02)
            bpy.context.view_layer.update();reparent_world(handle,hinge)
            if end=='Front':
                mirror=bpy.data.objects['Mirror'+side]
                bpy.context.view_layer.update();reparent_world(mirror,hinge)
    # Triangulate the final boolean panels explicitly; no runtime geometry or modifiers.
    for obj in col.all_objects:
        if obj.type=='MESH':
            bpy.context.view_layer.objects.active=obj
            mod=obj.modifiers.new('final_export_triangles','TRIANGULATE')
            bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    settings=json.loads((a.ROOT/'tools/s01/export_settings.json').read_text())
    settings.update(export_animations=False,export_skins=False,collection=col.name,
        filepath=str(a.OUTPUT/(asset+'.glb')))
    bpy.ops.export_scene.gltf(**settings)
    record_path=a.RECORDS/(asset+'_source.json');record=json.loads(record_path.read_text())
    record.update(members=sorted(o.name for o in col.all_objects),door_hinges=sorted(o.name for o in doors.children),
        rigid_animation_contract='Hinge rotation around Godot +Y; wheel spin around local +X; no skin/armature',
        spatial_author='gpt-6-astra high; runtime verified in active codex-turn-6',
        triangles=sum(len(o.data.polygons) for o in col.all_objects if o.type=='MESH'))
    points=[o.matrix_world@Vector(c) for o in col.all_objects if o.type=='MESH' for c in o.bound_box]
    low=[min(p[i] for p in points) for i in range(3)];high=[max(p[i] for p in points) for i in range(3)]
    record.update(godot_aabb_min=[low[0],low[2],-high[1]],godot_aabb_max=[high[0],high[2],-low[1]])
    record_path.write_text(json.dumps(record,indent=2)+'\n')
    print('DOORS_SAVED',asset,record['door_hinges'],flush=True)


for spec in a.SPECS:refine(spec)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
asset='car_preview_stage';col=bpy.data.collections.new('export_'+asset);scene.collection.children.link(col)
root=a.empty(col,asset)
road=a.material('preview_road',(34,53,63),.93)
line=a.material('preview_line',(150,170,167),.9)
a.box(col,root,'Ground',(64,44,.10),(0,0,-.05),road,.01)
for x in (-6,0,6):
    for y in (-4,4):a.box(col,root,'BayMark',(.065,1,.015),(x,y,.01),line,.003)
source=a.SOURCES/(asset+'.blend');assert not source.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(source))
settings=json.loads((a.ROOT/'tools/s01/export_settings.json').read_text())
settings.update(export_animations=False,export_skins=False,collection=col.name,filepath=str(a.OUTPUT/(asset+'.glb')))
bpy.ops.export_scene.gltf(**settings)
(a.RECORDS/(asset+'_source.json')).write_text(json.dumps({'id':asset,'source':str(source.relative_to(a.ROOT)),
    'export':str((a.OUTPUT/(asset+'.glb')).relative_to(a.ROOT)),'collection':col.name,
    'members':sorted(o.name for o in col.all_objects),'purpose':'Blender-authored cosmetic preview floor, no collision'},indent=2)+'\n')
print('VEHICLE_REFINEMENT_COMPLETE',flush=True)
