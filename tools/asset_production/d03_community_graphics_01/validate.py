"""Audit reused noticeboard topology, binary face mapping and immutable fresh export."""
import hashlib
import importlib.util
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
NID = "d03_community_graphics_01"
CARRIER = "city_sign_supports_03"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def fingerprint(path):
    """Retain exact shared dependency identities without modifying their receipts."""
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    """Measure original geometry independently and prove the artwork needs no new carrier."""
    source = ROOT / f"art/source/models/environment/{CARRIER}/{CARRIER}.blend"
    glb = ROOT / f"art/models/environment/{CARRIER}/{CARRIER}.glb"
    dependencies = [source, glb, glb.with_suffix(".glb.import"),
                    ROOT / f"scenes/prefabs/environment/{CARRIER}.tscn",
                    ROOT / f"tools/asset_production/{CARRIER}/export.py",
                    ROOT / "tools/assets/blender/export_settings.json",
                    ROOT / "tools/asset_production/d03_court_graphics_02/validate.py"]
    before = {p.relative_to(ROOT).as_posix(): fingerprint(p) for p in dependencies}
    # Reuse the preceding lane sibling's pure accessor decoder; do not run its validator.
    spec = importlib.util.spec_from_file_location("court_binary", dependencies[-1])
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.app.version_string == "5.2.2 LTS"
    assert bpy.context.scene.unit_settings.system == "METRIC"
    assert bpy.context.scene.unit_settings.scale_length == 1
    collection = bpy.data.collections["export_" + CARRIER]
    assert {obj.name for obj in collection.objects} == {
        "CitySignSupports03", "CitySignSupports03_Hardware", "CitySignSupports03_ArtworkCarrier"}
    source_vertices = source_triangles = 0
    for obj in collection.objects:
        assert tuple(obj.location) == (0,0,0) and tuple(obj.rotation_euler) == (0,0,0)
        assert tuple(obj.scale) == (1,1,1)
        if obj.type != "MESH":
            continue
        assert not obj.modifiers
        mesh = obj.data
        mesh.calc_loop_triangles()
        source_vertices += len(mesh.vertices)
        source_triangles += len(mesh.loop_triangles)
        assert all(abs(n.vector.length-1) < .0001 for n in mesh.corner_normals)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges)
        assert all(f.calc_area() > 1e-10 for f in bm.faces)
        assert bm.calc_volume(signed=True) > 0
        bm.free()
    face = bpy.data.objects["CitySignSupports03_ArtworkCarrier"].data
    assert [m.name for m in face.materials] == ["sign_face", "mount_metal"]
    for polygon in face.polygons:
        if polygon.material_index != 0:
            continue
        assert polygon.normal.y > .99999
        for index in polygon.loop_indices:
            point = face.vertices[face.loops[index].vertex_index].co
            uv = face.uv_layers.active.data[index].uv
            assert abs(uv.x-(.82-point.x)/1.64) < 1e-5
            assert abs(uv.y-(point.z-.9)/1.04) < 1e-5
    raw = glb.read_bytes()
    length = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20+length])
    binary = raw[28+length:]
    assert len(doc["meshes"]) == 2 and len(doc["nodes"]) == 3
    assert not any(doc.get(k) for k in ("images","textures","animations","skins","cameras"))
    points_all = []
    triangles = vertices = surfaces = art_surfaces = 0
    for mesh in doc["meshes"]:
        for surface, primitive in enumerate(mesh["primitives"]):
            surfaces += 1
            points = decoder.accessor(doc,binary,primitive["attributes"]["POSITION"])
            normals = decoder.accessor(doc,binary,primitive["attributes"]["NORMAL"])
            indices = [v[0] for v in decoder.accessor(doc,binary,primitive["indices"])]
            points_all.extend(points)
            vertices += len(points)
            triangles += len(indices)//3
            assert all(math.isfinite(v) for p in points for v in p)
            assert all(abs(Vector(n).length-1)<.0001 for n in normals)
            for i in range(0,len(indices),3):
                a,b,c = [Vector(points[j]) for j in indices[i:i+3]]
                cross = (b-a).cross(c-a)
                assert cross.length_squared > 1e-20
                assert cross.dot(sum((Vector(normals[j]) for j in indices[i:i+3]),Vector())) > 0
            if doc["materials"][primitive["material"]]["name"] == "sign_face":
                art_surfaces += 1
                assert surface == 0 and mesh["name"] == "CitySignSupports03_ArtworkCarrier"
                uvs = decoder.accessor(doc,binary,primitive["attributes"]["TEXCOORD_0"])
                for point,uv,normal in zip(points,uvs,normals):
                    assert abs(point[2]+.071) < 1e-5 and Vector(normal).z < -.99999
                    assert abs(uv[0]-(.82-point[0])/1.64) < 1e-5
                    assert abs(uv[1]-(1.94-point[1])/1.04) < 1e-5
    lo = [min(p[i] for p in points_all) for i in range(3)]
    hi = [max(p[i] for p in points_all) for i in range(3)]
    assert all(abs(a-b)<1e-5 for a,b in zip(lo+hi,[-.95,0,-.22,.95,2.1,.22]))
    assert (source_vertices,source_triangles,vertices,triangles,surfaces,art_surfaces) == (
        1340,2636,1711,2636,5,1)
    sys.argv = ["export.py", "--", str(SCRATCH / "reexport")]
    runpy.run_path(str(Path(__file__).with_name("export.py")),run_name="__main__")
    assert (SCRATCH / "reexport" / glb.name).read_bytes() == raw
    assert before == {p.relative_to(ROOT).as_posix(): fingerprint(p) for p in dependencies}
    report = {"asset_id":"d03_community_graphics.01", "status":"PASS", "new_geometry":False,
              "blender":bpy.app.version_string,"blender_build":bpy.app.build_hash.decode(),
              "exporter":"5.2.40", "dependencies":before,"shared_dependencies_unchanged":True,
              "source_vertices":source_vertices,"triangles":triangles,"glb_vertices":vertices,
              "meshes":2,"surfaces":surfaces,"nonmanifold_edges":0,"degenerate_faces":0,
              "degenerate_glb_triangles":0,"unit_source_export_normals":True,
              "godot_aabb":{"min":lo,"max":hi},"dimensions_m":[1.9,2.1,.44],
              "pivot":[0,0,0],"ground_datum_m":0,"fresh_reexport_byte_identical":True,
              "face":{"slot":0,"material":"sign_face","size_m":[1.64,1.04],
                      "safe_copy_m":[1.58,.98],"front_z_m":-.071,"upright_unmirrored_uv":True}}
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    (EVIDENCE / "validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8", newline="\n")
    print("COMMUNITY_SOURCE_PASS: unchanged carrier, topology/UV audit and identical fresh export")


if __name__ == "__main__":
    main()
