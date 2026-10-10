"""Author the original low seawall; planar end sections support butt-connected shore kits."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_shore_edges_01"
HALF_LENGTH = 2.0
# Cross-sections are (Blender Y, Z) metres, clockwise when viewed from +X.
# Preserve these planar profiles at X +/-2 for the separately owned corner/end kit.
PROFILES = {
    "foot": [(-.32, 0), (-.32, .13), (-.30, .16), (.30, .16), (.32, .13), (.32, 0)],
    "body": [(-.30, .16), (-.25, .77), (-.24, .79), (.24, .79), (.25, .77), (.30, .16)],
    "bed": [(-.255, .79), (-.255, .82), (.255, .82), (.255, .79)],
    "cap": [(-.32, .82), (-.36, .855), (-.36, .975), (-.335, 1.0),
            (.335, 1.0), (.36, .975), (.36, .855), (.32, .82)],
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
    # The centre coping groove is 16 mm wide, 8 mm deep; it never opens the solid.
    stations = [(-HALF_LENGTH, 0), (HALF_LENGTH, 0)]
    if joint:
        stations = [(-HALF_LENGTH, 0), (-.008, 0), (0, .008), (.008, 0), (HALF_LENGTH, 0)]
    vertices = [(x, y - inset * (1 if y > 0 else -1), z - inset)
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


extrude("Low battered wall", PROFILES["body"], slate)
extrude("Recessed plinth", PROFILES["foot"], foot)
extrude("Coping mortar bed", PROFILES["bed"], bed)
extrude("Chamfered coping with sparse joint", PROFILES["cap"], cap, joint=True)
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityShoreEdges01_Mesh"
root = bpy.data.objects.new("CityShoreEdges01", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_shore_edges.01"
root["authorship"] = "Original Blender construction; commissioned production specialist"
root["datum"] = "Land-contact Z=0; end joins X=+/-2; water-facing +Y maps to Godot -Z"
root["interface"] = "4m straight; 1m top; .72m coping width; square un-bevelled end joins"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
