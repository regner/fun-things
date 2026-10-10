"""Measure six saved rail components, actual GLB accessors, and fresh-export identity."""
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
ASSET = "city_quay_furniture_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence/validation.json"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}/reexport")
# Independent literal Godot-axis envelope expectations, in metres.
BOUNDS = {
    "straight": ([-1.5, .45, -.05], [1.5, 1, .05]),
    "corner": ([-.75, .45, -.75], [.80, 1, .80]),
    "end": ([0, .43, -.05], [.535, 1, .05]),
    "post_quay": ([-.15, 0, -.15], [.15, 1.06, .15]),
    "post_deck": ([-.11, 0, -.17], [.11, 1.06, .17]),
    "post_landward": ([-.16, 0, -.16], [.16, 1.06, .16]),
}


def accessor(document, binary, index):
    """Read the delivered binary stream, respecting glTF offsets and byte stride."""
    entry = document["accessors"][index]
    view = document["bufferViews"][entry["bufferView"]]
    fmt = "<" + {5123: "H", 5125: "I", 5126: "f"}[entry["componentType"]] * {
        "SCALAR": 1, "VEC3": 3}[entry["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    offset = view.get("byteOffset", 0) + entry.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, offset + i * stride) for i in range(entry["count"])]


def check_component(component):
    """Reject invalid topology, transforms, surface contracts or source/export drift."""
    collection = bpy.data.collections[f"export_{ASSET}_{component}"]
    name = "CityQuayFurniture02_" + component
    assert {obj.name for obj in collection.objects} == {name, name + "_Mesh"}
    for obj in collection.objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
    obj = bpy.data.objects[name + "_Mesh"]
    assert not obj.modifiers
    mesh = obj.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    assert all(edge.is_manifold for edge in bm.edges)
    assert bm.calc_volume(signed=True) > 0
    bm.free()
    assert all(math.isfinite(c) for vertex in mesh.vertices for c in vertex.co)
    assert all(face.area > 1e-10 for face in mesh.polygons)
    assert all(triangle.area > 1e-10 for triangle in mesh.loop_triangles)
    source_error = max(abs(normal.vector.length - 1) for normal in mesh.corner_normals)
    assert source_error < 1e-5
    coordinates = [(v.co.x, v.co.z, -v.co.y) for v in mesh.vertices]
    minimum = [min(v[i] for v in coordinates) for i in range(3)]
    maximum = [max(v[i] for v in coordinates) for i in range(3)]
    expected_min, expected_max = BOUNDS[component]
    assert all(abs(a - b) < .001 for a, b in zip(minimum + maximum, expected_min + expected_max)), (
        component, minimum, maximum)
    export = ROOT / f"art/models/environment/{ASSET}/{ASSET}_{component}.glb"
    raw = export.read_bytes()
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    json_length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    document = json.loads(raw[20:20 + json_length])
    bin_length, kind = struct.unpack_from("<II", raw, 20 + json_length)
    assert kind == 0x004E4942
    binary = raw[28 + json_length:28 + json_length + bin_length]
    assert not any(document.get(key) for key in ("animations", "skins", "cameras", "images", "textures"))
    assert len(document["meshes"]) == 1 and len(document["nodes"]) == 2
    for node in document["nodes"]:
        assert node.get("translation", [0, 0, 0]) == [0, 0, 0]
        assert node.get("rotation", [0, 0, 0, 1]) == [0, 0, 0, 1]
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
    primitives = document["meshes"][0]["primitives"]
    expected_surfaces = 3 if component.startswith("post_") else 1
    assert len(primitives) == expected_surfaces
    positions = []
    triangles = 0
    export_error = 0.0
    for primitive in primitives:
        assert primitive.get("mode", 4) == 4
        local = accessor(document, binary, primitive["attributes"]["POSITION"])
        normals = accessor(document, binary, primitive["attributes"]["NORMAL"])
        indices = [v[0] for v in accessor(document, binary, primitive["indices"])]
        assert len(indices) % 3 == 0
        for offset in range(0, len(indices), 3):
            a, b, c = (Vector(local[index]) for index in indices[offset:offset + 3])
            assert (b - a).cross(c - a).length * .5 > 1e-10
        positions.extend(local)
        triangles += len(indices) // 3
        export_error = max(export_error, max(abs(Vector(n).length - 1) for n in normals))
    assert export_error < 1e-5
    assert triangles == len(mesh.loop_triangles)
    gmin = [min(v[i] for v in positions) for i in range(3)]
    gmax = [max(v[i] for v in positions) for i in range(3)]
    assert all(abs(a - b) < 1e-5 for a, b in zip(gmin + gmax, minimum + maximum))
    materials = document["materials"]
    assert all(not mat.get("doubleSided", False) for mat in materials)
    assert {mat["name"] for mat in materials} == {mat.name for mat in mesh.materials}
    assert (SCRATCH / export.name).read_bytes() == raw, "Fresh export differs: " + component
    return {"source_vertices": len(mesh.vertices), "source_faces": len(mesh.polygons),
            "export_vertices": len(positions), "triangles": triangles, "mesh_count": 1,
            "surface_count": len(primitives), "godot_bounds_min_m": gmin,
            "godot_bounds_max_m": gmax, "pivot_m": [0, 0, 0],
            "degenerate_faces": 0, "degenerate_triangles": 0, "nonmanifold_edges": 0,
            "source_normal_max_length_error": source_error,
            "export_normal_max_length_error": export_error, "materials": materials,
            "glb_bytes": len(raw), "glb_sha256": hashlib.sha256(raw).hexdigest(),
            "fresh_export_byte_identical": True}


def main():
    """Open the committed source and export afresh before validating every component."""
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    sys.argv = ["export.py", "--", str(SCRATCH)]
    script = Path(__file__).parent / "export.py"
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": __file__})
    report = {"asset": "city_quay_furniture.02", "blender": bpy.app.version_string,
              "blender_build": bpy.app.build_hash.decode(), "exporter": "5.2.40",
              "dimensions_provisional": True, "bounds_tolerance_m": .001,
              "components": {name: check_component(name) for name in BOUNDS},
              "source_export_status": "passed"}
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("CITY_QUAY_FURNITURE_02_SOURCE_PASS")
    for name, values in report["components"].items():
        print(name, values["triangles"], "triangles", values["export_vertices"], "export vertices")


if __name__ == "__main__":
    main()
