"""Inspect immutable sources independently of producer author/export assertions."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
import io_scene_gltf2
ROOT=Path('/tmp/six-asset-review-390377d');OUT=Path(__file__).resolve().parent
IDS=['city_lights_01','city_lights_02','city_lights_04','city_sign_supports_01','city_planting_01','city_planting_02']
assert bpy.app.version_string=='5.2.2 LTS'
assert bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
reports=[]
for aid in IDS:
    src=ROOT/'art/source/models/environment'/aid/(aid+'.blend')
    bpy.ops.wm.open_mainfile(filepath=str(src))
    scene=bpy.context.scene;bpy.context.view_layer.update()
    col=bpy.data.collections['export_'+aid]
    report=dict(asset=aid,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),units=scene.unit_settings.system,unit_scale=scene.unit_settings.scale_length,libraries=[l.filepath for l in bpy.data.libraries],images=[dict(name=i.name,filepath=i.filepath,packed=bool(i.packed_file),source=i.source) for i in bpy.data.images],members=[],excluded_objects=[dict(name=o.name,type=o.type) for o in bpy.data.objects if o not in list(col.all_objects)],cameras=[])
    points=[]
    for o in col.all_objects:
        item=dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,location=list(o.location),rotation=list(o.rotation_euler),scale=list(o.scale),modifiers=[m.name for m in o.modifiers])
        if o.type=='MESH':
            m=o.data;bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles()
            vertices=[o.matrix_world@v.co for v in m.vertices];points.extend(vertices)
            item.update(vertices=len(m.vertices),triangles=len(m.loop_triangles),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),inconsistent_edges=sum(e.is_manifold and not e.is_contiguous for e in bm.edges),loose_vertices=sum(not v.link_faces for v in bm.verts),loose_edges=sum(not e.link_faces for e in bm.edges),signed_volume=bm.calc_volume(signed=True),zero_area_faces=sum(p.area<1e-10 for p in m.polygons),zero_area_triangles=sum((m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co).length<1e-10 for t in m.loop_triangles),nonfinite_coordinates=sum(not math.isfinite(c) for v in m.vertices for c in v.co),bad_corner_normals=sum(not all(math.isfinite(c) for c in n.vector) or abs(n.vector.length-1)>1e-5 for n in m.corner_normals),materials=[x.name for x in m.materials],material_face_counts={str(i):sum(p.material_index==i for p in m.polygons) for i in range(len(m.materials))},uv_layers=[u.name for u in m.uv_layers],bounds_blender=[[min(v[i] for v in vertices) for i in range(3)],[max(v[i] for v in vertices) for i in range(3)]])
            bm.free()
        report['members'].append(item)
    report['bounds_blender']=[[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]]
    report['meter_reference_objects']=[dict(name=o.name,dimensions=list(o.dimensions),type=o.type) for o in bpy.data.objects if 'met' in o.name.lower() or 'ref' in o.name.lower()]
    for o in bpy.data.objects:
        if o.type=='CAMERA':report['cameras'].append(dict(name=o.name,type=o.data.type,position=list(o.location),rotation=list(o.rotation_euler),angle_y=o.data.angle_y,resolution=[scene.render.resolution_x,scene.render.resolution_y],clip=[o.data.clip_start,o.data.clip_end]))
    reports.append(report)
(OUT/'independent-source-inspection.json').write_text(json.dumps(dict(blender=bpy.app.version_string,build=bpy.app.build_hash.decode(),exporter=io_scene_gltf2.bl_info['version'],assets=reports),indent=2)+'\n')
print('INSPECTED',len(reports),'SOURCES')
