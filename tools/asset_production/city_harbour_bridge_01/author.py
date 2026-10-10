"""Original harbour structural deck; isolated Blender 5.2.2 LTS only."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "city_harbour_bridge_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
SPAN = 91.0
WIDTH = 17.0
SLAB_DEPTH = 0.55


def material(name, color, metallic=0.0, roughness=0.65):
    """Create a quiet opaque Principled material with deliberate backface culling."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


def finish(obj, collection, mat, bevel=0.0):
    """Apply manufactured edge treatment and clean closed component topology."""
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft edge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted manufactured normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    return obj


def box(name, center, size, mat, collection, bevel=0.02):
    """Add a closed Blender-authored detail, never a runtime render primitive."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    return finish(obj, collection, mat, bevel)


def main():
    """Build one level deck with integral fascia, longitudinal girders and diaphragms."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new(f"export_{NID}")
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("CityHarbourBridge01", None)
    collection.objects.link(root)
    root["asset_id"] = "city_harbour_bridge.01"
    root["datum"] = "Level structural deck top at Godot Y=0; centre of existing 91 x 17 m footprint"
    root["provenance"] = "Original commissioned Blender construction; no external geometry"
    root["road_owner"] = "Road tool owns overlays/markings/sidewalk surfaces, not this structural deck"
    concrete = material("bridge_civic_concrete", (0.16, 0.23, 0.25))
    fascia = material("bridge_pale_fascia", (0.57, 0.63, 0.60), roughness=0.58)
    steel = material("bridge_petrol_steel", (0.032, 0.081, 0.095), 0.65, 0.43)
    reveal = material("bridge_recess", (0.045, 0.071, 0.077), 0.25, 0.6)
    # Exact, square top perimeter and bank joints; lower outside shoulders chamfer inward.
    section = [(-WIDTH / 2, 0), (-WIDTH / 2, -0.35),
               (-WIDTH / 2 + 0.15, -SLAB_DEPTH),
               (WIDTH / 2 - 0.15, -SLAB_DEPTH), (WIDTH / 2, -0.35),
               (WIDTH / 2, 0), (WIDTH / 2 - 0.35, 0), (-WIDTH / 2 + 0.35, 0)]
    vertices = [(x, y, z) for x in (-SPAN / 2, SPAN / 2) for y, z in section]
    n = len(section)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    mesh = bpy.data.meshes.new("Level slab with chamfered soffit")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    slab = bpy.data.objects.new("Structural slab", mesh)
    collection.objects.link(slab)
    finish(slab, collection, concrete)
    slab.data.materials.append(fascia)
    for face in slab.data.polygons:
        face.use_smooth = False
        if abs(face.normal.z) < 0.99 or (face.normal.z > 0.99 and abs(face.center.y) > 8.15):
            face.material_index = 1
    parts = [slab]
    # Five shallow welded box girders leave the entire harbour mouth free of piers.
    for y in (-6.6, -3.3, 0, 3.3, 6.6):
        parts.append(box("Longitudinal box girder", (0, y, -0.885),
                         (90.2, 0.64, 0.73), steel, collection, 0.035))
        parts.append(box("Girder lower flange", (0, y, -1.20),
                         (90.2, 0.9, 0.10), steel, collection, 0.018))
    for x in (-43.5, -29, -14.5, 0, 14.5, 29, 43.5):
        parts.append(box("Transverse diaphragm", (x, 0, -0.75),
                         (0.26, 14.0, 0.44), steel, collection, 0.025))
    # Thin horizontal reveal sits below the walking plane, not a raised trip edge/rail.
    for y in (-8.495, 8.495):
        parts.append(box("Fascia recessed metal strip", (0, y, -0.245),
                         (90.96, 0.010, 0.07), reveal, collection, 0.002))
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = slab
    bpy.ops.object.join()
    slab.name = "CityHarbourBridge01_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    slab.parent = root
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    exec(compile((Path(__file__).parent / "export.py").read_text(),
                 str(Path(__file__).parent / "export.py"), "exec"))


if __name__ == "__main__":
    main()
