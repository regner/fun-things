"""Author the S15 particle draw meshes and rocket carrier with Blender 5.2."""
import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "art/source/models/effects/s15_vfx.blend"
OUTPUT_DIR = ROOT / "art/models/effects"
ASSET_NAMES = [
    "fireball",
    "smoke",
    "spark",
    "debris",
    "muzzle_flash",
    "tracer",
    "impact",
    "rocket_trail",
    "rocket",
]


def move_to_collection(item, collection):
    """Move one authored object out of defaults and into its explicit export collection."""
    for old_collection in list(item.users_collection):
        old_collection.objects.unlink(item)
    collection.objects.link(item)


def material(name, color, emission_strength=0.0):
    """Create one simple named material; Godot overrides particle colors after import."""
    created = bpy.data.materials.new(name)
    created.use_nodes = True
    node = next(node for node in created.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    node.inputs["Base Color"].default_value = color
    node.inputs["Roughness"].default_value = 0.8
    if emission_strength > 0.0:
        node.inputs["Emission Color"].default_value = color
        node.inputs["Emission Strength"].default_value = emission_strength
    created.diffuse_color = color
    return created


def finish_object(item, collection, shape_material):
    """Apply transforms, triangulate, name, and link one exported Shape mesh."""
    item.name = "Shape"
    if not item.users_collection:
        bpy.context.scene.collection.objects.link(item)
    bpy.context.view_layer.objects.active = item
    item.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    modifier = item.modifiers.new("explicit_triangles", "TRIANGULATE")
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    item.data.materials.append(shape_material)
    move_to_collection(item, collection)
    return item


def ico_shape(collection, radius, shape_material):
    """Create a faceted spherical particle mesh at the emission pivot."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius)
    return finish_object(bpy.context.object, collection, shape_material)


def box_shape(collection, dimensions, shape_material):
    """Create a low-cost rectangular particle mesh at the emission pivot."""
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    item = bpy.context.object
    item.scale = dimensions
    return finish_object(item, collection, shape_material)


def card_shape(collection, width, height, shape_material):
    """Create a vertical XY-in-Godot card using Blender's XZ plane."""
    mesh = bpy.data.meshes.new("ShapeMesh")
    mesh.from_pydata(
        [
            (-width * 0.5, 0.0, -height * 0.5),
            (width * 0.5, 0.0, -height * 0.5),
            (width * 0.5, 0.0, height * 0.5),
            (-width * 0.5, 0.0, height * 0.5),
        ],
        [],
        [(0, 1, 2, 3)],
    )
    mesh.update()
    return finish_object(bpy.data.objects.new("Shape", mesh), collection, shape_material)


def rocket_shape(collection, shape_material):
    """Create and join a chunky octagonal rocket body and nose along local X."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.15,
        depth=0.65,
        location=(-0.1, 0.0, 0.0),
        rotation=(0.0, math.pi * 0.5, 0.0),
    )
    body = bpy.context.object
    bpy.ops.mesh.primitive_cone_add(
        vertices=8,
        radius1=0.18,
        radius2=0.0,
        depth=0.3,
        location=(0.375, 0.0, 0.0),
        rotation=(0.0, math.pi * 0.5, 0.0),
    )
    nose = bpy.context.object
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    nose.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    return finish_object(body, collection, shape_material)


def export_collection(name):
    """Export one declared collection with the repository's explicit glTF settings."""
    settings = json.loads((ROOT / "tools/s01/export_settings.json").read_text())
    settings["collection"] = f"export_s15_{name}"
    settings["export_animations"] = False
    settings["filepath"] = str(OUTPUT_DIR / f"s15_{name}.glb")
    bpy.ops.export_scene.gltf(**settings)


def main():
    """Build the shared source, save it, and export all nine declared mesh carriers."""
    if bpy.app.version_string != "5.2.2 LTS":
        raise RuntimeError(f"expected Blender 5.2.2 LTS, got {bpy.app.version_string}")
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    neutral = material("particle_shape", (0.8, 0.8, 0.8, 1.0))
    rocket_material = material("rocket_body", (1.0, 0.25, 0.04, 1.0), 1.5)
    collections = {}
    for name in ASSET_NAMES:
        collection = bpy.data.collections.new(f"export_s15_{name}")
        scene.collection.children.link(collection)
        collections[name] = collection

    ico_shape(collections["fireball"], 0.9, neutral)
    ico_shape(collections["smoke"], 1.1, neutral)
    box_shape(collections["spark"], (0.07, 0.07, 0.38), neutral)
    box_shape(collections["debris"], (0.18, 0.12, 0.22), neutral)
    card_shape(collections["muzzle_flash"], 0.9, 0.9, neutral)
    card_shape(collections["tracer"], 0.12, 1.8, neutral)
    card_shape(collections["impact"], 0.65, 0.65, neutral)
    ico_shape(collections["rocket_trail"], 0.28, neutral)
    rocket_shape(collections["rocket"], rocket_material)

    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    for name in ASSET_NAMES:
        export_collection(name)
    print("S15_VFX_AUTHORED", SOURCE, len(ASSET_NAMES), "exports", bpy.app.version_string)


if __name__ == "__main__":
    main()
