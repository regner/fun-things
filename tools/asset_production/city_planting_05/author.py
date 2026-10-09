"""Author original closed, swept broad blades; no runtime procedural geometry."""
import bpy, bmesh, math
from pathlib import Path
from mathutils import Vector
import io_scene_gltf2
R = Path(__file__).resolve().parents[3]
assert bpy.app.version[:3] == (5, 2, 2)
assert bpy.app.build_hash.decode() == 'd13f752e3b9c'
assert io_scene_gltf2.bl_info['version'] == (5, 2, 40)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
s = bpy.context.scene
s.unit_settings.system = 'METRIC'
s.unit_settings.scale_length = 1
s.render.threads_mode = 'FIXED'
s.render.threads = 4
bpy.context.preferences.filepaths.save_version = 0

def material(name, rgb, roughness):
    """Use explicit linear PBR colors from authored sRGB swatches."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.use_backface_culling = True
    c = [((v / 255 + .055) / 1.055) ** 2.4 if v > 10 else v / 3294.6 for v in rgb]
    m.diffuse_color = (*c, 1)
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*c, 1)
    p.inputs['Roughness'].default_value = roughness
    return m

mats = [material('weed_olive', (92, 108, 61), .89),
        material('weed_olive_light', (112, 122, 72), .88),
        material('weed_olive_dry', (125, 121, 76), .94)]
export = bpy.data.collections.new('export_city_planting_05')
s.collection.children.link(export)

def blade(name, base, angle, reach, height, width, lean, material_id, col, root):
    """Sweep a thin lenticular solid with a broad middle and tapered hooked tip."""
    direction = Vector((math.cos(angle), math.sin(angle), 0))
    side = Vector((-math.sin(angle), math.cos(angle), 0))
    verts, faces = [], []
    # Eleven longitudinal rings and six cross-section vertices suffice for a
    # smooth broad blade; closed solids avoid backface-dependent leaf cards.
    stations = [0, .08, .16, .25, .35, .46, .57, .68, .78, .87, .94]
    for t in stations:
        z = .012 + height * math.sin(math.pi * .78 * t)
        centre = Vector(base) + direction * (reach * t ** 1.35) + side * (lean * t*t)
        centre.z += z
        tangent = direction * (reach * 1.35 * max(t, .001) ** .35)
        tangent += side * (2 * lean * t) + Vector((0, 0, height * math.pi * .78 * math.cos(math.pi*.78*t)))
        normal = tangent.normalized().cross(side).normalized()
        w = width * (.20 + .80 * math.sin(math.pi * t)) * (1 - .65 * t)
        thickness = .003 * (.65 + .35 * math.sin(math.pi*t))
        for j in range(6):
            a = j * math.tau / 6
            verts.append(tuple(centre + side * (w * math.cos(a)) + normal * (thickness * math.sin(a))))
    tip = Vector(base) + direction * reach + side * lean
    tip.z += .012 + height * math.sin(math.pi * .78)
    verts.append(tuple(tip))
    faces.append(tuple(reversed(range(6))))
    for k in range(len(stations)-1):
        for j in range(6):
            a = k*6+j; b = k*6+(j+1)%6
            faces.append((a,b,b+6,a+6))
    last = (len(stations)-1)*6
    faces.extend((last+j,last+(j+1)%6,len(verts)-1) for j in range(6))
    me = bpy.data.meshes.new(name+'_mesh')
    me.from_pydata(verts, [], faces)
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(me); bm.free()
    me.materials.append(mats[material_id])
    for p in me.polygons: p.use_smooth=True
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); ob.parent=root
    return ob

for variant, dimensions in [('short_tuft',(.56,.42,.26)),('spreading_clump',(1.0,.62,.20))]:
    col=bpy.data.collections.new('variant_'+variant); export.children.link(col)
    root=bpy.data.objects.new('city_planting_05_'+variant,None); col.objects.link(root)
    root['provenance']='Original Codex Blender construction for city_planting.05, 2026-10-09'
    root['front']='Blender +Y/+Z up -> Godot -Z/+Y up'
    root['ground_datum_m']=0.0
    root['runtime']='Static visual dressing; no collision, wind, growth, rigs or sockets'
    objects=[]
    if variant=='short_tuft':
        specs=[(0,0, 12,.23,.23,.045,.012,0),(.018,0,67,.16,.28,.040,-.012,1),
               (-.02,0,116,.20,.21,.042,.009,0),(0,-.01,162,.25,.17,.044,-.015,0),
               (.005,.01,209,.23,.23,.038,.018,1),(-.01,.02,252,.18,.27,.039,-.01,0),
               (0,0,301,.25,.18,.045,.012,0),(.012,-.01,337,.19,.22,.037,-.014,2),
               (-.014,0,85,.08,.29,.032,.006,0)]
    else:
        specs=[]
        for cx,cy,phase in [(-.24,-.035,16),(.03,.085,43),(.27,-.045,-7)]:
            for j,(reach,height,width,mi) in enumerate([(.24,.17,.045,0),(.20,.19,.04,1),(.27,.14,.044,0),(.23,.18,.041,0),(.19,.16,.037,2)]):
                specs.append((cx,cy,phase+j*73,reach,height,width,.012*(-1)**j,mi))
    for i,(x,y,a,r,h,w,lean,mi) in enumerate(specs):
        objects.append(blade(variant+'_blade_%02d'%(i+1),(x,y,0),math.radians(a),r,h,w,lean,mi,col,root))
    pts=[v.co for o in objects for v in o.data.vertices]
    lo=[min(v[i] for v in pts) for i in range(3)]; hi=[max(v[i] for v in pts) for i in range(3)]
    # Bake measured fitting into mesh coordinates; all object/root transforms stay identity.
    for o in objects:
        for v in o.data.vertices:
            for i in range(3):
                origin=lo[i] if i==2 else (hi[i]+lo[i])/2
                v.co[i]=(v.co[i]-origin)*dimensions[i]/(hi[i]-lo[i])
        o.data.update()
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join()
    bpy.context.object.name=variant+'_blades'
    root['blade_count']=len(specs)
    root['blender_dimensions_m']=dimensions
    col.hide_render=(variant=='spreading_clump')

studio=bpy.data.collections.new('authoring_reference_excluded'); s.collection.children.link(studio)
def move(ob):
    """Keep fixtures and presentation objects outside the named export collection."""
    for c in list(ob.users_collection): c.objects.unlink(ob)
    studio.objects.link(ob)
    return ob
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.3,0,.5))
ref=move(bpy.context.object); ref.name='reference_one_metre_vertical'
ref.scale=(.035,.035,1); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
ref.data.materials.append(material('reference_ivory',(224,215,189),.8))
ref['height_m']=1.0; ref['excluded_from_runtime']=True
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.002))
floor=move(bpy.context.object); floor.name='preview_ground_excluded'
floor.data.materials.append(material('preview_slate',(104,116,120),.95))
def camera(name,loc,target):
    """Provide reproducible close and project-camera views."""
    bpy.ops.object.camera_add(location=loc); c=move(bpy.context.object); c.name=name
    c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
    return c
hero=camera('hero_camera',(1.8,-2.7,1.8),(0,0,.15)); hero.data.type='ORTHO'; hero.data.ortho_scale=1.3
project=camera('project_vertical_47m_42deg',(0,0,47),(0,0,0))
project.data.sensor_fit='VERTICAL'; project.data.angle=math.radians(42)
for name,loc,power,size in [('key',(1,-3,6),800,4),('fill',(-4,1,3),450,5),('rim',(2,3,4),500,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); light=move(bpy.context.object); light.name=name
    light.data.energy=power; light.data.shape='DISK'; light.data.size=size
    light.rotation_euler=(Vector((0,0,.2))-light.location).to_track_quat('-Z','Y').to_euler()
s.world.color=(.25,.25,.25); s.render.engine='CYCLES'; s.cycles.samples=32
s.cycles.use_denoising=True; s.cycles.device='CPU'; s.camera=hero
s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'
s.render.resolution_x=1200; s.render.resolution_y=800; s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/source/models/environment/city_planting_05/city_planting_05.blend'))
print('AUTHOR_PASS: original 9-blade tuft / 15-blade three-root clump; source saved')
