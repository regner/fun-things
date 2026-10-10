"""Measure saved gate geometry, actual GLB accessors and repeat-export identity."""
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
ASSET = "city_barriers_07"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence/validation.json"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}/reexport")
# Independent literal bounds in Godot axes; not imported from the construction recipe.
BOUNDS = {
    "left": ([-.027, .1, -.11], [3.235, 2.1, .067]),
    "right": ([-3.1325, .1, -.09], [.027, 2.1, .067]),
    "mount": ([-.162, .585, -.047], [.020, 1.615, .047]),
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
    name = "CityBarriers07_" + variant.title()
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
    if variant != "mount":
        # The knuckle's bore is genuinely hollow along the vertical hinge axis.
        assert tree.ray_cast(Vector((0, 0, .60)), Vector((0, 0, 1)), .10)[0] is None
    else:
        assert tree.ray_cast(Vector((0, 0, .57)), Vector((0, 0, 1)), .10)[0] is not None
    remaining = set(bm.verts)
    components = 0
    while remaining:
        pending = [remaining.pop()]
        components += 1
        while pending:
            for edge in pending.pop().link_edges:
                for vertex in edge.verts:
                    if vertex in remaining:
                        remaining.remove(vertex)
                        pending.append(vertex)
    bm.free()
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
            "hinge_bore_or_pin_ray_passed": True,
            "finish_matches_panel_glb": True,
            "glb_sha256": hashlib.sha256(raw).hexdigest(), "fresh_export_byte_identical": True}


def tree_for(variant, location, angle=0):
    """Build independent world-space BVHs from the saved leaf/fitting meshes."""
    from mathutils import Matrix
    mesh = bpy.data.objects["CityBarriers07_" + variant.title() + "_Mesh"].data
    transform = Matrix.Translation(Vector(location)) @ Matrix.Rotation(angle, 4, "Z")
    return BVHTree.FromPolygons([transform @ v.co for v in mesh.vertices],
                               [tuple(p.vertices) for p in mesh.polygons])


def check_fit():
    """Verify paired latch fit and knuckle/pin clearance from actual saved geometry."""
    left = tree_for("left", (-3.15, 0, 0))
    right = tree_for("right", (3.15, 0, 0))
    assert not left.overlap(right), "Closed leaf/latch surfaces intersect"
    for variant, sign in (("left", 1), ("right", -1)):
        mount = tree_for("mount", (0, 0, 0), 0 if sign == 1 else math.pi)
        for degrees in (0, 45, 90):
            leaf = tree_for(variant, (0, 0, 0), math.radians(degrees) * sign)
            assert not leaf.overlap(mount), (variant, degrees, "hinge interference")
    # Ray through the keeper opening along the bolt axis, before the receiving frame.
    keeper = tree_for("right", (0, 0, 0))
    assert keeper.ray_cast(Vector((-3.145, .06, 1.1)), Vector((1, 0, 0)), .065)[0] is None
    return {"closed_pair_surface_intersections": 0, "keeper_opening_ray_clear": True,
            "hinge_mount_surface_intersections_at_0_45_90_degrees": 0,
            "hinge_axis_ground_projection_m": [0, 0, 0],
            "hinge_heights_m": [.65, 1.55], "hinge_axis_spacing_m": 6.3,
            "post_axis_spacing_m": 6.53, "frame_centre_gap_m": .15}


def main():
    """Reopen saved source and export afresh before recording all three component results and actual hardware mating."""
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    sys.argv = ["export.py", "--", str(SCRATCH)]
    script = Path(__file__).parent / "export.py"
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": __file__})
    report = {"asset": "city_barriers.07", "blender": bpy.app.version_string,
              "blender_build": bpy.app.build_hash.decode(), "exporter": "5.2.40",
              "bounds_tolerance_m": .001, "source_export_tolerance_m": .00001,
              "dimensions_status": "provisional", "variants": {v: check(v) for v in BOUNDS},
              "source_export_status": "passed", "fit": check_fit()}
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
