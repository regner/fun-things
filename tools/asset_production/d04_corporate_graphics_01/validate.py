"""Audit saved source and decoded GLB, including independent face visibility and UV checks."""
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
NID = "d04_corporate_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
GLB = ROOT / f"art/models/environment/{NID}/{NID}.glb"


def close(actual, expected, tolerance=1e-5):
    """Compare coordinates against independent literal envelope/UV expectations."""
    assert len(actual) == len(expected)
    assert all(abs(a-b) < tolerance for a, b in zip(actual, expected)), (actual, expected)


def decode_glb(path):
    """Decode actual packed accessor data rather than trusting metadata bounds."""
    raw = path.read_bytes()
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    length = struct.unpack_from("<I", raw, 12)[0]
    gltf = json.loads(raw[20:20+length])
    binary = raw[28+length:]

    def accessor(index):
        """Read this export's scalar/vector accessor with any declared byte stride."""
        item = gltf["accessors"][index]
        view = gltf["bufferViews"][item["bufferView"]]
        code = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[item["componentType"]]
        width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[item["type"]]
        fmt = "<" + code * width
        stride = view.get("byteStride", struct.calcsize(fmt))
        offset = view.get("byteOffset", 0) + item.get("byteOffset", 0)
        return [struct.unpack_from(fmt, binary, offset+i*stride) for i in range(item["count"])]

    assert len(gltf["meshes"]) == 2 and len(gltf["nodes"]) == 3
    for key in ("images", "textures", "animations", "skins", "cameras"):
        assert not gltf.get(key)
    coords = []
    vertices = triangles = surfaces = front_vertices = 0
    for mesh in gltf["meshes"]:
        for primitive in mesh["primitives"]:
            positions = accessor(primitive["attributes"]["POSITION"])
            normals = accessor(primitive["attributes"]["NORMAL"])
            indices = [i[0] for i in accessor(primitive["indices"])]
            assert all(abs(Vector(n).length-1) < 1e-5 for n in normals)
            assert all(math.isfinite(c) for p in positions for c in p)
            for start in range(0, len(indices), 3):
                ids = indices[start:start+3]
                a, b, c = [Vector(positions[i]) for i in ids]
                normal = (b-a).cross(c-a)
                assert normal.length > 1e-10
                assert normal.dot(sum((Vector(normals[i]) for i in ids), Vector())) > 0
            if gltf["materials"][primitive["material"]]["name"] == "sign_face":
                uv = accessor(primitive["attributes"]["TEXCOORD_0"])
                for p, n, t in zip(positions, normals, uv):
                    # Applied weighted normals retain a sub-milliradian bevel influence.
                    close(n, [0, 0, -1], tolerance=.001)
                    assert abs(p[2]+.128) < 1e-5
                    close(t, [(2.68-p[0])/5.36, (1.88-p[1])/3.76])
                    front_vertices += 1
            coords.extend(positions)
            vertices += len(positions)
            triangles += len(indices)//3
            surfaces += 1
    close([min(p[i] for p in coords) for i in range(3)], [-2.8, -2, -.14])
    close([max(p[i] for p in coords) for i in range(3)], [2.8, 2, 0])
    assert front_vertices >= 4 and surfaces == 5
    return {"vertices": vertices, "triangles": triangles, "meshes": 2, "surfaces": surfaces,
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "degenerate_triangles": 0, "unit_normals": True, "outward_winding": True,
            "front_uv_vertices_checked": front_vertices, "front_uv_upright_unmirrored": True}


def main():
    """Validate source, prove no hidden face, and byte-compare a fresh saved-source export."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    collection = bpy.data.collections[f"export_{NID}"]
    assert set(o.name for o in collection.all_objects) == {
        "D04CorporateGraphics01", "D04CorporateGraphics01_Hardware",
        "D04CorporateGraphics01_ArtworkCarrier"}
    objects = []
    for obj in collection.all_objects:
        close(obj.location, [0, 0, 0])
        close(obj.rotation_euler, [0, 0, 0])
        close(obj.scale, [1, 1, 1])
        assert not obj.modifiers
        if obj.type != "MESH":
            continue
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges), obj.name
        assert bm.calc_volume(signed=True) > 0
        assert all(p.area > 1e-10 for p in mesh.polygons)
        assert all(abs(n.vector.length-1) < 1e-5 for n in mesh.corner_normals)
        mesh.calc_loop_triangles()
        objects.append({"name": obj.name, "vertices": len(mesh.vertices),
                        "triangles": len(mesh.loop_triangles), "nonmanifold_edges": 0,
                        "degenerate_faces": 0, "unit_normals": True,
                        "slots": [m.name for m in mesh.materials]})
        bm.free()
    # Independently ray-test a 5 x 3 grid from the front, catching an occluding gasket/tray.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for x in (-2.5, -1.25, 0, 1.25, 2.5):
        for z in (-1.7, 0, 1.7):
            hit, position, normal, face, obj, _ = scene.ray_cast(
                depsgraph, Vector((x, 1, z)), Vector((0, -1, 0)))
            assert hit and obj.name == "D04CorporateGraphics01_ArtworkCarrier", obj
            assert obj.data.polygons[face].material_index == 0
            assert abs(position.y-.128) < 1e-5
    SCRATCH.mkdir(parents=True, exist_ok=True)
    original = GLB.read_bytes()
    sys.argv = ["export.py", "--", str(SCRATCH / "reexport")]
    runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
    assert (SCRATCH / f"reexport/{NID}.glb").read_bytes() == original
    report = {"asset_id": "d04_corporate_graphics.01", "blender": bpy.app.version_string,
              "build_hash": bpy.app.build_hash.decode(), "exporter": "5.2.40",
              "source_objects": objects, "source_vertices": sum(o["vertices"] for o in objects),
              "source_triangles": sum(o["triangles"] for o in objects),
              "degenerate_faces": 0, "nonmanifold_edges": 0, "unit_normals": True,
              "glb": decode_glb(GLB), "fresh_reexport_byte_identical": True,
              "face_visibility_rays": 15, "aabb_min_godot": [-2.8, -2, -.14],
              "aabb_max_godot": [2.8, 2, 0], "dimensions_m": [5.6, 4, .14],
              "pivot": "Wall-contact centre; Blender +Y / Godot -Z front",
              "face_dimensions_m": [5.36, 3.76], "status": "PASS"}
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print("CORPORATE_VALIDATION_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
