"""Validate source topology, actual GLB data, envelopes and byte-identical fresh exports."""
import hashlib
import json
import math
import runpy
import struct
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_lights_03"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}/reexport")
EXPECTED_MIN = [-1.45, 0.0, -1.16]
EXPECTED_MAX = [1.45, 8.4, .28]


def accessor(doc, binary, index):
    """Read tightly packed or strided numeric GLB accessors, not exporter summary claims."""
    item = doc["accessors"][index]
    view = doc["bufferViews"][item["bufferView"]]
    types = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}
    width = {"SCALAR": 1, "VEC3": 3, "VEC2": 2, "VEC4": 4}[item["type"]]
    fmt = "<" + types[item["componentType"]] * width
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + row * stride)
            for row in range(item["count"])]


def read_glb(path):
    """Decode the GLB header, JSON and binary chunks with explicit length checks."""
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and length == len(raw)
    size, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(raw[20:20 + size])
    binary_size, binary_kind = struct.unpack_from("<II", raw, 20 + size)
    assert binary_kind == 0x004E4942
    binary = raw[28 + size:28 + size + binary_size]
    return raw, doc, binary


def main():
    """Reject bad topology/normals, wrong dimensions, nonidentity roots or nondeterminism."""
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    assert bpy.app.version_string == "5.2.2 LTS"
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    collection = bpy.data.collections[f"export_{ASSET}"]
    assert {obj.name for obj in collection.objects} == {"CityLights03", "CityLights03_Mesh"}
    obj = bpy.data.objects["CityLights03_Mesh"]
    root = bpy.data.objects["CityLights03"]
    assert obj.parent == root
    for node in (root, obj):
        assert node.location.length < 1e-6 and node.rotation_euler.to_matrix().is_identity
        assert all(abs(value - 1) < 1e-6 for value in node.scale)
    assert not obj.modifiers
    mesh = obj.data
    mesh.calc_loop_triangles()
    assert all(math.isfinite(value) for vertex in mesh.vertices for value in vertex.co)
    normal_error = max(abs(normal.vector.length - 1) for normal in mesh.corner_normals)
    assert normal_error < 1e-4
    degenerate_faces = sum(face.area <= 1e-10 for face in mesh.polygons)
    degenerate_triangles = sum(triangle.area <= 1e-10 for triangle in mesh.loop_triangles)
    topology = bmesh.new()
    topology.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in topology.edges)
    volume = topology.calc_volume(signed=True)
    topology.free()
    assert degenerate_faces == 0 and degenerate_triangles == 0 and nonmanifold == 0
    assert volume > 0
    coords = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    low = [min(vertex[i] for vertex in coords) for i in range(3)]
    high = [max(vertex[i] for vertex in coords) for i in range(3)]
    minimum, maximum = [low[0], low[2], -high[1]], [high[0], high[2], -low[1]]
    assert all(abs(a - b) < .001 for a, b in zip(minimum + maximum,
                                               EXPECTED_MIN + EXPECTED_MAX))
    report = {
        "asset_id": "city_lights.03", "blender": bpy.app.version_string,
        "build_hash": bpy.app.build_hash.decode(), "vertices": len(mesh.vertices),
        "triangles": len(mesh.loop_triangles), "mesh_objects": 1, "surfaces": 4,
        "degenerate_faces": degenerate_faces, "degenerate_triangles": degenerate_triangles,
        "nonmanifold_edges": nonmanifold, "max_corner_normal_length_error": normal_error,
        "source_bounds_blender": {"min": low, "max": high},
        "godot_axis_bounds_m": {"min": minimum, "max": maximum,
                                 "size": [b - a for a, b in zip(minimum, maximum)]},
        "dimension_tolerance_m": .001, "source_glb_tolerance_m": 1e-5,
        "pivot_m": [0, 0, 0], "applied_transforms": True,
        "source_material_slots": [material.name for material in mesh.materials], "exports": {},
    }
    old_args = sys.argv[:]
    try:
        sys.argv = ["export.py", "--", str(SCRATCH)]
        runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
    finally:
        sys.argv = old_args
    for variant in ("warm", "cool"):
        path = ROOT / f"art/models/environment/{ASSET}/{ASSET}_{variant}.glb"
        raw, doc, binary = read_glb(path)
        assert raw == (SCRATCH / path.name).read_bytes(), "Fresh export differs"
        assert not any(doc.get(key) for key in ("images", "textures", "skins", "animations", "cameras"))
        assert len(doc["nodes"]) == 2 and len(doc["meshes"]) == 1
        assert {node["name"] for node in doc["nodes"]} == {"CityLights03", "CityLights03_Mesh"}
        for node in doc["nodes"]:
            assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
            assert node.get("translation", [0, 0, 0]) == [0, 0, 0]
            assert node.get("rotation", [0, 0, 0, 1]) == [0, 0, 0, 1]
        primitives = doc["meshes"][0]["primitives"]
        assert len(primitives) == 4
        assert {mat["name"] for mat in doc["materials"]} == {
            "pole_petrol", "fixture_rim", "service_recess", f"lens_{variant}"}
        assert all(not mat.get("doubleSided", False) and mat.get("alphaMode", "OPAQUE") == "OPAQUE"
                   for mat in doc["materials"])
        positions, triangles, normals = [], 0, []
        for primitive in primitives:
            assert primitive.get("mode", 4) == 4
            vertices = accessor(doc, binary, primitive["attributes"]["POSITION"])
            indices = [item[0] for item in accessor(doc, binary, primitive["indices"])]
            assert len(indices) % 3 == 0
            for index in range(0, len(indices), 3):
                a, b, c = (Vector(vertices[i]) for i in indices[index:index + 3])
                assert (b - a).cross(c - a).length / 2 > 1e-10
            positions.extend(vertices)
            triangles += len(indices) // 3
            normals.extend(accessor(doc, binary, primitive["attributes"]["NORMAL"]))
        glb_min = [min(value[i] for value in positions) for i in range(3)]
        glb_max = [max(value[i] for value in positions) for i in range(3)]
        assert all(abs(a - b) < 1e-5 for a, b in zip(glb_min + glb_max, minimum + maximum))
        assert all(abs(Vector(normal).length - 1) < 1e-4 for normal in normals)
        assert triangles == report["triangles"]
        report["exports"][variant] = {
            "path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(), "vertices": len(positions),
            "triangles": triangles, "surfaces": len(primitives),
            "bounds_min_m": glb_min, "bounds_max_m": glb_max,
            "unit_length_normals": True, "degenerate_triangles": 0,
            "fresh_export_byte_identical": True, "materials": doc["materials"],
        }
    report["fresh_export_byte_identical"] = True
    report["status"] = "PASS: source topology, normals, transforms, bounds and both deterministic GLBs"
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
