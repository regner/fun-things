"""Original Blender authoring for Regner's selected compact-combustion effects.

Run with Blender5.2.2 LTS --background --threads2 --python this_file.
Visible geometry is authored here, never constructed by Godot runtime code.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[5]
SOURCE = Path(__file__).with_name('weapon_effects_a.blend')
OUTPUT = ROOT / 'art/models/effects/weapon_effects'


def material(name, color, emission=0):
    """Create source-owned untextured colors; runtime particle overrides are explicit."""
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = 0.85
    shader.inputs['Emission Color'].default_value = color
    shader.inputs['Emission Strength'].default_value = emission
    return mat


def collection(name):
    """Declare one unique family output and its exact collection membership."""
    value = bpy.data.collections.new('export_weapon_effects_a_' + name)
    bpy.context.scene.collection.children.link(value)
    return value


def finish(obj, target, name, mat, smooth=True):
    """Bake static geometry transforms and triangles; retain an identity export pivot."""
    obj.name = name
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    triangulate = obj.modifiers.new('explicit_triangles', 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=triangulate.name)
    for face in obj.data.polygons:
        face.use_smooth = smooth
    obj.data.materials.append(mat)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    target.objects.link(obj)
    obj.select_set(False)
    return obj


def puff(target, name, axes, mat, shape=0):
    """Author a small smooth asymmetric rounded lobe with a centred emission pivot."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1)
    obj = bpy.context.object
    for vertex in obj.data.vertices:
        x,y,z = vertex.co
        wobble = 1 + shape * math.sin(math.atan2(y,x)*3) * (1-z*z)
        vertex.co = Vector((x*axes[0]*wobble, y*axes[1]*wobble, z*axes[2]))
    return finish(obj, target, name, mat)


def drop(target, name, length, width, height, mat):
    """Author a tapered flash facing Blender+Y, rooted at its emission point."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1)
    obj = bpy.context.object
    for vertex in obj.data.vertices:
        x,y,z = vertex.co
        along = (y+1)/2
        taper = 1 - 0.75*along
        vertex.co = Vector((x*width*taper, along*length, z*height*taper))
    return finish(obj,target,name,mat)


def box(target, name, size, position, mat, bevel=0):
    """Author stage geometry and deliberately non-colliding cosmetic fragments."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    if bevel:
        modifier=obj.modifiers.new('rounded_edges','BEVEL')
        modifier.width=bevel
        modifier.segments=2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return finish(obj,target,name,mat,smooth=bool(bevel))


def main():
    """Save editable Blender sources and explicit collection exports with measured bounds."""
    assert bpy.app.version_string == '5.2.2 LTS', bpy.app.version_string
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    scene.unit_settings.scale_length=1
    scene.render.fps=30
    scene['authorship']='Weapon effects lead (Codex), original bpy-authored art for Regner'
    scene['selection']='2026-10-09: A compact combustion; B retained as alternate'
    scene['axes']='Blender+Z up/+Y front; glTF maps to Godot+Y up/-Z front; metres'
    neutral=material('weapon_effects_a_particle',(1,1,1,1))
    amber=material('weapon_effects_a_flash_amber',(1,0.33,0.018,1),1.5)
    ivory=material('weapon_effects_a_flash_ivory',(1,0.9,0.58,1),2)
    outputs={name:collection(name) for name in
             ['muzzle_drop','fire_lobe','smoke_puff','spark','chip','trail_puff']}
    outer=drop(outputs['muzzle_drop'],'FlashOuter',0.66,0.27,0.16,amber)
    core=drop(outputs['muzzle_drop'],'FlashCore',0.43,0.12,0.075,ivory)
    core.location.z=0.075
    bpy.ops.object.select_all(action='DESELECT')
    outer.select_set(True)
    core.select_set(True)
    bpy.context.view_layer.objects.active=outer
    bpy.ops.object.join()
    outer.name='Shape'
    outer.select_set(False)
    puff(outputs['fire_lobe'],'Shape',(0.58,0.50,0.55),neutral,0.06)
    puff(outputs['smoke_puff'],'Shape',(0.70,0.62,0.48),neutral,0.12)
    # Long dimension is BlenderZ / GodotY for ALIGN_Y_TO_VELOCITY particles.
    puff(outputs['spark'],'Shape',(0.025,0.025,0.16),neutral)
    box(outputs['chip'],'Shape',(0.11,0.14,0.08),(0,0,0),neutral,0.016)
    puff(outputs['trail_puff'],'Shape',(0.20,0.20,0.16),neutral,0.05)
    bpy.ops.object.select_all(action='DESELECT')
    OUTPUT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    preset=json.loads((ROOT/'tools/s01/export_settings.json').read_text())
    records=[]
    for name,target in outputs.items():
        filepath=OUTPUT/f'weapon_effects_a_{name}.glb'
        settings=dict(preset,collection=target.name,export_animations=False,filepath=str(filepath))
        bpy.ops.export_scene.gltf(**settings)
        points=[obj.matrix_world@Vector(v) for obj in target.objects for v in obj.bound_box]
        # Convert Blender(x,y,z) -> Godot(x,z,-y).
        points=[(v.x,v.z,-v.y) for v in points]
        minimum=[min(v[axis] for v in points) for axis in range(3)]
        maximum=[max(v[axis] for v in points) for axis in range(3)]
        records.append({'id':f'weapon_effects_a_{name}','collection':target.name,
                        'members':[o.name for o in target.objects],
                        'minimum':minimum,'maximum':maximum,
                        'triangles':sum(len(o.data.polygons) for o in target.objects)})
    (SOURCE.parent/'geometry.json').write_text(json.dumps(records,indent=2)+'\n')
    print('WEAPON_EFFECTS_A_SOURCE_SAVED',str(SOURCE),len(records),'explicit GLBs')


if __name__=='__main__':
    main()
