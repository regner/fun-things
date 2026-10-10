"""Measure saved support geometry, actual GLB accessors and repeat-export identity."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_barriers_06"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence/validation.json"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}/reexport")
# Independent literal bounds in Godot axes; not imported from the construction recipe.
BOUNDS = {
    "line": ([-.105, 0, -.048], [.105, 2.16, .048]),
    "terminal": ([-.048, 0, -.11], [.95, 2.16, .048]),
    "corner": ([-.048, 0, -.95], [.95, 2.16, .048]),
}


def accessor(document, binary, index):
    """Read vertex/index values rather than trusting only accessor metadata."""
    item = document["accessors"][index]
    view = document["bufferViews"][item["bufferView"]]
    fmt = "<" + {5123: "H", 5125: "I", 5126: "f"}[item["componentType"]] * {
        "SCALAR": 1, "VEC3": 3}[item["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(item["count"])]


def check(variant):
    """Reject topology, transforms, normals, bounds or explicit-export contract faults."""
    name = "CityBarriers06_" + variant.title()
    collection = bpy.data.collections[f"export_{ASSET}_{variant}"]
    assert {obj.name for obj in collection.objects} == {name, name + "_Mesh"}
    for obj in collection.objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
    obj = bpy.data.objects[name + "_Mesh"]
    mesh = obj.data
    assert not obj.modifiers
    mesh.calc_loop_triangles()
    normal_error = max(abs(n.vector.length - 1) for n in mesh.corner_normals)
    assert normal_error < 1e-5
    assert all(math.isfinite(v) for point in mesh.vertices for v in point.co)
    assert all(face.area > 1e-10 for face in mesh.polygons)
    assert all(face.area > 1e-10 for face in mesh.loop_triangles)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    assert not any(not edge.is_manifold for edge in bm.edges)
    volume = bm.calc_volume(signed=True)
    assert volume > 0
    tree = BVHTree.FromBMesh(bm)
    assert tree.ray_cast(Vector((.075, 0, .37)), Vector((0, 0, 1)), .06)[0] is None
    assert tree.ray_cast(Vector((0, -.2, 1)), Vector((0, 1, 0)), .4)[0] is not None
    remaining = set(bm.verts)
    components = 0
    braces = []
    while remaining:
        pending = [remaining.pop()]
        vertices = set(pending)
        components += 1
        while pending:
            for edge in pending.pop().link_edges:
                for vertex in edge.verts:
                    if vertex in remaining:
                        remaining.remove(vertex)
                        pending.append(vertex)
                        vertices.add(vertex)
        size = [max(v.co[i] for v in vertices) - min(v.co[i] for v in vertices)
                for i in range(3)]
        if size[2] > 1 and max(size[:2]) > .85:
            ordered = list(vertices)
            indices = {v: i for i, v in enumerate(ordered)}
            faces = {face for v in vertices for face in v.link_faces}
            braces.append(BVHTree.FromPolygons([v.co for v in ordered],
                          [[indices[v] for v in face.verts] for face in faces]))
    if variant == "corner":
        assert len(braces) == 2 and not braces[0].overlap(braces[1]), "Corner brace intersection"
    bm.free()
    assert components == {"line": 16, "terminal": 14, "corner": 24}[variant]
    positions = [(v.co.x, v.co.z, -v.co.y) for v in mesh.vertices]
    lo = [min(v[i] for v in positions) for i in range(3)]
    hi = [max(v[i] for v in positions) for i in range(3)]
    expected_lo, expected_hi = BOUNDS[variant]
    assert all(abs(a - b) < .001 for a, b in zip(lo + hi, expected_lo + expected_hi)), (lo, hi)
    path = ROOT / f"art/models/environment/{ASSET}/{ASSET}_{variant}.glb"
    raw = path.read_bytes()
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    json_length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(raw[20:20 + json_length])
    binary_length, kind = struct.unpack_from("<II", raw, 20 + json_length)
    assert kind == 0x004E4942
    binary = raw[28 + json_length:28 + json_length + binary_length]
    assert not any(doc.get(key) for key in ("animations", "cameras", "skins", "images", "textures"))
    assert len(doc["nodes"]) == 2 and len(doc["meshes"]) == 1
    for node in doc["nodes"]:
        assert node.get("translation", [0, 0, 0]) == [0, 0, 0]
        assert node.get("rotation", [0, 0, 0, 1]) == [0, 0, 0, 1]
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
    primitives = doc["meshes"][0]["primitives"]
    assert len(primitives) == 3
    positions, triangles, export_normal_error = [], 0, 0.0
    for primitive in primitives:
        assert primitive.get("mode", 4) == 4
        local = accessor(doc, binary, primitive["attributes"]["POSITION"])
        normals = accessor(doc, binary, primitive["attributes"]["NORMAL"])
        indices = [value[0] for value in accessor(doc, binary, primitive["indices"])]
        assert all(math.isfinite(value) for point in local for value in point)
        assert len(indices) % 3 == 0
        for index in range(0, len(indices), 3):
            a, b, c = (Vector(local[i]) for i in indices[index:index + 3])
            assert (b - a).cross(c - a).length * .5 > 1e-10
        export_normal_error = max(export_normal_error, max(abs(Vector(n).length - 1) for n in normals))
        positions.extend(local)
        triangles += len(indices) // 3
    assert export_normal_error < 1e-5
    export_lo = [min(v[i] for v in positions) for i in range(3)]
    export_hi = [max(v[i] for v in positions) for i in range(3)]
    assert all(abs(a - b) < 1e-5 for a, b in zip(lo + hi, export_lo + export_hi))
    assert triangles == len(mesh.loop_triangles)
    assert [mat.name for mat in mesh.materials] == [
        "fence_galvanised_frame", "fence_galvanised_wire", "fence_joint_oxide"]
    assert {m["name"] for m in doc["materials"]} == {m.name for m in mesh.materials}
    assert all(not m.get("doubleSided", False) for m in doc["materials"])
    panel = (ROOT / "art/models/environment/city_barriers_05/city_barriers_05.glb").read_bytes()
    panel_json_length = struct.unpack_from("<I", panel, 12)[0]
    panel_materials = json.loads(panel[20:20 + panel_json_length])["materials"]
    assert {m["name"]: m for m in doc["materials"]} == {m["name"]: m for m in panel_materials}
    assert (SCRATCH / path.name).read_bytes() == raw, "Fresh export drift: " + variant
    return {"source_vertices": len(mesh.vertices), "source_faces": len(mesh.polygons),
            "triangles": triangles, "export_vertices": len(positions), "mesh_count": 1,
            "surface_count": 3, "closed_components": components, "closed_volume_m3": volume,
            "degenerate_faces": 0, "degenerate_triangles": 0, "nonmanifold_edges": 0,
            "source_normal_max_length_error": normal_error,
            "export_normal_max_length_error": export_normal_error,
            "godot_bounds_min_m": export_lo, "godot_bounds_max_m": export_hi,
            "dimensions_m": [hi[i] - lo[i] for i in range(3)], "pivot_m": [0, 0, 0],
            "ground_datum_m": 0, "materials": doc["materials"], "glb_bytes": len(raw),
            "clamp_bore_ray_clear": True, "post_visual_ray_blocked": True,
            "finish_matches_panel_glb": True,
            "corner_braces_surface_intersections": 0 if variant == "corner" else None,
            "glb_sha256": hashlib.sha256(raw).hexdigest(), "fresh_export_byte_identical": True}


def main():
    """Reopen saved source and export afresh before recording all three component results."""
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    sys.argv = ["export.py", "--", str(SCRATCH)]
    script = Path(__file__).parent / "export.py"
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": __file__})
    report = {"asset": "city_barriers.06", "blender": bpy.app.version_string,
              "blender_build": bpy.app.build_hash.decode(), "exporter": "5.2.40",
              "bounds_tolerance_m": .001, "source_export_tolerance_m": .00001,
              "dimensions_status": "provisional", "variants": {v: check(v) for v in BOUNDS},
              "source_export_status": "passed"}
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
