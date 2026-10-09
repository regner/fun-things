"""Inspect frozen saved Blender data and export only explicit roots into review evidence."""
import bpy
import bmesh
import hashlib
import io_scene_gltf2
import json
import math
from mathutils import Vector
from pathlib import Path
import sys

asset, destination = sys.argv[sys.argv.index('--')+1:]
out = Path(destination)
assert bpy.app.version == (5, 2, 2)
assert bpy.app.build_hash.decode() == 'd13f752e3b9c'
assert io_scene_gltf2.bl_info['version'] == (5, 2, 40)
source = Path(bpy.data.filepath)
before = hashlib.sha256(source.read_bytes()).hexdigest()
scene = bpy.context.scene
assert scene.unit_settings.system == 'METRIC' and scene.unit_settings.scale_length == 1
groups = [(asset, 'export_'+asset)]
if asset == 'city_planting_04':
    groups = [(asset+'_'+v, 'export_'+asset+'_'+v) for v in ('compact', 'broad')]
elif asset == 'city_planting_05':
    groups = [(asset+'_'+v, 'variant_'+v) for v in ('short_tuft', 'spreading_clump')]
result = {'asset':asset, 'source_sha256':before, 'pin':{
    'blender':bpy.app.version_string,'build':bpy.app.build_hash.decode(),
    'gltf':io_scene_gltf2.bl_info['version']},
    'libraries':[x.filepath for x in bpy.data.libraries],
    'images':[{'name':x.name,'path':x.filepath,'packed':bool(x.packed_file)} for x in bpy.data.images],
    'all_collections':{c.name:[o.name for o in c.objects] for c in bpy.data.collections},
    'all_objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,
                    'custom_properties':dict(o.items())} for o in bpy.data.objects],
    'variants':[]}
assert not result['libraries']
for rootname, collection in groups:
    col = bpy.data.collections[collection]
    col.hide_viewport = False
    col.hide_render = False
    objects = list(col.all_objects)
    root = bpy.data.objects[rootname]
    assert root in objects and root.type == 'EMPTY' and root.parent is None
    assert all(o == root or o.parent == root for o in objects)
    bpy.context.view_layer.update()
    points = []
    rows = []
    for o in objects:
        assert max(abs(o.matrix_world[i][j] - (i==j)) for i in range(4) for j in range(4)) < 1e-6
        if o == root:
            continue
        assert o.type == 'MESH' and not o.modifiers
        mesh = o.data
        mesh.calc_loop_triangles()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bad = [e.index for e in bm.edges if not e.is_manifold or not e.is_contiguous]
        assert not bad, (o.name,bad)
        unseen = set(bm.verts)
        islands = []
        while unseen:
            seed = unseen.pop()
            connected = {seed}
            todo = [seed]
            while todo:
                for e in todo.pop().link_edges:
                    for v in e.verts:
                        if v in unseen:
                            unseen.remove(v)
                            connected.add(v)
                            todo.append(v)
            faces = {f for v in connected for f in v.link_faces}
            # Divergence theorem on consistently wound polygon faces.
            volume = sum(f.calc_area()*f.normal.dot(f.calc_center_median())/3 for f in faces)
            if faces:
                assert volume > 0, (o.name,volume)
            islands.append({'vertices':len(connected),'faces':len(faces),'signed_volume':volume,
                'zero_face_vertex_coordinates':[list(v.co) for v in connected] if not faces else []})
        areas = [(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(
            mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length/2
            for t in mesh.loop_triangles]
        assert min(areas) > 1e-12, (o.name,min(areas))
        assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
        points.extend(o.matrix_world@v.co for v in mesh.vertices)
        rows.append({'name':o.name,'vertices':len(mesh.vertices),'triangles':len(areas),
            'minimum_triangle_area_m2':min(areas),'bad_edges':bad,'islands':islands,
            'uv_layers':list(mesh.uv_layers.keys()),'custom_normals':mesh.has_custom_normals,
            'materials':[m.name for m in mesh.materials],
            'matrix_world':[list(row) for row in o.matrix_world]})
        bm.free()
    low = [min(p[i] for p in points) for i in range(3)]
    high = [max(p[i] for p in points) for i in range(3)]
    materials = []
    for m in {m for o in objects if o.type=='MESH' for m in o.data.materials}:
        p = m.node_tree.nodes.get('Principled BSDF')
        materials.append({'name':m.name,'base_color':list(p.inputs['Base Color'].default_value),
            'metallic':p.inputs['Metallic'].default_value,'roughness':p.inputs['Roughness'].default_value,
            'backface_culling':m.use_backface_culling,
            'texture_nodes':[n.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE']})
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    settings = dict(export_format='GLB',use_selection=True,export_yup=True,
        export_apply=True,export_texcoords=False,export_normals=True,
        export_tangents=False,export_materials='EXPORT',export_cameras=False,
        export_lights=False,export_extras=False,export_animations=False)
    path = out/(rootname+'-fresh.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),**settings)
    variant = {'root':rootname,'collection':collection,'objects':rows,
               'blender_bounds':[low,high],
               'godot_bounds':[[low[0],low[2],-high[1]],[high[0],high[2],-low[1]]],
               'materials':materials,'export_settings':settings,
               'fresh_bytes':path.stat().st_size,
               'fresh_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    result['variants'].append(variant)
    # Independent source preview: authored export objects alone; scratch stage only.
    for o in scene.objects:
        o.hide_render = o not in objects
    for c in bpy.data.collections:
        c.hide_render = False
    center = Vector([(low[i]+high[i])/2 for i in range(3)])
    extent = max(high[i]-low[i] for i in range(3))
    cam_data = bpy.data.cameras.new('review_camera')
    camera = bpy.data.objects.new('review_camera',cam_data)
    scene.collection.objects.link(camera)
    camera.location = center+Vector((1.8,-2.5,1.7))*extent
    camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = extent*1.4
    scene.camera = camera
    lights = []
    for loc,power,size in [((2,-3,5),500,5),((-3,-1,2),250,4),((0,4,4),300,4)]:
        data = bpy.data.lights.new('review_light','AREA')
        data.energy = power
        data.shape = 'DISK'
        data.size = size
        ob = bpy.data.objects.new('review_light',data)
        scene.collection.objects.link(ob)
        ob.location = center+Vector(loc)
        ob.rotation_euler = (center-ob.location).to_track_quat('-Z','Y').to_euler()
        lights.append(ob)
    scene.world.color = (.12,.12,.12)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 2
    scene.render.resolution_x = 800
    scene.render.resolution_y = 650
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(out/(rootname+'-fresh-source.png'))
    scene.view_settings.view_transform = 'AgX'
    bpy.ops.render.render(write_still=True)
    variant['review_camera'] = {'position':list(camera.location),'rotation':list(camera.rotation_euler),
                               'orthographic_scale':cam_data.ortho_scale,'samples':16}
    for o in [camera]+lights:
        bpy.data.objects.remove(o,do_unlink=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == before
(out/(asset+'-source.json')).write_text(json.dumps(result,indent=2,default=list)+'\n')
print('INDEPENDENT_SOURCE_AUDIT_COMPLETE',asset)
