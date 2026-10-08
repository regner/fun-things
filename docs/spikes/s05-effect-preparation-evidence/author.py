"""One-time original Blender authoring; the saved .blend owns future edits."""
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'art/source/models/spikes/s05_explosion_carrier.blend'
assert not SOURCE.exists(), 'Never overwrite an authored source'
assert bpy.app.version_string == '5.2.2 LTS'
assert bpy.app.build_hash == b'd13f752e3b9c'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.render.fps = 30
collection = bpy.data.collections.new('export_s05_explosion_carrier')
scene.collection.children.link(collection)


def material(name, rgb):
    """Author a stable opaque, non-emissive flat color in linear space."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    color = tuple(v / 3294.6 if v <= 10 else ((v / 255 + .055) / 1.055) ** 2.4
                  for v in rgb)
    node = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Roughness'].default_value = .8
    mat.diffuse_color = (*color, 1)
    return mat


vertices, faces, slots = [], [], []


def lobe(center, radius, angle, slot, cap=False):
    """Author a closed tapered burst surface with broad smooth radial rings."""
    start = len(vertices)
    segments, rings = 16, 8
    # Taper/lean follows the blast direction; this is original Blender geometry.
    vertices.append((center[0], center[1], center[2] - radius[2]))
    for ring in range(1, rings):
        phi = math.pi * ring / rings
        height = -math.cos(phi)
        width = math.sin(phi) * (1 - .18 * height)
        lean = .12 * radius[0] * (height + 1)
        for segment in range(segments):
            theta = 2 * math.pi * segment / segments
            radial = radius[0] * width * math.cos(theta) + lean
            tangent = radius[1] * width * math.sin(theta)
            vertices.append((center[0] + radial * math.cos(angle) - tangent * math.sin(angle),
                             center[1] + radial * math.sin(angle) + tangent * math.cos(angle),
                             center[2] + radius[2] * height))
    top = len(vertices)
    vertices.append((center[0] + .24 * radius[0] * math.cos(angle),
                     center[1] + .24 * radius[0] * math.sin(angle),
                     center[2] + radius[2]))
    for segment in range(segments):
        nxt = (segment + 1) % segments
        faces.append((start, start + 1 + nxt, start + 1 + segment))
        slots.append(slot)
    for ring in range(rings - 2):
        lower = start + 1 + ring * segments
        upper = lower + segments
        for segment in range(segments):
            nxt = (segment + 1) % segments
            faces.extend(((lower + segment, lower + nxt, upper + nxt),
                          (lower + segment, upper + nxt, upper + segment)))
            slots.extend((2 if cap and ring >= 4 else slot,) * 2)
    last = top - segments
    for segment in range(segments):
        faces.append((last + segment, last + (segment + 1) % segments, top))
        slots.append(2 if cap else slot)


# A small flash and five detached outward coral lobes leave radial road-view gaps.
lobe((0, 0, .9), (.48, .48, .8), 0, 0, cap=True)
for index in range(5):
    angle = math.pi / 2 + index * 2 * math.pi / 5
    lobe((1.22 * math.cos(angle), 1.22 * math.sin(angle), .73),
         (.53, .42, .60), angle, 1)
mesh = bpy.data.meshes.new('s05_burst_authored')
mesh.from_pydata(vertices, [], faces)
mesh.update()
assert not mesh.validate(verbose=True), 'Invalid authored topology'
obj = bpy.data.objects.new('ExplosionCarrier', mesh)
collection.objects.link(obj)
for mat in (material('flash_amber', (255, 192, 90)),
            material('burst_coral', (255, 114, 93)),
            material('flash_ivory', (246, 241, 220))):
    mesh.materials.append(mat)
for face, slot in zip(mesh.polygons, slots, strict=True):
    face.material_index = slot
    face.use_smooth = True
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
print('S05_SOURCE_SAVED', SOURCE, bpy.app.version_string, bpy.app.build_hash)
