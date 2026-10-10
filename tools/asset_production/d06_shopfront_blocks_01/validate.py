"""Read-only Blender source audit of the seven reused models; no assembly mesh is authored."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/assets/production/d06_shopfront_blocks_01-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
assert bpy.app.build_hash.decode() == "d13f752e3b9c"
report = json.loads((EVIDENCE / "validation.json").read_text())
assert report["status"] == "passed"
counts = Counter(item["path"].removeprefix("res://") for item in report["model_instances"])
models = []


def receipt(path):
    """Identify an existing immutable input without modifying its producer receipt."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


for relative, instances in sorted(counts.items()):
    glb = ROOT / relative
    asset = glb.parent.name
    source = ROOT / f"art/source/models/environment/{asset}/{asset}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.context.scene.unit_settings.scale_length == 1
    collection = ("variant_single" if asset in ("city_shop_fittings_03", "city_shop_fittings_06")
                  else "export_" + asset)
    objects = bpy.data.collections[collection].all_objects
    vertices = triangles = nonmanifold = degenerate = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        assert not obj.modifiers, obj.name
        assert all(abs(v - 1) < 1e-6 for v in obj.scale), obj.name
        assert all(abs(v) < 1e-6 for v in obj.rotation_euler), obj.name
        mesh = obj.data
        assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
        assert all(abs(n.vector.length - 1) < 1e-4 for n in mesh.corner_normals)
        mesh.calc_loop_triangles()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        nonmanifold += sum(not e.is_manifold for e in bm.edges)
        assert all(e.is_contiguous for e in bm.edges)
        bm.free()
        degenerate += sum(p.area <= 1e-10 for p in mesh.polygons)
        for triangle in mesh.loop_triangles:
            a, b, c = (mesh.vertices[i].co for i in triangle.vertices)
            assert (b - a).cross(c - a).length > 1e-10
        vertices += len(mesh.vertices)
        triangles += len(mesh.loop_triangles)
    assert nonmanifold == degenerate == 0, asset
    raw = glb.read_bytes()
    length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(raw[20:20 + length])
    assert not doc.get("images") and not doc.get("skins") and not doc.get("animations")
    primitives = [p for mesh in doc["meshes"] for p in mesh["primitives"]]
    exported_triangles = sum(doc["accessors"][p["indices"]]["count"] // 3 for p in primitives)
    assert exported_triangles == triangles
    models.append({"source": receipt(source), "glb": receipt(glb), "collection": collection,
                   "instances": instances, "source_vertices": vertices, "triangles": triangles,
                   "exported_split_vertices": sum(doc["accessors"][p["attributes"]["POSITION"]]
                                                  ["count"] for p in primitives),
                   "meshes": len(doc["meshes"]), "surfaces": len(primitives),
                   "degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
                   "unit_corner_normals": True})
report["geometry"] = {
    "scope": "fresh read-only audit of reused Blender sources and raw GLB accessor counts",
    "blender": bpy.app.version_string, "build": bpy.app.build_hash.decode(),
    "models": models,
    "instance_weighted": {key: sum(m[key] * m["instances"] for m in models)
                          for key in ("source_vertices", "triangles", "exported_split_vertices",
                                      "meshes", "surfaces", "degenerate_faces", "nonmanifold_edges")},
    "new_meshes": 0,
    "fresh_reexport": "not applicable: assembly has no new or modified GLB; shared sources untouched",
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print("REUSED_SOURCE_AUDIT_PASS", json.dumps(report["geometry"]["instance_weighted"]))
