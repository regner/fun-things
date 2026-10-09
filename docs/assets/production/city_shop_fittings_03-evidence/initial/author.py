"""Original editable entrance surrounds, authored only in a private Blender process."""
import bpy, bmesh
from pathlib import Path
import io_scene_gltf2
R = Path(__file__).resolve().parents[3]
assert bpy.app.version[:3] == (5, 2, 2)
assert bpy.app.build_hash.decode() == 'd13f752e3b9c'
assert io_scene_gltf2.bl_info['version'] == (5, 2, 40)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
s = bpy.context.scene
s.unit_settings.system = 'METRIC'; s.unit_settings.scale_length = 1
export = bpy.data.collections.new('export_city_shop_fittings_03')
s.collection.children.link(export)
studio = bpy.data.collections.new('authoring_excluded'); s.collection.children.link(studio)

def material(name, swatch, metallic, roughness):
    m = bpy.data.materials.new(name); m.use_nodes = True; m.use_backface_culling = True
    rgb = [int(swatch[i:i+2], 16)/255 for i in (0, 2, 4)]
    rgba = tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = rgba
    p.inputs['Metallic'].default_value = metallic; p.inputs['Roughness'].default_value = roughness
    m.diffuse_color = rgba
    return m

paint = material('surround_slate_petrol', '405B68', .25, .46)
trim = material('surround_warm_ivory', 'C8C2AD', .22, .48)
stop = material('surround_dark_rebate', '293B43', .25, .55)
sill = material('surround_satin_threshold', '929D9F', .65, .38)

def mesh(name, vertices, faces, mat, bevel, col, parent=None):
    data = bpy.data.meshes.new(name); data.from_pydata(vertices, [], faces); data.update()
    o = bpy.data.objects.new(name, data); col.objects.link(o); o.parent = parent
    data.materials.append(mat)
    bm = bmesh.new(); bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(data); bm.free()
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    if bevel:
        m = o.modifiers.new('manufactured_edge_radius', 'BEVEL'); m.width = bevel; m.segments = 4
        bpy.ops.object.modifier_apply(modifier=m.name)
    for f in data.polygons: f.use_smooth = True
    m = o.modifiers.new('broad_face_normals', 'WEIGHTED_NORMAL'); m.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=m.name)
    o.select_set(False)
    return o

def u_section(outer, inner, top, head, bottom=.02):
    return [(-outer/2,bottom),(-outer/2,top),(outer/2,top),(outer/2,bottom),
            (inner/2,bottom),(inner/2,head),(-inner/2,head),(-inner/2,bottom)]

def sweep(name, stations, mat, bevel, col, root):
    verts = [(x,y,z) for y,section in stations for x,z in section]; n=len(stations[0][1])
    faces = [tuple(reversed(range(n))), tuple((len(stations)-1)*n+i for i in range(n))]
    for k in range(len(stations)-1):
        faces.extend((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n))
    return mesh(name, verts, faces, mat, bevel, col, root)

for variant,w in [('single',1.04),('double',1.84)]:
    col = bpy.data.collections.new('variant_'+variant); export.children.link(col)
    root = bpy.data.objects.new('city_shop_fittings_03_'+variant,None); col.objects.link(root)
    root['datum'] = 'Centre of opening, finished floor Z=0, wall plane Y=0; +Y street'
    root['rear_aperture_width_m'] = w; root['aperture_head_m'] = 2.24
    root['leaf_front_y_m'] = -.430; root['leaf_back_y_m'] = -.475
    root['leaf_bottom_z_m'] = .030; root['leaf_top_z_m'] = 2.232
    root['leaf_side_gap_m'] = .008; root['leaf_meeting_gap_m'] = .008 if variant=='double' else 0.
    # Full-depth formed reveal narrows toward the rear leaf seat. This is loose cladding,
    # not a replacement shell wall or a second door-leaf perimeter frame.
    sweep(variant+'_recessed_reveal',[
        (-.520,u_section(w+.36,w,2.44,2.24)),
        (-.400,u_section(w+.36,w,2.44,2.24)),
        (-.070,u_section(w+.36,w+.22,2.44,2.36)),
        (.045,u_section(w+.36,w+.22,2.44,2.36))],paint,.006,col,root)
    sweep(variant+'_rounded_face_casing',[
        (.010,u_section(w+.50,w+.205,2.48,2.355)),
        (.085,u_section(w+.50,w+.205,2.48,2.355))],trim,.012,col,root)
    sweep(variant+'_rear_stop',[
        (-.516,u_section(w+.045,w-.032,2.275,2.224)),
        (-.481,u_section(w+.045,w-.032,2.275,2.224))],stop,.003,col,root)
    # 20 mm sill crown, sloped front nose and rear return; no tread/noise geometry.
    profile=[(-.520,0),(.110,0),(.110,.004),(.045,.020),(-.500,.020),(-.520,.014)]
    verts=[(x,y,z) for x in (-(w+.36)/2,(w+.36)/2) for y,z in profile]; n=len(profile)
    faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
    faces.extend((i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n))
    mesh(variant+'_sloped_threshold',verts,faces,sill,.001,col,root)
# An actual saved, excluded cubic metre, never a production component.
bpy.ops.mesh.primitive_cube_add(size=1, location=(-2,0,.5))
ref=bpy.context.object; ref.name='authoring_1m_reference'
for c in list(ref.users_collection): c.objects.unlink(ref)
studio.objects.link(ref); ref.data.materials.append(trim); ref.hide_render=True; ref.hide_set(True)
ref['measured_dimensions_m']=[1.,1.,1.]
s['provenance']='Original Codex / requested Astra medium commission; Blender-authored meshes; no external mesh/image/texture inputs.'
s['axis_contract']='Metres; Blender +Y front +Z up -> Godot -Z front +Y up'
s['scope']='Loose entrance surrounds only. No leaves, walls, interior, animation, collision or gameplay.'
s['variants']='single: 1.04m aperture; double: 1.84m aperture; identity roots overlap intentionally for variant export.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/source/models/environment/city_shop_fittings_03/city_shop_fittings_03.blend'))
print('AUTHOR_COMPLETE')
