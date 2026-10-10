"""Author the approved minimal flush ground-artwork carrier, not a road/slab kit."""
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_paving_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
TEXTURE = ROOT / f"art/textures/environment/{NID}/quay_border_albedo.png"


def main():
    """Save an original 8 x 1.2 m upward quad 15 mm above an external ground datum."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new("export_" + NID)
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("D05QuayPaving01", None)
    collection.objects.link(root)
    root["asset_id"] = "d05_quay_paving.01"
    root["authorship"] = "Original Blender quad and Python/Pillow harbour-line artwork"
    root["ground_contract"] = "External continuous collision at Y=0; visual-only +0.015 m"
    root["provisional_dimensions_m"] = "8 x 1.2; repeat on local X only"
    mesh = bpy.data.meshes.new("D05QuayPaving01_Geometry")
    mesh.from_pydata([(-4, -.6, .015), (4, -.6, .015),
                      (4, .6, .015), (-4, .6, .015)], [], [(0, 1, 2, 3)])
    mesh.update()
    obj = bpy.data.objects.new("D05QuayPaving01_Mesh", mesh)
    collection.objects.link(obj)
    obj.parent = root
    uv = mesh.uv_layers.new(name="UVMap")
    for loop in mesh.loops:
        point = mesh.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = ((point.x + 4) / 8, (point.y + .6) / 1.2)
    material = bpy.data.materials.new("quay_border")
    material.use_nodes = True
    material.use_backface_culling = True
    principled = material.node_tree.nodes["Principled BSDF"]
    principled.inputs["Base Color"].default_value = (.381326, .386429, .341914, 1)
    principled.inputs["Roughness"].default_value = .94
    image = material.node_tree.nodes.new("ShaderNodeTexImage")
    image.name = "CommittedAlbedo"
    image.image = bpy.data.images.load(str(TEXTURE))
    image.image.colorspace_settings.name = "sRGB"
    image.extension = "EXTEND"
    material.node_tree.links.new(image.outputs["Color"], principled.inputs["Base Color"])
    mesh.materials.append(material)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    sys.path.insert(0, str(Path(__file__).parent))
    from export import export_border
    export_border(ROOT / f"art/models/environment/{NID}")


if __name__ == "__main__":
    main()
