"""Export all declared outputs from the saved Dock Thumper Blender source."""
import json
import sys
from pathlib import Path
import bpy

SOURCE = Path(__file__).resolve().parent
manifest = json.loads((SOURCE / "source_manifest.json").read_text())
assert bpy.app.version_string == manifest["blender"]
assert Path(bpy.data.filepath).name == manifest["source"]
output = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
output.mkdir(parents=True, exist_ok=True)
for name, members in manifest["collections"].items():
    col = bpy.data.collections[name]
    assert sorted(obj.name for obj in col.all_objects) == sorted(row["name"] for row in members)
    for obj in col.all_objects:
        assert all(abs(v-1) < 1e-6 for v in obj.scale)
        assert obj.matrix_world.determinant() > 0
    bpy.ops.export_scene.gltf(**manifest["settings"], collection=name,
        filepath=str(output / (name.removeprefix("export_") + ".glb")))
