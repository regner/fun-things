"""Check closed source geometry, actual GLB buffers, sockets and byte-identical reexport."""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_harbour_footbridge_05"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}/reexport")
TOLERANCE = 0.00001
EXPECTED = {
    "main": ((-1.6, -0.35, -19.84), (1.6, 5.5, 0), (0, 19.84, 0), (0, 1, 0)),
    "south": ((-1.6, -0.35, -11.52), (9.92, 5.5, 0), (9.92, 9.92, 0), (1, 0, 0)),
    "quay": ((-9.92, -0.35, -11.52), (1.6, 5.5, 0), (-9.92, 9.92, 0), (-1, 0, 0)),
}


def accessor(doc, binary, index):
    """Decode an actual non-sparse glTF accessor respecting buffer offsets and stride."""
    entry = doc["accessors"][index]
    view = doc["bufferViews"][entry["bufferView"]]
    codes = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}
    dimensions = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    fmt = "<" + codes[entry["componentType"]] * dimensions[entry["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + entry.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(entry["count"])]


def check_variant(variant):
    """Assert independent geometry bounds, step heights, interfaces and exported topology."""
    collection = bpy.data.collections[f"export_{NID}_{variant}"]
    name = f"D06HarbourFootbridge05_{variant}"
    assert {obj.name for obj in collection.objects} == {
        name, name + "_Mesh", f"socket_incoming_{variant}", f"socket_ground_{variant}"}
    root, obj = bpy.data.objects[name], bpy.data.objects[name + "_Mesh"]
    assert obj.parent == root and root.parent is None
    for node in (root, obj):
        assert node.location.length == 0 and node.rotation_euler.to_quaternion().angle == 0
        assert tuple(node.scale) == (1, 1, 1) and not node.modifiers
    mesh = obj.data
    mesh.calc_loop_triangles()
    assert all(abs(n.vector.length - 1) < 0.0001 for n in mesh.corner_normals)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    degenerate = sum(face.calc_area() <= 1e-10 for face in bm.faces)
    volume = bm.calc_volume(signed=True)
    assert nonmanifold == 0 and degenerate == 0 and volume > 0
    bm.free()
    levels = {round(face.center.z, 6) for face in mesh.polygons
              if face.normal.z > 0.999 and face.area > 0.5}
    assert levels == {round(index * 0.171875, 6) for index in range(33)}, sorted(levels)
    lo, hi, ground, outward = EXPECTED[variant]
    coords = [Vector((v.co.x, v.co.z, -v.co.y)) for v in mesh.vertices]
    bounds = [min(v[i] for v in coords) for i in range(3)] + [
        max(v[i] for v in coords) for i in range(3)]
    assert all(abs(a - b) < TOLERANCE for a, b in zip(bounds, lo + hi))
    sockets = {}
    for kind, position, forward in (("incoming", (0, 0, 5.5), (0, -1, 0)),
                                     ("ground", ground, outward)):
        node = bpy.data.objects[f"socket_{kind}_{variant}"]
        axis = node.rotation_euler.to_matrix() @ Vector((0, 1, 0))
        assert (node.location - Vector(position)).length < TOLERANCE
        assert (axis - Vector(forward)).length < TOLERANCE
        assert tuple(node.scale) == (1, 1, 1) and node.parent == root
        relative = [v.co - node.location for v in mesh.vertices
                    if abs((v.co - node.location).dot(axis)) < TOLERANCE]
        across = Vector((axis.y, -axis.x, 0))
        width = [v.dot(across) for v in relative]
        assert abs(min(width) + 1.6) < TOLERANCE and abs(max(width) - 1.6) < TOLERANCE
        assert abs(min(v.z for v in relative) + 0.35) < TOLERANCE
        assert abs(max(v.z for v in relative)) < TOLERANCE
        sockets[kind] = {"position_godot": [position[0], position[2], -position[1]],
                         "outward_godot": [forward[0], forward[2], -forward[1]],
                         "measured_width_m": max(width) - min(width)}
    path = ROOT / f"art/models/environment/{NID}/{NID}_{variant}.glb"
    raw = path.read_bytes()
    magic, version, size = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and size == len(raw)
    n = struct.unpack_from("<I", raw, 12)[0]
    doc, binary = json.loads(raw[20:20 + n]), raw[28 + n:]
    assert len(doc["meshes"]) == 1 and len(doc["nodes"]) == 4
    assert not any(doc.get(key) for key in ("images", "textures", "skins", "animations", "cameras"))
    primitives = doc["meshes"][0]["primitives"]
    assert len(primitives) == 3
    positions_all, triangles = [], 0
    for primitive in primitives:
        positions = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["POSITION"])]
        normals = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["NORMAL"])]
        indices = [v[0] for v in accessor(doc, binary, primitive["indices"])]
        assert all(abs(v.length - 1) < 0.0001 for v in normals)
        assert all(math.isfinite(value) for v in positions for value in v)
        assert len(indices) % 3 == 0
        for i in range(0, len(indices), 3):
            a, b, c = (positions[j] for j in indices[i:i + 3])
            assert (b - a).cross(c - a).length / 2 > 1e-10
        triangles += len(indices) // 3
        positions_all.extend(positions)
    actual = [min(v[i] for v in positions_all) for i in range(3)] + [
        max(v[i] for v in positions_all) for i in range(3)]
    assert all(abs(a - b) < TOLERANCE for a, b in zip(actual, lo + hi))
    assert triangles == len(mesh.loop_triangles)
    expected_materials = [("deck_warm_pale", (0.72, 0.73, 0.66, 1), 0.78),
                          ("deck_pale_fascia", (0.49, 0.59, 0.59, 1), 0.56),
                          ("deck_petrol_underside", (0.075, 0.16, 0.18, 1), 0.65)]
    for primitive, (name, color, roughness) in zip(primitives, expected_materials):
        material = doc["materials"][primitive["material"]]
        assert material["name"] == name and not material.get("doubleSided", False)
        pbr = material["pbrMetallicRoughness"]
        assert all(abs(a - b) < TOLERANCE for a, b in zip(pbr["baseColorFactor"], color))
        assert abs(pbr["roughnessFactor"] - roughness) < TOLERANCE
    return {"source_vertices": len(mesh.vertices), "triangles": triangles,
            "glb_vertices_including_surface_splits": len(positions_all),
            "mesh_count": 1, "surface_count": 3, "degenerate_faces": degenerate,
            "nonmanifold_edges": nonmanifold, "degenerate_export_triangles": 0,
            "unit_corner_and_export_normals": True, "source_signed_volume_m3": volume,
            "aabb_godot": {"min": actual[:3], "max": actual[3:],
                           "size": [actual[i + 3] - actual[i] for i in range(3)]},
            "pivot_godot": [0, 0, 0], "broad_horizontal_levels_m": sorted(levels),
            "sockets": sockets, "materials": doc["materials"], "export_nodes": doc["nodes"],
            "glb_sha256": hashlib.sha256(raw).hexdigest()}


def main():
    """Validate all saved variants, then reexport and byte-compare every GLB."""
    source = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.app.version_string == "5.2.2 LTS"
    assert bpy.context.scene.unit_settings.system == "METRIC"
    assert bpy.context.scene.unit_settings.scale_length == 1
    variants = {variant: check_variant(variant) for variant in EXPECTED}
    SCRATCH.mkdir(parents=True, exist_ok=True)
    sys.argv = [__file__, "--", str(SCRATCH)]
    script = Path(__file__).parent / "export.py"
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": str(script)})
    for variant, result in variants.items():
        fresh = (SCRATCH / f"{NID}_{variant}.glb").read_bytes()
        assert hashlib.sha256(fresh).hexdigest() == result["glb_sha256"]
        result["fresh_reexport_byte_identical"] = True
    report = {"asset_id": "d06_harbour_footbridge.05", "status": "PASS",
              "blender": bpy.app.version_string, "build": bpy.app.build_hash.decode(),
              "exporter": "5.2.40", "variants": variants, "dimension_tolerance_m": TOLERANCE,
              "datum": "Ground below incoming centre; apron foundation extends to Y=-0.35",
              "source_shells_per_variant": 5,
              "shell_note": "Closed flight/landing shells meet on end planes; internal caps retained.",
              "collision_note": "Ramp proxy lies up to 0.171875 m below treads; traversal pending."}
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
