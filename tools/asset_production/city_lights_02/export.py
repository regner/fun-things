"""Reexport the saved source's declared collection and audit source geometry."""
import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector
import io_scene_gltf2
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_lights_02-evidence'
OUT=ROOT/'art/models/environment/city_lights_02'
col=bpy.data.collections['export_city_lights_02']
assert bpy.app.version[:3]==(5,2,2),bpy.app.version_string
meshes=[o for o in col.objects if o.type=='MESH']
bpy.context.view_layer.update()
coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=[min(v[i] for v in coords) for i in range(3)]; hi=[max(v[i] for v in coords) for i in range(3)]
assert all(abs(a-b)<.001 for a,b in zip(lo,[-.36,-.36,0])),lo
assert all(abs(a-b)<.001 for a,b in zip(hi,[.36,.36,3])),hi
report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'exporter':io_scene_gltf2.bl_info['version'],'bounds_blender':[lo,hi],'dimensions_godot_m':[.72,3,.72],'objects':[]}
for o in meshes:
    assert all(abs(v-1)<1e-6 for v in o.scale)
    assert all(abs(v)<1e-6 for v in o.rotation_euler)
    bm=bmesh.new(); bm.from_mesh(o.data)
    bad=sum(not e.is_manifold for e in bm.edges)
    assert bad==0,(o.name,bad)
    assert bm.calc_volume(signed=True)>0,o.name
    assert all(p.area>1e-10 for p in o.data.polygons),o.name
    o.data.calc_loop_triangles()
    report['objects'].append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'nonmanifold_edges':bad,'signed_volume':bm.calc_volume(signed=True)})
    bm.free()
report['triangles']=sum(o['triangles'] for o in report['objects'])
assert report['triangles']<6000
settings=dict(export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=False,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=False,export_animations=False)
report['export_settings']=settings
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
lens=bpy.data.objects['broad_recessed_diffuser']
report['outputs']={}
for suffix,mat in [('', 'city_lights_02_lens_warm'),('_cool','city_lights_02_lens_cool')]:
    lens.data.materials[0]=bpy.data.materials[mat]
    path=OUT/('city_lights_02'+suffix+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),**settings)
    report['outputs'][str(path.relative_to(ROOT))]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
lens.data.materials[0]=bpy.data.materials['city_lights_02_lens_warm']
(E/'source_export_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('CITY_LIGHTS_02_CHECKS_PASS',json.dumps(report))
