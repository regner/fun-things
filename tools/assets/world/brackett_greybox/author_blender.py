"""Author neutral modular greybox in a private Blender 5.2.2 background process.

Original geometry by Codex for Regner, 9 October 2026. No external meshes/textures.
This bootstrap refuses to overwrite editable sources unless explicitly requested.
"""
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT/'art/source/models/brackett_greybox'
PLAN = json.loads((SOURCE/'authoring_plan.json').read_text())
assert bpy.app.version_string == '5.2.2 LTS'
REPLACE = '--replace-owned-sources' in sys.argv
MATERIALS = {
    'grey_building': (.42, .45, .48), 'grey_roof': (.29, .32, .35),
    'grey_land': (.22, .25, .27), 'grey_road': (.075, .085, .095),
    'grey_walk': (.37, .40, .42), 'grey_field': (.24, .29, .27),
    'grey_water': (.055, .085, .11),
}


def reset():
    """Reset only this private process and install metre units and flat materials."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1
    for name, rgb in MATERIALS.items():
        material = bpy.data.materials.new(name)
        material.use_nodes = True
        material.diffuse_color = (*rgb, 1)
        shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value = (*rgb, 1)
        shader.inputs['Roughness'].default_value = .85


def collection(name):
    """Declare an explicit export collection for each replaceable asset."""
    result = bpy.data.collections.new('export_'+name)
    bpy.context.scene.collection.children.link(result)
    return result


def finish(obj, target, material):
    """Apply model transforms and triangulation before committing editable sources."""
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    target.objects.link(obj)
    obj.data.materials.append(bpy.data.materials[material])
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    modifier = obj.modifiers.new('Explicit triangles', 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)


def cube(target, name, width, depth, height, bottom, material):
    """Create an original Blender mass, ground-centred, +Y north, +Z up."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, bottom+height/2))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (width, depth, height)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bevel = obj.modifiers.new('Readable soft block edges', 'BEVEL')
    bevel.width = .12
    bevel.segments = 1
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    finish(obj, target, material)


def surface(target, name, triangles, height, solid=False):
    """Create source-owned triangulated surface with no filled harbour holes."""
    vertices, faces, lookup = [], [], {}
    for triangle in triangles:
        indices = []
        for x, south in triangle:
            point = (x-630, 355-south, height)
            if point not in lookup:
                lookup[point] = len(vertices)
                vertices.append(point)
            indices.append(lookup[point])
        a, b, c = [vertices[i] for i in indices]
        if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]) < 0:
            indices.reverse()
        faces.append(indices)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if solid:
        modifier = obj.modifiers.new('Island edge below flat datum', 'SOLIDIFY')
        modifier.thickness = 2
        modifier.offset = -1
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    finish(obj, target, 'grey_'+name)


def save(name, outputs):
    """Save source with explicit membership; cameras and studio lights are absent."""
    path = SOURCE/(name+'.blend')
    assert REPLACE or not path.exists(), f'Refusing source overwrite: {path}'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    return dict(source=str(path.relative_to(ROOT)), outputs=outputs,
                collections={c.name: sorted(o.name for o in c.all_objects)
                             for c in bpy.context.scene.collection.children})


def main():
    """Write nine district kits, twelve small surface sources, and the preview sea."""
    manifest = []
    for district in PLAN['districts']:
        reset()
        outputs = []
        for asset in [a for a in PLAN['kit'] if a['district_id'] == district['id']]:
            name, w, d, h = [asset[k] for k in ('asset_id', 'width', 'depth', 'height')]
            target = collection(name)
            boxes = []
            if name.startswith('tower'):
                cube(target, name+'_podium', w, d, 6, 0, 'grey_building')
                cube(target, name+'_shaft', w*.61, d*.61, h-6, 6, 'grey_roof')
                boxes = [[w, 6, d, 0, 3, 0], [w*.61, h-6, d*.61, 0, (h+6)/2, 0]]
            else:
                cube(target, name+'_mass', w, d, h, 0, 'grey_building')
                boxes = [[w, h, d, 0, h/2, 0]]
            asset['collision_boxes'] = boxes
            outputs.append(name)
        manifest.append(save(f'district_{district["id"]:02d}_kit', outputs))
    for sector in PLAN['sectors']:
        reset()
        target = collection(sector['asset_id'])
        for name, data in sector['parts'].items():
            if data:
                surface(target, name, data, {'land': 0, 'road': .025, 'walk': .06, 'field': .015}[name], name == 'land')
        manifest.append(save(sector['asset_id'], [sector['asset_id']]))
    reset()
    target = collection('water')
    surface(target, 'water', [[[-400, -300], [1650, -300], [1650, 1050]],
                             [[-400, -300], [1650, 1050], [-400, 1050]]], -2.1)
    manifest.append(save('water', ['water']))
    (SOURCE/'source_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    # The editor receives only finite placement/collision metadata, not visible vertex copies.
    editor = {key: PLAN[key] for key in ['districts', 'placements', 'kit', 'summary', 'reference_hashes']}
    editor['surfaces'] = [s['asset_id'] for s in PLAN['sectors']]
    (ROOT/'tools/assets/world/brackett_greybox/editor_input.json').write_text(json.dumps(editor, indent=2)+'\n')
    print('BRACKETT_SOURCES', len(manifest), 'BLENDER', bpy.app.version_string)


if __name__ == '__main__':
    main()
