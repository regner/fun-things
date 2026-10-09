"""Author the original shallow north-end relief; isolated pinned Blender only."""
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
root = bpy.data.objects.new("D06SouthernShoppingParade03", None)
collection.objects.link(root)
root["asset_id"] = "d06_southern_shopping_parade.03"
root["provenance"] = "Original Blender construction; no external geometry or textures"
root["datum"] = "North wall ground datum; Blender +Y outward maps to Godot -Z"
parts = []


def material(name, swatch, metal=0, rough=.7):
    """Match the parade's sRGB palette with opaque linear Principled materials."""
    rgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*linear, 1)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*linear, 1)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
    return mat


plum = material("parade_muted_plum_render", "81777C")
field = material("north_deep_plum_relief", "70616F")
slate = material("parade_quiet_blue_roof", "405B68", .12, .65)
cyan = material("north_cyan_inlay", "60ADBA", .15, .5)
magenta = material("north_magenta_inlay", "B5628F", .15, .5)


def box(name, lo, hi, mat, bevel=.018):
    """Construct a closed editable relief part with baked smooth edge treatment."""
    a, b, c = lo
    d, e, f = hi
    data = bpy.data.meshes.new(name)
    data.from_pydata([(a,b,c),(d,b,c),(d,e,c),(a,e,c),
                     (a,b,f),(d,b,f),(d,e,f),(a,e,f)], [],
                    [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if bevel:
        modifier = obj.modifiers.new("Soft architectural edges", "BEVEL")
        modifier.width, modifier.segments = bevel, 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    for polygon in data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Broad plane normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)


# Shallow plinth masks the existing 35 mm projecting base without cutting its mesh.
# All other backing meets the solid north wall; nothing extends behind its plane.
box("Continuous_slate_toe", (-8.7,.035,0), (8.7,.18,.30), slate, .018)
box("Quiet_upper_brow", (-8.7,0,4.48), (8.7,.18,4.8), slate, .025)
for x in (-8.7, 8.26):
    box("Plum_edge_pier", (x,0,.32), (x+.44,.16,4.46), plum, .025)
box("Lower_plum_course", (-8.24,0,.32), (8.24,.14,.58), plum)
# One broad centre field, not a bank of windows or a blank duplicate fascia carrier.
box("Broad_plum_end_field", (-5.55,0,.62), (4.75,.065,4.44), field)
box("West_relief_backing", (-8.24,0,.62), (-5.60,.065,4.44), field)
box("East_relief_backing", (4.80,0,.62), (8.24,.065,4.44), field)
# Asymmetric rhythm: three full-height west blades and two shortened east blades.
# Colour occupies narrow inlays only. No lettering, real brand, emission or sign face.
for index, x in enumerate((-7.94,-7.22,-6.50)):
    box(f"West_plum_blade_{index}", (x,.065,.76), (x+.42,.16,4.30), plum)
    if index != 1:
        # Inlay rests on the blade front while staying inside the 180 mm envelope.
        box(f"West_cyan_inlay_{index}", (x+.12,.16,1.18), (x+.30,.18,3.90), cyan, .006)
for index, x in enumerate((5.35,6.75)):
    box(f"East_plum_blade_{index}", (x,.065,1.15), (x+.80,.16,3.82), plum)
    box(f"East_magenta_inlay_{index}", (x+.26,.16,1.52), (x+.54,.18,3.45), magenta, .006)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D06SouthernShoppingParade03_Mesh"
scene.cursor.location = (0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
model.parent = root
# Studio setup is editable but excluded from the explicitly filtered export.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24,.28,.34,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .7
bpy.ops.mesh.primitive_plane_add(size=250, location=(0,0,-.025))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_ground", "687780"))
bpy.ops.mesh.primitive_cube_add(size=1, location=(12,0,.5))
bpy.context.object.name = "STUDIO_one_metre_reference"
bpy.context.object.hide_render = True
for name, location, power, size in [("key",(-15,20,30),24000,25),
                                    ("fill",(20,8,20),16000,20)]:
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.size = power, size
    lamp = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(lamp)
    lamp.location = location
    lamp.rotation_euler = (Vector((0,0,2))-lamp.location).to_track_quat('-Z','Y').to_euler()
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(camera)
scene.camera = camera
camera.location = (-16,25,14)
camera.rotation_euler = (Vector((0,0,2.4))-camera.location).to_track_quat('-Z','Y').to_euler()
data.type, data.ortho_scale = "ORTHO", 22
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
