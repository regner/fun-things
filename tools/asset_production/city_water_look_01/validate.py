"""Validate saved Blender topology, actual GLB data and byte-identical fresh export."""
from pathlib import Path
import hashlib
import json
import math
import runpy
import struct
import sys

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_water_look_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
GLB = ROOT / f"art/models/environment/{NID}/{NID}.glb"
SCRATCH = Path("C:/tmp/ft/assets") / NID
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
collection = bpy.data.collections[f"export_{NID}"]
assert {obj.name for obj in collection.objects} == {"CityWaterLook01", "CityWaterLook01_Mesh"}
for obj in collection.objects:
    assert tuple(obj.location) == (0, 0, 0)
    assert tuple(obj.rotation_euler) == (0, 0, 0)
    assert tuple(obj.scale) == (1, 1, 1)
mesh = bpy.data.objects["CityWaterLook01_Mesh"].data
mesh.calc_loop_triangles()
assert len(mesh.vertices) == 4 and len(mesh.loop_triangles) == 2
assert len(mesh.materials) == 1 and mesh.materials[0].name == "open_sea"
assert bpy.context.scene.unit_settings.scale_length == 1
assert all(abs(normal.vector.length - 1) < 0.00001 for normal in mesh.corner_normals)
assert all(normal.vector.z > 0.99999 for normal in mesh.corner_normals)
assert all(math.isfinite(component) for vertex in mesh.vertices for component in vertex.co)
assert all(face.area > 0.000001 for face in mesh.polygons)
bm = bmesh.new()
bm.from_mesh(mesh)
bm.faces.ensure_lookup_table()
boundary = sum(edge.is_boundary for edge in bm.edges)
nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
assert boundary == 4 and nonmanifold == 4
assert len(bm.faces) == 1 and abs(bm.faces[0].calc_area() - 256) < 0.0001
bm.free()
for image in bpy.data.images:
    if image.source == "FILE":
        assert image.filepath.startswith("//") and not image.packed_file
        assert Path(bpy.path.abspath(image.filepath)).is_file()
        assert tuple(image.size) == (512, 512)
raw = GLB.read_bytes()
magic, version, length = struct.unpack_from("<4sII", raw)
assert (magic, version, length) == (b"glTF", 2, len(raw))
json_size, chunk_type = struct.unpack_from("<II", raw, 12)
assert chunk_type == 0x4E4F534A
metadata = json.loads(raw[20:20 + json_size])
binary_start = 20 + json_size + 8
assert len(metadata["meshes"]) == 1 and len(metadata["nodes"]) == 2
assert not any(metadata.get(key) for key in ("images", "textures", "skins", "animations", "cameras"))
primitive = metadata["meshes"][0]["primitives"][0]
assert len(metadata["meshes"][0]["primitives"]) == 1


def accessor(index):
    """Decode the actual packed scalar/vector data instead of trusting metadata counts."""
    item = metadata["accessors"][index]
    view = metadata["bufferViews"][item["bufferView"]]
    count = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}[item["type"]]
    code = {5126: "f", 5123: "H"}[item["componentType"]]
    step = struct.calcsize("<" + code * count)
    start = binary_start + view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from("<" + code * count, raw,
                               start + i * view.get("byteStride", step))
            for i in range(item["count"])]


positions = accessor(primitive["attributes"]["POSITION"])
normals = accessor(primitive["attributes"]["NORMAL"])
uvs = accessor(primitive["attributes"]["TEXCOORD_0"])
indices = [item[0] for item in accessor(primitive["indices"])]
assert len(positions) == 4 and len(indices) == 6
assert set(positions) == {(-8, 0, -8), (-8, 0, 8), (8, 0, -8), (8, 0, 8)}
assert set(uvs) == {(0, 0), (0, 1), (1, 0), (1, 1)}
assert all(tuple(normal) == (0, 1, 0) for normal in normals)
for offset in (0, 3):
    a, b, c = [Vector(positions[indices[offset + i]]) for i in range(3)]
    cross = (b - a).cross(c - a)
    assert cross.y > 0 and abs(cross.length / 2 - 128) < 0.0001
sys.argv = [__file__, "--", str(SCRATCH / "reexport")]
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
assert (SCRATCH / f"reexport/{NID}.glb").read_bytes() == raw
engine = json.loads((SCRATCH / "prefab.json").read_text())
assert engine["status"] == "PASS"
report = {
    "asset_id": "city_water_look.01", "status": "PASS",
    "blender": bpy.app.version_string, "build_hash": bpy.app.build_hash.decode(),
    "gltf_exporter": metadata["asset"]["generator"],
    "vertices": 4, "triangles": 2, "mesh_objects": 1, "surfaces": 1,
    "degenerate_faces": 0, "nonmanifold_edges": nonmanifold, "boundary_edges": boundary,
    "boundary_justification": "Exactly four intentional perimeter edges on a single-sided planar material-study swatch; not a solid or walkable water mesh.",
    "unit_source_and_glb_normals": True, "surface_area_m2": 256,
    "godot_axis_aabb": {"min": [-8, 0, -8], "max": [8, 0, 8], "size": [16, 0, 16]},
    "pivot": [0, 0, 0], "datum": "Surface centre, not ground contact",
    "dimension_tolerance_m": 0.001, "uv0_range": [0, 1], "tile_metres": 16,
    "glb_bytes": len(raw), "glb_sha256": hashlib.sha256(raw).hexdigest(),
    "fresh_reexport_byte_identical": True, "embedded_images": 0,
    "external_textures": {"count": 2, "size": [512, 512], "normal_convention": "+Y/OpenGL"},
    "engine": engine,
    "pending": ["Independent review", "Godot rendered camera/lighting review", "District placement and coastline interfaces", "Moving-camera aliasing and target-device profiling"],
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
