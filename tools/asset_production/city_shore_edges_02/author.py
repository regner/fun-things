"""Author the original heavy quay retaining face with coping flush to the land datum."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_shore_edges_02"
HALF_LENGTH = 2.0
# Cross-sections are (Blender Y, Z) metres, clockwise when viewed from +X.
# Preserve these planar profiles at X +/-2 for the separately owned corner/end kit.
PROFILES = {
    "foot": [(-.55, -2.4), (-.55, -2.14), (-.51, -2.1),
             (.51, -2.1), (.55, -2.14), (.55, -2.4)],
    "body": [(-.51, -2.1), (-.50, -.34), (-.48, -.31),
             (.48, -.31), (.50, -.34), (.51, -2.1)],
    "bed": [(-.51, -.31), (-.51, -.28), (.51, -.28), (.51, -.31)],
    "cap": [(-.56, -.28), (-.60, -.24), (-.60, -.035), (-.565, 0),
            (.565, 0), (.60, -.035), (.60, -.24), (.56, -.28)],
}
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)


def material(name, color, roughness):
    """Use quiet opaque mineral colors without procedural textures or emission."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    return mat


slate = material("shore_body_slate", (.20, .265, .29), .72)
foot = material("shore_foot_dark_slate", (.095, .145, .16), .78)
cap = material("shore_coping_pale_slate", (.46, .52, .53), .62)
bed = material("shore_joint_recess", (.045, .075, .085), .82)
parts = []


def extrude(name, profile, mat, joint=False):
    """Build a closed profiled solid with square end joins and an optional shallow centre joint."""
    # A 20 mm wide, 10 mm deep cap joint supplies a sparse 2 m construction rhythm.
    # Keep the underside fixed: no intersection with the dark bed at the groove.
    stations = [(-HALF_LENGTH, 0), (HALF_LENGTH, 0)]
    if joint:
        stations = [(-HALF_LENGTH, 0), (-.010, 0), (0, .010), (.010, 0), (HALF_LENGTH, 0)]
    vertices = [(x, y - inset * (1 if y > 0 else -1),
                 z - inset if z > -.28 else z)
                for x, inset in stations for y, z in profile]
    count = len(profile)
    faces = [tuple(reversed(range(count)))]
    for station in range(len(stations) - 1):
        for i in range(count):
            a = station * count + i
            b = station * count + (i + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(stations) - 1) * count, len(stations) * count)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(mat)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    # Broad flat facets and narrow bevel facets provide stable, clean mineral highlights.
    # Flat end normals are intentional so adjacent modules do not share shading dependencies.
    parts.append(obj)


extrude("Deep quay retaining face", PROFILES["body"], slate)
extrude("Broad dark toe", PROFILES["foot"], foot)
extrude("Coping mortar bed", PROFILES["bed"], bed)
extrude("Heavy coping with sparse joint", PROFILES["cap"], cap, joint=True)
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityShoreEdges02_Mesh"
root = bpy.data.objects.new("CityShoreEdges02", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_shore_edges.02"
root["authorship"] = "Original Blender construction; commissioned production specialist"
root["datum"] = "Land surface and cap top Z=0; toe Z=-2.4; water-facing +Y maps to Godot -Z"
root["interface"] = "4m straight; 1.2m coping width; X=+/-2 square ends; corner/transition owner .04"
root["placement"] = "Retaining component, not raised terrain; no assigned tide or water-entry rule"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
