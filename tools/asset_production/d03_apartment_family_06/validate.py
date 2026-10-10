"""Check both source corner solids, binary GLBs, family joins and exact saved-source reexport."""
import hashlib
import json
import math
from pathlib import Path
import runpy
import struct
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_06"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
MATERIALS = ["terrace_bluegrey_render", "terrace_pale_frame", "terrace_teal_spandrel",
             "terrace_petrol_closed_glass", "terrace_coral_corner"]
# Literal expectations are independent of the author script's construction logic.
FOOTPRINTS = {
    "outside": [(-6, -6), (6, -6), (6, 6), (-6, 6)],
    "inside": [(-9, -9), (9, -9), (9, 3), (3, 3), (3, 9), (-9, 9)],
}
BOUNDS = {"outside": ([-6.18, 0, -6.18], [6, 3.2, 6]),
          "inside": ([-9.18, 0, -9.18], [9, 3.2, 9])}


def receipt(path):
    """Record final payload bytes without relying on timestamps."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def accessor(asset, binary, index):
    """Decode binary accessor data rather than relying only on GLB metadata."""
    item = asset["accessors"][index]
    view = asset["bufferViews"][item["bufferView"]]
    code = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[item["componentType"]]
    components = {"SCALAR": 1, "VEC3": 3}[item["type"]]
    fmt = "<" + code * components
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(item["count"])]


def measure(variant):
    """Require closed manifold topology, uninflated joints, unit normals and correct core volume."""
    collection = bpy.data.collections[f"export_{NID}_{variant}"]
    name = "D03ApartmentFamily06" + variant.title()
    assert set(o.name for o in collection.objects) == {name, name + "_Mesh"}
    for obj in collection.objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
        assert not obj.modifiers
    mesh = bpy.data.objects[name + "_Mesh"].data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    bm.free()
    degenerate = sum(face.area <= 1e-10 for face in mesh.polygons)
    assert nonmanifold == degenerate == 0
    assert all(math.isfinite(v) for vert in mesh.vertices for v in vert.co)
    normal_error = max(abs(n.vector.length - 1) for n in mesh.corner_normals)
    assert normal_error < .0001
    coords = [Vector((v.co.x, v.co.z, -v.co.y)) for v in mesh.vertices]
    expected_min, expected_max = BOUNDS[variant]
    low = [min(v[i] for v in coords) for i in range(3)]
    high = [max(v[i] for v in coords) for i in range(3)]
    assert all(abs(a - b) < .00001 for a, b in zip(low + high, expected_min + expected_max))
    for x, z in FOOTPRINTS[variant]:
        for y in (0, 3.2):
            assert any((v - Vector((x, y, z))).length < .00001 for v in coords)
    core_volume = 0
    for triangle in mesh.loop_triangles:
        if triangle.material_index == 0:
            a, b, c = [coords[index] for index in triangle.vertices]
            core_volume += a.dot(b.cross(c)) / 6
    assert abs(core_volume - (460.8 if variant == "outside" else 921.6)) < .001

    export = ROOT / f"art/models/environment/{NID}/{NID}_{variant}.glb"
    raw = export.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and length == len(raw)
    json_size, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    asset = json.loads(raw[20:20 + json_size])
    bin_size, kind = struct.unpack_from("<II", raw, 20 + json_size)
    assert kind == 0x004E4942
    binary = raw[28 + json_size:28 + json_size + bin_size]
    assert not any(asset.get(k) for k in ("images", "textures", "animations", "skins", "cameras"))
    assert len(asset["meshes"]) == 1 and len(asset["nodes"]) == 2
    for node in asset["nodes"]:
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
        assert "rotation" not in node and "translation" not in node
    primitives = asset["meshes"][0]["primitives"]
    assert len(primitives) == 5
    positions, normals = [], []
    triangles, glb_degenerate = 0, 0
    for primitive in primitives:
        assert primitive.get("mode", 4) == 4
        points = accessor(asset, binary, primitive["attributes"]["POSITION"])
        positions.extend(points)
        normals.extend(accessor(asset, binary, primitive["attributes"]["NORMAL"]))
        indices = [v[0] for v in accessor(asset, binary, primitive["indices"])]
        triangles += len(indices) // 3
        for i in range(0, len(indices), 3):
            a, b, c = [Vector(points[j]) for j in indices[i:i + 3]]
            glb_degenerate += (b - a).cross(c - a).length / 2 <= 1e-10
    assert glb_degenerate == 0
    assert all(abs(Vector(n).length - 1) < .0001 for n in normals)
    glb_min = [min(v[i] for v in positions) for i in range(3)]
    glb_max = [max(v[i] for v in positions) for i in range(3)]
    assert all(abs(a - b) < .00001 for a, b in zip(glb_min + glb_max,
                                               expected_min + expected_max))
    assert triangles == len(mesh.loop_triangles)
    assert [mat["name"] for mat in asset["materials"]] == MATERIALS
    assert all(not mat.get("doubleSided", False) and mat.get("alphaMode", "OPAQUE") == "OPAQUE"
               for mat in asset["materials"])
    assert (SCRATCH / f"reexport/{NID}_{variant}.glb").read_bytes() == raw
    return {
        "source_vertices": len(mesh.vertices), "triangles": triangles,
        "export_vertices": len(positions), "mesh_count": 1, "surface_count": len(primitives),
        "source_degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
        "glb_degenerate_triangles": glb_degenerate, "maximum_source_normal_error": normal_error,
        "glb_unit_normals": True, "godot_aabb_min": glb_min, "godot_aabb_max": glb_max,
        "dimensions_m": [b - a for a, b in zip(glb_min, glb_max)], "pivot": [0, 0, 0],
        "structural_footprint_xz": FOOTPRINTS[variant], "core_volume_m3": core_volume,
        "connector_corners_exact": True, "export": receipt(export),
        "fresh_reexport_byte_identical": True, "materials": asset["materials"],
    }


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
sys.argv = [__file__, "--", str(SCRATCH / "reexport")]
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
report = {
    "status": "PASS", "blender": bpy.app.version_string,
    "blender_build": bpy.app.build_hash.decode(), "gltf_exporter": "5.2.40",
    "source": receipt(SOURCE), "dimension_tolerance_m": .001,
    "axis_mapping_tolerance_m": .00001,
    "variants": {variant: measure(variant) for variant in ("outside", "inside")},
    "renders": {"resolution": [1280, 720], "compression": 95, "renderer": "Blender Cycles CPU",
                "samples": 32, "dither_intensity": 0, "overhead_height_m": 47,
                "vertical_fov_degrees": 42, "presentation_only_x_offsets_m": [-11, 8]},
}
engine = SCRATCH / "prefab-check.json"
if engine.exists():
    report["godot"] = json.loads(engine.read_text())
    assert report["godot"]["ok"]
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
