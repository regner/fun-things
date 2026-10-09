"""Validate source topology, actual GLB data, portal geometry and deterministic export."""
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
NID = "d06_harbour_footbridge_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}/reexport")
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
GLB = ROOT / f"art/models/environment/{NID}/{NID}.glb"
TOLERANCE = 0.00001


def accessor(doc, binary, index):
    """Decode the actual non-sparse glTF numeric accessor, respecting byte stride."""
    entry = doc["accessors"][index]
    view = doc["bufferViews"][entry["bufferView"]]
    codes = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}
    dimensions = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    fmt = "<" + codes[entry["componentType"]] * dimensions[entry["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + entry.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(entry["count"])]


def main():
    """Fail loudly on source/export contract violations and retain numerical evidence."""
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    collection = bpy.data.collections[f"export_{NID}"]
    expected_names = {"D06HarbourFootbridge03", "D06HarbourFootbridge03_Mesh",
                      "socket_incoming", "socket_outgoing"}
    assert {obj.name for obj in collection.objects} == expected_names
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    root = bpy.data.objects["D06HarbourFootbridge03"]
    assert root.location.length == 0 and root.rotation_euler.to_quaternion().angle == 0
    assert tuple(root.scale) == (1, 1, 1) and root.parent is None
    slab = bpy.data.objects["D06HarbourFootbridge03_Mesh"]
    assert slab.parent == root
    mesh = slab.data
    assert not slab.modifiers
    assert slab.location.length == 0 and slab.rotation_euler.to_quaternion().angle == 0
    assert tuple(slab.scale) == (1, 1, 1)
    assert all(abs(normal.vector.length - 1) < 0.0001 for normal in mesh.corner_normals)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    degenerate = sum(face.calc_area() <= 1e-10 for face in bm.faces)
    volume = bm.calc_volume(signed=True)
    assert nonmanifold == 0 and degenerate == 0 and volume > 0
    bm.free()
    mesh.calc_loop_triangles()
    points = [slab.matrix_world @ vertex.co for vertex in mesh.vertices]
    lo = [min(v[i] for v in points) for i in range(3)]
    hi = [max(v[i] for v in points) for i in range(3)]
    expected_lo = (-1.6, 0, -0.35)
    expected_hi = (1.6, 12, 0)
    assert all(abs(a - b) < TOLERANCE for a, b in zip(lo + hi, expected_lo + expected_hi))
    portals = {}
    for name, position, forward in (
        ("socket_incoming", (0, 0, 0), (0, -1, 0)),
        ("socket_outgoing", (0, 12, 0), (0, 1, 0)),
    ):
        socket = bpy.data.objects[name]
        assert (socket.location - Vector(position)).length < TOLERANCE
        actual_forward = socket.rotation_euler.to_matrix() @ Vector((0, 1, 0))
        assert (actual_forward - Vector(forward)).length < TOLERANCE
        assert tuple(socket.scale) == (1, 1, 1)
        # Measure the exported mating plane from source vertices, not just empty metadata.
        plane_points = [v - socket.location for v in points
                        if abs((v - socket.location).dot(actual_forward)) < TOLERANCE]
        across = Vector((actual_forward.y, -actual_forward.x, 0))
        widths = [v.dot(across) for v in plane_points]
        assert abs(min(widths) + 1.6) < TOLERANCE and abs(max(widths) - 1.6) < TOLERANCE
        assert abs(min(v.z for v in plane_points) + 0.35) < TOLERANCE
        assert abs(max(v.z for v in plane_points)) < TOLERANCE
        portals[name] = {"position_godot": [position[0], position[2], -position[1]],
                         "outward_godot": [forward[0], forward[2], -forward[1]],
                         "measured_width_m": max(widths) - min(widths),
                         "mating_plane_vertex_count": len(plane_points)}

    raw = GLB.read_bytes()
    magic, version, size = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and size == len(raw)
    json_length = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20 + json_length])
    binary = raw[28 + json_length:]
    assert len(doc["meshes"]) == 1 and len(doc["nodes"]) == 4
    assert not any(doc.get(key) for key in ("images", "textures", "skins", "animations", "cameras"))
    primitives = doc["meshes"][0]["primitives"]
    assert len(primitives) == 3
    all_positions = []
    triangle_count = 0
    exported_vertices = 0
    for primitive in primitives:
        positions = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["POSITION"])]
        normals = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["NORMAL"])]
        indices = [v[0] for v in accessor(doc, binary, primitive["indices"])]
        assert all(abs(v.length - 1) < 0.0001 for v in normals)
        assert all(math.isfinite(value) for v in positions for value in v)
        assert len(indices) % 3 == 0
        for i in range(0, len(indices), 3):
            a, b, c = (positions[j] for j in indices[i:i + 3])
            assert (b - a).cross(c - a).length / 2 > 1e-10
        triangle_count += len(indices) // 3
        exported_vertices += len(positions)
        all_positions.extend(positions)
    actual_lo = [min(v[i] for v in all_positions) for i in range(3)]
    actual_hi = [max(v[i] for v in all_positions) for i in range(3)]
    mapped_bounds = [lo[0], lo[2], -hi[1], hi[0], hi[2], -lo[1]]
    assert all(abs(a - b) < TOLERANCE for a, b in zip(actual_lo + actual_hi, mapped_bounds))
    assert triangle_count == len(mesh.loop_triangles)
    assert {m["name"] for m in doc["materials"]} == {
        "deck_warm_pale", "deck_pale_fascia", "deck_petrol_underside"}
    assert all(not m.get("doubleSided", False) for m in doc["materials"])
    expected_surfaces = [
        ("deck_warm_pale", (0.72, 0.73, 0.66, 1), 0.78),
        ("deck_pale_fascia", (0.49, 0.59, 0.59, 1), 0.56),
        ("deck_petrol_underside", (0.075, 0.16, 0.18, 1), 0.65),
    ]
    for primitive, (name, color, roughness) in zip(primitives, expected_surfaces):
        surface = doc["materials"][primitive["material"]]
        pbr = surface["pbrMetallicRoughness"]
        assert surface["name"] == name
        assert all(abs(a - b) < TOLERANCE for a, b in zip(pbr["baseColorFactor"], color))
        assert abs(pbr["roughnessFactor"] - roughness) < TOLERANCE

    SCRATCH.mkdir(parents=True, exist_ok=True)
    sys.argv = [__file__, "--", str(SCRATCH)]
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": str(export_script)})
    fresh = (SCRATCH / GLB.name).read_bytes()
    assert fresh == raw, "Fresh export differs from committed candidate"
    report = {
        "asset_id": "d06_harbour_footbridge.03", "status": "PASS",
        "blender": bpy.app.version_string, "blender_build": bpy.app.build_hash.decode(),
        "exporter": "5.2.40", "source_vertices": len(mesh.vertices),
        "triangles": triangle_count, "glb_vertices_including_surface_splits": exported_vertices,
        "mesh_count": 1, "surface_count": 3, "degenerate_faces": degenerate,
        "degenerate_export_triangles": 0, "nonmanifold_edges": nonmanifold,
        "unit_corner_and_export_normals": True, "source_signed_volume_m3": volume,
        "aabb_godot": {"min": actual_lo, "max": actual_hi,
                        "size": [b - a for a, b in zip(actual_lo, actual_hi)]},
        "pivot_godot": [0, 0, 0], "datum": "incoming portal surface centre, not ground",
        "dimension_tolerance_m": TOLERANCE, "portals": portals,
        "materials": doc["materials"], "export_nodes": doc["nodes"],
        "fresh_reexport_byte_identical": True, "glb_sha256": hashlib.sha256(raw).hexdigest(),
        "provisional_placed_surface_height_m": 5.5, "slab_depth_m": 0.35,
        "remaining_acceptance": ["Independent review", "Family assembly and world fit",
                                 "Production movement and multiplayer", "Device rendering and performance"],
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
