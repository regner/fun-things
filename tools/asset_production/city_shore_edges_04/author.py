"""Construct six original corner/terminal solids using the saved sibling cut-face contracts."""
from collections import Counter, defaultdict
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_shore_edges_04"
FAMILIES = {"wall": "01", "quay": "02", "rock": "03"}
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1


def read_sections(number):
    """Read ordered closed boundary loops, not the sibling's unordered end vertex receipt."""
    sibling = "city_shore_edges_" + number
    source = ROOT / f"art/source/models/environment/{sibling}/{sibling}.blend"
    with bpy.data.libraries.load(str(source), link=False) as (available, loaded):
        loaded.objects = ["CityShoreEdges" + number + "_Mesh"]
    obj = loaded.objects[0]
    mesh = obj.data
    edges = Counter()
    materials = {}
    for face in mesh.polygons:
        if all(abs(mesh.vertices[i].co.x + 2) < 1e-6 for i in face.vertices):
            for a, b in face.edge_keys:
                edge = tuple(sorted((a, b)))
                edges[edge] += 1
                materials[edge] = mesh.materials[face.material_index]
    adjacency = defaultdict(list)
    for (a, b), count in edges.items():
        if count == 1:
            adjacency[a].append(b)
            adjacency[b].append(a)
    assert all(len(neighbors) == 2 for neighbors in adjacency.values())
    sections = []
    unused = set(adjacency)
    while unused:
        first = min(unused)
        loop, previous, current = [first], first, min(adjacency[first])
        while current != first:
            loop.append(current)
            previous, current = current, next(v for v in adjacency[current] if v != previous)
        unused.difference_update(loop)
        material = materials[tuple(sorted((loop[0], loop[1]))) ]
        # Existing shared mineral names are one contract, never a suffixed duplicate.
        material = bpy.data.materials.get(material.name.split(".")[0], material)
        sections.append(([(mesh.vertices[i].co.y, mesh.vertices[i].co.z) for i in loop], material))
    bpy.data.objects.remove(obj, do_unlink=True)
    return sections


def closed_loft(collection, name, rings, material, smooth):
    """Build manifold closed rings; triangulate only after corner planes are explicit."""
    count = len(rings[0])
    vertices = [v for ring in rings for v in ring]
    faces = [tuple(reversed(range(count)))]
    for station in range(len(rings) - 1):
        for i in range(count):
            a, b = station * count + i, station * count + (i + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(rings) - 1) * count, len(rings) * count)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if smooth:
        for face in bm.faces:
            face.smooth = len(face.verts) == 4
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="FIXED")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    if smooth:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        weighted = obj.modifiers.new("Broad mineral facet normals", "WEIGHTED_NORMAL")
        weighted.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=weighted.name)
        obj.select_set(False)
    return obj


def rings_for(profile, family, variant):
    """Sweep a 90-degree mitre or a short finished end without changing the mating section."""
    rings = []
    if variant == "corner":
        stations = [-2, -1.5, -1, 0, 1, 1.5, 2] if family == "rock" else [-2, 0, 2]
        rock_section = max(z for _, z in profile) > 0
        crest = max(z for _, z in profile)
        for station in stations:
            ring = []
            for u, z in profile:
                if family == "rock" and rock_section and abs(station) < 2:
                    # Two quiet shoulders flank the mitre; preserve the exact end section.
                    peak = .65 if abs(station) == 1.5 else (.46 if station == 0 else .53)
                    z = -.3 + (z + .3) * (peak + .3) / (crest + .3)
                    u *= .92 if abs(station) == 1 else 1
                if station < 0:
                    ring.append((station, u, z))
                elif station > 0:
                    ring.append((-u, station, z))
                else:
                    ring.append((-u, u, z))
            rings.append(ring)
    else:
        for x, width in [(-.5, 1), (-.12, 1), (.35, 1), (.5, .84)]:
            ring = []
            for u, z in profile:
                if family == "rock":
                    crest = max(v for _, v in profile)
                    if crest > 0 and x != -.5:
                        peak = .65 if x == -.12 else (.43 if x == .35 else .15)
                        z = -.3 + (z + .3) * (peak + .3) / (crest + .3)
                    width = {-.5: 1, -.12: 1, .35: .8, .5: .4}[x]
                elif x == .5:
                    bottom, top = (0, 1) if family == "wall" else (-2.4, 0)
                    z = bottom + .025 + (z - bottom) * (top - bottom - .05) / (top - bottom)
                ring.append((x, u * width, z))
            rings.append(ring)
    return rings


for family, number in FAMILIES.items():
    sections = read_sections(number)
    for variant in ("corner", "end"):
        suffix = family + "_" + variant
        collection = bpy.data.collections.new("export_" + ASSET + "_" + suffix)
        scene.collection.children.link(collection)
        parts = []
        for index, (profile, material) in enumerate(sections):
            parts.append(closed_loft(collection, suffix + "_solid_" + str(index),
                         rings_for(profile, family, variant), material,
                         family == "rock" and max(z for _, z in profile) > 0))
        bpy.ops.object.select_all(action="DESELECT")
        for obj in parts:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        bpy.ops.object.join()
        obj = bpy.context.object
        name = "CityShoreEdges04_" + suffix
        obj.name = name + "_Mesh"
        root = bpy.data.objects.new(name, None)
        collection.objects.link(root)
        obj.parent = root
        root["asset_id"] = "city_shore_edges.04"
        root["authorship"] = "Original Blender loft construction from project sibling section contracts"
        root["interface"] = "Corner X=-2/Y=2 or end X=-.5; Blender Z=land datum; metres"
        root["sibling"] = "city_shore_edges." + number
# Remove appended but unused complete sibling mesh datablocks, never retain duplicate carriers.
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SIX_SOURCE_COMPONENTS_SAVED", source)
