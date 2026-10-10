"""Audit the saved oval carrier, source UVs, GLB accessors and fresh export bytes."""
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
NID = "d01_sports_surface_01"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def accessor(document, binary, index):
    """Decode numeric GLB accessors rather than accepting source-only counts."""
    item = document["accessors"][index]
    view = document["bufferViews"][item["bufferView"]]
    kind = {5123: "H", 5125: "I", 5126: "f"}[item["componentType"]]
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[item["type"]]
    fmt = "<" + kind * width
    stride = view.get("byteStride", struct.calcsize(fmt))
    offset = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, offset + i * stride) for i in range(item["count"])]


def check_boundary(bm):
    """Require exactly two closed boundary loops, justified for this zero-thickness decal."""
    edges = [edge for edge in bm.edges if edge.is_boundary]
    assert len(edges) == 516
    assert not any(not edge.is_manifold and not edge.is_boundary for edge in bm.edges)
    remaining = set(vertex for edge in edges for vertex in edge.verts)
    assert all(sum(edge.is_boundary for edge in vertex.link_edges) == 2 for vertex in remaining)
    sizes = []
    while remaining:
        stack = [remaining.pop()]
        visited = set(stack)
        while stack:
            vertex = stack.pop()
            for edge in vertex.link_edges:
                if edge.is_boundary:
                    other = edge.other_vert(vertex)
                    if other not in visited:
                        visited.add(other)
                        remaining.remove(other)
                        stack.append(other)
        sizes.append(len(visited))
    assert sizes == [258, 258]
    return sizes


def main():
    """Reject geometry, datum, normal, dependency or material export regressions."""
    source = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.app.version_string == "5.2.2 LTS"
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    collection = bpy.data.collections["export_" + NID]
    assert {obj.name for obj in collection.objects} == {
        "D01SportsSurface01", "D01SportsSurface01_Mesh"}
    for obj in collection.objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
    mesh = bpy.data.objects["D01SportsSurface01_Mesh"].data
    mesh.calc_loop_triangles()
    assert len(mesh.vertices) == 516 and len(mesh.loop_triangles) == 516
    assert all(abs(n.vector.length - 1) < 1e-6 for n in mesh.corner_normals)
    assert all(p.normal.z > .99999 for p in mesh.polygons)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    degenerates = sum(face.calc_area() <= 1e-10 for face in bm.faces)
    assert degenerates == 0
    loops = check_boundary(bm)
    bm.free()
    assert len(mesh.materials) == 1 and mesh.materials[0].name == "oval_track"
    material = mesh.materials[0]
    assert material.use_backface_culling
    principled = material.node_tree.nodes["Principled BSDF"]
    assert abs(principled.inputs["Roughness"].default_value - .94) < 1e-6
    assert principled.inputs["Metallic"].default_value == 0
    image = material.node_tree.nodes["CommittedAlbedo"].image
    assert image.filepath.startswith("//") and not image.packed_file
    texture = Path(bpy.path.abspath(image.filepath)).resolve()
    assert texture == (ROOT / f"art/textures/environment/{NID}/oval_track_albedo.png").resolve()
    assert texture.is_file()
    for loop in mesh.loops:
        point = mesh.vertices[loop.vertex_index].co
        uv = mesh.uv_layers.active.data[loop.index].uv
        assert abs(uv.x - (point.x + 40) / 80) < 1e-6
        assert abs(uv.y - (point.y + 22.5) / 45) < 1e-6
    raw = glb.read_bytes()
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(raw[20:20 + length])
    binary_size, kind = struct.unpack_from("<II", raw, 20 + length)
    assert kind == 0x004E4942
    binary = raw[28 + length:28 + length + binary_size]
    assert len(doc["meshes"]) == 1 and len(doc["nodes"]) == 2
    assert len(doc["materials"]) == 1
    assert not any(doc.get(key) for key in ("images", "textures", "animations", "skins", "cameras"))
    for node in doc["nodes"]:
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
        assert "rotation" not in node and "translation" not in node
    primitives = doc["meshes"][0]["primitives"]
    assert len(primitives) == 1
    primitive = primitives[0]
    positions = accessor(doc, binary, primitive["attributes"]["POSITION"])
    normals = accessor(doc, binary, primitive["attributes"]["NORMAL"])
    uvs = accessor(doc, binary, primitive["attributes"]["TEXCOORD_0"])
    indices = [item[0] for item in accessor(doc, binary, primitive["indices"])]
    assert len(positions) == 516 and len(indices) == 1548
    assert all(math.isfinite(value) for point in positions for value in point)
    assert all(abs(Vector(normal).length - 1) < 1e-6 and normal[1] > .99999 for normal in normals)
    low = [min(point[axis] for point in positions) for axis in range(3)]
    high = [max(point[axis] for point in positions) for axis in range(3)]
    assert all(abs(a - b) < 1e-6 for a, b in zip(low, [-40, .015, -22.5]))
    assert all(abs(a - b) < 1e-6 for a, b in zip(high, [40, .015, 22.5]))
    for start in range(0, len(indices), 3):
        a, b, c = [Vector(positions[i]) for i in indices[start:start + 3]]
        cross = (b - a).cross(c - a)
        assert cross.length > 1e-8 and cross.normalized().y > .99999
        centre = (a + b + c) / 3
        # No exported triangles may close the quiet infield or extend outside the outer oval.
        radial = math.hypot(max(abs(centre.x) - 17.5, 0), centre.z)
        assert 15.89 < radial < 22.501
    for point, uv in zip(positions, uvs):
        assert abs(uv[0] - (point[0] + 40) / 80) < 1e-6
        assert abs(uv[1] - (point[2] + 22.5) / 45) < 1e-6
    sys.path.insert(0, str(Path(__file__).parent))
    from export import export_track
    export_track(SCRATCH / "reexport")
    assert (SCRATCH / "reexport" / glb.name).read_bytes() == raw
    report = {
        "asset_id": "d01_sports_surface.01", "blender": bpy.app.version_string,
        "blender_build": bpy.app.build_hash.decode(), "gltf_exporter": "5.2.40",
        "source_vertices": len(mesh.vertices), "glb_vertices": len(positions),
        "triangles": len(indices) // 3, "mesh_count": 1, "surface_count": 1,
        "degenerate_faces": 0, "degenerate_triangles": 0, "unit_normals": True,
        "upward_winding": True, "non_manifold_edges": 516, "boundary_loop_sizes": loops,
        "non_boundary_non_manifold_edges": 0,
        "boundary_justification": "Two intentional open perimeters on a flush, single-sided decal; "
            "no sidewalls or deck. World terrain owns all walk/drive collision.",
        "aabb_min_godot": low, "aabb_max_godot": high,
        "dimensions_godot_metres": [80, 0, 45], "pivot": [0, 0, 0],
        "visual_surface_y": .015, "ground_datum_y": 0,
        "infield_opening_metres": [66.8, 31.8], "uv_axis": "U east/+X, image V south/+Z",
        "embedded_images": 0, "source_texture_relative_and_unpacked": True,
        "material": {"name": "oval_track", "roughness": .94, "metallic": 0, "opaque": True},
        "texture_sha256": hashlib.sha256(texture.read_bytes()).hexdigest(),
        "glb_bytes": len(raw), "glb_sha256": hashlib.sha256(raw).hexdigest(),
        "fresh_reexport_byte_identical": True, "source_status": "PASS",
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("TRACK_SOURCE_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
