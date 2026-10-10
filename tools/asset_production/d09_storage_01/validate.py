"""Reject container topology, bounds, normal, scope or byte-reproduction regressions."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d09_storage_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EXPORT = ROOT / f"art/models/environment/{ASSET}/{ASSET}.glb"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence/validation.json"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}/reexport")
EXPECTED_MIN = [-1.25, 0, -6.0]
EXPECTED_MAX = [1.25, 2.6, 6.0]
MATERIALS = ["storage_body_blue", "storage_frame_slate", "storage_hardware_steel",
             "storage_id_face"]


def accessor(document, binary, index):
    """Read actual binary accessor values, rather than trusting GLB summary bounds."""
    value = document["accessors"][index]
    view = document["bufferViews"][value["bufferView"]]
    fmt = "<" + {5123: "H", 5125: "I", 5126: "f"}[value["componentType"]] * {
        "SCALAR": 1, "VEC2": 2, "VEC3": 3}[value["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    offset = view.get("byteOffset", 0) + value.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, offset + i * stride) for i in range(value["count"])]


def main():
    """Measure source shells and exported triangles, then compare a fresh pinned export."""
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    assert bpy.app.version_string == "5.2.2 LTS"
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    collection = bpy.data.collections["export_" + ASSET]
    assert {obj.name for obj in collection.objects} == {"D09Storage01", "D09Storage01_Mesh"}
    for obj in collection.objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
    obj = bpy.data.objects["D09Storage01_Mesh"]
    assert obj.parent.name == "D09Storage01" and not obj.modifiers
    mesh = obj.data
    mesh.calc_loop_triangles()
    assert all(math.isfinite(value) for vertex in mesh.vertices for value in vertex.co)
    assert all(face.area > 1e-10 for face in mesh.polygons)
    assert all(triangle.area > 1e-10 for triangle in mesh.loop_triangles)
    source_normal_error = max(abs(normal.vector.length - 1) for normal in mesh.corner_normals)
    assert source_normal_error < 1e-5
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    assert nonmanifold == 0
    volume = bm.calc_volume(signed=True)
    assert volume > 0
    bm.free()
    assert [material.name for material in mesh.materials] == MATERIALS
    coords = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    low = [min(v[i] for v in coords) for i in range(3)]
    high = [max(v[i] for v in coords) for i in range(3)]
    godot_low, godot_high = [low[0], low[2], -high[1]], [high[0], high[2], -low[1]]
    assert all(abs(a - b) < .001 for a, b in zip(godot_low + godot_high, EXPECTED_MIN + EXPECTED_MAX))
    raw = EXPORT.read_bytes()
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    document = json.loads(raw[20:20 + length])
    bin_length, kind = struct.unpack_from("<II", raw, 20 + length)
    assert kind == 0x004E4942
    binary = raw[28 + length:28 + length + bin_length]
    assert not any(document.get(key) for key in ("animations", "skins", "cameras", "images", "textures"))
    assert len(document["nodes"]) == 2 and len(document["meshes"]) == 1
    for node in document["nodes"]:
        assert node.get("translation", [0, 0, 0]) == [0, 0, 0]
        assert node.get("rotation", [0, 0, 0, 1]) == [0, 0, 0, 1]
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
    assert [material["name"] for material in document["materials"]] == MATERIALS
    assert all(not material.get("doubleSided", False) for material in document["materials"])
    primitives = document["meshes"][0]["primitives"]
    assert len(primitives) == 4
    # The future freight-art owner needs only the two outward amber quads, not a sign mesh.
    artwork = primitives[3]
    assert artwork["material"] == 3
    artwork_indices = accessor(document, binary, artwork["indices"])
    assert len(artwork_indices) == 12, "Artwork slot must contain exactly two quads"
    artwork_uv = accessor(document, binary, artwork["attributes"]["TEXCOORD_0"])
    assert all(-1e-6 <= value <= 1 + 1e-6 for uv in artwork_uv for value in uv)
    assert {tuple(round(value, 5) for value in uv) for uv in artwork_uv} == {
        (0, 0), (1, 0), (1, 1), (0, 1)}
    positions = []
    triangles, normal_error = 0, 0.0
    for primitive in primitives:
        local = accessor(document, binary, primitive["attributes"]["POSITION"])
        normals = accessor(document, binary, primitive["attributes"]["NORMAL"])
        indices = [value[0] for value in accessor(document, binary, primitive["indices"])]
        assert len(indices) % 3 == 0 and primitive.get("mode", 4) == 4
        for i in range(0, len(indices), 3):
            a, b, c = (Vector(local[j]) for j in indices[i:i + 3])
            assert (b - a).cross(c - a).length * .5 > 1e-10
        normal_error = max(normal_error, max(abs(Vector(n).length - 1) for n in normals))
        positions.extend(local)
        triangles += len(indices) // 3
    assert normal_error < 1e-5 and triangles == len(mesh.loop_triangles)
    export_low = [min(v[i] for v in positions) for i in range(3)]
    export_high = [max(v[i] for v in positions) for i in range(3)]
    assert all(abs(a - b) < 1e-5 for a, b in zip(export_low + export_high, godot_low + godot_high))
    sys.argv = ["export.py", "--", str(SCRATCH)]
    script = Path(__file__).with_name("export.py")
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": str(script)})
    assert (SCRATCH / f"{ASSET}.glb").read_bytes() == raw, "Fresh export byte mismatch"
    report = {
        "asset": "d09_storage.01", "blender": bpy.app.version_string,
        "blender_build": bpy.app.build_hash.decode(), "exporter": "5.2.40",
        "bounds_tolerance_m": .001, "godot_bounds_min_m": export_low,
        "godot_bounds_max_m": export_high,
        "godot_dimensions_m": [b - a for a, b in zip(export_low, export_high)],
        "pivot_m": [0, 0, 0], "source_vertices": len(mesh.vertices),
        "source_faces": len(mesh.polygons), "triangles": triangles,
        "export_vertices": len(positions), "mesh_count": 1, "surface_count": 4,
        "degenerate_faces": 0, "degenerate_triangles": 0, "nonmanifold_edges": nonmanifold,
        "source_normal_max_length_error": source_normal_error,
        "export_normal_max_length_error": normal_error, "summed_closed_shell_volume_m3": volume,
        "shell_intersections": "Deliberately seated closed hardware shells, not a watertight Boolean union",
        "materials": document["materials"], "glb_bytes": len(raw),
        "glb_sha256": hashlib.sha256(raw).hexdigest(), "fresh_export_byte_identical": True,
        "source_export_status": "passed",
        "artwork_interface": {"surface_index": 3, "face_count": 2, "uv0_unit_square": True},
    }
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
