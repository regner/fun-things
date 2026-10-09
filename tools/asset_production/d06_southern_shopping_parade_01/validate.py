"""Audit saved source, raw GLB, standard fitting apertures and exact fresh re-export."""
import hashlib
import json
import math
from pathlib import Path
import runpy
import struct
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}/reexport")
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
GLB = ROOT / f"art/models/environment/{NID}/{NID}.glb"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
collection = bpy.data.collections[f"export_{NID}"]
objects = [obj for obj in collection.objects if obj.type == "MESH"]
assert len(objects) == 1
obj = objects[0]
mesh = obj.data
assert tuple(obj.location) == (0,0,0) and tuple(obj.scale) == (1,1,1)
assert tuple(obj.rotation_euler) == (0,0,0) and not obj.modifiers
assert bpy.context.scene.unit_settings.scale_length == 1
assert all(math.isfinite(value) for vertex in mesh.vertices for value in vertex.co)
assert all(abs(normal.vector.length - 1) < .0001 for normal in mesh.corner_normals)
bm = bmesh.new()
bm.from_mesh(mesh)
nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
degenerate = sum(face.calc_area() < 1e-10 for face in bm.faces)
assert nonmanifold == 0, nonmanifold
assert degenerate == 0, degenerate
bm.free()
mesh.calc_loop_triangles()
coords = [vertex.co for vertex in mesh.vertices]
lo = [min(v[i] for v in coords) for i in range(3)]
hi = [max(v[i] for v in coords) for i in range(3)]
expected_lo, expected_hi = [-9.045,-30.035,0], [9.04,30.035,5.4]
assert all(abs(a-b) < .001 for a,b in zip(lo+hi, expected_lo+expected_hi)), (lo,hi)
assert tuple(bpy.data.objects["D06SouthernShoppingParade01"].location) == (0,0,0)
# Probe actual holes all the way through the shared 0.54 m insertion envelope.
# Recess backing is deliberately at 0.60 m, not a traversable interior.
probes = 0
for number, centre in enumerate((25,15,5,-5,-15,-25), 1):
    station = bpy.data.objects[f"west_bay_{number:02}"]
    assert (station.location - Vector((-9,centre,0))).length < 1e-6
    assert (station.matrix_world.to_3x3() @ Vector((0,1,0)) - Vector((-1,0,0))).length < 1e-6
    for u0,u1,z0,z1 in [(-2.47,.57,.54,2.42),(1.24,2.66,0,2.45)]:
        for i in range(1,10):
            for j in range(1,10):
                point = Vector((-9.001,centre+u0+(u1-u0)*i/10,z0+(z1-z0)*j/10))
                hit, *_ = obj.ray_cast(point, Vector((1,0,0)), distance=.541)
                assert not hit, (number, point)
                probes += 1
    for u,z in [(-2.6,1),(.8,1),(2.9,1),(0,4.7)]:
        hit, point, *_ = obj.ray_cast(Vector((-10,centre+u,z)),Vector((1,0,0)),distance=1.01)
        assert hit and abs(point.x + 9) < .001
    for name, position in {"entrance_single": (1.95,0,0), "door_single": (1.95,0,0),
                           "display_window": (-.95,0,.48), "canopy": (-.95,0,3),
                           "fascia": (-.95,0,3.8)}.items():
        marker = bpy.data.objects[f"west_bay_{number:02}_mount_{name}"]
        assert (marker.location - Vector(position)).length < 1e-6
raw = GLB.read_bytes()
magic, version, length = struct.unpack_from('<4sII', raw)
assert magic == b'glTF' and version == 2 and length == len(raw)
json_length = struct.unpack_from('<I',raw,12)[0]
doc = json.loads(raw[20:20+json_length])
binary = raw[28+json_length:]
assert not any(doc.get(key) for key in ('images','textures','animations','skins','cameras'))
assert len(doc['meshes']) == 1 and len(doc['materials']) == 5
assert {node['name'] for node in doc['nodes']} == {item.name for item in collection.objects}
assert all(not material.get('doubleSided', False) for material in doc['materials'])
assert all(material.get('alphaMode', 'OPAQUE') == 'OPAQUE' for material in doc['materials'])
assert len(doc['nodes']) == 75, len(doc['nodes'])


def accessor(index):
    """Read actual buffer values rather than trusting accessor metadata."""
    item = doc['accessors'][index]
    view = doc['bufferViews'][item['bufferView']]
    count = {'SCALAR': 1, 'VEC3': 3}[item['type']]
    fmt = '<' + {5123:'H',5125:'I',5126:'f'}[item['componentType']] * count
    offset = view.get('byteOffset',0) + item.get('byteOffset',0)
    stride = view.get('byteStride',struct.calcsize(fmt))
    return [struct.unpack_from(fmt,binary,offset+i*stride) for i in range(item['count'])]


positions = []
triangles = 0
export_vertices = 0
for primitive in doc['meshes'][0]['primitives']:
    points = [Vector(v) for v in accessor(primitive['attributes']['POSITION'])]
    normals = [Vector(v) for v in accessor(primitive['attributes']['NORMAL'])]
    indices = [v[0] for v in accessor(primitive['indices'])]
    assert len(indices) % 3 == 0
    assert all(abs(normal.length-1) < .0001 for normal in normals)
    for i in range(0,len(indices),3):
        a,b,c = (points[k] for k in indices[i:i+3])
        cross = (b-a).cross(c-a)
        assert cross.length > 1e-10
        assert cross.dot(sum((normals[k] for k in indices[i:i+3]), Vector())) > 0
    positions.extend(points)
    triangles += len(indices)//3
    export_vertices += len(points)
gmin = [min(v[i] for v in positions) for i in range(3)]
gmax = [max(v[i] for v in positions) for i in range(3)]
assert all(abs(a-b) < .00001 for a,b in zip(gmin+gmax,
    [lo[0],lo[2],-hi[1],hi[0],hi[2],-lo[1]]))
assert triangles == len(mesh.loop_triangles)
# Saved source reopens in this fresh Blender process; export must match committed bytes.
sys.argv = [sys.argv[0], '--', str(SCRATCH)]
runpy.run_path(str(Path(__file__).with_name('export.py')),run_name='__main__')
assert (SCRATCH / GLB.name).read_bytes() == raw
report = {
    'asset_id': 'd06_southern_shopping_parade.01',
    'blender': bpy.app.version_string, 'build_hash': bpy.app.build_hash.decode(),
    'source_vertices': len(mesh.vertices), 'export_vertices': export_vertices,
    'triangles': triangles, 'mesh_count': 1, 'surface_count': 5,
    'nonmanifold_edges': nonmanifold, 'degenerate_faces': degenerate,
    'unit_source_and_export_normals': True, 'positive_triangle_normal_alignment': True,
    'source_bounds': {'min': lo,'max':hi}, 'godot_bounds': {'min':gmin,'max':gmax},
    'structural_footprint_m': [18,60], 'height_m':5.4, 'ground_pivot':[0,0,0],
    'aperture_insertion_ray_probes': probes, 'west_bay_count':6,
    'mount_interface': '6.4m stations, 10m pitch; city_small_shop_shells_01 literal offsets',
    'rear_interface': 'Same 6.4m mount frames, solid quiet wall; no rear fitting insertion openings',
    'export_nodes': len(doc['nodes']), 'materials':doc['materials'],
    'reexport_byte_identical': True, 'glb_bytes':len(raw),
    'glb_sha256': hashlib.sha256(raw).hexdigest(),
    'status': 'PASS source/raw GLB/reexport; engine and downstream gates recorded separately'
}
(EVIDENCE / 'validation.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
print(json.dumps(report,indent=2))
