"""Author three broad original slate outcrops over a continuous closed shore toe."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_shore_edges_03"
# Input Blender (Y,Z) profiles: water faces +Y. Validation records the final beveled
# and clipped X +/-2 section, which is the separately owned .04 connector interface.
TOE_PROFILE = [(-.72, -.6), (-.8, -.48), (-.76, -.3),
               (.76, -.3), (.8, -.48), (.72, -.6)]
END_PROFILE = [(-.76, -.3), (-.8, -.10), (-.73, .12), (-.56, .30),
               (-.25, .42), (.18, .42), (.48, .32), (.70, .12),
               (.8, -.10), (.76, -.3)]
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)


def material(name, color, roughness):
    """Keep broad mineral tones compatible with the municipal shore siblings."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    return mat


slate = material("shore_body_slate", (.20, .265, .29), .72)
foot = material("shore_foot_dark_slate", (.095, .145, .16), .78)
weathered = material("shore_rock_weathered_slate", (.32, .39, .41), .76)
parts = []


def loft(name, stations, mat, smooth=False):
    """Close a sequence of original cross-sections, with explicit triangulation of warped faces."""
    count = len(stations[0][1])
    vertices = [(x, y, z) for x, profile in stations for y, z in profile]
    faces = [tuple(reversed(range(count)))]
    for station in range(len(stations) - 1):
        for i in range(count):
            a = station * count + i
            b = station * count + (i + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(stations) - 1) * count, len(stations) * count)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(mat)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    # Only side faces shade continuously. The cut ends remain flat and never alter seam normals.
    for face in bm.faces:
        face.smooth = smooth and abs(face.normal.x) < .999
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="FIXED")
    bm.to_mesh(mesh)
    bm.free()
    parts.append(obj)


def rock(name, stations, mat, mirrored=False):
    """Shape an original convex outcrop, soften mineral edges, then cut only the shared end plane."""
    vertices = []
    for x, width, lift, shift, lean in stations:
        for y, z in END_PROFILE:
            height_factor = max(0, (z + .3) / .72)
            vertices.append((x + lean * height_factor, y * width + shift,
                             z + lift * height_factor))
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for vertex in vertices:
        bm.verts.new(vertex)
    hull = bmesh.ops.convex_hull(bm, input=list(bm.verts))
    bmesh.ops.delete(bm, geom=hull["geom_interior"], context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.dissolve_limit(bm, angle_limit=.02, verts=list(bm.verts), edges=list(bm.edges))
    bevel_edges = [edge for edge in bm.edges if edge.calc_face_angle(0) > .50]
    bmesh.ops.bevel(bm, geom=bevel_edges, offset=.04, segments=3,
                    affect="EDGES", clamp_overlap=True)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
    cut = bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                                plane_co=(-2, 0, 0), plane_no=(1, 0, 0),
                                clear_inner=True, dist=1e-7)
    boundary = [edge for edge in cut["geom_cut"]
                if isinstance(edge, bmesh.types.BMEdge) and edge.is_boundary]
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary)
    if mirrored:
        for vertex in bm.verts:
            vertex.co.x = -vertex.co.x
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for face in bm.faces:
        face.smooth = abs(face.normal.x) < .999
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    weighted = obj.modifiers.new("Broad mineral facet normals", "WEIGHTED_NORMAL")
    weighted.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    obj.select_set(False)
    parts.append(obj)


loft("Continuous dark shore toe", [(x, [(y * width, z) for y, z in TOE_PROFILE])
     for x, width in [(-2, 1), (-1.45, .97), (-.72, .88), (0, .98),
                      (.72, .88), (1.45, .97), (2, 1)]], foot)
# End outcrops share an exact mirrored cut section. The central outcrop has its
# own asymmetric silhouette; large overlapping shoulders hide deep gaps, not tiny rubble.
end_stations = [(-2.35, .91, -.04, -.01, .04),
                (-1.68, 1.0, .14, 0, -.12),
                (-.91, .78, -.08, -.10, -.08),
                (-.49, .48, -.29, -.15, -.04)]
rock("West broad outcrop", end_stations, slate)
rock("Central weathered outcrop", [(-.95, .48, -.26, .15, .04),
     (-.44, .83, .23, .06, .04), (.30, .89, .23, -.03, -.14),
     (.92, .42, -.20, -.10, -.05)], weathered)
rock("East broad outcrop", end_stations, slate, mirrored=True)
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityShoreEdges03_Mesh"
# Ground toe already fixes the full width and depth. Preserve the exact crest datum
# after bevel softening by scaling only the above-toe height of the rock geometry.
crest = max(vertex.co.z for vertex in obj.data.vertices)
for vertex in obj.data.vertices:
    if vertex.co.z > -.3:
        vertex.co.z = -.3 + (vertex.co.z + .3) * .95 / (crest + .3)
root = bpy.data.objects.new("CityShoreEdges03", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_shore_edges.03"
root["authorship"] = "Original Blender construction; commissioned production specialist"
root["datum"] = "Land contact Z=0; rock toe Z=-.6 and crest Z=.65; water-facing +Y"
root["interface"] = "4m straight; 1.6m wide; identical X=+/-2 cut sections; corner/end owner .04"
root["placement"] = "Shore obstacle, not a walking deck or terrain raise; no water-entry rule"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
