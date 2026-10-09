"""Author the original shared humanoid v1 rest rig and technical bind template.

Run only in a private Blender 5.2.2 process. The saved blend is the reusable source;
this bootstrap is not runtime geometry and must not overwrite later manual edits.
"""
from pathlib import Path
import hashlib
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'art/source/models/characters/shared_humanoid/shared_humanoid_v1.blend'
OUTPUT = ROOT / 'art/models/characters/shared_humanoid/shared_humanoid_bind_v1.glb'
COLLECTION = 'export_shared_humanoid_bind_v1'


def definitions():
    """Declare a metre-based A-pose with ground root and anatomical hinge joints."""
    bones = [
        ('root', (0, 0, 0), (0, 0, .16), None),
        ('pelvis', (0, 0, .92), (0, 0, 1.03), 'root'),
        ('spine', (0, 0, 1.03), (0, 0, 1.20), 'pelvis'),
        ('chest', (0, 0, 1.20), (0, 0, 1.40), 'spine'),
        ('neck', (0, 0, 1.40), (0, 0, 1.51), 'chest'),
        ('head', (0, 0, 1.51), (0, 0, 1.77), 'neck'),
    ]
    for side, sign in [('r', 1), ('l', -1)]:
        point = lambda x, y, z: (sign * x, y, z)
        bones.extend([
            (f'clavicle_{side}', point(.07, 0, 1.37), point(.245, 0, 1.38), 'chest'),
            (f'upper_arm_{side}', point(.245, 0, 1.38), point(.445, 0, 1.16), f'clavicle_{side}'),
            (f'forearm_{side}', point(.445, 0, 1.16), point(.635, .015, .96), f'upper_arm_{side}'),
            (f'hand_{side}', point(.635, .015, .96), point(.730, .025, .87), f'forearm_{side}'),
            (f'thumb_{side}', point(.662, .053, .951), point(.713, .093, .921), f'hand_{side}'),
            (f'index_{side}', point(.718, .060, .89), point(.780, .062, .833), f'hand_{side}'),
            (f'fingers_{side}', point(.726, .010, .878), point(.784, .008, .823), f'hand_{side}'),
            (f'thigh_{side}', point(.135, 0, .92), point(.14, .025, .50), 'pelvis'),
            (f'shin_{side}', point(.14, .025, .50), point(.14, 0, .12), f'thigh_{side}'),
            (f'foot_{side}', point(.14, 0, .12), point(.14, .17, .07), f'shin_{side}'),
            (f'toe_{side}', point(.14, .17, .07), point(.14, .29, .065), f'foot_{side}'),
        ])
    return bones


def move_collection(obj, collection):
    """Put an authored object exclusively in its declared export collection."""
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)


def ellipsoid(collection, name, center, radius, material, bone):
    """Make a smooth technical bind-template body piece with explicit one-bone skin."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = radius
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    move_collection(obj, collection)
    obj.data.materials.append(material)
    for face in obj.data.polygons:
        face.use_smooth = True
    obj.vertex_groups.new(name=bone).add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
    return obj


def main():
    """Save the source, exact rest matrices and explicit technical-template export."""
    assert bpy.app.version_string == '5.2.2 LTS', bpy.app.version_string
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    scene.render.fps = 30
    collection = bpy.data.collections.new(COLLECTION)
    scene.collection.children.link(collection)
    bpy.ops.object.armature_add()
    rig = bpy.context.object
    rig.name = 'Rig'
    rig.data.name = 'shared_humanoid_v1'
    move_collection(rig, collection)
    bpy.ops.object.mode_set(mode='EDIT')
    rig.data.edit_bones.remove(rig.data.edit_bones[0])
    for name, head, tail, parent in definitions():
        bone = rig.data.edit_bones.new(name)
        bone.head, bone.tail, bone.roll = head, tail, 0
        bone.use_connect = False
        if parent:
            bone.parent = rig.data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.show_in_front = True
    rig['rig_contract'] = 'shared_humanoid/1.0.0'
    rig['front'] = '+Y Blender / -Z Godot'
    rig['side_convention'] = 'r = +X; l = -X in authored rest'
    rig['source_owner'] = 'player_character lead; original project rig'
    mat = bpy.data.materials.new('bind_template_ivory')
    mat.diffuse_color = (.63, .59, .48, 1)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = mat.diffuse_color
    bsdf.inputs['Roughness'].default_value = .8
    parts = [
        ellipsoid(collection, 'TemplatePelvis', (0,0,.94), (.22,.135,.14),mat,'pelvis'),
        ellipsoid(collection, 'TemplateTorso', (0,0,1.20), (.25,.15,.24),mat,'chest'),
        ellipsoid(collection, 'TemplateHead', (0,0,1.645), (.145,.14,.155),mat,'head'),
    ]
    for name, head, tail, parent in definitions():
        if name.startswith(('upper_arm','forearm','thigh','shin','foot','hand','thumb','index','fingers')):
            a,b=Vector(head),Vector(tail)
            r=.055 if name.startswith(('hand','thumb','index','fingers')) else .075
            obj=ellipsoid(collection,'Template_'+name,(a+b)*.5,(r,r,(b-a).length*.55),mat,name)
            # Geometry rotates around the piece centre, leaving unit object transforms.
            from mathutils import Matrix
            centre=(a+b)*.5
            rot=Vector((0,0,1)).rotation_difference(b-a).to_matrix().to_4x4()
            matrix=Matrix.Translation(centre) @ rot @ Matrix.Translation(-centre)
            obj.data.transform(matrix)
            parts.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts: part.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    skin=bpy.context.object
    skin.name='BindTemplate'
    skin.parent=rig
    modifier=skin.modifiers.new('SharedRig','ARMATURE')
    modifier.object=rig
    # No templates or helper geometry become a production player skin.
    skin['purpose']='technical rest/clip carrier; not production character art'
    rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    rest=[]
    for bone in rig.data.bones:
        rest.append({'name':bone.name,'parent':bone.parent.name if bone.parent else None,
                     'head_blender_m':list(bone.head_local),'tail_blender_m':list(bone.tail_local),
                     'matrix_blender_armature': [list(row) for row in bone.matrix_local]})
    serialized=json.dumps(rest,sort_keys=True,separators=(',',':'))
    fingerprint=hashlib.sha256(serialized.encode()).hexdigest()
    rig['rest_sha256']=fingerprint
    SOURCE.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    settings=json.loads((ROOT/'tools/s01/export_settings.json').read_text())
    settings.update(collection=COLLECTION,export_animations=False,filepath=str(OUTPUT))
    bpy.ops.export_scene.gltf(**settings)
    manifest={'contract':'shared_humanoid/1.0.0','source':str(SOURCE.relative_to(ROOT)),
              'export':str(OUTPUT.relative_to(ROOT)),'collection':COLLECTION,
              'members':['Rig','BindTemplate'],'rest_sha256':fingerprint,'bones':rest,
              'blender_version':bpy.app.version_string,'blender_build':bpy.app.build_hash.decode(),
              'units':'metres','height_reference_m':1.8,'rest_pose':'A pose',
              'skin_rules':{'max_influences':4,'weight_sum_tolerance':.0001,
                            'required_bone_names':True,'required_exact_rest':True},
              'animations_ready':False}
    (SOURCE.parent/'shared_humanoid_v1.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('SHARED_RIG_V1',len(rest),'bones',fingerprint)


if __name__ == '__main__':
    main()
