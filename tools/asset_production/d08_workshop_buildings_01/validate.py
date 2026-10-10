"""Measure saved source, raw export buffers, literal design bounds and fresh re-export."""
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
NID = "d08_workshop_buildings_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}/reexport")
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
GLB = ROOT / f"art/models/environment/{NID}/{NID}.glb"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
collection = bpy.data.collections[f"export_{NID}"]
assert {obj.name for obj in collection.objects} == {"D08WorkshopBuildings01", "D08WorkshopBuildings01_Mesh"}
obj = bpy.data.objects["D08WorkshopBuildings01_Mesh"]
mesh = obj.data
for member in collection.objects:
    assert tuple(member.location) == (0,0,0) and tuple(member.scale) == (1,1,1)
    assert tuple(member.rotation_euler) == (0,0,0) and not member.modifiers
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
assert all(math.isfinite(value) for vertex in mesh.vertices for value in vertex.co)
assert all(abs(normal.vector.length - 1) < .0001 for normal in mesh.corner_normals)
bm = bmesh.new()
bm.from_mesh(mesh)
nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
degenerate = sum(face.calc_area() <= 1e-10 for face in bm.faces)
assert nonmanifold == 0, nonmanifold
assert degenerate == 0, degenerate
bm.free()
mesh.calc_loop_triangles()
coords = [vertex.co for vertex in mesh.vertices]
lo = [min(v[i] for v in coords) for i in range(3)]
hi = [max(v[i] for v in coords) for i in range(3)]
assert all(abs(a-b) < .001 for a,b in zip(lo+hi, [-5.35,-6.35,0,5.35,6.35,5.88])), (lo,hi)
# Exterior face rays protect the original coplanar-base correction and closed shutter.
for origin, direction, material_name in [
    ((6,.3,.35),(-1,0,0),"ironreach_worn_brick"),
    ((0,-7,2),(0,1,0),"ironreach_faded_petrol"),
    ((-1.5,7,1.75),(0,-1,0),"ironreach_roof_petrol"),
]:
    hit, point, normal, face = obj.ray_cast(Vector(origin),Vector(direction))
    assert hit and mesh.materials[mesh.polygons[face].material_index].name == material_name, (
        origin, material_name, mesh.materials[mesh.polygons[face].material_index].name)
raw = GLB.read_bytes()
magic, version, length = struct.unpack_from('<4sII', raw)
assert magic == b'glTF' and version == 2 and length == len(raw)
json_length = struct.unpack_from('<I',raw,12)[0]
doc = json.loads(raw[20:20+json_length])
binary = raw[28+json_length:]
assert not any(doc.get(key) for key in ('images','textures','animations','skins','cameras'))
assert len(doc['meshes']) == 1 and len(doc['materials']) == 8 and len(doc['nodes']) == 2
assert {node['name'] for node in doc['nodes']} == {item.name for item in collection.objects}
assert all(node.get('scale',[1,1,1]) == [1,1,1] and 'rotation' not in node for node in doc['nodes'])
assert all(not mat.get('doubleSided', False) for mat in doc['materials'])
assert all(mat.get('alphaMode', 'OPAQUE') == 'OPAQUE' for mat in doc['materials'])


def accessor(index):
    """Decode actual GLB buffer values independently of claimed accessor bounds."""
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
export_degenerate = 0
for primitive in doc['meshes'][0]['primitives']:
    points = [Vector(v) for v in accessor(primitive['attributes']['POSITION'])]
    normals = [Vector(v) for v in accessor(primitive['attributes']['NORMAL'])]
    indices = [v[0] for v in accessor(primitive['indices'])]
    assert len(indices) % 3 == 0
    assert all(abs(normal.length-1) < .0001 for normal in normals)
    for i in range(0,len(indices),3):
        a,b,c = (points[k] for k in indices[i:i+3])
        cross = (b-a).cross(c-a)
        export_degenerate += cross.length <= 1e-10
        assert cross.dot(sum((normals[k] for k in indices[i:i+3]), Vector())) > 0
    positions.extend(points)
    triangles += len(indices)//3
    export_vertices += len(points)
assert export_degenerate == 0
assert triangles == len(mesh.loop_triangles)
gmin = [min(v[i] for v in positions) for i in range(3)]
gmax = [max(v[i] for v in positions) for i in range(3)]
assert all(abs(a-b) < .00001 for a,b in zip(gmin+gmax,
    [lo[0],lo[2],-hi[1],hi[0],hi[2],-lo[1]]))
sys.argv = [sys.argv[0], '--', str(SCRATCH)]
runpy.run_path(str(Path(__file__).with_name('export.py')),run_name='__main__')
assert (SCRATCH / GLB.name).read_bytes() == raw
report = {
    'asset_id': 'd08_workshop_buildings.01',
    'blender': bpy.app.version_string, 'build_hash': bpy.app.build_hash.decode(),
    'exporter': '5.2.40', 'source_vertices': len(mesh.vertices),
    'export_vertices': export_vertices, 'triangles': triangles, 'mesh_count': 1,
    'surface_count': len(doc['meshes'][0]['primitives']), 'nonmanifold_edges': nonmanifold,
    'degenerate_source_faces': degenerate, 'degenerate_export_triangles': export_degenerate,
    'unit_source_and_export_normals': True, 'positive_triangle_normal_alignment': True,
    'source_bounds': {'min':lo,'max':hi}, 'godot_bounds': {'min':gmin,'max':gmax},
    'godot_dimensions_m': [gmax[i]-gmin[i] for i in range(3)],
    'provisional_structural_footprint_m': [10,12], 'ground_pivot':[0,0,0],
    'dimension_tolerance_m': .001, 'axis_mapping_tolerance_m': .00001,
    'base_rear_wall_and_closed_shutter_material_rays': True,
    'materials': doc['materials'], 'reexport_byte_identical': True,
    'glb_bytes':len(raw), 'glb_sha256': hashlib.sha256(raw).hexdigest(),
    'status': 'PASS source/raw GLB/reexport; engine checks and downstream gates recorded separately'
}
(EVIDENCE / 'validation.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
print(json.dumps(report,indent=2))
