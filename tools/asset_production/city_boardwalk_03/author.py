"""Original swept slate fascia and flush low trim; pinned Blender construction only."""
from pathlib import Path
import sys

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).parent))
from design import ASSET, PROFILE, VARIANTS, segments, station

ROOT = Path(__file__).resolve().parents[3]
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1


def material(name, color, metallic, roughness):
    """Create quiet opaque Principled materials without external texture dependencies."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


slate = material("boardwalk_fascia_slate", (.048, .069, .078), .15, .58)
trim = material("boardwalk_edge_trim", (.090, .126, .137), .20, .50)
for variant in VARIANTS:
    suffix = variant[0]
    name = "CityBoardwalk03" + suffix
    collection = bpy.data.collections.new("export_" + ASSET + suffix)
    scene.collection.children.link(collection)
    count, size = segments(variant), len(PROFILE)
    vertices = [station(variant, i / count, u, h)
                for i in range(count + 1) for u, h in PROFILE]
    faces = [tuple(reversed(range(size))), tuple(range(count * size, (count + 1) * size))]
    slots = [0, 0]
    for i in range(count):
        for j in range(size):
            k = (j + 1) % size
            faces.append((i * size + j, i * size + k,
                          (i + 1) * size + k, (i + 1) * size + j))
            slots.append(1 if j in (2, 3, 4) else 0)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.clear()
    mesh.materials.append(slate)
    mesh.materials.append(trim)
    for polygon, slot in zip(mesh.polygons, slots):
        polygon.material_index = slot
    obj = bpy.data.objects.new(name + "_Mesh", mesh)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    # Round manufactured profile edges, not every shallow arc station.
    bevel = obj.modifiers.new("Soft profile arris", "BEVEL")
    bevel.width, bevel.segments = .003, 2
    bevel.limit_method, bevel.angle_limit = "ANGLE", .12
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    weighted = obj.modifiers.new("Weighted profile normals", "WEIGHTED_NORMAL")
    weighted.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    obj.select_set(False)
    root = bpy.data.objects.new(name, None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_boardwalk.03"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["datum"] = "Flush top Z=0, underside Z=-.24; not a guardrail"
    root["pivot"] = "Edge centre for straight/terminal; deck entry centre for curved variants"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
