"""Export a saved owned Blender collection; never reconstruct source geometry."""
import json
from pathlib import Path
import sys
import bpy

ROOT=Path(__file__).resolve().parents[4]


def main():
    """Validate source ownership and export only the requested declared collection."""
    assert bpy.app.version_string=='5.2.2 LTS',bpy.app.version_string
    source=Path(bpy.data.filepath).resolve()
    allowed=[ROOT/'art/source/models/characters/shared_humanoid',ROOT/'art/source/models/characters/coral_courier']
    assert any(source.is_relative_to(p) for p in allowed),source
    args=sys.argv[sys.argv.index('--')+1:]
    collection,output=args[:2]
    assert collection in bpy.data.collections,collection
    for obj in bpy.data.collections[collection].all_objects:
        assert all(abs(s-1)<1e-6 for s in obj.scale),(obj.name,list(obj.scale))
        assert obj.matrix_world.determinant()>0,obj.name
    settings=json.loads((ROOT/'tools/assets/blender/export_settings.json').read_text())
    settings.update(collection=collection,filepath=str(Path(output).resolve()),
                    export_animations='--animations' in args)
    bpy.ops.export_scene.gltf(**settings)
    print('REEXPORTED',source.name,collection,output)


if __name__=='__main__':
    main()
