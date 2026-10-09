"""Validate closed Blender shells and actual GLB buffers, then byte-compare fresh saved-source exports."""
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
NID = "d06_harbour_footbridge_06"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}/reexport")
# Independent nominal envelopes. End bevels may inset a sloped extremum by up to 6 mm.
EXPECTED = {
    "junction": ((-3, -0.15, -3), (3.295118, 1.2, 3.295118)),
    "span": ((-1.66, -0.15, -12), (1.66, 1.2, 0)),
    "main": ((-1.66, -0.15, -19.84), (1.66, 6.88, 0)),
    "south": ((-1.66, -0.15, -11.58), (9.92, 6.88, 0)),
    "quay": ((-9.92, -0.15, -11.58), (1.66, 6.88, 0)),
    "support_tall": ((-1.2, 0, -0.6), (1.2, 5.15, 0.6)),
    "support_mid": ((-1.2, 0, -0.6), (1.2, 2.4, 0.6)),
}


def accessor(doc, binary, index):
    """Decode actual non-sparse exported buffers with their component types and stride."""
    entry = doc["accessors"][index]
    view = doc["bufferViews"][entry["bufferView"]]
    codes = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}
    dimensions = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    fmt = "<" + codes[entry["componentType"]] * dimensions[entry["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + entry.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start+i*stride) for i in range(entry["count"])]


def bounds(coords):
    """Measure the actual vertices rather than trusting stored accessor extrema."""
    return [min(v[i] for v in coords) for i in range(3)] + [
        max(v[i] for v in coords) for i in range(3)]


def check_variant(variant):
    """Check the independently specified envelope, transforms, manifold shells and exported normals."""
    name = f"D06HarbourFootbridge06_{variant}"
    collection = bpy.data.collections[f"export_{NID}_{variant}"]
    assert {obj.name for obj in collection.objects} == {name, name+"_Mesh"}
    root, obj = bpy.data.objects[name], bpy.data.objects[name+"_Mesh"]
    assert obj.parent == root and root.parent is None
    for node in (root, obj):
        assert node.location.length == 0 and node.rotation_euler.to_quaternion().angle == 0
        assert tuple(node.scale) == (1, 1, 1) and not node.modifiers
    mesh = obj.data
    mesh.calc_loop_triangles()
    assert all(abs(n.vector.length-1) < 0.0001 for n in mesh.corner_normals)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not e.is_manifold for e in bm.edges)
    degenerate = sum(f.calc_area() <= 1e-10 for f in bm.faces)
    volume = bm.calc_volume(signed=True)
    assert nonmanifold == 0 and degenerate == 0 and volume > 0
    bm.free()
    actual = bounds([Vector((v.co.x, v.co.z, -v.co.y)) for v in mesh.vertices])
    lo, hi = EXPECTED[variant]
    assert all(abs(a-b) < 0.008 for a, b in zip(actual, lo+hi)), (variant, actual)
    path = ROOT / f"art/models/environment/{NID}/{NID}_{variant}.glb"
    raw = path.read_bytes()
    magic, version, size = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and size == len(raw)
    n = struct.unpack_from("<I", raw, 12)[0]
    doc, binary = json.loads(raw[20:20+n]), raw[28+n:]
    assert len(doc["meshes"]) == 1 and len(doc["nodes"]) == 2
    assert not any(doc.get(k) for k in ("images", "textures", "skins", "animations", "cameras"))
    assert all(n.get("scale", [1, 1, 1]) == [1, 1, 1] for n in doc["nodes"])
    assert all("rotation" not in n and "translation" not in n for n in doc["nodes"])
    primitives = doc["meshes"][0]["primitives"]
    surfaces = 3 if variant.startswith("support") else 2
    assert len(primitives) == surfaces
    positions_all, triangles = [], 0
    for primitive in primitives:
        positions = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["POSITION"])]
        normals = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["NORMAL"])]
        indices = [v[0] for v in accessor(doc, binary, primitive["indices"])]
        assert all(abs(v.length-1) < 0.0001 for v in normals)
        assert all(math.isfinite(c) for v in positions for c in v)
        assert len(indices) % 3 == 0
        for i in range(0, len(indices), 3):
            a, b, c = (positions[j] for j in indices[i:i+3])
            assert (b-a).cross(c-a).length / 2 > 1e-10
        triangles += len(indices)//3
        positions_all.extend(positions)
    exported = bounds(positions_all)
    assert all(abs(a-b) < 0.00001 for a, b in zip(actual, exported))
    assert triangles == len(mesh.loop_triangles)
    expected_names = (["deck_warm_pale", "deck_pale_fascia", "deck_petrol_underside"]
                      if surfaces == 3 else ["rail_dark_teal", "edge_cyan"])
    assert [doc["materials"][p["material"]]["name"] for p in primitives] == expected_names
    assert all(not mat.get("doubleSided", False) for mat in doc["materials"])
    assert all(mat.get("alphaMode", "OPAQUE") == "OPAQUE" for mat in doc["materials"])
    if surfaces == 2:
        cyan = next(m for m in doc["materials"] if m["name"] == "edge_cyan")
        assert all(abs(a-b) < 1e-5 for a, b in zip(cyan["emissiveFactor"], (.054, .2925, .324)))
    return {"source_vertices": len(mesh.vertices), "triangles": triangles,
            "glb_vertices_including_surface_splits": len(positions_all), "mesh_count": 1,
            "surface_count": surfaces, "degenerate_faces": degenerate,
            "nonmanifold_edges": nonmanifold, "degenerate_export_triangles": 0,
            "unit_corner_and_export_normals": True, "source_signed_volume_m3": volume,
            "aabb_godot": {"min": actual[:3], "max": actual[3:],
                           "size": [actual[i+3]-actual[i] for i in range(3)]},
            "nominal_aabb_godot": {"min": lo, "max": hi}, "pivot_godot": [0, 0, 0],
            "materials": doc["materials"], "export_nodes": doc["nodes"],
            "glb_sha256": hashlib.sha256(raw).hexdigest()}


def main():
    """Validate every collection and compare every fresh export against its delivered counterpart."""
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
    assert bpy.app.version_string == "5.2.2 LTS"
    assert bpy.context.scene.unit_settings.system == "METRIC"
    assert bpy.context.scene.unit_settings.scale_length == 1
    assert not bpy.data.libraries, "No render-context dependencies may leak into saved source"
    variants = {variant: check_variant(variant) for variant in EXPECTED}
    SCRATCH.mkdir(parents=True, exist_ok=True)
    sys.argv = [__file__, "--", str(SCRATCH)]
    script = Path(__file__).parent / "export.py"
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": str(script)})
    for variant, result in variants.items():
        fresh = (SCRATCH / f"{NID}_{variant}.glb").read_bytes()
        assert hashlib.sha256(fresh).hexdigest() == result["glb_sha256"]
        result["fresh_reexport_byte_identical"] = True
    report = {"asset_id": "d06_harbour_footbridge.06", "status": "PASS",
              "blender": bpy.app.version_string, "build": bpy.app.build_hash.decode(),
              "exporter": "5.2.40", "variants": variants,
              "nominal_envelope_tolerance_m": 0.008, "source_export_tolerance_m": 0.00001,
              "shell_note": "Separate closed rail/post/strip/pier shells; intentional joint overlaps.",
              "support_placement": "Unplaced: road/land fit approval required."}
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
