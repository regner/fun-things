"""Build the original closed Blender swatch, not a world-placement paving module."""
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "city_ground_finishes_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
TEXTURE = ROOT / f"art/textures/environment/{NID}/plain_plaza_paving_albedo.png"


def main():
    """Create a 4 m square surface-datum swatch with explicit repeatable UV0."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    collection = bpy.data.collections.new("export_" + NID)
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("CityGroundFinishes01", None)
    collection.objects.link(root)
    root["asset_id"] = "city_ground_finishes.01"
    root["authorship"] = "Original commissioned Blender construction and deterministic texture"
    root["surface_contract"] = "Y=0 Godot surface; UV0 unit = 4 metres; sample only"
    # Closed thickness exists only for the portable review swatch. Actual site geometry is external.
    bpy.ops.mesh.primitive_cube_add(size=1)
    mesh = bpy.context.object
    mesh.name = "CityGroundFinishes01_Mesh"
    mesh.data.name = "PlainPlazaSwatch"
    for owner in list(mesh.users_collection):
        owner.objects.unlink(mesh)
    collection.objects.link(mesh)
    mesh.dimensions = (4.0, 4.0, 0.08)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for vertex in mesh.data.vertices:
        vertex.co.z -= 0.04
    mesh.parent = root
    uv = mesh.data.uv_layers.active
    uv.name = "UVMap"
    for polygon in mesh.data.polygons:
        for loop_index in polygon.loop_indices:
            vertex = mesh.data.vertices[mesh.data.loops[loop_index].vertex_index].co
            if abs(polygon.normal.z) > 0.5:
                uv.data[loop_index].uv = ((vertex.x + 2) / 4, (vertex.y + 2) / 4)
            elif abs(polygon.normal.x) > 0.5:
                uv.data[loop_index].uv = ((vertex.y + 2) / 4, vertex.z / 4)
            else:
                uv.data[loop_index].uv = ((vertex.x + 2) / 4, vertex.z / 4)
    material = bpy.data.materials.new("plain_plaza_paving")
    material.use_nodes = True
    material.use_backface_culling = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.23455, 0.28744, 0.33716, 1)
    principled.inputs["Roughness"].default_value = 0.88
    image_node = material.node_tree.nodes.new("ShaderNodeTexImage")
    image_node.name = "CommittedAlbedo"
    image_node.image = bpy.data.images.load(str(TEXTURE))
    image_node.image.colorspace_settings.name = "sRGB"
    image_node.extension = "REPEAT"
    material.node_tree.links.new(image_node.outputs["Color"], principled.inputs["Base Color"])
    mesh.data.materials.append(material)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    sys.path.insert(0, str(Path(__file__).parent))
    from export import export_swatch
    export_swatch(ROOT / f"art/models/environment/{NID}")


if __name__ == "__main__":
    main()
