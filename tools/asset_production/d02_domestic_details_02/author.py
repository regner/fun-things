"""Author the original Crescents L-shaped wall return in pinned isolated Blender."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_domestic_details_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + NID)
scene.collection.children.link(collection)
parts = []
# Provisional return: 1.6 m square bounds; the straight sibling owns the matching section.
CORNER = -.62
END = .8
CORE_DEPTH = .26
CAP_DEPTH = .36


def material(name, swatch, roughness):
    """Use the delivered Crescents house swatches as opaque flat Principled colors."""
    rgb = [int(swatch[i:i+2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*linear, 1)
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*linear, 1)
    shader.inputs["Roughness"].default_value = roughness
    return mat


wall = material("crescents_warm_render", "ACA69E", .65)
cap = material("crescents_ivory_trim", "D4CEBB", .55)
base = material("crescents_slate_plinth", "58636B", .75)


def sweep(name, stations, section, mat, bevel):
    """Sweep a closed wall section through a mitred corner without overlapping solids.

    Stations (x, y, dx, dy) map section offset to a transverse vector. The corner
    uses (1, 1) so both orthogonal arms share one exact diagonal section.
    """
    n = len(section)
    vertices = [(x + dx*t, y + dy*t, z)
                for x, y, dx, dy in stations for t, z in section]
    last = (len(stations)-1)*n
    faces = [tuple(reversed(range(n))), tuple(range(last, last+n))]
    for k in range(len(stations)-1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((k*n+i, k*n+j, (k+1)*n+j, (k+1)*n+i))
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    modifier = obj.modifiers.new("Soft dressed edges", "BEVEL")
    modifier.width = bevel
    modifier.segments = 3
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    data.update()
    for face in data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Broad plane normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)


full_path = [(END, CORNER, 0, 1), (CORNER, CORNER, 1, 1), (CORNER, END, 1, 0)]
sweep("Continuous_L_render", full_path,
      [(-CORE_DEPTH/2, .14), (CORE_DEPTH/2, .14),
       (CORE_DEPTH/2, .80), (-CORE_DEPTH/2, .80)], wall, .012)
sweep("Continuous_L_plinth", full_path,
      [(-.15, 0), (.15, 0), (.15, .14), (-.15, .14)], base, .008)
# One dressed L coping stone plus two straight end stones. Six-mm joints; no
# diagonal overlap at the elbow. Matching crest/shoulders meet the straight run.
profile = [(-CAP_DEPTH/2, .80), (CAP_DEPTH/2, .80), (CAP_DEPTH/2, .91),
           (.07, .94), (-.07, .94), (-CAP_DEPTH/2, .91)]
sweep("Corner_coping", [(.087, CORNER, 0, 1), (CORNER, CORNER, 1, 1),
                         (CORNER, .087, 1, 0)], profile, cap, .008)
sweep("East_end_coping", [(END, CORNER, 0, 1), (.093, CORNER, 0, 1)], profile, cap, .008)
sweep("North_end_coping", [(CORNER, .093, 1, 0), (CORNER, END, 1, 0)], profile, cap, .008)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D02DomesticDetails02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D02DomesticDetails02", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d02_domestic_details.02"
root["provenance"] = "Original Blender construction; no external meshes, textures or artwork"
root["datum"] = "Ground-centred AABB; L arms east/north; Blender +Y maps to Godot -Z"
root["module_ends"] = "Godot east (.8,0,.62), north (-.62,0,-.8); height .94; cap depth .36"
root["state"] = "Static intact low boundary; no gate, interior or destruction state"
bpy.ops.mesh.primitive_cube_add(size=1, location=(5, 0, .5))
reference = bpy.context.object
reference.name = "authoring_1m_reference"
reference.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
