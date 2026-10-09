"""Independent saved-source topology, membership, transforms and deterministic exports."""
import bpy
import bmesh
import io_scene_gltf2
import hashlib
import json
import math
from pathlib import Path
import sys

OUT=Path(__file__).resolve().parent
FROZEN=Path('/tmp/batch03-independent/frozen')
ident=sys.argv[sys.argv.index('--')+1]
assert bpy.app.version[:3]==(5,2,2)
assert bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
assert bpy.context.scene.unit_settings.system=='METRIC'
assert bpy.context.scene.unit_settings.scale_length==1
result=dict(id=ident,filepath=bpy.data.filepath,blender=bpy.app.version_string,
 build=bpy.app.build_hash.decode(),gltf=io_scene_gltf2.bl_info['version'],
 libraries=[l.filepath for l in bpy.data.libraries],
 images=[dict(name=i.name,type=i.type,path=i.filepath,packed=bool(i.packed_file)) for i in bpy.data.images],
 variants=[],all_scene_objects=[dict(name=o.name,type=o.type,collections=[c.name for c in o.users_collection]) for o in bpy.data.objects])
ref=bpy.data.objects['authoring_1m_reference']
result['metre_reference']=dict(dimensions=list(ref.dimensions),matrix=[list(row) for row in ref.matrix_world])
issues=[]
if result['libraries']: issues.append('external libraries')
if any(i['path'] or i['packed'] for i in result['images']): issues.append('external/packed images')
if any(abs(x-1)>1e-6 for x in ref.dimensions): issues.append('reference dimensions')
variant_names=['single','double'] if ident in ('city_shop_fittings_03','city_shop_fittings_06') else [None]
for variant in variant_names:
    export_name=ident+('_'+variant if variant else '')
    col=bpy.data.collections['variant_'+variant if variant else 'export_'+ident]
    members=list(col.all_objects)
    root=bpy.data.objects[export_name]
    entry=dict(name=export_name,members=sorted(o.name for o in members),objects=[])
    if ref in members: issues.append(export_name+': exported reference')
    if root.parent or root.type!='EMPTY': issues.append(export_name+': root contract')
    for o in members:
        item=dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,
                  location=list(o.location),rotation=list(o.rotation_euler),scale=list(o.scale),
                  modifiers=[m.type for m in o.modifiers])
        if any(abs(x-1)>1e-7 for x in o.scale) or any(abs(x)>1e-7 for x in o.rotation_euler): issues.append(o.name+': scale/rotation')
        if o!=root and o.parent!=root: issues.append(o.name+': parent')
        if o.type=='MESH':
            if any(abs(x)>1e-7 for x in o.location) or o.modifiers: issues.append(o.name+': unapplied static transforms/modifiers')
            mesh=o.data
            mesh.calc_loop_triangles()
            bm=bmesh.new();bm.from_mesh(mesh)
            bad_edges=[e.index for e in bm.edges if not e.is_manifold or not e.is_contiguous]
            isolated=[v.index for v in bm.verts if not v.link_faces]
            remaining=set(bm.verts);volumes=[]
            while remaining:
                v=remaining.pop();group={v};stack=[v]
                while stack:
                    for e in stack.pop().link_edges:
                        for w in e.verts:
                            if w in remaining:
                                remaining.remove(w);group.add(w);stack.append(w)
                faces={f for v in group for f in v.link_faces}
                volumes.append(sum(f.calc_area()*f.normal.dot(f.calc_center_median())/3 for f in faces))
            coords=[o.matrix_world@v.co for v in mesh.vertices]
            lo=[min(v[i] for v in coords) for i in range(3)]
            hi=[max(v[i] for v in coords) for i in range(3)]
            tiny=[];normal_bad=[];winding=[];dots=[]
            for tri in mesh.loop_triangles:
                a,b,c=[mesh.vertices[i].co for i in tri.vertices]
                n=(b-a).cross(c-a)
                if n.length<1e-10: tiny.append(tri.index);continue
                n.normalize()
                for li in tri.loops:
                    cn=mesh.corner_normals[li].vector
                    if not all(math.isfinite(x) for x in cn) or abs(cn.length-1)>1e-4: normal_bad.append(li)
                    dots.append(n.dot(cn))
                    if n.dot(cn)<-1e-5: winding.append(tri.index)
            item.update(vertices=len(mesh.vertices),polygons=len(mesh.polygons),triangles=len(mesh.loop_triangles),
                bounds_blender=[lo,hi],materials=[m.name for m in mesh.materials],
                uv_layers=[u.name for u in mesh.uv_layers],component_volumes_m3=volumes,
                bad_edges=bad_edges,isolated_vertices=isolated,degenerate_triangles=tiny,
                invalid_normals=normal_bad,reversed_normal_triangles=sorted(set(winding)),minimum_winding_dot=min(dots),
                nonfinite_positions=sum(not all(math.isfinite(x) for x in v.co) for v in mesh.vertices))
            if bad_edges or isolated or tiny or normal_bad or winding or any(v<=0 for v in volumes) or item['nonfinite_positions']: issues.append(o.name+': topology/normals')
            bm.free()
        elif o.type!='EMPTY': issues.append(o.name+': unexpected type')
        entry['objects'].append(item)
    settings=dict(export_format='GLB',use_selection=True,export_yup=True,
        export_apply=ident!='city_shop_fittings_02',
        export_texcoords=ident in ('city_shop_fittings_02','city_shop_fittings_08'),
        export_normals=True,export_tangents=False,export_materials='EXPORT',
        export_cameras=False,export_lights=False,export_extras=False,export_animations=False)
    if ident=='city_shop_fittings_02': settings.update(export_skins=False,export_morph=False)
    bpy.ops.object.select_all(action='DESELECT')
    for o in members:o.select_set(True)
    target=OUT/'reexports'/(export_name+'.glb');target.parent.mkdir(exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(target),**settings)
    original=FROZEN/'art/models/environment'/ident/(export_name+'.glb')
    entry.update(export_settings=settings,reexport_path=str(target),
        reexport_bytes=target.stat().st_size,reexport_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        candidate_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
        byte_identical=target.read_bytes()==original.read_bytes())
    if not entry['byte_identical']: issues.append(export_name+': stale export or mismatched settings')
    result['variants'].append(entry)
result['issues']=issues
(OUT/(ident+'.source.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(id=ident,issues=issues,variants=[dict(name=v['name'],members=len(v['members']),byte_identical=v['byte_identical']) for v in result['variants']]),indent=2))
assert not issues,issues
