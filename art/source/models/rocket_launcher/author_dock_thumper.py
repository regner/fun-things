"""Original Codex Blender authoring for Regner-approved Dock Thumper, 9 Oct 2026.

Historical bootstrap only: future edits belong in the committed .blend, followed
by reexport_dock_thumper.py. No external models/textures or functional weapon design.
Brief and exact concept prompt: docs/concepts/assets-v1/rocket-launcher/.
Run only in a worktree-private Blender background process, never a shared session.
"""
import json
import math
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
FAMILY = "rocket_launcher"
SOURCE = ROOT / "art/source/models" / FAMILY
OUTPUT = ROOT / "art/models" / FAMILY
assert bpy.app.version_string == "5.2.2 LTS"
assert (ROOT / "art/source/.gdignore").exists()
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0


def linear(value):
    return value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4


def material(name, color, roughness=.5, metallic=.0, emission=0):
    mat = bpy.data.materials.new("dock_thumper_" + name)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgba = tuple(linear(v) for v in color) + (1,)
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if emission:
        shader.inputs["Emission Color"].default_value = rgba
        shader.inputs["Emission Strength"].default_value = emission
    mat.diffuse_color = rgba
    return mat


MATS = {
    "petrol": material("petrol", (.12, .19, .25), .42, .15),
    "coral": material("coral", (.96, .36, .25), .5),
    "ivory": material("ivory", (.90, .87, .74), .52),
    "graphite": material("graphite", (.075, .095, .115), .58),
    "cyan": material("cyan", (.16, .82, .88), .38, emission=.35),
    "asphalt": material("asphalt", (.11, .15, .18), .85),
}


def collection(asset):
    col = bpy.data.collections.new("export_" + asset)
    scene.collection.children.link(col)
    return col


def finish(obj, col, name, mat, bevel=0, smooth=False):
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(MATS[mat])
    if bevel:
        mod = obj.modifiers.new("authored_soft_edges", "BEVEL")
        mod.width, mod.segments = bevel, 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if name == "IvoryCrown":
        for face in bm.faces:
            if face.normal.z < 0:
                face.normal_flip()
    bm.to_mesh(obj.data)
    bm.free()
    for poly in obj.data.polygons:
        poly.use_smooth = smooth
    mod = obj.modifiers.new("explicit_triangles", "TRIANGULATE")
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def box(col, name, size, pos, mat, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object
    obj.scale = size
    return finish(obj, col, name, mat, bevel)


def cylinder(col, name, radius, depth, pos, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth,
                                     location=pos, rotation=(math.pi / 2, 0, 0))
    return finish(bpy.context.object, col, name, mat, .006, True)


def mesh(col, name, verts, faces, mat, bevel=0, smooth=False):
    data = bpy.data.meshes.new(name + "_mesh")
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    return finish(obj, col, name, mat, bevel, smooth)


def ring(col, name, outer, inner, start, end, z, mat):
    verts = []
    for y, radius in [(start, outer), (end, outer), (start, inner), (end, inner)]:
        for i in range(32):
            angle = 2 * math.pi * i / 32
            verts.append((radius * math.cos(angle), y, z + radius * math.sin(angle)))
    faces = []
    for i in range(32):
        j = (i + 1) % 32
        faces += [(i, j, 32+j, 32+i), (64+j, 64+i, 96+i, 96+j),
                  (j, i, 64+i, 64+j), (32+i, 32+j, 96+j, 96+i)]
    return mesh(col, name, verts, faces, mat, .004, True)


def marker(col, name, pos, normal=None):
    obj = bpy.data.objects.new(name, None)
    col.objects.link(obj)
    obj.location = pos
    obj.empty_display_type = "ARROWS"
    obj.empty_display_size = .08
    if normal:
        obj["contact_normal_blender"] = list(normal)
    return obj


launcher = collection("dock_thumper_launcher_a")
cylinder(launcher, "TubeBody", .15, 1.14, (0, .14, .30), "petrol")
ring(launcher, "CoralMuzzleCollar", .20, .137, .72, .90, .30, "coral")
cylinder(launcher, "MuzzleRecess", .138, .013, (0, .735, .30), "graphite")
ring(launcher, "RearGraphiteCollar", .175, .13, -.53, -.42, .30, "graphite")
cylinder(launcher, "RearRecess", .131, .01, (0, -.46, .30), "graphite")
ring(launcher, "RearIvoryBand", .169, .147, -.40, -.365, .30, "ivory")
ring(launcher, "FrontGraphiteBand", .159, .147, .655, .703, .30, "graphite")

# The wide ivory strip wraps the tube crown, preserving A's overhead signature.
verts = []
for y in [-.31, .635]:
    for i in range(9):
        angle = math.pi / 2 + (i - 4) * math.pi / 24
        verts.append((.154 * math.cos(angle), y, .30 + .154 * math.sin(angle)))
mesh(launcher, "IvoryCrown", verts, [(i, i+1, i+10, i+9) for i in range(8)],
     "ivory", smooth=True)
box(launcher, "UpperRail", (.055, .68, .035), (0, .04, .469), "petrol", .008)
for y in [-.30, .55]:
    box(launcher, "SightBlock_" + str(y), (.10, .08, .045), (0, y, .48),
        "graphite", .009)
box(launcher, "CyanStatus", (.10, .06, .012), (0, .652, .459), "cyan", .004)
box(launcher, "DominantGrip", (.09, .10, .25), (0, 0, .05), "graphite", .015)
box(launcher, "GripCoralInset", (.094, .035, .17), (0, .035, .055), "coral", .007)
box(launcher, "SupportGrip", (.085, .10, .24), (0, .43, .045), "graphite", .014)
box(launcher, "SupportIvoryBase", (.09, .105, .035), (0, .43, -.065), "ivory", .007)
box(launcher, "ShoulderPad", (.235, .22, .065), (0, -.28, .1175), "graphite", .012)
box(launcher, "ShoulderCoralTrim", (.243, .235, .032), (0, -.28, .159), "coral", .01)
for side in [-1, 1]:
    box(launcher, "FrontVent_" + str(side), (.012, .085, .065),
        (side * .197, .81, .30), "graphite", .004)
    box(launcher, "RearSidePanel_" + str(side), (.017, .21, .09),
        (side * .15, -.26, .29), "petrol", .007)
marker(launcher, "socket_grip", (0, 0, 0))
marker(launcher, "socket_muzzle", (0, .905, .30))
# Contact planes use weapon frame, not guessed wrist/bone rotations.
marker(launcher, "socket_support_hand", (0, .43, -.0825), (0, 0, -1))
marker(launcher, "socket_shoulder", (0, -.28, .085), (0, 0, -1))

rocket = collection("dock_thumper_rocket_a")
cylinder(rocket, "RocketBody", .056, .30, (0, -.055, 0), "petrol")
ring(rocket, "RocketIvoryBand", .059, .052, .084, .105, 0, "ivory")
# Rounded stylized nose, not a functional internal design.
verts = []
profile = [(0.10, .057), (.135, .055), (.17, .044), (.20, .026), (.225, .006)]
for y, radius in profile:
    for i in range(24):
        a = 2 * math.pi * i / 24
        verts.append((radius * math.cos(a), y, radius * math.sin(a)))
faces = [(j*24+i, j*24+(i+1)%24, (j+1)*24+(i+1)%24, (j+1)*24+i)
         for j in range(4) for i in range(24)]
faces.append(tuple(range(96, 120)))
mesh(rocket, "RoundedCoralNose", verts, faces, "coral", smooth=True)
ring(rocket, "ExhaustRim", .06, .033, -.225, -.195, 0, "graphite")
cylinder(rocket, "ExhaustRecess", .034, .009, (0, -.199, 0), "graphite")
for i in range(3):
    # Three broad ivory fins preserve the matching concept's simple silhouette.
    a = 2 * math.pi * i / 3
    radial = Vector((math.cos(a), 0, math.sin(a)))
    tangent = Vector((-math.sin(a), 0, math.cos(a)))
    points = [(r, y) for r, y in [(.045, -.08), (.12, -.145), (.12, -.212), (.045, -.20)]]
    verts = [tuple(radial*r + Vector((0, y, 0)) + tangent*t)
             for t in [-.006, .006] for r, y in points]
    mesh(rocket, "IvoryFin_" + str(i), verts,
         [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
          (2, 3, 7, 6), (3, 0, 4, 7)], "ivory", .003)
marker(rocket, "socket_trail", (0, -.23, 0))

stage = collection("dock_thumper_preview_stage")
box(stage, "AsphaltStage", (64, 48, .10), (0, 0, -.06), "asphalt", .005)
box(stage, "MetreReference", (1, .04, .012), (-2.0, 0, .002), "ivory", .002)
for x in [-2.5, -1.5]:
    box(stage, "MetreTick_" + str(x), (.04, .20, .012), (x, 0, .002), "coral", .002)

settings = json.loads((ROOT / "tools/s01/export_settings.json").read_text())
settings.update(export_animations=False, export_skins=False)
record = {"creator": "Codex rocket-launcher lead", "concept": "Regner approved A Dock Thumper",
          "blender": bpy.app.version_string, "build": bpy.app.build_hash.decode(),
          "source": "dock_thumper_a.blend", "collections": {}, "settings": settings}
for col in [launcher, rocket, stage]:
    members = []
    for obj in col.objects:
        assert all(abs(v-1) < 1e-6 for v in obj.scale), obj.name
        row = {"name": obj.name, "type": obj.type, "location_blender": list(obj.location)}
        if obj.type == "MESH":
            bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            mapped = [(v.x, v.z, -v.y) for v in bounds]
            row["aabb_godot_min"] = [min(v[i] for v in mapped) for i in range(3)]
            row["aabb_godot_max"] = [max(v[i] for v in mapped) for i in range(3)]
            row["triangles"] = len(obj.data.polygons)
            row["material"] = obj.data.materials[0].name
        else:
            row["position_godot"] = [obj.location.x, obj.location.z, -obj.location.y]
            row["basis_godot"] = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            if "contact_normal_blender" in obj:
                n = obj["contact_normal_blender"]
                row["contact_normal_godot"] = [n[0], n[2], -n[1]]
        members.append(row)
    record["collections"][col.name] = members
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / "dock_thumper_a.blend"))
for col in [launcher, rocket, stage]:
    target = OUTPUT / (col.name.removeprefix("export_") + ".glb")
    bpy.ops.export_scene.gltf(**settings, collection=col.name, filepath=str(target))
(SOURCE / "source_manifest.json").write_text(json.dumps(record, indent=2) + "\n")
print("DOCK_THUMPER_AUTHORED", bpy.data.filepath)
