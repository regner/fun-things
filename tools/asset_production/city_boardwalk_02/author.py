"""Construct original 22.5/45/90-degree timber coastal bends in pinned Blender."""
from math import radians
from pathlib import Path
import sys

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).parent))
from design import ASSET, BOARD_DEPTH, BOARD_GAP, DEPTH, RADIUS, VARIANTS, WIDTH, outline, point

ROOT = Path(__file__).resolve().parents[3]
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1


def material(name, color, metallic=0, roughness=.68):
    """Match the straight member's opaque Principled material contract exactly."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


slate = material("boardwalk_underdeck_slate", (.048, .069, .078), .15, .58)
wood = material("boardwalk_timber_warm", (.235, .145, .085))
light = material("boardwalk_timber_light", (.260, .166, .101))
muted = material("boardwalk_timber_muted", (.215, .136, .085))
palette = (wood, wood, light, wood, muted, wood, light, wood)


def prism(name, plan, bottom, top, mat, bevel, collection):
    """Extrude a closed plan polygon; bake roundovers and weighted corner normals."""
    count = len(plan)
    verts = [(x, y, z) for z in (bottom, top) for x, y in plan]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
              for i in range(count)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # The broad core has a concave outline: bevel only the timbers, avoiding
    # fragile long n-gon bevel tessellation and preserving exact connector planes.
    if bevel:
        modifier = obj.modifiers.new("Soft timber arris", "BEVEL")
        modifier.width, modifier.segments = bevel, 2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    return obj


for suffix, degrees, count in VARIANTS:
    name = ASSET + suffix
    collection = bpy.data.collections.new("export_" + name)
    scene.collection.children.link(collection)
    # Chorded coast outline; every timber has straight cross-deck end seams.
    parts = [prism("Recessed underdeck core", outline(degrees, count, .04),
                   -DEPTH, -BOARD_DEPTH, slate, 0, collection)]
    pitch = radians(degrees) / count
    half_gap = BOARD_GAP / (2 * RADIUS)
    for index in range(count):
        begin, end = index * pitch + half_gap, (index + 1) * pitch - half_gap
        plan = [point(r, a)[:2] for r, a in (
            (RADIUS - WIDTH / 2, begin), (RADIUS - WIDTH / 2, end),
            (RADIUS + WIDTH / 2, end), (RADIUS + WIDTH / 2, begin))]
        parts.append(prism(f"Radial timber {index:02d}", plan, -BOARD_DEPTH, 0,
                           palette[index % len(palette)], .004, collection))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    root_name = "CityBoardwalk02" + suffix
    mesh.name = root_name + "_Mesh"
    root = bpy.data.objects.new(root_name, None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "city_boardwalk.02"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["datum"] = "Entry centre on walk surface Z=0; underside Z=-.24"
    root["axes"] = "Entry tangent +Y to Godot -Z; right bend toward +X"
    root["provisional_angle_degrees"] = degrees
    root["provisional_centre_radius_m"] = RADIUS
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
