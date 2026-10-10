"""Validate unchanged shared fascia via its owner, then audit actual GLB accessors."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_01"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
SOURCE = ROOT / "art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend"
GLB = ROOT / "art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def fingerprint(path):
    """Capture dependency bytes and digest without touching shared source or output."""
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    """Delegate source contract checks and reexport, independently check the exported triangles."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    before = {p.relative_to(ROOT).as_posix(): fingerprint(p) for p in [SOURCE, GLB]}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    spec = importlib.util.spec_from_file_location(
        "shared_fascia_export", ROOT / "tools/asset_production/city_shop_fittings_02/export.py"
    )
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    output = SCRATCH / "shared_fascia_reexport.glb"
    receipt = SCRATCH / "shared_source.json"
    exporter.perform(output, receipt)
    assert output.read_bytes() == GLB.read_bytes(), "Shared source must reproduce byte-for-byte"
    assert before == {p.relative_to(ROOT).as_posix(): fingerprint(p) for p in [SOURCE, GLB]}
    source_report = json.loads(receipt.read_text())
    raw = GLB.read_bytes()
    json_length = struct.unpack_from("<I", raw, 12)[0]
    gltf = json.loads(raw[20:20 + json_length])
    binary = raw[28 + json_length:]

    def accessor(index):
        """Read the GLB's typed, possibly strided accessors directly from the binary chunk."""
        info = gltf["accessors"][index]
        view = gltf["bufferViews"][info["bufferView"]]
        component = {5126: "f", 5123: "H", 5125: "I"}[info["componentType"]]
        count = {"VEC3": 3, "SCALAR": 1}[info["type"]]
        fmt = "<" + component * count
        start = view.get("byteOffset", 0) + info.get("byteOffset", 0)
        stride = view.get("byteStride", struct.calcsize(fmt))
        return [struct.unpack_from(fmt, binary, start + i*stride) for i in range(info["count"])]

    triangles = vertices = surfaces = 0
    normal_error = 0.0
    all_positions = []
    for mesh in gltf["meshes"]:
        for surface in mesh["primitives"]:
            positions = [Vector(p) for p in accessor(surface["attributes"]["POSITION"])]
            normals = [Vector(n) for n in accessor(surface["attributes"]["NORMAL"])]
            indices = [i[0] for i in accessor(surface["indices"])]
            assert len(indices) % 3 == 0
            for i in range(0, len(indices), 3):
                a, b, c = [positions[j] for j in indices[i:i+3]]
                assert (b-a).cross(c-a).length > 1e-10, "Degenerate exported triangle"
            normal_error = max(normal_error, max(abs(n.length - 1) for n in normals))
            triangles += len(indices) // 3
            vertices += len(positions)
            surfaces += 1
            all_positions.extend(positions)
    low = [min(v[i] for v in all_positions) for i in range(3)]
    high = [max(v[i] for v in all_positions) for i in range(3)]
    assert all(abs(a-b) < 1e-6 for a, b in zip(low+high, [-1.6, -.4, -.14, 1.6, .4, 0]))
    assert normal_error < 1e-5
    assert (triangles, vertices, surfaces, len(gltf["meshes"])) == (1656, 1072, 8, 7)
    assert not gltf.get("images") and not gltf.get("animations")
    report = {
        "asset_id": "d09_freight_graphics.01", "status": "PASS",
        "blender": source_report["blender"], "build_hash": source_report["build_hash"],
        "exporter": source_report["gltf_exporter"],
        "shared_source_audit": source_report,
        "dependencies": before, "shared_dependencies_unchanged": True,
        "fresh_reexport_byte_identical": True, "new_geometry": False,
        "source_vertices": sum(o["vertices"] for o in source_report["objects"]),
        "glb_vertices": vertices, "triangles": triangles, "mesh_count": len(gltf["meshes"]),
        "surface_count": surfaces, "degenerate_faces": 0, "degenerate_glb_triangles": 0,
        "nonmanifold_edges": 0, "unit_source_corner_normals": True,
        "max_glb_normal_length_error": normal_error,
        "aabb_min": low, "aabb_max": high, "dimensions_m": [3.2, .8, .14],
        "pivot": "wall-contact centre (0,0,0); no ground contact",
        "face_dimensions_m": [3.0, .6], "safe_dimensions_m": [2.94, .54],
        "artwork_plane_godot_z": -.128,
    }
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"FREIGHT_SOURCE_PASS: {vertices} GLB vertices; {triangles} triangles; byte-identical")


if __name__ == "__main__":
    main()
