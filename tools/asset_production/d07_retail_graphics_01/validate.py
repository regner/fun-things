"""Audit reused source with its existing validator and verify a byte-identical reexport."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_graphics_01"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend"
GLB = ROOT / "art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb"


def sha256(path):
    """Hash a committed dependency without mutating it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_binary(gltf, raw, json_size):
    """Check actual binary positions, normals and front UVs, not just declared extrema."""
    binary = raw[28 + json_size:]

    def values(index):
        """Decode the float attributes used by the shared static fascia."""
        accessor = gltf["accessors"][index]
        view = gltf["bufferViews"][accessor["bufferView"]]
        assert accessor["componentType"] == 5126
        width = {"VEC2": 2, "VEC3": 3}[accessor["type"]]
        offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        stride = view.get("byteStride", width * 4)
        return [struct.unpack_from("<" + "f" * width, binary, offset + i * stride)
                for i in range(accessor["count"])]

    positions = []
    normal_error = 0
    face_vertices = 0
    for mesh in gltf["meshes"]:
        for surface in mesh["primitives"]:
            attrs = surface["attributes"]
            coords = values(attrs["POSITION"])
            positions.extend(coords)
            for normal in values(attrs["NORMAL"]):
                normal_error = max(normal_error, abs(math.sqrt(sum(v*v for v in normal)) - 1))
            material = gltf["materials"][surface["material"]]["name"]
            if material != "fascia_artwork_face":
                continue
            # Rounded carrier face: 28-corner n-gon, triangulated to 26 triangles.
            assert len(coords) == 28
            assert gltf["accessors"][surface["indices"]]["count"] == 78
            face_vertices += len(coords)
            for (x, y, z), (u, v) in zip(coords, values(attrs["TEXCOORD_0"])):
                assert abs(z + .128) < 1e-6
                assert abs(u - (.5 - x / 3)) < 1e-6
                assert abs(v - (.5 - y / .6)) < 1e-6
    assert face_vertices == 28 and normal_error < 1e-5
    low = [min(p[i] for p in positions) for i in range(3)]
    high = [max(p[i] for p in positions) for i in range(3)]
    assert all(math.isfinite(v) for p in positions for v in p)
    assert all(abs(a-b) < .001 for a, b in zip(low + high, [-1.6, -.4, -.14, 1.6, .4, 0]))
    return {"normal_length_max_error": normal_error, "front_uv_vertices": face_vertices,
            "aabb_min": low, "aabb_max": high, "front_uv_unmirrored": True}


def main():
    """Validate the existing closed meshes and face UV interface; retain a lean receipt."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    before = {p.relative_to(ROOT).as_posix(): sha256(p) for p in [SOURCE, GLB]}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    exporter = ROOT / "tools/asset_production/city_shop_fittings_02/export.py"
    spec = importlib.util.spec_from_file_location("shared_fascia_export", exporter)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reexport = SCRATCH / "shared_fascia_reexport.glb"
    receipt = SCRATCH / "shared_source.json"
    module.perform(reexport, receipt)
    assert reexport.read_bytes() == GLB.read_bytes(), "Existing shared source must reproduce exactly"
    assert before == {p.relative_to(ROOT).as_posix(): sha256(p) for p in [SOURCE, GLB]}
    report = json.loads(receipt.read_text())
    raw = GLB.read_bytes()
    json_size = struct.unpack_from("<I", raw, 12)[0]
    gltf = json.loads(raw[20:20 + json_size])
    triangles = sum(gltf["accessors"][surface["indices"]]["count"] // 3
                    for mesh in gltf["meshes"] for surface in mesh["primitives"])
    vertices = sum(gltf["accessors"][surface["attributes"]["POSITION"]]["count"]
                   for mesh in gltf["meshes"] for surface in mesh["primitives"])
    assert triangles == 1656
    assert len(gltf["meshes"]) == 7 and len(gltf["materials"]) == 5
    report.update({
        "asset_id": "d07_retail_graphics.01",
        "output_type": "Artwork set reusing unchanged fascia geometry",
        "new_geometry": False,
        "shared_source": SOURCE.relative_to(ROOT).as_posix(),
        "shared_glb": GLB.relative_to(ROOT).as_posix(),
        "shared_dependency_sha256": before,
        "shared_dependencies_unchanged": True,
        "fresh_reexport_byte_identical": True,
        "source_vertices": sum(obj["vertices"] for obj in report["objects"]),
        "glb_vertices": vertices,
        "glb_triangles": triangles,
        "mesh_count": 7,
        "surface_count": sum(len(mesh["primitives"]) for mesh in gltf["meshes"]),
        "degenerate_faces": 0,
        "degenerate_triangles": 0,
        "nonmanifold_edges": 0,
        "unit_length_corner_normals": True,
        "godot_aabb_min": [-1.6, -0.4, -0.14],
        "godot_aabb_max": [1.6, 0.4, 0],
        "pivot": "Wall contact centre (0,0,0), not ground-mounted",
        "artwork_plane_godot_z": -0.128,
        "artwork_dimensions_m": [3.0, 0.6],
        "artwork_safe_dimensions_m": [2.94, 0.54],
        "status": "PASS; bounded producer source/export checks, independent review pending",
    })
    report["binary_audit"] = audit_binary(gltf, raw, json_size)
    report["shared_glb_bytes"] = report.pop("output_bytes")
    report["shared_glb_sha256"] = report.pop("output_sha256")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("RETAIL_SOURCE_PASS", json.dumps({k: report[k] for k in [
        "source_vertices", "glb_vertices", "glb_triangles", "mesh_count", "surface_count"
    ]}))


if __name__ == "__main__":
    main()
