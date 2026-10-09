"""Bootstrap owned car sources once; subsequent reexports read the saved .blend files."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / 'docs/assets/vehicle_car_evidence'
SPECS = [
    dict(id='car_latch_a', width=1.88, height=1.54, length=3.40, radius=.31,
         paint=(255,114,93), hood=(246,241,220), roof_width=1.34,
         roof_front=.24, roof_back=-.90, glass_front=.72, glass_back=-1.36),
    dict(id='car_crate_a', width=1.90, height=1.64, length=3.65, radius=.33,
         paint=(246,241,220), hood=(18,79,91), roof_width=1.48,
         roof_front=.30, roof_back=-1.22, glass_front=.66, glass_back=-1.48),
    dict(id='car_sable_a', width=1.92, height=1.44, length=4.25, radius=.32,
         paint=(91,48,91), hood=(181,101,97), roof_width=1.37,
         roof_front=.29, roof_back=-.90, glass_front=.92, glass_back=-1.37),
]


def material(name, rgb, roughness=.55, metallic=0, emission=0):
    """Author glTF-compatible opaque palette materials in scene-linear space."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    color = [((v / 255 + .055) / 1.055) ** 2.4 if v > 10 else v / 3294.6 for v in rgb]
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    if emission:
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = emission
    mat.diffuse_color = (*color, 1)
    return mat


def move_to(obj, col, parent):
    """Keep only explicit export-collection membership and authored local parenting."""
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    col.objects.link(obj)
    obj.parent = parent
    return obj


def empty(col, name, parent=None, position=(0, 0, 0)):
    """Create an exportable rigid-part pivot or source socket using Blender axes."""
    obj = bpy.data.objects.new(name, None)
    col.objects.link(obj)
    obj.parent = parent
    obj.location = position
    obj.empty_display_size = .12
    return obj


def finish(obj, mat, bevel=.025):
    """Apply bevels and triangulation while retaining broad face normals."""
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    if bevel:
        mod = obj.modifiers.new('source_bevel', 'BEVEL')
        mod.width, mod.segments = bevel, 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for face in obj.data.polygons:
        face.use_smooth = True
    normals = obj.modifiers.new('broad_face_normals', 'WEIGHTED_NORMAL')
    normals.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=normals.name)
    tri = obj.modifiers.new('export_triangles', 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=tri.name)
    return obj


def box(col, parent, name, size, position, mat, bevel=.025):
    """Build a source-owned bevelled rigid panel without runtime mesh generation."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = move_to(bpy.context.object, col, parent)
    obj.name = name
    obj.location = position
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return finish(obj, mat, bevel)


def mesh(col, parent, name, vertices, faces, mat, bevel=.025):
    """Author a closed shaped car volume with explicit source topology."""
    data = bpy.data.meshes.new(name + '_mesh')
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    obj.parent = parent
    return finish(obj, mat, bevel)


def loft(col, parent, name, sections, mat):
    """Loft octagonal hull sections to shape hood, shoulders and rear independently."""
    vertices = []
    for y, half_width, bottom, top in sections:
        corner = .10
        vertices.extend([
            (-half_width + corner, y, bottom), (half_width - corner, y, bottom),
            (half_width, y, bottom + corner), (half_width, y, top - corner),
            (half_width - corner, y, top), (-half_width + corner, y, top),
            (-half_width, y, top - corner), (-half_width, y, bottom + corner),
        ])
    faces = [tuple(reversed(range(8))), tuple(range((len(sections)-1)*8,len(sections)*8))]
    for ring in range(len(sections)-1):
        for i in range(8):
            j = (i+1)%8
            faces.append((ring*8+i,ring*8+j,(ring+1)*8+j,(ring+1)*8+i))
    # Recalculate mesh normals rather than depend on source winding conventions.
    obj = mesh(col,parent,name,vertices,faces,mat,.035)
    bpy.context.view_layer.objects.active=obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)
    return obj


def wheel_mesh(col, parent, name, radius, depth, offset, mat):
    """Author an axle-aligned cylindrical tire or hub at its actual spin pivot."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth)
    obj=move_to(bpy.context.object,col,parent)
    obj.name=name
    obj.location=(offset,0,0)
    obj.rotation_euler=(0,math.pi/2,0)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    return finish(obj,mat,.018)


def source_path(asset):
    """Return one vehicle's canonical editable source path."""
    return ROOT / 'art/source/models/vehicles' / asset / (asset + '.blend')


def output_path(asset):
    """Return one vehicle's canonical runtime export path."""
    return ROOT / 'art/models/vehicles' / asset / (asset + '.glb')


def build(spec):
    """Construct one separately identified vehicle with mechanical pivots and sockets."""
    asset=spec['id']; source=source_path(asset); output=output_path(asset)
    source.parent.mkdir(parents=True,exist_ok=True)
    output.parent.mkdir(parents=True,exist_ok=True)
    assert not source.exists(), 'Bootstrap refuses to replace saved source: '+str(source)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
    scene.render.fps=30
    col=bpy.data.collections.new('export_'+asset);scene.collection.children.link(col)
    root=empty(col,asset)
    mats={
        'body_paint':material('body_paint',spec['paint'],.46,.12),
        'hood_inset':material('hood_inset',spec['hood'],.53,.05),
        'glass':material('glass',(24,56,72),.28,.2),
        'tire':material('tire',(25,30,35),.85),
        'trim':material('trim',(40,48,57),.7),
        'wheel_hub':material('wheel_hub',(139,147,154),.42,.45),
        'headlamp':material('headlamp',(255,235,181),.4,emission=.65),
        'tail_lamp':material('tail_lamp',(241,66,59),.4,emission=.55),
    }
    W,H,L=spec['width'],spec['height'],spec['length']
    half=W/2-.07
    sections=[(-L/2,half-.11,.29,.87),(-L/2+.23,half,.22,1.00),
              (-.60,half,.22,1.04),(.70,half,.22,1.04),
              (L/2-.22,half-.025,.27,1.00),(L/2,half-.16,.34,.87)]
    body=loft(col,root,'Body',sections,mats['body_paint'])
    # Arch cutters remain authoring intermediates and are removed before source save/export.
    front=L/2-.62; rear=-L/2+.62; radius=spec['radius']
    for x in (-W/2+.07,W/2-.07):
        for y in (front,rear):
            bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius+.06,depth=.36,
                location=(x,y,radius),rotation=(0,math.pi/2,0))
            cutter=bpy.context.object
            bpy.context.view_layer.objects.active=body
            mod=body.modifiers.new('source_wheel_arch','BOOLEAN')
            mod.operation='DIFFERENCE';mod.object=cutter
            bpy.ops.object.modifier_apply(modifier=mod.name)
            bpy.data.objects.remove(cutter,do_unlink=True)
    lower_front=spec['glass_front'];lower_back=spec['glass_back']
    upper_front=spec['roof_front'];upper_back=spec['roof_back']
    a=(W-.34)/2;b=spec['roof_width']/2;lower=1.06;upper=H-.035
    verts=[(-a,lower_back,lower),(a,lower_back,lower),(a,lower_front,lower),(-a,lower_front,lower),
           (-b,upper_back,upper),(b,upper_back,upper),(b,upper_front,upper),(-b,upper_front,upper)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh(col,root,'CabinGlass',verts,faces,mats['glass'],.035)
    box(col,root,'Roof',(spec['roof_width'],upper_front-upper_back,.07),
        (0,(upper_front+upper_back)/2,H-.035),mats['body_paint'],.033)
    hood_length=L/2-.26-lower_front
    box(col,root,'HoodInset',(W*.57,hood_length,.027),
        (0,lower_front+hood_length/2,1.055),mats['hood_inset'],.013)
    if asset=='car_sable_a':
        box(col,root,'RearDeck',(W*.69,.38,.035),(0,-L/2+.40,1.025),mats['body_paint'],.016)
    if asset=='car_crate_a':
        for x in (-.30,.30):
            box(col,root,'RoofRib_'+str(x),(.023,.94,.012),(x,-.51,H+.004),mats['body_paint'],.005)
    for sign in (-1,1):
        box(col,root,'MirrorLeft' if sign<0 else 'MirrorRight',(.15,.21,.11),
            (sign*(W/2-.085),lower_front-.18,1.15),mats['body_paint'],.035)
        # Broad pillars are source parts rather than thin painted window decals.
        box(col,root,'PillarLeft' if sign<0 else 'PillarRight',(.055,.10,H-1.075),
            (sign*(W/2-.175),-.24,(H+1.04)/2),mats['body_paint'],.018)
        box(col,root,'HeadlampLeft' if sign<0 else 'HeadlampRight',(.29,.11,.14),
            (sign*(half-.27),L/2-.075,.82),mats['headlamp'],.035)
        box(col,root,'TaillampLeft' if sign<0 else 'TaillampRight',(.28,.08,.12),
            (sign*(half-.25),-L/2+.035,.82),mats['tail_lamp'],.027)
    box(col,root,'FrontBumper',(W-.22,.15,.20),(0,L/2-.075,.46),mats['trim'],.06)
    box(col,root,'RearBumper',(W-.22,.13,.18),(0,-L/2+.065,.42),mats['trim'],.055)
    wheels=empty(col,'Wheels',root)
    for side,sign in [('Left',-1),('Right',1)]:
        for end,y in [('Front',front),('Rear',rear)]:
            steer=empty(col,'Steer'+end+side,wheels,(sign*(W/2-.10),y,radius))
            spin=empty(col,'Spin'+end+side,steer)
            wheel_mesh(col,spin,'Tire'+end+side,radius,.20,0,mats['tire'])
            wheel_mesh(col,spin,'Hub'+end+side,radius*.63,.021,sign*.092,mats['wheel_hub'])
            wheel_mesh(col,spin,'HubCenter'+end+side,radius*.22,.025,sign*.094,mats['trim'])
    markers=empty(col,'Markers',root)
    socket_positions={
        'socket_driver':(-.34,.86,-.12),
        'socket_entry_left':(-W/2-.40,0,-.10),'socket_entry_right':(W/2+.40,0,-.10),
        'socket_exit_left':(-W/2-.62,0,-.10),'socket_exit_right':(W/2+.62,0,-.10),
    }
    for name,pos in socket_positions.items():
        empty(col,name,markers,(pos[0],-pos[2],pos[1]))
    # A metre reference belongs to a non-export collection in the editable source.
    ref=bpy.data.collections.new('authoring_reference');scene.collection.children.link(ref)
    box(ref,None,'MetreReference',(1,1,1),(4,0,.5),mats['trim'],0)
    ref.hide_render=True;ref.hide_viewport=True
    scene['creator']='Codex vehicle lead; original geometry from approved imagegen concepts'
    scene['approved_concept']={
        'car_latch_a':'Latch compact','car_crate_a':'Crate hatch','car_sable_a':'Sable sedan'
    }[asset]+'; completed concept images remain in commit 80d0f24'
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    settings=json.loads((ROOT/'tools/s01/export_settings.json').read_text())
    settings.update(export_animations=False,export_skins=False,collection=col.name,
        filepath=str(output))
    bpy.ops.export_scene.gltf(**settings)
    points=[o.matrix_world@Vector(c) for o in col.all_objects if o.type=='MESH' for c in o.bound_box]
    mins=[min(p[i] for p in points) for i in range(3)];maxs=[max(p[i] for p in points) for i in range(3)]
    record={'id':asset,'source':str(source.relative_to(ROOT)),
        'export':str(output.relative_to(ROOT)),
        'collection':col.name,'members':sorted(o.name for o in col.all_objects),'source_spec':spec,
        'godot_aabb_min':[mins[0],mins[2],-maxs[1]],'godot_aabb_max':[maxs[0],maxs[2],-mins[1]],
        'sockets_godot_m':socket_positions,'triangles':sum(len(o.data.polygons) for o in col.all_objects if o.type=='MESH'),
        'materials':list(mats),'blender_version':bpy.app.version_string,'blender_hash':bpy.app.build_hash.decode()}
    (RECORDS/(asset+'_source.json')).write_text(json.dumps(record,indent=2)+'\n')
    print('VEHICLE_SOURCE',asset,json.dumps(record['godot_aabb_min']),json.dumps(record['godot_aabb_max']))


if __name__ == '__main__':
    assert bpy.app.version_string=='5.2.2 LTS'
    assert (ROOT/'art/source/.gdignore').exists()
    RECORDS.mkdir(parents=True,exist_ok=True)
    for spec in SPECS:build(spec)
