"""Independently measure the full-scale plaque, closed topology, face UVs and fresh GLB bytes."""
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
NID='d03_community_graphics_02'
EVIDENCE=ROOT/f'docs/assets/production/{NID}-evidence'
SCRATCH=Path(f'C:/tmp/ft/assets/{NID}')


def fingerprint(path):
    """Record exact payload identity for the final handoff."""
    raw=path.read_bytes()
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


def main():
    """Check source and binary geometry using literal dimensional and topology expectations."""
    source=ROOT/f'art/source/models/environment/{NID}/{NID}.blend'
    glb=ROOT/f'art/models/environment/{NID}/{NID}.glb'
    dependencies=[ROOT/'tools/asset_production/d03_court_graphics_02/validate.py',
                  ROOT/'tools/asset_production/d03_court_graphics_02/author.py',
                  ROOT/'tools/asset_production/d03_court_graphics_02/artwork.py',
                  ROOT/'tools/assets/blender/export_settings.json']
    for category,suffix in [('source/models','.blend'),('models','.glb')]:
        dependencies.append(ROOT/f'art/{category}/environment/d03_apartment_family_08/d03_apartment_family_08{suffix}')
    dependencies += [ROOT/'scenes/prefabs/environment/d03_apartment_family_08.tscn']
    before={p.relative_to(ROOT).as_posix():fingerprint(p) for p in dependencies}
    spec=importlib.util.spec_from_file_location('binary_decoder',dependencies[0])
    decoder=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.app.version_string=='5.2.2 LTS'
    assert bpy.context.scene.unit_settings.system=='METRIC'
    assert bpy.context.scene.unit_settings.scale_length==1
    collection=bpy.data.collections['export_'+NID]
    assert {o.name for o in collection.objects}=={'D03CommunityGraphics02','D03CommunityGraphics02_Mesh'}
    for obj in collection.objects:
        assert tuple(obj.location)==tuple(obj.rotation_euler)==(0,0,0)
        assert tuple(obj.scale)==(1,1,1) and not obj.modifiers
    obj=bpy.data.objects['D03CommunityGraphics02_Mesh']
    mesh=obj.data
    mesh.calc_loop_triangles()
    assert len(mesh.vertices)==80 and len(mesh.loop_triangles)==156
    assert all(math.isfinite(v) for p in mesh.vertices for v in p.co)
    assert all(abs(n.vector.length-1)<.0001 for n in mesh.corner_normals)
    bm=bmesh.new()
    bm.from_mesh(mesh)
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges)
    assert all(f.calc_area()>1e-10 for f in bm.faces)
    assert bm.calc_volume(signed=True)>0
    bm.free()
    face_polygons=[p for p in mesh.polygons if p.material_index==0]
    assert len(face_polygons)==1 and len(face_polygons[0].vertices)==20
    for p in face_polygons:
        assert p.normal.y>.99999
        for index in p.loop_indices:
            vertex=mesh.vertices[mesh.loops[index].vertex_index].co
            uv=mesh.uv_layers.active.data[index].uv
            assert abs(vertex.y-.032)<1e-6
            assert abs(uv.x-(.28-vertex.x)/.56)<1e-6
            assert abs(uv.y-(vertex.z+.2)/.4)<1e-6
    assert tuple(bpy.data.objects['STUDIO_one_metre_reference'].dimensions)==(1,1,1)
    image=bpy.data.materials['entrance_number_face'].node_tree.nodes['CommittedAlbedo'].image
    assert image.filepath.startswith('//') and image.packed_file is None
    raw=glb.read_bytes()
    length=int.from_bytes(raw[12:16],'little')
    doc=json.loads(raw[20:20+length])
    binary=raw[28+length:]
    assert len(doc['nodes'])==2 and len(doc['meshes'])==1
    assert not any(doc.get(k) for k in ('images','textures','skins','animations','cameras'))
    assert [doc['materials'][p['material']]['name'] for p in doc['meshes'][0]['primitives']]==['entrance_number_face','entrance_plaque_edge']
    points_all=[]
    triangles=vertices=0
    for slot,primitive in enumerate(doc['meshes'][0]['primitives']):
        points=decoder.accessor(doc,binary,primitive['attributes']['POSITION'])
        normals=decoder.accessor(doc,binary,primitive['attributes']['NORMAL'])
        indices=[x[0] for x in decoder.accessor(doc,binary,primitive['indices'])]
        uvs=decoder.accessor(doc,binary,primitive['attributes']['TEXCOORD_0'])
        points_all+=points
        vertices+=len(points)
        triangles+=len(indices)//3
        assert all(math.isfinite(v) for p in points for v in p)
        assert all(abs(Vector(n).length-1)<.0001 for n in normals)
        for i in range(0,len(indices),3):
            a,b,c=[Vector(points[j]) for j in indices[i:i+3]]
            cross=(b-a).cross(c-a)
            assert cross.length_squared>1e-20
            assert cross.dot(sum((Vector(normals[j]) for j in indices[i:i+3]),Vector()))>0
        if slot==0:
            assert len(indices)//3==18
            for p,n,uv in zip(points,normals,uvs):
                assert abs(p[2]+.032)<1e-6 and n[2]<-.99999
                assert abs(uv[0]-(.28-p[0])/.56)<1e-6
                assert abs(uv[1]-(.2-p[1])/.4)<1e-6
    lo=[min(p[i] for p in points_all) for i in range(3)]
    hi=[max(p[i] for p in points_all) for i in range(3)]
    assert all(abs(a-b)<1e-6 for a,b in zip(lo+hi,[-.28,-.2,-.032,.28,.2,0]))
    assert triangles==156
    sys.path.insert(0,str(Path(__file__).parent))
    from export import export_plaque
    export_plaque(SCRATCH/'reexport')
    assert (SCRATCH/'reexport'/glb.name).read_bytes()==raw
    assert before=={p.relative_to(ROOT).as_posix():fingerprint(p) for p in dependencies}
    result={'asset_id':'d03_community_graphics.02','status':'PASS',
            'blender':bpy.app.version_string,'build':bpy.app.build_hash.decode(),'exporter':'5.2.40',
            'source':fingerprint(source),'glb':fingerprint(glb),'dependencies':before,
            'source_vertices':80,'glb_vertices':vertices,'triangles':156,'meshes':1,'surfaces':2,
            'degenerate_faces':0,'degenerate_glb_triangles':0,'nonmanifold_edges':0,
            'unit_source_export_normals':True,'aabb':{'min':lo,'max':hi},
            'dimensions_m':[.56,.4,.032],'pivot':[0,0,0],'pivot_type':'wall-back centre',
            'face_slot':0,'upright_unmirrored_uv':True,'fresh_reexport_byte_identical':True,
            'shared_dependencies_unchanged':True}
    (EVIDENCE/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('ENTRANCE_VALIDATION_PASS',json.dumps(result))


if __name__=='__main__':
    main()
