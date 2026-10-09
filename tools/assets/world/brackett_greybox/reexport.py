"""Run inside pinned Blender; export declared collections from saved .blend sources.

Usage: blender -b -t 2 --python tools/assets/world/brackett_greybox/reexport.py -- /tmp/exports
Explicitly pass art/models/brackett_greybox to install; existing .import UIDs stay intact.
"""
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[4]


def main():
    """Load each committed source and export only its recorded collection membership."""
    assert bpy.app.version_string == '5.2.2 LTS'
    destination = Path(sys.argv[sys.argv.index('--')+1]).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    sources = ROOT/'art/source/models/brackett_greybox/source_manifest.json'
    settings = json.loads((ROOT/'tools/assets/blender/export_settings.json').read_text())
    settings['export_animations'] = False
    fingerprints = []
    for entry in json.loads(sources.read_text()):
        path = ROOT/entry['source']
        bpy.ops.wm.open_mainfile(filepath=str(path))
        assert bpy.context.scene.unit_settings.scale_length == 1
        for asset in entry['outputs']:
            name = 'export_'+asset
            objects = bpy.data.collections[name].all_objects
            assert sorted(o.name for o in objects) == entry['collections'][name]
            assert all(all(abs(s-1) < .00001 for s in o.scale) for o in objects)
            output = destination/(asset+'.glb')
            bpy.ops.export_scene.gltf(**settings, collection=name, filepath=str(output))
            fingerprints.append(dict(source=entry['source'], source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                     export=output.name, export_sha256=hashlib.sha256(output.read_bytes()).hexdigest()))
    (destination/'fingerprints.json').write_text(json.dumps(fingerprints, indent=2)+'\n')
    print('BRACKETT_EXPORTS', len(fingerprints))


if __name__ == '__main__':
    main()
