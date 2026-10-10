"""Validate new flashing, actual linked GLB junctions and byte-identical saved-source reexport."""
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
from mathutils.geometry import intersect_ray_tri

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_11"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EXPORT = ROOT / f"art/models/environment/{NID}/{NID}.glb"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
TOLERANCE = .00001


def receipt(path):
    """Record final payload bytes for manifest and handoff cross-checking."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def accessor(asset, binary, index):
    """Decode the actual binary accessor rather than trusting metadata bounds."""
    item = asset["accessors"][index]
    view = asset["bufferViews"][item["bufferView"]]
    code = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[item["componentType"]]
    count = {"SCALAR": 1, "VEC3": 3}[item["type"]]
    fmt = "<" + code * count
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(item["count"])]


def read_glb(path):
    """Decode identity-root static GLB positions, normals, triangles and material structure."""
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and length == len(raw)
    size, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    asset = json.loads(raw[20:20 + size])
    binary_size, kind = struct.unpack_from("<II", raw, 20 + size)
    assert kind == 0x004E4942
    binary = raw[28 + size:28 + size + binary_size]
    assert len(asset["meshes"]) == 1 and len(asset["nodes"]) == 2
    assert not any(asset.get(k) for k in ("images", "textures", "cameras", "skins", "animations"))
    for node in asset["nodes"]:
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
        assert "rotation" not in node and "translation" not in node
    positions, triangles, normals = [], [], []
    primitives = asset["meshes"][0]["primitives"]
    for primitive in primitives:
        assert primitive.get("mode", 4) == 4
        points = [Vector(v) for v in accessor(asset, binary, primitive["attributes"]["POSITION"])]
        positions.extend(points)
        normals.extend(accessor(asset, binary, primitive["attributes"]["NORMAL"]))
        indices = [v[0] for v in accessor(asset, binary, primitive["indices"])]
        for i in range(0, len(indices), 3):
            triangles.append(tuple(points[j] for j in indices[i:i + 3]))
    assert all(math.isfinite(c) for p in positions for c in p)
    assert all(abs(Vector(n).length - 1) < .0001 for n in normals)
    assert all((b - a).cross(c - a).length / 2 > 1e-10 for a, b, c in triangles)
    assert all(not m.get("doubleSided", False) and m.get("alphaMode", "OPAQUE") == "OPAQUE"
               for m in asset["materials"])
    return asset, positions, triangles


def bounds(points):
    """Return measured Godot-axis bounds."""
    return ([min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)])


def glb_path(sibling, variant=""):
    """Locate the explicit production export for a linked component."""
    suffix = "_" + variant if variant else ""
    return ROOT / f"art/models/environment/{sibling}/{sibling}{suffix}.glb"


def ray_hits(triangles, origin, direction):
    """Measure positive ray distances on actual binary triangles, including both face sides."""
    hits = []
    origin, direction = Vector(origin), Vector(direction)
    for a, b, c in triangles:
        hit = intersect_ray_tri(a, b, c, direction, origin, True)
        if hit is not None:
            distance = (hit - origin).dot(direction)
            if distance >= 0:
                hits.append(distance)
    return hits


def check_junction(flashing):
    """Reject visible seam gaps or equal-depth cross-object surfaces in the actual linked assembly."""
    components = {"flashing": flashing}
    dependencies = []
    specs = [
        ("upper_wall", "d03_apartment_family_07", "", (0, 3.2, 0)),
        ("upper_end_cap", "d03_apartment_family_10", "end", (0, 3.2, 0)),
        ("high_lower", "d03_apartment_family_05", "", (-3.12, 0, 0)),
        ("high_upper", "d03_apartment_family_05", "", (-3.12, 3.2, 0)),
        ("low", "d03_apartment_family_05", "", (2.88, 0, 0)),
        ("high_roof", "d03_apartment_family_10", "straight", (-3.12, 3.2, 0)),
        ("low_roof", "d03_apartment_family_10", "straight", (2.88, 0, 0)),
    ]
    for name, sibling, variant, offset in specs:
        path = glb_path(sibling, variant)
        asset, points, triangles = read_glb(path)
        shift = Vector(offset)
        components[name] = [tuple(v + shift for v in tri) for tri in triangles]
        if receipt(path) not in dependencies:
            dependencies.append(receipt(path))

    def nearest(origin, direction, expected_owner):
        """Require a unique nearest object, excluding duplicate triangles on the same surface."""
        distances = {name: min(hits) for name, tris in components.items()
                     if (hits := ray_hits(tris, origin, direction))}
        assert distances, (origin, direction)
        distance = min(distances.values())
        owners = [name for name, value in distances.items() if abs(value - distance) < TOLERANCE]
        assert owners == [expected_owner], (origin, owners, distances)
        return Vector(origin) + Vector(direction) * distance

    mask_samples = []
    for side in (-1, 1):
        for x in (-.115, 0, .115, .30, .49):
            for y in (3.201, 3.26, 3.39, 3.55):
                hit = nearest((x, y, side * 8), (0, 0, -side), "flashing")
                assert abs(hit.z - side * 6.12) < TOLERANCE
                mask_samples.append([x, y, hit.z])
    # Independent literal samples check toe burial below both field and coping, not just AABBs.
    toe_samples = []
    for z, roof_height in ((-5.94, 3.52), (-3, 3.42), (0, 3.42), (3, 3.42), (5.94, 3.52)):
        inside = nearest((.4999, 8, z), (0, -1, 0), "flashing")
        outside = nearest((.5001, 8, z), (0, -1, 0), "low_roof")
        assert abs(inside.y - 3.58005) < TOLERANCE
        assert abs(outside.y - roof_height) < TOLERANCE
        # A horizontal ray below roof top reaches the solid toe; its bottom is never floating.
        hits = ray_hits(flashing, (1, roof_height - .005, z), (-1, 0, 0))
        assert hits and abs(min(hits) - .5) < TOLERANCE
        toe_samples.append({"z": z, "flashing_top": inside.y, "roof_top": outside.y})
    for z in (-5.94, -4.5, 0, 4.5, 5.94):
        hit = nearest((1, 3.60, z), (-1, 0, 0), "flashing")
        assert abs(hit.x - .46) < TOLERANCE
        high = nearest((-.1201, 8, z), (0, -1, 0), "high_roof")
        end = nearest((-.1199, 8, z), (0, -1, 0), "upper_end_cap")
        assert abs(end.y - 6.72) < TOLERANCE
        assert abs(high.y - (6.72 if abs(z) > 5.76 else 6.62)) < TOLERANCE
    # Rigid 180-degree yaw maps every seam exactly without scale or mesh mutation.
    reverse = [tuple(Vector((-v.x, v.y, -v.z)) for v in tri) for tri in flashing]
    for x, y, z in mask_samples:
        side = 1 if z > 0 else -1
        hits = ray_hits(reverse, (-x, y, -side * 8), (0, 0, side))
        assert hits and abs(min(hits) - 1.88) < TOLERANCE
    return {"end_return_mask_samples": mask_samples, "toe_samples": toe_samples,
            "upper_cap_profiles": 5, "wall_flashing_profiles": 5,
            "reverse_yaw_mask_samples": len(mask_samples),
            "unique_first_surface_at_all_samples": True,
            "no_sampled_junction_gap_or_exposed_coplanar_overlap": True,
            "linked_export_receipts": dependencies}


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert bpy.app.version_string == "5.2.2 LTS"
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
collection = bpy.data.collections[f"export_{NID}"]
assert set(o.name for o in collection.objects) == {"D03ApartmentFamily11", "D03ApartmentFamily11_Mesh"}
assert not any(item.name.startswith("export_d03_apartment_family_07") or
               item.name.startswith("export_d03_apartment_family_10") for item in bpy.data.collections)
for obj in collection.objects:
    assert tuple(obj.location) == (0, 0, 0)
    assert tuple(obj.rotation_euler) == (0, 0, 0)
    assert tuple(obj.scale) == (1, 1, 1)
    assert not obj.modifiers
mesh = bpy.data.objects["D03ApartmentFamily11_Mesh"].data
mesh.calc_loop_triangles()
bm = bmesh.new()
bm.from_mesh(mesh)
nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
bm.free()
degenerate = sum(face.area <= 1e-10 for face in mesh.polygons)
assert nonmanifold == degenerate == 0
normal_error = max(abs(n.vector.length - 1) for n in mesh.corner_normals)
assert normal_error < .0001
points = [Vector((v.co.x, v.co.z, -v.co.y)) for v in mesh.vertices]
assert all(math.isfinite(c) for p in points for c in p)
low, high = bounds(points)
expected = [-.12, 3.18, -6.12, .5, 3.8, 6.12]
assert all(abs(a - b) < TOLERANCE for a, b in zip(low + high, expected))
# Three closed authored solids: central flashing and its two profile-matched return aprons.
remaining = set(range(len(mesh.vertices)))
islands = []
neighbours = {i: set() for i in remaining}
for edge in mesh.edges:
    a, b = edge.vertices
    neighbours[a].add(b)
    neighbours[b].add(a)
while remaining:
    pending = [next(iter(remaining))]
    island = set()
    while pending:
        index = pending.pop()
        if index in island:
            continue
        island.add(index)
        pending.extend(neighbours[index] - island)
    remaining -= island
    islands.append(bounds([points[i] for i in island]))
assert len(islands) == 3
for expected_bounds in [([.1, 3.4, -5.98], [.5, 3.8, 5.98]),
                        ([-.12, 3.18, -6.12], [.5, 3.8, -5.98]),
                        ([-.12, 3.18, 5.98], [.5, 3.8, 6.12])]:
    assert any(all(abs(a - b) < TOLERANCE for a, b in zip(lo + hi, sum(expected_bounds, [])))
               for lo, hi in islands)
sys.argv = [__file__, "--", str(SCRATCH / "reexport")]
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
assert EXPORT.read_bytes() == (SCRATCH / f"reexport/{NID}.glb").read_bytes()
asset, exported_points, triangles = read_glb(EXPORT)
assert [m["name"] for m in asset["materials"]] == ["terrace_bluegrey_roof", "terrace_pale_frame"]
assert len(asset["meshes"][0]["primitives"]) == 2
assert len(triangles) == len(mesh.loop_triangles)
glb_min, glb_max = bounds(exported_points)
assert all(abs(a - b) < TOLERANCE for a, b in zip(glb_min + glb_max, expected))
engine = json.loads((SCRATCH / "prefab-check.json").read_text())
assert engine["ok"] and engine["roundtrip"]["byte_stable"]
report = {
    "status": "PASS", "blender": bpy.app.version_string,
    "blender_build": bpy.app.build_hash.decode(), "gltf_exporter": "5.2.40",
    "source": receipt(SOURCE), "export": receipt(EXPORT),
    "source_vertices": len(mesh.vertices), "export_vertices": len(exported_points),
    "triangles": len(triangles), "mesh_count": 1, "surface_count": 2,
    "nonmanifold_edges": nonmanifold, "source_degenerate_faces": degenerate,
    "glb_degenerate_triangles": 0, "source_normal_max_error": normal_error,
    "export_unit_normals": True, "applied_identity_transforms": True,
    "godot_aabb_min": glb_min, "godot_aabb_max": glb_max,
    "dimensions_m": [b - a for a, b in zip(glb_min, glb_max)],
    "ground_reference_pivot": [0, 0, 0], "closed_solids": islands,
    "fresh_reexport_byte_identical": True, "materials": asset["materials"],
    "junction": check_junction(triangles), "godot": engine,
    "renders": {"resolution": [1280, 720], "compression": 95, "samples": 32,
                "renderer": "Blender Cycles CPU", "height_m": 47, "vertical_fov_degrees": 42,
                "context": "unchanged sibling collections instanced only after source save/export"},
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
