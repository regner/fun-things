"""Original flush entry-axis artwork carrier; no slab, ground collider or procedural road."""
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_forecourt_graphics_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
TEXTURE = ROOT / f"art/textures/environment/{NID}/entry_axis_motif_albedo.png"
DECAL_LIFT_M = .015
WIDTH_M, DEPTH_M = 8.0, 16.0


def main():
    """Save a named, identity-transform metre-space quad and export only that collection."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new("export_" + NID)
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("D04ForecourtGraphics02", None)
    collection.objects.link(root)
    root["asset_id"] = "d04_forecourt_graphics.02"
    root["authorship"] = "Original commissioned Blender quad and Python/Pillow artwork"
    root["surface_contract"] = "Visual-only at +15 mm; external flat ground owns collision"
    root["provisional_dimensions"] = "8 x 16 m entry-axis artwork"
    data = bpy.data.meshes.new("D04ForecourtGraphics02_Geometry")
    data.from_pydata([(-4, -8, DECAL_LIFT_M), (4, -8, DECAL_LIFT_M),
                     (4, 8, DECAL_LIFT_M), (-4, 8, DECAL_LIFT_M)], [], [(0, 1, 2, 3)])
    data.update()
    mesh = bpy.data.objects.new("D04ForecourtGraphics02_Mesh", data)
    collection.objects.link(mesh)
    mesh.parent = root
    uv = data.uv_layers.new(name="UVMap")
    for loop in data.loops:
        point = data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = ((point.x + 4) / WIDTH_M, (point.y + 8) / DEPTH_M)
    material = bpy.data.materials.new("entry_axis_motif")
    material.use_nodes = True
    material.use_backface_culling = True
    shader = material.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (.55, .60, .59, 1)
    shader.inputs["Roughness"].default_value = .94
    image = material.node_tree.nodes.new("ShaderNodeTexImage")
    image.name = "CommittedAlbedo"
    image.image = bpy.data.images.load(str(TEXTURE))
    image.image.colorspace_settings.name = "sRGB"
    image.extension = "EXTEND"
    material.node_tree.links.new(image.outputs["Color"], shader.inputs["Base Color"])
    data.materials.append(material)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    sys.path.insert(0, str(Path(__file__).parent))
    from export import export_motif
    export_motif(ROOT / f"art/models/environment/{NID}")


if __name__ == "__main__":
    main()
