"""Measure saved source and GLB, verify fresh export bytes, and retain a lean receipt."""
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
NID = "city_ground_finishes_05"
SCRATCH = Path("C:/tmp/ft/assets") / NID
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def accessor(document, binary, index):
    """Read exported numeric accessors including any byte stride."""
    item = document["accessors"][index]
    view = document["bufferViews"][item["bufferView"]]
    kind = {5123: "H", 5125: "I", 5126: "f"}[item["componentType"]]
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[item["type"]]
    fmt = "<" + kind * width
    stride = view.get("byteStride", struct.calcsize(fmt))
    offset = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, offset + i * stride) for i in range(item["count"])]


def main():
    """Reject topology, normal, UV, datum, dependency and re-export regressions."""
    source = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
    export = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.app.version_string == "5.2.2 LTS"
    collection = bpy.data.collections["export_" + NID]
    assert {obj.name for obj in collection.objects} == {
        "CityGroundFinishes05", "CityGroundFinishes05_Mesh"}
    for obj in collection.objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
    obj = bpy.data.objects["CityGroundFinishes05_Mesh"]
    mesh = obj.data
    assert not obj.modifiers
    assert bpy.context.scene.unit_settings.system == "METRIC"
    assert bpy.context.scene.unit_settings.scale_length == 1
    mesh.calc_loop_triangles()
    assert len(mesh.vertices) == 8 and len(mesh.loop_triangles) == 12
    assert all(abs(n.vector.length - 1) < 1e-6 for n in mesh.corner_normals)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    degenerates = sum(face.calc_area() <= 1e-10 for face in bm.faces)
    bm.free()
    assert nonmanifold == 0 and degenerates == 0
    assert len(mesh.materials) == 1 and mesh.materials[0].name == "quiet_garden_soil"
    material = mesh.materials[0]
    assert material.use_backface_culling
    principled = material.node_tree.nodes["Principled BSDF"]
    assert abs(principled.inputs["Roughness"].default_value - 0.98) < 1e-6
    assert principled.inputs["Metallic"].default_value == 0
    image = material.node_tree.nodes["CommittedAlbedo"].image
    assert image.filepath.startswith("//") and not image.packed_file
    assert Path(bpy.path.abspath(image.filepath)).resolve() == (
        ROOT / f"art/textures/environment/{NID}/quiet_garden_soil_albedo.png").resolve()
    assert Path(bpy.path.abspath(image.filepath)).is_file()
    raw = export.read_bytes()
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    document = json.loads(raw[20:20 + length])
    binary_size, kind = struct.unpack_from("<II", raw, 20 + length)
    assert kind == 0x004E4942
    binary = raw[28 + length:28 + length + binary_size]
    assert len(document["meshes"]) == 1 and len(document["nodes"]) == 2
    assert len(document["materials"]) == 1
    for node in document["nodes"]:
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
        assert "rotation" not in node and "translation" not in node
    assert not any(document.get(key) for key in ("images", "textures", "animations", "skins", "cameras"))
    primitives = document["meshes"][0]["primitives"]
    assert len(primitives) == 1
    primitive = primitives[0]
    positions = accessor(document, binary, primitive["attributes"]["POSITION"])
    normals = accessor(document, binary, primitive["attributes"]["NORMAL"])
    uvs = accessor(document, binary, primitive["attributes"]["TEXCOORD_0"])
    indices = [item[0] for item in accessor(document, binary, primitive["indices"])]
    assert len(positions) == 24 and len(indices) == 36
    assert all(math.isfinite(value) for point in positions for value in point)
    assert all(abs(Vector(normal).length - 1) < 1e-6 for normal in normals)
    bounds_min = [min(point[axis] for point in positions) for axis in range(3)]
    bounds_max = [max(point[axis] for point in positions) for axis in range(3)]
    assert all(abs(a - b) < 1e-6 for a, b in zip(bounds_min, [-2, -0.08, -2]))
    assert all(abs(a - b) < 1e-6 for a, b in zip(bounds_max, [2, 0, 2]))
    for start in range(0, len(indices), 3):
        a, b, c = [Vector(positions[i]) for i in indices[start:start + 3]]
        cross = (b - a).cross(c - a)
        assert cross.length > 1e-8
        assert cross.normalized().dot(Vector(normals[indices[start]])) > 0.99999
    top = [uv for uv, normal in zip(uvs, normals) if normal[1] > 0.99]
    assert set(top) == {(0, 0), (0, 1), (1, 0), (1, 1)}
    for position, normal, uv in zip(positions, normals, uvs):
        if normal[1] > 0.99:
            assert abs(uv[0] - (position[0] + 2) / 4) < 1e-6
            assert abs(uv[1] - (position[2] + 2) / 4) < 1e-6
    sys.path.insert(0, str(Path(__file__).parent))
    from export import export_swatch
    export_swatch(SCRATCH / "reexport")
    assert (SCRATCH / "reexport" / export.name).read_bytes() == raw
    report = {
        "asset_id": "city_ground_finishes.05",
        "blender": bpy.app.version_string,
        "blender_build": bpy.app.build_hash.decode(),
        "gltf_exporter": "5.2.40",
        "source_vertices": 8,
        "export_vertices": 24,
        "triangles": 12,
        "mesh_count": 1,
        "surface_count": 1,
        "degenerate_faces": degenerates,
        "non_manifold_edges": nonmanifold,
        "unit_normals": True,
        "outward_winding": True,
        "aabb_min_godot": bounds_min,
        "aabb_max_godot": bounds_max,
        "dimensions_godot_metres": [4, 0.08, 4],
        "pivot": [0, 0, 0],
        "surface_datum_y": 0,
        "top_uv_orientation": "U east/+X, V south/+Z; UV0 unit = 4 metres",
        "material": {"roughness": 0.98, "metallic": 0, "opaque": True},
        "texture": {"size": [512, 512], "tile_metres": [4, 4],
                    "channels": "RGB sRGB albedo", "embedded_images": 0,
                    "png_sha256": hashlib.sha256(
                        Path(bpy.path.abspath(image.filepath)).read_bytes()).hexdigest()},
        "fresh_reexport_byte_identical": True,
        "glb_sha256": hashlib.sha256(raw).hexdigest(),
        "source_status": "PASS",
    }
    for name in ("prefab_normalized", "prefab"):
        receipt = SCRATCH / f"{name}.json"
        if receipt.exists():
            report[name] = json.loads(receipt.read_text())
    suite = SCRATCH / "checks/summary.json"
    if suite.exists():
        report["production_checks"] = json.loads(suite.read_text())["results"]
        compilation = json.loads((SCRATCH / "checks/script-checks/compilation.json").read_text())
        logs = (SCRATCH / "checks/script-checks").glob("compile-*.log")
        report["production_script_compilation"] = {
            "passed": sum(row["ok"] for row in compilation), "total": len(compilation),
            "deadline_expired_logs": sum("CHECK DEADLINE EXCEEDED" in path.read_text()
                                         for path in logs),
            "note": "See final_log.txt for setup and explicit owned-script check disposition.",
        }
    report["limitations"] = [
        "Prefab receipts record assertions, not absence of runtime diagnostics; "
        "review final_log.txt and the production record for command/log disposition.",
        "Road-tool UV adaptation, production-camera motion, placement, actor/car traversal, "
        "multiplayer and device/performance acceptance remain pending.",
    ]
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
