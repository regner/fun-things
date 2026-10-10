"""Audit the saved stepping carrier, source UVs, GLB accessors and fresh export bytes."""
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
NID = "d03_court_graphics_02"
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
    """Require eight closed eight-edge cell perimeters and no other non-manifold or branching edges."""
    boundary = {edge for edge in bm.edges if edge.is_boundary}
    assert len(boundary) == 64
    assert all(edge.is_boundary or edge.is_manifold for edge in bm.edges)
    sizes = []
    while boundary:
        seed = next(iter(boundary))
        pending = [seed]
        seen = set()
        while pending:
            edge = pending.pop()
            if edge in seen:
                continue
            seen.add(edge)
            for vertex in edge.verts:
                neighbors = [item for item in vertex.link_edges if item.is_boundary]
                assert len(neighbors) == 2
                pending.extend(item for item in neighbors if item not in seen)
        boundary -= seen
        sizes.append(len(seen))
    assert sorted(sizes) == [8] * 8
    return sorted(sizes)


def main():
    """Reject geometry, datum, normal, dependency or material export regressions."""
    source = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.app.version_string == "5.2.2 LTS"
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    collection = bpy.data.collections["export_" + NID]
    reference = bpy.data.objects["STUDIO_one_metre_reference"]
    assert tuple(reference.dimensions) == (1, 1, 1) and reference.hide_render
    assert reference.name not in collection.objects
    assert {obj.name for obj in collection.objects} == {
        "D03CourtGraphics02", "D03CourtGraphics02_Mesh"}
    for obj in collection.objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
    mesh = bpy.data.objects["D03CourtGraphics02_Mesh"].data
    mesh.calc_loop_triangles()
    assert len(mesh.vertices) == 64 and len(mesh.loop_triangles) == 48
    assert all(abs(n.vector.length - 1) < 1e-6 for n in mesh.corner_normals)
    assert all(p.normal.z > .99999 for p in mesh.polygons)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    degenerates = sum(face.calc_area() <= 1e-10 for face in bm.faces)
    assert degenerates == 0
    loops = check_boundary(bm)
    bm.free()
    assert len(mesh.materials) == 1 and mesh.materials[0].name == "play_steps"
    material = mesh.materials[0]
    assert material.use_backface_culling
    principled = material.node_tree.nodes["Principled BSDF"]
    assert abs(principled.inputs["Roughness"].default_value - .94) < 1e-6
    assert principled.inputs["Metallic"].default_value == 0
    image = material.node_tree.nodes["CommittedAlbedo"].image
    assert image.filepath.startswith("//") and not image.packed_file
    texture = Path(bpy.path.abspath(image.filepath)).resolve()
    assert texture == (ROOT / f"art/textures/environment/{NID}/play_steps_albedo.png").resolve()
    assert texture.is_file()
    for loop in mesh.loops:
        point = mesh.vertices[loop.vertex_index].co
        uv = mesh.uv_layers.active.data[loop.index].uv
        assert abs(uv.x - (point.x + 1.5) / 3) < 1e-6
        assert abs(uv.y - (point.y + 3) / 6) < 1e-6
    # Literal independently specified centres and envelopes, not imported author parameters.
    cells = [(0, -2.25), (0, -1.35), (-.5, -.45), (.5, -.45),
             (0, .45), (-.5, 1.35), (.5, 1.35), (0, 2.25)]
    assert len(mesh.polygons) == 8
    for polygon, (cx, cy) in zip(mesh.polygons, cells):
        points = [mesh.vertices[index].co for index in polygon.vertices]
        assert len(points) == 8
        assert abs(polygon.area - .7072) < 1e-6
        assert abs(min(p.x for p in points) - (cx - .45)) < 1e-6
        assert abs(max(p.x for p in points) - (cx + .45)) < 1e-6
        assert abs(min(p.y for p in points) - (cy - .4)) < 1e-6
        assert abs(max(p.y for p in points) - (cy + .4)) < 1e-6
    for vertex in mesh.vertices:
        assert abs(vertex.co.z - .015) < 1e-6
    for obj in collection.objects:
        assert not obj.modifiers
    assert len(bpy.data.libraries) == 2
    dependencies = []
    for library in bpy.data.libraries:
        assert library.filepath.startswith("//")
        path = Path(bpy.path.abspath(library.filepath)).resolve()
        assert path.is_file()
        dependencies.append({"path": path.relative_to(ROOT).as_posix(),
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                             "bytes": path.stat().st_size, "use": "studio-only linked context"})
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
    assert len(positions) == 64 and len(indices) == 144
    assert all(math.isfinite(value) for point in positions for value in point)
    assert all(abs(Vector(normal).length - 1) < 1e-6 and normal[1] > .99999 for normal in normals)
    low = [min(point[axis] for point in positions) for axis in range(3)]
    high = [max(point[axis] for point in positions) for axis in range(3)]
    assert all(abs(a - b) < 1e-6 for a, b in zip(low, [-.95, .015, -2.65]))
    assert all(abs(a - b) < 1e-6 for a, b in zip(high, [.95, .015, 2.65]))
    for start in range(0, len(indices), 3):
        a, b, c = [Vector(positions[i]) for i in indices[start:start + 3]]
        cross = (b - a).cross(c - a)
        assert cross.length > 1e-8 and cross.normalized().y > .99999
        # Every triangle belongs to one authored cell: no exported bridge across a gap.
        assert any(all(abs(point.x - cx) <= .450001 and abs(-point.z - cy) <= .400001
                       for point in (a, b, c)) for cx, cy in cells)
    exported_area = sum((Vector(positions[indices[i + 1]]) - Vector(positions[indices[i]])).cross(
        Vector(positions[indices[i + 2]]) - Vector(positions[indices[i]])).length / 2
        for i in range(0, len(indices), 3))
    assert abs(exported_area - 5.6576) < 1e-5
    for point, uv in zip(positions, uvs):
        assert abs(uv[0] - (point[0] + 1.5) / 3) < 1e-6
        assert abs(uv[1] - (point[2] + 3) / 6) < 1e-6
    sys.path.insert(0, str(Path(__file__).parent))
    from export import export_motif
    export_motif(SCRATCH / "reexport")
    assert (SCRATCH / "reexport" / glb.name).read_bytes() == raw
    report = {
        "asset_id": "d03_court_graphics.02", "blender": bpy.app.version_string,
        "blender_build": bpy.app.build_hash.decode(), "gltf_exporter": "5.2.40",
        "source_vertices": len(mesh.vertices), "glb_vertices": len(positions),
        "triangles": len(indices) // 3, "mesh_count": 1, "surface_count": 1,
        "degenerate_faces": 0, "degenerate_triangles": 0, "unit_normals": True,
        "upward_winding": True, "one_metre_studio_reference_verified": True,
        "non_manifold_edges": 64, "boundary_loop_sizes": loops,
        "non_boundary_non_manifold_edges": 0,
        "boundary_justification": "Eight intentional open cell perimeters on a flush, single-sided decal; "
            "no sidewalls or deck. World terrain owns all walk/drive collision.",
        "aabb_min_godot": low, "aabb_max_godot": high,
        "dimensions_godot_metres": [1.9, 0, 5.3], "pivot": [0, 0, 0],
        "visual_surface_y": .015, "ground_datum_y": 0,
        "uv_axis": "U east/+X, image V south/+Z",
        "embedded_images": 0, "source_texture_relative_and_unpacked": True,
        "material": {"name": "play_steps", "roughness": .94, "metallic": 0, "opaque": True},
        "painted_area_square_metres": exported_area,
        "cell_centres_blender_xy": cells, "cell_size_metres": [.9, .8],
        "cell_gap_metres": .1,
        "source_bytes": source.stat().st_size,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "studio_dependencies": dependencies,
        "texture_sha256": hashlib.sha256(texture.read_bytes()).hexdigest(),
        "glb_bytes": len(raw), "glb_sha256": hashlib.sha256(raw).hexdigest(),
        "fresh_reexport_byte_identical": True, "source_status": "PASS",
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("MOTIF_SOURCE_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
