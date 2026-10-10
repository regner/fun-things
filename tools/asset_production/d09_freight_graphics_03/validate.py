"""Audit both unchanged sign carriers and delegate fresh exports to their existing owners."""
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import struct
import sys

import bmesh
import bpy
import io_scene_gltf2
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_03"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
CONTRACTS = {
    "wall": {"carrier": "city_sign_supports_01", "min": [-.7, -.5, -.1],
             "max": [.7, .5, 0], "face": [1.22, .82, 0, -.088],
             "counts": [2720, 12, 13], "pivot": "wall-contact centre (0,0,0)"},
    "low": {"carrier": "city_sign_supports_02", "min": [-.8, 0, -.2],
            "max": [.8, 1.35, .2], "face": [1.44, .39, 1.075, -.071],
            "counts": [2448, 2, 5], "pivot": "ground-centred feet (0,0,0)"},
}


def fingerprint(path):
    """Measure the bytes used by this delivery, without trusting historical hashes."""
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def audit(contract):
    """Check source topology and actual binary bounds, normals, triangles and front-only UVs."""
    carrier = contract["carrier"]
    source = ROOT / f"art/source/models/environment/{carrier}/{carrier}.blend"
    glb = ROOT / f"art/models/environment/{carrier}/{carrier}.glb"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.context.scene.unit_settings.system == "METRIC"
    assert bpy.context.scene.unit_settings.scale_length == 1
    source_vertices = source_triangles = 0
    source_normal_error = 0.0
    collection = bpy.data.collections[f"export_{carrier}"]
    for obj in collection.all_objects:
        assert all(abs(v) < 1e-7 for v in obj.location)
        assert all(abs(v) < 1e-7 for v in obj.rotation_euler)
        assert all(abs(v-1) < 1e-7 for v in obj.scale)
        if obj.type != "MESH":
            assert obj.type == "EMPTY" and obj.parent is None
            continue
        assert not obj.modifiers
        mesh = obj.data
        mesh.calc_loop_triangles()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges)
        assert bm.calc_volume(signed=True) > 0
        assert all(face.calc_area() > 1e-10 for face in bm.faces)
        bm.free()
        source_normal_error = max(source_normal_error,
                                  max(abs(n.vector.length-1) for n in mesh.corner_normals))
        for tri in mesh.loop_triangles:
            a, b, c = [mesh.vertices[i].co for i in tri.vertices]
            assert (b-a).cross(c-a).length > 1e-10
        source_vertices += len(mesh.vertices)
        source_triangles += len(mesh.loop_triangles)
    assert source_normal_error < 1e-5
    # Reuse the owning exporters, never write shared output or historical receipts.
    output_dir = SCRATCH / carrier
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / glb.name
    if carrier.endswith("01"):
        spec = importlib.util.spec_from_file_location(
            "wall_export", ROOT / f"tools/asset_production/{carrier}/export.py"
        )
        exporter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exporter)
        exporter.perform(output, output_dir / "owner_source.json")
    else:
        sys.argv = ["export.py", "--", str(output_dir)]
        runpy.run_path(str(ROOT / f"tools/asset_production/{carrier}/export.py"),
                      run_name="__main__")
    assert output.read_bytes() == glb.read_bytes()
    raw = glb.read_bytes()
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    length = struct.unpack_from("<I", raw, 12)[0]
    document = json.loads(raw[20:20+length])
    binary = raw[28+length:]

    def accessor(index):
        """Decode actual typed accessors with their stride and byte offsets."""
        entry = document["accessors"][index]
        view = document["bufferViews"][entry["bufferView"]]
        count = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}[entry["type"]]
        fmt = "<" + {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[entry["componentType"]]*count
        start = view.get("byteOffset", 0) + entry.get("byteOffset", 0)
        stride = view.get("byteStride", struct.calcsize(fmt))
        return [struct.unpack_from(fmt, binary, start+i*stride) for i in range(entry["count"])]

    vertices = triangles = surfaces = face_surfaces = face_triangles = 0
    normal_error = 0.0
    coords = []
    for node in document["nodes"]:
        assert not any(key in node for key in ("matrix", "translation", "rotation", "scale"))
    for mesh in document["meshes"]:
        for surface in mesh["primitives"]:
            positions = accessor(surface["attributes"]["POSITION"])
            normals = accessor(surface["attributes"]["NORMAL"])
            indices = [i[0] for i in accessor(surface["indices"])]
            coords.extend(positions)
            vertices += len(positions)
            triangles += len(indices)//3
            surfaces += 1
            normal_error = max(normal_error, max(abs(Vector(n).length-1) for n in normals))
            for offset in range(0, len(indices), 3):
                ids = indices[offset:offset+3]
                a, b, c = [Vector(positions[i]) for i in ids]
                cross = (b-a).cross(c-a)
                assert cross.length > 1e-10
                assert cross.dot(sum((Vector(normals[i]) for i in ids), Vector())) > 0
            if document["materials"][surface["material"]]["name"] == "sign_face":
                face_surfaces += 1
                face_triangles += len(indices)//3
                width, height, centre, z = contract["face"]
                uvs = accessor(surface["attributes"]["TEXCOORD_0"])
                for p, uv, normal in zip(positions, uvs, normals):
                    assert abs(p[2]-z) < 1e-6 and normal[2] < -.99999
                    assert abs(uv[0] - (.5-p[0]/width)) < 1e-6
                    assert abs(uv[1] - (.5-(p[1]-centre)/height)) < 1e-6
    low = [min(p[i] for p in coords) for i in range(3)]
    high = [max(p[i] for p in coords) for i in range(3)]
    assert all(abs(a-b) < 1e-6 for a, b in zip(low+high, contract["min"]+contract["max"]))
    assert [triangles, len(document["meshes"]), surfaces] == contract["counts"]
    assert triangles == source_triangles and face_surfaces == 1 and normal_error < 1e-5
    assert not any(document.get(k) for k in ("images", "textures", "skins", "animations", "cameras"))
    return {"carrier": carrier, "source_vertices": source_vertices, "glb_vertices": vertices,
            "triangles": triangles, "meshes": len(document["meshes"]), "surfaces": surfaces,
            "degenerate_faces": 0, "degenerate_glb_triangles": 0, "nonmanifold_edges": 0,
            "max_source_normal_length_error": source_normal_error,
            "max_glb_normal_length_error": normal_error, "outward_winding": True,
            "aabb_min": low, "aabb_max": high, "pivot": contract["pivot"],
            "face_dimensions_m": contract["face"][:2], "face_triangles": face_triangles,
            "upright_outside_left_to_right_uv": True, "face_surface": 0,
            "fresh_reexport_byte_identical": True, "glb": fingerprint(glb)}


def main():
    """Keep a measured receipt and prove every shared dependency stayed unchanged."""
    assert bpy.app.version_string == "5.2.2 LTS"
    assert bpy.app.build_hash.decode() == "d13f752e3b9c"
    assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    paths = [ROOT / "tools/assets/blender/export_settings.json"]
    for suffix in ("01", "02"):
        paths.append(ROOT / f"tools/asset_production/d09_freight_graphics_{suffix}/author.py")
    for contract in CONTRACTS.values():
        carrier = contract["carrier"]
        paths.extend([
            ROOT / f"art/source/models/environment/{carrier}/{carrier}.blend",
            ROOT / f"art/models/environment/{carrier}/{carrier}.glb",
            ROOT / f"art/models/environment/{carrier}/{carrier}.glb.import",
            ROOT / f"scenes/prefabs/environment/{carrier}.tscn",
            ROOT / f"tools/asset_production/{carrier}/export.py",
        ])
    before = {p.relative_to(ROOT).as_posix(): fingerprint(p) for p in paths}
    reports = {variant: audit(contract) for variant, contract in CONTRACTS.items()}
    assert before == {p.relative_to(ROOT).as_posix(): fingerprint(p) for p in paths}
    report = {"asset_id": "d09_freight_graphics.03", "status": "PASS", "new_geometry": False,
              "blender": bpy.app.version_string, "build_hash": bpy.app.build_hash.decode(),
              "exporter": "5.2.40", "shared_dependencies_unchanged": True,
              "dependencies": before, "carriers": reports}
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2)+"\n",
                                             encoding="utf-8", newline="\n")
    print("LOADING_SOURCE_PASS: both carriers, topology, UVs, bounds and byte-identical exports")


if __name__ == "__main__":
    main()
