"""Read-only top view of the authored Blender source; no runtime visual acceptance."""
import json
import sys
from pathlib import Path
import bpy

output = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
assert bpy.app.version_string == '5.2.2 LTS'
assert len([o for o in bpy.context.scene.objects if o.type == 'MESH']) == 34
scene = bpy.context.scene
camera = bpy.data.objects.new('S06EvidenceCamera', bpy.data.cameras.new('S06EvidenceCamera'))
scene.collection.objects.link(camera)
camera.location = (0, 0, 60)
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 52
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 8
scene.world = bpy.data.worlds.new('S06EvidenceWorld')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (1, 1, 1, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .8
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.render.filepath = str(output)
bpy.ops.render.render(write_still=True)
print('S06_STATIC_CAPTURE', json.dumps({'source': bpy.data.filepath, 'image': str(output),
      'scope': 'Blender source top view only; no engine/runtime/input-feel evidence'}))
