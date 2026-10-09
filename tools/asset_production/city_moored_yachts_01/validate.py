"""Validate source/export geometry; seal or verify the complete producer payload."""
import hashlib
import json
import math
from pathlib import Path
import runpy
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "city_moored_yachts_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
MODEL = ROOT / f"art/models/environment/{NID}/{NID}.glb"


def sha256(path):
    """Hash the actual file bytes without including local filesystem metadata."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def produced_files():
    """Enumerate only this asset's source, runtime, tooling and lean evidence."""
    directories = [SOURCE.parent, MODEL.parent, EVIDENCE, Path(__file__).parent]
    files = [ROOT / f"docs/assets/production/{NID}.md"]
    files.extend((ROOT / "scenes/prefabs/environment").glob(f"{NID}.tscn*"))
    for directory in directories:
        files.extend(path for path in directory.rglob("*") if path.is_file()
                     and "__pycache__" not in path.parts and path.name != "manifest.json")
    return sorted(files)


def manifest(verify=False):
    """Seal all payload hashes, excluding only the self-referential manifest."""
    rows = [{"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
             "sha256": sha256(path)} for path in produced_files()]
    path = EVIDENCE / "manifest.json"
    if verify:
        assert json.loads(path.read_text())["files"] == rows, "Producer payload changed"
        print(f"PASS: {len(rows)} producer payload hashes and exact path set")
    else:
        path.write_text(json.dumps({"asset_id": "city_moored_yachts.01",
                        "excludes": ["manifest.json (self-reference)"], "files": rows},
                        indent=2) + "\n", encoding="utf-8")
        print(f"Sealed {len(rows)} produced files")


def accessor(document, binary, index):
    """Decode actual GLB float/index arrays, including accessor byte strides."""
    item = document["accessors"][index]
    view = document["bufferViews"][item["bufferView"]]
    formats = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}
    sizes = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    fmt = "<" + formats[item["componentType"]] * sizes[item["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    offset = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, offset + i * stride) for i in range(item["count"])]


def validate_geometry():
    """Assert independent envelope/topology expectations and fresh export identity."""
    import bmesh
    import bpy
    from mathutils import Vector

    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    collection = bpy.data.collections[f"export_{NID}"]
    assert {o.name for o in collection.objects} == {"CityMooredYachts01", "CityMooredYachts01_Mesh"}
    root = bpy.data.objects["CityMooredYachts01"]
    obj = bpy.data.objects["CityMooredYachts01_Mesh"]
    assert obj.parent == root
    for node in collection.objects:
        assert all(abs(value) < 1e-6 for value in node.location)
        assert all(abs(value) < 1e-6 for value in node.rotation_euler)
        assert all(abs(value - 1) < 1e-6 for value in node.scale)
    assert bpy.context.scene.unit_settings.system == "METRIC"
    assert bpy.context.scene.unit_settings.scale_length == 1
    assert not obj.modifiers
    mesh = obj.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    assert nonmanifold == 0, nonmanifold
    assert all(face.area > 1e-10 for face in mesh.polygons)
    assert all(tri.area > 1e-10 for tri in mesh.loop_triangles)
    assert all(math.isfinite(value) for vertex in mesh.vertices for value in vertex.co)
    normal_error = max(abs(normal.vector.length - 1) for normal in mesh.corner_normals)
    assert normal_error < 1e-4
    coordinates = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    lower = [min(point[axis] for point in coordinates) for axis in range(3)]
    upper = [max(point[axis] for point in coordinates) for axis in range(3)]
    godot_min = [lower[0], lower[2], -upper[1]]
    godot_max = [upper[0], upper[2], -lower[1]]
    # Approved nominal envelope; rub strake endcap has <= 15 mm bow overhang.
    expected_min = [-1.9, -1.0, -6.2]
    expected_max = [1.9, 3.1, 6.2]
    assert all(abs(a - b) < 0.015 for a, b in zip(godot_min + godot_max,
                                                expected_min + expected_max)), (godot_min, godot_max)
    assert abs(lower[2] + 1) < 0.001 and abs(upper[2] - 3.1) < 0.001
    raw = MODEL.read_bytes()
    magic, version, size = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and size == len(raw)
    json_size, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    document = json.loads(raw[20:20 + json_size])
    bin_size, kind = struct.unpack_from("<II", raw, 20 + json_size)
    assert kind == 0x004E4942
    binary = raw[28 + json_size:28 + json_size + bin_size]
    assert len(document["nodes"]) == 2 and len(document["meshes"]) == 1
    for key in ("images", "textures", "animations", "skins", "cameras"):
        assert not document.get(key)
    for node in document["nodes"]:
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
        assert not node.get("rotation") and not node.get("translation")
    primitives = document["meshes"][0]["primitives"]
    assert len(primitives) == 7
    assert {m["name"] for m in document["materials"]} == {
        "hull_ivory", "glazing_petrol", "waterline_navy", "deck_sand",
        "hardware_slate", "upholstery_cream", "accent_coral",
    }
    for mat in document["materials"]:
        assert not mat.get("doubleSided", False)
        assert mat.get("alphaMode", "OPAQUE") == "OPAQUE"
    positions = []
    exported_triangles = 0
    exported_normal_error = 0
    for primitive in primitives:
        verts = accessor(document, binary, primitive["attributes"]["POSITION"])
        normals = accessor(document, binary, primitive["attributes"]["NORMAL"])
        indices = [row[0] for row in accessor(document, binary, primitive["indices"])]
        positions.extend(verts)
        assert len(indices) % 3 == 0
        exported_triangles += len(indices) // 3
        exported_normal_error = max(exported_normal_error,
                                   max(abs(Vector(n).length - 1) for n in normals))
        for i in range(0, len(indices), 3):
            a, b, c = [Vector(verts[index]) for index in indices[i:i + 3]]
            assert (b - a).cross(c - a).length / 2 > 1e-10
    assert exported_normal_error < 1e-4
    assert exported_triangles == len(mesh.loop_triangles)
    actual_min = [min(v[i] for v in positions) for i in range(3)]
    actual_max = [max(v[i] for v in positions) for i in range(3)]
    assert all(abs(a - b) < 1e-5 for a, b in zip(actual_min + actual_max,
                                              godot_min + godot_max))
    scratch = Path("C:/tmp/ft/assets") / NID / "reexport"
    saved_args = sys.argv[:]
    sys.argv = [str(Path(__file__).with_name("export.py")), "--", str(scratch)]
    runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
    sys.argv = saved_args
    assert (scratch / MODEL.name).read_bytes() == raw, "Saved-source reexport differs"
    report = {
        "asset_id": "city_moored_yachts.01", "blender": bpy.app.version_string,
        "build_hash": bpy.app.build_hash.decode(), "exporter": "5.2.40",
        "source": {"vertices": len(mesh.vertices), "triangles": len(mesh.loop_triangles),
                   "mesh_count": 1, "material_surfaces": 7, "nonmanifold_edges": nonmanifold,
                   "degenerate_faces": 0, "degenerate_triangles": 0,
                   "max_unit_normal_error": normal_error,
                   "bounds_blender": {"min": lower, "max": upper}},
        "godot_axis_bounds": {"min": actual_min, "max": actual_max,
                              "size": [b - a for a, b in zip(actual_min, actual_max)]},
        "datum": {"pivot": [0, 0, 0], "waterline_y_m": 0, "draft_m": 1,
                  "bow": "Godot -Z", "nominal_envelope_tolerance_m": 0.015,
                  "source_export_tolerance_m": 0.00001},
        "glb": {"vertices": len(positions), "triangles": exported_triangles,
                "meshes": 1, "surfaces": 7, "degenerate_triangles": 0,
                "max_unit_normal_error": exported_normal_error,
                "bytes": len(raw), "sha256": sha256(MODEL),
                "fresh_saved_source_reexport_byte_identical": True,
                "materials": document["materials"]},
        "evidence_camera": {"render": "isolated Blender; not engine acceptance",
                            "height_m": 47, "vertical_fov_degrees": 42,
                            "resolution": [1280, 720], "north_up": True},
        "pending": ["independent review", "actual dock placement and clearance",
                    "production actor/weapon and network checks", "target-device performance"],
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    bm.free()
    print(json.dumps(report, indent=2))
    print("PASS: topology, normals, independent bounds, GLB content and byte-identical reexport")


if __name__ == "__main__":
    if "--manifest-only" in sys.argv:
        manifest()
    elif "--verify-manifest" in sys.argv:
        manifest(verify=True)
    else:
        validate_geometry()
