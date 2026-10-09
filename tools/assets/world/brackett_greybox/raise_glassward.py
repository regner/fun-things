"""One-time owner-requested height revision; run in private Blender 5.2.2.

Regner: "The buildings in the high rise area should be taller." 9 October 2026.
Authored by Codex, verified effective gpt-6-astra/high before spatial work.
Preserves all footprints, materials, bevel widths, object names and placements.
"""
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT/'art/source/models/brackett_greybox'
HEIGHTS = {'office': (22, 42), 'tower_mid': (30, 68), 'tower_high': (38, 90)}


def main():
    """Extend vertical walls between existing bevels, retaining ground/podium datums."""
    assert bpy.app.version_string == '5.2.2 LTS'
    source = SOURCE/'district_04_kit.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert Path(bpy.data.filepath).resolve() == source
    assert bpy.context.scene.unit_settings.scale_length == 1
    for asset, (old, new) in HEIGHTS.items():
        tower = asset.startswith('tower')
        obj = bpy.data.objects[asset+('_shaft' if tower else '_mass')]
        bottom = 6 if tower else 0
        assert all(abs(s-1) < .00001 for s in obj.scale)
        assert abs(obj.dimensions.z-(old-bottom)) < .001
        # Both bevel rings translate intact: bottom vertices remain at the old
        # world height; top vertices rise. No stretch of the 0.12 m bevel detail.
        delta = new-old
        for vertex in obj.data.vertices:
            vertex.co.z += delta/2 if vertex.co.z > 0 else -delta/2
        obj.location.z += delta/2
        obj.data.update()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(source), compress=True)
    for path in [SOURCE/'authoring_plan.json', ROOT/'tools/assets/world/brackett_greybox/editor_input.json']:
        data = json.loads(path.read_text())
        for asset in data['kit']:
            if asset['asset_id'] not in HEIGHTS:
                continue
            old, height = HEIGHTS[asset['asset_id']]
            assert asset['height'] == old
            asset['height'] = height
            if 'collision_boxes' in asset:
                w, d = asset['width'], asset['depth']
                asset['collision_boxes'] = (
                    [[w, 6, d, 0, 3, 0], [w*.61, height-6, d*.61, 0, (height+6)/2, 0]]
                    if asset['asset_id'].startswith('tower') else [[w, height, d, 0, height/2, 0]])
        formatting = {'separators': (',', ':')} if path.name == 'authoring_plan.json' else {'indent': 2}
        path.write_text(json.dumps(data, **formatting)+'\n')
    print('GLASSWARD_HEIGHTS', HEIGHTS)


if __name__ == '__main__':
    main()
